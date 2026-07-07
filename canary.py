#!/usr/bin/env python3
"""Canary generation + anchor records for the FARADAY harness.

FARADAY watches the AIR-GAP membrane: your marker planted INSIDE a boundary that
was supposed to hold, appearing OUTSIDE it. The cage that should have contained
it, leaked. Its siblings watch other routes (published page, weights, human
relay, live inference); this one watches a gap that was designed to have no path.

The axis that makes FARADAY honest is ISOLATION -- the claimed containment of the
enclave the marker was planted in:
  - "air_gapped" : claimed to have NO egress path. A marker of this enclave found
                   outside is a BREACH -- the gap failed.
  - "connected"  : has a legitimate path out (a sync, a share, an export). A
                   marker found outside is EXPECTED, not a breach -- gated.
  - "held_out"   : planted NOWHERE. A control. If it surfaces outside, the harness
                   is fabricating, and the run is invalid.

Each air-gapped enclave also declares WHICH KIND of gap it is, so a breach can
name what failed (after the air-gap-ladder's four kinds):
  distance | sovereignty | design | impermanence
"""
from __future__ import annotations
import secrets, hashlib, time
from dataclasses import dataclass

ENTROPY_BITS = 128
HEX_LEN = ENTROPY_BITS // 4       # 32 hex chars, ~zero prior probability
GAP_KINDS = ("distance", "sovereignty", "design", "impermanence")


def new_value(bits: int = ENTROPY_BITS) -> str:
    return secrets.token_hex(bits // 8)


def sha256_hex(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()


@dataclass
class Canary:
    value: str                          # the high-entropy marker
    isolation: str = "air_gapped"       # air_gapped | connected | held_out
    enclave: str = ""                   # which boundary it was planted in
    gap_kind: str = "design"            # distance | sovereignty | design | impermanence
    planted_utc: str | None = None      # when it went inside (None for held_out)
    context: str = ""
    kind: str = "canary"

    def __post_init__(self):
        self.canonical = f"{self.kind}|{self.value}|{self.isolation}"
        self.hash = "sha256:" + sha256_hex(self.canonical)

    @property
    def held_out(self) -> bool:
        return self.isolation == "held_out"

    def anchor(self) -> dict:
        return {
            "primitive": self.kind,
            "canonical": self.canonical,
            "hash": self.hash,
            "value": self.value,
            "isolation": self.isolation,
            "held_out": self.held_out,
            "enclave": self.enclave,
            "gap_kind": self.gap_kind,
            "planted_utc": self.planted_utc,
            "context": self.context,
        }


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def make_airgapped(enclave="", gap_kind="design", context="", planted_utc=None, value=None) -> Canary:
    """A marker inside an enclave claimed to have NO egress path."""
    assert gap_kind in GAP_KINDS, f"gap_kind must be one of {GAP_KINDS}"
    return Canary(value or new_value(), isolation="air_gapped", enclave=enclave,
                  gap_kind=gap_kind, planted_utc=planted_utc or _now(), context=context)


def make_connected(enclave="", context="", planted_utc=None, value=None) -> Canary:
    """A marker inside an enclave that HAS a legitimate path out."""
    return Canary(value or new_value(), isolation="connected", enclave=enclave,
                  planted_utc=planted_utc or _now(), context=context)


def make_held_out(context="control") -> Canary:
    """A marker placed NOWHERE -- exists only as a control arm."""
    return Canary(new_value(), isolation="held_out", context=context)
