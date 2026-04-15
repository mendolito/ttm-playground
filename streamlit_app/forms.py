# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

"""Streamlit form helpers.

Every helper accepts a ``key_prefix`` so the same form can be instantiated in
multiple tabs without session-state collisions between them.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import streamlit as st

from transformer_thermal_model.schemas import (
    InputProfile,
    ThreeWindingInputProfile,
    UserThreeWindingTransformerSpecifications,
    UserTransformerSpecifications,
    WindingSpecifications,
)
from transformer_thermal_model.schemas.thermal_model import (
    CoolingSwitchConfig,
    CoolingSwitchSettings,
    ONANParameters,
)
from transformer_thermal_model.schemas.thermal_model.initial_state import (
    ColdStart,
    InitialLoad,
    InitialState,
    InitialTopOilTemp,
)

from streamlit_app import plots
from streamlit_app.presets import (
    PROFILE_PRESETS,
    THREE_WINDING_PROFILE_PRESETS,
)


# ---------------------------------------------------------------------------
# Transformer specifications
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class _FieldSpec:
    """Render metadata for a single numeric spec field."""

    name: str
    label: str
    step: float
    required: bool = False
    format_str: str = "%g"
    min_value: float | None = 0.0


_LOSS_FIELDS = (
    _FieldSpec("load_loss", "Load loss [W]", step=1000.0, required=True),
    _FieldSpec("no_load_loss", "No-load loss [W]", step=500.0, required=True),
    _FieldSpec("nom_load_sec_side", "Nominal secondary current [A]", step=10.0, required=True),
)
_THERMAL_FIELDS = (
    _FieldSpec("time_const_oil", "Time constant oil [min]", step=5.0),
    _FieldSpec("time_const_windings", "Time constant windings [min]", step=1.0),
    _FieldSpec("top_oil_temp_rise", "Top-oil temperature rise [K]", step=1.0),
    _FieldSpec("winding_oil_gradient", "Winding-oil gradient [K]", step=1.0),
    _FieldSpec("hot_spot_fac", "Hot-spot factor [-]", step=0.05),
)
_MODEL_FIELDS = (
    _FieldSpec("oil_const_k11", "Oil constant k11 [-]", step=0.1),
    _FieldSpec("winding_const_k21", "Winding constant k21 [-]", step=1.0),
    _FieldSpec("winding_const_k22", "Winding constant k22 [-]", step=1.0),
    _FieldSpec("oil_exp_x", "Oil exponent x [-]", step=0.05),
    _FieldSpec("winding_exp_y", "Winding exponent y [-]", step=0.05),
)
_CORRECTION_FIELDS = (
    _FieldSpec("end_temp_reduction", "End-temperature reduction [K]", step=1.0, min_value=None),
    _FieldSpec("amb_temp_surcharge", "Ambient surcharge [K]", step=1.0, min_value=None),
)


def _collect_field_values(
    preset: object,
    fields: tuple[_FieldSpec, ...],
    key_prefix: str,
    group_label: str,
) -> dict[str, float | None]:
    """Render number inputs for a group of spec fields and collect their values.

    Optional fields may be left blank to defer to the library's IEC defaults;
    those come back as ``None`` and are dropped before constructing the spec.
    """
    st.markdown(f"**{group_label}**")
    cols = st.columns(min(len(fields), 3))
    values: dict[str, float | None] = {}
    for i, field in enumerate(fields):
        preset_value = getattr(preset, field.name, None)
        with cols[i % len(cols)]:
            value = st.number_input(
                label=field.label,
                value=float(preset_value) if preset_value is not None else None,
                step=field.step,
                format=field.format_str,
                min_value=field.min_value,
                key=f"{key_prefix}.{field.name}",
                help="La stå tom for å bruke standardverdi fra biblioteket." if not field.required else None,
            )
        if value is None and field.required:
            # Streamlit returns None if the user clears a number_input; for required
            # fields we fall back to the preset value so the simulation keeps working.
            value = float(preset_value) if preset_value is not None else 0.0
        values[field.name] = float(value) if value is not None else None
    return values


def render_spec_form(
    preset: UserTransformerSpecifications,
    key_prefix: str,
) -> UserTransformerSpecifications:
    """Render an override form for two-winding transformer specs.

    The preset pre-fills the fields; any optional field the user clears is
    omitted so the library's IEC defaults take over.
    """
    with st.expander("Overstyr spesifikasjoner", expanded=False):
        losses = _collect_field_values(preset, _LOSS_FIELDS, key_prefix, "Tap")
        thermals = _collect_field_values(preset, _THERMAL_FIELDS, key_prefix, "Termiske konstanter")
        models = _collect_field_values(preset, _MODEL_FIELDS, key_prefix, "Modellkonstanter")
        corrections = _collect_field_values(preset, _CORRECTION_FIELDS, key_prefix, "Korreksjoner")

    kwargs = {
        **{k: v for k, v in losses.items() if v is not None},
        **{k: v for k, v in thermals.items() if v is not None},
        **{k: int(v) for k, v in models.items() if v is not None and k in {"winding_const_k21", "winding_const_k22"}},
        **{
            k: v
            for k, v in models.items()
            if v is not None and k not in {"winding_const_k21", "winding_const_k22"}
        },
        **{k: v for k, v in corrections.items() if v is not None},
    }
    return UserTransformerSpecifications(**kwargs)


def _render_winding_form(
    preset: WindingSpecifications,
    key_prefix: str,
    label: str,
) -> WindingSpecifications:
    st.markdown(f"**{label}**")
    cols = st.columns(3)
    with cols[0]:
        nom_load = st.number_input(
            "Nominal load [A]",
            value=float(preset.nom_load),
            step=10.0,
            min_value=0.0,
            key=f"{key_prefix}.nom_load",
        )
    with cols[1]:
        nom_power = st.number_input(
            "Nominal power [MVA]",
            value=float(preset.nom_power),
            step=1.0,
            min_value=0.0,
            key=f"{key_prefix}.nom_power",
        )
    with cols[2]:
        hot_spot_fac = st.number_input(
            "Hot-spot factor [-]",
            value=float(preset.hot_spot_fac) if preset.hot_spot_fac is not None else None,
            step=0.05,
            min_value=0.0,
            key=f"{key_prefix}.hot_spot_fac",
            help="La stå tom for å bruke standardverdi fra biblioteket.",
        )
    cols = st.columns(2)
    with cols[0]:
        winding_oil_gradient = st.number_input(
            "Winding-oil gradient [K]",
            value=float(preset.winding_oil_gradient) if preset.winding_oil_gradient is not None else None,
            step=1.0,
            min_value=0.0,
            key=f"{key_prefix}.winding_oil_gradient",
            help="La stå tom for å bruke standardverdi fra biblioteket.",
        )
    with cols[1]:
        time_const_winding = st.number_input(
            "Winding time constant [min]",
            value=float(preset.time_const_winding) if preset.time_const_winding is not None else None,
            step=1.0,
            min_value=0.0,
            key=f"{key_prefix}.time_const_winding",
            help="La stå tom for å bruke standardverdi fra biblioteket.",
        )

    optional = {
        "hot_spot_fac": hot_spot_fac,
        "winding_oil_gradient": winding_oil_gradient,
        "time_const_winding": time_const_winding,
    }
    return WindingSpecifications(
        nom_load=nom_load,
        nom_power=nom_power,
        **{k: v for k, v in optional.items() if v is not None},
    )


def render_three_winding_spec_form(
    preset: UserThreeWindingTransformerSpecifications,
    key_prefix: str,
) -> UserThreeWindingTransformerSpecifications:
    """Render an override form for three-winding transformer specs."""
    with st.expander("Overstyr spesifikasjoner", expanded=False):
        st.markdown("**Viklinger**")
        lv = _render_winding_form(preset.lv_winding, f"{key_prefix}.lv", "Lavspenningsvikling")
        mv = _render_winding_form(preset.mv_winding, f"{key_prefix}.mv", "Mellomspenningsvikling")
        hv = _render_winding_form(preset.hv_winding, f"{key_prefix}.hv", "Høyspenningsvikling")

        st.markdown("**Tap mellom viklinger [W]**")
        cols = st.columns(3)
        with cols[0]:
            load_loss_hv_lv = st.number_input(
                "HV → LV", value=float(preset.load_loss_hv_lv), step=1000.0, min_value=0.0,
                key=f"{key_prefix}.load_loss_hv_lv",
            )
        with cols[1]:
            load_loss_hv_mv = st.number_input(
                "HV → MV", value=float(preset.load_loss_hv_mv), step=1000.0, min_value=0.0,
                key=f"{key_prefix}.load_loss_hv_mv",
            )
        with cols[2]:
            load_loss_mv_lv = st.number_input(
                "MV → LV", value=float(preset.load_loss_mv_lv), step=1000.0, min_value=0.0,
                key=f"{key_prefix}.load_loss_mv_lv",
            )

        st.markdown("**Felles**")
        cols = st.columns(3)
        with cols[0]:
            no_load_loss = st.number_input(
                "No-load loss [W]", value=float(preset.no_load_loss), step=500.0, min_value=0.0,
                key=f"{key_prefix}.no_load_loss",
            )
        with cols[1]:
            amb_temp_surcharge = st.number_input(
                "Ambient surcharge [K]",
                value=float(preset.amb_temp_surcharge) if preset.amb_temp_surcharge is not None else None,
                step=1.0,
                key=f"{key_prefix}.amb_temp_surcharge",
                help="La stå tom for å bruke standardverdi fra biblioteket.",
                min_value=None,
            )
        with cols[2]:
            top_oil_temp_rise = st.number_input(
                "Top-oil temp rise [K]",
                value=float(preset.top_oil_temp_rise) if preset.top_oil_temp_rise is not None else None,
                step=1.0,
                min_value=0.0,
                key=f"{key_prefix}.top_oil_temp_rise",
                help="La stå tom for å bruke standardverdi fra biblioteket.",
            )

    kwargs: dict[str, object] = {
        "no_load_loss": no_load_loss,
        "lv_winding": lv,
        "mv_winding": mv,
        "hv_winding": hv,
        "load_loss_hv_lv": load_loss_hv_lv,
        "load_loss_hv_mv": load_loss_hv_mv,
        "load_loss_mv_lv": load_loss_mv_lv,
    }
    if amb_temp_surcharge is not None:
        kwargs["amb_temp_surcharge"] = amb_temp_surcharge
    if top_oil_temp_rise is not None:
        kwargs["top_oil_temp_rise"] = top_oil_temp_rise

    return UserThreeWindingTransformerSpecifications(**kwargs)


# ---------------------------------------------------------------------------
# Profile pickers
# ---------------------------------------------------------------------------


def render_profile_picker(
    specs: UserTransformerSpecifications,
    key_prefix: str,
) -> InputProfile:
    """Render a selectbox over two-winding profile presets with a preview plot."""
    label = st.selectbox(
        "Lastprofil",
        options=list(PROFILE_PRESETS),
        key=f"{key_prefix}.profile_label",
    )
    profile = PROFILE_PRESETS[label](specs.nom_load_sec_side)
    st.caption(f"{len(profile)} målinger · tidssteg = {_describe_time_step(profile.time_step)}")
    st.plotly_chart(plots.plot_load_profile(profile), width="stretch", key=f"{key_prefix}.profile_preview")
    return profile


def render_three_winding_profile_picker(
    specs: UserThreeWindingTransformerSpecifications,
    key_prefix: str,
) -> ThreeWindingInputProfile:
    """Render a selectbox over three-winding profile presets with a preview plot."""
    label = st.selectbox(
        "Lastprofil",
        options=list(THREE_WINDING_PROFILE_PRESETS),
        key=f"{key_prefix}.profile_label",
    )
    profile = THREE_WINDING_PROFILE_PRESETS[label](
        specs.lv_winding.nom_load,
        specs.mv_winding.nom_load,
        specs.hv_winding.nom_load,
    )
    st.caption(f"{len(profile)} målinger · tidssteg = {_describe_time_step(profile.time_step)}")
    st.plotly_chart(plots.plot_load_profile(profile), width="stretch", key=f"{key_prefix}.profile_preview")
    return profile


def _describe_time_step(time_step: np.ndarray) -> str:
    # The first value is always 0 (prepend=first), so skip it.
    if len(time_step) < 2:
        return "ukjent"
    dt = float(time_step[1])
    return f"{dt:g} min"


# ---------------------------------------------------------------------------
# Initial state
# ---------------------------------------------------------------------------


def render_initial_state_picker(key_prefix: str) -> InitialState:
    """Radio over ColdStart / InitialLoad / InitialTopOilTemp."""
    mode = st.radio(
        "Starttilstand",
        options=["Kaldstart", "Startlast", "Start topp-oljetemperatur"],
        horizontal=True,
        key=f"{key_prefix}.initial_state_mode",
    )
    if mode == "Kaldstart":
        return ColdStart()
    if mode == "Startlast":
        initial_load = st.number_input(
            "Initial load [A]",
            value=0.0,
            step=10.0,
            min_value=0.0,
            key=f"{key_prefix}.initial_load",
        )
        return InitialLoad(initial_load=initial_load)
    initial_top = st.number_input(
        "Initial top-oil temperature [°C]",
        value=30.0,
        step=1.0,
        key=f"{key_prefix}.initial_top_oil_temp",
    )
    return InitialTopOilTemp(initial_top_oil_temp=initial_top)


# ---------------------------------------------------------------------------
# Cooling switch
# ---------------------------------------------------------------------------


def render_cooling_switch_form(
    onaf_specs: UserTransformerSpecifications,
    profile_length: int,
    key_prefix: str,
    onan_key_prefix: str | None = None,
) -> tuple[CoolingSwitchSettings, np.ndarray | None]:
    """Render the ONAN/ONAF switch form and return the settings + effective fan_on array.

    The second return value is the ``fan_on`` array when the user picked the
    schedule mode — useful for overlaying on the temperature plot. When the
    user picked the temperature-threshold mode it's ``None`` (the library
    computes the fan state internally).

    ``key_prefix`` scopes the tab-level switch controls (mode, thresholds, fan
    schedule). ``onan_key_prefix`` scopes the ONAN-parameter widgets, whose
    defaults come from ``onaf_specs`` and therefore need to re-initialise when
    the preset changes; it defaults to ``key_prefix`` for backward compatibility.
    """
    onan_prefix = onan_key_prefix if onan_key_prefix is not None else key_prefix
    st.markdown("**ONAN/ONAF-bryter**")
    mode = st.radio(
        "Utløser for omkobling",
        options=["Temperaturgrense", "Vifteplan"],
        horizontal=True,
        key=f"{key_prefix}.cooling_mode",
    )

    fan_on_array: np.ndarray | None = None
    temperature_threshold: CoolingSwitchConfig | None = None
    fan_on_param: np.ndarray | None = None

    if mode == "Temperaturgrense":
        cols = st.columns(2)
        with cols[0]:
            activation = st.number_input(
                "Fan activation temperature [°C]",
                value=75.0,
                step=1.0,
                key=f"{key_prefix}.activation_temp",
            )
        with cols[1]:
            deactivation = st.number_input(
                "Fan deactivation temperature [°C]",
                value=65.0,
                step=1.0,
                key=f"{key_prefix}.deactivation_temp",
                help="Må være lavere enn aktiveringstemperaturen.",
            )
        temperature_threshold = CoolingSwitchConfig(
            activation_temp=activation,
            deactivation_temp=deactivation,
        )
    else:
        # Simple fan schedule: fans on between two fractions of the simulation
        on_start, on_end = st.slider(
            "Vifte-på-vindu (i % av simuleringen)",
            min_value=0,
            max_value=100,
            value=(50, 100),
            step=5,
            key=f"{key_prefix}.fan_window",
        )
        start_idx = int(round(on_start / 100 * profile_length))
        end_idx = int(round(on_end / 100 * profile_length))
        fan_on_array = np.zeros(profile_length, dtype=bool)
        fan_on_array[start_idx:end_idx] = True
        fan_on_param = fan_on_array

    with st.expander("ONAN-modus-parametere (når viftene er av)", expanded=False):
        cols = st.columns(3)
        with cols[0]:
            top_oil_temp_rise = st.number_input(
                "Top-oil rise [K]", value=float(onaf_specs.top_oil_temp_rise or 50.0), step=1.0,
                min_value=0.0, key=f"{onan_prefix}.onan_top_oil_temp_rise",
            )
            load_loss = st.number_input(
                "Load loss [W]", value=float(onaf_specs.load_loss), step=1000.0,
                min_value=0.0, key=f"{onan_prefix}.onan_load_loss",
            )
        with cols[1]:
            time_const_oil = st.number_input(
                "Oil time constant [min]", value=float(onaf_specs.time_const_oil or 210.0), step=5.0,
                min_value=0.0, key=f"{onan_prefix}.onan_time_const_oil",
            )
            nom_load_sec_side = st.number_input(
                "Nominal load [A]", value=float(onaf_specs.nom_load_sec_side), step=10.0,
                min_value=0.0, key=f"{onan_prefix}.onan_nom_load",
                help="Ofte lavere enn ONAF-merkeverdien — vifter gir høyere kapasitet.",
            )
        with cols[2]:
            time_const_windings = st.number_input(
                "Winding time constant [min]", value=float(onaf_specs.time_const_windings or 10.0), step=1.0,
                min_value=0.0, key=f"{onan_prefix}.onan_time_const_windings",
            )
            winding_oil_gradient = st.number_input(
                "Winding-oil gradient [K]", value=float(onaf_specs.winding_oil_gradient or 20.0), step=1.0,
                min_value=0.0, key=f"{onan_prefix}.onan_winding_oil_gradient",
            )
        hot_spot_fac = st.number_input(
            "Hot-spot factor [-]", value=float(onaf_specs.hot_spot_fac or 1.2), step=0.05,
            min_value=0.0, key=f"{onan_prefix}.onan_hot_spot_fac",
        )

    onan_parameters = ONANParameters(
        top_oil_temp_rise=top_oil_temp_rise,
        time_const_oil=time_const_oil,
        time_const_windings=time_const_windings,
        load_loss=load_loss,
        nom_load_sec_side=nom_load_sec_side,
        winding_oil_gradient=winding_oil_gradient,
        hot_spot_fac=hot_spot_fac,
    )

    if temperature_threshold is not None:
        settings = CoolingSwitchSettings(
            temperature_threshold=temperature_threshold,
            onan_parameters=onan_parameters,
        )
    else:
        settings = CoolingSwitchSettings(
            fan_on=fan_on_param,
            onan_parameters=onan_parameters,
        )

    return settings, fan_on_array
