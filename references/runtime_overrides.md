# Runtime Plot Overrides

Use this reference when a blue-green plotting task needs live control over aspect ratio, size, palette, or output formats while preserving `plot_config.py` defaults.

## Suggested User-Facing Controls

- `aspect`: width / height, e.g. `1.0`, `1.6`, `2.2`
- `width`: figure width in inches
- `height`: figure height in inches
- `scale`: multiplier applied after size calculation
- `colors`: comma-separated hex colors or a Python list
- `formats`: tuple/list such as `("png", "svg")` or `("png",)`
- `dpi`: PNG DPI override; default comes from `PlotConfig.OUTPUT_DPI`
- `grid`: optional bool override if a diagnostic plot needs grid lines

## Size Resolution

Use this order:

1. If both `width` and `height` are set, use them.
2. Else if `aspect` is set, use `height = PlotConfig.FIG_HEIGHT * nrows` and `width = height * aspect * ncols / max(nrows, 1)`.
3. Else use `PlotConfig.FIG_WIDTH * ncols`, `PlotConfig.FIG_HEIGHT * nrows`.
4. Apply `scale` last.

## Palette Resolution

Use this order:

1. User-supplied colors.
2. Existing script palette if it already encodes domain meaning.
3. `PlotConfig.COLOR_LIST`.

For ordered groups, map labels in the same order they appear in the data or in the user-provided legend.

## Paired Condition Colors

If a plot compares two main conditions, use these semantic colors before any general palette or command-line color override:

- First condition: `PlotConfig.PAIR_COLOR_A`
- Second condition: `PlotConfig.PAIR_COLOR_B`

Use the helper to avoid hand-written mappings:

```python
from blue_green_plot import paired_color_map, condition_color

colors = paired_color_map(("Control", "Treatment"))
ax.plot(t, control, color=colors["Control"], label="Control")
ax.plot(t, treatment, color=colors["Treatment"], label="Treatment")
```

For confidence bands or repeated raw traces, use the same color with lower alpha:

```python
ax.fill_between(t, control_low, control_high, color=colors["Control"], alpha=0.18, linewidth=0)
ax.fill_between(t, treatment_low, treatment_high, color=colors["Treatment"], alpha=0.18, linewidth=0)
```

## Marker Edge Rule

Ordinary scatter points:

```python
ax.scatter(x, y, color=color, edgecolors="none", linewidths=0)
```

Point-line plots:

```python
from blue_green_plot import line_marker_kwargs

ax.plot(x, y, color=color, marker="o", **line_marker_kwargs(color))
```

The point-line marker edge is a darker version of the fill color. Do not use black marker edges unless the fill is already black.

## Save Rule

Always save through `save_styled_figure()` or `save_figure()` so PNG/SVG format and DPI remain consistent.

## CLI Integration

For scripts that should support live plot changes, use:

```python
from blue_green_plot import add_style_args, overrides_from_args

add_style_args(parser)
args = parser.parse_args()
overrides = overrides_from_args(args)
```

Supported flags:

```bash
--plot-aspect 1.6
--plot-width 3.2 --plot-height 2.0
--plot-scale 1.15
--plot-colors "#367DB0,#F7941D,#ED1C24"
--plot-formats "png,svg"
--plot-dpi 450
--plot-grid
--no-plot-grid
```
