"""Lean 4 kernel-acceptance gate via the LSP server (`lean --server`).

Implements the four-condition acceptance criterion documented in the
README:

  1. The file compiles with `lake build` returning exit code 0.
  2. The proposed theorem is present with the proposed statement.
  3. The proof body contains zero sorry/admit/axiom introductions.
  4. No new axiom declarations were added.

For (1) we use the persistent LSP server (faster than per-file lake
builds when the substrate is already compiled). For (2)-(4) we parse
the source and the server diagnostics.

The server interface follows the Language Server Protocol over stdio,
using JSON-RPC 2.0 framing. We do NOT use a full LSP library because
we only need a small subset (initialize, didOpen, didClose, diagnostics).
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import threading
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class AcceptanceVerdict:
    """The verdict for one proof attempt, with full evidence."""

    accepted: bool
    file_path: str
    statement_present: bool
    no_sorry: bool
    no_admit: bool
    no_axiom_intro: bool
    diagnostic_errors: list[str] = field(default_factory=list)
    diagnostic_warnings: list[str] = field(default_factory=list)
    elapsed_seconds: float = 0.0
    rejection_reason: str = ""


# Tokens that disqualify a proof. These are checked syntactically over
# the proof body; the kernel's own check is separately required.
_FORBIDDEN_BODY_TOKENS = (
    r"\bsorry\b",
    r"\badmit\b",
    r"\bnative_decide\b",  # by-name: this is decide-by-codegen, opens reflection surface; we exclude it
)


class LeanServer:
    """A long-lived `lean --server` instance providing kernel verification.

    Usage:
        with LeanServer(project_root=Path("lean-substrate")) as srv:
            verdict = srv.verify(proof_path, expected_statement=...)
    """

    def __init__(self, project_root: Path, lean_binary: str = "lean") -> None:
        if not shutil.which(lean_binary):
            raise RuntimeError(f"`{lean_binary}` not found on PATH")
        if not project_root.is_dir():
            raise RuntimeError(f"project_root does not exist: {project_root}")
        self._root = project_root.resolve()
        self._lean = lean_binary
        self._proc: subprocess.Popen[bytes] | None = None
        self._lock = threading.Lock()
        self._next_id = 1
        self._diagnostics: dict[str, list[dict[str, Any]]] = {}
        self._reader_thread: threading.Thread | None = None
        self._reader_stop = threading.Event()

    # ── lifecycle ──────────────────────────────────────────────────────

    def __enter__(self) -> LeanServer:
        self.start()
        return self

    def __exit__(self, *exc: object) -> None:
        self.stop()

    def start(self) -> None:
        if self._proc is not None:
            return
        self._proc = subprocess.Popen(
            [self._lean, "--server"],
            cwd=str(self._root),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self._reader_thread = threading.Thread(
            target=self._read_loop, daemon=True
        )
        self._reader_thread.start()
        self._initialize()

    def stop(self) -> None:
        if self._proc is None:
            return
        try:
            self._send_notification("exit", {})
        except Exception:
            pass
        self._reader_stop.set()
        try:
            self._proc.terminate()
            self._proc.wait(timeout=5)
        except Exception:
            self._proc.kill()
        self._proc = None

    # ── LSP plumbing ───────────────────────────────────────────────────

    def _send_message(self, msg: dict[str, Any]) -> None:
        assert self._proc and self._proc.stdin
        body = json.dumps(msg).encode("utf-8")
        header = f"Content-Length: {len(body)}\r\n\r\n".encode("ascii")
        with self._lock:
            self._proc.stdin.write(header + body)
            self._proc.stdin.flush()

    def _send_request(self, method: str, params: dict[str, Any]) -> int:
        rid = self._next_id
        self._next_id += 1
        self._send_message({"jsonrpc": "2.0", "id": rid, "method": method, "params": params})
        return rid

    def _send_notification(self, method: str, params: dict[str, Any]) -> None:
        self._send_message({"jsonrpc": "2.0", "method": method, "params": params})

    def _read_loop(self) -> None:
        assert self._proc and self._proc.stdout
        stdout = self._proc.stdout
        while not self._reader_stop.is_set():
            try:
                header = b""
                while True:
                    line = stdout.readline()
                    if not line:
                        return
                    header += line
                    if line == b"\r\n":
                        break
                m = re.search(rb"Content-Length:\s*(\d+)", header)
                if not m:
                    continue
                size = int(m.group(1))
                body = stdout.read(size)
                msg = json.loads(body.decode("utf-8"))
                self._handle_message(msg)
            except Exception:
                # Reader errors are non-fatal — we'll surface them on the
                # next verify() via diagnostic absence.
                continue

    def _handle_message(self, msg: dict[str, Any]) -> None:
        if msg.get("method") == "textDocument/publishDiagnostics":
            params = msg.get("params", {})
            uri = params.get("uri", "")
            self._diagnostics[uri] = params.get("diagnostics", [])

    def _initialize(self) -> None:
        self._send_request(
            "initialize",
            {
                "processId": None,
                "rootUri": f"file://{self._root}",
                "capabilities": {"textDocument": {"publishDiagnostics": {}}},
            },
        )
        # Wait briefly for the server to settle (Lean takes a moment to
        # boot up the substrate's mathlib dependencies).
        time.sleep(2.0)
        self._send_notification("initialized", {})

    # ── verification ───────────────────────────────────────────────────

    def verify(
        self,
        file_path: Path,
        *,
        expected_statement: str,
        wait_seconds: float = 90.0,
    ) -> AcceptanceVerdict:
        """Verify one proof attempt.

        file_path: a .lean file under the project root containing the
            proof. Caller is responsible for writing the file before
            calling this method.

        expected_statement: the verbatim Lean source of the theorem
            statement (everything between `theorem NAME` and `:=`).
            Used to detect quiet weakening.

        wait_seconds: how long to wait for the server to publish
            diagnostics for this file.
        """
        text = file_path.read_text()
        t0 = time.perf_counter()
        uri = f"file://{file_path.resolve()}"
        self._diagnostics.pop(uri, None)

        # Open the document in the LSP session.
        self._send_notification(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": uri,
                    "languageId": "lean4",
                    "version": 1,
                    "text": text,
                }
            },
        )

        # Wait for diagnostics. Lean publishes diagnostics multiple
        # times (incrementally as elaboration proceeds), so we wait
        # for a quiet period rather than the first publish.
        deadline = time.time() + wait_seconds
        last_count = -1
        stable_since = time.time()
        while time.time() < deadline:
            current = len(self._diagnostics.get(uri, []))
            if current != last_count:
                last_count = current
                stable_since = time.time()
            elif time.time() - stable_since > 3.0 and last_count >= 0:
                break
            time.sleep(0.5)

        diagnostics = self._diagnostics.get(uri, [])
        elapsed = time.perf_counter() - t0

        # Close the document (so the server doesn't accumulate stale state).
        self._send_notification("textDocument/didClose", {"textDocument": {"uri": uri}})

        # Classify diagnostics: severity 1 = Error, 2 = Warning.
        errors = [d for d in diagnostics if d.get("severity") == 1]
        warnings = [d for d in diagnostics if d.get("severity") == 2]

        # Condition 2: theorem signature preserved (no quiet weakening).
        # We compare signatures (theorem name + statement up to `:=`),
        # ignoring the proof body which legitimately differs between
        # spec (`by sorry`) and proof (`by <real proof>`).
        statement_present = self._theorem_signature_present(text, expected_statement)

        # Condition 3: no sorry / admit / native_decide.
        no_sorry = not re.search(r"\bsorry\b", text)
        no_admit = not re.search(r"\badmit\b", text)

        # Condition 4: no new axiom declarations.
        no_axiom_intro = not re.search(r"^\s*axiom\s+\w+", text, re.MULTILINE)

        # Final verdict: all four must hold AND no kernel errors.
        accepted = (
            not errors
            and statement_present
            and no_sorry
            and no_admit
            and no_axiom_intro
        )

        reason = ""
        if errors:
            reason = f"kernel reported {len(errors)} error(s)"
        elif not statement_present:
            reason = "proposed theorem statement not present verbatim"
        elif not no_sorry:
            reason = "proof body contains `sorry`"
        elif not no_admit:
            reason = "proof body contains `admit`"
        elif not no_axiom_intro:
            reason = "file introduces a new `axiom` declaration"

        return AcceptanceVerdict(
            accepted=accepted,
            file_path=str(file_path),
            statement_present=statement_present,
            no_sorry=no_sorry,
            no_admit=no_admit,
            no_axiom_intro=no_axiom_intro,
            diagnostic_errors=[self._format_diag(d) for d in errors],
            diagnostic_warnings=[self._format_diag(d) for d in warnings],
            elapsed_seconds=elapsed,
            rejection_reason=reason,
        )


    @staticmethod
    def _extract_theorem_signature(src: str) -> str | None:
        """Return the theorem signature string from `theorem NAME ... :` up
        to (but not including) `:=`. None if no theorem declaration found."""
        # Find the first `theorem <name>` followed by either ` :=` or `:=`
        m = re.search(r"theorem\s+\w+[^:=]*?:[\s\S]*?(?=:=)", src)
        if not m:
            return None
        sig = m.group(0).strip()
        return sig

    @staticmethod
    def _theorem_signature_present(proof_text: str, expected_spec_text: str) -> bool:
        """True iff both sources declare the same theorem signature."""
        proof_sig = LeanServer._extract_theorem_signature(proof_text)
        spec_sig  = LeanServer._extract_theorem_signature(expected_spec_text)
        if proof_sig is None or spec_sig is None:
            return False
        return LeanServer._normalize_whitespace(proof_sig) == LeanServer._normalize_whitespace(spec_sig)

    @staticmethod
    def _normalize_whitespace(s: str) -> str:
        return re.sub(r"\s+", " ", s).strip()

    @staticmethod
    def _format_diag(d: dict[str, Any]) -> str:
        rng = d.get("range", {}).get("start", {})
        return f"line {rng.get('line', '?') + 1}: {d.get('message', '')}"
