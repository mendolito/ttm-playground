# SPDX-FileCopyrightText: Contributors to the Transformer Thermal Model project
#
# SPDX-License-Identifier: MPL-2.0

"""Transformer and load/ambient profile presets for the Streamlit UI.

The presets are plain data (Pydantic specs and factory callables). Forms pre-fill
from them and round-trip user overrides back into fresh spec instances, so no
runtime coupling to the rendering code is required.
"""

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
import pandas as pd

from transformer_thermal_model.cooler import CoolerType
from transformer_thermal_model.schemas import (
    InputProfile,
    ThreeWindingInputProfile,
    UserThreeWindingTransformerSpecifications,
    UserTransformerSpecifications,
    WindingSpecifications,
)
from transformer_thermal_model.schemas.thermal_model import CoolingSwitchSettings
from transformer_thermal_model.transformer import (
    DistributionTransformer,
    PowerTransformer,
    ThreeWindingTransformer,
)

# ---------------------------------------------------------------------------
# Transformer presets
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TransformerPreset:
    """A labelled preset for a two-winding transformer.

    Holds the required user specs plus the transformer family (power vs
    distribution) and a suggested default cooling type for power transformers.
    Distribution transformers are always ONAN in this library and take no
    cooling_type argument.
    """

    specs: UserTransformerSpecifications
    default_cooling_type: CoolerType
    is_distribution: bool


@dataclass(frozen=True)
class ThreeWindingTransformerPreset:
    """A labelled preset for a three-winding transformer."""

    specs: UserThreeWindingTransformerSpecifications
    default_cooling_type: CoolerType


# Values are inspired by the example notebooks in ``docs/examples``; they're
# calibrated to produce meaningful (non-degenerate) thermal curves when paired
# with any of the profile presets below, not to represent any specific real
# transformer nameplate.
TRANSFORMER_PRESETS: dict[str, TransformerPreset] = {
    "Typical 400 MVA power (ONAF)": TransformerPreset(
        specs=UserTransformerSpecifications(
            load_loss=160_000,
            nom_load_sec_side=3000,
            no_load_loss=70_000,
            amb_temp_surcharge=10,
        ),
        default_cooling_type=CoolerType.ONAF,
        is_distribution=False,
    ),
    "Typical 100 MVA power (ONAN)": TransformerPreset(
        specs=UserTransformerSpecifications(
            load_loss=40_000,
            nom_load_sec_side=1500,
            no_load_loss=20_000,
            amb_temp_surcharge=20,
        ),
        default_cooling_type=CoolerType.ONAN,
        is_distribution=False,
    ),
    "Typical 1 MVA distribution (ONAN)": TransformerPreset(
        specs=UserTransformerSpecifications(
            load_loss=10_000,
            nom_load_sec_side=1500,
            no_load_loss=1_500,
        ),
        default_cooling_type=CoolerType.ONAN,
        is_distribution=True,
    ),
}


THREE_WINDING_PRESETS: dict[str, ThreeWindingTransformerPreset] = {
    "Typical three-winding (ONAF)": ThreeWindingTransformerPreset(
        specs=UserThreeWindingTransformerSpecifications(
            no_load_loss=20_000,
            amb_temp_surcharge=10,
            lv_winding=WindingSpecifications(
                nom_load=1000,
                nom_power=100,
                winding_oil_gradient=20,
                hot_spot_fac=1.2,
                time_const_winding=7,
            ),
            mv_winding=WindingSpecifications(
                nom_load=1000,
                nom_power=100,
                winding_oil_gradient=20,
                hot_spot_fac=1.2,
                time_const_winding=7,
            ),
            hv_winding=WindingSpecifications(
                nom_load=2000,
                nom_power=200,
                winding_oil_gradient=20,
                hot_spot_fac=1.2,
                time_const_winding=7,
            ),
            load_loss_hv_lv=100_000,
            load_loss_hv_mv=100_000,
            load_loss_mv_lv=100_000,
        ),
        default_cooling_type=CoolerType.ONAF,
    ),
}


# ---------------------------------------------------------------------------
# Profile presets — factories parameterised by nominal load
# ---------------------------------------------------------------------------


ProfileFactory = Callable[[float], InputProfile]
ThreeWindingProfileFactory = Callable[[float, float, float], ThreeWindingInputProfile]


def _iec_reference_profile(nom_load: float) -> InputProfile:
    """Piecewise IEC load profile with overloads, 5-min steps.

    Adapted from the IEC 60076-7 reference profile used in the library's test
    fixtures. Factors range from 0.0 to 2.1 × nominal load; ambient is held at
    25.6 °C.
    """
    breakpoints_min = [0, 190, 365, 500, 705, 730, 745]
    load_factors = [1.0, 0.6, 1.5, 0.3, 2.1, 0.0]
    timestep_min = 5

    start_time = pd.Timestamp("2025-01-01 00:00:00")
    timestamps: list[pd.Timestamp] = []
    loads: list[float] = []
    for i in range(len(breakpoints_min) - 1):
        start = breakpoints_min[i]
        end = breakpoints_min[i + 1]
        n_steps = (end - start) // timestep_min
        for step in range(1, n_steps + 1):
            timestamps.append(start_time + pd.Timedelta(minutes=start + step * timestep_min))
            loads.append(load_factors[i] * nom_load)

    ambient = [25.6] * len(timestamps)
    return InputProfile.create(
        datetime_index=timestamps,
        load_profile=loads,
        ambient_temperature_profile=ambient,
    )


def _constant_nominal_profile(nom_load: float) -> InputProfile:
    """One-week constant nominal load at 20 °C ambient, 15-min steps."""
    one_week = 4 * 24 * 7
    datetime_index = pd.date_range("2025-07-01", periods=one_week, freq="15min")
    return InputProfile.create(
        datetime_index=list(datetime_index),
        load_profile=[nom_load] * one_week,
        ambient_temperature_profile=[20.0] * one_week,
    )


def _step_load_profile(nom_load: float) -> InputProfile:
    """24-hour profile that steps from 50 % to 130 % of nominal at t = 12 h."""
    one_day = 4 * 24
    datetime_index = pd.date_range("2025-07-01", periods=one_day, freq="15min")
    halfway = one_day // 2
    loads = [0.5 * nom_load] * halfway + [1.3 * nom_load] * (one_day - halfway)
    return InputProfile.create(
        datetime_index=list(datetime_index),
        load_profile=loads,
        ambient_temperature_profile=[20.0] * one_day,
    )


def _diurnal_sinusoid_profile(nom_load: float) -> InputProfile:
    """Two days of sinusoidal load (0.7–1.3 × nominal) and ambient (10–25 °C)."""
    two_days = 4 * 24 * 2
    datetime_index = pd.date_range("2025-07-01", periods=two_days, freq="15min")
    t = np.arange(two_days, dtype=float)
    day_steps = 4 * 24
    load = (1.0 + 0.3 * np.sin(2 * np.pi * t / day_steps)) * nom_load
    # Ambient trough at dawn (quarter-day lag vs load midpoint): 10 °C min, 25 °C max.
    ambient = 17.5 + 7.5 * np.sin(2 * np.pi * (t - day_steps / 4) / day_steps)
    return InputProfile.create(
        datetime_index=list(datetime_index),
        load_profile=load.tolist(),
        ambient_temperature_profile=ambient.tolist(),
    )


PROFILE_PRESETS: dict[str, ProfileFactory] = {
    "IEC reference load (overloads, ~12 h)": _iec_reference_profile,
    "Constant nominal load (1 week)": _constant_nominal_profile,
    "Step load 50 % → 130 % (24 h)": _step_load_profile,
    "Diurnal sinusoid (48 h)": _diurnal_sinusoid_profile,
}


def _three_winding_diurnal_profile(
    nom_lv: float,
    nom_mv: float,
    nom_hv: float,
) -> ThreeWindingInputProfile:
    """Two days of sinusoidal load on every winding with a matching ambient cycle."""
    two_days = 4 * 24 * 2
    datetime_index = pd.date_range("2025-07-01", periods=two_days, freq="15min")
    t = np.arange(two_days, dtype=float)
    day_steps = 4 * 24
    factor = 1.0 + 0.3 * np.sin(2 * np.pi * t / day_steps)
    ambient = 17.5 + 7.5 * np.sin(2 * np.pi * (t - day_steps / 4) / day_steps)
    return ThreeWindingInputProfile.create(
        datetime_index=list(datetime_index),
        ambient_temperature_profile=ambient.tolist(),
        load_profile_low_voltage_side=(factor * nom_lv).tolist(),
        load_profile_middle_voltage_side=(factor * nom_mv).tolist(),
        load_profile_high_voltage_side=(factor * nom_hv).tolist(),
    )


def _three_winding_constant_profile(
    nom_lv: float,
    nom_mv: float,
    nom_hv: float,
) -> ThreeWindingInputProfile:
    """One week of constant per-winding nominal load at 20 °C ambient."""
    one_week = 4 * 24 * 7
    datetime_index = pd.date_range("2025-07-01", periods=one_week, freq="15min")
    return ThreeWindingInputProfile.create(
        datetime_index=list(datetime_index),
        ambient_temperature_profile=[20.0] * one_week,
        load_profile_low_voltage_side=[nom_lv] * one_week,
        load_profile_middle_voltage_side=[nom_mv] * one_week,
        load_profile_high_voltage_side=[nom_hv] * one_week,
    )


THREE_WINDING_PROFILE_PRESETS: dict[str, ThreeWindingProfileFactory] = {
    "Diurnal sinusoid (48 h)": _three_winding_diurnal_profile,
    "Constant nominal load (1 week)": _three_winding_constant_profile,
}


# ---------------------------------------------------------------------------
# Transformer construction helpers
# ---------------------------------------------------------------------------


def build_two_winding_transformer(
    preset: TransformerPreset,
    specs: UserTransformerSpecifications,
    cooling_type: CoolerType | None = None,
    cooling_switch_settings: CoolingSwitchSettings | None = None,
) -> PowerTransformer | DistributionTransformer:
    """Construct the right Transformer subclass for a two-winding preset.

    DistributionTransformer ignores ``cooling_type`` / ``cooling_switch_settings``
    — the library fixes it to ONAN and has no switch support — so the caller
    doesn't have to special-case that distinction.
    """
    if preset.is_distribution:
        return DistributionTransformer(user_specs=specs)
    return PowerTransformer(
        user_specs=specs,
        cooling_type=cooling_type if cooling_type is not None else preset.default_cooling_type,
        cooling_switch_settings=cooling_switch_settings,
    )


def build_three_winding_transformer(
    preset: ThreeWindingTransformerPreset,
    specs: UserThreeWindingTransformerSpecifications,
    cooling_type: CoolerType | None = None,
) -> ThreeWindingTransformer:
    """Construct a ThreeWindingTransformer from a preset + (possibly edited) specs."""
    return ThreeWindingTransformer(
        user_specs=specs,
        cooling_type=cooling_type if cooling_type is not None else preset.default_cooling_type,
    )
