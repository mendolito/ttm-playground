# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

"""Plotly chart helpers for the Streamlit UI."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from transformer_thermal_model.aging import aging_rate_profile
from transformer_thermal_model.schemas import (
    InputProfile,
    OutputProfile,
    ThreeWindingInputProfile,
)
from transformer_thermal_model.transformer import PaperInsulationType

_HOT_SPOT_COLORS = {
    "low_voltage_side": "#d62728",
    "middle_voltage_side": "#ff7f0e",
    "high_voltage_side": "#9467bd",
}


def plot_temperatures(
    output: OutputProfile,
    profile: InputProfile | ThreeWindingInputProfile,
    fan_on: np.ndarray | None = None,
) -> go.Figure:
    """Two-row temperature plot: top-oil + ambient on top, hot-spot below.

    For three-winding outputs (``hot_spot_temp_profile`` is a DataFrame), the
    bottom row shows one trace per winding. When ``fan_on`` is supplied, an
    ONAN/ONAF step overlay is drawn on a secondary y-axis of the top row.
    """
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.55, 0.45],
        subplot_titles=("Top-oil & ambient temperature", "Hot-spot temperature"),
        specs=[[{"secondary_y": True}], [{}]],
    )

    x = pd.DatetimeIndex(profile.datetime_index)

    fig.add_trace(
        go.Scatter(
            x=x,
            y=output.top_oil_temp_profile.to_numpy(),
            mode="lines",
            name="Top-oil",
            line={"color": "#2ca02c", "width": 2},
        ),
        row=1,
        col=1,
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=np.asarray(profile.ambient_temperature_profile, dtype=float),
            mode="lines",
            name="Ambient",
            line={"color": "#7f7f7f", "width": 1, "dash": "dot"},
        ),
        row=1,
        col=1,
    )

    if fan_on is not None:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=np.asarray(fan_on, dtype=float),
                mode="lines",
                name="Fan on (ONAF)",
                line={"color": "#1f77b4", "width": 1, "shape": "hv"},
                opacity=0.6,
            ),
            row=1,
            col=1,
            secondary_y=True,
        )
        fig.update_yaxes(
            title_text="Fan state",
            tickvals=[0, 1],
            ticktext=["off", "on"],
            range=[-0.1, 1.1],
            row=1,
            col=1,
            secondary_y=True,
        )

    hot_spot = output.hot_spot_temp_profile
    if isinstance(hot_spot, pd.DataFrame):
        for column in hot_spot.columns:
            label = column.replace("_", " ").title()
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=hot_spot[column].to_numpy(),
                    mode="lines",
                    name=f"Hot-spot · {label}",
                    line={"color": _HOT_SPOT_COLORS.get(column, "#d62728"), "width": 2},
                ),
                row=2,
                col=1,
            )
    else:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=hot_spot.to_numpy(),
                mode="lines",
                name="Hot-spot",
                line={"color": "#d62728", "width": 2},
            ),
            row=2,
            col=1,
        )

    fig.update_yaxes(title_text="Temperature [°C]", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="Temperature [°C]", row=2, col=1)
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_layout(
        height=600,
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.15},
        margin={"t": 40, "l": 10, "r": 10, "b": 10},
    )
    return fig


def plot_aging(
    hot_spot: pd.Series,
    insulation_type: PaperInsulationType,
) -> go.Figure:
    """Plot the insulation aging rate over time for a given hot-spot series."""
    rate = aging_rate_profile(hot_spot, insulation_type)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=pd.DatetimeIndex(rate.index),
            y=rate.to_numpy(),
            mode="lines",
            name="Aging rate",
            line={"color": "#8c564b", "width": 2},
        )
    )
    fig.add_hline(y=1.0, line={"color": "#7f7f7f", "dash": "dot"}, annotation_text="Nominal (1 day/day)")
    fig.update_layout(
        height=320,
        xaxis_title="Time",
        yaxis_title="Aging rate [day / day]",
        hovermode="x unified",
        margin={"t": 20, "l": 10, "r": 10, "b": 10},
    )
    return fig


def plot_load_profile(profile: InputProfile | ThreeWindingInputProfile) -> go.Figure:
    """Preview an input profile: load (per winding for three-winding) + ambient."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    x = pd.DatetimeIndex(profile.datetime_index)

    if isinstance(profile, ThreeWindingInputProfile):
        for label, series, color in [
            ("LV load", profile.load_profile_low_voltage_side, _HOT_SPOT_COLORS["low_voltage_side"]),
            ("MV load", profile.load_profile_middle_voltage_side, _HOT_SPOT_COLORS["middle_voltage_side"]),
            ("HV load", profile.load_profile_high_voltage_side, _HOT_SPOT_COLORS["high_voltage_side"]),
        ]:
            fig.add_trace(
                go.Scatter(
                    x=x,
                    y=np.asarray(series, dtype=float),
                    mode="lines",
                    name=label,
                    line={"color": color, "width": 1.5},
                ),
                secondary_y=False,
            )
    else:
        fig.add_trace(
            go.Scatter(
                x=x,
                y=profile.load_profile.astype(float),
                mode="lines",
                name="Load",
                line={"color": "#1f77b4", "width": 2},
            ),
            secondary_y=False,
        )

    fig.add_trace(
        go.Scatter(
            x=x,
            y=np.asarray(profile.ambient_temperature_profile, dtype=float),
            mode="lines",
            name="Ambient",
            line={"color": "#7f7f7f", "width": 1, "dash": "dot"},
        ),
        secondary_y=True,
    )

    fig.update_yaxes(title_text="Load [A]", secondary_y=False)
    fig.update_yaxes(title_text="Ambient [°C]", secondary_y=True)
    fig.update_layout(
        height=260,
        hovermode="x unified",
        legend={"orientation": "h", "y": -0.25},
        margin={"t": 10, "l": 10, "r": 10, "b": 10},
    )
    return fig
