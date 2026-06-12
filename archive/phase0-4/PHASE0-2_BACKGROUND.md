# Phase 0–2 Background (pre-architecture-sprint)

Consolidated, sanitized history of the earlier optimization passes around the ecdsa.fail frontier commit
`013f1f7`, prior to the Phase 3/4 architecture work. Full classified ledger: `../../docs/FULL_HISTORY_MATRIX.md`.

## Phase 0 — baseline
The frontier commit `013f1f7` was built and validated: score **1,899,562,014** (avg Toffoli 1,458,957 × peak
1,302 qubits), validity **0/0/0 over 9024 shots**. This commit (carrying an externally-landed submission) was
inherited as the starting point; it already sits well under the published textbook and reference operating points.

## Phase 1 — local-knob edits (5 attempts, none kept)
Source-backed edits and bounded env-knob sweeps on three named levers:
- `BORROW_CURRENT_S2=1` — clean validation but peak unchanged (the lever was already enabled by default).
- `FUSED_OVFCLEAR_MEASURED=1` — invalid (17 classical / 6 phase mismatches): the +612-op change reseeds the
  SHAKE256-hashed op stream → the inherited Fiat-Shamir island is no longer clean for the new test set.
- `APPLY_CLEAN_COMPARE_BITS=17`, `KAL_FOLD_CARRY_TRUNC_W=20`, `ACTIVE_ITERATIONS=257` — all invalid via the same
  Fiat-Shamir island miss.
Verdict: every structurally-attractive truncation was blocked by the same op-stream-reseed mechanism.

## Phase 2 — nonstandard lanes (4 lanes, no valid path)
- **Failure-signature extraction:** failing shot indices are disjoint across candidates (the op-stream hash
  reseeds the entire test set on any perturbation); no cheap per-input "hard" predicate exists.
- **Adaptive nonce hunt:** 26 distinct nonces sampled; the fail-count distribution is **flat/Poisson** (no
  "close-to-clean island" cluster), and a 2048-shot prefilter does **not** predict 9024-shot survival.
- **ovf-rescue split:** splitting the overflow-clear into independent measured halves reached a best invalid
  profile of 12 classical / 8 phase — still short of clean, and not localized to one clear.
- **Unused-primitive hunt:** catalogued dead-code primitives; one materialize-f substitution point identified
  with LOW confidence (later examined and closed in Phase 3 Lane C).
Verdict: `CLOSE_NO_VALID_PATH` — no concrete non-bruteforce lane survived.

## Carry-forward to Phase 3/4
Two walls emerged that the later architecture work confirmed and quantified:
1. **The Fiat-Shamir island wall** — any change to the hashed op stream reseeds the 9024 test inputs.
2. **The peak/scratch co-residency** at the widest GCD steps — quantified in Phase 3 Lane B and Phase 4.

These motivated the Phase 3 local-lever survey (Lanes A–E) and the Phase 4 architecture sprint, all archived in
the parent package.
