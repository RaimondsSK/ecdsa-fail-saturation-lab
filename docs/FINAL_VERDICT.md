# ECDSA_PHASE4_FINAL_VERDICT — Archive at Saturation

**Status: `ECDSA_PHASE4_ARCHIVED_AT_SATURATION`** · Date: 2026-06-12 ·  Reviewer/lead: the research lead.

This closes the active ecdsa.fail optimization sprint. **This is not "gave up early"** — it is a
high-confidence architectural saturation result: every surveyed local, hybrid, and apply-reuse route was driven
to a grounded refutation or impossibility, with diagnostics, traces, and (where decidable) mechanical proofs.
No challenge source was modified; main is untouched at `013f1f7`. **Documentation only.**

---

## 1. Baseline (the frontier we hold)
| field | value | source |
|---|---|---|
| commit | `013f1f7925bd2c509678e37c4c18eb8b34d57c31` (submission `ea8a7716`, inherited) | git / `BASELINE.md` |
| **score** | **1,899,562,014** | `score.json` |
| avg Toffoli/shot | 1,458,957 | `eval_circuit` |
| peak qubits | 1,302 | `eval_circuit` |
| validity | **0 / 0 / 0** over 9024 shots | `eval_circuit` |
| toolchain | rustc 1.93.0, bwrap 0.9.0, WSL2 (validated env) | re-verified ×5 across lanes |

The frontier was **landed by an external party** (submission `ea8a7716`); across the entire sprint **no
score-improving change landed by us** — every structural edit was refuted before a valid improvement.

## 2. What was attempted (full ledger)
**Phase 0–2 (pre-this analysis, in `<challenge-workspace>/`):** baseline establish; Phase 1 local-knob edits
(`BORROW_CURRENT_S2`, `FUSED_OVFCLEAR_MEASURED`, `APPLY_CLEAN_COMPARE_BITS=17`, `KAL_FOLD_CARRY_TRUNC_W=20`,
`ACTIVE_ITERATIONS=257`); Phase 2 four lanes (failure-signature extraction, adaptive nonce hunt = 26 nonces,
ovf1/ovf2 rescue split, unused-primitive hunt). Verdict then: `CLOSE_NO_VALID_PATH`.

**Phase 3 (local levers, diagnostic):**
| lane | hypothesis | verdict |
|---|---|---|
| A | selective `ovf2` rescue in `fused_double_y` | STOP — identity `ovf2==s2&y[0]` exact (0/2.47M); failures were op-count reseed |
| B | peak-lifetime teardown 1302→1301 | STOP — 1302 structurally bound (composite-scratch deficit) |
| C | `cmod_add_qq_lowq` qoffset substitution | STOP — target dead code / off-peak (≤1218q) / semantics mismatch |
| D | jump-GCD feasibility | STOP — already at depth-2 sweet spot; deeper widens transcript |
| E | round84 square engine | REFUTED — 9.88% share (<15%), already at the ~n² Wallace floor |

**Phase 4 (architecture sprint):**
| step | what | verdict |
|---|---|---|
| 4A | control plane (9 docs + factory scripts) | built |
| 4B | hypothesis queue (R1/R2/H3) | built; R1 chosen |
| 4C R1 | operand-narrow → transcript recycle | REFUTED — donor `freed_uv=0` at the peak steps 9–10 |
| 4C S1 | early-scratch-deficit map + revised queue | NO_LOCAL_SCRATCH_PATH — borrow headroom at peak = 0 |
| 4C S1-A | early-width convergence pre-test (400k factors) | REFUTED — width trim adds `WidthOverflow` / breaks correctness |
| 4D scout | engine-layout redesign scout (3 routes) | SCOUT_READY; R2 hybrid identified, gated by R3 |
| 4D R3a | toy lifecycle accounting (n=16/32/64) | INCONCLUSIVE — reconstruction exact; peak flips on apply-reuse assumption |
| 4D R3a' | apply-register-reuse source analysis | NOT_PLAUSIBLE — apply-reuse already exists at HEAD; peak is the walk |

## 3. What was proven / refuted (explicit, with evidence)
| finding | status | evidence |
|---|---|---|
| No blind nonce path | proven futile | P2 Lane 2: 26 nonces, flat distribution; `NONCE_HISTORY.md` |
| 2048-shot prefilter ≠ 9024 survival | proven | nonce 1000000: 1/1@2048 → 19/7@9024; `NONCE_HISTORY.md` |
| op-count-changing local edits hit the Fiat-Shamir island wall | proven | every P1/P2/P3 structural edit; Lane A reproduced it (258 probe ops → 15/9) |
| **peak = 1302 at steps 9–10, active_width=256, freed_uv=0** | measured | `ph4_r1_donor_map.tsv` |
| **borrow headroom at the peak = 0** | measured | `ph4_s1_borrow_raw.txt` (nonalias_beyond_safe=0) |
| early `active_width` trim breaks correctness (`WidthOverflow`) | measured | `ph4_s1a_convergence_400k.tsv` (trim adds 24–101 hard inputs; 0–9 trim = 100% fail) |
| transcript-only reconstruction works (operands freed) | proven (toy) | `r3a_lifecycle_model.py`: 2000/2000 exact, n=16/32/64 |
| **apply-register reuse already exists at HEAD** | proven (source) | `release_terminal_u` + `apply_bitvector_reverse → target=ty` (compressed.rs:1727–1749) |
| **peak is the GCD walk, not the apply** | measured + source | Lane B: tobitvector walk = 1302, apply ≤1297; `…APPLY_REGISTER_REUSE_ANALYSIS.md` |
| full Schrottenloher likely worsens score (Toffoli) | derived | TrailMix low-qubit 1169×2.09M = 2.44e9 > 1.90e9; `TRAILMIX_LAYOUT_DIFF.md` |

**Convergent root cause:** the 1,899,562,014 frontier is bound by the **GCD walk's co-residency** of operands +
transcript-write + the `2·active_width−1` body-scratch deficit at the widest early steps, under a **reseed-locked
validity gate** (Fiat-Shamir island). Every local relabel is closed (donor=0, borrow=0); width-narrowing breaks
correctness; the apply-reuse split already exists and isn't where the peak lives.

## 4. Remaining theoretical paths (all UNSUPPORTED / out of current sprint)
| path | status |
|---|---|
| a genuinely new inversion primitive that is **both** low-iteration **and** low-peak | **HYPOTHESIS — no such primitive identified** in TrailMix or the surveyed literature; unsupported |
| S1-C body **phase split** (op-stream-changing) | open but unmeasured Toffoli cost; Wall-2-exposed; not pursued (would re-enter the island wall) |
| full **engine replacement** (Schrottenloher pack/apply_bv) | likely **score-negative** (+43% Toffoli); not a Kaliski-preserving hybrid |
| future **community / paper / upstream** breakthrough | external dependency; cannot be manufactured here |

None has positive expected value under the current evidence.

## 5. Reusable artifacts (DO NOT DELETE)
**Infrastructure:** `lab.db` (+ `schema.sql`), `ingest/{ingest_git,ingest_notes,ingest_trailmix,gen_docs}.py`,
`scripts/{ph4_new_experiment.sh,ph4_record_result.py,s1a_patch_and_bin.py}`, `_external/trailmix/` (clone @ `cd961ff`).

**Matrices / maps:** `SCORE_EPOCHS.md`, `NONCE_HISTORY.md`, `PARAM_NONCE_MATRIX.md`, `ALGORITHM_LINEAGE.md`,
`FILE_HOTSPOTS.md`, `TRAILMIX_IDEA_MATRIX.md`, `ECDSA_PHASE4_{FULL_HISTORY_MATRIX,SCORE_EPOCH_MAP,NONCE_RANGE_MAP,
UNTRIED_ALGORITHM_GAPS,HEAD_LIFETIME_MAP,TRAILMIX_LAYOUT_DIFF,COMPRESSED_LOG_REDESIGN_SKETCH,EXPERIMENT_FACTORY_RUNBOOK,
PR4_REPLAY}.md`.

**Diagnostics / proofs (`proof/phase3`, `proof/phase4d`):** `laneB_peak_trace.tsv`, `laneC_cmod_add_lowq_trace.tsv`,
`laneD_gcd_tail.tsv`, `laneE_round84_cost_breakdown.tsv`, `ph4_r1_donor_map.tsv`, `ph4_s1_{decomp,borrow}_raw.txt`,
`ph4_s1a_convergence_400k.tsv`, `r3a_lifecycle_model.py` + `r3a_peak_accounting.tsv`, raw `laneB/C_trace_raw.txt`.

**Reports:** the PH3_A–E reports, the PHASE4C/4D result docs, the decision reviews, and **this verdict**.

## 6. Decision
**`ECDSA_PHASE4_ARCHIVED_AT_SATURATION`** — no active experiment carries positive expected value under current
evidence. The local, hybrid, and apply-reuse routes are exhausted with grounded refutations; the only remaining
paths are externally-dependent or score-negative.

**Reopen only if one of:**
1. a new **paper / community idea** surfaces a low-iteration-AND-low-peak inversion primitive;
2. a new **upstream commit** changes the challenge architecture (the local clone is a single squashed commit — a
   full-history fetch could also reopen archaeology);
3. someone provides the missing **PR4 / full-history** data (currently absent — `PR4_REPLAY.md`);
4. a **concrete low-Toffoli/low-peak primitive** is identified (none exists today).

Until then, this analysis holds the ECDSA lab in archived state. Artifacts preserved for any future sprint.

## Compliance
documentation only · no artifacts deleted · no benchmark · no challenge source modification · no nonce/GPU ·
no submission · main untouched (`013f1f7`).
