"""Figure style of the ESANN papers (esannV2.cls): final size, 8 pt serif (Computer Modern), PDF + PNG 300 dpi.

Reduced copy of `src/paper_figs/layout.py` of the companion repository ESANN27_weight_paths (only what Fig. 1 needs).
"""
from pathlib import Path

import matplotlib

TEXTWIDTH_CM = 12.2          # esannV2.cls: \textwidth 12.2 cm
CM = 1 / 2.54
COL = {"G": "#2a6fdb", "ink": "#1c2836", "mute": "#6b6b6b", "harm": "#c0392b"}


def paper_style(font_pt=8):
    matplotlib.rcParams.update({
        "font.family": "serif", "font.serif": ["cmr10", "CMU Serif", "DejaVu Serif"], "mathtext.fontset": "cm",
        "axes.formatter.use_mathtext": True, "axes.unicode_minus": True,
        "font.size": font_pt, "axes.labelsize": font_pt, "axes.titlesize": font_pt, "legend.fontsize": font_pt,
        "xtick.labelsize": font_pt, "ytick.labelsize": font_pt,
        "axes.linewidth": 0.6, "lines.linewidth": 1.1, "lines.markersize": 3.5, "patch.linewidth": 0.5,
        "xtick.major.width": 0.6, "ytick.major.width": 0.6, "xtick.major.size": 2.5, "ytick.major.size": 2.5,
        "xtick.minor.size": 1.5, "ytick.minor.size": 1.5, "xtick.major.pad": 2, "ytick.major.pad": 2,
        "axes.labelpad": 2, "axes.titlepad": 3,
        "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#333333",
        "axes.labelcolor": COL["ink"], "xtick.color": COL["ink"], "ytick.color": COL["ink"],
        "axes.grid": False, "legend.frameon": False, "legend.handlelength": 1.8, "legend.handletextpad": 0.5,
        "legend.columnspacing": 1.2, "legend.borderaxespad": 0.2,
        "figure.facecolor": "white", "axes.facecolor": "white", "savefig.facecolor": "white",
        "pdf.fonttype": 42, "ps.fonttype": 42, "figure.dpi": 100, "savefig.dpi": 300,
    })


def figsize_cm(width_frac=1.0, height_cm=5.0):
    return (TEXTWIDTH_CM * width_frac * CM, height_cm * CM)


def save(fig, name, out, formats=("pdf", "png")):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    for fmt in formats:
        fig.savefig(out / f"{name}.{fmt}", **({"dpi": 300} if fmt == "png" else {}))
    w, h = fig.get_size_inches()
    print(f"{name}: {w / CM:.2f} × {h / CM:.2f} cm -> {out / name}.{{{','.join(formats)}}}")
