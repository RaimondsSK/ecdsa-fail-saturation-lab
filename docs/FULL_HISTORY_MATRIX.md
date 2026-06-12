# ECDSA_PHASE4_FULL_HISTORY_MATRIX

**Phase 4A · Workstream 1.** Complete, classified history of every recorded step on the ecdsa.fail
secp256k1 point-add circuit. Source of record: `lab.db` (scores/experiments/runs/submissions/nonces),
`<challenge-workspace>/` (Phase 0–2 notes), Phase 3 lane reports. **No score claim** — all numbers
are transcriptions of validated harness runs or cited memory-note frontier points.

> Step-class legend: **PARAM** parameter/knob only · **ALGO** source algorithm change · **NONCE** Fiat-Shamir
> island selector · **PEAK** peak-qubit reduction · **TOF** Toffoli reduction · **TOOL** verification/diagnostic
> tooling · **FAIL** failed experiment (not kept).

## A. Validated frontier steps (kept; score-improving)
| commit | by | avg Toffoli | qubits | score | step class | what changed | source |
|---|---|---|---|---|---|---|---|
| `fa473ea` | challenge | 3,942,753 | 2715 | 10,704,574,395 | — | textbook initial | results.tsv / README |
| `83e3b66` | (frontier) | (n/r) | 1309 | 1,968,793,475 | PEAK+TOF | comparator/iteration era frontier | memory_note |
| `436b516` | us | 1,503,871 | 1309 | 1,968,567,139 | PARAM+NONCE | `APPLY_CLEAN_COMPARE_BITS=21` + nonce 431581 | memory_note |
| `a66b042` | an external contributor | 1,503,355 | 1309 | 1,967,891,695 | PARAM+NONCE | `CB=20` + nonce 721381 | memory_note |
| `lowq0` | us | 1,497,795 | 1309 | 1,960,613,655 | PARAM+NONCE | `active262` + nonce 2432 | memory_note |
| **`013f1f7`** | unknown (ea8a7716) | **1,458,957** | **1302** | **1,899,562,014** | **PEAK+TOF** | **1309→1302 peak break + lower Toffoli** (the live frontier we inherit) | results.tsv / git subject |

*Intermediate local-run commits in `results.tsv`: `935dc1f` (4 OK runs, 2715q tuning), `750fdf9`, `196206e`
(3,962,753 T / 2715q variant). These are pre-frontier textbook-era tuning, not distinct frontier points.*

## B. Our experiment ledger (Phase 0–3) — all classified
| phase | step | class | validation | kept | outcome |
|---|---|---|---|---|---|
| 0 | baseline (no edits) | — | 0/0/0 | ✓ | baseline = 1,899,562,014 |
| 1 | `BORROW_CURRENT_S2=1` | PARAM | 0/0/0 | ✗ | no-op (already default-on via configure_) |
| 1 | `FUSED_OVFCLEAR_MEASURED=1` | ALGO | 17/6/0 | ✗ | FAIL — +612 ops reseed → island miss |
| 1 | `APPLY_CLEAN_COMPARE_BITS=17` | PARAM | 13/16/0 | ✗ | FAIL — island miss |
| 1 | `KAL_FOLD_CARRY_TRUNC_W=20` | PARAM | 13/12/0 | ✗ | FAIL — island miss |
| 1 | `ACTIVE_ITERATIONS=257` | PARAM | 23/16/0 | ✗ | FAIL — nonconvergence floor + island |
| 2 lane1 | failure-signature diag (4 candidates) | TOOL | — | ✗ | no hard-input predicate; failing shots disjoint |
| 2 lane2 | adaptive nonce hunt (26 nonces) | NONCE | all invalid | ✗ | FAIL — flat distribution; 2048-prefilter≠9024 |
| 2 lane3 | `OVFCLEAR` ovf1-only / ovf2-only split | ALGO | 20/15, 12/8 | ✗ | FAIL — best 12/8, still island-bound |
| 3 A | selective ovf2 rescue | TOOL | — | ✗ | STOP — ovf2 identity exact (0/2.47M); failures = reseed |
| 3 B | peak teardown 1302→1301 | TOOL | — | ✗ | STOP — 1302 structurally bound (composite scratch) |
| 3 C | qoffset substitution | TOOL | — | ✗ | STOP — `cmod_add_qq_lowq` dead / off-peak / semantics mismatch |
| 3 D | jump-GCD depth feasibility | TOOL | — | ✗ | STOP — already depth-2 sweet spot; deeper widens transcript |
| 3 E | round84 square engine | TOOL | — | ✗ | REFUTED — 9.88% share, already at ~n² floor |

**Net:** across Phase 0–3, **0 score-improving steps landed by us**; the live frontier `013f1f7` was landed
by an external party (submission `ea8a7716`). Every local structural edit failed at the **Fiat-Shamir island
wall** (op-stream reseed) and/or was **off-peak / already-optimal**.

## C. Submission record (read-only history; we have NOT submitted)
| submission uuid | commit | score | by | source |
|---|---|---|---|---|
| `ea8a7716-15fb-46d7-8837-3c6173ba464e` | `013f1f7` | 1,899,562,014 | unknown | git subject (HEAD) |
| (no uuid) | `436b516` | 1,968,567,139 | us | memory_note |
| (no uuid) | `a66b042` | 1,967,891,695 | an external contributor | memory_note |
| (no uuid) | `lowq0` | 1,960,613,655 | us | memory_note |

## D. Completeness gaps (for Phase 4 archaeology to close)
| gap | status | how to close |
|---|---|---|
| Local git is a **single squashed commit** (`013f1f7`) | only HEAD has full tree | recover historical commits from the upstream/public repo if the operator can fetch it (not present locally) |
| Frontier commits `83e3b66`/`436b516`/`a66b042`/`lowq0` exist only as **memory-note short-hashes** | not in local git | verify against the public leaderboard / submission notes if exported |
| Leaderboard/submission notes beyond `ea8a7716` | not present | Workstream 4 ( community scout) |
| Nonces used by *other* competitors | only ours + an external contributor's 721381 known | Workstream 4 |

**Two committed epochs and one inherited epoch are fully grounded; deeper history requires an upstream fetch
or community export — flagged, not fabricated.** See `ECDSA_PHASE4_SCORE_EPOCH_MAP.md`.
