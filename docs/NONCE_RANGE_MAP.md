# ECDSA_PHASE4_NONCE_RANGE_MAP

**Phase 4A · Workstreams 1 + 6.** Every `DIALOG_TAIL_NONCE` value used historically, classified into ranges,
with the conditional-compute policy that governs any future nonce use. **No blind nonce search** — this is a
map + policy, not a search. Source: `lab.db` nonces table (26 distinct), Phase 2 `NONCE_STRATEGY.md`, memory notes.

## What a nonce is here
`DIALOG_TAIL_NONCE` = a fixed-length 96-op identity tail that reseeds the SHAKE256-derived 9024-shot test set
**without changing the circuit's action, Toffoli count, or peak**. It slides an otherwise-correct truncation
off "hard-input islands". It is **not** a cryptographic signing nonce — there is no key-recovery surface.

## Historically-used nonces (26 distinct, range [1, 31,415,926,535])
| range bucket | values | context |
|---|---|---|
| **inherited HEAD** | `10016000183` | the live baseline nonce (`013f1f7`); P2 round1 ranked it 12th/16 (7 class fails) |
| near-inherited | `10016000182`, `10016000200` | P2 round1 neighbours (5, 6 class) |
| small ints | `1`, `3`, `7`, `17`, `42`, `256`, `1024`, `65537` | P2 round1/round2 prefilter |
| decade scales | `1000000`, `1000007`, `999983`, `1000000000`, `10000000000` | P2 round1/round2 |
| powers/structured | `2147483647` (2³¹−1), `8589934592` (2³³), `31415926535`, `13371337`, `271828`, `314159` | P2 round2 |
| date-coded | `2026060801`–`2026060804` | P2 round1 |
| **historical winners (other commits)** | `431581` (our `436b516`), `721381` (an external contributor `a66b042`), `2432` (our `lowq0`) | memory_note — NOT in local nonces table; never re-evaluated at HEAD |

## Key empirical findings (Phase 2 Lane 2) — why blind nonce search is banned
1. **Distribution is FLAT, not bimodal** — full-9024 confirmations all land 19–27 class fails, statistically
   identical to the inherited baseline. No "easy island" cluster among 26 sampled nonces.
2. **2048-shot prefilter does NOT predict 9024 survival** — nonce `1000000` went 1/1 @2048 → 19/7 @9024.
3. The historical winners' nonces (`431581`, `721381`, `2432`) were each found for a *specific structural
   candidate*; they do not transfer to a different op-stream (each structural change reseeds).

## Smarter nonce map (for Workstream 6 — used ONLY when a structural candidate earns it)
| tier | range | when to draw from it |
|---|---|---|
| T0 — inherited + neighbours | `10016000183 ± small` | first check: does the candidate land clean at the inherited island? |
| T1 — historical winners | `431581, 721381, 2432` | candidates structurally close to those eras |
| T2 — small / power-of-two | `1..65537`, `2^k` | cheap broad coverage |
| T3 — candidate-specific ranked | computed per-candidate via a **measured** 2048→9024 correlation | only if T3's prefilter is shown to correlate for *this* candidate |
| T4 — random sparse | bounded ≤ operator-set cap | last resort, the research lead-approved only |

## Conditional nonce policy (gate — all must hold before ANY nonce use)
Per the sprint plan Workstream 6:
1. a **structural candidate** that lowers score *if valid* exists;
2. it **compiles**;
3. diagnostics show **no broad semantic error** (only an island miss, not a real bug);
4. full validation fails **only** as a Fiat-Shamir island miss;
5. quick filters have a **measured correlation** to full validation *for this specific candidate*;
6. **the research lead approves** a bounded search (explicit cap, no unbounded sweep).
**Stop rules:** no unbounded sweep · no score claim from short shots · no "looks promising" without full
9024-shot proof. Until a structural candidate exists, the allowed nonce action is **zero**.

## Gaps to close in Phase 4
- The 3 historical-winner nonces are memory-note-only; if the operator exports submission notes, verify them.
- Other competitors' nonces are unknown (Workstream 4 community scout).
