# This script provides a modular framework to analyze economic indicators from FRED
# across presidential terms (Trump and Biden). It includes plotting trends and computing
# detailed statistical summaries for each term.

import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import numpy as np
from fredapi import Fred

plt.style.use('ggplot')
plt.style.use('dark_background')

# Initialize FRED API 
fred = Fred(api_key='-------------------')

# -------------------- Tools For Main Functions --------------------

def get_presidency_dates():
    return {
        "Trump": (datetime(2017, 1, 20), datetime(2021, 1, 20)),
        "Biden": (datetime(2021, 1, 20), datetime(2025, 1, 20))
    }

def fetch_fred_data(series_id):
    data = fred.get_series(series_id).dropna()
    data.index = pd.to_datetime(data.index)
    return data.sort_index()

def compute_metrics(series, start_date, end_date):
    subset = series[(series.index >= start_date) & (series.index <= end_date)]
    if subset.empty:
        return [None] * 10
    start = subset.iloc[0]
    end = subset.iloc[-1]
    avg = subset.mean()
    med = subset.median()
    std_dev = subset.std()
    max_val = subset.max()
    min_val = subset.min()
    pct_change = ((end - start) / start) * 100
    years = (end_date - start_date).days / 365.25
    ann_return = ((end / start) ** (1 / years) - 1) * 100 if start > 0 else None
    ann_volatility = std_dev * np.sqrt(12)
    return [round(start,2), round(end,2), round(avg,2), round(med,2), round(std_dev,2),
            round(max_val,2), round(min_val,2), round(pct_change,2),
            round(ann_return,2) if ann_return is not None else None,
            round(ann_volatility,2)]

# -------------------- Main Functions --------------------

def plot_of_metrics(metric_dict, title="Metric Trends: Trump vs. Biden"):
    dates = get_presidency_dates()
    trump_start, trump_end = dates["Trump"]
    biden_start, biden_end = dates["Biden"]

    for name, series_id in metric_dict.items():
        try:
            data = fetch_fred_data(series_id)
            filtered_data = data[(data.index >= trump_start) & (data.index <= biden_end)]

            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(filtered_data.index, filtered_data.values, label=name, linewidth=2)
            ax.axvspan(trump_start, trump_end, color='red', alpha=0.2, label='Trump Term (2017–2021)')
            ax.axvspan(biden_start, biden_end, color='blue', alpha=0.2, label='Biden Term (2021–2025)')
            ax.set_title(f"{name} Trend (Trump vs. Biden)", fontsize=14)
            ax.set_xlabel("Date")
            ax.set_ylabel("Value")
            ax.legend()
            ax.grid(True, linestyle='--', alpha=0.6)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            print(f"Error fetching or plotting {name}: {e}")

def detailed_value_summary(metric_dict):
    dates = get_presidency_dates()
    trump_start, trump_end = dates["Trump"]
    biden_start, biden_end = dates["Biden"]

    results = []
    for name, series_id in metric_dict.items():
        try:
            data = fetch_fred_data(series_id)
            trump_stats = compute_metrics(data, trump_start, trump_end)
            biden_stats = compute_metrics(data, biden_start, biden_end)

            results.append([name, "Trump (2017–2021)", *trump_stats])
            results.append([name, "Biden (2021–2025)", *biden_stats])

        except Exception as e:
            print(f"Error computing summary for {name}: {e}")

    columns = [
        'Metric', 'Term', 'Start', 'End', 'Average', 'Median',
        'Std Dev', 'Max', 'Min', '% Change',
        'Annualized Return (%)', 'Annualized Volatility'
    ]
    return pd.DataFrame(results, columns=columns)

# Energy Prices
energy_fuels_metrics = {
    "Crude Oil (WTI)": "DCOILWTICO",                  
    "Natural Gas": "DHHNGSP",                         
    "Gasoline (Retail, U.S. Average)": "GASREGCOVW",  
    "Electricity Price (Residential)": "APU000072610" 
}
plot_of_metrics(energy_fuels_metrics, title="📉 Health Care Price Trends")
detailed_value_summary(energy_fuels_metrics)

# Health Care Consumer Price Index
health_metrics = {
    "CPI - Medical Care": "CPIMEDSL",
    "CPI - Health Insurance": "CUSR0000SEMC",
}
plot_of_metrics(health_metrics, title="📉 Health Care Price Index Trends")
detailed_value_summary(health_metrics)

# Food and Agriculture Prices U.S. Prices / metric ton
food_ag_metrics = {
    "Corn": "PMAIZMTUSDM",            # U.S. corn price, USD/metric ton
    "Wheat": "PWHEAMTUSDM",           # U.S. wheat price, USD/metric ton
    "Soybeans": "PSOYBUSDQ",          # Soybeans price, USD/metric ton
    "Sugar": "PSUGAISAUSDM",          # International sugar price, USD/metric ton
    "Coffee": "PCOFFOTMUSDM"          # Coffee price, USD/metric ton
}

plot_of_metrics(food_ag_metrics, title="📉 Food & Agriculture Prices")
detailed_value_summary(food_ag_metrics)

# Auto Price Index 
auto_price_metrics = {
    "CPI - New Vehicles": "CUSR0000SETA01",      
    "CPI - Used Cars and Trucks": "CUSR0000SETA02",  
    "PPI - Motor Vehicles": "CUSR0000SETA",   
    "PPI - Motor Vehicle Parts": "PCU3363--3363--"  
}
plot_of_metrics(auto_price_metrics, title="Auto Prices")
detailed_value_summary(auto_price_metrics)
