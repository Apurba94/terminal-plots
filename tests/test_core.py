import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from terminal_plots.cli import main
from terminal_plots.core import bar_chart, boxplot, histogram, scatter, sparkline


class PlotTests(unittest.TestCase):
    def test_histogram_counts(self):
        out = histogram([1, 1, 2, 3, 4, 4, 4, 5], bins=4, width=10, ascii_only=True)
        lines = out.splitlines()
        self.assertEqual(len(lines), 5)
        self.assertTrue(lines[0].endswith(" 2"))
        self.assertTrue(lines[3].rstrip().endswith("4"))
        self.assertIn("##########", lines[3])      # max bin uses the full width
        self.assertIn("n=8", lines[-1])

    def test_histogram_edge_cases(self):
        self.assertEqual(histogram([]), "(no data)")
        self.assertIn("n=3", histogram([2, 2, 2], bins=2))

    def test_bar_chart_counts_labels(self):
        out = bar_chart(["a", "b", "a", "c", "a", "b"], width=6, ascii_only=True)
        first = out.splitlines()[0]
        self.assertTrue(first.startswith("a ######"))
        self.assertIn("(50.0%)", first)
        self.assertEqual(len(bar_chart({"x": 1, "y": 2, "z": 3}, top=2).splitlines()), 2)

    def test_sparkline(self):
        self.assertEqual(sparkline([0, 7]), "▁█")
        self.assertEqual(len(sparkline(list(range(20)))), 20)
        self.assertEqual(sparkline([3, 3, 3], ascii_only=True), "---")

    def test_unicode_partial_blocks(self):
        self.assertIn("▌", histogram([0, 0, 1], bins=2, width=1))

    def test_boxplot_marks_outlier(self):
        out = boxplot({"A": [1, 2, 3, 4, 5, 6, 100], "B": [10, 11, 12]})
        self.assertIn("o", out.splitlines()[0])
        self.assertIn("median=4", out)

    def test_scatter_shape(self):
        out = scatter([0, 1, 2], [0, 1, 2], width=30, height=5)
        self.assertEqual(len(out.splitlines()), 7)

    def test_cli(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "d.csv")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write("g,v\na,1\na,2\nb,5\nb,6\n")
            with redirect_stdout(io.StringIO()) as buf:
                main(["box", p, "-c", "v", "-g", "g"])
                main(["bar", p, "-c", "g", "--ascii"])
            self.assertIn("median=", buf.getvalue())
            self.assertIn("(50.0%)", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
