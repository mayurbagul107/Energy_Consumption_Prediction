"""
visualization.py
Provides high-polish Plotly interactive visualizations for EnergyWise.
Adheres to Light Modern Theme (white cards, clean light blue/navy accents, smooth typography).
"""

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List

# Cohesive modern color palette
COLOR_PRIMARY = "#1E88E5"      # Vivid Blue
COLOR_SECONDARY = "#0D47A1"    # Deep Navy
COLOR_ACCENT = "#00ACC1"       # Cyan
COLOR_SUCCESS = "#43A047"      # Emerald Green
COLOR_WARNING = "#FB8C00"      # Amber Orange
COLOR_DANGER = "#E53935"       # Coral Red
COLOR_NEUTRAL_DARK = "#1E293B" # Slate 800
COLOR_GRID = "#E2E8F0"         # Slate 200

TEMPLATE_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(255,255,255,0.9)",
    font=dict(family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif", color=COLOR_NEUTRAL_DARK),
    margin=dict(l=40, r=30, t=50, b=40),
    xaxis=dict(showgrid=True, gridcolor=COLOR_GRID, linecolor="#CBD5E1", tickfont=dict(size=12)),
    yaxis=dict(showgrid=True, gridcolor=COLOR_GRID, linecolor="#CBD5E1", tickfont=dict(size=12)),
    legend=dict(
        bgcolor="rgba(255,255,255,0.8)",
        bordercolor="#E2E8F0",
        borderwidth=1,
        font=dict(size=11)
    )
)


def apply_theme(fig: go.Figure, title: str = "", height: int = 420) -> go.Figure:
    """Applies cohesive styling, borders, and margins to any Plotly figure."""
    fig.update_layout(
        **TEMPLATE_LAYOUT,
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(size=16, color=COLOR_SECONDARY),
            x=0.02,
            y=0.96
        ),
        height=height
    )
    return fig


# -------------------------------------------------------------------------
# Page 1: Overview Dashboard Visualizations
# -------------------------------------------------------------------------

def plot_energy_distribution(df: pd.DataFrame) -> go.Figure:
    """Histogram & KDE curve of Energy Consumption."""
    fig = px.histogram(
        df,
        x="EnergyConsumption",
        nbins=45,
        marginal="box",
        color_discrete_sequence=[COLOR_PRIMARY],
        opacity=0.85,
        labels={"EnergyConsumption": "Energy Consumption (kWh)"}
    )
    mean_val = df["EnergyConsumption"].mean()
    median_val = df["EnergyConsumption"].median()

    fig.add_vline(
        x=mean_val, line_dash="dash", line_color=COLOR_DANGER, line_width=2,
        annotation_text=f"Mean: {mean_val:.2f} kWh", annotation_position="top left",
        annotation_font=dict(color=COLOR_DANGER, size=11)
    )
    fig.add_vline(
        x=median_val, line_dash="dot", line_color=COLOR_SUCCESS, line_width=2,
        annotation_text=f"Median: {median_val:.2f} kWh", annotation_position="top right",
        annotation_font=dict(color=COLOR_SUCCESS, size=11)
    )
    return apply_theme(fig, "Energy Consumption Distribution (kWh)")


def plot_energy_trend(df: pd.DataFrame) -> go.Figure:
    """Time-series trend of energy consumption over time."""
    if "Datetime" in df.columns:
        # Sample or aggregate daily for smooth interactive rendering
        daily_df = df.set_index("Datetime").resample("D")["EnergyConsumption"].agg(["mean", "min", "max"]).reset_index()
        fig = go.Figure()
        
        # Max-min range ribbon
        fig.add_trace(go.Scatter(
            x=daily_df["Datetime"], y=daily_df["max"],
            mode="lines", line=dict(width=0), showlegend=False
        ))
        fig.add_trace(go.Scatter(
            x=daily_df["Datetime"], y=daily_df["min"],
            mode="lines", line=dict(width=0), fill="tonexty",
            fillcolor="rgba(30, 136, 229, 0.15)", name="Daily Range (Min-Max)"
        ))
        # Daily Mean line
        fig.add_trace(go.Scatter(
            x=daily_df["Datetime"], y=daily_df["mean"],
            mode="lines", line=dict(color=COLOR_PRIMARY, width=2.2), name="Daily Average"
        ))
        
        # 30-day moving average
        daily_df["MA30"] = daily_df["mean"].rolling(30).mean()
        fig.add_trace(go.Scatter(
            x=daily_df["Datetime"], y=daily_df["MA30"],
            mode="lines", line=dict(color=COLOR_WARNING, width=2.5, dash="dash"), name="30-Day Moving Avg"
        ))
        
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all", label="All")
                ])
            )
        )
        return apply_theme(fig, "Energy Consumption Trend Over Time (Aggregated Daily)")
    else:
        # Fallback index line plot
        sample_df = df.iloc[:1000].reset_index()
        fig = px.line(
            sample_df, x="index", y="EnergyConsumption",
            color_discrete_sequence=[COLOR_PRIMARY],
            labels={"index": "Record Index", "EnergyConsumption": "Energy Consumption (kWh)"}
        )
        return apply_theme(fig, "Energy Consumption Sequence (Sampled Records)")


def plot_temperature_vs_energy(df: pd.DataFrame) -> go.Figure:
    """Scatter plot with trendline showing Temperature vs Energy Consumption."""
    sample_df = df.sample(min(3000, len(df)), random_state=42)
    fig = px.scatter(
        sample_df,
        x="Temperature",
        y="EnergyConsumption",
        color="HVACUsage",
        color_discrete_map={"On": COLOR_PRIMARY, "Off": "#94A3B8"},
        opacity=0.65,
        trendline="ols",
        labels={"Temperature": "Ambient Temperature (°C)", "EnergyConsumption": "Energy Consumption (kWh)"}
    )
    return apply_theme(fig, "Temperature vs. Energy Consumption (with HVAC Status)")


def plot_occupancy_vs_energy(df: pd.DataFrame) -> go.Figure:
    """Box plot showing Energy Consumption by Occupancy Level."""
    fig = px.box(
        df,
        x="Occupancy",
        y="EnergyConsumption",
        color="Occupancy",
        color_discrete_sequence=px.colors.qualitative.Prism,
        labels={"Occupancy": "Occupancy (Persons)", "EnergyConsumption": "Energy Consumption (kWh)"}
    )
    fig.update_layout(showlegend=False)
    return apply_theme(fig, "Energy Consumption by Occupancy Level")


def plot_hvac_comparison(df: pd.DataFrame) -> go.Figure:
    """Box/Violin plot comparing HVAC On vs HVAC Off."""
    fig = px.violin(
        df,
        x="HVACUsage",
        y="EnergyConsumption",
        color="HVACUsage",
        box=True,
        points=False,
        color_discrete_map={"On": COLOR_PRIMARY, "Off": "#64748B"},
        labels={"HVACUsage": "HVAC Status", "EnergyConsumption": "Energy Consumption (kWh)"}
    )
    return apply_theme(fig, "HVAC System Impact on Energy Consumption")


def plot_lighting_comparison(df: pd.DataFrame) -> go.Figure:
    """Bar/Box plot comparing Lighting Usage."""
    fig = px.box(
        df,
        x="LightingUsage",
        y="EnergyConsumption",
        color="LightingUsage",
        color_discrete_map={"On": COLOR_ACCENT, "Off": "#94A3B8"},
        labels={"LightingUsage": "Lighting Status", "EnergyConsumption": "Energy Consumption (kWh)"}
    )
    return apply_theme(fig, "Lighting Usage Impact on Energy Consumption")


def plot_day_of_week_comparison(df: pd.DataFrame) -> go.Figure:
    """Bar chart with average energy consumption across Days of the Week."""
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    grouped = df.groupby('DayOfWeek')['EnergyConsumption'].agg(['mean', 'std', 'count']).reindex(day_order).reset_index()
    
    fig = px.bar(
        grouped,
        x='DayOfWeek',
        y='mean',
        error_y='std',
        color='mean',
        color_continuous_scale='Blues',
        labels={'DayOfWeek': 'Day of Week', 'mean': 'Avg Energy Consumption (kWh)'}
    )
    fig.update_coloraxes(showscale=False)
    fig.update_yaxes(range=[grouped['mean'].min() - 5, grouped['mean'].max() + 5])
    return apply_theme(fig, "Average Energy Consumption by Day of Week")


def plot_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Interactive correlation heatmap for all numerical features."""
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Filter out pure index or ID cols if present
    num_cols = [c for c in num_cols if c not in ['index', 'id', 'IsSynthetic']]
    corr = df[num_cols].corr()

    fig = go.Figure(data=go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        colorscale="Blues",
        zmin=-1, zmax=1,
        text=np.round(corr.values, 2),
        texttemplate="%{text}",
        textfont=dict(size=12, color=COLOR_NEUTRAL_DARK),
        hoverongaps=False
    ))
    return apply_theme(fig, "Feature Correlation Heatmap", height=460)


# -------------------------------------------------------------------------
# Page 3: Model Performance Visualizations
# -------------------------------------------------------------------------

def plot_model_comparison(results: Dict[str, Dict[str, Any]]) -> go.Figure:
    """Grouped bar chart comparing R2, MAE, and RMSE across all trained models."""
    models = list(results.keys())
    r2_scores = [results[m]['r2'] for m in models]
    mae_scores = [results[m]['mae'] for m in models]
    rmse_scores = [results[m]['rmse'] for m in models]

    fig = go.Figure(data=[
        go.Bar(name='R² Score', x=models, y=r2_scores, marker_color=COLOR_PRIMARY, text=[f"{v:.3f}" for v in r2_scores], textposition='auto'),
        go.Bar(name='MAE (kWh)', x=models, y=mae_scores, marker_color=COLOR_WARNING, text=[f"{v:.2f}" for v in mae_scores], textposition='auto'),
        go.Bar(name='RMSE (kWh)', x=models, y=rmse_scores, marker_color=COLOR_DANGER, text=[f"{v:.2f}" for v in rmse_scores], textposition='auto'),
    ])
    fig.update_layout(barmode='group')
    return apply_theme(fig, "Model Performance Comparison (Test Dataset)")


def plot_actual_vs_predicted(y_true: List[float], y_pred: List[float], model_name: str) -> go.Figure:
    """Scatter plot of actual vs predicted values with reference diagonal."""
    df_plot = pd.DataFrame({"Actual": y_true, "Predicted": y_pred})
    min_val = min(min(y_true), min(y_pred))
    max_val = max(max(y_true), max(y_pred))

    fig = px.scatter(
        df_plot,
        x="Actual",
        y="Predicted",
        opacity=0.6,
        color_discrete_sequence=[COLOR_PRIMARY],
        labels={"Actual": "Actual Energy Consumption (kWh)", "Predicted": "Predicted Energy Consumption (kWh)"}
    )
    # Perfect fit reference line
    fig.add_trace(go.Scatter(
        x=[min_val, max_val], y=[min_val, max_val],
        mode="lines", line=dict(color=COLOR_DANGER, dash="dash", width=2.5),
        name="Ideal Perfect Fit (y = x)"
    ))
    return apply_theme(fig, f"Actual vs. Predicted Consumption — {model_name}")


def plot_residuals(y_true: List[float], y_pred: List[float], model_name: str) -> go.Figure:
    """Residual plot (Residuals = Actual - Predicted) vs Predicted values."""
    residuals = np.array(y_true) - np.array(y_pred)
    df_res = pd.DataFrame({"Predicted": y_pred, "Residuals": residuals})

    fig = px.scatter(
        df_res,
        x="Predicted",
        y="Residuals",
        opacity=0.6,
        color_discrete_sequence=[COLOR_SECONDARY],
        labels={"Predicted": "Predicted Energy Consumption (kWh)", "Residuals": "Residual Error (kWh)"}
    )
    fig.add_hline(
        y=0, line_dash="dash", line_color=COLOR_DANGER, line_width=2,
        annotation_text="Zero Residual Line", annotation_position="bottom right"
    )
    return apply_theme(fig, f"Residual Plot — {model_name}")


def plot_feature_importance(feature_importances: Dict[str, float], model_name: str) -> go.Figure:
    """Horizontal bar chart of top features by predictive importance."""
    if not feature_importances:
        fig = go.Figure()
        fig.add_annotation(text="Feature importances not applicable for this linear kernel model.", showarrow=False)
        return apply_theme(fig, f"Feature Importance — {model_name}")

    df_fi = pd.DataFrame(list(feature_importances.items()), columns=['Feature', 'Importance'])
    df_fi = df_fi.sort_values(by='Importance', ascending=True)

    fig = px.bar(
        df_fi,
        x='Importance',
        y='Feature',
        orientation='h',
        color='Importance',
        color_continuous_scale='Blues',
        labels={'Importance': 'Relative Importance / Weight', 'Feature': 'Predictive Feature'}
    )
    fig.update_coloraxes(showscale=False)
    return apply_theme(fig, f"Feature Importance Ranking — {model_name}")


def plot_daily_24h_profile(hourly_df: pd.DataFrame, target_date_str: str) -> go.Figure:
    """
    Renders an interactive 24-hour diurnal load curve showing hourly predicted electricity
    consumption (kWh) and renewable energy generation across the single target day.
    """
    fig = go.Figure()

    # Predicted hourly consumption line with smooth gradient fill
    fig.add_trace(go.Scatter(
        x=hourly_df['Time'],
        y=hourly_df['Predicted_kWh'],
        mode='lines+markers',
        name='Predicted Consumption (kWh)',
        line=dict(color=COLOR_PRIMARY, width=3),
        marker=dict(size=6, color=COLOR_SECONDARY),
        fill='tozeroy',
        fillcolor='rgba(30, 136, 229, 0.12)'
    ))

    # Onsite Renewable solar generation bar if present
    if 'RenewableEnergy' in hourly_df.columns and hourly_df['RenewableEnergy'].sum() > 0:
        fig.add_trace(go.Bar(
            x=hourly_df['Time'],
            y=hourly_df['RenewableEnergy'],
            name='Solar / Renewable (kWh)',
            marker_color='rgba(67, 160, 71, 0.4)',
            opacity=0.6
        ))

    # Highlight peak hour and baseload hour
    peak_idx = hourly_df['Predicted_kWh'].idxmax()
    peak_row = hourly_df.loc[peak_idx]

    fig.add_annotation(
        x=peak_row['Time'], y=peak_row['Predicted_kWh'],
        text=f"Peak: {peak_row['Predicted_kWh']:.1f} kWh ({peak_row['Time']})",
        showarrow=True, arrowhead=2, arrowcolor=COLOR_DANGER,
        font=dict(size=11, color=COLOR_DANGER),
        bgcolor="white", bordercolor=COLOR_DANGER, borderwidth=1
    )

    fig.update_layout(
        xaxis=dict(title="Hour of Day (24-Hour Cycle)", tickangle=-45),
        yaxis=dict(title="Hourly Consumption (kWh)"),
        hovermode="x unified"
    )

    return apply_theme(fig, f"24-Hour Electricity Consumption Profile — {target_date_str}")


def plot_monthly_daily_trend(daily_summary_df: pd.DataFrame, month_name: str) -> go.Figure:
    """
    Renders an interactive monthly daily load profile showing daily electricity consumption (kWh)
    across all calendar days of the month, highlighting weekdays vs weekends, solar offset,
    and the monthly daily average baseline.
    """
    fig = go.Figure()

    # Differentiate weekend vs weekday bars
    bar_colors = [
        "rgba(245, 158, 11, 0.85)" if d in ['Saturday', 'Sunday'] else "rgba(30, 136, 229, 0.85)"
        for d in daily_summary_df['DayOfWeek']
    ]

    # Daily consumption bar
    fig.add_trace(go.Bar(
        x=[f"Day {r['Day']} ({r['DayOfWeek'][:3]})" for _, r in daily_summary_df.iterrows()],
        y=daily_summary_df['Daily_kWh'],
        name='Daily Consumption (kWh)',
        marker_color=bar_colors,
        hovertemplate="<b>%{x}</b><br>Consumption: <b>%{y:.2f} kWh</b><extra></extra>"
    ))

    # Solar PV generation bar if present
    if 'Solar_kWh' in daily_summary_df.columns and daily_summary_df['Solar_kWh'].sum() > 0:
        fig.add_trace(go.Bar(
            x=[f"Day {r['Day']} ({r['DayOfWeek'][:3]})" for _, r in daily_summary_df.iterrows()],
            y=daily_summary_df['Solar_kWh'],
            name='Solar Generation (kWh)',
            marker_color='rgba(67, 160, 71, 0.45)',
            hovertemplate="<b>%{x}</b><br>Solar Offset: <b>%{y:.2f} kWh</b><extra></extra>"
        ))

    # Average daily consumption line
    avg_daily = daily_summary_df['Daily_kWh'].mean()
    fig.add_hline(
        y=avg_daily,
        line_dash="dot",
        line_color=COLOR_SECONDARY,
        line_width=2,
        annotation_text=f"Daily Avg: {avg_daily:.1f} kWh",
        annotation_position="top left",
        annotation_font=dict(size=11, color=COLOR_SECONDARY)
    )

    # Highlight peak day
    peak_idx = daily_summary_df['Daily_kWh'].idxmax()
    peak_row = daily_summary_df.loc[peak_idx]
    peak_x = f"Day {peak_row['Day']} ({peak_row['DayOfWeek'][:3]})"

    fig.add_annotation(
        x=peak_x, y=peak_row['Daily_kWh'],
        text=f"Peak Day: {peak_row['Daily_kWh']:.1f} kWh",
        showarrow=True, arrowhead=2, arrowcolor=COLOR_DANGER,
        font=dict(size=11, color=COLOR_DANGER),
        bgcolor="white", bordercolor=COLOR_DANGER, borderwidth=1
    )

    fig.update_layout(
        xaxis=dict(title="Calendar Day of Month", tickangle=-45),
        yaxis=dict(title="Daily Electricity Consumption (kWh)"),
        barmode='group',
        hovermode="x unified"
    )

    return apply_theme(fig, f"Daily Electricity Consumption Trend Across {month_name}")


def plot_msedcl_bill_breakdown(bill: Dict[str, Any]) -> go.Figure:
    """
    Renders an interactive donut chart illustrating the itemized cost breakdown of the MSEDCL bill:
    Energy Charges, Wheeling Charges, Fixed Charges, Fuel Adjustment Charges (FAC), Electricity Duty (16%),
    and Municipal Charge.
    """
    labels = [
        "Energy Charges",
        "Wheeling Charges",
        "Fixed Demand Charges",
        "FAC Surcharge",
        "Electricity Duty (16%)",
        "Municipal Charge"
    ]
    values = [
        max(0.0, float(bill.get("energy_charge", 0.0))),
        max(0.0, float(bill.get("wheeling_charge", 0.0))),
        max(0.0, float(bill.get("fixed_charge", 0.0))),
        max(0.0, float(bill.get("fac_charge", 0.0))),
        max(0.0, float(bill.get("ed_charge", 0.0))),
        max(0.0, float(bill.get("municipal_charge", 0.0))),
    ]
    colors = ["#1E88E5", "#00ACC1", "#8E24AA", "#FB8C00", "#E53935", "#43A047"]

    # Filter out 0 value entries for clean display
    plot_labels, plot_vals, plot_colors = [], [], []
    for l, v, c in zip(labels, values, colors):
        if v > 0:
            plot_labels.append(l)
            plot_vals.append(v)
            plot_colors.append(c)

    total_amt = bill.get("total_estimated_bill", sum(values))
    fig = go.Figure(data=[go.Pie(
        labels=plot_labels,
        values=plot_vals,
        hole=0.55,
        marker=dict(colors=plot_colors, line=dict(color='#FFFFFF', width=2)),
        textinfo='label+percent',
        hoverinfo='label+value+percent',
        hovertemplate="<b>%{label}</b><br>Amount: <b>₹ %{value:,.2f}</b><br>Share: <b>%{percent}</b><extra></extra>"
    )])

    fig.update_layout(
        annotations=[dict(
            text=f"<b>Total</b><br>₹{total_amt:,.0f}",
            x=0.5, y=0.5,
            font_size=15,
            font_color=COLOR_NEUTRAL_DARK,
            showarrow=False
        )],
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
    )
    return apply_theme(fig, "Estimated MSEDCL Bill Cost Composition", height=420)


def plot_slab_distribution(slab_breakdown: List[Dict[str, Any]]) -> go.Figure:
    """
    Renders a grouped bar chart showing progressive slab units consumed and energy charges in each slab.
    """
    labels = [s["slab_label"] for s in slab_breakdown]
    units = [s["units"] for s in slab_breakdown]
    costs = [s["cost"] for s in slab_breakdown]

    fig = go.Figure(data=[
        go.Bar(
            name='Units in Slab (kWh)',
            x=labels,
            y=units,
            marker_color=COLOR_PRIMARY,
            text=[f"{u:,.1f} kWh" if u > 0 else "0" for u in units],
            textposition='auto',
            hovertemplate="<b>%{x}</b><br>Units: <b>%{y:,.2f} kWh</b><extra></extra>"
        ),
        go.Bar(
            name='Energy Charge (₹)',
            x=labels,
            y=costs,
            marker_color=COLOR_WARNING,
            text=[f"₹{c:,.1f}" if c > 0 else "₹0" for c in costs],
            textposition='auto',
            hovertemplate="<b>%{x}</b><br>Charge: <b>₹ %{y:,.2f}</b><extra></extra>"
        )
    ])
    fig.update_layout(
        barmode='group',
        xaxis=dict(title="Progressive Tariff Slab Tier"),
        yaxis=dict(title="Units / Cost (₹)"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.25, xanchor="center", x=0.5)
    )
    return apply_theme(fig, "Progressive Slab Units & Energy Charges", height=420)


