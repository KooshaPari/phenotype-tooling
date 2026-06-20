# pheno-prompt-test — SPEC

## Scope

pytest-friendly assertions and harness for LLM prompt regression tests.
Implements §77.3 of `FLEET_100TASK_DAG_V4.md`.

## Public API

- `LLMResponse` — frozen dataclass wrapping an LLM completion.
- `PromptCase` — a `(prompt, name)` test case with name, prompt, expected
  output, and assertions.
- `assert_in_text(response, substring)` — pass if substring is in response.
- `assert_matches_pattern(response, pattern)` — pass if regex matches.
- `assert_json_valid(response, schema=None)` — pass if JSON parses / schema valid.
- `compute_similarity(a, b)` — Jaccard token overlap for fuzzy match.
- `find_prompt_cases(root)` — discovery helper.
- `register_case(case)` / `registered_cases()` — registration API.
- `run_case(case, backend)` — end-to-end runner that takes a callable
  LLM backend.
- `init_prompt_test(target_dir)` — scaffold-kit entrypoint (V6 PR-4) that
  materializes a starter `tests/prompts/` skeleton.

## Conventions

- **When to use:** regression testing LLM completions.
- **When NOT to use:** non-LLM unit tests.
- **5-line quickstart:**
  ```python
  from pheno_prompt_test import PromptCase, run_case
  case = PromptCase(name="hi", prompt="say hi",
                    assertions=[lambda r: "hi" in r.text])
  def backend(prompt): return type("R", (), {"text": "hi"})()
  run_case(case, backend)
  ```

## Quality bar

- 71-pillar score: 21/71 (Tier 0)
- Test matrix: 3 test files (smoke, init, plugin)
- License: dual (MIT + Apache-2.0)

## See also

- ADR-039 (pheno-flake template)
- §77.3 of FLEET_100TASK_DAG_V4.md