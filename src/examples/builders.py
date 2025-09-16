# Example table and chart builder functions for use with create_report.py
from __future__ import annotations

from datetime import date
import pandas as pd
import numpy as np

import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def _parse_asof(asof: str) -> date:
    """Parse an 'as-of' date string into a date object; fall back to today."""
    try:
        return pd.to_datetime(asof).date()
    except Exception:
        return date.today()


def build_base_pay_by_grade(asof: str, scenario: str = "Central") -> pd.DataFrame:
    """
    Return a simple base pay table by grade for testing.

    Parameters
    ----------
    asof : str
        e.g., "2025-03-31"
    scenario : str
        "Central", "High", "Low" — used to tweak costs.

    Returns
    -------
    pd.DataFrame
        Columns: Grade, Headcount, Base cost (£), On‑cost rate, On‑cost (£), Scenario, As of
    """
    asof_dt = _parse_asof(asof)

    grades = ["A", "B", "C", "D"]
    headcount = [120, 85, 40, 20]
    fte = [118.25, 80.35, 36.56, 18.76]
    base_cost = np.array([2_150_000, 1_430_000, 690_000, 390_000], dtype=float)

    # Scenario tweak: +/- 5%
    if scenario.lower() == "high":
        base_cost *= 1.05
    elif scenario.lower() == "low":
        base_cost *= 0.95

    # Simple on‑cost rates per grade
    oncost_rates = np.array([0.27, 0.24, 0.22, 0.20])
    oncost_amount = (base_cost * oncost_rates).round(0)

    df = pd.DataFrame({
        "Grade": grades,
        "Headcount": headcount,
        "FTE": fte,
        "Base cost (£)": base_cost.round(0).astype(int),
        "OC rate": oncost_rates,
        "On‑cost (£)": oncost_amount.astype(int),
        "Scenario": scenario,
        "As of date": asof_dt
    })

    return df


def build_pay_tables(asof: str, scenario: str = "Central") -> dict[str, pd.DataFrame]:
    """
    Return a dict of DataFrames to test the TOML 'key' selector.

    Keys:
      - 'base_pay' : base pay by grade
      - 'on_costs' : on-cost rates by grade alone
    """
    base = build_base_pay_by_grade(asof=asof, scenario=scenario).copy()

    on_costs = base.loc[:, ["Grade", "OC rate"]].copy()
    on_costs.rename(columns={"OC rate": "OC rate"}, inplace=True)

    return {
        "base_pay": base,
        "on_costs": on_costs
    }


def build_empty_table() -> pd.DataFrame:
    """
    Return an empty DataFrame with headers only — to test your '(no data)' flow.
    """
    cols = ["Grade", "Headcount", "Base cost (£)"]
    return pd.DataFrame(columns=cols)



def make_chart():
    # Sample data
    x = np.arange(1, 13)
    y1 = np.random.randint(80, 140, size=12)
    y2 = np.random.randint(60, 160, size=12)
    df = pd.DataFrame({'Month': x, 'Sales_A': y1, 'Sales_B': y2})
    
    # Create the Matplotlib figure
    fig, ax = plt.subplots(figsize=(6.5, 3.8), dpi=150)
    ax.plot(x, y1, label='Sales_A', color='#5B9BD5', linewidth=2)
    ax.plot(x, y2, label='Sales_B', color='#ED7D31', linewidth=2)
    ax.set_title('Monthly Sales')
    ax.set_xlabel('Month')
    ax.set_ylabel('Sales (£k)')
    ax.grid(True, alpha=0.3)
    ax.legend(loc='lower right')
    
    # Save figure to an in-memory buffer
    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png', dpi=150)
    plt.close(fig)
    img.seek(0)

    return img
