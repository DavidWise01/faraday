#!/usr/bin/env python3
"""Escapes = Detection + Comparison.

An ESCAPE is a place OUTSIDE your enclaves where you found text -- a public dump,
another network, a device that should never have seen the enclave's contents. Each
escape records where it was seen, when, and whether it is genuinely outside the
boundary or still within it.

  where of an escape:
    "outside" : beyond the enclave boundary (the real case -- the gap was crossed).
    "inside"  : still within the boundary (not a breach; the marker never left).

Detection is the family's stands-alone rule: a canary counts only when it is not
flanked by [A-Za-z0-9_-].
"""
from __future__ import annotations
import re
from dataclasses import dataclass


def scan_text(text: str, values):
    """Return the canary values that stand ALONE in text (word-boundary)."""
    found = []
    for v in values:
        if not v:
            continue
        pat = r"(?<![A-Za-z0-9_-])" + re.escape(v) + r"(?![A-Za-z0-9_-])"
        if re.search(pat, text):
            found.append(v)
    return found


@dataclass
class Escape:
    text: str                    # what you found out in the wild
    where: str = "outside"       # outside | inside
    observed_utc: str | None = None
    source: str = ""             # where you found it

    def canaries_in(self, values):
        return scan_text(self.text, values)
