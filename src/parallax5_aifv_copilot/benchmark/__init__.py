"""Benchmark harness for the 100-contract corpus × 4-LLM matrix."""
from .harness import AttemptRecord, CorpusEntry, load_corpus, run_benchmark

__all__ = ["AttemptRecord", "CorpusEntry", "load_corpus", "run_benchmark"]
