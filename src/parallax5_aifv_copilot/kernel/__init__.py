"""Lean kernel-acceptance gate.

The kernel is the only authority. LLMs draft proofs; the kernel decides
which drafts are accepted. The `LeanServer` class wraps a persistent
`lean --server` LSP session and exposes a single `verify()` method that
returns an `AcceptanceVerdict` carrying all the evidence needed to
adjudicate the four acceptance conditions.
"""
from .lean_server import AcceptanceVerdict, LeanServer

__all__ = ["AcceptanceVerdict", "LeanServer"]
