"""
generate_dashboard_schematics.py
Creates crisp, professional UI schematics / layout representations
for Chapter 10 of the M.Tech Report.
"""

import os
import sys
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches

plt.rcParams['font.sans-serif'] = 'Arial'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'report_assets')
os.makedirs(ASSETS_DIR, exist_ok=True)

def draw_card(ax, x, y, w, h, title, content, bg_color="#FFFFFF", border_color="#CBD5E1", title_color="#0F172A"):
    box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.015,rounding_size=0.03",
                                 linewidth=1.2, edgecolor=border_color, facecolor=bg_color)
    ax.add_patch(box)
    if title:
        ax.text(x + 0.02, y + h - 0.05, title, fontsize=9.5, fontweight='bold', color=title_color, va='top')
    if content:
        ax.text(x + 0.02, y + h - 0.12, content, fontsize=8, color="#334155", va='top', linespacing=1.3)

# -------------------------------------------------------------------------
# Figure 10.1: Overview Dashboard Layout
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 6.5))
ax.axis('off')
ax.set_facecolor("#F8FAFC")
fig.patch.set_facecolor("#F8FAFC")

# Header
ax.text(0.04, 0.95, "EnergyWise — Overview Dashboard", fontsize=14, fontweight='bold', color="#0F172A")
ax.text(0.04, 0.90, "Machine Learning-Based Energy Analytics System | M.Tech Data Science Project", fontsize=9, color="#64748B")

# Sidebar representation
sidebar = patches.Rectangle((0.02, 0.04), 0.20, 0.82, facecolor="#FFFFFF", edgecolor="#E2E8F0", linewidth=1.2)
ax.add_patch(sidebar)
ax.text(0.04, 0.82, "⚡ EnergyWise", fontsize=11, fontweight='bold', color="#1E88E5")
ax.text(0.04, 0.77, "Navigation:", fontsize=8.5, fontweight='bold', color="#475569")
nav_items = ["● 📊 Overview", "○ 🔮 Predict Energy", "○ ⚡ MSEDCL Bill", "○ 📈 Model Eval", "○ 📁 Dataset Explorer", "○ 💡 Insights"]
for idx, item in enumerate(nav_items):
    color = "#1E88E5" if idx == 0 else "#64748B"
    ax.text(0.04, 0.72 - idx*0.045, item, fontsize=8, color=color, fontweight='bold' if idx==0 else 'normal')

ax.text(0.04, 0.42, "Dataset Selection:", fontsize=8, fontweight='bold', color="#475569")
ax.text(0.04, 0.38, "[Energy_Consumption_Virtual.csv]", fontsize=7.5, color="#0284C7")
ax.text(0.04, 0.34, "Records: 30,000", fontsize=7.5, color="#16A34A")

# KPI Summary Row
kpis = [
    ("TOTAL RECORDS", "30,000", "#1E88E5"),
    ("AVERAGE ENERGY", "77.02 kWh", "#0284C7"),
    ("PEAK DEMAND", "99.20 kWh", "#D97706"),
    ("BASELOAD DEMAND", "53.26 kWh", "#7C3AED"),
    ("CORE FEATURES", "9 Predictors", "#10B981")
]
for idx, (title, val, border_c) in enumerate(kpis):
    x = 0.25 + idx * 0.145
    box = patches.FancyBboxPatch((x, 0.74), 0.135, 0.12, boxstyle="round,pad=0.015,rounding_size=0.03",
                                 facecolor="#FFFFFF", edgecolor=border_c, linewidth=1.5)
    ax.add_patch(box)
    ax.text(x + 0.067, 0.82, title, fontsize=7, color="#64748B", fontweight='bold', ha='center')
    ax.text(x + 0.067, 0.77, val, fontsize=10.5, color="#0F172A", fontweight='bold', ha='center')

# Main Visualizations
draw_card(ax, 0.25, 0.39, 0.35, 0.32, "Plotly 1: Distribution Analysis",
          "• Dynamic Histogram (45 bins) & KDE curve\n• Vertical Dash line: Mean = 77.02 kWh\n• Vertical Dot line: Median = 76.88 kWh\n• Integrated upper boxplot for outlier audit",
          border_color="#1E88E5")

draw_card(ax, 0.62, 0.39, 0.35, 0.32, "Plotly 2: Time-Series Trend Over Time",
          "• Daily Aggregation with Min-Max range ribbon\n• 30-Day Rolling Moving Average trend\n• Dynamic Range Slider (1m, 6m, 1y, All)\n• Interactive zoom & pan toolbars",
          border_color="#0284C7")

draw_card(ax, 0.25, 0.04, 0.35, 0.32, "Plotly 3: Temperature vs. Energy (HVAC)",
          "• 2,500 point scatter plot\n• Dual OLS regression lines (HVAC On vs Off)\n• Clear demonstration of thermal slope\n• Hover tooltips with record metadata",
          border_color="#D97706")

draw_card(ax, 0.62, 0.04, 0.35, 0.32, "Plotly 4: Annotated Correlation Matrix",
          "• Heatmap of all 6 numeric variables\n• Strongest correlation: Temperature (+0.694)\n• Occupancy (+0.192), Renewable (+0.073)\n• Square footage baseline neutrality (r = -0.0003)",
          border_color="#10B981")

ax.set_title("Figure 10.1: Streamlit Dashboard UI Layout — Page 1: Overview Dashboard", fontsize=12, fontweight='bold', pad=12)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig(os.path.join(ASSETS_DIR, 'fig_10_1_overview_dashboard_ui.png'), dpi=300)
plt.close()
print("[OK] Saved Figure 10.1: Overview Dashboard UI")

# -------------------------------------------------------------------------
# Figure 10.2: Predict Energy Interface Layout
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 6.5))
ax.axis('off')
ax.set_facecolor("#F8FAFC")
fig.patch.set_facecolor("#F8FAFC")

ax.text(0.04, 0.95, "EnergyWise — Predict Energy & MSEDCL Estimated Bill", fontsize=14, fontweight='bold', color="#0F172A")
ax.text(0.04, 0.90, "Dual Prediction Horizon Engine (Monthly & Daily Profile) with Tree Ensemble Variance", fontsize=9, color="#64748B")

# Input Form Column
draw_card(ax, 0.04, 0.05, 0.44, 0.82, "Interactive Input Form & Configuration",
          "Prediction Horizon Mode:\n  (●) Monthly Prediction (Default)    (○) Daily 24-Hour Profile\n\n"
          "Target Calendar Month: April 2026 (720 Hours Simulation)\n\n"
          "Environmental & Physical Predictors:\n"
          "  • Ambient Temperature: [ 25.0 °C ] (Slider: 20.0 to 30.0)\n"
          "  • Relative Humidity: [ 45.0 % ] (Slider: 30.0 to 60.0)\n"
          "  • Square Footage: [ 1,500 sq ft ] (Range: 1,000 to 2,000)\n"
          "  • Occupancy Count: [ 5 persons ] (Range: 0 to 10)\n"
          "  • Onsite Renewable Generation: [ 15.0 kWh ] (0 to 30)\n"
          "  • HVAC Operating Status: [ On ▼ ]\n"
          "  • Lighting Status: [ On ▼ ]\n"
          "  • Connection Type: [ Single Phase (₹130/mo) ▼ ]\n\n"
          "[  🔮 RUN MACHINE LEARNING PREDICTION  ]",
          border_color="#1E88E5", bg_color="#FFFFFF")

# Output Section
draw_card(ax, 0.51, 0.55, 0.45, 0.32, "Standardized 4-Component Metric Summary",
          "• DAILY CONSUMPTION: 77.02 kWh / day\n"
          "• MONTHLY CONSUMPTION: 2,310.60 kWh / month\n"
          "• ESTIMATED DAILY COST: ₹ 1,668.99 / day\n"
          "• ESTIMATED MONTHLY BILL: ₹ 50,069.80 / month\n\n"
          "Model Confidence (90% CI): [ 75.52 kWh — 78.52 kWh ]\n"
          "Ensemble Standard Error: ± 0.91 kWh",
          border_color="#16A34A", bg_color="#F0FDF4")

draw_card(ax, 0.51, 0.05, 0.45, 0.46, "MSEDCL Official Estimated Bill Notice & Diagnostics",
          "⚠️ OFFICIAL ESTIMATED BILL NOTICE:\n"
          "• Calculated strictly in accordance with MERC Domestic Tariff Order\n"
          "  LT-I category applicable from 1 April 2026.\n"
          "• Telescopic slab energy charges: ₹ 37,869.82\n"
          "• Wheeling charges (@ ₹1.60/kWh): ₹ 3,696.96\n"
          "• Fixed demand charge: ₹ 130.00\n"
          "• Fuel Adjustment Charge (FAC @ ₹0.65): ₹ 1,501.89\n"
          "• Statutory Maharashtra Electricity Duty (16%): ₹ 6,911.79\n"
          "• Additional Municipal Charge: ₹ 10.00\n"
          "• Total Estimated Bill: ₹ 50,069.80 (Effective Rate: ₹21.67/kWh)",
          border_color="#D97706", bg_color="#FFFBEB")

ax.set_title("Figure 10.2: Streamlit Dashboard UI Layout — Page 2: Predict Energy Interface", fontsize=12, fontweight='bold', pad=12)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig(os.path.join(ASSETS_DIR, 'fig_10_2_predict_interface_ui.png'), dpi=300)
plt.close()
print("[OK] Saved Figure 10.2: Predict Interface UI")

# -------------------------------------------------------------------------
# Figure 10.3: MSEDCL Tariff Calculator Layout
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 6.5))
ax.axis('off')
ax.set_facecolor("#F8FAFC")
fig.patch.set_facecolor("#F8FAFC")

ax.text(0.04, 0.95, "EnergyWise — MSEDCL Domestic Bill Calculator (1 April 2026)", fontsize=14, fontweight='bold', color="#0F172A")
ax.text(0.04, 0.90, "Standalone Transparent Tariff Calculator with Progressive Slabs & Mathematical Audit Log", fontsize=9, color="#64748B")

draw_card(ax, 0.04, 0.50, 0.44, 0.37, "Tariff Parameters & One-Click Model Sync",
          "• Monthly Consumption: [ 200 kWh ]   [ 🔄 Sync with Model ]\n"
          "• Connection Type: Single Phase Standard (₹130/month)\n"
          "• Billing Period: April 2026 (Initial Tariff Order)\n"
          "• Wheeling Charge Rate: ₹ 1.60 / unit\n"
          "• Fuel Adjustment Charge (FAC): ₹ 0.65 / unit\n"
          "• Statutory Electricity Duty: 16.0%\n"
          "• Municipal Charge: ₹ 10.00 / month",
          border_color="#1E88E5")

draw_card(ax, 0.51, 0.50, 0.45, 0.37, "Progressive Telescopic Slab Breakdown",
          "• Slab 1 (1 – 100 units @ ₹3.96): 100.0 units = ₹ 396.00\n"
          "• Slab 2 (101 – 300 units @ ₹10.80): 100.0 units = ₹ 1,080.00\n"
          "• Slab 3 (301 – 500 units @ ₹15.03): 0.0 units = ₹ 0.00\n"
          "• Slab 4 (> 500 units @ ₹17.53): 0.0 units = ₹ 0.00\n"
          "---------------------------------------------------\n"
          "Total Energy Charges: ₹ 1,476.00",
          border_color="#16A34A")

draw_card(ax, 0.04, 0.05, 0.92, 0.41, "8-Step Mathematical Formula Audit Log (Complete Transparency)",
          "Step 1: Base Energy Charges (Telescopic Slabs) = ₹ 1,476.00\n"
          "Step 2: Wheeling Charges (200 units × ₹1.60) = ₹ 320.00\n"
          "Step 3: Fixed Demand Charges (Single Phase) = ₹ 130.00\n"
          "Step 4: Fuel Adjustment Charge (FAC = 200 units × ₹0.65) = ₹ 130.00\n"
          "Step 5: Applicable Charges Base for Duty = (Step 1 + Step 2 + Step 3 + Step 4) = ₹ 2,056.00\n"
          "Step 6: Statutory Maharashtra Electricity Duty (16.0% × ₹2,056.00) = ₹ 328.96\n"
          "Step 7: Additional Municipal Charge = ₹ 10.00\n"
          "Step 8: Final Estimated Monthly Bill = (Step 5 + Step 6 + Step 7) = ₹ 2,394.96  (Effective Rate: ₹11.97 / kWh)",
          border_color="#D97706", bg_color="#FFFFFF")

ax.set_title("Figure 10.3: Streamlit Dashboard UI Layout — Page 3: MSEDCL Bill Calculator", fontsize=12, fontweight='bold', pad=12)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig(os.path.join(ASSETS_DIR, 'fig_10_3_tariff_calculator_ui.png'), dpi=300)
plt.close()
print("[OK] Saved Figure 10.3: Tariff Calculator UI")

# -------------------------------------------------------------------------
# Figure 10.4: Model Performance Layout
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 6.5))
ax.axis('off')
ax.set_facecolor("#F8FAFC")
fig.patch.set_facecolor("#F8FAFC")

ax.text(0.04, 0.95, "EnergyWise — Model Performance & Evaluation Hub", fontsize=14, fontweight='bold', color="#0F172A")
ax.text(0.04, 0.90, "Empirical Benchmark on 20% Holdout Test Set (6,000 Records)", fontsize=9, color="#64748B")

draw_card(ax, 0.04, 0.50, 0.92, 0.37, "Comparative Evaluation Benchmark Table",
          "Model Algorithm              R² Score     MAE (kWh)    MSE (kWh²)   RMSE (kWh)   Status\n"
          "----------------------------------------------------------------------------------------\n"
          "Random Forest Regressor       0.9871       0.46         0.83         0.91         Selected Best Model 🏆\n"
          "Gradient Boosting Regressor   0.8752       2.20         8.00         2.83         Candidate Model\n"
          "Support Vector Regressor      0.7157       2.99        18.23         4.27         Candidate Model\n"
          "Linear Regression             0.6165       3.96        24.59         4.96         Baseline Model",
          border_color="#1E88E5")

draw_card(ax, 0.04, 0.05, 0.44, 0.41, "Visual Diagnostics & Plots",
          "• Grouped Performance Bar Charts (R², MAE, RMSE)\n"
          "• Actual vs Predicted Scatter (Identity line fit)\n"
          "• Residual Plot (Zero-centered error audit)\n"
          "• Retrain Models with Custom Hyperparameters Button",
          border_color="#16A34A")

draw_card(ax, 0.51, 0.05, 0.45, 0.41, "Feature Importance Hierarchy (Random Forest)",
          "1. Ambient Temperature: 53.54%\n"
          "2. Square Footage: 9.85%\n"
          "3. Renewable Generation: 8.88%\n"
          "4. HVAC Status (On): 8.18%\n"
          "5. Relative Humidity: 8.12%\n"
          "6. Occupancy Count: 7.92%\n"
          "7. Holiday (Yes): 1.92%\n"
          "8. Lighting Status (On): 1.54%",
          border_color="#7C3AED")

ax.set_title("Figure 10.4: Streamlit Dashboard UI Layout — Page 4: Model Performance Hub", fontsize=12, fontweight='bold', pad=12)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig(os.path.join(ASSETS_DIR, 'fig_10_4_model_performance_ui.png'), dpi=300)
plt.close()
print("[OK] Saved Figure 10.4: Model Performance UI")

# -------------------------------------------------------------------------
# Figure 10.5: Dataset Explorer Layout
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 6.5))
ax.axis('off')
ax.set_facecolor("#F8FAFC")
fig.patch.set_facecolor("#F8FAFC")

ax.text(0.04, 0.95, "EnergyWise — Dataset Explorer & Data Quality Inspection", fontsize=14, fontweight='bold', color="#0F172A")
ax.text(0.04, 0.90, "Real-Time Data Health Auditing, Multi-Criteria Filtering, and Export Utilities", fontsize=9, color="#64748B")

draw_card(ax, 0.04, 0.65, 0.92, 0.22, "Data Quality Verification Cards",
          "TOTAL ROWS: 30,000      TOTAL COLUMNS: 11      MISSING VALUES: 0 (0.00%)      DUPLICATES: 0 (0.00%)\n"
          "Data Types: 5 Float64 (Temp, Hum, SqFt, Renewable, Energy) | 1 Int64 (Occupancy) | 5 Object/Categorical\n"
          "Data Health Status: ALL INTEGRITY CHECKS PASSED [VERIFIED]",
          border_color="#16A34A", bg_color="#F0FDF4")

draw_card(ax, 0.04, 0.05, 0.92, 0.56, "Interactive Data Table & Multi-Criteria Filtering",
          "Filter Controls: [ HVAC: All ▼ ]  [ Lighting: All ▼ ]  [ Day: All ▼ ]  [ Temp Range: 20–30°C ]\n"
          "----------------------------------------------------------------------------------------------\n"
          "Timestamp         Temp(°C)  Humidity(%)  SqFt     Occupancy  HVAC  Light  Renewable  Energy(kWh)\n"
          "01-01-2022 00:00  25.14     43.43        1565.69  5          On    Off    2.77       78.43\n"
          "01-01-2022 01:00  27.73     54.23        1411.06  1          Off   On     21.83      82.15\n"
          "01-01-2022 02:00  28.70     58.91        1755.72  2          On    On     6.76       89.21\n"
          "01-01-2022 03:00  20.08     35.12        1102.34  0          Off   Off    12.45      55.10\n"
          "...\n"
          "[ 📥 Download Filtered Dataset as CSV ]",
          border_color="#0284C7")

ax.set_title("Figure 10.5: Streamlit Dashboard UI Layout — Page 5: Dataset Explorer", fontsize=12, fontweight='bold', pad=12)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig(os.path.join(ASSETS_DIR, 'fig_10_5_dataset_explorer_ui.png'), dpi=300)
plt.close()
print("[OK] Saved Figure 10.5: Dataset Explorer UI")

# -------------------------------------------------------------------------
# Figure 10.6: Insights & Recommendations Layout
# -------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(10.5, 6.5))
ax.axis('off')
ax.set_facecolor("#F8FAFC")
fig.patch.set_facecolor("#F8FAFC")

ax.text(0.04, 0.95, "EnergyWise — Insights & Energy Efficiency Recommendations", fontsize=14, fontweight='bold', color="#0F172A")
ax.text(0.04, 0.90, "Data-Driven Architectural Findings and Demand-Side Management Strategies", fontsize=9, color="#64748B")

draw_card(ax, 0.04, 0.50, 0.44, 0.37, "Empirical Finding 1: HVAC Load Escalation",
          "• Operating HVAC increases mean energy consumption\n  from 74.74 kWh (Off) to 79.40 kWh (On).\n"
          "• Net surge: +4.66 kWh (+6.24% jump in baseload).\n"
          "• Accounts for ₹1,000+ monthly tariff elevation under\n  higher telescopic slab rates.",
          border_color="#D97706")

draw_card(ax, 0.51, 0.50, 0.45, 0.37, "Empirical Finding 2: Ambient Temperature Correlation",
          "• Ambient temperature exhibits dominant correlation\n  with energy demand (r = +0.694).\n"
          "• Each +1.0 °C rise escalates building demand by\n  approximately +1.98 kWh.\n"
          "• Primary driver of cooling load across warm months.",
          border_color="#E53935")

draw_card(ax, 0.04, 0.05, 0.92, 0.41, "Actionable Energy Management & Efficiency Opportunities",
          "1. Smart Pre-Cooling Strategy: Pre-cool spaces during morning off-peak hours before ambient peaks.\n"
          "2. Occupancy Setpoint Deadbands: Relax thermostat setpoint by 1.5–2.0 °C during unoccupied periods (saves 8–12%).\n"
          "3. Daylight Harvesting Integration: Interlock perimeter lighting with ambient photocells (saves ~1.6 kWh/day).\n"
          "4. Solar PV Self-Consumption: Schedule deferrable loads (laundry, pumps, EV charging) during peak solar generation.\n"
          "5. MSEDCL Slab Boundary Management: Monitor cumulative monthly units to avoid breaching ₹15.03/unit and ₹17.53/unit slabs.",
          border_color="#16A34A", bg_color="#F0FDF4")

ax.set_title("Figure 10.6: Streamlit Dashboard UI Layout — Page 6: Insights & Recommendations", fontsize=12, fontweight='bold', pad=12)
ax.set_xlim(0, 1)
ax.set_ylim(0, 1)
plt.tight_layout()
plt.savefig(os.path.join(ASSETS_DIR, 'fig_10_6_insights_ui.png'), dpi=300)
plt.close()
print("[OK] Saved Figure 10.6: Insights & Recommendations UI")

print("All Dashboard UI Schematics Successfully Generated!")
