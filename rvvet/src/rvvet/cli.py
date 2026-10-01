"""Command-line interface.

    rvvet vet --rvbank data/rvbank.parquet --star HD297396 [--period 4.26837] [--known 12.9,5.37] [--trend 2]

prints the ladder features as JSON, with a provenance block (package version, content hash
of the source files, input file size and modification time, arguments).
"""
import argparse, hashlib, json, os, sys, time

import numpy as np
import pandas as pd

from . import __version__
from .data import load_star
from .ladder import vet


def source_hash():
    h = hashlib.sha256()
    here = os.path.dirname(os.path.abspath(__file__))
    for f in sorted(os.listdir(here)):
        if f.endswith(".py"):
            h.update(open(os.path.join(here, f), "rb").read())
    return h.hexdigest()[:16]


def main(argv=None):
    ap = argparse.ArgumentParser(prog="rvvet")
    sub = ap.add_subparsers(dest="cmd", required=True)
    v = sub.add_parser("vet", help="run the ladder on one star")
    v.add_argument("--rvbank", required=True, help="parquet file made by scripts/load_rvbank.py")
    v.add_argument("--star", required=True)
    v.add_argument("--period", type=float, default=None, help="vet this period (default: highest peak)")
    v.add_argument("--known", default="", help="comma-separated periods of known signals to remove first")
    v.add_argument("--trend", type=int, default=0, help="degree of a polynomial trend to remove")
    v.add_argument("--clip", type=float, default=15.0, help="gross-outlier clip in robust sigma (0 = off)")
    a = ap.parse_args(argv)
    df = pd.read_parquet(a.rvbank)
    s = load_star(df, a.star, clip_sigma=a.clip or None)
    known = [float(x) for x in a.known.split(",") if x.strip()]
    r = vet(s, period=a.period, known_periods=known, trend=a.trend)
    out = {k: (float(v) if isinstance(v, (np.floating, float)) else v) for k, v in r.items() if not k.startswith("_")}
    st = os.stat(a.rvbank)
    out["provenance"] = dict(rvvet=__version__, source_sha256_16=source_hash(), input=os.path.abspath(a.rvbank),
                             input_bytes=st.st_size, input_mtime=time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(st.st_mtime)),
                             args=vars(a), n_clipped=s.meta.get("n_clipped", 0))
    json.dump(out, sys.stdout, indent=1, default=str)
    print()


if __name__ == "__main__":
    main()
