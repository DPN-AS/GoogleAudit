"""Visualization components for audit data presentation.

This module provides a very small chart factory used by the reporting
system.  According to :mod:`REFERENCE_GUIDE.md`, Matplotlib is the
primary dependency for rendering charts.  The :class:`ChartFactory`
below exposes helpers for creating pie and bar charts from a mapping of
labels to numeric values.  The returned :class:`~matplotlib.figure.Figure`
instances can then be embedded in reports or saved to disk by the caller.
"""

from __future__ import annotations

from typing import Mapping

from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class ChartFactory:
    """Factory for creating charts used in reports."""

    def create_pie_chart(self, data: Mapping[str, float]) -> Figure:
        """Return a pie chart representing ``data``.

        Parameters
        ----------
        data:
            Mapping of labels to numeric values.

        Returns
        -------
        :class:`~matplotlib.figure.Figure`
            A Matplotlib figure containing the rendered pie chart.
        """

        figure = plt.figure(figsize=(6, 4))
        ax = figure.add_subplot(111)

        labels = list(data.keys())
        sizes = list(data.values())

        ax.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")

        return figure

    def create_bar_chart(self, data: Mapping[str, float]) -> Figure:
        """Return a bar chart representing ``data``.

        Parameters
        ----------
        data:
            Mapping of labels to numeric values.

        Returns
        -------
        :class:`~matplotlib.figure.Figure`
            A Matplotlib figure containing the rendered bar chart.
        """

        figure = plt.figure(figsize=(6, 4))
        ax = figure.add_subplot(111)

        labels = list(data.keys())
        heights = list(data.values())

        ax.bar(labels, heights, color="skyblue")
        ax.set_ylabel("Count")
        ax.set_title("Findings Distribution")

        figure.tight_layout()

        return figure
