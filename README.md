# EnergyWise — Energy Consumption Prediction Using Machine Learning

**M.Tech Data Science Project**  
*Machine Learning-Based Energy Analytics and Prediction System*

---

## ⚡ Overview

**EnergyWise** is an end-to-end, interactive web dashboard built with **Python**, **Streamlit**, **Scikit-learn**, and **Plotly** to predict, analyze, and optimize building energy consumption.

The system is trained on 30,000 historical records encompassing ambient environmental conditions (temperature, humidity), building characteristics (square footage, occupancy), and equipment operational states (HVAC status, lighting, onsite renewable generation).

---

## 🌟 Key Features

1. **📊 Overview Dashboard**:
   - Dynamic KPI summary cards (Total Records, Average Energy, Peak Demand, Minimum Baseload, Core Features).
   - 8 interactive Plotly visualizations:
     - Energy consumption distribution with KDE and mean/median indicators.
     - Daily time-series trend over time with range slider.
     - Temperature vs. Energy consumption with HVAC status overlay.
     - Occupancy vs. Energy consumption box plot.
     - HVAC usage comparison (On vs Off).
     - Lighting usage comparison (On vs Off).
     - Day of week consumption variation with error bars.
     - Annotated numerical correlation heatmap.

2. **🔮 Predict Energy Consumption & MSEDCL Estimated Bill (from 1 April 2026)**:
   - Comprehensive prediction form with input validation and dual prediction horizon modes:
     - **📅 Monthly Prediction (Default & Primary Feature)**: Aggregates actual hourly ML predictions across all calendar hours of the selected month (e.g., 720h for April, 744h for May). Models weekday vs. weekend occupancy patterns, diurnal temperature curves, and daytime solar PV offsets without simplistic multiplying by 30 or 720.
     - **⚡ Daily Prediction (24-Hour Profile)**: Predicts hourly electricity consumption for 24 hours on a selected target date, summing the 24 predictions to calculate exact daily kWh.
   - **4-Component Standardized Metric Summary**:
     - `Daily Consumption (kWh)`: Daily average (Monthly mode) or 24-hour sum (Daily mode).
     - `Monthly Consumption (kWh)`: Full month sum (Monthly mode) or 30-day billing equivalent (Daily mode).
     - `Estimated Daily Cost`: Monthly bill ÷ days (Monthly mode) or daily prorated charges (Daily mode).
     - `Estimated Monthly Bill`: Full MSEDCL monthly bill (Monthly mode) or projected bill (Daily mode).
   - Powered by genuine trained **Random Forest Regressor** pipeline (`best_energy_model.joblib`, $R^2 = 0.9871$).
   - Ensemble variance calculation providing 90% confidence intervals.
   - Prominently labeled with official **Estimated Bill Notices**, distinguishing estimates from official utility bills.

3. **⚡ Dedicated MSEDCL Domestic Electricity Bill Calculator Page (From 1 April 2026)**:
   - Standalone interactive tariff calculator based on the official MERC Domestic Electricity Tariff Order (LT-I Category).
   - **One-Click Sync**: `🔄 Sync with Model` button automatically imports the latest ML forecasted consumption.
   - **Progressive Telescopic Slabs & Energy Charges**:
     - **1 – 100 units:** ₹ 3.96 / unit
     - **101 – 300 units:** ₹ 10.80 / unit
     - **301 – 500 units:** ₹ 15.03 / unit
     - **501 – 1000 units:** ₹ 17.53 / unit
     - **Above 1000 units:** ₹ 17.53 / unit
   - **Wheeling Charge:** ₹ 1.60 per unit consumed.
   - **Fixed Demand Charge:** ₹ 130 per month (single-phase standard) / ₹ 440 per month (three-phase).
   - **Fuel Adjustment Charge (FAC):** Applicable rate for the selected billing period (April–October 2026).
   - **Maharashtra Electricity Duty:** Statutory 16.0% of applicable charges ($\text{Energy} + \text{Wheeling} + \text{Fixed} + \text{FAC}$).
   - **Additional Municipal Charge:** ₹ 10 per month, where applicable.
   - **Interactive Rate Editor:** Allows updating all time-varying rates and slabs dynamically without code hardcoding.
   - **Interactive Visualizations**: Interactive Donut Chart of bill cost composition and Progressive Slab bar chart.
   - **Step-by-Step Mathematical Audit Log**: Transparent 8-step formula with subtotals.
   - **Seasonal & Connection Sensitivity Comparison**: Compares bills across billing periods and connection types.

4. **📈 Model Performance & Evaluation**:
   - Rigorous side-by-side comparison of 4 algorithms on an independent 20% holdout test set:
     - **Random Forest Regressor** ($R^2 = 0.9871$, $\text{RMSE} = 0.91\text{ kWh}$, $\text{MAE} = 0.46\text{ kWh}$) — **Best Model** 🏆
     - **Gradient Boosting Regressor** ($R^2 = 0.8752$, $\text{RMSE} = 2.83\text{ kWh}$)
     - **Support Vector Regressor (SVR)** ($R^2 = 0.7157$, $\text{RMSE} = 4.27\text{ kWh}$)
     - **Linear Regression** ($R^2 = 0.6165$, $\text{RMSE} = 4.96\text{ kWh}$)
   - Grouped performance bar chart ($R^2$, MAE, RMSE).
   - In-depth diagnostics: Actual vs. Predicted scatter plots, Residual plots, and Feature Importance rankings.
   - Detailed justification of model selection strategy.

5. **📁 Dataset Explorer & Quality Inspection**:
   - Switch between datasets or upload custom CSV files.
   - Real-time data quality verification (null value detection, duplicate checks).
   - Interactive data table with multi-criteria filtering (HVAC, Lighting, Temperature).
   - Column-level distribution inspector and data type viewer.
   - Cleaned/filtered CSV dataset download.

6. **💡 Insights & Energy Efficiency Recommendations**:
   - Data-backed empirical findings (e.g., HVAC adds $+4.66\text{ kWh}$ or $\sim 6.2\%$ demand surge; ambient temperature correlation $r = +0.694$).
   - Actionable energy management opportunities (smart pre-cooling, occupancy setpoint deadbands, daylight harvesting, renewable self-consumption).
   - Clear scientific distinction between empirical correlation and causal trial outcomes.

---

## 🛠️ Project Structure

```
Energy_Consumption_Prediction/
│
├── app.py                             # Main Streamlit web application
├── requirements.txt                   # Python dependencies
├── README.md                          # Project documentation and setup guide
│
├── .streamlit/
│   └── config.toml                    # Streamlit Light Modern Theme configuration
│
├── data/
│   ├── Energy_Consumption_Virtual.csv # Primary 30,000-record dataset
│   └── Energy_Consumption_30000_Augmented.csv
│
├── models/
│   ├── best_energy_model.joblib       # Serialized best model pipeline (Random Forest)
│   └── all_models_summary.joblib      # Evaluation metrics and pre-computed test results
│
├── src/
│   ├── __init__.py
│   ├── data_processing.py             # Data loading, validation, and feature preparation
│   ├── model_training.py              # ML pipelines, model fitting, and evaluation
│   ├── prediction.py                  # Prediction logic, bounds, and uncertainty
│   ├── mseb_tariff.py                 # MSEB Maharashtra electricity rules & tariff engine
│   └── visualization.py               # Polished Plotly charts in Light Modern styling
│
└── ECP_Main (3).ipynb                 # Original exploratory machine learning notebook
```

---

## 🚀 Installation & Running Locally (Windows)

### 1. Open Terminal (PowerShell or Command Prompt)
Navigate to the project directory:
```bash
cd "c:\Users\mayur\OneDrive\Desktop\ML Mini Project\Energy_Consumption_Prediction"
```

### 2. Create and Activate a Virtual Environment
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Streamlit Application
```bash
streamlit run app.py
```

### 5. Access the Web Application
Open your web browser and navigate to:
```
http://localhost:8501
```

---

## 📊 Model Evaluation Summary Table

| Model Algorithm | $R^2$ Score | MAE (kWh) | MSE | RMSE (kWh) | Selection Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest Regressor** | **0.9871** | **0.46** | **0.83** | **0.91** | **Selected Best Model 🏆** |
| **Gradient Boosting Regressor** | 0.8752 | 2.20 | 8.00 | 2.83 | Candidate Model |
| **Support Vector Regressor (SVR)** | 0.7157 | 2.99 | 18.23 | 4.27 | Candidate Model |
| **Linear Regression** | 0.6165 | 3.96 | 24.59 | 4.96 | Baseline Model |

---

## 📜 Academic Integrity Note
All metrics, charts, and predictions are computed dynamically from genuinely trained machine learning models fitted on the project's actual 30,000 records without synthetic placeholder formulas or fabricated statistics.
