#!/usr/bin/env python3
"""Shared matplotlib style settings for compact blue-green scientific plots."""

from pathlib import Path

import matplotlib.pyplot as plt


class PlotConfig:
    """Reusable plot configuration values."""

    # Figure and axes size, in inches.
    AXES_WIDTH = 1.5
    AXES_HEIGHT = 1.5
    AXES_ASPECT = 1.0
    FIG_WIDTH = 2.2
    FIG_HEIGHT = 2.2

    # Line widths, in points.
    MAIN_LINE_WIDTH = 1.0
    AXIS_LINE_WIDTH = 0.75
    MINOR_LINE_WIDTH = 0.5

    # Fonts.
    FONT_FAMILY = ["Arial", "Arial Unicode MS", "DejaVu Sans"]
    TITLE_FONTSIZE = 8
    TITLE_FONTWEIGHT = "normal"
    LABEL_FONTSIZE = 8
    LABEL_FONTWEIGHT = "normal"
    TICK_FONTSIZE = 8
    LEGEND_FONTSIZE = 8

    # Axis label spacing, in multiples of label font size.
    XLABEL_PAD = 0.5
    YLABEL_PAD = 0.5

    # Ticks.
    TICK_LENGTH_MAJOR = 2.5
    TICK_LENGTH_MINOR = 1.5
    TICK_WIDTH = MINOR_LINE_WIDTH

    # Blue-green palette with warm accents for warnings or highlights.
    COLORS = {
        "Primary": "#367DB0",
        "Secondary": "#9DC7DD",
        "Accent": "#9ED17B",
        "Warning": "#F7941D",
        "Danger": "#ED1C24",
        "Purple": "#8B5CF6",
    }
    COLOR_LIST = ["#367DB0", "#9DC7DD", "#9ED17B", "#F7941D", "#ED1C24", "#8B5CF6"]
    COLOR_PRIMARY = "#367DB0"
    COLOR_SECONDARY = "#9DC7DD"
    COLOR_ACCENT = "#9ED17B"
    COLOR_WARNING = "#F7941D"
    COLOR_DANGER = "#ED1C24"
    COLOR_PURPLE = "#8B5CF6"
    COLOR_BLACK = "black"
    COLOR_GRAY = "#666666"

    # Stable colors for two-condition comparisons.
    PAIR_COLOR_A = COLOR_PRIMARY
    PAIR_COLOR_B = COLOR_ACCENT

    # Scatter plots.
    SCATTER_SIZE = 30
    SCATTER_ALPHA = 0.75
    SCATTER_EDGE_COLOR = "none"
    SCATTER_EDGE_WIDTH = 0
    SCATTER_JITTER = 0.06

    # Markers on point-line plots may keep a darker edge.
    LINE_MARKER_EDGE_DARKEN_FACTOR = 0.65

    # Mean lines.
    MEAN_LINE_WIDTH = MAIN_LINE_WIDTH
    MEAN_LINE_EXTENSION = 0.25

    # Bar charts.
    BAR_WIDTH = 0.35
    BAR_WIDTH_SINGLE = 0.5
    BAR_ALPHA = 0.8
    BAR_EDGE_COLOR = "black"
    BAR_EDGE_WIDTH = MINOR_LINE_WIDTH
    BAR_AXIS_LINE_WIDTH = MINOR_LINE_WIDTH
    BAR_COLOR_POSITIVE = COLOR_ACCENT
    BAR_COLOR_NEGATIVE = COLOR_PRIMARY

    # Error bars.
    ERROR_BAR_CAPSIZE = 3
    ERROR_BAR_LINEWIDTH = MINOR_LINE_WIDTH
    ERROR_BAR_COLOR = "black"

    # Line plots.
    LINE_WIDTH = MAIN_LINE_WIDTH
    LINE_MARKER_SIZE = 4
    LINE_MARKER_EDGE_WIDTH = MINOR_LINE_WIDTH

    # Grid.
    GRID_ALPHA = 0.3
    GRID_LINESTYLE = "--"
    GRID_LINEWIDTH = 0.8
    GRID_ENABLED = False

    # Output.
    OUTPUT_DPI = 300
    OUTPUT_FORMAT_PNG = "png"
    OUTPUT_FORMAT_SVG = "svg"
    SAVE_PAD_INCHES = 0.1


def setup_matplotlib():
    """Apply global matplotlib defaults for this style."""
    plt.rcParams["font.sans-serif"] = PlotConfig.FONT_FAMILY
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["svg.fonttype"] = "none"
    plt.rcParams["mathtext.fontset"] = "custom"
    plt.rcParams["mathtext.rm"] = "Arial"
    plt.rcParams["mathtext.it"] = "Arial:italic"
    plt.rcParams["mathtext.bf"] = "Arial:bold"


def apply_axis_style(ax):
    """Apply axis, tick, spine, and grid defaults to an Axes object."""
    ax.tick_params(
        axis="both",
        which="major",
        length=PlotConfig.TICK_LENGTH_MAJOR,
        width=PlotConfig.TICK_WIDTH,
        labelsize=PlotConfig.TICK_FONTSIZE,
    )
    ax.tick_params(
        axis="both",
        which="minor",
        length=PlotConfig.TICK_LENGTH_MINOR,
        width=PlotConfig.TICK_WIDTH,
    )

    for spine in ax.spines.values():
        spine.set_linewidth(PlotConfig.AXIS_LINE_WIDTH)

    if PlotConfig.GRID_ENABLED:
        ax.grid(
            True,
            alpha=PlotConfig.GRID_ALPHA,
            linestyle=PlotConfig.GRID_LINESTYLE,
            linewidth=PlotConfig.GRID_LINEWIDTH,
        )
    else:
        ax.grid(False)


def set_xlabel(ax, label):
    """Set an x-axis label using the configured style."""
    ax.set_xlabel(
        label,
        fontsize=PlotConfig.LABEL_FONTSIZE,
        fontweight=PlotConfig.LABEL_FONTWEIGHT,
        labelpad=PlotConfig.XLABEL_PAD * PlotConfig.LABEL_FONTSIZE,
    )


def set_ylabel(ax, label):
    """Set a y-axis label using the configured style."""
    ax.set_ylabel(
        label,
        fontsize=PlotConfig.LABEL_FONTSIZE,
        fontweight=PlotConfig.LABEL_FONTWEIGHT,
        labelpad=PlotConfig.YLABEL_PAD * PlotConfig.LABEL_FONTSIZE,
    )


def save_figure(fig, filename_base, formats=("png", "svg")):
    """Save a figure to one or more formats and return the written paths."""
    base = Path(filename_base)
    if base.parent != Path("."):
        base.parent.mkdir(parents=True, exist_ok=True)

    saved_files = []
    for fmt in formats:
        filepath = base.with_suffix(f".{fmt}")
        if fmt == "png":
            fig.savefig(
                filepath,
                dpi=PlotConfig.OUTPUT_DPI,
                bbox_inches="tight",
                pad_inches=PlotConfig.SAVE_PAD_INCHES,
            )
        else:
            fig.savefig(
                filepath,
                format=fmt,
                bbox_inches="tight",
                pad_inches=PlotConfig.SAVE_PAD_INCHES,
            )
        saved_files.append(str(filepath))
    return saved_files
