# hwLedger: IndexTTS 2.0 → Kokoro-82M Migration Plan

**Status:** Draft (not yet opened as PR)
**Author:** Phenotype voice-stack audit (audit #238)
**Date:** 2026-04-24
**Target repo:** `KooshaPari/hwLedger`
**Related ADR:** `hwLedger/docs-site/architecture/adrs/0010-tts-backend-piper.md` (v2, five-tier chain)

---

## Context

Audit #238 selected Kokoro-82M as the Phenotype-wide default TTS engine:

- M-series MLX-native with ~80 ms latency per sentence.
- Apache-2.0 licence (same as IndexTTS).
- 330 MB install vs. IndexTTS's 6.8 GB (weights + torch + modelscope).
- CPU-fast; no GPU required; no torch install.
- Already present in hwLedger's A/B harness (`tools/tts-ab/render_kokoro.py`)
  and already wired as tier-3 in `hwledger-journey-render::select_voice_backend`.

Current hwLedger chain (ADR-0010 v2):

1. `HWLEDGER_VOICE` explicit override
2. **IndexTTS 2.0** (tier-2, default on GPU hosts)
3. **Kokoro-82M** (tier-3)
4. KittenTTS nano (tier-4)
5. AVSpeechSynthesizer (tier-5 macOS)
6. Piper (tier-6 Linux CI)
7. Silent

Goal: swap tier priority so **Kokoro-82M is the default** and IndexTTS is
demoted to an opt-in "hero-render" tier behind `HWLEDGER_VOICE=indextts2`.

---

## Why Kokoro beats IndexTTS as *default*

| Axis | IndexTTS 2.0 | Kokoro-82M | Winner |
|---|---|---|---|
| Quality (MOS, A/B slot) | 4.5 (slot D) | 4.2 (slot E) | IndexTTS +0.3 |
| Offline | Yes | Yes | tie |
| Licence | Apache-2.0 | Apache-2.0 | tie |
| Install footprint | 6.8 GB (torch + modelscope + 5.5 GB weights) | 330 MB (ONNX + 50+ voices) | **Kokoro** (20×) |
| Cold-start | ~30 s on MPS | ~1 s on CPU | **Kokoro** (30×) |
| RTF | 13.5× on MPS, ~1× CPU-slow | 0.3× on M-series CPU | **Kokoro** on non-GPU |
| GPU required for usable speed | Yes | No | **Kokoro** |
| Determinism | Not byte-deterministic across torch/MPS versions | Byte-deterministic per model+voices.bin | **Kokoro** |
| Per-sentence latency | ~2.5 s autoregressive | ~80 ms (MLX path) / ~200 ms (ONNX CPU) | **Kokoro** (30×) |
| Voice cloning | Zero-shot | No (50+ preset voices) | IndexTTS (only if needed) |

**Key insight:** The 0.3 MOS quality gap is imperceptible on 40-second
narration clips to anyone who isn't specifically A/B-ing them. Meanwhile
install/cold-start/determinism heavily favour Kokoro for CI and
self-hosted runners. IndexTTS remains valuable only for zero-shot voice
cloning in marketing renders.

---

## API compatibility

Both drivers already live in `tools/tts-ab/` and output WAV. Rust callers
in `hwledger-journey-render` use `synthesise_voiceover_indextts2` and
`synthesise_voiceover_kokoro`. Both return `Result<String, RenderError>`
where the `String` is the path to a WAV on disk; the Remotion pipeline
(ADR-0011) transcodes to AAC/m4a downstream.

No signature changes required. Only the selector in `select_voice_backend`
changes priority.

---

## Scope of changes

### 1. `crates/hwledger-journey-render/src/lib.rs::select_voice_backend`

Re-order the auto-chain:

```text
old:  HWLEDGER_VOICE -> IndexTTS (if GPU) -> Kokoro -> KittenTTS -> AVSpeech -> Piper -> Silent
new:  HWLEDGER_VOICE -> Kokoro -> KittenTTS -> AVSpeech -> Piper -> Silent
```

IndexTTS is removed from the auto-chain entirely; still reachable via
`HWLEDGER_VOICE=indextts2` override. This also lets the selector skip the
`gpu_available()` + `indextts_available()` probe on every journey, which
currently spawns a subprocess cold-check.

Pseudocode delta (planner, not code):

- Drop the `if gpu_available() && indextts_available() { return IndexTts2 }`
  branch from `select_voice_backend`.
- Promote the `if kokoro_available()` branch to run first after explicit-override.
- Leave `synthesise_voiceover_indextts2` / `indextts_available` intact
  — they remain callable via explicit override.
- Update doc comment `///   2. IndexTTS 2.0 if GPU + venv present.` to note
  it is now explicit-override-only.

### 2. ADR-0010 revision (v3)

Open `docs-site/architecture/adrs/0010-tts-backend-piper.md` for a v3 bump.
Key diff sections:

- **Decision:** swap tier-2 and tier-3; note IndexTTS is opt-in.
- **Rationale:** cite install footprint, cold-start, determinism, and
  per-sentence latency (Kokoro MLX ~80 ms vs. IndexTTS autoregressive
  ~2.5 s). Reference audit #238.
- **Revisit when:** a new offline model beats Kokoro on the A/B page,
  or voice-cloning becomes a default requirement (which would restore
  IndexTTS to tier-2).

### 3. `docs-site/audio/voice-ab.md`

Update the "Your take" section footer to note Kokoro is now the default;
IndexTTS is hero-render-only.

### 4. Tests

`crates/hwledger-journey-render/src/lib.rs` has unit tests for
`select_voice_backend` (check the `#[cfg(test)] mod tests`). The test that
asserts IndexTTS wins on GPU hosts needs to flip: on any host with Kokoro
installed, Kokoro wins. GPU + IndexTTS path is still tested under explicit
override.

Add one new test: `select_voice_backend_prefers_kokoro_over_indextts_on_gpu_host`.

### 5. Re-render the 26 journeys

Per ADR-0010 v2's "Your take" footer, picking Kokoro means re-rendering
the 26 captured journeys. This is the fastest offline path (~0.3× RTF on
M-series CPU, ~3 min per 40 s journey, ~80 min total batch).

Tracking: new work package under `kitty-specs/` before execution.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Kokoro voice (af_heart) sounds worse than IndexTTS default speaker on longer scripts | Medium | Medium | Keep slot D/E audio files from A/B page; re-run A/B on representative 90 s journey clip before merging |
| Existing journey attestations (ADR-0015) reference IndexTTS-rendered WAV hashes | High | Low | Regenerate attestations as part of re-render batch; hashes update naturally |
| CI runners that had no GPU already fell through to Kokoro — this PR is a no-op for them | n/a | n/a | No change for Linux CI; change only affects macOS MPS hosts |
| Users override `HWLEDGER_VOICE=auto` expecting IndexTTS | Low | Low | CHANGELOG note; provide `HWLEDGER_VOICE=indextts2` one-liner migration hint in release notes |
| Kokoro ONNX model download URL (github releases) disappears | Low | High | Mirror `kokoro-v1.0.onnx` + `voices-v1.0.bin` to an internal Phenotype artifact store; pin SHA-256 in driver |
| Disk floor in constrained dev envs | Low | Low | Kokoro cache is 330 MB; well under the 8 GiB floor |

---

## Performance delta (estimate)

On the self-hosted macOS runner (M-series), per 40 s journey:

| Stage | IndexTTS 2.0 (current default) | Kokoro-82M (proposed default) | Delta |
|---|---|---|---|
| Cold-start (first journey) | ~30 s (torch + MPS warmup) | ~1 s (ONNX init) | **-29 s** |
| Per-sentence synth | ~2.5 s autoregressive | ~80 ms MLX / ~200 ms ONNX | **~30× faster** |
| 40 s journey end-to-end | ~506 s (13.5× RTF) | ~12 s (0.3× RTF) | **~40× faster** |
| 26 journeys (batch) | ~220 min | ~5-8 min | **~30× faster** |

Install footprint: **-6.5 GB** on fresh runner (drop torch, modelscope,
IndexTTS weights). Kept as optional install for hero renders.

CI latency (Linux, Kokoro already default since no GPU): **unchanged**.

---

## Migration steps (agent-actionable)

1. Open worktree `repos/hwLedger-wtrees/kokoro-default/` from main.
2. Create AgilePlus spec:
   `agileplus specify --title "Kokoro-82M default TTS" --description "Demote IndexTTS 2.0 from tier-2 to explicit-opt-in; Kokoro becomes auto-chain default. See phenotype-tooling/docs/hwledger-kokoro-migration.md"`
3. Edit `crates/hwledger-journey-render/src/lib.rs::select_voice_backend` per §1.
4. Update unit tests per §4.
5. Bump ADR-0010 to v3 per §2.
6. Update voice-ab.md footer per §3.
7. Run `cargo test -p hwledger-journey-render` locally.
8. Re-render one sample journey as smoke test:
   `HWLEDGER_VOICE=auto cargo run -p hwledger-journey-render -- <journey-id>`.
9. Open PR against `main` referencing audit #238, ADR-0010 v3 diff, and
   this migration plan. Add `docs-site/audio/voice-ab.md` re-render as
   follow-up work package if the 26-journey batch isn't done in-PR.
10. Merge via `gh pr merge --admin` (expect CI billing failure per
    workspace policy; verify locally instead).

Estimated effort (agent): 1 parallel subagent batch, 8-15 tool calls,
~4-6 min wall clock excluding the 26-journey re-render.

---

## Cross-Project Reuse Opportunities

- The voice CLI scaffolded in `phenotype-tooling/voice/` (Phase A/B of
  audit #238) should wrap the *same* `kokoro-onnx` driver that hwLedger
  uses. Once `agent_voice.py` ships, `render_kokoro.py` in hwLedger
  becomes a thin importer of `phenotype_tooling.voice.agent_voice` rather
  than a standalone 50-line script. Candidate extraction target:
  `phenotype-tooling/voice/` (new Python package) or
  `crates/phenotype-voice/` (Rust facade over Python driver).

- STT (Whisper Large V3 Turbo via `faster-whisper`) from the same audit
  has no current hwLedger consumer, but should land in
  `phenotype-tooling/voice/` alongside Kokoro for future journey-capture
  transcript generation.

---

## References

- ADR-0010 v2: `hwLedger/docs-site/architecture/adrs/0010-tts-backend-piper.md`
- Selector code: `hwLedger/crates/hwledger-journey-render/src/lib.rs::select_voice_backend`
- A/B harness: `hwLedger/tools/tts-ab/{render_indextts.py,render_kokoro.py}`
- A/B page: `hwLedger/docs-site/audio/voice-ab.md`
- Kokoro-82M: https://huggingface.co/hexgrad/Kokoro-82M (Apache-2.0)
- kokoro-onnx: https://github.com/thewh1teagle/kokoro-onnx
- Audit #238 (Phenotype voice-stack selection): Kokoro + faster-whisper
