"""Record how the paper's numbers depend on the scikit-learn version, and write the macros quoted in
Sect. 8.1 (paper/numbers_versions.tex).

The paper's numbers come from the environment pinned in requirements-paper.txt (scikit-learn 1.8.0).
scikit-learn 1.9 changed how GroupKFold assigns stars to folds, which changes the out-of-fold
classifier scores. To regenerate results/sklearn19_sensitivity.json, run analyze.py in a copy of the
repository with scikit-learn 1.9.x installed and pass that copy's results/numbers.json and
paper/numbers.tex:

    python rvvet/scripts/version_sensitivity.py --other-json OTHER/results/numbers.json \
        --other-tex OTHER/paper/numbers.tex --other-version 1.9.1

Without arguments the script only rewrites paper/numbers_versions.tex from the stored JSON.
"""
import argparse, json, math, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
JSON = os.path.join(ROOT, "results", "sklearn19_sensitivity.json")
CLASSIFIERS = ("cv_logistic", "cv_boosting", "cv_boosting_with_prior_features",
               "cv_boosting_no_indicators", "cv_boosting_no_proxy")


def macros(path):
    return {m.group(1): m.group(2) for m in
            re.finditer(r"\\newcommand\{\\(\w+)\}\{(.*?)\}\s*$", open(path).read(), flags=re.M)}


def main():
    a = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    a.add_argument("--other-json"); a.add_argument("--other-tex"); a.add_argument("--other-version")
    a = a.parse_args()
    if a.other_json:
        rel = macros(os.path.join(ROOT, "paper", "numbers.tex")); new = macros(a.other_tex)
        nj_rel = json.load(open(os.path.join(ROOT, "results", "numbers.json"))); nj_new = json.load(open(a.other_json))
        full = {k: {"paper": nj_rel[k]["auc"], "other": nj_new[k]["auc"], "delta": nj_new[k]["auc"] - nj_rel[k]["auc"]}
                for k in CLASSIFIERS + ("cv_n_only",)}
        out = {"other_scikit_learn": a.other_version,
               "what": "Paper numbers (scikit-learn 1.8.0) against a rerun with another scikit-learn version, "
                       "everything else pinned as in requirements-paper.txt. scikit-learn 1.5.2, 1.6.1, 1.7.2 and "
                       "1.8.0 reproduce the paper exactly; 1.9 changed GroupKFold's assignment of stars to folds.",
               "simulation_cv_auc_full_precision": full,
               "max_abs_auc_change_classifiers": max(abs(full[k]["delta"]) for k in CLASSIFIERS),
               "macros_that_change": {k: {"paper": rel[k], "other": new[k]} for k in sorted(rel) if rel[k] != new[k]},
               "n_macros_total": len(rel)}
        json.dump(out, open(JSON, "w"), indent=1)
    d = json.load(open(JSON))
    ch = d["macros_that_change"]
    lines = ["% Written by rvvet/scripts/version_sensitivity.py from results/sklearn19_sensitivity.json",
             r"\newcommand{\nmVerOther}{%s}" % d["other_scikit_learn"],
             r"\newcommand{\nmVerAucMax}{%.3f}" % (math.ceil(d["max_abs_auc_change_classifiers"] * 1000) / 1000),
             r"\newcommand{\nmVerNMacros}{%d}" % len(ch),
             r"\newcommand{\nmVerBNoIndPaper}{%s}" % ch["nmBAucNoInd"]["paper"],
             r"\newcommand{\nmVerBNoIndOther}{%s}" % ch["nmBAucNoInd"]["other"]]
    open(os.path.join(ROOT, "paper", "numbers_versions.tex"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
