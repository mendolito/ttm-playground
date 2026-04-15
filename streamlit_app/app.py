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
        page_title="Termisk transformatormodell",
        page_icon=":zap:",
        layout="wide",
    )

    st.title("Termisk transformatormodell")
    st.caption(
        "Interaktiv lekeplass for biblioteket "
        "[`transformer-thermal-model`](https://github.com/alliander-opensource/transformer-thermal-model) "
        "— IEC 60076-7 termisk simulering for kraft-, distribusjons- og tre-vikling-transformatorer."
    )

    with st.sidebar:
        st.header("Om")
        st.markdown(
            "Denne appen samler de fire hovedarbeidsflytene i biblioteket:\n\n"
            "- **Grunnleggende simulering** — topp-olje- og hot-spot-kurver for en kraft- eller "
            "distribusjonstransformator.\n"
            "- **Tre-vikling** — hot-spot-utdata per vikling for tre-vikling-transformatorer.\n"
            "- **Kjølebryter** — dynamisk ONAN/ONAF-omkobling styrt av temperatur eller en vifteplan.\n"
            "- **Kalibrering & aldring** — kalibrer hot-spot-faktoren mot en målgrense og "
            "estimer isolasjonsaldring.\n\n"
            "Last- og omgivelsesprofiler er innebygde forhåndsvalg; hvert forhåndsvalg tilpasser seg "
            "transformatoren du velger."
        )
        st.markdown("---")
        st.caption("Bygget med Streamlit + Plotly. Kildekode: `streamlit_app/`.")

    tab_labels = [
        "Grunnleggende simulering",
        "Tre-vikling",
        "Kjølebryter",
        "Kalibrering & aldring",
    ]
    tabs = st.tabs(tab_labels)
    renderers = (basic.render, three_winding.render, cooling_switch.render, calibration_aging.render)
    for tab, render in zip(tabs, renderers, strict=True):
        with tab:
            render()


main()
