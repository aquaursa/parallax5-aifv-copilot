# Operational prerequisites

The co-pilot calls four LLM provider APIs. Each requires environment
configuration and account-side prerequisites that are not bundled in
the Docker image.

## API keys

```bash
export ANTHROPIC_API_KEY=...        # https://console.anthropic.com/
export OPENAI_API_KEY=...           # https://platform.openai.com/
export DEEPSEEK_API_KEY=...         # https://platform.deepseek.com/
export MISTRAL_API_KEY=...          # https://console.mistral.ai/
```

## Provider-specific notes

### Mistral — Labs models must be enabled

The default Mistral model is `labs-leanstral-2603`, which is part of
Mistral's **Labs** product tier. Calls fail with HTTP 403 and error
code `1913` (`labs_not_enabled`) until an admin enables Labs in your
organization settings at https://admin.mistral.ai/plateforme/privacy.

If Labs is not available, swap the default to a general model that's
on the standard tier:

```bash
# In src/parallax5_aifv_copilot/llm/__init__.py, set:
DEFAULT_MODELS["mistral"] = "mistral-large-2512"   # or magistral-medium-2509
```

The benchmark report must document any non-default model so that
acceptance-rate numbers are correctly attributed.

### OpenAI — sufficient quota required

`gpt-5.5-pro` is a pro-tier reasoning model with higher per-token cost
than `gpt-5` or `gpt-4o`. Quota exhaustion produces HTTP 429
(`insufficient_quota`). For the full 100-contract × 4-provider × 2-pass
benchmark, plan for roughly:

  - Spec drafting: 100 × 4 × ~2K input + ~1K output tokens
  - Proof drafting: 100 × 4 × ~3K input + ~3K output tokens

≈ 1.2M input + 800K output tokens per provider per full run. Multiply
by 3 runs (for variance) and 4 providers. Per-provider quotas should
be set accordingly before kicking off `parallax5-aifv benchmark`.

### Deepseek — reasoning content counts against max_tokens

`deepseek-v4-pro` is a reasoning model. The response contains both
`reasoning_content` (visible to debugger; not used by the kernel gate)
and `content` (the actual answer). Both count against `max_tokens`.
Use `max_tokens >= 8192` for the proof pipeline so the model has room
to think out loud before emitting the final code block.

### Anthropic — context window

`claude-opus-4-7` has a 200K-token context window, which is sufficient
for any single contract in the corpus. The adapter does not perform
context-packing.

## Lean toolchain

A working `lean` binary version-matched to the substrate (currently
4.22.0) must be on PATH. The Docker image installs this automatically
via `elan`; for local runs:

```bash
curl https://raw.githubusercontent.com/leanprover/elan/master/elan-init.sh -sSf | sh
lean --version   # confirm
```

## Substrate

The Lean 4 substrate must be cloned as a submodule and built before
the benchmark runs (the LSP server needs `.olean` artifacts present):

```bash
git submodule update --init --recursive
cd lean-substrate
lake build
cd ..
```

The benchmark harness initializes its `LeanServer` instance with
`project_root=Path("lean-substrate")` and expects the substrate to be
already compiled.
