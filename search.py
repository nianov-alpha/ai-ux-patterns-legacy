#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai-ux — standalone BM25 search over the AI-Native Interface Patterns database.

Zero dependencies (Python 3.x standard library only).

Usage:
    python search.py "<query>" [-n <max_results>]
    python search.py --categories        # list categories with counts

The BM25 implementation is adapted from the ui-ux-pro-max toolkit
(© Next Level Builder, MIT). See NOTICE.md. The ai-ux pattern database
and this file are © Azka, MIT.
"""

import sys
import csv
import re
import argparse
from math import log
from pathlib import Path
from collections import defaultdict

DATA = Path(__file__).resolve().parent / "data" / "ai-ux-patterns.csv"

SEARCH_COLS = ["Pattern Category", "Pattern Name", "Keywords", "Problem", "When to Use"]
OUTPUT_COLS = ["Pattern Category", "Pattern Name", "Keywords", "Problem", "Solution",
               "Do", "Don't", "Code Example", "Anti-Pattern", "When to Use",
               "Trust Impact", "Severity"]


class BM25:
    """BM25 ranking (k1=1.5, b=0.75)."""

    def __init__(self, k1=1.5, b=0.75):
        self.k1, self.b = k1, b
        self.corpus, self.doc_lengths = [], []
        self.avgdl, self.N = 0, 0
        self.idf = {}
        self.doc_freqs = defaultdict(int)

    @staticmethod
    def tokenize(text):
        text = re.sub(r"[^\w\s]", " ", str(text).lower())
        return [w for w in text.split() if len(w) >= 2]

    def fit(self, documents):
        self.corpus = [self.tokenize(d) for d in documents]
        self.N = len(self.corpus)
        if self.N == 0:
            return
        self.doc_lengths = [len(d) for d in self.corpus]
        self.avgdl = sum(self.doc_lengths) / self.N
        for doc in self.corpus:
            for word in set(doc):
                self.doc_freqs[word] += 1
        for word, freq in self.doc_freqs.items():
            self.idf[word] = log((self.N - freq + 0.5) / (freq + 0.5) + 1)

    def score(self, query):
        q = self.tokenize(query)
        scores = []
        for idx, doc in enumerate(self.corpus):
            s, dl = 0.0, self.doc_lengths[idx]
            tf = defaultdict(int)
            for w in doc:
                tf[w] += 1
            for t in q:
                if t in self.idf:
                    f = tf[t]
                    s += self.idf[t] * (f * (self.k1 + 1)) / (
                        f + self.k1 * (1 - self.b + self.b * dl / self.avgdl))
            scores.append((idx, s))
        return sorted(scores, key=lambda x: x[1], reverse=True)


def load_rows():
    if not DATA.exists():
        raise FileNotFoundError(f"Data file not found: {DATA}")
    with open(DATA, encoding="utf-8") as f:
        return list(csv.DictReader(f))


def search(query, max_results=3):
    rows = load_rows()
    docs = [" ".join(str(r.get(c, "")) for c in SEARCH_COLS) for r in rows]
    bm = BM25()
    bm.fit(docs)
    out = []
    for idx, sc in bm.score(query)[:max_results]:
        if sc > 0:
            r = rows[idx]
            out.append({c: r.get(c, "") for c in OUTPUT_COLS if c in r})
    return out


def categories():
    counts = {}
    for r in load_rows():
        c = r.get("Pattern Category", "").strip()
        if c:
            counts[c] = counts.get(c, 0) + 1
    return dict(sorted(counts.items()))


def _format(results, query):
    lines = [f"# ai-ux search — \"{query}\"  ({len(results)} result(s))"]
    for i, r in enumerate(results, 1):
        lines.append(f"\n## {i}. {r.get('Pattern Name','')}  [{r.get('Pattern Category','')}]")
        for k in OUTPUT_COLS:
            if k in ("Pattern Name", "Pattern Category"):
                continue
            v = r.get(k, "")
            if str(v).strip():
                lines.append(f"- **{k}:** {v}")
    if not results:
        lines.append("\n(no matches — try broader keywords)")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="Search the ai-ux interface-pattern database.")
    ap.add_argument("query", nargs="?", help="search query")
    ap.add_argument("-n", "--max-results", type=int, default=3)
    ap.add_argument("--categories", action="store_true", help="list categories with counts")
    args = ap.parse_args()

    if args.categories:
        cats = categories()
        total = sum(cats.values())
        print(f"ai-ux — {total} patterns across {len(cats)} categories:")
        for c, n in cats.items():
            print(f"  {c}: {n}")
        return
    if not args.query:
        ap.error("provide a query, or use --categories")
    print(_format(search(args.query, args.max_results), args.query))


if __name__ == "__main__":
    main()
