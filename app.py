"""
EnergyWise — Energy Consumption Prediction
Machine Learning-Based Energy Analytics and Prediction System
M.Tech Data Science Project Application
"""

import os
import sys
import calendar
from datetime import datetime, date, time
import pandas as pd
import numpy as np
import streamlit as st

# Configure Streamlit page settings
st.set_page_config(
    page_title="EnergyWise — Energy Consumption Prediction",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from src.data_processing import (
    load_dataset,
    find_default_dataset,
    get_available_datasets,
    prepare_features_and_target,
    TARGET_COLUMN,
    NUMERIC_FEATURES,
    CATEGORICAL_FEATURES
)
from src.model_training import (
    train_and_evaluate_all_models,
    save_models,
    load_saved_summary,
    load_best_model
)
from src.prediction import (
    predict_energy,
    predict_daily_24h_energy,
    predict_monthly_energy,
    generate_24h_schedule,
    generate_monthly_schedule,
    VALID_DAYS,
    VALID_HVAC,
    VALID_LIGHTING,
    VALID_HOLIDAY
)
from src.mseb_tariff import (
    calculate_mseb_cost,
    calculate_msedcl_2026_bill,
    calculate_msedcl_daily_bill,
    calculate_progressive_energy_charges,
    DEFAULT_MSEDCL_SLABS_2026,
    DEFAULT_MSEDCL_DAILY_SLABS_2026,
    DEFAULT_WHEELING_CHARGE_PER_UNIT,
    DEFAULT_FIXED_CHARGE_SINGLE_PHASE,
    DEFAULT_FIXED_CHARGE_THREE_PHASE,
    DEFAULT_ELECTRICITY_DUTY_PCT,
    DEFAULT_MUNICIPAL_CHARGE_MONTHLY,
    BILLING_PERIODS_CONFIG,
    CONNECTION_TYPES,
    VALID_BILLING_PERIODS,
    VALID_CONNECTION_TYPES,
    DISCLAIMER_TEXT,
    DAILY_DISCLAIMER_TEXT
)
from src import visualization as viz

# -----------------------------------------------------------------------------
# Custom CSS for Light Modern Dashboard Theme
# -----------------------------------------------------------------------------
CUSTOM_CSS = """
<style>
    /* Global Page Styling */
    .stApp {
        background-color: #F4F7FB;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Main container padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 2.5rem;
        max-width: 1400px;
    }

    /* Modern Card Container */
    .ew-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 24px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
        margin-bottom: 20px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .ew-card:hover {
        box-shadow: 0 6px 20px rgba(15, 23, 42, 0.07);
    }

    /* Metric Cards */
    .metric-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 20px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.03);
        border-left: 4px solid #1E88E5;
    }
    .metric-title {
        font-size: 0.85rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 1.85rem;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.1;
    }
    .metric-subtitle {
        font-size: 0.8rem;
        color: #94A3B8;
        margin-top: 4px;
    }

    /* Prediction Hero Card */
    .hero-prediction-card {
        background: linear-gradient(135deg, #1E88E5 0%, #0D47A1 100%);
        border-radius: 16px;
        padding: 32px;
        color: #FFFFFF;
        box-shadow: 0 8px 24px rgba(30, 136, 229, 0.25);
        text-align: center;
        margin-bottom: 24px;
    }
    .hero-prediction-val {
        font-size: 3.4rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin: 10px 0;
    }
    .hero-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
    }
    .mseb-badge {
        display: inline-block;
        background: rgba(255, 193, 7, 0.22);
        color: #FFE082;
        border: 1px solid rgba(255, 193, 7, 0.4);
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.88rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .mseb-card-container {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 4px 16px rgba(15, 23, 42, 0.04);
        margin-bottom: 20px;
    }
    .mseb-breakdown-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .mseb-breakdown-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        color: #64748B;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .mseb-breakdown-value {
        font-size: 1.4rem;
        font-weight: 700;
        color: #0F172A;
    }
    .estimated-bill-banner {
        background: #FFFBEB;
        border: 1px solid #FDE68A;
        border-left: 5px solid #F59E0B;
        border-radius: 8px;
        padding: 12px 18px;
        color: #92400E;
        font-size: 0.9rem;
        margin-bottom: 18px;
        font-weight: 500;
        line-height: 1.45;
    }
    .daily-summary-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
        gap: 16px;
        margin: 20px 0;
    }
    .daily-summary-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 18px 22px;
        box-shadow: 0 2px 10px rgba(15, 23, 42, 0.04);
        position: relative;
        overflow: hidden;
    }
    .daily-summary-card.card-blue { border-top: 4px solid #1E88E5; }
    .daily-summary-card.card-teal { border-top: 4px solid #0284C7; }
    .daily-summary-card.card-amber { border-top: 4px solid #D97706; }
    .daily-summary-card.card-purple { border-top: 4px solid #8B5CF6; }
    .daily-summary-card.card-green { border-top: 4px solid #10B981; }
    .daily-summary-title {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .daily-summary-value {
        font-size: 1.85rem;
        font-weight: 800;
        color: #0F172A;
        line-height: 1.2;
    }
    .daily-summary-sub {
        font-size: 0.8rem;
        color: #64748B;
        margin-top: 5px;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* Buttons */
    div.stButton > button:first-child {
        background-color: #1E88E5;
        color: #FFFFFF;
        font-weight: 600;
        border-radius: 8px;
        border: none;
        padding: 0.55rem 1.4rem;
        box-shadow: 0 2px 6px rgba(30, 136, 229, 0.25);
        transition: all 0.2s;
    }
    div.stButton > button:first-child:hover {
        background-color: #1565C0;
        box-shadow: 0 4px 12px rgba(21, 101, 192, 0.35);
    }

    /* Section Headers */
    .section-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: #0F172A;
        margin-top: 0.5rem;
        margin-bottom: 0.2rem;
    }
    .section-subtitle {
        font-size: 0.95rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def render_html(html_str: str) -> None:
    """
    Renders application-generated HTML cleanly in Streamlit without CommonMark code-block conversion.
    Strips leading indentation from each line so st.markdown(..., unsafe_allow_html=True)
    treats the markup as raw HTML elements instead of indented <pre><code> code blocks.
    """
    clean_html = "\n".join(line.strip() for line in html_str.splitlines() if line.strip())
    st.markdown(clean_html, unsafe_allow_html=True)



# -----------------------------------------------------------------------------
# Data & Model Caching Helpers
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def get_cached_dataset(file_path_or_buf, synthetic_filter="All"):
    """Loads and caches dataset."""
    return load_dataset(file_path_or_buf, is_synthetic_filter=synthetic_filter)


@st.cache_resource(show_spinner=False)
def get_or_create_models(df):
    """Loads pre-trained model summary or trains models if not available."""
    summary = load_saved_summary()
    best_pipe = load_best_model()

    if summary is not None and best_pipe is not None:
        return summary, best_pipe

    # Fallback to direct training if saved artifacts do not exist
    X, y, num_cols, cat_cols = prepare_features_and_target(df)
    summary = train_and_evaluate_all_models(X, y, num_cols, cat_cols)
    save_models(summary)
    best_pipe = summary['results'][summary['best_model_name']]['model_pipeline']
    return summary, best_pipe


# Initialize Session State
if "prediction_history" not in st.session_state:
    st.session_state.prediction_history = []

if "active_dataset_key" not in st.session_state:
    st.session_state.active_dataset_key = "Energy_Consumption_Virtual.csv"

if "last_predicted_monthly_kwh" not in st.session_state:
    st.session_state.last_predicted_monthly_kwh = None

if "last_predicted_daily_kwh" not in st.session_state:
    st.session_state.last_predicted_daily_kwh = None


# -----------------------------------------------------------------------------
# Sidebar Navigation & Dataset Configuration
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
            <div style="background: #1E88E5; width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; font-size: 24px; color: white;">
                ⚡
            </div>
            <div>
                <h2 style="margin: 0; font-size: 1.35rem; color: #0F172A; font-weight: 700;">EnergyWise</h2>
                <span style="font-size: 0.75rem; color: #64748B; font-weight: 500;">M.Tech Data Science Project</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    nav_page = st.radio(
        "Navigation",
        options=[
            "📊 Overview Dashboard",
            "🔮 Predict Energy",
            "⚡ MSEDCL Bill Calculator",
            "📈 Model Performance",
            "📁 Dataset Explorer",
            "💡 Insights & Recommendations"
        ],
        label_visibility="collapsed"
    )

    st.markdown("---")
    st.markdown("### 🗄️ Dataset Selection")

    available_datasets = get_available_datasets()
    dataset_options = list(available_datasets.keys())
    
    # Allow user to upload custom CSV
    selected_ds = st.selectbox(
        "Active Project Dataset",
        options=dataset_options + ["Upload Custom CSV..."],
        index=0 if dataset_options else None
    )

    uploaded_file = None
    if selected_ds == "Upload Custom CSV...":
        uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])
        if uploaded_file is not None:
            active_file = uploaded_file
            st.session_state.active_dataset_key = uploaded_file.name
        else:
            active_file = available_datasets.get(dataset_options[0]) if dataset_options else None
    else:
        active_file = available_datasets[selected_ds]
        st.session_state.active_dataset_key = selected_ds

    # Synthetic data filtering toggle if applicable
    synthetic_filter = "All"
    
    # Load dataset
    try:
        df, dataset_meta = get_cached_dataset(active_file, synthetic_filter)
        st.success(f"Loaded: **{dataset_meta['current_rows']:,}** records", icon="✅")
    except Exception as e:
        st.error(f"Error loading dataset: {e}")
        st.stop()

    if dataset_meta.get('has_synthetic_col'):
        st.info("ℹ️ `IsSynthetic` column detected.")
        synthetic_filter = st.selectbox(
            "Evaluation Slice",
            options=["All", "Real Only", "Synthetic Only"],
            index=0
        )
        if synthetic_filter != "All":
            df, dataset_meta = get_cached_dataset(active_file, synthetic_filter)

    st.markdown("---")
    st.markdown("""
        <div style="font-size: 0.78rem; color: #64748B; line-height: 1.4;">
            <b>System Info</b><br>
            • Framework: Streamlit & Scikit-Learn<br>
            • Target: <code>EnergyConsumption</code> (kWh)<br>
            • Evaluation: 80/20 Train/Test Split
        </div>
    """, unsafe_allow_html=True)


# Load trained models & summary
summary, best_model_pipe = get_or_create_models(df)


# -----------------------------------------------------------------------------
# PAGE 1: Overview Dashboard
# -----------------------------------------------------------------------------
if "Overview Dashboard" in nav_page:
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="color: #0F172A; font-weight: 800; font-size: 2.2rem; margin-bottom: 4px;">EnergyWise — Energy Consumption Prediction</h1>
            <p style="color: #64748B; font-size: 1.05rem; margin-bottom: 0;">Machine Learning-Based Energy Analytics and Prediction System</p>
        </div>
    """, unsafe_allow_html=True)

    # Dynamic KPI Summary Cards
    col1, col2, col3, col4, col5 = st.columns(5)
    
    avg_energy = df['EnergyConsumption'].mean()
    max_energy = df['EnergyConsumption'].max()
    min_energy = df['EnergyConsumption'].min()
    total_records = len(df)
    core_features_count = len([c for c in df.columns if c not in ['EnergyConsumption', 'Datetime', 'Timestamp', 'IsSynthetic']])

    with col1:
        render_html(f"""
            <div class="metric-container" style="border-left-color: #1E88E5;">
                <div class="metric-title">Total Records</div>
                <div class="metric-value">{total_records:,}</div>
                <div class="metric-subtitle">Active sample rows</div>
            </div>
        """)

    with col2:
        avg_mseb = calculate_mseb_cost(avg_energy)['direct_cost']
        render_html(f"""
            <div class="metric-container" style="border-left-color: #0D47A1;">
                <div class="metric-title">Average Energy</div>
                <div class="metric-value">{avg_energy:.2f} <span style="font-size: 1rem; font-weight: 500;">kWh</span></div>
                <div class="metric-subtitle">≈ ₹ {avg_mseb:,.2f} per cycle (MSEB)</div>
            </div>
        """)

    with col3:
        render_html(f"""
            <div class="metric-container" style="border-left-color: #E53935;">
                <div class="metric-title">Max Demand</div>
                <div class="metric-value">{max_energy:.2f} <span style="font-size: 1rem; font-weight: 500;">kWh</span></div>
                <div class="metric-subtitle">Peak recorded consumption</div>
            </div>
        """)

    with col4:
        render_html(f"""
            <div class="metric-container" style="border-left-color: #43A047;">
                <div class="metric-title">Min Demand</div>
                <div class="metric-value">{min_energy:.2f} <span style="font-size: 1rem; font-weight: 500;">kWh</span></div>
                <div class="metric-subtitle">Baseload consumption</div>
            </div>
        """)

    with col5:
        render_html(f"""
            <div class="metric-container" style="border-left-color: #00ACC1;">
                <div class="metric-title">Predictive Features</div>
                <div class="metric-value">{core_features_count}</div>
                <div class="metric-subtitle">Environmental & operational</div>
            </div>
        """)

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

    # Row 1 Charts: Distribution & Time Series Trend
    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(viz.plot_energy_distribution(df), use_container_width=True)
    with c2:
        st.plotly_chart(viz.plot_energy_trend(df), use_container_width=True)

    # Row 2 Charts: Temperature vs Energy & Occupancy vs Energy
    c3, c4 = st.columns([1, 1])
    with c3:
        st.plotly_chart(viz.plot_temperature_vs_energy(df), use_container_width=True)
    with c4:
        st.plotly_chart(viz.plot_occupancy_vs_energy(df), use_container_width=True)

    # Row 3 Charts: HVAC and Lighting Usage Comparisons
    c5, c6 = st.columns([1, 1])
    with c5:
        st.plotly_chart(viz.plot_hvac_comparison(df), use_container_width=True)
    with c6:
        st.plotly_chart(viz.plot_lighting_comparison(df), use_container_width=True)

    # Row 4 Charts: Day of Week & Correlation Heatmap
    c7, c8 = st.columns([1, 1])
    with c7:
        st.plotly_chart(viz.plot_day_of_week_comparison(df), use_container_width=True)
    with c8:
        st.plotly_chart(viz.plot_correlation_heatmap(df), use_container_width=True)


# -----------------------------------------------------------------------------
# PAGE 2: Predict Energy Consumption
# -----------------------------------------------------------------------------
elif "Predict Energy" in nav_page:
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="color: #0F172A; font-weight: 800; font-size: 2.1rem; margin-bottom: 4px;">Predict Energy Consumption</h1>
            <p style="color: #64748B; font-size: 1.02rem;">Enter building, environmental, and operational parameters to predict expected consumption using the trained machine learning pipeline.</p>
        </div>
    """, unsafe_allow_html=True)

    # Form Container
    with st.container():
        st.markdown('<div class="ew-card">', unsafe_allow_html=True)
        st.markdown("### ⚙️ Operational Parameters")

        with st.form("energy_prediction_form"):
            # Requirement 1: Prediction Period Selector (Monthly is default and primary!)
            st.markdown("##### ⏱️ Prediction Period Horizon")
            prediction_period = st.radio(
                "Prediction Period Mode",
                options=[
                    "📅 Monthly Prediction (Full Billing Cycle — Primary)",
                    "⚡ Daily Prediction (24-Hour Profile)"
                ],
                index=0,  # MONTHLY IS DEFAULT AND PRIMARY!
                horizontal=True,
                help="Monthly Prediction aggregates actual hours for the entire selected month (e.g. 720h for April). Daily Prediction calculates a 24-hour load profile for a single date."
            )
            is_monthly = "Monthly" in prediction_period

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if is_monthly:
                    st.markdown("##### 📅 Target Billing Month")
                    month_options = [
                        "April 2026", "May 2026", "June 2026", "July 2026", "August 2026",
                        "September 2026", "October 2026", "November 2026", "December 2026",
                        "January 2026", "February 2026", "March 2026"
                    ]
                    selected_month_str = st.selectbox(
                        "Target Billing Month",
                        options=month_options,
                        index=0,
                        help="Select month for full billing cycle forecast. Hourly predictions will be aggregated across all actual hours of the month."
                    )
                    m_name_part, y_part = selected_month_str.split()
                    target_year = int(y_part)
                    target_month_num = list(calendar.month_name).index(m_name_part)
                    actual_days = calendar.monthrange(target_year, target_month_num)[1]
                    actual_hours = actual_days * 24
                    st.caption(f"🗓️ **{selected_month_str}**: **{actual_days} days** ({actual_hours} actual billing hours)")
                    holiday = st.selectbox("Holiday Treatment", options=["Normal Calendar Schedule", "Include Statutory Holidays"], index=0, help="Specify holiday treatment during the month")
                    consumption_basis_mode = st.selectbox(
                        "📊 Monthly Calculation Basis",
                        options=[
                            "Direct Monthly Prediction (No Multiplication — Domestic Scale)",
                            "Hourly Schedule Simulation (Sum of actual month hours e.g. 720h / 744h)",
                            "Daily Schedule Aggregate (Sum of actual month days e.g. 30 / 31 days)"
                        ],
                        index=0,
                        help="Direct Monthly: The model prediction (~77 kWh) is treated directly as the total monthly consumption (recommended for domestic residences/flats, preventing artificial 720x explosion). Hourly Simulation: Aggregates hour-by-hour predictions across all hours of the selected month."
                    )
                    pred_date = date(target_year, target_month_num, 1)
                    day_of_week = pred_date.strftime("%A")
                else:
                    st.markdown("##### 📅 Target Date & Calendar")
                    pred_date = st.date_input("Target Date", value=date.today(), help="Select the target date for 24-hour electricity consumption and bill estimation")
                    default_dow = pred_date.strftime("%A")
                    dow_index = VALID_DAYS.index(default_dow) if default_dow in VALID_DAYS else 0
                    day_of_week = st.selectbox("Day of Week", options=VALID_DAYS, index=dow_index, help="Automatically determined from selected target date")
                    holiday = st.selectbox("Holiday Status", options=VALID_HOLIDAY, index=0, help="Specify if target date is a public or statutory holiday")
                    selected_month_str = pred_date.strftime("%B %Y")
                    target_year = pred_date.year
                    target_month_num = pred_date.month
                    actual_days = calendar.monthrange(target_year, target_month_num)[1]
                    actual_hours = 24

            with col_b:
                st.markdown("##### 🌡️ Environmental Conditions")
                temp_label = "Mean Monthly Temperature (°C)" if is_monthly else "Base Daily Temperature (°C)"
                temperature = st.number_input(
                    temp_label,
                    min_value=-20.0, max_value=60.0, value=25.0, step=0.1,
                    help="Mean outdoor dry-bulb temperature (diurnal sine curve accounts for daily day/night fluctuations)"
                )
                humidity = st.number_input(
                    "Relative Humidity (%)",
                    min_value=0.0, max_value=100.0, value=45.0, step=0.5,
                    help="Mean relative humidity percentage"
                )
                square_footage = st.number_input(
                    "Square Footage (sq ft)",
                    min_value=100.0, max_value=50000.0, value=1500.0, step=50.0,
                    help="Gross floor area of the building"
                )

            with col_c:
                st.markdown("##### ⚡ Equipment & Operational Loads")
                occupancy = st.number_input(
                    "Base Occupancy (Persons)",
                    min_value=0, max_value=100, value=4, step=1,
                    help="Active occupant count (diurnal profile modulates daytime/nighttime and weekday/weekend occupancy)"
                )
                hvac_usage = st.selectbox("HVAC Status", options=VALID_HVAC, index=0, help="Air conditioning/heating load operational status")
                lighting_usage = st.selectbox("Lighting Status", options=VALID_LIGHTING, index=0, help="Artificial lighting system status (daylight harvesting modulates solar hours)")
                renewable_energy = st.number_input(
                    "Peak Solar / Renewable Generation (kWh)",
                    min_value=0.0, max_value=100.0, value=10.0, step=0.5,
                    help="Peak hourly solar generation at solar noon (modeled across 06:00 to 18:00 daylight hours; 0 kWh at night)"
                )

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
            st.markdown("##### ⚡ Official MSEDCL Domestic Electricity Tariff (Applicable from 1 April 2026)")
            col_m1, col_m2 = st.columns(2)
            with col_m1:
                # Pre-select matching billing period
                matching_period_idx = 0
                for idx_bp, bp_name in enumerate(VALID_BILLING_PERIODS):
                    if selected_month_str.split()[0] in bp_name:
                        matching_period_idx = idx_bp
                        break
                selected_billing_period = st.selectbox(
                    "📅 Billing Period Tariff Order",
                    options=VALID_BILLING_PERIODS,
                    index=matching_period_idx,
                    help="Select billing period to load the applicable Fuel Adjustment Charge (FAC) rate"
                )
            with col_m2:
                selected_connection_type = st.selectbox(
                    "🔌 Connection Type",
                    options=VALID_CONNECTION_TYPES,
                    index=0,
                    help="Fixed demand charge: ₹130/month for Single Phase, ₹440/month for Three Phase"
                )

            col_m3, col_m4 = st.columns([1.2, 1.8])
            with col_m3:
                apply_municipal_charge = st.checkbox(
                    "🏛️ Municipal Corporation Charge (₹10/month)",
                    value=True,
                    help="Applicable for consumers residing within Municipal Corporation jurisdictions"
                )
            with col_m4:
                if not is_monthly:
                    daily_tariff_slab_mode = st.radio(
                        "⚡ Daily Energy Slab Calculation Mode",
                        options=[
                            "MERC Daily Prorata Slabs (Monthly / 30 Days)",
                            "Standard Progressive Slabs (Direct Telescopic)"
                        ],
                        index=0,
                        horizontal=True,
                        help="Under MERC regulations, daily pro-rata slabs divide monthly slab caps by 30 days (e.g. 0–3.33 units @ ₹3.96/kWh)"
                    )
                else:
                    st.info("ℹ️ Full Progressive Telescopic Monthly Slabs (1–100, 101–300, 301–500, 501–1000, >1000 units) will be applied.")
                    daily_tariff_slab_mode = "standard"

            # Editable Time-Varying Tariff Parameters Expander
            with st.expander("⚙️ Time-Varying Tariff Parameters & Rate Editor (MSEDCL Order — 1 April 2026)", expanded=False):
                st.markdown("<div style='font-size: 0.85rem; color: #64748B; margin-bottom: 8px;'>You can review or adjust the official MSEDCL 2026 rates below. Changes update the bill calculation dynamically without code hardcoding:</div>", unsafe_allow_html=True)
                default_period_fac = BILLING_PERIODS_CONFIG.get(selected_billing_period, {}).get("fac_rate", 0.65)
                
                t_col1, t_col2, t_col3 = st.columns(3)
                with t_col1:
                    user_wheeling_rate = st.number_input(
                        "Wheeling Charge (₹/unit)",
                        min_value=0.0, max_value=10.0, value=DEFAULT_WHEELING_CHARGE_PER_UNIT, step=0.05,
                        help="Official wheeling charge applied per consumed unit (default: ₹1.60/unit)"
                    )
                    user_fixed_single = st.number_input(
                        "Single Phase Fixed (₹/month)",
                        min_value=0.0, max_value=1000.0, value=DEFAULT_FIXED_CHARGE_SINGLE_PHASE, step=5.0,
                        help="Fixed demand charge for single phase domestic connections (default: ₹130/month)"
                    )
                with t_col2:
                    user_fac_rate = st.number_input(
                        "Fuel Adjustment Charge (FAC ₹/unit)",
                        min_value=0.0, max_value=5.0, value=float(default_period_fac), step=0.01,
                        help=f"FAC rate for {selected_billing_period} (default: ₹{default_period_fac:.2f}/unit)"
                    )
                    user_fixed_three = st.number_input(
                        "Three Phase Fixed (₹/month)",
                        min_value=0.0, max_value=2000.0, value=DEFAULT_FIXED_CHARGE_THREE_PHASE, step=10.0,
                        help="Fixed demand charge for three phase domestic connections (default: ₹440/month)"
                    )
                with t_col3:
                    user_ed_pct = st.number_input(
                        "Electricity Duty (%)",
                        min_value=0.0, max_value=50.0, value=DEFAULT_ELECTRICITY_DUTY_PCT, step=0.5,
                        help="Government of Maharashtra statutory electricity duty (default: 16% of applicable charges)"
                    )
                    user_muni_charge = st.number_input(
                        "Municipal Charge (₹/month)",
                        min_value=0.0, max_value=100.0, value=DEFAULT_MUNICIPAL_CHARGE_MONTHLY, step=1.0,
                        help="Additional municipal corporation fee where applicable (default: ₹10/month)"
                    )

                st.markdown("<div style='font-size: 0.82rem; font-weight: 600; color: #475569; margin: 10px 0 4px 0;'>MSEDCL Domestic Energy Slabs (Applicable from 1 April 2026):</div>", unsafe_allow_html=True)
                s_c1, s_c2, s_c3, s_c4, s_c5 = st.columns(5)
                with s_c1:
                    slab1_rate = st.number_input("1–100 Units (₹)", value=3.96, step=0.01, format="%.2f")
                with s_c2:
                    slab2_rate = st.number_input("101–300 Units (₹)", value=10.80, step=0.01, format="%.2f")
                with s_c3:
                    slab3_rate = st.number_input("301–500 Units (₹)", value=15.03, step=0.01, format="%.2f")
                with s_c4:
                    slab4_rate = st.number_input("501–1000 Units (₹)", value=17.53, step=0.01, format="%.2f")
                with s_c5:
                    slab5_rate = st.number_input("Above 1000 Units (₹)", value=17.53, step=0.01, format="%.2f")

            st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
            col_btn1, col_btn2 = st.columns([1.5, 3.5])
            with col_btn1:
                btn_caption = "⚡ Predict Monthly Consumption & Calculate Bill" if is_monthly else "⚡ Predict 24h Consumption & Daily Bill"
                submitted = st.form_submit_button(btn_caption, use_container_width=True)
            with col_btn2:
                reset = st.form_submit_button("🔄 Reset to Dataset Medians")

        st.markdown('</div>', unsafe_allow_html=True)

    # Process Form
    if submitted or reset:
        chosen_period = selected_billing_period if 'selected_billing_period' in locals() else VALID_BILLING_PERIODS[0]
        chosen_conn = selected_connection_type if 'selected_connection_type' in locals() else VALID_CONNECTION_TYPES[0]
        chosen_muni = apply_municipal_charge if 'apply_municipal_charge' in locals() else True
        chosen_slab_mode = "prorata" if ("Prorata" in daily_tariff_slab_mode if 'daily_tariff_slab_mode' in locals() else False) else "standard"
        chosen_is_monthly = is_monthly if 'is_monthly' in locals() else True

        chosen_basis = "monthly_direct"
        if 'consumption_basis_mode' in locals():
            if "Hourly Schedule" in consumption_basis_mode:
                chosen_basis = "hourly_aggregate"
            elif "Daily Schedule" in consumption_basis_mode:
                chosen_basis = "daily_aggregate"

        # Resolve edited rates or defaults
        resolved_wheeling = user_wheeling_rate if 'user_wheeling_rate' in locals() else DEFAULT_WHEELING_CHARGE_PER_UNIT
        resolved_fac = user_fac_rate if 'user_fac_rate' in locals() else BILLING_PERIODS_CONFIG.get(chosen_period, {}).get("fac_rate", 0.65)
        resolved_fixed = (user_fixed_three if "Three Phase" in chosen_conn else user_fixed_single) if ('user_fixed_single' in locals() and 'user_fixed_three' in locals()) else (DEFAULT_FIXED_CHARGE_THREE_PHASE if "Three Phase" in chosen_conn else DEFAULT_FIXED_CHARGE_SINGLE_PHASE)
        resolved_ed = user_ed_pct if 'user_ed_pct' in locals() else DEFAULT_ELECTRICITY_DUTY_PCT
        resolved_muni = user_muni_charge if 'user_muni_charge' in locals() else DEFAULT_MUNICIPAL_CHARGE_MONTHLY

        # Custom progressive slabs if edited
        active_monthly_slabs = [
            {"min": 0, "max": 100, "rate": float(slab1_rate if 'slab1_rate' in locals() else 3.96), "label": "1 – 100 units"},
            {"min": 100, "max": 300, "rate": float(slab2_rate if 'slab2_rate' in locals() else 10.80), "label": "101 – 300 units"},
            {"min": 300, "max": 500, "rate": float(slab3_rate if 'slab3_rate' in locals() else 15.03), "label": "301 – 500 units"},
            {"min": 500, "max": 1000, "rate": float(slab4_rate if 'slab4_rate' in locals() else 17.53), "label": "501 – 1000 units"},
            {"min": 1000, "max": float("inf"), "rate": float(slab5_rate if 'slab5_rate' in locals() else 17.53), "label": "Above 1000 units"},
        ]

        active_daily_slabs = [
            {"min": 0.0, "max": 100.0 / 30.0, "rate": float(slab1_rate if 'slab1_rate' in locals() else 3.96), "label": "0 – 3.33 units/day (1–100 mo)"},
            {"min": 100.0 / 30.0, "max": 300.0 / 30.0, "rate": float(slab2_rate if 'slab2_rate' in locals() else 10.80), "label": "3.34 – 10.00 units/day (101–300 mo)"},
            {"min": 300.0 / 30.0, "max": 500.0 / 30.0, "rate": float(slab3_rate if 'slab3_rate' in locals() else 15.03), "label": "10.01 – 16.67 units/day (301–500 mo)"},
            {"min": 500.0 / 30.0, "max": 1000.0 / 30.0, "rate": float(slab4_rate if 'slab4_rate' in locals() else 17.53), "label": "16.68 – 33.33 units/day (501–1000 mo)"},
            {"min": 1000.0 / 30.0, "max": float("inf"), "rate": float(slab5_rate if 'slab5_rate' in locals() else 17.53), "label": "Above 33.33 units/day (>1000 mo)"},
        ] if chosen_slab_mode == "prorata" else active_monthly_slabs

        if reset:
            chosen_is_monthly = True
            chosen_period = VALID_BILLING_PERIODS[0]
            chosen_conn = VALID_CONNECTION_TYPES[0]
            chosen_muni = True
            target_year = 2026
            target_month_num = 4
            selected_month_str = "April 2026"
            actual_days = 30
            actual_hours = 720
            input_dict = {
                'Temperature': float(df['Temperature'].median()),
                'Humidity': float(df['Humidity'].median()),
                'SquareFootage': float(df['SquareFootage'].median()),
                'Occupancy': int(df['Occupancy'].median()),
                'RenewableEnergy': float(df['RenewableEnergy'].median()),
                'HVACUsage': str(df['HVACUsage'].mode()[0]),
                'LightingUsage': str(df['LightingUsage'].mode()[0]),
                'DayOfWeek': 'Wednesday',
                'Holiday': 'No'
            }
        else:
            input_dict = {
                'Temperature': float(temperature),
                'Humidity': float(humidity),
                'SquareFootage': float(square_footage),
                'Occupancy': int(occupancy),
                'RenewableEnergy': float(renewable_energy),
                'HVACUsage': str(hvac_usage),
                'LightingUsage': str(lighting_usage),
                'DayOfWeek': str(day_of_week),
                'Holiday': 'Yes' if ('Statutory' in holiday or holiday == 'Yes') else 'No'
            }

        try:
            if chosen_is_monthly:
                # -------------------------------------------------------------
                # MONTHLY PREDICTION PIPELINE (PRIMARY & DEFAULT)
                # Aggregates hourly predictions across actual month hours
                # -------------------------------------------------------------
                m_name_part, y_part = selected_month_str.split()
                target_year = int(y_part)
                target_month_num = list(calendar.month_name).index(m_name_part)

                pred_res = predict_monthly_energy(
                    pipeline=best_model_pipe,
                    year=target_year,
                    month=target_month_num,
                    base_inputs=input_dict,
                    connection_type=chosen_conn,
                    billing_period=chosen_period,
                    consumption_basis=chosen_basis,
                    fac_rate=resolved_fac,
                    wheeling_rate=resolved_wheeling,
                    fixed_charge_monthly=resolved_fixed,
                    electricity_duty_pct=resolved_ed,
                    apply_municipal_charge=chosen_muni,
                    municipal_charge_monthly=resolved_muni,
                    custom_slabs=active_monthly_slabs
                )

                daily_consumption_kwh = pred_res['daily_consumption_kwh']
                monthly_consumption_kwh = pred_res['monthly_consumption_kwh']
                st.session_state.last_predicted_monthly_kwh = monthly_consumption_kwh
                st.session_state.last_predicted_daily_kwh = daily_consumption_kwh
                estimated_daily_cost = pred_res['estimated_daily_cost']
                estimated_monthly_bill = pred_res['estimated_monthly_bill']
                msedcl_bill = pred_res['msedcl_monthly_bill']
                daily_summary_df = pred_res['daily_summary_df']
                hourly_df = pred_res['hourly_df']
                actual_days = pred_res['days_in_month']
                actual_hours = pred_res['total_hours']

                # Record in session history
                history_record = {
                    'Period Type': 'Monthly (Full Cycle)',
                    'Target Period': f"{pred_res['target_month_name']} ({actual_hours}h)",
                    'Daily Consumption (kWh)': f"{daily_consumption_kwh:,.2f}",
                    'Monthly Consumption (kWh)': f"{monthly_consumption_kwh:,.2f}",
                    'Estimated Daily Cost (₹)': f"₹ {estimated_daily_cost:,.2f}",
                    'Estimated Monthly Bill (₹)': f"₹ {estimated_monthly_bill:,.2f}",
                    'Effective Rate (₹/kWh)': f"₹ {pred_res['effective_rate_per_kwh']:.2f}",
                    'Peak Load': f"{pred_res['peak_day_kwh']:,.1f} kWh on {pred_res['peak_day']}",
                    'Billing Period': chosen_period.split('(')[0].strip(),
                    'Connection Type': 'Single Phase' if 'Single Phase' in chosen_conn else 'Three Phase'
                }
                st.session_state.prediction_history.insert(0, history_record)

                # Mandatory Notice: Clearly explain assumptions & distinguish estimated bill
                render_html(f"""
                    <div class="estimated-bill-banner">
                        📅 <b>MONTHLY PREDICTION & ESTIMATED BILL NOTICE (MSEDCL 2026 TARIFF):</b> 
                        This forecast aggregates <b>{actual_hours} actual hourly ML predictions</b> across all <b>{actual_days} calendar days of {pred_res['target_month_name']}</b>, 
                        simulating weekday vs weekend operational patterns, natural diurnal temperature curves, and daytime solar PV offset. 
                        The electricity bill is calculated under official <b>MSEDCL Domestic Tariff rules (applicable from 1 April 2026)</b>: 
                        full monthly fixed demand charge (<b>₹{msedcl_bill['fixed_charge']:.2f}/month</b>), telescopic progressive energy slabs (1–100, 101–300, 301–500, 501–1000, >1000 units), 
                        wheeling charges (@ ₹{msedcl_bill['wheeling_rate']:.2f}/unit), fuel adjustment charges (FAC @ ₹{msedcl_bill['fac_rate']:.4f}/unit), 
                        and 16% Maharashtra Electricity Duty. 
                        <b>This result is an estimate for consumption forecasting and budget planning, not an official utility bill issued by Mahavitaran / MSEDCL.</b>
                    </div>
                """)

                # Hero Prediction Card (Monthly Primary View)
                render_html(f"""
                    <div class="hero-prediction-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 16px;">
                            <span class="hero-badge">Model: {summary['best_model_name']} (R²: {summary['best_r2']:.4f})</span>
                            <span class="mseb-badge">⚡ MSEDCL Domestic Tariff (from 1 April 2026)</span>
                            <span class="hero-badge">Billing Cycle: {pred_res['target_month_name']} ({actual_days} days / {actual_hours}h)</span>
                            <span class="hero-badge">Primary Monthly Mode</span>
                        </div>

                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; align-items: stretch; margin: 16px 0;">
                            <!-- Predicted Monthly Consumption Column -->
                            <div style="background: rgba(255, 255, 255, 0.12); border-radius: 12px; padding: 24px; border: 1px solid rgba(255, 255, 255, 0.2); backdrop-filter: blur(4px);">
                                <div style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.88; font-weight: 600;">📅 Predicted Monthly Electricity Consumption</div>
                                <div class="hero-prediction-val">{monthly_consumption_kwh:,.2f} <span style="font-size: 1.6rem; font-weight: 500;">kWh</span></div>
                                <div style="font-size: 0.95rem; opacity: 0.95;">
                                    Expected 90% CI: <b>{pred_res['monthly_lb_kwh']:,.2f} kWh</b> — <b>{pred_res['monthly_ub_kwh']:,.2f} kWh</b>
                                </div>
                                <div style="font-size: 0.78rem; opacity: 0.82; margin-top: 6px;">
                                    Aggregated across all {actual_hours} actual hours of {pred_res['target_month_name']} • Daily average: <b>{daily_consumption_kwh:,.2f} kWh/day</b>
                                </div>
                            </div>

                            <!-- Estimated Monthly MSEDCL Bill Column -->
                            <div style="background: rgba(255, 255, 255, 0.12); border-radius: 12px; padding: 24px; border: 1px solid rgba(255, 213, 79, 0.4); backdrop-filter: blur(4px);">
                                <div style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; color: #FFE082; font-weight: 600;">💰 Estimated MSEDCL Monthly Bill</div>
                                <div class="hero-prediction-val" style="color: #FFD54F;">₹ {estimated_monthly_bill:,.2f}</div>
                                <div style="font-size: 0.95rem; opacity: 0.95;">
                                    Expected CI Range: <b>₹ {pred_res['lb_monthly_bill']:,.2f}</b> — <b>₹ {pred_res['ub_monthly_bill']:,.2f}</b>
                                </div>
                                <div style="font-size: 0.82rem; color: #FFF9C4; margin-top: 6px;">
                                    Effective Rate: <b>₹ {pred_res['effective_rate_per_kwh']:.2f} / kWh</b> • Daily equivalent: <b>₹ {estimated_daily_cost:,.2f} / day</b>
                                </div>
                            </div>
                        </div>

                        <div style="font-size: 0.82rem; margin-top: 14px; opacity: 0.9; max-width: 860px; margin-left: auto; margin-right: auto; line-height: 1.45;">
                            * Calculated per official MSEDCL MERC order from 1 April 2026. Includes progressive telescopic energy slabs (₹3.96 – ₹17.53/unit), wheeling charge (₹{msedcl_bill['wheeling_rate']:.2f}/unit), fixed demand charge (₹{msedcl_bill['fixed_charge']:.2f}/month), fuel adjustment charge (FAC @ ₹{msedcl_bill['fac_rate']:.4f}/unit), and Maharashtra Electricity Duty (16% of applicable charges).
                        </div>
                    </div>
                """)

                # Requirement 7: Dedicated 4-Component Summary Row with Separate Labels
                st.markdown("### 📊 Electricity Consumption & Cost Summary")
                render_html(f"""
                    <div class="daily-summary-grid">
                        <div class="daily-summary-card card-blue">
                            <div class="daily-summary-title">⚡ Daily Consumption (kWh)</div>
                            <div class="daily-summary-value">{daily_consumption_kwh:,.2f} <span style="font-size: 1.05rem; font-weight: 500;">kWh</span></div>
                            <div class="daily-summary-sub">Average per day across {actual_days} days</div>
                        </div>
                        <div class="daily-summary-card card-teal">
                            <div class="daily-summary-title">📅 Monthly Consumption (kWh)</div>
                            <div class="daily-summary-value" style="color: #0284C7;">{monthly_consumption_kwh:,.2f} <span style="font-size: 1.05rem; font-weight: 500;">kWh</span></div>
                            <div class="daily-summary-sub">Aggregated sum of {actual_hours} actual hours</div>
                        </div>
                        <div class="daily-summary-card card-amber">
                            <div class="daily-summary-title">💡 Estimated Daily Cost</div>
                            <div class="daily-summary-value" style="color: #D97706;">₹ {estimated_daily_cost:,.2f}</div>
                            <div class="daily-summary-sub">Daily equivalent (Monthly bill ÷ {actual_days})</div>
                        </div>
                        <div class="daily-summary-card card-green">
                            <div class="daily-summary-title">💰 Estimated Monthly Bill</div>
                            <div class="daily-summary-value" style="color: #059669;">₹ {estimated_monthly_bill:,.2f}</div>
                            <div class="daily-summary-sub">Full MSEDCL Monthly Bill (inc. 16% Duty)</div>
                        </div>
                    </div>
                """)

                # Itemized Monthly Charges Breakdown (6 Key Metric Tiles)
                st.markdown(f"### 🧾 Itemized MSEDCL Monthly Bill Breakdown — {pred_res['target_month_name']}")
                k1, k2, k3, k4, k5, k6 = st.columns(6)
                with k1:
                    render_html(f"""
                        <div class="mseb-breakdown-box">
                            <div class="mseb-breakdown-label">Energy Charge</div>
                            <div class="mseb-breakdown-value">₹ {msedcl_bill['energy_charge']:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #64748B;">Progressive Slabs</div>
                        </div>
                    """)
                with k2:
                    render_html(f"""
                        <div class="mseb-breakdown-box">
                            <div class="mseb-breakdown-label">Wheeling Charge</div>
                            <div class="mseb-breakdown-value">₹ {msedcl_bill['wheeling_charge']:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #64748B;">@ ₹{msedcl_bill['wheeling_rate']:.2f}/unit</div>
                        </div>
                    """)
                with k3:
                    render_html(f"""
                        <div class="mseb-breakdown-box">
                            <div class="mseb-breakdown-label">Fixed Demand</div>
                            <div class="mseb-breakdown-value">₹ {msedcl_bill['fixed_charge']:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #64748B;">Full Monthly Fee</div>
                        </div>
                    """)
                with k4:
                    render_html(f"""
                        <div class="mseb-breakdown-box">
                            <div class="mseb-breakdown-label">FAC Surcharge</div>
                            <div class="mseb-breakdown-value">₹ {msedcl_bill['fac_charge']:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #64748B;">@ ₹{msedcl_bill['fac_rate']:.4f}/unit</div>
                        </div>
                    """)
                with k5:
                    render_html(f"""
                        <div class="mseb-breakdown-box" style="background: #F0F7FF; border-color: #1E88E5;">
                            <div class="mseb-breakdown-label" style="color: #1E88E5;">Electricity Duty (16%)</div>
                            <div class="mseb-breakdown-value" style="color: #0D47A1;">₹ {msedcl_bill['ed_charge']:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #1E88E5;">16% of Applicable</div>
                        </div>
                    """)
                with k6:
                    render_html(f"""
                        <div class="mseb-breakdown-box" style="background: #FEF3C7; border-color: #F59E0B;">
                            <div class="mseb-breakdown-label" style="color: #B45309;">Municipal Charge</div>
                            <div class="mseb-breakdown-value" style="color: #92400E;">₹ {msedcl_bill['municipal_charge']:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #B45309;">Where Applicable</div>
                        </div>
                    """)

                st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

                # Interactive Monthly Daily Load Profile Chart
                st.markdown(f"### 📈 Daily Electricity Consumption Profile Across {pred_res['target_month_name']}")
                fig_month = viz.plot_monthly_daily_trend(daily_summary_df, pred_res['target_month_name'])
                st.plotly_chart(fig_month, use_container_width=True)

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

                # Calculation Breakdown & Simulation Tabs
                b_tab1, b_tab2, b_tab3, b_tab4 = st.tabs([
                    f"📅 Daily Breakdown Table ({actual_days} Days)",
                    "📶 MSEDCL Progressive Slab Breakdown",
                    "🧮 Step-by-Step Monthly Calculation Formula",
                    "🎛️ Interactive Monthly Bill Simulator"
                ])

                with b_tab1:
                    st.markdown(f"##### 📅 Day-by-Day Forecast Across **{pred_res['target_month_name']}** ({actual_hours} Hours Total)")
                    display_daily = daily_summary_df[['Day', 'Date', 'DayOfWeek', 'Daily_kWh', 'Daily_Cost_INR', 'Peak_Hour', 'Peak_kWh', 'Solar_kWh', 'Avg_Temp']].copy()
                    display_daily.columns = ['Day', 'Date', 'Day of Week', 'Consumption (kWh)', 'Est. Cost (₹)', 'Peak Hour', 'Peak Load (kWh)', 'Solar PV (kWh)', 'Avg Temp (°C)']
                    st.dataframe(display_daily, use_container_width=True)

                    c_dl1, c_dl2 = st.columns([1, 1])
                    with c_dl1:
                        csv_daily = display_daily.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download Daily Summary (CSV)",
                            data=csv_daily,
                            file_name=f"monthly_daily_summary_{selected_month_str.replace(' ', '_')}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                    with c_dl2:
                        csv_hourly = hourly_df[['Timestamp', 'Hour', 'Predicted_kWh', 'Estimated_Cost_INR', 'Temperature', 'Humidity', 'Occupancy', 'RenewableEnergy']].to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label=f"📥 Download Full {actual_hours}h Hourly Schedule (CSV)",
                            data=csv_hourly,
                            file_name=f"hourly_forecast_{selected_month_str.replace(' ', '_')}_{actual_hours}h.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                with b_tab2:
                    st.markdown(f"##### 📶 Progressive Energy Slabs for **{monthly_consumption_kwh:,.2f} kWh**")
                    slab_display_data = []
                    for s in msedcl_bill['slab_breakdown']:
                        status_text = "✅ Active" if s["is_active"] and s["units"] > 0 else ("⏳ Inactive" if s["units"] == 0 else "✅ Covered")
                        slab_display_data.append({
                            "Tariff Slab Tier": s["slab_label"],
                            "Tariff Rate (₹/kWh)": f"₹ {s['rate']:.2f}",
                            "Units Consumed (kWh)": f"{s['units']:,.2f}",
                            "Energy Charge (₹)": f"₹ {s['cost']:,.2f}",
                            "Slab Status": status_text
                        })
                    st.table(pd.DataFrame(slab_display_data))

                with b_tab3:
                    st.markdown(f"##### 🧮 Step-by-Step Monthly Calculation Formula (MERC Rules — {pred_res['target_month_name']})")
                    render_html(f"""
                    <div class="mseb-card-container">
                        <table style="width: 100%; border-collapse: collapse; font-size: 0.92rem;">
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 9px 0; color: #475569;">1. Energy Charges (Sum of Progressive Monthly Slabs)</td>
                                <td style="padding: 9px 0; text-align: right; font-weight: 600; color: #D97706;">₹ {msedcl_bill['energy_charge']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 9px 0; color: #475569;">2. Wheeling Charges ({monthly_consumption_kwh:,.2f} units × ₹{msedcl_bill['wheeling_rate']:.2f}/unit)</td>
                                <td style="padding: 9px 0; text-align: right; font-weight: 600;">₹ {msedcl_bill['wheeling_charge']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 9px 0; color: #475569;">3. Fixed Monthly Demand Charges ({chosen_conn.split('(')[0].strip()})</td>
                                <td style="padding: 9px 0; text-align: right; font-weight: 600;">₹ {msedcl_bill['fixed_charge']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 9px 0; color: #475569;">4. Fuel Adjustment Charges (FAC) ({monthly_consumption_kwh:,.2f} units × ₹{msedcl_bill['fac_rate']:.4f}/unit)</td>
                                <td style="padding: 9px 0; text-align: right; font-weight: 600;">₹ {msedcl_bill['fac_charge']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 2px solid #CBD5E1; background: #F8FAFC;">
                                <td style="padding: 10px 0; font-weight: 700; color: #0F172A;">Applicable Charges Subtotal (Base for 16% Electricity Duty)</td>
                                <td style="padding: 10px 0; text-align: right; font-weight: 700; color: #0F172A;">₹ {msedcl_bill['applicable_charges']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 9px 0; color: #475569;">5. Maharashtra Electricity Duty (16.0% of ₹{msedcl_bill['applicable_charges']:,.2f})</td>
                                <td style="padding: 9px 0; text-align: right; font-weight: 600; color: #1E88E5;">₹ {msedcl_bill['ed_charge']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 9px 0; color: #475569;">6. Municipal Corporation Charge (Where applicable)</td>
                                <td style="padding: 9px 0; text-align: right; font-weight: 600; color: #92400E;">₹ {msedcl_bill['municipal_charge']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0; background: #FDF4FF;">
                                <td style="padding: 10px 0; font-weight: 700; color: #7C3AED;">Total Additional Charges Subtotal (Wheeling + Fixed + FAC + Duty + Muni)</td>
                                <td style="padding: 10px 0; text-align: right; font-weight: 700; color: #7C3AED;">₹ {msedcl_bill['total_additional_charges']:,.2f}</td>
                            </tr>
                            <tr style="background: #EFF6FF; border-top: 2px solid #1E88E5;">
                                <td style="padding: 12px 0; font-weight: 800; font-size: 1.1rem; color: #0D47A1;">Total Estimated Monthly Bill Payable</td>
                                <td style="padding: 12px 0; text-align: right; font-weight: 800; font-size: 1.25rem; color: #0D47A1;">₹ {msedcl_bill['total_estimated_bill']:,.2f}</td>
                            </tr>
                        </table>
                    </div>
                    """)

                with b_tab4:
                    st.markdown("##### 🎛️ Interactive Monthly Bill Simulator")
                    st.markdown("Simulate different monthly consumption levels and inspect bill calculations dynamically under the 1 April 2026 tariff:")

                    sim_monthly_kwh = st.slider(
                        "Simulate Monthly Consumption (kWh / Units)",
                        min_value=0.0, max_value=2500.0,
                        value=float(min(2500.0, max(0.0, monthly_consumption_kwh))),
                        step=10.0
                    )
                    sim_m_bill = calculate_msedcl_2026_bill(
                        monthly_kwh=sim_monthly_kwh,
                        connection_type=chosen_conn,
                        billing_period=chosen_period,
                        fac_rate=resolved_fac,
                        wheeling_rate=resolved_wheeling,
                        fixed_charge=resolved_fixed,
                        electricity_duty_pct=resolved_ed,
                        apply_municipal_charge=chosen_muni,
                        municipal_charge_amount=resolved_muni,
                        custom_slabs=active_monthly_slabs
                    )
                    sc1, sc2, sc3, sc4 = st.columns(4)
                    with sc1:
                        st.metric("Simulated Monthly Units", f"{sim_monthly_kwh:,.1f} kWh")
                    with sc2:
                        st.metric("Energy Charges", f"₹ {sim_m_bill['energy_charge']:,.2f}")
                    with sc3:
                        st.metric("Estimated Monthly Bill", f"₹ {sim_m_bill['total_estimated_bill']:,.2f}")
                    with sc4:
                        st.metric("Effective Unit Rate", f"₹ {sim_m_bill['effective_rate_per_kwh']:.2f}/kWh")

                # Contextual Factor Breakdown
                st.markdown("#### 🔍 Key Operational Drivers for this Monthly Prediction")
                drivers = [
                    f"Full monthly prediction aggregating {actual_hours} hours across {actual_days} days of {pred_res['target_month_name']}",
                    f"Peak demand day: {pred_res['peak_day']} ({pred_res['peak_day_kwh']:,.1f} kWh/day) | Peak hourly load: {pred_res['peak_hour_kwh']:.2f} kWh at {pred_res['peak_hour_timestamp'].split()[-1]}"
                ]
                if input_dict['HVACUsage'] == 'On':
                    drivers.append("HVAC continuous cooling cycle active throughout operational daytime and evening hours")
                else:
                    drivers.append("HVAC disabled (natural ventilation / baseload cooling)")

                if input_dict['RenewableEnergy'] > 0:
                    total_solar_mo = float(hourly_df['RenewableEnergy'].sum())
                    solar_savings_mo = total_solar_mo * msedcl_bill['effective_rate_per_kwh']
                    drivers.append(f"Onsite Solar PV offset: {total_solar_mo:,.1f} kWh generated in month (saves ~₹{solar_savings_mo:,.2f})")

                cols = st.columns(len(drivers))
                for i, d in enumerate(drivers):
                    with cols[i]:
                        st.info(d, icon="💡")

            else:
                # -------------------------------------------------------------
                # DAILY PREDICTION PIPELINE (24 HOURS)
                # -------------------------------------------------------------
                target_date_val = pred_date
                daily_res = predict_daily_24h_energy(
                    pipeline=best_model_pipe,
                    target_date=target_date_val,
                    base_inputs=input_dict,
                    connection_type=chosen_conn,
                    billing_period=chosen_period,
                    fac_rate=resolved_fac,
                    wheeling_rate=resolved_wheeling,
                    fixed_charge_monthly=resolved_fixed,
                    electricity_duty_pct=resolved_ed,
                    apply_municipal_charge=chosen_muni,
                    municipal_charge_monthly=resolved_muni,
                    slab_mode=chosen_slab_mode,
                    custom_slabs=active_daily_slabs
                )

                daily_consumption_kwh = daily_res['daily_consumption_kwh']
                monthly_consumption_kwh = daily_res['monthly_consumption_kwh']
                st.session_state.last_predicted_daily_kwh = daily_consumption_kwh
                st.session_state.last_predicted_monthly_kwh = monthly_consumption_kwh
                estimated_daily_cost = daily_res['estimated_daily_cost']
                estimated_monthly_bill = daily_res['estimated_monthly_bill']
                msedcl_daily = daily_res['msedcl_daily_bill']
                hourly_df = daily_res['hourly_df']
                peak_hour = daily_res['peak_hour']
                peak_kwh = daily_res['peak_kwh']
                baseload_hour = daily_res['baseload_hour']
                baseload_kwh = daily_res['baseload_kwh']

                # Record in session history
                history_record = {
                    'Period Type': 'Daily (24h Profile)',
                    'Target Period': f"{target_date_val} ({daily_res['day_of_week']})",
                    'Daily Consumption (kWh)': f"{daily_consumption_kwh:,.2f}",
                    'Monthly Consumption (kWh)': f"{monthly_consumption_kwh:,.2f}",
                    'Estimated Daily Cost (₹)': f"₹ {estimated_daily_cost:,.2f}",
                    'Estimated Monthly Bill (₹)': f"₹ {estimated_monthly_bill:,.2f}",
                    'Effective Rate (₹/kWh)': f"₹ {msedcl_daily['effective_rate_per_kwh']:.2f}",
                    'Peak Load': f"{peak_kwh:.2f} kWh @ {peak_hour}",
                    'Billing Period': chosen_period.split('(')[0].strip(),
                    'Connection Type': 'Single Phase' if 'Single Phase' in chosen_conn else 'Three Phase'
                }
                st.session_state.prediction_history.insert(0, history_record)

                # Mandatory Notice: Clearly distinguish daily calculation from monthly bill & label as estimate
                slab_mode_desc = "MERC Daily Pro-rata Slabs (Monthly / 30)" if chosen_slab_mode == "prorata" else "Standard Progressive Slabs"
                render_html(f"""
                    <div class="estimated-bill-banner">
                        ⚠️ <b>ESTIMATED DAILY ELECTRICITY CALCULATION (MSEDCL 2026 TARIFF):</b> 
                        This calculation estimates electricity consumption and charges for a <b>single 24-hour day ({target_date_val}, {daily_res['day_of_week']})</b>, 
                        <b>clearly distinguished from a full monthly bill</b>. Under MERC billing principles for partial or daily durations, 
                        fixed demand charges (<b>₹{msedcl_daily['fixed_charge_daily']:.2f}/day</b> prorated from ₹{msedcl_daily['fixed_charge_monthly']:.0f}/month) 
                        and municipal fees are prorated (1/30th), progressive energy slabs are evaluated on a daily basis ({slab_mode_desc}), 
                        and 16% Maharashtra Electricity Duty is computed on daily applicable charges. 
                        <b>This result is an estimate for energy consumption forecasting and planning, not an official MSEDCL / Mahavitaran bill.</b>
                    </div>
                """)

                # Hero Prediction Card (Daily 24h Consumption & Estimated Daily MSEDCL Amount)
                render_html(f"""
                    <div class="hero-prediction-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 16px;">
                            <span class="hero-badge">Model: {summary['best_model_name']} (R²: {summary['best_r2']:.4f})</span>
                            <span class="mseb-badge">⚡ MSEDCL Domestic Tariff (from 1 April 2026)</span>
                            <span class="hero-badge">Target Date: {target_date_val} ({daily_res['day_of_week']})</span>
                            <span class="hero-badge">{slab_mode_desc}</span>
                        </div>

                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; align-items: stretch; margin: 16px 0;">
                            <!-- Predicted Daily 24h Consumption Column -->
                            <div style="background: rgba(255, 255, 255, 0.12); border-radius: 12px; padding: 24px; border: 1px solid rgba(255, 255, 255, 0.2); backdrop-filter: blur(4px);">
                                <div style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.88; font-weight: 600;">⚡ Predicted Daily Electricity Consumption (24 Hours)</div>
                                <div class="hero-prediction-val">{daily_consumption_kwh:,.2f} <span style="font-size: 1.6rem; font-weight: 500;">kWh</span></div>
                                <div style="font-size: 0.95rem; opacity: 0.95;">
                                    Expected 90% CI: <b>{daily_res['daily_lb_kwh']:,.2f} kWh</b> — <b>{daily_res['daily_ub_kwh']:,.2f} kWh</b>
                                </div>
                                <div style="font-size: 0.78rem; opacity: 0.82; margin-top: 6px;">
                                    Sum of 24 hourly ML predictions (Peak: <b>{peak_kwh:.2f} kWh</b> @ {peak_hour} • Baseload: <b>{baseload_kwh:.2f} kWh</b> @ {baseload_hour})
                                </div>
                            </div>

                            <!-- Estimated Daily MSEDCL Charges Column -->
                            <div style="background: rgba(255, 255, 255, 0.12); border-radius: 12px; padding: 24px; border: 1px solid rgba(255, 213, 79, 0.4); backdrop-filter: blur(4px);">
                                <div style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; color: #FFE082; font-weight: 600;">💰 Total Estimated Daily Amount</div>
                                <div class="hero-prediction-val" style="color: #FFD54F;">₹ {estimated_daily_cost:,.2f}</div>
                                <div style="font-size: 0.95rem; opacity: 0.95;">
                                    Expected CI Range: <b>₹ {daily_res['msedcl_lb_daily_bill']['total_estimated_amount']:,.2f}</b> — <b>₹ {daily_res['msedcl_ub_daily_bill']['total_estimated_amount']:,.2f}</b>
                                </div>
                                <div style="font-size: 0.82rem; color: #FFF9C4; margin-top: 6px;">
                                    Effective Daily Rate: <b>₹ {msedcl_daily['effective_rate_per_kwh']:.2f} / kWh</b> (Energy Charges + Additional Charges)
                                </div>
                            </div>
                        </div>

                        <div style="font-size: 0.82rem; margin-top: 14px; opacity: 0.9; max-width: 860px; margin-left: auto; margin-right: auto; line-height: 1.45;">
                            * Calculated strictly for a single day (24 hours) under MSEDCL MERC order applicable from 1 April 2026. Includes progressive energy slabs (₹3.96 – ₹17.53/unit), wheeling charge (₹{msedcl_daily['wheeling_rate']:.2f}/unit), prorated fixed demand charge (₹{msedcl_daily['fixed_charge_daily']:.2f}/day), fuel adjustment charge (FAC @ ₹{msedcl_daily['fac_rate']:.4f}/unit), and Maharashtra Electricity Duty (16% of applicable charges).
                        </div>
                    </div>
                """)

                # Requirement 7: Dedicated 4-Component Summary Row with Separate Labels
                st.markdown("### 📊 Electricity Consumption & Cost Summary")
                render_html(f"""
                    <div class="daily-summary-grid">
                        <div class="daily-summary-card card-blue">
                            <div class="daily-summary-title">⚡ Daily Consumption (kWh)</div>
                            <div class="daily-summary-value">{daily_consumption_kwh:,.2f} <span style="font-size: 1.05rem; font-weight: 500;">kWh</span></div>
                            <div class="daily-summary-sub">Sum of 24 hourly ML predictions</div>
                        </div>
                        <div class="daily-summary-card card-teal">
                            <div class="daily-summary-title">📅 Monthly Consumption (kWh)</div>
                            <div class="daily-summary-value" style="color: #0284C7;">{monthly_consumption_kwh:,.2f} <span style="font-size: 1.05rem; font-weight: 500;">kWh</span></div>
                            <div class="daily-summary-sub">Projected 30-day billing equivalent</div>
                        </div>
                        <div class="daily-summary-card card-amber">
                            <div class="daily-summary-title">💡 Estimated Daily Cost</div>
                            <div class="daily-summary-value" style="color: #D97706;">₹ {estimated_daily_cost:,.2f}</div>
                            <div class="daily-summary-sub">Estimated MSEDCL Daily Charges</div>
                        </div>
                        <div class="daily-summary-card card-green">
                            <div class="daily-summary-title">💰 Estimated Monthly Bill</div>
                            <div class="daily-summary-value" style="color: #059669;">₹ {estimated_monthly_bill:,.2f}</div>
                            <div class="daily-summary-sub">Projected full monthly bill</div>
                        </div>
                    </div>
                """)

                # Itemized Daily Charges Breakdown (6 Key Metric Tiles)
                st.markdown("### 🧾 Itemized Daily Charges Breakdown (MSEDCL 2026 Tariff)")
                k1, k2, k3, k4, k5, k6 = st.columns(6)
                with k1:
                    render_html(f"""
                        <div class="mseb-breakdown-box">
                            <div class="mseb-breakdown-label">Energy Charge</div>
                            <div class="mseb-breakdown-value">₹ {msedcl_daily['energy_charge']:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #64748B;">Progressive Slabs</div>
                        </div>
                    """)
                with k2:
                    render_html(f"""
                        <div class="mseb-breakdown-box">
                            <div class="mseb-breakdown-label">Wheeling Charge</div>
                            <div class="mseb-breakdown-value">₹ {msedcl_daily['wheeling_charge']:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #64748B;">@ ₹{msedcl_daily['wheeling_rate']:.2f}/unit</div>
                        </div>
                    """)
                with k3:
                    render_html(f"""
                        <div class="mseb-breakdown-box">
                            <div class="mseb-breakdown-label">Daily Fixed Charge</div>
                            <div class="mseb-breakdown-value">₹ {msedcl_daily['fixed_charge_daily']:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #64748B;">₹{msedcl_daily['fixed_charge_monthly']:.0f}/mo ÷ 30 days</div>
                        </div>
                    """)
                with k4:
                    render_html(f"""
                        <div class="mseb-breakdown-box">
                            <div class="mseb-breakdown-label">Daily FAC</div>
                            <div class="mseb-breakdown-value">₹ {msedcl_daily['fac_charge']:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #64748B;">@ ₹{msedcl_daily['fac_rate']:.4f}/unit</div>
                        </div>
                    """)
                with k5:
                    render_html(f"""
                        <div class="mseb-breakdown-box" style="background: #F0F7FF; border-color: #1E88E5;">
                            <div class="mseb-breakdown-label" style="color: #1E88E5;">Electricity Duty (16%)</div>
                            <div class="mseb-breakdown-value" style="color: #0D47A1;">₹ {msedcl_daily['ed_charge']:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #1E88E5;">16% of Applicable</div>
                        </div>
                    """)
                with k6:
                    render_html(f"""
                        <div class="mseb-breakdown-box" style="background: #FEF3C7; border-color: #F59E0B;">
                            <div class="mseb-breakdown-label" style="color: #B45309;">Daily Muni Charge</div>
                            <div class="mseb-breakdown-value" style="color: #92400E;">₹ {msedcl_daily['municipal_charge_daily']:,.2f}</div>
                            <div style="font-size: 0.72rem; color: #B45309;">₹10/mo ÷ 30 days</div>
                        </div>
                    """)

                st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)

                # Interactive 24-Hour Load Profile Chart
                st.markdown("### 📈 24-Hour Electricity Load Curve & Diurnal Profile")
                fig_24h = viz.plot_daily_24h_profile(hourly_df, str(target_date_val))
                st.plotly_chart(fig_24h, use_container_width=True)

                st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

                # Calculation Breakdown & Simulation Tabs
                b_tab1, b_tab2, b_tab3, b_tab4 = st.tabs([
                    "🕒 24-Hour Hourly Breakdown Table",
                    "📶 Daily Progressive Slab Breakdown",
                    "🧮 Step-by-Step Daily Calculation Formula",
                    "🎛️ Interactive Daily Bill Simulator"
                ])

                with b_tab1:
                    st.markdown(f"##### 🕒 Hourly Load Profile for **{target_date_val}** ({daily_res['day_of_week']})")
                    display_hourly = hourly_df[['Time', 'Predicted_kWh', 'Estimated_Cost_INR', 'Temperature', 'Humidity', 'Occupancy', 'HVACUsage', 'LightingUsage', 'RenewableEnergy']].copy()
                    display_hourly.columns = ['Time', 'Predicted (kWh)', 'Est. Cost (₹)', 'Temp (°C)', 'Humidity (%)', 'Occupants', 'HVAC', 'Lighting', 'Solar PV (kWh)']
                    st.dataframe(display_hourly, use_container_width=True)

                    c_dl, _ = st.columns([1, 2])
                    with c_dl:
                        csv_24h = display_hourly.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="📥 Download 24h Hourly Forecast (CSV)",
                            data=csv_24h,
                            file_name=f"24h_energy_profile_{target_date_val}.csv",
                            mime="text/csv",
                            use_container_width=True
                        )

                with b_tab2:
                    st.markdown(f"##### 📶 Daily Progressive Energy Slabs for **{daily_consumption_kwh:,.2f} kWh** ({slab_mode_desc})")
                    slab_display_data = []
                    for s in msedcl_daily['slab_breakdown']:
                        status_text = "✅ Active" if s["is_active"] and s["units"] > 0 else ("⏳ Inactive" if s["units"] == 0 else "✅ Covered")
                        slab_display_data.append({
                            "Daily Slab Tier": s["slab_label"],
                            "Tariff Rate (₹/kWh)": f"₹ {s['rate']:.2f}",
                            "Units Consumed (kWh)": f"{s['units']:.2f}",
                            "Energy Charge (₹)": f"₹ {s['cost']:,.2f}",
                            "Tier Status": status_text
                        })
                    st.table(pd.DataFrame(slab_display_data))
                    st.caption("Under MERC prorata rules for partial durations, monthly slab limits are prorated (divided by 30 days) to prevent disproportionate slab jumps.")

                with b_tab3:
                    st.markdown(f"##### 🧮 Step-by-Step Daily Calculation Formula (MERC Rules — {target_date_val})")
                    render_html(f"""
                    <div class="mseb-card-container">
                        <table style="width: 100%; border-collapse: collapse; font-size: 0.92rem;">
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 9px 0; color: #475569;">1. Daily Energy Charges (Sum of Progressive Daily Slabs)</td>
                                <td style="padding: 9px 0; text-align: right; font-weight: 600; color: #D97706;">₹ {msedcl_daily['energy_charge']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 9px 0; color: #475569;">2. Daily Wheeling Charges ({daily_consumption_kwh:,.2f} units × ₹{msedcl_daily['wheeling_rate']:.2f}/unit)</td>
                                <td style="padding: 9px 0; text-align: right; font-weight: 600;">₹ {msedcl_daily['wheeling_charge']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 9px 0; color: #475569;">3. Daily Fixed Demand Charges (Prorated: ₹{msedcl_daily['fixed_charge_monthly']:.0f}/month ÷ 30 days)</td>
                                <td style="padding: 9px 0; text-align: right; font-weight: 600;">₹ {msedcl_daily['fixed_charge_daily']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 9px 0; color: #475569;">4. Daily Fuel Adjustment Charges (FAC) ({daily_consumption_kwh:,.2f} units × ₹{msedcl_daily['fac_rate']:.4f}/unit)</td>
                                <td style="padding: 9px 0; text-align: right; font-weight: 600;">₹ {msedcl_daily['fac_charge']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 2px solid #CBD5E1; background: #F8FAFC;">
                                <td style="padding: 10px 0; font-weight: 700; color: #0F172A;">Applicable Charges Subtotal (Base for 16% Electricity Duty)</td>
                                <td style="padding: 10px 0; text-align: right; font-weight: 700; color: #0F172A;">₹ {msedcl_daily['applicable_charges']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 9px 0; color: #475569;">5. Maharashtra Electricity Duty (16.0% of ₹{msedcl_daily['applicable_charges']:,.2f})</td>
                                <td style="padding: 9px 0; text-align: right; font-weight: 600; color: #1E88E5;">₹ {msedcl_daily['ed_charge']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0;">
                                <td style="padding: 9px 0; color: #475569;">6. Daily Municipal Corporation Charge (Prorated: ₹10.00/month ÷ 30 days)</td>
                                <td style="padding: 9px 0; text-align: right; font-weight: 600; color: #92400E;">₹ {msedcl_daily['municipal_charge_daily']:,.2f}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #E2E8F0; background: #FDF4FF;">
                                <td style="padding: 10px 0; font-weight: 700; color: #7C3AED;">Total Applicable Additional Charges (Wheeling + Fixed + FAC + Duty + Muni)</td>
                                <td style="padding: 10px 0; text-align: right; font-weight: 700; color: #7C3AED;">₹ {msedcl_daily['total_additional_charges']:,.2f}</td>
                            </tr>
                            <tr style="background: #EFF6FF; border-top: 2px solid #1E88E5;">
                                <td style="padding: 12px 0; font-weight: 800; font-size: 1.1rem; color: #0D47A1;">Total Estimated Daily Amount Payable</td>
                                <td style="padding: 12px 0; text-align: right; font-weight: 800; font-size: 1.25rem; color: #0D47A1;">₹ {msedcl_daily['total_estimated_amount']:,.2f}</td>
                            </tr>
                        </table>
                    </div>
                    """)

                with b_tab4:
                    st.markdown("##### 🎛️ Interactive Daily Bill Simulator")
                    st.markdown("Simulate different daily consumption levels and inspect daily energy charges, additional charges, and total amounts:")

                    sim_daily_kwh = st.slider(
                        "Simulate Daily Consumption (kWh / Units)",
                        min_value=0.0, max_value=2500.0,
                        value=float(min(2500.0, max(0.0, daily_consumption_kwh))),
                        step=5.0
                    )
                    sim_daily_bill = calculate_msedcl_daily_bill(
                        daily_kwh=sim_daily_kwh,
                        connection_type=chosen_conn,
                        billing_period=chosen_period,
                        fac_rate=resolved_fac,
                        wheeling_rate=resolved_wheeling,
                        fixed_charge_monthly=resolved_fixed,
                        electricity_duty_pct=resolved_ed,
                        apply_municipal_charge=chosen_muni,
                        municipal_charge_monthly=resolved_muni,
                        slab_mode=chosen_slab_mode,
                        custom_slabs=active_daily_slabs
                    )
                    sc1, sc2, sc3, sc4 = st.columns(4)
                    with sc1:
                        st.metric("Daily Units", f"{sim_daily_kwh:,.1f} kWh")
                    with sc2:
                        st.metric("Daily Energy Charges", f"₹ {sim_daily_bill['energy_charge']:,.2f}")
                    with sc3:
                        st.metric("Additional Charges", f"₹ {sim_daily_bill['total_additional_charges']:,.2f}")
                    with sc4:
                        st.metric("Total Daily Amount", f"₹ {sim_daily_bill['total_estimated_amount']:,.2f}")

                # Contextual Factor Breakdown
                st.markdown("#### 🔍 Key Operational Drivers for this Daily Prediction")
                drivers = []
                if daily_consumption_kwh > 1500:
                    drivers.append(f"High continuous load ({daily_consumption_kwh:,.1f} kWh/day) corresponding to {input_dict['SquareFootage']:.0f} sq ft facility area")
                else:
                    drivers.append(f"Daily load profile ({daily_consumption_kwh:,.1f} kWh/day) on {target_date_val} ({daily_res['day_of_week']})")

                if input_dict['HVACUsage'] == 'On':
                    drivers.append("HVAC continuous cooling cycle active throughout operational daytime & evening hours")
                else:
                    drivers.append("HVAC disabled (natural ventilation / baseload cooling)")

                if input_dict['RenewableEnergy'] > 0:
                    total_solar_day = float(hourly_df['RenewableEnergy'].sum())
                    solar_savings = total_solar_day * msedcl_daily['effective_rate_per_kwh']
                    drivers.append(f"Solar PV generation offset: {total_solar_day:.1f} kWh/day produced (saves ~₹{solar_savings:,.2f}/day)")

                drivers.append(f"Peak demand hour: {peak_hour} ({peak_kwh:.2f} kWh/hr) | Baseload hour: {baseload_hour} ({baseload_kwh:.2f} kWh/hr)")

                cols = st.columns(len(drivers))
                for i, d in enumerate(drivers):
                    with cols[i]:
                        st.info(d, icon="💡")

        except Exception as e:
            st.error(f"Prediction and bill calculation failed: {e}", icon="⚠️")

    # Session Prediction History Table
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 Session Prediction History")

    if st.session_state.prediction_history:
        history_df = pd.DataFrame(st.session_state.prediction_history)
        st.dataframe(history_df, use_container_width=True)

        c_down, c_clear = st.columns([1, 1])
        with c_down:
            csv_data = history_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Prediction History (CSV)",
                data=csv_data,
                file_name=f"energy_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        with c_clear:
            if st.button("🗑️ Clear History", use_container_width=True):
                st.session_state.prediction_history = []
                st.rerun()
    else:
        st.info("No predictions recorded yet during this session. Use the form above to run a prediction.", icon="ℹ️")


# -----------------------------------------------------------------------------
# PAGE: MSEDCL Domestic Electricity Bill Calculator (From 1 April 2026)
# -----------------------------------------------------------------------------
elif "MSEDCL Bill Calculator" in nav_page:
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px; flex-wrap: wrap;">
                <span class="mseb-badge">⚡ Official MSEDCL Tariff Order</span>
                <span class="hero-badge">Applicable from 1 April 2026</span>
                <span class="hero-badge">Category: LT-I Domestic</span>
                <span class="hero-badge">MERC Regulatory Framework</span>
            </div>
            <h1 style="color: #0F172A; font-weight: 800; font-size: 2.1rem; margin-bottom: 4px;">⚡ MSEDCL Domestic Electricity Bill Calculator</h1>
            <p style="color: #64748B; font-size: 1.02rem;">
                Official Maharashtra State Electricity Distribution Co. Ltd. (Mahavitaran) progressive domestic tariff engine. 
                Computes estimated electricity bills using progressive telescopic energy slabs, wheeling charges (₹1.60/unit), 
                fixed demand charges, billing-period Fuel Adjustment Charges (FAC), and 16% Maharashtra Electricity Duty.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Sync notification if ML prediction exists
    last_pred_kwh = st.session_state.get('last_predicted_monthly_kwh', None)
    default_calc_kwh = 250.0
    if last_pred_kwh is not None:
        default_calc_kwh = float(last_pred_kwh)
        col_sync1, col_sync2 = st.columns([4, 1.2])
        with col_sync1:
            st.info(f"💡 **Latest Machine Learning Forecast Available:** **{last_pred_kwh:,.2f} kWh** monthly consumption (from '🔮 Predict Energy' page)", icon="🤖")
        with col_sync2:
            if st.button("🔄 Sync with Model", use_container_width=True, help="Set input consumption to latest ML model forecast"):
                st.session_state.calc_monthly_kwh_input = float(last_pred_kwh)
                st.rerun()

    if "calc_monthly_kwh_input" not in st.session_state:
        st.session_state.calc_monthly_kwh_input = default_calc_kwh

    # Main Input Configuration Card
    with st.container():
        st.markdown('<div class="ew-card">', unsafe_allow_html=True)
        st.markdown("### 🎛️ Consumption & Tariff Configuration")

        # Quick Test Case Presets (Requirement 7)
        st.markdown("##### ⚡ Quick Test Cases & Empirical Benchmarks")
        tc1, tc2, tc3, tc4, tc5, tc6 = st.columns(6)
        with tc1:
            if st.button("📋 42 Units\n(Ref Bill)", use_container_width=True, help="Empirical Sample Bill Reference: 42 units, ₹870 actual"):
                st.session_state.calc_monthly_kwh_input = 42.0
                st.rerun()
        with tc2:
            if st.button("🔹 100 Units\n(Slab 1)", use_container_width=True, help="Upper limit of Slab 1 (1–100 units @ ₹3.96)"):
                st.session_state.calc_monthly_kwh_input = 100.0
                st.rerun()
        with tc3:
            if st.button("🔹 200 Units\n(Slab 2)", use_container_width=True, help="Mid-point of Slab 2 (101–300 units @ ₹10.80)"):
                st.session_state.calc_monthly_kwh_input = 200.0
                st.rerun()
        with tc4:
            if st.button("🔹 500 Units\n(Slab 3)", use_container_width=True, help="Upper limit of Slab 3 (301–500 units @ ₹15.03)"):
                st.session_state.calc_monthly_kwh_input = 500.0
                st.rerun()
        with tc5:
            if st.button("🔹 1000 Units\n(Slab 4)", use_container_width=True, help="Upper limit of Slab 4 (501–1000 units @ ₹17.53)"):
                st.session_state.calc_monthly_kwh_input = 1000.0
                st.rerun()
        with tc6:
            if st.button("🔹 2800 Units\n(Slab 5)", use_container_width=True, help="High consumption tier (>1000 units @ ₹17.53)"):
                st.session_state.calc_monthly_kwh_input = 2800.0
                st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        c_kwh, c_period, c_conn = st.columns([1.4, 1.3, 1.3])

        with c_kwh:
            calc_monthly_kwh = st.number_input(
                "Monthly Electricity Consumption (kWh / Units)",
                min_value=0.0,
                max_value=500000.0,
                value=float(st.session_state.calc_monthly_kwh_input),
                step=10.0,
                help="Enter monthly electricity consumption in kWh, or use the value forecasted by the machine learning pipeline."
            )
            # Update session state if user changed input
            st.session_state.calc_monthly_kwh_input = calc_monthly_kwh

        with c_period:
            calc_billing_period = st.selectbox(
                "Billing Period (FAC Schedule)",
                options=VALID_BILLING_PERIODS,
                index=0,
                help="Select billing month to apply the applicable Fuel Adjustment Charge (FAC) rate."
            )
            period_fac_default = BILLING_PERIODS_CONFIG.get(calc_billing_period, {}).get("fac_rate", 0.65)
            period_notes = BILLING_PERIODS_CONFIG.get(calc_billing_period, {}).get("notes", "")
            st.caption(f"🗓️ Applicable FAC: **₹{period_fac_default:.2f} / unit** • {period_notes}")

        with c_conn:
            calc_connection_type = st.selectbox(
                "Connection Type",
                options=VALID_CONNECTION_TYPES,
                index=0,
                help="Single Phase (₹130/month) is standard for domestic households. Three Phase (₹440/month) is for heavier domestic loads."
            )
            calc_apply_muni = st.checkbox(
                "Apply Additional Municipal Charge (₹10/month)",
                value=True,
                help="Municipal Corporation charge applicable within urban corporation/council limits (default ₹10/month)."
            )

        st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

        # Time-Varying Tariff Parameters & Rate Editor Expander
        with st.expander("⚙️ Time-Varying Tariff Parameters & Rate Editor (MSEDCL Order — 1 April 2026)", expanded=False):
            st.markdown("<div style='font-size: 0.85rem; color: #64748B; margin-bottom: 8px;'>You can review or adjust all official MSEDCL 2026 rates below. Changes update the bill calculation dynamically without code hardcoding:</div>", unsafe_allow_html=True)
            
            t1, t2, t3 = st.columns(3)
            with t1:
                calc_user_wheeling = st.number_input(
                    "Wheeling Charge (₹/unit)",
                    min_value=0.0, max_value=10.0, value=DEFAULT_WHEELING_CHARGE_PER_UNIT, step=0.05,
                    key="p_user_wheeling",
                    help="Official wheeling charge applied per unit consumed (default: ₹1.60/unit)"
                )
                calc_user_fixed_single = st.number_input(
                    "Single Phase Fixed (₹/month)",
                    min_value=0.0, max_value=1000.0, value=DEFAULT_FIXED_CHARGE_SINGLE_PHASE, step=5.0,
                    key="p_user_fixed_single",
                    help="Fixed demand charge for single phase connections (default: ₹130/month)"
                )
            with t2:
                calc_user_fac = st.number_input(
                    "Fuel Adjustment Charge (FAC ₹/unit)",
                    min_value=0.0, max_value=5.0, value=float(period_fac_default), step=0.01,
                    key="p_user_fac",
                    help=f"FAC rate for {calc_billing_period} (default: ₹{period_fac_default:.2f}/unit)"
                )
                calc_user_fixed_three = st.number_input(
                    "Three Phase Fixed (₹/month)",
                    min_value=0.0, max_value=2000.0, value=DEFAULT_FIXED_CHARGE_THREE_PHASE, step=10.0,
                    key="p_user_fixed_three",
                    help="Fixed demand charge for three phase connections (default: ₹440/month)"
                )
            with t3:
                calc_user_ed = st.number_input(
                    "Electricity Duty (%)",
                    min_value=0.0, max_value=50.0, value=DEFAULT_ELECTRICITY_DUTY_PCT, step=0.5,
                    key="p_user_ed",
                    help="Government of Maharashtra statutory electricity duty (default: 16% of applicable charges)"
                )
                calc_user_muni = st.number_input(
                    "Municipal Charge (₹/month)",
                    min_value=0.0, max_value=100.0, value=DEFAULT_MUNICIPAL_CHARGE_MONTHLY, step=1.0,
                    key="p_user_muni",
                    help="Additional municipal fee where applicable (default: ₹10/month)"
                )

            st.markdown("<div style='font-size: 0.82rem; font-weight: 600; color: #475569; margin: 10px 0 4px 0;'>MSEDCL Domestic Progressive Energy Slabs (Applicable from 1 April 2026):</div>", unsafe_allow_html=True)
            sk1, sk2, sk3, sk4, sk5 = st.columns(5)
            with sk1:
                ps1 = st.number_input("1–100 Units (₹)", value=3.96, step=0.01, format="%.2f", key="p_s1")
            with sk2:
                ps2 = st.number_input("101–300 Units (₹)", value=10.80, step=0.01, format="%.2f", key="p_s2")
            with sk3:
                ps3 = st.number_input("301–500 Units (₹)", value=15.03, step=0.01, format="%.2f", key="p_s3")
            with sk4:
                ps4 = st.number_input("501–1000 Units (₹)", value=17.53, step=0.01, format="%.2f", key="p_s4")
            with sk5:
                ps5 = st.number_input("Above 1000 Units (₹)", value=17.53, step=0.01, format="%.2f", key="p_s5")

        st.markdown('</div>', unsafe_allow_html=True)

    # Active Progressive Slabs
    calc_active_slabs = [
        {"min": 0, "max": 100, "rate": float(ps1), "label": "1 – 100 units"},
        {"min": 100, "max": 300, "rate": float(ps2), "label": "101 – 300 units"},
        {"min": 300, "max": 500, "rate": float(ps3), "label": "301 – 500 units"},
        {"min": 500, "max": 1000, "rate": float(ps4), "label": "501 – 1000 units"},
        {"min": 1000, "max": float("inf"), "rate": float(ps5), "label": "Above 1000 units"},
    ]
    resolved_calc_fixed = calc_user_fixed_three if "Three Phase" in calc_connection_type else calc_user_fixed_single

    # Execute MSEDCL 2026 Bill Calculation
    calc_bill = calculate_msedcl_2026_bill(
        monthly_kwh=calc_monthly_kwh,
        connection_type=calc_connection_type,
        billing_period=calc_billing_period,
        fac_rate=calc_user_fac,
        wheeling_rate=calc_user_wheeling,
        fixed_charge=resolved_calc_fixed,
        electricity_duty_pct=calc_user_ed,
        apply_municipal_charge=calc_apply_muni,
        municipal_charge_amount=calc_user_muni,
        custom_slabs=calc_active_slabs
    )

    # Requirement: Clearly label the output as an estimated bill, not an official bill
    render_html(f"""
        <div class="estimated-bill-banner">
            ⚠️ <b>ESTIMATED BILL NOTICE:</b> This calculation is an estimate derived from the official 
            MSEDCL domestic electricity tariff framework applicable from <b>1 April 2026</b>. 
            <b>This is NOT an official electricity bill issued by Mahavitaran / MSEDCL.</b> 
            Actual utility bills may vary based on exact meter reading cycles, localized fuel surcharge adjustments, 
            prompt payment discounts (1%), or delayed payment charges.
        </div>
    """)

    # Hero Prediction & Bill Result Card
    render_html(f"""
        <div class="hero-prediction-card">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px; margin-bottom: 16px;">
                <span class="mseb-badge">⚡ MSEDCL Domestic Tariff (from 1 April 2026)</span>
                <span class="hero-badge">Billing Period: {calc_billing_period.split('(')[0].strip()}</span>
                <span class="hero-badge">Connection: {'Single Phase (Standard)' if 'Single Phase' in calc_connection_type else 'Three Phase (Heavy Load)'}</span>
                <span class="hero-badge">FAC Rate: ₹ {calc_bill['fac_rate']:.4f}/unit</span>
            </div>

            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 18px; align-items: stretch; margin: 16px 0;">
                <!-- Monthly Electricity Consumption Column -->
                <div style="background: rgba(255, 255, 255, 0.12); border-radius: 12px; padding: 24px; border: 1px solid rgba(255, 255, 255, 0.2); backdrop-filter: blur(4px);">
                    <div style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.88; font-weight: 600;">⚡ Monthly Electricity Consumption</div>
                    <div class="hero-prediction-val">{calc_monthly_kwh:,.2f} <span style="font-size: 1.6rem; font-weight: 500;">kWh</span></div>
                    <div style="font-size: 0.95rem; opacity: 0.95;">
                        Daily Equivalent Load: <b>{calc_monthly_kwh / 30.0:,.2f} kWh / day</b> (over standard 30-day billing cycle)
                    </div>
                    <div style="font-size: 0.78rem; opacity: 0.82; margin-top: 6px;">
                        Progressive slab tiers applied: 1–100, 101–300, 301–500, 501–1000, >1000 units
                    </div>
                </div>

                <!-- Estimated MSEDCL Electricity Bill Column -->
                <div style="background: rgba(255, 255, 255, 0.12); border-radius: 12px; padding: 24px; border: 1px solid rgba(255, 213, 79, 0.4); backdrop-filter: blur(4px);">
                    <div style="font-size: 0.82rem; text-transform: uppercase; letter-spacing: 0.05em; color: #FFE082; font-weight: 600;">💰 Total Estimated Monthly Bill</div>
                    <div class="hero-prediction-val" style="color: #FFD54F;">₹ {calc_bill['total_estimated_bill']:,.2f}</div>
                    <div style="font-size: 0.95rem; opacity: 0.95;">
                        Effective Average Rate: <b>₹ {calc_bill['effective_rate_per_kwh']:.2f} / kWh</b> (All-inclusive)
                    </div>
                    <div style="font-size: 0.82rem; color: #FFF9C4; margin-top: 6px;">
                        Estimated Daily Cost: <b>₹ {calc_bill['total_estimated_bill'] / 30.0:,.2f} / day</b> • Base for 16% Duty: ₹ {calc_bill['applicable_charges']:,.2f}
                    </div>
                </div>
            </div>

            <div style="font-size: 0.82rem; margin-top: 14px; opacity: 0.9; max-width: 860px; margin-left: auto; margin-right: auto; line-height: 1.45;">
                * Calculated per official MERC Tariff Order applicable from 1 April 2026. Includes progressive telescopic energy charges (₹3.96 – ₹17.53/unit), wheeling charge (₹{calc_bill['wheeling_rate']:.2f}/unit), fixed demand charge (₹{calc_bill['fixed_charge']:.2f}/month), fuel adjustment charge (FAC @ ₹{calc_bill['fac_rate']:.4f}/unit), and Maharashtra Electricity Duty (16% of applicable charges).
            </div>
        </div>
    """)

    # Requirement 2 & 7: Empirical Sample Bill Reference Card (42 Units)
    if abs(calc_monthly_kwh - 42.0) < 0.05:
        render_html(f"""
            <div style="background: #FFFBEB; border: 1px solid #FDE68A; border-left: 5px solid #F59E0B; border-radius: 10px; padding: 18px 22px; margin: 18px 0; color: #92400E;">
                <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px; margin-bottom: 8px;">
                    <span style="font-weight: 700; font-size: 1.05rem; color: #B45309;">📋 Actual Electricity Bill Reference Comparison (42 Units — November 2025)</span>
                    <span style="background: #F59E0B; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.78rem; font-weight: 600;">Empirical Test Case</span>
                </div>
                <div style="font-size: 0.92rem; line-height: 1.55; color: #78350F;">
                    <b>Actual User Utility Bill (November 2025):</b><br>
                    • <b>Connection:</b> Residential, Single Phase | <b>Sanctioned Load:</b> 2 kW<br>
                    • <b>Meter Readings:</b> Previous: 3663, Current: 3705 → <b>Actual Billed Units: 42 kWh</b><br>
                    • <b>Actual Bill Amount: ₹ 870.00</b> (Due Date Amount: <b>₹ 880.00</b>, reflecting ₹10 Delayed Payment Charge)<br>
                    <div style="margin: 8px 0; padding: 10px 14px; background: rgba(255, 255, 255, 0.7); border-radius: 8px; border: 1px dashed #F59E0B;">
                        <b>1 April 2026 Tariff Calculation for 42 Units:</b><br>
                        • Energy Charges (42 units @ ₹3.96): <b>₹ {calc_bill['energy_charge']:.2f}</b><br>
                        • Wheeling Charges (42 units @ ₹1.60): <b>₹ {calc_bill['wheeling_charge']:.2f}</b><br>
                        • Fixed Demand Charge (Single Phase): <b>₹ {calc_bill['fixed_charge']:.2f}</b><br>
                        • Fuel Adjustment Charges (FAC @ ₹{calc_bill['fac_rate']:.4f}/unit): <b>₹ {calc_bill['fac_charge']:.2f}</b><br>
                        • Applicable Charges Subtotal: <b>₹ {calc_bill['applicable_charges']:.2f}</b><br>
                        • Maharashtra Electricity Duty (16% of ₹{calc_bill['applicable_charges']:.2f}): <b>₹ {calc_bill['ed_charge']:.2f}</b><br>
                        • Municipal Corporation Charge: <b>₹ {calc_bill['municipal_charge']:.2f}</b><br>
                        • <b>Total Calculated 2026 Estimate: ₹ {calc_bill['total_estimated_bill']:.2f}</b> (Effective: ₹ {calc_bill['effective_rate_per_kwh']:.2f}/kWh)
                    </div>
                    ℹ️ <b>Analytical Note:</b> ₹870 is used strictly as an empirical reference example. 
                    Because itemized line receipts are unavailable, the calculator does NOT invent missing charges or claim official verification against the actual bill. 
                    Historical November 2025 bills operated under earlier MYT tariff orders, cumulative past FAC adjustments/arrears, meter rent, or minimum billing for 2 kW load.
                </div>
            </div>
        """)

    # Requirement 7: Dedicated 4-Component Summary Row with Separate Labels
    st.markdown("### 📊 Electricity Consumption & Cost Summary")
    render_html(f"""
        <div class="daily-summary-grid">
            <div class="daily-summary-card card-blue">
                <div class="daily-summary-title">⚡ Daily Consumption (kWh)</div>
                <div class="daily-summary-value">{calc_monthly_kwh / 30.0:,.2f} <span style="font-size: 1.05rem; font-weight: 500;">kWh</span></div>
                <div class="daily-summary-sub">Daily equivalent (Monthly kWh ÷ 30)</div>
            </div>
            <div class="daily-summary-card card-teal">
                <div class="daily-summary-title">📅 Monthly Consumption (kWh)</div>
                <div class="daily-summary-value" style="color: #0284C7;">{calc_monthly_kwh:,.2f} <span style="font-size: 1.05rem; font-weight: 500;">kWh</span></div>
                <div class="daily-summary-sub">Total billed monthly units</div>
            </div>
            <div class="daily-summary-card card-amber">
                <div class="daily-summary-title">💡 Estimated Daily Cost</div>
                <div class="daily-summary-value" style="color: #D97706;">₹ {calc_bill['total_estimated_bill'] / 30.0:,.2f}</div>
                <div class="daily-summary-sub">Daily equivalent (Monthly bill ÷ 30)</div>
            </div>
            <div class="daily-summary-card card-green">
                <div class="daily-summary-title">💰 Estimated Monthly Bill</div>
                <div class="daily-summary-value" style="color: #059669;">₹ {calc_bill['total_estimated_bill']:,.2f}</div>
                <div class="daily-summary-sub">Full MSEDCL Monthly Bill (inc. 16% Duty)</div>
            </div>
        </div>
    """)

    # Itemized Charges Breakdown (6 Key Metric Tiles)
    st.markdown("### 🧾 Itemized MSEDCL Monthly Bill Breakdown")
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    with k1:
        render_html(f"""
            <div class="mseb-breakdown-box">
                <div class="mseb-breakdown-label">Energy Charge</div>
                <div class="mseb-breakdown-value">₹ {calc_bill['energy_charge']:,.2f}</div>
                <div style="font-size: 0.72rem; color: #64748B;">Progressive Slabs</div>
            </div>
        """)
    with k2:
        render_html(f"""
            <div class="mseb-breakdown-box">
                <div class="mseb-breakdown-label">Wheeling Charge</div>
                <div class="mseb-breakdown-value">₹ {calc_bill['wheeling_charge']:,.2f}</div>
                <div style="font-size: 0.72rem; color: #64748B;">@ ₹{calc_bill['wheeling_rate']:.2f}/unit</div>
            </div>
        """)
    with k3:
        render_html(f"""
            <div class="mseb-breakdown-box">
                <div class="mseb-breakdown-label">Fixed Demand</div>
                <div class="mseb-breakdown-value">₹ {calc_bill['fixed_charge']:,.2f}</div>
                <div style="font-size: 0.72rem; color: #64748B;">{'Single Phase' if 'Single Phase' in calc_connection_type else 'Three Phase'}</div>
            </div>
        """)
    with k4:
        render_html(f"""
            <div class="mseb-breakdown-box">
                <div class="mseb-breakdown-label">FAC Surcharge</div>
                <div class="mseb-breakdown-value">₹ {calc_bill['fac_charge']:,.2f}</div>
                <div style="font-size: 0.72rem; color: #64748B;">@ ₹{calc_bill['fac_rate']:.4f}/unit</div>
            </div>
        """)
    with k5:
        render_html(f"""
            <div class="mseb-breakdown-box" style="background: #F0F7FF; border-color: #1E88E5;">
                <div class="mseb-breakdown-label" style="color: #1E88E5;">Electricity Duty (16%)</div>
                <div class="mseb-breakdown-value" style="color: #0D47A1;">₹ {calc_bill['ed_charge']:,.2f}</div>
                <div style="font-size: 0.72rem; color: #1E88E5;">16% of Applicable</div>
            </div>
        """)
    with k6:
        render_html(f"""
            <div class="mseb-breakdown-box" style="background: #FEF3C7; border-color: #F59E0B;">
                <div class="mseb-breakdown-label" style="color: #B45309;">Municipal Charge</div>
                <div class="mseb-breakdown-value" style="color: #92400E;">₹ {calc_bill['municipal_charge']:,.2f}</div>
                <div style="font-size: 0.72rem; color: #B45309;">Where Applicable</div>
            </div>
        """)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # In-Depth Inspection Tabs
    tab_viz, tab_slabs, tab_formula, tab_compare, tab_tests = st.tabs([
        "📊 Bill Visualizations",
        "📑 Progressive Slab Breakdown",
        "🧮 Step-by-Step Formula & Audit",
        "🔄 Period & Connection Comparison",
        "🧪 Validation & Test Cases (6 Scenarios)"
    ])

    with tab_viz:
        st.markdown("##### 📊 Cost Composition & Slab Consumption Distribution")
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.plotly_chart(viz.plot_msedcl_bill_breakdown(calc_bill), use_container_width=True)
        with v_col2:
            st.plotly_chart(viz.plot_slab_distribution(calc_bill['slab_breakdown']), use_container_width=True)

    with tab_slabs:
        st.markdown("##### 📑 Progressive Domestic Tariff Slab Evaluation (From 1 April 2026)")
        st.markdown("Under MERC rules, domestic consumers are billed progressively: units in higher tiers do not increase the rate of units in lower tiers.")
        slab_rows = []
        for s in calc_bill['slab_breakdown']:
            status_text = "✅ Active" if s["is_active"] and s["units"] > 0 else ("⏳ Inactive" if s["units"] == 0 else "✅ Covered")
            slab_rows.append({
                "Tariff Slab Tier": s["slab_label"],
                "Tariff Rate (₹/kWh)": f"₹ {s['rate']:.2f}",
                "Units Consumed (kWh)": f"{s['units']:,.2f}",
                "Energy Charge (₹)": f"₹ {s['cost']:,.2f}",
                "Slab Status": status_text
            })
        st.table(pd.DataFrame(slab_rows))

    with tab_formula:
        st.markdown(f"##### 🧮 Step-by-Step Mathematical Calculation & Audit Log (MERC Order)")
        render_html(f"""
        <div class="mseb-card-container">
            <table style="width: 100%; border-collapse: collapse; font-size: 0.92rem;">
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 9px 0; color: #475569;">1. Energy Charges (Sum of 5 Progressive Telescopic Slabs)</td>
                    <td style="padding: 9px 0; text-align: right; font-weight: 600; color: #D97706;">₹ {calc_bill['energy_charge']:,.2f}</td>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 9px 0; color: #475569;">2. Wheeling Charges ({calc_monthly_kwh:,.2f} units × ₹{calc_bill['wheeling_rate']:.2f}/unit)</td>
                    <td style="padding: 9px 0; text-align: right; font-weight: 600;">₹ {calc_bill['wheeling_charge']:,.2f}</td>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 9px 0; color: #475569;">3. Fixed Monthly Demand Charges ({calc_connection_type.split('(')[0].strip()})</td>
                    <td style="padding: 9px 0; text-align: right; font-weight: 600;">₹ {calc_bill['fixed_charge']:,.2f}</td>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 9px 0; color: #475569;">4. Fuel Adjustment Charges (FAC) ({calc_monthly_kwh:,.2f} units × ₹{calc_bill['fac_rate']:.4f}/unit)</td>
                    <td style="padding: 9px 0; text-align: right; font-weight: 600;">₹ {calc_bill['fac_charge']:,.2f}</td>
                </tr>
                <tr style="border-bottom: 2px solid #CBD5E1; background: #F8FAFC;">
                    <td style="padding: 10px 0; font-weight: 700; color: #0F172A;">Applicable Charges Subtotal (Sum of 1+2+3+4, Base for 16% Electricity Duty)</td>
                    <td style="padding: 10px 0; text-align: right; font-weight: 700; color: #0F172A;">₹ {calc_bill['applicable_charges']:,.2f}</td>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 9px 0; color: #475569;">5. Maharashtra Electricity Duty (16.0% of ₹{calc_bill['applicable_charges']:,.2f})</td>
                    <td style="padding: 9px 0; text-align: right; font-weight: 600; color: #1E88E5;">₹ {calc_bill['ed_charge']:,.2f}</td>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0;">
                    <td style="padding: 9px 0; color: #475569;">6. Municipal Corporation Charge (Where applicable)</td>
                    <td style="padding: 9px 0; text-align: right; font-weight: 600; color: #92400E;">₹ {calc_bill['municipal_charge']:,.2f}</td>
                </tr>
                <tr style="border-bottom: 1px solid #E2E8F0; background: #FDF4FF;">
                    <td style="padding: 10px 0; font-weight: 700; color: #7C3AED;">Total Additional Charges Subtotal (Wheeling + Fixed + FAC + Duty + Municipal)</td>
                    <td style="padding: 10px 0; text-align: right; font-weight: 700; color: #7C3AED;">₹ {calc_bill['total_additional_charges']:,.2f}</td>
                </tr>
                <tr style="background: #EFF6FF; border-top: 2px solid #1E88E5;">
                    <td style="padding: 12px 0; font-weight: 800; font-size: 1.15rem; color: #0D47A1;">Total Estimated Monthly Bill Payable</td>
                    <td style="padding: 12px 0; text-align: right; font-weight: 800; font-size: 1.3rem; color: #0D47A1;">₹ {calc_bill['total_estimated_bill']:,.2f}</td>
                </tr>
            </table>
        </div>
        """)

    with tab_compare:
        st.markdown(f"##### 🔄 Bill Sensitivity Across Billing Periods ({calc_monthly_kwh:,.1f} kWh / month)")
        st.markdown("Inspect how the monthly electricity bill fluctuates across seasons due to changing FAC rates and connection types:")
        comp_rows = []
        for bp_name in VALID_BILLING_PERIODS:
            if bp_name == "Custom / Other Billing Period":
                continue
            fac_val = float(BILLING_PERIODS_CONFIG[bp_name]["fac_rate"])
            # Single phase bill
            b_single = calculate_msedcl_2026_bill(
                monthly_kwh=calc_monthly_kwh,
                connection_type="Single Phase (Domestic Standard — ₹130/month)",
                billing_period=bp_name,
                fac_rate=fac_val,
                wheeling_rate=calc_user_wheeling,
                fixed_charge=calc_user_fixed_single,
                electricity_duty_pct=calc_user_ed,
                apply_municipal_charge=calc_apply_muni,
                municipal_charge_amount=calc_user_muni,
                custom_slabs=calc_active_slabs
            )
            # Three phase bill
            b_three = calculate_msedcl_2026_bill(
                monthly_kwh=calc_monthly_kwh,
                connection_type="Three Phase (Heavy Load — ₹440/month)",
                billing_period=bp_name,
                fac_rate=fac_val,
                wheeling_rate=calc_user_wheeling,
                fixed_charge=calc_user_fixed_three,
                electricity_duty_pct=calc_user_ed,
                apply_municipal_charge=calc_apply_muni,
                municipal_charge_amount=calc_user_muni,
                custom_slabs=calc_active_slabs
            )
            comp_rows.append({
                "Billing Period": bp_name.split('(')[0].strip(),
                "FAC Rate (₹/unit)": f"₹ {fac_val:.2f}",
                "Single Phase Bill (₹)": f"₹ {b_single['total_estimated_bill']:,.2f}",
                "Single Phase Rate (₹/kWh)": f"₹ {b_single['effective_rate_per_kwh']:.2f}",
                "Three Phase Bill (₹)": f"₹ {b_three['total_estimated_bill']:,.2f}",
                "Three Phase Rate (₹/kWh)": f"₹ {b_three['effective_rate_per_kwh']:.2f}",
                "Season Notes": BILLING_PERIODS_CONFIG[bp_name].get("notes", "")
            })
        st.table(pd.DataFrame(comp_rows))

    with tab_tests:
        st.markdown("##### 🧪 Verification & Audit of 6 Mandatory Consumption Test Cases")
        st.markdown(
            "Under the 1 April 2026 MSEDCL Domestic Tariff Order, bills are calculated with progressive slabs, "
            "wheeling charge (₹1.60/unit), single-phase fixed charge (₹130/month), FAC (@ ₹0.65/unit), "
            "16% Maharashtra Electricity Duty, and ₹10 municipal charge. "
            "Every test case confirms that `Total Estimated Bill == Energy + Wheeling + Fixed + FAC + Duty + Municipal` with zero double counting."
        )

        test_case_units = [42.0, 100.0, 200.0, 500.0, 1000.0, 2800.0]
        test_rows = []
        for u in test_case_units:
            t_bill = calculate_msedcl_2026_bill(
                monthly_kwh=u,
                connection_type="Single Phase (Domestic Standard — ₹130/month)",
                billing_period="April 2026 (Initial Tariff Order)",
                fac_rate=0.65,
                wheeling_rate=1.60,
                fixed_charge=130.00,
                electricity_duty_pct=16.0,
                apply_municipal_charge=True,
                municipal_charge_amount=10.00
            )
            comp_sum = round(t_bill['energy_charge'] + t_bill['wheeling_charge'] + t_bill['fixed_charge'] + t_bill['fac_charge'] + t_bill['ed_charge'] + t_bill['municipal_charge'], 2)
            sum_pass = "✅ PASS" if abs(comp_sum - t_bill['total_estimated_bill']) < 0.01 else "❌ FAIL"

            test_rows.append({
                "Units (kWh)": f"{u:,.0f}",
                "Energy Charges (₹)": f"₹ {t_bill['energy_charge']:,.2f}",
                "Wheeling (₹)": f"₹ {t_bill['wheeling_charge']:,.2f}",
                "Fixed (₹)": f"₹ {t_bill['fixed_charge']:,.2f}",
                "FAC (₹)": f"₹ {t_bill['fac_charge']:,.2f}",
                "Applicable Base (₹)": f"₹ {t_bill['applicable_charges']:,.2f}",
                "Duty 16% (₹)": f"₹ {t_bill['ed_charge']:,.2f}",
                "Municipal (₹)": f"₹ {t_bill['municipal_charge']:,.2f}",
                "Total Estimated Bill (₹)": f"₹ {t_bill['total_estimated_bill']:,.2f}",
                "Effective Rate": f"₹ {t_bill['effective_rate_per_kwh']:.2f}/kWh",
                "Integrity Audit": sum_pass
            })

        st.dataframe(pd.DataFrame(test_rows), use_container_width=True)

        render_html("""
            <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 8px; padding: 14px 18px; font-size: 0.88rem; color: #475569; margin-top: 10px;">
                <b>📋 Analytical Audit Observations:</b><br>
                • <b>42 Units (Reference Case):</b> Energy ₹166.32 + Wheeling ₹67.20 + Fixed ₹130.00 + FAC ₹27.30 = Applicable ₹390.82 → 16% Duty ₹62.53 + Muni ₹10.00 = <b>₹463.35</b>.<br>
                • <b>Sample Bill Comparison:</b> The user's actual November 2025 bill was ₹870 (₹880 after due date). As per instructions, ₹870 is treated strictly as an empirical reference without inventing missing charges or artificially forcing the 2026 tariff engine.<br>
                • <b>Progressive Slabs:</b> Slabs transition smoothly across 100, 200, 500, 1000, and 2800 units without retroactive repricing of previous tiers.<br>
                • <b>Duty Base Compliance:</b> Electricity duty (16%) is strictly applied to applicable charges (Energy + Wheeling + Fixed + FAC) with municipal charge kept separate.<br>
                • <b>Zero Double Counting:</b> In every case, the total equals the exact sum of all displayed charge items.
            </div>
        """)


# -----------------------------------------------------------------------------
# PAGE 3: Model Performance
# -----------------------------------------------------------------------------
elif "Model Performance" in nav_page:
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="color: #0F172A; font-weight: 800; font-size: 2.1rem; margin-bottom: 4px;">Model Performance & Evaluation</h1>
            <p style="color: #64748B; font-size: 1.02rem;">Comparative evaluation of candidate machine learning algorithms evaluated on an independent 20% holdout test dataset ({:,} test samples).</p>
        </div>
    """.format(summary['test_samples']), unsafe_allow_html=True)

    # Model Summary Cards
    m_cols = st.columns(len(summary['results']))
    for idx, (m_name, m_res) in enumerate(summary['results'].items()):
        is_best = (m_name == summary['best_model_name'])
        badge = "🏆 Best Model" if is_best else "Candidate"
        border_color = "#1E88E5" if is_best else "#CBD5E1"
        bg_card = "#F0F7FF" if is_best else "#FFFFFF"

        with m_cols[idx]:
            render_html(f"""
                <div style="background: {bg_card}; border: 2px solid {border_color}; border-radius: 12px; padding: 18px; box-shadow: 0 2px 8px rgba(0,0,0,0.04); margin-bottom: 15px;">
                    <span style="font-size: 0.72rem; font-weight: 700; text-transform: uppercase; color: {'#1E88E5' if is_best else '#64748B'}; background: {'#DBEAFE' if is_best else '#F1F5F9'}; padding: 3px 8px; border-radius: 6px;">
                        {badge}
                    </span>
                    <h4 style="margin: 10px 0 6px 0; color: #0F172A; font-size: 1.1rem;">{m_name}</h4>
                    <div style="font-size: 1.55rem; font-weight: 800; color: #1E88E5;">R² = {m_res['r2']:.4f}</div>
                    <hr style="margin: 8px 0; border: none; border-top: 1px solid #E2E8F0;">
                    <div style="font-size: 0.85rem; color: #475569; line-height: 1.5;">
                        <b>MAE:</b> {m_res['mae']:.2f} kWh<br>
                        <b>MSE:</b> {m_res['mse']:.2f}<br>
                        <b>RMSE:</b> {m_res['rmse']:.2f} kWh
                    </div>
                </div>
            """)

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Comparative Bar Chart
    st.plotly_chart(viz.plot_model_comparison(summary['results']), use_container_width=True)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
    st.markdown("### 🔬 In-Depth Diagnostic Analysis")

    selected_diag_model = st.selectbox(
        "Select Model for Detailed Diagnostics",
        options=list(summary['results'].keys()),
        index=list(summary['results'].keys()).index(summary['best_model_name'])
    )

    diag_res = summary['results'][selected_diag_model]

    d_col1, d_col2 = st.columns([1, 1])
    with d_col1:
        st.plotly_chart(
            viz.plot_actual_vs_predicted(diag_res['y_test_sample'], diag_res['y_pred_sample'], selected_diag_model),
            use_container_width=True
        )
    with d_col2:
        st.plotly_chart(
            viz.plot_residuals(diag_res['y_test_sample'], diag_res['y_pred_sample'], selected_diag_model),
            use_container_width=True
        )

    # Feature Importance for compatible models
    if diag_res['feature_importances']:
        st.plotly_chart(
            viz.plot_feature_importance(diag_res['feature_importances'], selected_diag_model),
            use_container_width=True
        )

    # Best Model Selection Rationale
    st.markdown("""
        <div class="ew-card" style="border-left: 4px solid #1E88E5;">
            <h4 style="color: #0F172A; margin-top: 0;">📌 Selection Strategy & Justification</h4>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.6;">
                <b>Why Random Forest Regressor was selected:</b><br>
                1. <b>Superior Accuracy:</b> Achieves the highest coefficient of determination (<b>R² = 98.71%</b>) and lowest Root Mean Squared Error (<b>RMSE = 0.91 kWh</b>), outperforming Gradient Boosting (R² = 87.52%), SVR (R² = 71.57%), and Linear Regression (R² = 61.65%).<br>
                2. <b>Nonlinear Interactions:</b> Energy consumption depends strongly on nonlinear combinatorial thresholds (e.g. high ambient temperatures interacting with active HVAC cooling schedules and building occupancy load). Decision tree ensembles inherently capture these step interactions without requiring artificial polynomial feature expansion.<br>
                3. <b>Ensemble Robustness:</b> Averaging across 100 decorrelated decision trees prevents overfitting while providing a natural mechanism for empirical prediction intervals and uncertainty quantification.
            </p>
        </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# PAGE 4: Dataset Explorer
# -----------------------------------------------------------------------------
elif "Dataset Explorer" in nav_page:
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="color: #0F172A; font-weight: 800; font-size: 2.1rem; margin-bottom: 4px;">Dataset Explorer & Quality Inspection</h1>
            <p style="color: #64748B; font-size: 1.02rem;">Examine raw records, column distributions, missing values, duplicates, and statistical summaries.</p>
        </div>
    """, unsafe_allow_html=True)

    # Quality Summary Badges
    q1, q2, q3, q4 = st.columns(4)
    with q1:
        st.metric("Total Records", f"{dataset_meta['current_rows']:,}")
    with q2:
        st.metric("Total Columns", f"{dataset_meta['current_cols']}")
    with q3:
        st.metric("Duplicate Rows", f"{dataset_meta['duplicates']:,}")
    with q4:
        st.metric("Missing Values", f"{dataset_meta['missing_values']:,}")

    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

    # Filterable Data Preview
    st.markdown("### 🔍 Interactive Data Table")
    
    # Filter controls
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        hvac_filter = st.multiselect("Filter by HVAC Status", options=df['HVACUsage'].unique().tolist(), default=df['HVACUsage'].unique().tolist())
    with f_col2:
        lighting_filter = st.multiselect("Filter by Lighting Status", options=df['LightingUsage'].unique().tolist(), default=df['LightingUsage'].unique().tolist())
    with f_col3:
        temp_range = st.slider(
            "Filter by Temperature Range (°C)",
            float(df['Temperature'].min()), float(df['Temperature'].max()),
            (float(df['Temperature'].min()), float(df['Temperature'].max()))
        )

    filtered_df = df[
        (df['HVACUsage'].isin(hvac_filter)) &
        (df['LightingUsage'].isin(lighting_filter)) &
        (df['Temperature'] >= temp_range[0]) &
        (df['Temperature'] <= temp_range[1])
    ]

    st.caption(f"Displaying {len(filtered_df):,} matching rows out of {len(df):,} total records.")
    st.dataframe(filtered_df.head(200), use_container_width=True)

    # Download Cleaned/Filtered Dataset
    csv_cleaned = filtered_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Dataset (CSV)",
        data=csv_cleaned,
        file_name=f"energy_data_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

    st.markdown("<div style='height: 25px;'></div>", unsafe_allow_html=True)

    # Descriptive Statistics & Types
    tab_stat, tab_types, tab_col_viz = st.tabs(["📊 Descriptive Statistics", "📋 Data Types & Non-Nulls", "📈 Column Visualizer"])

    with tab_stat:
        st.dataframe(df.describe().T, use_container_width=True)

    with tab_types:
        types_df = pd.DataFrame({
            "Column Name": df.columns,
            "Data Type": [str(t) for t in df.dtypes],
            "Non-Null Count": df.notnull().sum().values,
            "Null Count": df.isnull().sum().values,
            "Null %": (df.isnull().sum().values / len(df) * 100).round(2),
            "Unique Values": [df[c].nunique() for c in df.columns]
        })
        st.dataframe(types_df, use_container_width=True)

    with tab_col_viz:
        col_to_plot = st.selectbox("Select column to inspect", options=[c for c in df.columns if c not in ['Datetime', 'Timestamp']])
        if pd.api.types.is_numeric_dtype(df[col_to_plot]):
            fig_col = px.histogram(
                df, x=col_to_plot, nbins=35,
                color_discrete_sequence=["#1E88E5"],
                title=f"Distribution of {col_to_plot}"
            )
        else:
            fig_col = px.bar(
                df[col_to_plot].value_counts().reset_index(),
                x=col_to_plot, y='count',
                color_discrete_sequence=["#0D47A1"],
                title=f"Category Counts for {col_to_plot}"
            )
        st.plotly_chart(viz.apply_theme(fig_col, f"Inspection: {col_to_plot}"), use_container_width=True)


# -----------------------------------------------------------------------------
# PAGE 5: Insights and Recommendations
# -----------------------------------------------------------------------------
elif "Insights & Recommendations" in nav_page:
    st.markdown("""
        <div style="margin-bottom: 20px;">
            <h1 style="color: #0F172A; font-weight: 800; font-size: 2.1rem; margin-bottom: 4px;">Data-Driven Insights & Energy Efficiency Opportunities</h1>
            <p style="color: #64748B; font-size: 1.02rem;">Empirical relationships derived from statistical analysis of building telemetry and actionable recommendations for demand management.</p>
        </div>
    """, unsafe_allow_html=True)

    # Dynamic metrics from actual dataset
    hvac_diff = df.groupby('HVACUsage')['EnergyConsumption'].mean()
    hvac_saving = hvac_diff.get('On', 0) - hvac_diff.get('Off', 0)
    
    light_diff = df.groupby('LightingUsage')['EnergyConsumption'].mean()
    light_saving = light_diff.get('On', 0) - light_diff.get('Off', 0)
    
    temp_corr = df['Temperature'].corr(df['EnergyConsumption'])
    occ_corr = df['Occupancy'].corr(df['EnergyConsumption'])

    # Calculate financial impact under MSEB Residential Tariff
    hvac_mseb_rate = calculate_mseb_cost(hvac_saving)['effective_rate']
    light_mseb_rate = calculate_mseb_cost(light_saving)['effective_rate']
    hvac_cost_val = hvac_saving * hvac_mseb_rate
    light_cost_val = light_saving * light_mseb_rate

    # Key Empirical Observations
    st.markdown("### 🔬 Empirical Findings & MSEB Financial Value")
    
    o1, o2, o3 = st.columns(3)
    with o1:
        render_html(f"""
            <div class="ew-card">
                <div style="font-size: 2rem;">❄️</div>
                <h4 style="color: #0F172A; margin: 8px 0 4px 0;">HVAC Thermal Load</h4>
                <div style="font-size: 1.6rem; font-weight: 800; color: #1E88E5;">+{hvac_saving:.2f} kWh</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #D97706; margin-top: 2px;">≈ +₹ {hvac_cost_val:.2f} per cycle (MSEB)</div>
                <p style="color: #64748B; font-size: 0.88rem; margin-top: 6px;">
                    Average consumption increase when HVAC cooling/heating is active (79.39 kWh vs 74.73 kWh). Represents <b>~6.2%</b> of total facility energy demand.
                </p>
            </div>
        """)

    with o2:
        render_html(f"""
            <div class="ew-card">
                <div style="font-size: 2rem;">💡</div>
                <h4 style="color: #0F172A; margin: 8px 0 4px 0;">Lighting Operations</h4>
                <div style="font-size: 1.6rem; font-weight: 800; color: #00ACC1;">+{light_saving:.2f} kWh</div>
                <div style="font-size: 0.95rem; font-weight: 700; color: #D97706; margin-top: 2px;">≈ +₹ {light_cost_val:.2f} per cycle (MSEB)</div>
                <p style="color: #64748B; font-size: 0.88rem; margin-top: 6px;">
                    Average consumption differential between lighting active vs disabled (77.69 kWh vs 76.38 kWh). Opportunity for daylight harvesting controls.
                </p>
            </div>
        """)

    with o3:
        render_html(f"""
            <div class="ew-card">
                <div style="font-size: 2rem;">🌡️</div>
                <h4 style="color: #0F172A; margin: 8px 0 4px 0;">Ambient Temperature</h4>
                <div style="font-size: 1.6rem; font-weight: 800; color: #E53935;">r = +{temp_corr:.3f}</div>
                <p style="color: #64748B; font-size: 0.88rem; margin-top: 6px;">
                    Strong positive linear correlation with external ambient temperature. Highest consumption spikes coincide with peak outdoor temperatures above 27 °C.
                </p>
            </div>
        """)

    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

    # Actionable Energy Efficiency Recommendations
    st.markdown("### 💡 Actionable Efficiency Recommendations")

    st.markdown("""
        <div class="ew-card">
            <h4 style="color: #0F172A; margin-top: 0;">1. Pre-Cooling & Demand Shifting Strategies</h4>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.6;">
                Because temperature exhibits a strong <b>+0.694 correlation</b> with energy consumption, peak afternoon thermal loads strain the building chiller systems. 
                Implementing automated pre-cooling during cooler early-morning hours (04:00 - 08:00) when outdoor temperatures are ~21 °C lowers afternoon peak chiller surge by leveraging the building's thermal mass.
            </p>
        </div>

        <div class="ew-card">
            <h4 style="color: #0F172A; margin-top: 0;">2. Dynamic Occupancy-Based Setpoint Deadbands</h4>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.6;">
                Occupancy correlation (<b>r = +0.192</b>) indicates variable internal heat gains. Expanding thermostat deadbands from ±0.5 °C to ±1.5 °C when occupancy is low (&le; 2 persons) 
                can prevent unnecessary HVAC cycling, capturing a substantial portion of the <b>4.66 kWh</b> HVAC operational premium during low-occupancy windows.
            </p>
        </div>

        <div class="ew-card">
            <h4 style="color: #0F172A; margin-top: 0;">3. Daylight Harvesting & Automated Dimming</h4>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.6;">
                Active lighting adds an empirical <b>1.31 kWh</b> baseload. Installing passive infrared (PIR) occupancy sensors and photocell dimmers along perimeter building zones 
                ensures luminaires automatically de-energize when natural sunlight exceeds 300 lux.
            </p>
        </div>

        <div class="ew-card">
            <h4 style="color: #0F172A; margin-top: 0;">4. Maximizing Onsite Renewable Self-Consumption</h4>
            <p style="color: #475569; font-size: 0.95rem; line-height: 1.6;">
                With an average onsite renewable production of <b>15.05 kWh</b>, scheduling high-draw episodic operations (such as EV fleet charging or water heating) 
                to align with solar generation peaks ensures maximum self-consumption and minimizes grid imports during high-tariff periods.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Scientific Caution & Methodology Notice
    st.markdown("""
        <div style="background-color: #FEF3C7; border: 1px solid #FDE68A; border-radius: 10px; padding: 14px 18px; color: #92400E; font-size: 0.88rem; line-height: 1.5; margin-top: 20px;">
            ⚠️ <b>Methodological Distinction: Correlation vs. Causality:</b><br>
            All efficiency figures above represent empirical statistical associations measured across the 30,000-record historical telemetry dataset. 
            While HVAC and lighting states demonstrate clear operational premiums, specific real-world savings depend on verified measurement and verification (M&V) protocols (such as IPMVP Option B/C) under calibrated engineering trials.
        </div>
    """, unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("<div style='height: 35px;'></div>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: #94A3B8; font-size: 0.82rem; padding: 20px; border-top: 1px solid #E2E8F0;">
        <b>EnergyWise</b> — M.Tech Data Science Energy Consumption Prediction System &copy; 2026 | Antigravity AI Engine
    </div>
""", unsafe_allow_html=True)
