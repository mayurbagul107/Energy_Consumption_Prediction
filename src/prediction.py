"""
prediction.py
Handles prediction logic, input validation, uncertainty quantification, and prediction history.
"""

import pandas as pd
import numpy as np
import calendar
from datetime import date
from typing import Dict, Any, Tuple, Optional, List
from sklearn.pipeline import Pipeline


from src.mseb_tariff import (
    calculate_mseb_cost,
    calculate_msedcl_2026_bill,
    calculate_msedcl_daily_bill,
    BILLING_PERIODS_CONFIG,
    CONNECTION_TYPES,
    DEFAULT_MSEDCL_SLABS_2026,
    DEFAULT_MSEDCL_DAILY_SLABS_2026,
    DEFAULT_WHEELING_CHARGE_PER_UNIT,
    DEFAULT_FIXED_CHARGE_SINGLE_PHASE,
    DEFAULT_FIXED_CHARGE_THREE_PHASE,
    DEFAULT_ELECTRICITY_DUTY_PCT,
    DEFAULT_MUNICIPAL_CHARGE_MONTHLY,
    DISCLAIMER_TEXT,
    DAILY_DISCLAIMER_TEXT,
    VALID_BILLING_PERIODS,
    VALID_CONNECTION_TYPES
)

VALID_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
VALID_HVAC = ['On', 'Off']
VALID_LIGHTING = ['On', 'Off']
VALID_HOLIDAY = ['No', 'Yes']


def validate_inputs(inputs: Dict[str, Any]) -> Tuple[bool, str]:
    """Validates user inputs from prediction form."""
    try:
        temp = float(inputs.get('Temperature', 0))
        if not (-30.0 <= temp <= 65.0):
            return False, f"Temperature ({temp} °C) is outside realistic range (-30 °C to 65 °C)."

        humidity = float(inputs.get('Humidity', 0))
        if not (0.0 <= humidity <= 100.0):
            return False, f"Humidity ({humidity}%) must be between 0% and 100%."

        sqft = float(inputs.get('SquareFootage', 0))
        if sqft <= 0:
            return False, f"Square Footage ({sqft}) must be greater than 0."

        occupancy = int(inputs.get('Occupancy', 0))
        if occupancy < 0:
            return False, f"Occupancy ({occupancy}) cannot be negative."

        renewable = float(inputs.get('RenewableEnergy', 0))
        if renewable < 0:
            return False, f"Renewable Energy ({renewable} kWh) cannot be negative."

        hvac = str(inputs.get('HVACUsage', '')).strip().capitalize()
        if hvac not in VALID_HVAC:
            return False, f"HVAC Usage must be 'On' or 'Off'."

        lighting = str(inputs.get('LightingUsage', '')).strip().capitalize()
        if lighting not in VALID_LIGHTING:
            return False, f"Lighting Usage must be 'On' or 'Off'."

        day = str(inputs.get('DayOfWeek', '')).strip().capitalize()
        if day and day not in VALID_DAYS:
            return False, f"Day of Week must be a valid weekday name."

        raw_holiday = str(inputs.get('Holiday', 'No')).strip()
        holiday = raw_holiday.capitalize()
        if holiday not in VALID_HOLIDAY:
            if 'normal' in raw_holiday.lower() or 'no' in raw_holiday.lower():
                inputs['Holiday'] = 'No'
            elif 'statutory' in raw_holiday.lower() or 'yes' in raw_holiday.lower():
                inputs['Holiday'] = 'Yes'
            else:
                return False, f"Holiday must be 'Yes' or 'No'."
        else:
            inputs['Holiday'] = holiday

        return True, ""
    except (ValueError, TypeError) as e:
        return False, f"Invalid numerical value: {str(e)}"


def predict_energy(
    pipeline: Pipeline,
    inputs: Dict[str, Any],
    connection_type: str = "Single Phase (Domestic Standard — ₹130/month)",
    billing_period: str = "April 2026 (Initial Tariff Order)",
    fac_rate: Optional[float] = None,
    wheeling_rate: Optional[float] = None,
    fixed_charge: Optional[float] = None,
    electricity_duty_pct: Optional[float] = None,
    apply_municipal_charge: bool = True,
    mseb_category: str = "Residential (LT-I Domestic — 1 April 2026 Tariff)",
    three_phase: bool = False
) -> Dict[str, Any]:
    """
    Executes prediction using genuine trained model pipeline.
    Computes ensemble standard error for confidence intervals if model is RandomForest.
    Calculates estimated electricity bill based on official MSEDCL domestic tariff
    applicable from 1 April 2026.
    
    Returns dictionary with predicted value, bounds, confidence interval, MSEDCL bill, and input echoes.
    """
    is_valid, error_msg = validate_inputs(inputs)
    if not is_valid:
        raise ValueError(error_msg)

    # Convert to single-row DataFrame matching training feature columns
    df_input = pd.DataFrame([{
        'Temperature': float(inputs['Temperature']),
        'Humidity': float(inputs['Humidity']),
        'SquareFootage': float(inputs['SquareFootage']),
        'Occupancy': int(inputs['Occupancy']),
        'RenewableEnergy': float(inputs['RenewableEnergy']),
        'HVACUsage': str(inputs['HVACUsage']).capitalize(),
        'LightingUsage': str(inputs['LightingUsage']).capitalize(),
        'DayOfWeek': str(inputs['DayOfWeek']).capitalize(),
        'Holiday': str(inputs['Holiday']).capitalize(),
    }])

    predicted_val = float(pipeline.predict(df_input)[0])

    # Uncertainty estimation using tree ensemble variance
    lower_bound = predicted_val - 1.5
    upper_bound = predicted_val + 1.5
    std_dev = 0.83

    try:
        model = pipeline.named_steps.get('model')
        prep = pipeline.named_steps.get('prep')
        if hasattr(model, 'estimators_') and prep is not None:
            # Transform input features
            transformed_x = prep.transform(df_input)
            # Collect individual tree predictions
            tree_preds = [float(tree.predict(transformed_x)[0]) for tree in model.estimators_]
            std_dev = float(np.std(tree_preds))
            lower_bound = max(0.0, float(np.percentile(tree_preds, 5)))
            upper_bound = float(np.percentile(tree_preds, 95))
    except Exception:
        pass

    # Official MSEDCL Domestic Tariff (1 April 2026) Bill Calculations
    msedcl_bill = calculate_msedcl_2026_bill(
        monthly_kwh=predicted_val,
        connection_type=connection_type,
        billing_period=billing_period,
        fac_rate=fac_rate,
        wheeling_rate=wheeling_rate,
        fixed_charge=fixed_charge,
        electricity_duty_pct=electricity_duty_pct,
        apply_municipal_charge=apply_municipal_charge
    )
    msedcl_lb_bill = calculate_msedcl_2026_bill(
        monthly_kwh=lower_bound,
        connection_type=connection_type,
        billing_period=billing_period,
        fac_rate=fac_rate,
        wheeling_rate=wheeling_rate,
        fixed_charge=fixed_charge,
        electricity_duty_pct=electricity_duty_pct,
        apply_municipal_charge=apply_municipal_charge
    )
    msedcl_ub_bill = calculate_msedcl_2026_bill(
        monthly_kwh=upper_bound,
        connection_type=connection_type,
        billing_period=billing_period,
        fac_rate=fac_rate,
        wheeling_rate=wheeling_rate,
        fixed_charge=fixed_charge,
        electricity_duty_pct=electricity_duty_pct,
        apply_municipal_charge=apply_municipal_charge
    )

    # General multi-mode pricing object for backward compatibility
    mseb_pricing = calculate_mseb_cost(
        units_kwh=predicted_val,
        category=mseb_category,
        three_phase=three_phase,
        billing_period=billing_period,
        fac_rate=fac_rate,
        wheeling_rate=wheeling_rate,
        fixed_charge=fixed_charge,
        electricity_duty_pct=electricity_duty_pct,
        apply_municipal_charge=apply_municipal_charge
    )

    # Dynamic contextual insights for this specific prediction
    factors = []
    effective_rate = msedcl_bill['effective_rate_per_kwh']
    if float(inputs['Temperature']) > 26.0:
        factors.append("High ambient temperature driving higher thermal cooling demand")
    elif float(inputs['Temperature']) < 22.0:
        factors.append("Low ambient temperature moderating cooling demand")

    if str(inputs['HVACUsage']).capitalize() == 'On':
        factors.append(f"HVAC active (+~4.66 kWh / ~₹{4.66 * effective_rate:.2f} impact under MSEDCL 2026 tariff)")
    else:
        factors.append("HVAC inactive (baseload cooling disabled)")

    if str(inputs['LightingUsage']).capitalize() == 'On':
        factors.append(f"Lighting active (+~1.31 kWh / ~₹{1.31 * effective_rate:.2f} load)")

    if int(inputs['Occupancy']) > 5:
        factors.append(f"Elevated occupancy ({inputs['Occupancy']} persons) increasing internal heat gains")

    if float(inputs['RenewableEnergy']) > 15.0:
        solar_credit = float(inputs['RenewableEnergy']) * effective_rate
        factors.append(f"High onsite renewable generation ({inputs['RenewableEnergy']} kWh saved ≈ ₹{solar_credit:.2f} MSEDCL bill offset)")

    return {
        'prediction': predicted_val,
        'lower_bound': lower_bound,
        'upper_bound': upper_bound,
        'std_error': std_dev,
        'unit': 'kWh',
        'msedcl_bill': msedcl_bill,
        'msedcl_lb_bill': msedcl_lb_bill,
        'msedcl_ub_bill': msedcl_ub_bill,
        'mseb_pricing': mseb_pricing,
        'mseb_cost_direct': msedcl_bill['total_estimated_bill'],
        'mseb_cost_lb': msedcl_lb_bill['total_estimated_bill'],
        'mseb_cost_ub': msedcl_ub_bill['total_estimated_bill'],
        'mseb_category': mseb_category,
        'disclaimer': DISCLAIMER_TEXT,
        'key_factors': factors,
        'input_data': inputs
    }


def generate_24h_schedule(
    target_date: date,
    base_inputs: Dict[str, Any]
) -> pd.DataFrame:
    """
    Generates a realistic 24-hour diurnal profile (Hour 0 to 23) for the selected target date.
    Calculates natural diurnal variations for temperature, humidity, occupancy, lighting,
    and solar photovoltaic generation.
    """
    day_name = target_date.strftime("%A")
    is_weekend = day_name in ['Saturday', 'Sunday']
    holiday_status = str(base_inputs.get('Holiday', 'No')).capitalize()
    is_off_day = (holiday_status == 'Yes') or is_weekend

    base_temp = float(base_inputs.get('Temperature', 25.0))
    base_hum = float(base_inputs.get('Humidity', 45.0))
    sqft = float(base_inputs.get('SquareFootage', 1500.0))
    base_occ = int(base_inputs.get('Occupancy', 4))
    peak_solar = float(base_inputs.get('RenewableEnergy', 10.0))
    hvac_mode = str(base_inputs.get('HVACUsage', 'On')).capitalize()
    lighting_mode = str(base_inputs.get('LightingUsage', 'On')).capitalize()

    records = []
    for h in range(24):
        # Diurnal temperature: sine curve peaking at 15:00, coolest at 04:00
        temp_val = round(base_temp + 4.5 * np.sin(2 * np.pi * (h - 8.5) / 24.0), 1)
        # Humidity inversely proportional to temperature
        hum_val = round(float(np.clip(base_hum - 7.0 * np.sin(2 * np.pi * (h - 8.5) / 24.0), 5.0, 98.0)), 1)
        
        # Diurnal occupancy profile
        if is_off_day:
            occ_val = base_occ
        else:
            if 0 <= h < 7:
                occ_val = base_occ
            elif 7 <= h < 9:
                occ_val = base_occ
            elif 9 <= h < 17:
                occ_val = max(1, int(round(base_occ * 0.5)))
            else:
                occ_val = base_occ

        # HVAC operational status
        if hvac_mode == 'On':
            hvac_h = 'On' if (temp_val >= 23.5 or 10 <= h <= 22) else 'Off'
        else:
            hvac_h = 'Off'

        # Lighting operational status
        if lighting_mode == 'On':
            lighting_h = 'Off' if (7 <= h <= 18) else 'On'
        else:
            lighting_h = 'Off'

        # Solar PV generation: half-sine between 06:00 and 18:00
        if 6 <= h <= 18 and peak_solar > 0:
            solar_h = round(float(peak_solar * np.sin(np.pi * (h - 6) / 12.0)), 2)
        else:
            solar_h = 0.0

        records.append({
            'Hour': h,
            'Time': f"{h:02d}:00",
            'Temperature': temp_val,
            'Humidity': hum_val,
            'SquareFootage': sqft,
            'Occupancy': occ_val,
            'RenewableEnergy': solar_h,
            'HVACUsage': hvac_h,
            'LightingUsage': lighting_h,
            'DayOfWeek': day_name,
            'Holiday': holiday_status
        })

    return pd.DataFrame(records)


def predict_daily_24h_energy(
    pipeline: Pipeline,
    target_date: date,
    base_inputs: Dict[str, Any],
    connection_type: str = "Single Phase (Domestic Standard — ₹130/month)",
    billing_period: str = "April 2026 (Initial Tariff Order)",
    fac_rate: Optional[float] = None,
    wheeling_rate: Optional[float] = None,
    fixed_charge_monthly: Optional[float] = None,
    electricity_duty_pct: Optional[float] = None,
    apply_municipal_charge: bool = True,
    slab_mode: str = "prorated",
    custom_slabs: Optional[List[Dict[str, Any]]] = None,
    custom_hourly_df: Optional[pd.DataFrame] = None
) -> Dict[str, Any]:
    """
    Predicts 24-hour hourly electricity consumption for a single day and calculates
    estimated daily energy charges, applicable additional charges, and total estimated daily amount
    under official MSEDCL 2026 tariff rules.
    """
    is_valid, error_msg = validate_inputs(base_inputs)
    if not is_valid:
        raise ValueError(error_msg)

    # 1. Generate 24-hour schedule or use custom hourly dataframe
    if custom_hourly_df is not None:
        df_24h = custom_hourly_df.copy()
    else:
        df_24h = generate_24h_schedule(target_date, base_inputs)

    # Model input feature columns
    feature_cols = [
        'Temperature', 'Humidity', 'SquareFootage', 'Occupancy',
        'RenewableEnergy', 'HVACUsage', 'LightingUsage', 'DayOfWeek', 'Holiday'
    ]
    df_features = df_24h[feature_cols].copy()

    # 2. Predict hourly consumption for 24 hours
    hourly_preds = pipeline.predict(df_features)
    hourly_preds = np.maximum(0.0, hourly_preds)

    # 3. Sum 24 hourly predictions to get total daily consumption
    total_daily_kwh = float(np.sum(hourly_preds))

    # Uncertainty estimation using tree ensemble variance over the full 24 hours
    model = pipeline.named_steps.get('model')
    prep = pipeline.named_steps.get('prep')
    if hasattr(model, 'estimators_') and prep is not None:
        try:
            trans_x = prep.transform(df_features)
            tree_daily_sums = []
            for tree in model.estimators_:
                t_preds = tree.predict(trans_x)
                tree_daily_sums.append(float(np.sum(np.maximum(0.0, t_preds))))
            daily_lb = max(0.0, float(np.percentile(tree_daily_sums, 5)))
            daily_ub = float(np.percentile(tree_daily_sums, 95))
            daily_std = float(np.std(tree_daily_sums))
        except Exception:
            daily_lb = max(0.0, total_daily_kwh * 0.95)
            daily_ub = total_daily_kwh * 1.05
            daily_std = (daily_ub - daily_lb) / 3.29
    else:
        daily_lb = max(0.0, total_daily_kwh * 0.95)
        daily_ub = total_daily_kwh * 1.05
        daily_std = (daily_ub - daily_lb) / 3.29

    # 4. Calculate MSEDCL Daily Electricity Charges for the single day
    msedcl_daily_bill = calculate_msedcl_daily_bill(
        daily_kwh=total_daily_kwh,
        connection_type=connection_type,
        billing_period=billing_period,
        fac_rate=fac_rate,
        wheeling_rate=wheeling_rate,
        fixed_charge_monthly=fixed_charge_monthly,
        electricity_duty_pct=electricity_duty_pct,
        apply_municipal_charge=apply_municipal_charge,
        slab_mode=slab_mode,
        custom_slabs=custom_slabs
    )

    msedcl_lb_daily_bill = calculate_msedcl_daily_bill(
        daily_kwh=daily_lb,
        connection_type=connection_type,
        billing_period=billing_period,
        fac_rate=fac_rate,
        wheeling_rate=wheeling_rate,
        fixed_charge_monthly=fixed_charge_monthly,
        electricity_duty_pct=electricity_duty_pct,
        apply_municipal_charge=apply_municipal_charge,
        slab_mode=slab_mode,
        custom_slabs=custom_slabs
    )

    msedcl_ub_daily_bill = calculate_msedcl_daily_bill(
        daily_kwh=daily_ub,
        connection_type=connection_type,
        billing_period=billing_period,
        fac_rate=fac_rate,
        wheeling_rate=wheeling_rate,
        fixed_charge_monthly=fixed_charge_monthly,
        electricity_duty_pct=electricity_duty_pct,
        apply_municipal_charge=apply_municipal_charge,
        slab_mode=slab_mode,
        custom_slabs=custom_slabs
    )

    # Projected 30-day monthly values for comparison
    projected_monthly_kwh = total_daily_kwh * 30.0
    msedcl_proj_monthly_bill = calculate_msedcl_2026_bill(
        monthly_kwh=projected_monthly_kwh,
        connection_type=connection_type,
        billing_period=billing_period,
        fac_rate=fac_rate,
        wheeling_rate=wheeling_rate,
        fixed_charge=fixed_charge_monthly,
        electricity_duty_pct=electricity_duty_pct,
        apply_municipal_charge=apply_municipal_charge
    )

    # Attach predictions to hourly DataFrame
    df_24h['Predicted_kWh'] = np.round(hourly_preds, 2)
    effective_rate = msedcl_daily_bill['effective_rate_per_kwh']
    df_24h['Estimated_Cost_INR'] = np.round(hourly_preds * effective_rate, 2)

    peak_idx = int(np.argmax(hourly_preds))
    min_idx = int(np.argmin(hourly_preds))

    return {
        'period_type': 'daily',
        'target_date': str(target_date),
        'day_of_week': target_date.strftime("%A"),
        # Requirement 7 separate labels:
        'daily_consumption_kwh': round(total_daily_kwh, 2),
        'monthly_consumption_kwh': round(projected_monthly_kwh, 2),
        'estimated_daily_cost': round(msedcl_daily_bill['total_estimated_amount'], 2),
        'estimated_monthly_bill': round(msedcl_proj_monthly_bill['total_estimated_bill'], 2),
        # Existing aliases for backwards compatibility:
        'total_daily_kwh': round(total_daily_kwh, 2),
        'daily_lb_kwh': round(daily_lb, 2),
        'daily_ub_kwh': round(daily_ub, 2),
        'daily_std': round(daily_std, 2),
        'hourly_df': df_24h,
        'peak_hour': df_24h.iloc[peak_idx]['Time'],
        'peak_kwh': round(float(hourly_preds[peak_idx]), 2),
        'baseload_hour': df_24h.iloc[min_idx]['Time'],
        'baseload_kwh': round(float(hourly_preds[min_idx]), 2),
        'msedcl_daily_bill': msedcl_daily_bill,
        'msedcl_lb_daily_bill': msedcl_lb_daily_bill,
        'msedcl_ub_daily_bill': msedcl_ub_daily_bill,
        'msedcl_monthly_bill': msedcl_proj_monthly_bill,
        'disclaimer': DAILY_DISCLAIMER_TEXT,
        'input_data': base_inputs
    }


def generate_monthly_schedule(
    year: int,
    month: int,
    base_inputs: Dict[str, Any]
) -> pd.DataFrame:
    """
    Generates a full hourly profile for the entire month (actual days in month * 24 hours).
    Reflects calendar progression (actual DayOfWeek for every calendar day, weekends, holidays),
    natural day/night diurnal variations, and daytime solar photovoltaic generation.
    """
    num_days = calendar.monthrange(year, month)[1]

    base_temp = float(base_inputs.get('Temperature', 25.0))
    base_hum = float(base_inputs.get('Humidity', 45.0))
    sqft = float(base_inputs.get('SquareFootage', 1500.0))
    base_occ = int(base_inputs.get('Occupancy', 4))
    peak_solar = float(base_inputs.get('RenewableEnergy', 10.0))
    hvac_mode = str(base_inputs.get('HVACUsage', 'On')).capitalize()
    lighting_mode = str(base_inputs.get('LightingUsage', 'On')).capitalize()
    holiday_input = str(base_inputs.get('Holiday', 'No')).capitalize()

    records = []
    for day_num in range(1, num_days + 1):
        cur_date = date(year, month, day_num)
        day_name = cur_date.strftime("%A")
        is_weekend = day_name in ['Saturday', 'Sunday']
        is_holiday = (holiday_input == 'Yes' and day_num == 1)
        is_off_day = is_weekend or is_holiday
        holiday_status = 'Yes' if is_holiday else 'No'

        # Natural multi-day weather wave across the month
        day_temp_drift = 2.0 * np.sin(2 * np.pi * (day_num - 1) / num_days)

        for h in range(24):
            # Diurnal temperature: sine curve peaking at 15:00, coolest at 04:00
            temp_val = round(base_temp + day_temp_drift + 4.5 * np.sin(2 * np.pi * (h - 8.5) / 24.0), 1)
            # Humidity inversely proportional to temperature
            hum_val = round(float(np.clip(base_hum - 7.0 * np.sin(2 * np.pi * (h - 8.5) / 24.0), 5.0, 98.0)), 1)

            # Occupancy profile
            if is_off_day:
                occ_val = base_occ
            else:
                if 9 <= h < 17:
                    occ_val = max(1, int(round(base_occ * 0.5)))
                else:
                    occ_val = base_occ

            # HVAC operational status
            if hvac_mode == 'On':
                hvac_h = 'On' if (temp_val >= 23.5 or 10 <= h <= 22) else 'Off'
            else:
                hvac_h = 'Off'

            # Lighting operational status
            if lighting_mode == 'On':
                lighting_h = 'Off' if (7 <= h <= 18) else 'On'
            else:
                lighting_h = 'Off'

            # Solar PV generation: half-sine between 06:00 and 18:00
            if 6 <= h <= 18 and peak_solar > 0:
                solar_h = round(float(peak_solar * np.sin(np.pi * (h - 6) / 12.0)), 2)
            else:
                solar_h = 0.0

            records.append({
                'Date': str(cur_date),
                'Day': day_num,
                'Hour': h,
                'Time': f"{h:02d}:00",
                'Timestamp': f"{cur_date} {h:02d}:00",
                'Temperature': temp_val,
                'Humidity': hum_val,
                'SquareFootage': sqft,
                'Occupancy': occ_val,
                'RenewableEnergy': solar_h,
                'HVACUsage': hvac_h,
                'LightingUsage': lighting_h,
                'DayOfWeek': day_name,
                'Holiday': holiday_status
            })

    return pd.DataFrame(records)


def predict_monthly_energy(
    pipeline: Pipeline,
    year: int,
    month: int,
    base_inputs: Dict[str, Any],
    connection_type: str = "Single Phase (Domestic Standard — ₹130/month)",
    billing_period: str = "April 2026 (Initial Tariff Order)",
    consumption_basis: str = "monthly_direct",
    sanctioned_load_kw: float = 2.0,
    fac_rate: Optional[float] = None,
    wheeling_rate: Optional[float] = None,
    fixed_charge_monthly: Optional[float] = None,
    electricity_duty_pct: Optional[float] = None,
    apply_municipal_charge: bool = True,
    municipal_charge_monthly: Optional[float] = None,
    custom_slabs: Optional[List[Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    Executes Monthly Electricity Consumption Prediction and calculates estimated MSEDCL bill.
    Supports 3 clear model output interpretations:
      1. 'monthly_direct': Direct model prediction represents monthly consumption (e.g. 77 kWh).
         Does not multiply again, preserving realistic residential domestic scale.
      2. 'hourly_aggregate': Simulates and sums actual hours of month (D * 24, e.g. 720h or 744h).
      3. 'daily_aggregate': Aggregates daily prediction across actual days of month (D days).
    """
    is_valid, error_msg = validate_inputs(base_inputs)
    if not is_valid:
        raise ValueError(error_msg)

    num_days = calendar.monthrange(year, month)[1]
    total_hours = num_days * 24
    month_name = f"{calendar.month_name[month]} {year}"

    feature_cols = [
        'Temperature', 'Humidity', 'SquareFootage', 'Occupancy',
        'RenewableEnergy', 'HVACUsage', 'LightingUsage', 'DayOfWeek', 'Holiday'
    ]
    model = pipeline.named_steps.get('model')
    prep = pipeline.named_steps.get('prep')

    if consumption_basis == "monthly_direct":
        # Direct prediction represents monthly total consumption. Do not multiply again!
        df_input = pd.DataFrame([{
            'Temperature': float(base_inputs['Temperature']),
            'Humidity': float(base_inputs['Humidity']),
            'SquareFootage': float(base_inputs['SquareFootage']),
            'Occupancy': int(base_inputs['Occupancy']),
            'RenewableEnergy': float(base_inputs['RenewableEnergy']),
            'HVACUsage': str(base_inputs['HVACUsage']).capitalize(),
            'LightingUsage': str(base_inputs['LightingUsage']).capitalize(),
            'DayOfWeek': 'Wednesday',
            'Holiday': 'No',
        }])
        total_monthly_kwh = max(0.0, float(pipeline.predict(df_input)[0]))
        daily_avg_kwh = total_monthly_kwh / num_days

        # Uncertainty bounds
        if hasattr(model, 'estimators_') and prep is not None:
            try:
                trans_x = prep.transform(df_input)
                t_preds = [float(t.predict(trans_x)[0]) for t in model.estimators_]
                monthly_lb = max(0.0, float(np.percentile(t_preds, 5)))
                monthly_ub = float(np.percentile(t_preds, 95))
                monthly_std = float(np.std(t_preds))
            except Exception:
                monthly_lb = max(0.0, total_monthly_kwh * 0.95)
                monthly_ub = total_monthly_kwh * 1.05
                monthly_std = (monthly_ub - monthly_lb) / 3.29
        else:
            monthly_lb = max(0.0, total_monthly_kwh * 0.95)
            monthly_ub = total_monthly_kwh * 1.05
            monthly_std = (monthly_ub - monthly_lb) / 3.29

        # Generate month schedule and scale so daily chart displays diurnal variation summing to monthly kWh
        df_month = generate_monthly_schedule(year, month, base_inputs)
        raw_preds = np.maximum(0.0, pipeline.predict(df_month[feature_cols].copy()))
        sum_raw = float(np.sum(raw_preds))
        scale = (total_monthly_kwh / sum_raw) if sum_raw > 0 else (1.0 / total_hours)
        hourly_preds = raw_preds * scale

    elif consumption_basis == "daily_aggregate":
        # Model output represents daily consumption; aggregate across month's actual days
        df_input = pd.DataFrame([{
            'Temperature': float(base_inputs['Temperature']),
            'Humidity': float(base_inputs['Humidity']),
            'SquareFootage': float(base_inputs['SquareFootage']),
            'Occupancy': int(base_inputs['Occupancy']),
            'RenewableEnergy': float(base_inputs['RenewableEnergy']),
            'HVACUsage': str(base_inputs['HVACUsage']).capitalize(),
            'LightingUsage': str(base_inputs['LightingUsage']).capitalize(),
            'DayOfWeek': 'Wednesday',
            'Holiday': 'No',
        }])
        daily_kwh = max(0.0, float(pipeline.predict(df_input)[0]))
        total_monthly_kwh = daily_kwh * num_days
        daily_avg_kwh = daily_kwh

        monthly_lb = max(0.0, total_monthly_kwh * 0.95)
        monthly_ub = total_monthly_kwh * 1.05
        monthly_std = (monthly_ub - monthly_lb) / 3.29

        df_month = generate_monthly_schedule(year, month, base_inputs)
        raw_preds = np.maximum(0.0, pipeline.predict(df_month[feature_cols].copy()))
        sum_raw = float(np.sum(raw_preds))
        scale = (total_monthly_kwh / sum_raw) if sum_raw > 0 else 1.0
        hourly_preds = raw_preds * scale

    else:
        # "hourly_aggregate": continuous hourly simulation across actual hours of month
        df_month = generate_monthly_schedule(year, month, base_inputs)
        df_features = df_month[feature_cols].copy()
        hourly_preds = pipeline.predict(df_features)
        hourly_preds = np.maximum(0.0, hourly_preds)

        total_monthly_kwh = float(np.sum(hourly_preds))
        daily_avg_kwh = total_monthly_kwh / num_days

        if hasattr(model, 'estimators_') and prep is not None:
            try:
                trans_x = prep.transform(df_features)
                tree_monthly_sums = []
                for tree in model.estimators_:
                    t_preds = tree.predict(trans_x)
                    tree_monthly_sums.append(float(np.sum(np.maximum(0.0, t_preds))))
                monthly_lb = max(0.0, float(np.percentile(tree_monthly_sums, 5)))
                monthly_ub = float(np.percentile(tree_monthly_sums, 95))
                monthly_std = float(np.std(tree_monthly_sums))
            except Exception:
                monthly_lb = max(0.0, total_monthly_kwh * 0.95)
                monthly_ub = total_monthly_kwh * 1.05
                monthly_std = (monthly_ub - monthly_lb) / 3.29
        else:
            monthly_lb = max(0.0, total_monthly_kwh * 0.95)
            monthly_ub = total_monthly_kwh * 1.05
            monthly_std = (monthly_ub - monthly_lb) / 3.29

    # Calculate official MSEDCL 2026 Monthly Domestic Electricity Bill
    msedcl_monthly_bill = calculate_msedcl_2026_bill(
        monthly_kwh=total_monthly_kwh,
        connection_type=connection_type,
        billing_period=billing_period,
        sanctioned_load_kw=sanctioned_load_kw,
        fac_rate=fac_rate,
        wheeling_rate=wheeling_rate,
        fixed_charge=fixed_charge_monthly,
        electricity_duty_pct=electricity_duty_pct,
        apply_municipal_charge=apply_municipal_charge,
        municipal_charge_amount=municipal_charge_monthly,
        custom_slabs=custom_slabs
    )

    msedcl_lb_bill = calculate_msedcl_2026_bill(
        monthly_kwh=monthly_lb,
        connection_type=connection_type,
        billing_period=billing_period,
        sanctioned_load_kw=sanctioned_load_kw,
        fac_rate=fac_rate,
        wheeling_rate=wheeling_rate,
        fixed_charge=fixed_charge_monthly,
        electricity_duty_pct=electricity_duty_pct,
        apply_municipal_charge=apply_municipal_charge,
        municipal_charge_amount=municipal_charge_monthly,
        custom_slabs=custom_slabs
    )

    msedcl_ub_bill = calculate_msedcl_2026_bill(
        monthly_kwh=monthly_ub,
        connection_type=connection_type,
        billing_period=billing_period,
        sanctioned_load_kw=sanctioned_load_kw,
        fac_rate=fac_rate,
        wheeling_rate=wheeling_rate,
        fixed_charge=fixed_charge_monthly,
        electricity_duty_pct=electricity_duty_pct,
        apply_municipal_charge=apply_municipal_charge,
        municipal_charge_amount=municipal_charge_monthly,
        custom_slabs=custom_slabs
    )

    # 6. Estimated Daily Cost
    estimated_daily_cost = msedcl_monthly_bill['total_estimated_bill'] / num_days

    # Attach predictions to hourly DataFrame
    df_month['Predicted_kWh'] = np.round(hourly_preds, 2)
    effective_rate = msedcl_monthly_bill['effective_rate_per_kwh']
    df_month['Estimated_Cost_INR'] = np.round(hourly_preds * effective_rate, 2)

    # 7. Aggregate by day to produce daily summary table
    daily_records = []
    for cur_date_str, group in df_month.groupby('Date', sort=False):
        d_kwh = float(group['Predicted_kWh'].sum())
        p_idx = group['Predicted_kWh'].idxmax()
        p_row = group.loc[p_idx]
        daily_records.append({
            'Date': cur_date_str,
            'Day': int(group['Day'].iloc[0]),
            'DayOfWeek': str(group['DayOfWeek'].iloc[0]),
            'Daily_kWh': round(d_kwh, 2),
            'Daily_Cost_INR': round(d_kwh * effective_rate, 2),
            'Peak_Hour': str(p_row['Time']),
            'Peak_kWh': round(float(p_row['Predicted_kWh']), 2),
            'Solar_kWh': round(float(group['RenewableEnergy'].sum()), 2),
            'Avg_Temp': round(float(group['Temperature'].mean()), 1)
        })
    daily_summary_df = pd.DataFrame(daily_records)

    peak_day_idx = daily_summary_df['Daily_kWh'].idxmax()
    peak_day_row = daily_summary_df.loc[peak_day_idx]
    peak_hr_idx = df_month['Predicted_kWh'].idxmax()
    peak_hr_row = df_month.loc[peak_hr_idx]

    # Calculate daily prorated bill for average day for reference
    msedcl_daily_ref = calculate_msedcl_daily_bill(
        daily_kwh=daily_avg_kwh,
        connection_type=connection_type,
        billing_period=billing_period,
        fac_rate=fac_rate,
        wheeling_rate=wheeling_rate,
        fixed_charge_monthly=fixed_charge_monthly,
        electricity_duty_pct=electricity_duty_pct,
        apply_municipal_charge=apply_municipal_charge,
        slab_mode="prorated"
    )

    return {
        'period_type': 'monthly',
        'target_month_name': month_name,
        'year': year,
        'month': month,
        'days_in_month': num_days,
        'total_hours': total_hours,
        # Requirement 7 separate labels:
        'daily_consumption_kwh': round(daily_avg_kwh, 2),
        'monthly_consumption_kwh': round(total_monthly_kwh, 2),
        'estimated_daily_cost': round(estimated_daily_cost, 2),
        'estimated_monthly_bill': round(msedcl_monthly_bill['total_estimated_bill'], 2),
        # Uncertainty bounds:
        'monthly_lb_kwh': round(monthly_lb, 2),
        'monthly_ub_kwh': round(monthly_ub, 2),
        'monthly_std': round(monthly_std, 2),
        'lb_monthly_bill': round(msedcl_lb_bill['total_estimated_bill'], 2),
        'ub_monthly_bill': round(msedcl_ub_bill['total_estimated_bill'], 2),
        'effective_rate_per_kwh': round(effective_rate, 2),
        'msedcl_monthly_bill': msedcl_monthly_bill,
        'msedcl_daily_bill': msedcl_daily_ref,
        'daily_summary_df': daily_summary_df,
        'hourly_df': df_month,
        'peak_day': str(peak_day_row['Date']),
        'peak_day_kwh': round(float(peak_day_row['Daily_kWh']), 2),
        'peak_hour_timestamp': str(peak_hr_row['Timestamp']),
        'peak_hour_kwh': round(float(peak_hr_row['Predicted_kWh']), 2),
        'disclaimer': DISCLAIMER_TEXT,
        'input_data': base_inputs
    }


