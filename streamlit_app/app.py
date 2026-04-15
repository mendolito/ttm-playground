# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

"""Streamlit entrypoint for the transformer thermal model playground.

Run with::

    poetry run streamlit run streamlit_app/app.py
"""

from __future__ import annotations

# Streamlit adds the script's directory to sys.path (i.e. ``streamlit_app/``),
# which makes absolute imports like ``from streamlit_app.foo import bar`` fail.
# Prepend the repo root so those imports resolve whether the app is launched
# via ``streamlit run streamlit_app/app.py`` or as a package.
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import streamlit as st  # noqa: E402 — after sys.path bootstrap

from streamlit_app.tabs import (  # noqa: E402
    basic,
    calibration_aging,
    cooling_switch,
    three_winding,
)


def main() -> None:
    """Configure the page and dispatch to the tab renderers."""
    st.set_page_config(
        page_title="Transformer thermal model",
        page_icon=":zap:",
        layout="wide",
    )

    st.title("Transformer thermal model")
    st.caption(
        "Interactive playground for the "
        "[`transformer-thermal-model`](https://github.com/alliander-opensource/transformer-thermal-model) "
        "library — IEC 60076-7 thermal simulation for power, distribution, and three-winding transformers."
    )

    with st.sidebar:
        st.header("About")
        st.markdown(
            "This app wraps the four headline workflows of the library:\n\n"
            "- **Basic simulation** — top-oil and hot-spot curves for a power or distribution transformer.\n"
            "- **Three-winding** — per-winding hot-spot output for three-winding transformers.\n"
            "- **Cooling switch** — dynamic ONAN/ONAF switching driven by temperature or a fan schedule.\n"
            "- **Calibration & aging** — calibrate the hot-spot factor to a target limit and "
            "estimate insulation aging.\n\n"
            "Load and ambient profiles are built-in presets; each preset adapts to the transformer you pick."
        )
        st.markdown("---")
        st.caption("Built with Streamlit + Plotly. Source: `streamlit_app/`.")

    tab_labels = [
        "Basic simulation",
        "Three-winding",
        "Cooling switch",
        "Calibration & aging",
    ]
    tabs = st.tabs(tab_labels)
    renderers = (basic.render, three_winding.render, cooling_switch.render, calibration_aging.render)
    for tab, render in zip(tabs, renderers, strict=True):
        with tab:
            render()


main()
