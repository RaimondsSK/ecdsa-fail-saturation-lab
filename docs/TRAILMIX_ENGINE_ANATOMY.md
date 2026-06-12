# ECDSA_PHASE4D_TRAILMIX_ENGINE_ANATOMY

**Phase 4D · Stage B.** Anatomy of TrailMix's Schrottenloher-style low-qubit point-add engine — the reference
for "operands NOT co-resident with transcript at peak." Source: `_external/trailmix`
(`schrottenloher/{gcd_pack,bezout_unpack,gcd_compress5}.rs`, `notes/{schrottenloher_status,OVERVIEW}.md`,
`kmx_circuit_summaries.md` §1, `circuit.rs` tracker). **Reference, not a score claim for ecdsa.fail.** Items
inferred from headers/notes (not full code reads) are tagged HYPOTHESIS.

## 1. Two-phase structure (vs ecdsa.fail's single co-resident walk)
```
gcd_pack  (Alg 2): forward Euclidean walk → writes a packed garbage bit-vector;  operands u/v SHRINK and their
                   freed bits are recycled into the garbage tape (register-sharing).  Runs BELOW the peak.
apply_bv  (Alg 3): Bezout reconstruction → reads the garbage tape IN REVERSE, runs linear modular updates on
                   (r,s) seeded at (y,0), ends at (0, y·x⁻¹ mod q).  THE PEAK lives here.
```
(`bezout_unpack.rs` header; `kmx_circuit_summaries.md` §1.)

## 2. gcd_pack — operand shrink + register sharing (the low-peak mechanism)
- iterations `expected_iterations(n) = 1.413·n + 2.4·√n`, rounded to a multiple of `DIALOG_M=5`
  (`gcd_pack.rs:expected_iterations`). For n=256: **≈400 iters** (vs ecdsa.fail Kaliski-K2 **258**).
- transcript density: **`DIALOG_PACK=8` bits per `DIALOG_M=5` iters = 1.6 bits/iter** (M=5 base-3 packing,
  `gcd_compress5`). For n=256: garbage ≈ **640 bits**.
- **register sharing:** `u_padding(n) = 2.3·√n` (~37 for n=256) pads `u`,`v` so that **as the operands shrink,
  the vacated bits become valid garbage-tape storage** (`gcd_pack.rs` doc: "register-shared u,v … freed u/v
  bits feed the garbage allocator"). This is the architectural version of R1's failed local "donor recycle" —
  here it is *designed in*, so the forward walk's live count stays below the peak.
- adders: the GCD `csub` uses the **full Gidney 2n adder with `GCD_CSUB_VENTS = usize::MAX`** — because
  "the inversion's peak is set by `apply_bv`, NOT the GCD, so the GCD csub has full headroom" (gcd_pack.rs:GCD_CSUB_VENTS).
  **This is the inverse of ecdsa.fail**, whose GCD walk *is* the peak and is therefore scratch-starved.

## 3. apply_bv — where the peak lives
- reads the garbage tape in reverse; the live set is the **reconstruction registers `x2`,`y2` (≈257 each) +
  the garbage tape (640/648/670 depending on M)** → `670 + 514 + 7 ≈ 1191q` (`schrottenloher_status.md`).
- **the GCD operands `u/v` are already freed/recycled by now** — they are NOT co-resident with the tape at the
  peak. That is the whole point.
- `apply_bv` stays on Cuccaro 3n (no venting) because *it* is the peak; cost trade is the qubit/Toffoli exchange.

## 4. Cost profile (the decisive caveat for ecdsa.fail)
| config | qubits | Toffoli | **score = T×q** |
|---|---:|---:|---:|
| **ecdsa.fail HEAD `013f1f7`** | **1302** | **1,458,957** | **1,899,562,014** |
| TrailMix low-qubit (`emit_test_ec_add_schrottenloher`) | 1169 | ~2,090,000 | **~2.44×10⁹** |
| TrailMix low-tof | 1412 | ~1,900,000 | ~2.68×10⁹ |

**TrailMix's lower peak comes WITH higher Toffoli (~2.09M vs 1.46M).** Its published configs **score WORSE**
than ecdsa.fail. So **a full Schrottenloher port is NOT a score win** — Schrottenloher trades ecdsa.fail's
low-Toffoli Kaliski math for a low-peak layout at +43% Toffoli. The redesign must keep **both** ecdsa.fail's
low Toffoli **and** a low peak — neither existing engine does both.

## 5. The prove_zero / ghost / phase-lattice discipline (de-risks any redesign)
- **`free_qubit` always runs `prove_zero`** (`circuit.rs:2774`): every free is gated by a structural proof the
  qubit is `|0>`. `declare_identity` / `declare_copy_of` (`circuit.rs:3106`) inject symbolic facts *after* a
  64-shot sim check (`OVERVIEW.md` phase-lattice). The **ghost / spooky-pebble** API tracks measurement-uncompute
  obligations; the **run-backward debugger** localizes the op that broke an invariant.
- **Why it matters for ecdsa.fail:** a redesign that recycles operand bits into the transcript (R2/R3) needs
  exactly this — a proof that the donated lane is `|0>` across the transcript window and restored before its
  next operand use. ecdsa.fail's `sim.rs` can do the 64-shot check, but it lacks TrailMix's *systematic*
  prove-zero-on-free gate; porting that discipline (as a verification overlay) would make an aggressive
  operand-recycle layout safe to validate.

## 6. The transferable idea (for Stage C)
**Separate the GCD walk (operand-heavy, transcript-writing, operands shrinking) from the transcript-apply phase
(transcript-heavy, operands freed), recycling shrunk-operand bits into the transcript — WITHOUT adopting
Schrottenloher's higher-Toffoli engine.** That is the **R2 hybrid**: ecdsa.fail Kaliski math (low Toffoli) +
TrailMix's pack/apply *layout* (low peak). De-risk it first at toy width (R3). See
`ECDSA_PHASE4D_REDESIGN_ROUTE_MATRIX.md`.
