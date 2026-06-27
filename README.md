# Blue-Green Plot

A compact Codex skill for making clean blue-green scientific matplotlib figures.

## Install The Skill

Clone this repository into your Codex skills directory:

```bash
git clone https://github.com/SII-YujunChen/blue-green-plot.git ~/.codex/skills/blue-green-plot
```

Then ask Codex:

```text
Use $blue-green-plot to make this matplotlib figure follow a clean scientific style.
```

## Use In A Python Script

Add the skill's `scripts/` directory to your Python path, then import the style helpers:

```python
import sys
sys.path.insert(0, "path/to/blue-green-plot/scripts")

from plot_config import setup_matplotlib, save_figure

setup_matplotlib()
# build your matplotlib figure...
save_figure(fig, "figures/my_plot")
```

For more flexible plots, use:

```python
from blue_green_plot import PlotOverrides, styled_subplots, get_palette

overrides = PlotOverrides(palette="nature", scale=1.2)
fig, axes = styled_subplots(1, 2, overrides=overrides)
palette = get_palette(palette=overrides.palette)
```

## Change The Config

Edit:

```text
scripts/plot_config.py
```

Common settings to adjust:

- `DEFAULT_PALETTE` and `PALETTES`: choose or add color palettes.
- `FIG_WIDTH`, `FIG_HEIGHT`, `AXES_ASPECT`: control figure and panel proportions.
- `TITLE_FONTSIZE`, `LABEL_FONTSIZE`, `TICK_FONTSIZE`, `LEGEND_FONTSIZE`: control text size.
- `BAR_WIDTH`, `BAR_WIDTH_SINGLE`, `BAR_PAIR_CENTER_DISTANCE`, `BAR_X_MARGIN`: control bar-chart geometry.
- `OUTPUT_DPI` and `SAVE_PAD_INCHES`: control export quality and padding.

Built-in palettes include `blue-green`, `nature`, `npg`, `jama`, `lancet`, `nejm`, `okabe-ito`, `tableau`, and `gray`.

## Output

Use `save_figure(...)` or `save_styled_figure(...)` to save both PNG and SVG by default.
