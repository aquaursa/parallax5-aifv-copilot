"""parallax5-aifv command-line entrypoint."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.table import Table

from . import __version__
from .benchmark import load_corpus, run_benchmark
from .llm import DEFAULT_MODELS, make_all_default_clients

_console = Console()


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(__version__, prog_name="parallax5-aifv")
def cli() -> None:
    """PARALLAX-5 AI-FV Co-Pilot.

    LLM proposes; Lean disposes. Multi-LLM cross-validated proof
    drafting with kernel-verified acceptance.
    """


@cli.command()
def models() -> None:
    """Show the pinned model per provider."""
    t = Table(title="Pinned models")
    t.add_column("Provider", style="bold")
    t.add_column("Model")
    for p, m in DEFAULT_MODELS.items():
        t.add_row(p, m)
    _console.print(t)


@cli.command()
@click.option(
    "--corpus", "corpus_path", type=click.Path(exists=True, path_type=Path), required=True,
    help="Corpus manifest JSON (e.g. corpus/manifest/v0.1.json)",
)
@click.option(
    "--substrate", "substrate_root", type=click.Path(exists=True, path_type=Path),
    default=Path("lean-substrate"),
    help="Path to the PARALLAX-5 substrate Lean project (default: ./lean-substrate)",
)
@click.option(
    "--prompts", "prompts_dir", type=click.Path(exists=True, path_type=Path),
    default=Path("prompts"),
    help="Directory containing spec_v1.md and proof_v1.md",
)
@click.option(
    "--out", "output_dir", type=click.Path(path_type=Path),
    default=Path("results"),
    help="Directory under which run_<ts>/ will be created",
)
def benchmark(corpus_path: Path, substrate_root: Path, prompts_dir: Path, output_dir: Path) -> None:
    """Run the full corpus × 4-LLM benchmark matrix."""
    _console.print(f"[bold]Loading corpus from[/bold] {corpus_path}")
    corpus = load_corpus(corpus_path)
    _console.print(f"  [green]✓[/green] {len(corpus)} contracts")

    _console.print("[bold]Initializing LLM clients[/bold]")
    clients = make_all_default_clients()
    for p, c in clients.items():
        _console.print(f"  [green]✓[/green] {p}: {c.model}")

    _console.print(f"[bold]Running benchmark[/bold] (substrate at {substrate_root})")
    run_dir = run_benchmark(
        corpus=corpus,
        spec_clients=clients,
        proof_clients=clients,
        substrate_root=substrate_root,
        prompts_dir=prompts_dir,
        output_dir=output_dir,
    )

    summary = json.loads((run_dir / "summary.json").read_text())
    _console.print(f"\n[bold green]Run complete:[/bold green] {run_dir}")
    _console.print(f"  Total attempts: {summary['total_attempts']}")
    _console.print(f"  Accepted:       {summary['accepted']}")
    _console.print(f"  Rate:           {summary['acceptance_rate']:.1%}")


def main() -> int:
    cli()
    return 0


if __name__ == "__main__":
    sys.exit(main())
