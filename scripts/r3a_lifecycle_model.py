#!/usr/bin/env python3
"""
ECDSA Phase 4D R3a — toy classical register-lifetime accounting.

MECHANISM TEST ONLY (an accounting model, NOT a reversible-circuit result).
Tests whether a pack/apply SPLIT layout lowers the peak simultaneous-live
register count vs the current CO-RESIDENT layout, at toy widths n=16/32/64,
while the apply phase reconstructs the correct modular inverse from the
transcript alone (operands freed).

Grounding:
- The engine modelled is the Kaliski binary almost-inverse (ecdsa.fail's family).
- KEY FACT (exact, not hypothesis): the Bezout (r,s) updates depend ONLY on the
  per-step branch case, not on the operand values u,w. So a separate APPLY phase
  can replay the transcript to compute r,s with u,w already freed. We verify the
  reconstructed inverse == pow(v,-1,p_toy) for every sample.
- Register-lifetime ASSUMPTIONS (HYPOTHESIS, tagged): transcript density
  bits_per_step, apply-phase scratch model. Reported with a sensitivity sweep so
  the conclusion's robustness is explicit.

NO challenge source, NO circuit, NO benchmark, NO nonce/GPU.
"""
import sys

def bitlen(x): return x.bit_length()

def kaliski_pack(p, v):
    """Forward Kaliski almost-inverse. Returns (transcript, k, per_step bitlens).
    transcript[i] in {0,1,2,3} = the branch case. r,s NOT computed here (apply does)."""
    u, w = p, v
    k = 0
    tr = []
    blens = []  # (bits_u, bits_w) at each step entry
    while w > 0:
        blens.append((bitlen(u), bitlen(w)))
        if u % 2 == 0:
            u //= 2; case = 0
        elif w % 2 == 0:
            w //= 2; case = 1
        elif u > w:
            u = (u - w) // 2; case = 2
        else:
            w = (w - u) // 2; case = 3
        tr.append(case); k += 1
    return tr, k, blens

def kaliski_apply(p, transcript, k):
    """APPLY phase: reconstruct the inverse from the transcript ALONE (no u,w).
    The r,s recurrence depends only on the case -> operands are freed."""
    r, s = 0, 1
    for case in transcript:
        if case == 0:   s *= 2
        elif case == 1: r *= 2
        elif case == 2: r += s; s *= 2
        else:           s += r; r *= 2
    # standard Kaliski correction: result = p - (r mod p), then divide by 2^k
    r %= p
    res = (p - r) % p
    inv2 = pow((p + 1) // 2, 1, p)  # 2^-1 mod p
    for _ in range(k):
        res = (res * inv2) % p
    return res

def peak_accounting(p, v, n, bits_per_step, apply_scratch_frac):
    """Returns (co_resident_peak, split_peak, components, recon_ok)."""
    tr, k, blens = kaliski_pack(p, v)
    inv = kaliski_apply(p, tr, k)
    recon_ok = (inv == pow(v, -1, p))

    # Registers are fixed-width n each (a circuit cannot resize dynamically).
    U = n; W = n            # operand registers
    R = 2 * n               # Bezout (r,s), each up to n bits
    T_total = max(1, (k * bits_per_step + 7) // 8 * 8 // 8)  # packed transcript bits (~bits_per_step/step)
    T_total = max(1, round(k * bits_per_step))
    # per-step scratch (body carries+gated ~ 2*width-1), width = live operand width
    def width(i):
        bu, bw = blens[i]; return max(2, max(bu, bw))
    def Sp(i): return 2 * width(i) - 1
    def Twritten(i): return max(0, round((i + 1) * bits_per_step))   # transcript bits written by step i
    def freed(i):
        bu, bw = blens[i]; return (U - bu) + (W - bw)               # idle operand high bits

    # CO-RESIDENT: operands + full transcript register + per-step scratch, all co-resident.
    # (ecdsa.fail borrows UNWRITTEN transcript cells for scratch -> credit that borrow.)
    co = 0
    for i in range(k):
        unwritten = max(0, T_total - Twritten(i))
        live = U + W + T_total + max(0, Sp(i) - unwritten)
        co = max(co, live)

    # SPLIT pack: operands live, transcript HOSTED in freed operand bits, pack scratch.
    pack = 0
    for i in range(k):
        host_overflow = max(0, Twritten(i) - freed(i))   # transcript beyond freed operand space
        live = U + W + host_overflow + Sp(i)
        pack = max(pack, live)
    # SPLIT apply: operands FREED; Bezout R + full transcript + apply scratch.
    Sa = max(2, round(apply_scratch_frac * n))            # apply-phase scratch (HYPOTHESIS)
    apply = R + T_total + Sa
    split = max(pack, apply)

    # --- alternative framings (assumption sensitivity) ---
    # PESSIMISTIC co-resident: NO scratch-borrow credit (scratch is fully fresh).
    co_noborrow = max(U + W + T_total + Sp(i) for i in range(k))
    # OPTIMISTIC split: apply reconstructs INTO the freed operand registers
    # (R reuses the 2n operand pool -> adds no new qubits), like TrailMix apply_bv
    # writing into the existing point registers. (HYPOTHESIS — the TrailMix mechanism.)
    apply_reuse = max(U + W, T_total) + Sa
    split_optimistic = max(pack, apply_reuse)

    comp = dict(k=k, T_total=T_total, operand_live_peak=U+W,
                scratch_live_peak=max(Sp(i) for i in range(k)),
                pack_peak=pack, apply_peak=apply,
                co_noborrow=co_noborrow, split_optimistic=split_optimistic)
    return co, split, comp, recon_ok

# toy odd prime moduli (deterministic)
PRIMES = {16: 65521, 32: 4294967291, 64: 18446744073709551557}
def main():
    bits_per_step = float(sys.argv[1]) if len(sys.argv) > 1 else 2.5   # ecdsa.fail ~645/258=2.5; TrailMix packed ~1.6
    apply_scratch_frac = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0  # apply scratch ~ n (Cuccaro). HYPOTHESIS.
    SAMPLES = 2000
    rows = []
    print(f"# R3a toy lifecycle accounting (ACCOUNTING MODEL, not a circuit result).")
    print(f"# params: bits_per_step={bits_per_step} (HYP) apply_scratch_frac={apply_scratch_frac} (HYP) samples/width={SAMPLES}")
    print("n\tco_resident_peak\tsplit_peak\tdelta\ttranscript_size\toperand_live_peak\tscratch_live_peak\tapply_peak\tpack_peak\trecon_ok\trecon_fail\tnoninvertible\tsamples")
    seed = 0x4D3A_2026
    for n, p in PRIMES.items():
        co_max = split_max = 0; ok = fail = nonv = 0
        comp_at_comax = None; comp_at_splitmax = None
        for j in range(SAMPLES):
            seed = (seed * 6364136223846793005 + 1442695040888963407) & ((1 << 64) - 1)
            v = (seed % (p - 1)) + 1
            if v % p == 0:
                nonv += 1; continue
            co, split, comp, recon_ok = peak_accounting(p, v, n, bits_per_step, apply_scratch_frac)
            if recon_ok: ok += 1
            else: fail += 1
            if co > co_max: co_max = co; comp_at_comax = comp
            if split > split_max: split_max = split; comp_at_splitmax = comp
        c = comp_at_comax; cs = comp_at_splitmax
        print(f"{n}\t{co_max}\t{split_max}\t{co_max-split_max}\t{c['T_total']}\t{c['operand_live_peak']}\t{c['scratch_live_peak']}\t{cs['apply_peak']}\t{cs['pack_peak']}\t{ok}\t{fail}\t{nonv}\t{SAMPLES}")
        rows.append((n, co_max, split_max, ok, fail, cs['co_noborrow'], cs['split_optimistic']))
    # decision under the model-as-written
    all_recon = all(r[4] == 0 for r in rows)
    all_lower = all(r[1] > r[2] for r in rows)
    # decision under the OPTIMISTIC framing (apply reuses operand pool, co-resident no borrow credit)
    opt_lower = all(r[5] > r[6] for r in rows)
    print(f"# framing[model-as-written]: split_lower_all={all_lower}")
    print(f"# framing[optimistic (apply reuses operands, co no-borrow)]: split_optimistic_lower_all={opt_lower}")
    print(f"# co_noborrow vs split_optimistic per n: " + ", ".join(f"n{r[0]}:{r[5]}vs{r[6]}" for r in rows))
    if not all_recon:
        verdict = "REFUTED"
    elif all_lower == opt_lower:
        verdict = "PASS" if all_lower else "REFUTED"
    else:
        verdict = "INCONCLUSIVE"   # peak comparison flips with grounding assumptions
    print(f"# DECISION(bits_per_step={bits_per_step},apply_scratch_frac={apply_scratch_frac}): recon_clean={all_recon} -> {verdict}")

if __name__ == "__main__":
    main()
