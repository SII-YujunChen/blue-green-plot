#!/usr/bin/env python3
"""Runtime helper for blue-green plot_config-based matplotlib styling."""

from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
import importlib.util
import sys
from typing import Sequence

import matplotlib.pyplot as plt
from matplotlib import colors as mcolors


BUNDLED_CONFIG_PATH = Path(__file__).with_name("plot_config.py")
PAIR_A_FALLBACK_COLOR = "#367DB0"
PAIR_B_FALLBACK_COLOR = "#9ED17B"


def _resolve_plot_config_path(config_root: str | Path | None = None) -> Path:
    if config_root is None:
        return BUNDLED_CONFIG_PATH.resolve()

    root = Path(config_root).expanduser()
    config_path = root if root.name == "plot_config.py" else root / "plot_config.py"
    return config_path.resolve()


def _load_plot_config(config_root: str | Path | None = None):
    config_path = _resolve_plot_config_path(config_root)
    if not config_path.exists():
        raise FileNotFoundError(f"Cannot find plot_config.py at {config_path}")
    module_name = f"blue_green_plot_config_{abs(hash(config_path))}"
    spec = importlib.util.spec_from_file_location(module_name, config_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import plot_config.py from {config_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_CONFIG_CACHE = {}


def config(config_root: str | Path | None = None):
    config_path = _resolve_plot_config_path(config_root)
    if config_path not in _CONFIG_CACHE:
        _CONFIG_CACHE[config_path] = _load_plot_config(config_path)
    return _CONFIG_CACHE[config_path]


@dataclass
class PlotOverrides:
    """Optional runtime overrides layered on top of plot_config.py."""

    aspect: float | None = None
    width: float | None = None
    height: float | None = None
    scale: float = 1.0
    colors: Sequence[str] | str | None = None
    formats: Sequence[str] = ("png", "svg")
    dpi: int | None = None
    grid: bool | None = None
    config_root: str | Path | None = None


def setup_style_matplotlib(overrides: PlotOverrides | None = None):
    cfg = config(overrides.config_root if overrides else None)
    cfg.setup_matplotlib()
    return cfg


def resolve_figsize(
    nrows: int = 1,
    ncols: int = 1,
    overrides: PlotOverrides | None = None,
) -> tuple[float, float]:
    overrides = overrides or PlotOverrides()
    cfg = config(overrides.config_root)
    scale = overrides.scale or 1.0
    if overrides.width is not None and overrides.height is not None:
        width = float(overrides.width)
        height = float(overrides.height)
    elif overrides.aspect is not None:
        height = float(cfg.PlotConfig.FIG_HEIGHT) * max(1, nrows)
        width = height * float(overrides.aspect) * max(1, ncols) / max(1, nrows)
    else:
        width = float(cfg.PlotConfig.FIG_WIDTH) * max(1, ncols)
        height = float(cfg.PlotConfig.FIG_HEIGHT) * max(1, nrows)
    return width * scale, height * scale


def _parse_color_string(colors: str) -> list[str]:
    return [part.strip() for part in colors.split(",") if part.strip()]


def get_palette(
    colors: Sequence[str] | str | None = None,
    count: int | None = None,
    config_root: str | Path | None = None,
) -> list[str]:
    cfg = config(config_root)
    if colors is None:
        palette = list(cfg.PlotConfig.COLOR_LIST)
    elif isinstance(colors, str):
        palette = _parse_color_string(colors)
    else:
        palette = list(colors)
    if not palette:
        palette = list(cfg.PlotConfig.COLOR_LIST)
    if count is None or count <= len(palette):
        return palette if count is None else palette[:count]
    repeats = (count + len(palette) - 1) // len(palette)
    return (palette * repeats)[:count]


def darken_color(color: str, factor: float = 0.65) -> str:
    """Return a darker hex color for line-plot marker edges."""
    rgb = mcolors.to_rgb(color)
    return mcolors.to_hex(tuple(max(0.0, min(1.0, channel * factor)) for channel in rgb))


def plain_scatter_kwargs(**kwargs) -> dict:
    """Style kwargs for ordinary scatter points: no marker border."""
    styled = {"edgecolors": "none", "linewidths": 0}
    styled.update(kwargs)
    return styled


def line_marker_kwargs(color: str, *, edge_factor: float = 0.65, **kwargs) -> dict:
    """Style kwargs for markers on point-line plots."""
    styled = {
        "markerfacecolor": color,
        "markeredgecolor": darken_color(color, edge_factor),
        "markeredgewidth": 0.5,
    }
    styled.update(kwargs)
    return styled


def format_p_value(p_value: float | str, *, precision: int = 3, min_display: float = 0.001) -> str:
    """Return a compact p-value label for bar-chart annotations."""
    if isinstance(p_value, str):
        value = p_value.strip()
        return value if value.lower().startswith("p") else f"p = {value}"

    value = float(p_value)
    if not math.isfinite(value):
        raise ValueError(f"p_value must be finite, got {p_value!r}")
    if value < 0 or value > 1:
        raise ValueError(f"p_value must be in [0, 1], got {p_value!r}")
    if value < min_display:
        return f"p < {min_display:g}"
    return f"p = {value:.{precision}g}"


def add_p_value_bracket(
    ax,
    x1: float,
    x2: float,
    y: float,
    p_value: float | str,
    *,
    bracket_height: float | None = None,
    text_offset: float | None = None,
    color: str = "black",
    linewidth: float = 0.8,
    fontsize: float | None = None,
    label: str | None = None,
):
    """Annotate a bar-chart comparison with a p-value bracket."""
    y_min, y_max = ax.get_ylim()
    y_span = y_max - y_min if y_max != y_min else 1.0
    height = bracket_height if bracket_height is not None else y_span * 0.035
    offset = text_offset if text_offset is not None else y_span * 0.015
    label = label or format_p_value(p_value)

    ax.plot([x1, x1, x2, x2], [y, y + height, y + height, y], color=color, linewidth=linewidth, clip_on=False)
    text = ax.text(
        (x1 + x2) / 2,
        y + height + offset,
        label,
        ha="center",
        va="bottom",
        color=color,
        fontsize=fontsize,
        clip_on=False,
    )

    needed_top = y + height + offset + y_span * 0.08
    if needed_top > y_max:
        ax.set_ylim(y_min, needed_top)
    return text


def paired_color_map(
    labels: Sequence[str] = ("A", "B"),
    config_root: str | Path | None = None,
) -> dict[str, str]:
    """Return stable colors for a two-condition comparison."""
    if len(labels) != 2:
        raise ValueError(f"labels must contain exactly two entries, got {labels!r}")
    plot_config = config(config_root).PlotConfig
    color_a = getattr(plot_config, "PAIR_COLOR_A", getattr(plot_config, "COLOR_PRIMARY", PAIR_A_FALLBACK_COLOR))
    color_b = getattr(plot_config, "PAIR_COLOR_B", getattr(plot_config, "COLOR_ACCENT", PAIR_B_FALLBACK_COLOR))
    return {str(labels[0]): color_a, str(labels[1]): color_b}


def condition_color(
    label: str,
    labels: Sequence[str] = ("A", "B"),
    config_root: str | Path | None = None,
) -> str:
    """Return the semantic color for one label in a two-condition comparison."""
    colors = paired_color_map(labels, config_root)
    key = str(label)
    if key not in colors:
        raise ValueError(f"Unknown condition label {label!r}; expected one of {tuple(colors)}")
    return colors[key]


def ordered_color_map(
    labels: Sequence[str | float],
    colors: Sequence[str] | str | None = None,
    config_root: str | Path | None = None,
) -> dict[str | float, str]:
    """Map any ordered labels to palette colors in input order."""
    palette = get_palette(colors, len(labels), config_root)
    return {label: palette[idx] for idx, label in enumerate(labels)}


def styled_subplots(
    nrows: int = 1,
    ncols: int = 1,
    *,
    overrides: PlotOverrides | None = None,
    squeeze: bool = True,
    **kwargs,
):
    overrides = overrides or PlotOverrides()
    cfg = setup_style_matplotlib(overrides)
    figsize = resolve_figsize(nrows, ncols, overrides)
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, squeeze=squeeze, **kwargs)
    axes_iter = axes.ravel() if hasattr(axes, "ravel") else [axes]
    for ax in axes_iter:
        cfg.apply_axis_style(ax)
        if overrides.grid is not None:
            ax.grid(bool(overrides.grid))
    return fig, axes


def apply_axis(ax, *, overrides: PlotOverrides | None = None):
    cfg = config(overrides.config_root if overrides else None)
    cfg.apply_axis_style(ax)
    if overrides and overrides.grid is not None:
        ax.grid(bool(overrides.grid))


def set_labels(ax, xlabel: str | None = None, ylabel: str | None = None, *, config_root: str | Path | None = None):
    cfg = config(config_root)
    if xlabel is not None:
        cfg.set_xlabel(ax, xlabel)
    if ylabel is not None:
        cfg.set_ylabel(ax, ylabel)


def save_styled_figure(
    fig,
    filename_base: str | Path,
    *,
    overrides: PlotOverrides | None = None,
) -> list[str]:
    overrides = overrides or PlotOverrides()
    cfg = config(overrides.config_root)
    formats = tuple(overrides.formats or ("png", "svg"))
    if overrides.dpi is None:
        return cfg.save_figure(fig, str(filename_base), formats=formats)

    saved: list[str] = []
    for fmt in formats:
        path = f"{filename_base}.{fmt}"
        if fmt == "png":
            fig.savefig(
                path,
                dpi=int(overrides.dpi),
                bbox_inches="tight",
                pad_inches=cfg.PlotConfig.SAVE_PAD_INCHES,
            )
        else:
            fig.savefig(
                path,
                format=fmt,
                bbox_inches="tight",
                pad_inches=cfg.PlotConfig.SAVE_PAD_INCHES,
            )
        saved.append(path)
    return saved


def add_style_args(parser, *, prefix: str = "plot"):
    """Add reusable CLI flags for live figure style overrides."""
    parser.add_argument(f"--{prefix}-aspect", type=float, default=None, help="Figure aspect ratio: width / height.")
    parser.add_argument(f"--{prefix}-width", type=float, default=None, help="Figure width in inches.")
    parser.add_argument(f"--{prefix}-height", type=float, default=None, help="Figure height in inches.")
    parser.add_argument(f"--{prefix}-scale", type=float, default=1.0, help="Scale applied after size resolution.")
    parser.add_argument(
        f"--{prefix}-colors",
        default=None,
        help="Comma-separated color list, e.g. '#367DB0,#F7941D,#ED1C24'.",
    )
    parser.add_argument(
        f"--{prefix}-formats",
        default=None,
        help="Comma-separated output formats. Defaults to png,svg.",
    )
    parser.add_argument(f"--{prefix}-dpi", type=int, default=None, help="PNG DPI override.")
    grid_group = parser.add_mutually_exclusive_group()
    grid_group.add_argument(f"--{prefix}-grid", action="store_true", default=None, help="Enable grid lines.")
    grid_group.add_argument(f"--no-{prefix}-grid", action="store_false", dest=f"{prefix}_grid", help="Disable grid lines.")
    return parser


def overrides_from_args(args, *, prefix: str = "plot", config_root: str | Path | None = None) -> PlotOverrides:
    """Create PlotOverrides from argparse args added by add_style_args()."""
    formats = getattr(args, f"{prefix}_formats", None)
    return PlotOverrides(
        aspect=getattr(args, f"{prefix}_aspect", None),
        width=getattr(args, f"{prefix}_width", None),
        height=getattr(args, f"{prefix}_height", None),
        scale=getattr(args, f"{prefix}_scale", 1.0),
        colors=getattr(args, f"{prefix}_colors", None),
        formats=tuple(_parse_color_string(formats)) if formats else ("png", "svg"),
        dpi=getattr(args, f"{prefix}_dpi", None),
        grid=getattr(args, f"{prefix}_grid", None),
        config_root=config_root,
    )
