#!/usr/bin/env python3
"""Verify-first self-test. Plant markers in enclaves, look for them outside, and
prove the harness (1) certifies an AIR-GAPPED enclave's marker found outside as a
BREACH, tagged with the enclave and gap kind, corroborated by how many sightings;
(2) does NOT manufacture breaches on the held-out arm; (3) GATES a CONNECTED
enclave's marker (it had a legitimate path); (4) ignores a still-inside sighting;
(5) gates an impossible pre-plant sighting; (6) refuses a run with no control arm;
(7) only matches a marker that stands ALONE. No network, no keys.
"""
from __future__ import annotations
from canary import make_airgapped, make_connected, make_held_out
from registry import Registry
from escape import Escape, scan_text
from harness import run_panel

fails = 0
def check(cond, msg):
    global fails
    print(("ok  · " if cond else "FAIL· ") + msg)
    fails += 0 if cond else 1


PLANT = "2026-01-01T00:00:00Z"


def outside(canaries, where="outside", observed="2026-03-01T00:00:00Z", source="wild"):
    body = "found in a public dump: " + " ".join(c.value for c in canaries) + " <<eof"
    return Escape(text=body, where=where, observed_utc=observed, source=source)


# 1. Clean: air-gapped enclaves' markers found outside -> BREACH; held-out never appear.
reg = Registry()
gaps = [make_airgapped(enclave=f"vault-{i}", gap_kind=k, planted_utc=PLANT)
        for i, k in enumerate(("distance", "sovereignty", "design"))]
held = [make_held_out() for _ in range(3)]
for c in gaps + held:
    reg.add(c)
escapes = [
    outside([gaps[0]], source="dump A"),
    outside([gaps[0]], source="dump B"),   # gaps[0] corroborated by TWO sightings
    outside([gaps[1]], source="foreign net"),
    outside([gaps[2]], source="lost laptop"),
]
v = run_panel(reg, escapes)
check(v["control_fpr"] == 0, f"held-out FPR is 0 (got {v['control_fpr']})")
check(len(v["certified_breaches"]) == 3, f"all 3 air-gapped markers certified as breaches (got {len(v['certified_breaches'])})")
check(v["certified_breaches"].get(gaps[0].value, {}).get("sightings") == 2, "breach[0] corroborated by 2 sightings")
check(v["certified_breaches"].get(gaps[1].value, {}).get("gap_kind") == "sovereignty", "breach names which kind of gap failed")
check("CLEAN" in v["verdict"], "verdict CLEAN when controls pass")
check(v["base_rate"] < 1e-30, f"chance base-rate negligible ({v['base_rate']:.1e})")

# 2. Isolation gate: a CONNECTED enclave's marker outside -> it had a path -> not a breach.
reg2 = Registry()
conn = make_connected(enclave="synced-share", planted_utc=PLANT)
reg2.add(conn); reg2.add(make_held_out())
v2 = run_panel(reg2, [outside([conn], source="expected export")])
check(conn.value in v2["expected_gated"], "connected enclave's marker is EXPECTED-gated (had a path)")
check(len(v2["certified_breaches"]) == 0, "expected leak is not certified as a breach")

# 3. Inside gate: a marker seen still WITHIN the boundary is not a breach.
reg3 = Registry()
g3 = make_airgapped(enclave="vault", planted_utc=PLANT)
reg3.add(g3); reg3.add(make_held_out())
v3 = run_panel(reg3, [outside([g3], where="inside")])
check(len(v3["certified_breaches"]) == 0, "still-inside sighting is not certified")

# 4. Impossible gate: observed outside BEFORE it was planted inside.
reg4 = Registry()
g4 = make_airgapped(enclave="vault", planted_utc="2026-06-01T00:00:00Z")
reg4.add(g4); reg4.add(make_held_out())
v4 = run_panel(reg4, [outside([g4], observed="2026-01-01T00:00:00Z")])
check(g4.value in v4["impossible"], "pre-plant sighting is IMPOSSIBLE (gated)")

# 5. Fabrication: a held-out marker turns up outside -> control catches it.
reg5 = Registry()
g5 = make_airgapped(enclave="vault", planted_utc=PLANT); h5 = make_held_out()
reg5.add(g5); reg5.add(h5)
v5 = run_panel(reg5, [outside([g5]), outside([h5], source="fabricated")])
check(bool(v5["control_fpr"]) and v5["control_fpr"] > 0, f"fabricated escape spikes held-out FPR ({v5['control_fpr']})")
check("INVALID" in v5["verdict"], "fabricated/contaminated pipeline -> verdict INVALID")
check(len(v5["certified_breaches"]) == 0, "invalid run certifies nothing")

# 6. Performative guard: no held-out arm -> INVALID.
reg6 = Registry()
g6 = make_airgapped(enclave="vault", planted_utc=PLANT); reg6.add(g6)
v6 = run_panel(reg6, [outside([g6])])
check("INVALID" in v6["verdict"], "no held-out arm -> INVALID (performative guard)")

# 7. Word-boundary.
val = make_airgapped().value
check(scan_text(val, [val]) == [val], "a marker standing alone is detected")
check(scan_text("q" + val + "q", [val]) == [], "a marker inside a larger token is NOT detected")

print("\n" + ("SOME CHECKS FAILED" if fails else "all faraday-harness checks passed"))
raise SystemExit(1 if fails else 0)
