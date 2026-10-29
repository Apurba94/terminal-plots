# terminal-plots

**Look at your data without leaving the terminal: histograms, bar charts, sparklines, box plots
and scatter plots from CSV columns or piped numbers, over SSH, on clusters, anywhere.**

Part of the *Research Automation Toolkit*: 100 open tools for daily research work.

## Why

On HPC clusters, remote servers and instrument PCs there is often no GUI and no plotting library,
yet a quick look at a distribution catches unit errors, outliers and failed runs before they waste
compute time. A text plot in the log of a pipeline step is also a lightweight, version-controllable
record of what the data looked like.

## Features

- `hist`: fixed or Sturges bins, sub-character resolution with Unicode blocks, summary line
- `bar`: frequencies of categories with percentages, `--top N`
- `spark`: one-line trend (e.g. loss per epoch, daily counts)
- `box`: grouped box plots with 1.5 IQR whiskers and outliers
- `scatter`: density-shaded character scatter plot
- `--ascii` for terminals without Unicode; functions return strings for use in reports

## Usage

```bash
pip install .
terminal-plots hist results.csv -c reaction_time -b 15
terminal-plots bar survey.csv -c country --top 10
terminal-plots box trial.csv -c score -g arm
terminal-plots scatter data.csv -x dose -c response
python train.py | grep loss | cut -d= -f2 | terminal-plots spark -
```

## Testing

```bash
python -m unittest discover -s tests -t .
```

## License

MIT (c) JANIN A APURBA
