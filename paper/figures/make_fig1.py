"""Fig. 1 of the paper: (a) planted buyers, (b) short list by score. Only aggregated CSVs are read.

    python paper/figures/make_fig1.py [--out output]

(a) `2026-11-17_A_R14_groesse_pflanz/pflanz_modelle.csv`, rows seed == "Mittel": AUC of planted (flipped) buyers
    vs. true label-0 customers with 95 % interval (`auc_gekippt`, `_lo`, `_hi`) and of unflipped buyers
    (`auc_ungekippt`, ...) for M3GLVQ, RF, HGB; dashed line at the pre-set target .70.
(b) `2026-11-17_A_R13_reject_filter/vertrieb_top.csv`, stand == "neu" (corrected NAICS matrix): share of buyers among
    the top q % by the score s-bar; dashed line at the base rate (label .51, two decimals as in the text).
Width 12.2 cm (text width of esannV2.cls), height 4 cm. Same code as the figure in the paper, only paths changed.
"""
import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.ticker import FuncFormatter

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import layout as L  # noqa: E402

RES = HERE.parent / "results"
PLANT = RES / "2026-11-17_A_R14_groesse_pflanz" / "pflanz_modelle.csv"
TOP = RES / "2026-11-17_A_R13_reject_filter" / "vertrieb_top.csv"
TARGET = 0.70
MODELS = (("M³GLVQ", r"M$^3$GLVQ"), ("RF", "RF"), ("HGB", "HGB"))


def no_zero(v, nd):
    """Number in paper style without leading zero (.70, .513)."""
    return f"{v:.{nd}f}".replace("0.", ".", 1)


def data_a():
    P = pd.read_csv(PLANT, dtype={"seed": str})
    P = P[P.seed == "Mittel"]
    rows = []
    for key, lab in MODELS:
        q = P[P.modell.str.startswith(key)]
        if len(q) != 1:
            raise SystemExit(f"pflanz_modelle.csv: model {key} not unique ({len(q)} rows)")
        rows.append(dict(lab=lab, **q.iloc[0].to_dict()))
    return pd.DataFrame(rows)


def data_b():
    V = pd.read_csv(TOP)
    V = V[V.stand == "neu"].sort_values("oberste")
    if V.grundrate.nunique() != 1:
        raise SystemExit("vertrieb_top.csv: base rate not unique")
    return V


def make(out):
    import matplotlib.pyplot as plt
    L.paper_style()
    A, V = data_a(), data_b()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=L.figsize_cm(1.0, 4.0), gridspec_kw=dict(width_ratios=[1, 1]))

    x = np.arange(len(A))
    d = 0.13
    for off, pre, lab, col, mk in ((-d, "auc_gekippt", "flipped buyers", L.COL["harm"], "o"),
                                   (+d, "auc_ungekippt", "unflipped buyers", L.COL["mute"], "s")):
        y = A[pre].to_numpy()
        err = np.vstack([y - A[f"{pre}_lo"], A[f"{pre}_hi"] - y])
        ax.errorbar(x + off, y, yerr=err, fmt=mk, color=col, ms=3.2, elinewidth=0.8, capsize=1.8, label=lab)
    ax.axhline(TARGET, ls="--", lw=0.7, color=L.COL["ink"])
    ax.text(len(A) - 0.5, TARGET - 0.006, f"target {no_zero(TARGET, 2)}", ha="right", va="top", color=L.COL["ink"])
    ax.set_xticks(x)
    ax.set_xticklabels(A.lab)
    ax.set_xlim(-0.5, len(A) - 0.5)
    ax.set_ylim(0.48, 0.80)
    ax.set_yticks([.5, .6, .7])
    ax.set_ylabel("AUC vs. label 0")
    ax.legend(loc="upper left", handlelength=1.0, ncol=2, columnspacing=0.8)
    ax.set_title("(a) planted buyers", loc="left")

    q = V.oberste.to_numpy() * 100
    bx.plot(q, V.precision_kaeufer, "o-", color=L.COL["G"], ms=3.2)
    g = float(V.grundrate.iloc[0])
    bx.axhline(g, ls="--", lw=0.7, color=L.COL["ink"])
    bx.text(q.max(), g + 0.005, f"base rate {no_zero(g, 2)}", ha="right", va="bottom", color=L.COL["ink"])
    bx.set_xticks(q)
    bx.set_xticklabels([f"{v:g}" for v in q])
    bx.set_xlabel(r"top $q$ (%)")
    bx.set_ylabel("share of buyers")
    bx.set_ylim(0.48, 0.76)
    bx.set_yticks([.5, .6, .7])
    bx.set_title("(b) short list by score", loc="left")
    for a in (ax, bx):
        a.yaxis.set_major_formatter(FuncFormatter(lambda v, _: no_zero(v, 1)))

    fig.tight_layout(pad=0.3, w_pad=1.2)
    L.save(fig, "fig1", out=out)
    return fig


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(HERE.parents[1] / "output"))
    make(ap.parse_args().out)
