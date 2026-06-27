---
name: blue-green-plot
description: Standardize blue-green scientific plots using the bundled plot_config.py rules, with optional external plot_config.py overrides. Use when creating, editing, regenerating, or reviewing Python/matplotlib figures, especially when the user asks for figures to follow config style, bar charts with statistical p-values, live aspect-ratio changes, custom palettes, png/svg outputs, or consistent scientific plot formatting.
---

# Blue-Green Plot

## Core Rule

Use the bundled `scripts/plot_config.py` as the default source of truth for plot styling. If the target codebase already has its own compatible `plot_config.py` and the user asks to preserve it, pass that path through the helper's `config_root` override.

For every new or edited matplotlib plot:

```python
from plot_config import PlotConfig, setup_matplotlib, apply_axis_style, set_xlabel, set_ylabel, save_figure

setup_matplotlib()
```

Make the skill's `scripts/` directory importable before using `plot_config` or `blue_green_plot`, or copy `scripts/plot_config.py` next to the plotting script when a standalone script is easier for the target repo.

Use `save_figure(fig, str(path_without_suffix))` instead of raw `fig.savefig(...)` unless a script has a specific reason to save one format only.

## Default Format

- Save both `png` and `svg` by default.
- Use `PlotConfig.OUTPUT_DPI` for PNG.
- Use `PlotConfig.FIG_WIDTH`, `PlotConfig.FIG_HEIGHT`, or scaled multiples for subplot grids.
- Use `PlotConfig.COLOR_LIST` or named `PlotConfig` colors instead of hard-coded ad hoc palettes.
- Apply `apply_axis_style(ax)` to every axis.
- Use `set_xlabel(ax, ...)` and `set_ylabel(ax, ...)` for axis labels.
- Use `PlotConfig.TITLE_FONTSIZE`, `LABEL_FONTSIZE`, `TICK_FONTSIZE`, and `LEGEND_FONTSIZE`.
- Do not add figure titles, subplot titles, or suptitles by default. Put case identity and context in filenames, manifests, or chat captions unless the user explicitly asks for titles.
- Avoid enabling grids unless the user explicitly asks or the existing figure type already uses them.
- Ordinary scatter points must have no border: use `edgecolors="none"` and `linewidths=0`.
- Only point-line plot markers keep a border; the marker edge must be a darker version of the marker fill color, never a black default edge.
- For two-condition comparisons, use fixed semantic colors before the broader palette: first condition = `PlotConfig.PAIR_COLOR_A`, second condition = `PlotConfig.PAIR_COLOR_B`.

## Bar Charts And P Values

Every bar chart must include statistical p-value annotations for the relevant group or condition comparisons.

- Prefer exact labels such as `p = 0.032`; use thresholds such as `p < 0.001` only for very small values.
- Put p-value labels above the compared bars with brackets or another unambiguous comparison marker.
- State the statistical test used in the script output, manifest, caption, or chat summary; do not add a figure title just to name the test.
- Choose the test from the experimental design: paired vs. unpaired, two-group vs. multi-group, repeated-measures vs. independent observations. Apply multiple-comparison correction when showing multiple pairwise tests.
- Do not fabricate p values from mean-only or summary-only data. If raw replicate data or precomputed p values are missing, ask for them before finalizing the bar chart.

## Runtime Overrides

When the user asks to change the image ratio, dimensions, palette, or output format, keep the config defaults but expose a small local override layer. Prefer the bundled helper:

```python
from blue_green_plot import PlotOverrides, styled_subplots, get_palette, paired_color_map, plain_scatter_kwargs, add_p_value_bracket, save_styled_figure

overrides = PlotOverrides(
    aspect=1.6,                    # width / height
    scale=1.1,
    colors=["#367DB0", "#9DC7DD", "#9ED17B"],
    formats=("png", "svg"),
)
fig, axes = styled_subplots(1, 2, overrides=overrides)
palette = get_palette(overrides.colors)
pair_colors = paired_color_map(("Control", "Treatment"))
axes[0].scatter(x, y, color=palette[0], **plain_scatter_kwargs())
bars = axes[1].bar([0, 1], [control_mean, treatment_mean], color=list(pair_colors.values()))
add_p_value_bracket(axes[1], 0, 1, y=max(bar.get_height() for bar in bars), p_value=0.032)
save_styled_figure(fig, output_base, overrides=overrides)
```

For paired traces, override the general palette with semantic pair colors:

```python
pair_colors = paired_color_map(("Control", "Treatment"))
ax.plot(time, control_value, color=pair_colors["Control"], label="Control")
ax.plot(time, treatment_value, color=pair_colors["Treatment"], label="Treatment")
ax.fill_between(time, control_low, control_high, color=pair_colors["Control"], alpha=0.18, linewidth=0)
ax.fill_between(time, treatment_low, treatment_high, color=pair_colors["Treatment"], alpha=0.18, linewidth=0)
```

For command-line plot scripts, add live controls:

```python
from blue_green_plot import add_style_args, overrides_from_args

parser = argparse.ArgumentParser()
add_style_args(parser)
args = parser.parse_args()
overrides = overrides_from_args(args)
```

Then the script can be regenerated with:

```bash
python my_plot.py --plot-aspect 1.6 --plot-colors "#367DB0,#F7941D,#ED1C24"
```

Override priority:

1. User-provided `width` and `height`
2. User-provided `aspect` with config height
3. Subplot grid scaled from `PlotConfig.FIG_WIDTH` and `PlotConfig.FIG_HEIGHT`

Read `references/runtime_overrides.md` when implementing a more complex override UI or CLI.

## Patch Checklist

When updating an existing plot script:

1. Import `plot_config` and call `setup_matplotlib()` once near imports.
2. Replace hard-coded color dicts with `PlotConfig.COLOR_LIST` or runtime palette variables.
3. Replace `fig.savefig(..., dpi=...)` with `save_figure(...)`.
4. Remove hard-coded grid/spine/tick styling when `apply_axis_style()` covers it.
5. Remove ordinary scatter marker borders. For point-line markers, use a darker edge derived from the fill color.
6. If the plot compares two named conditions, map them with `paired_color_map(...)` so the semantic colors stay stable.
7. For every bar chart, compute or load the relevant statistical p values and annotate them on the bars.
8. Keep figure dimensions as config multiples, or route user-controlled dimensions through `PlotOverrides`.
9. Run `python -m py_compile <script>` and regenerate the requested images.
10. Confirm both `.png` and `.svg` exist unless the user requested a different format set.

## Output Naming

For `save_figure`, pass a path without suffix:

```python
save_figure(fig, str(FIG_DIR / "my_plot"))
```

This creates:

```text
my_plot.png
my_plot.svg
```

## Related Public Skill Repositories

These repositories can complement this skill when a figure needs a different visual grammar. Check each repository's license before reusing or redistributing its contents.

- [nature-skills](https://github.com/Yuan1z0825/nature-skills): Nature-style academic expression and scientific plotting guidance.
- [AgentFigureGallery](https://github.com/Dsadd4/AgentFigureGallery): reference-driven scientific plotting skill for coding agents.
- [engineering-figure-agent](https://github.com/heyu-233/engineering-figure-agent): publication-style engineering and computer-science figures, including architecture diagrams, flowcharts, curves, and multi-panel figures.
- [Codex-drawio-skill](https://github.com/SHALINS428/Codex-drawio-skill): editable academic diagrams in draw.io / diagrams.net with PNG export.
- [drawio-skill](https://github.com/Agents365-ai/drawio-skill): natural-language draw.io diagrams, flowcharts, architecture diagrams, and multi-format exports.
- [Awesome-Scientific-Skills](https://github.com/InternScience/Awesome-Scientific-Skills): curated index for discovering more scientific research skills.
- [medical-research-skills](https://github.com/aipoch/medical-research-skills): biomedical research skill collection with data analysis, evidence synthesis, and academic-writing workflows.

## Notes

- Do not modify `plot_config.py` unless the user explicitly wants global style changes.
- For one-off plots, use overrides in the plotting script rather than changing global config.
- Prefer absolute output paths when showing generated images back to the user.
