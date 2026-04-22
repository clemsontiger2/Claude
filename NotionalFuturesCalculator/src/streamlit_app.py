import pandas as pd
import streamlit as st

st.set_page_config(page_title="Notional Futures Calculator", layout="wide")

CONTRACTS = {
    "E-mini S&P 500 (ES)":        {"multiplier": 50,     "tick_size": 0.25,  "tick_value": 12.50,  "initial_margin": 12650, "maint_margin": 11500},
    "Micro E-mini S&P 500 (MES)": {"multiplier": 5,      "tick_size": 0.25,  "tick_value": 1.25,   "initial_margin": 1265,  "maint_margin": 1150},
    "E-mini Nasdaq-100 (NQ)":     {"multiplier": 20,     "tick_size": 0.25,  "tick_value": 5.00,   "initial_margin": 17600, "maint_margin": 16000},
    "Micro E-mini Nasdaq (MNQ)":  {"multiplier": 2,      "tick_size": 0.25,  "tick_value": 0.50,   "initial_margin": 1760,  "maint_margin": 1600},
    "E-mini Dow (YM)":            {"multiplier": 5,      "tick_size": 1.0,   "tick_value": 5.00,   "initial_margin": 9900,  "maint_margin": 9000},
    "Crude Oil (CL)":             {"multiplier": 1000,   "tick_size": 0.01,  "tick_value": 10.00,  "initial_margin": 6600,  "maint_margin": 6000},
    "Natural Gas (NG)":           {"multiplier": 10000,  "tick_size": 0.001, "tick_value": 10.00,  "initial_margin": 2750,  "maint_margin": 2500},
    "Gold (GC)":                  {"multiplier": 100,    "tick_size": 0.10,  "tick_value": 10.00,  "initial_margin": 9900,  "maint_margin": 9000},
    "Silver (SI)":                {"multiplier": 5000,   "tick_size": 0.005, "tick_value": 25.00,  "initial_margin": 9900,  "maint_margin": 9000},
    "10-Year T-Note (ZN)":        {"multiplier": 1000,   "tick_size": 0.015625, "tick_value": 15.625, "initial_margin": 1650, "maint_margin": 1500},
    "30-Year T-Bond (ZB)":        {"multiplier": 1000,   "tick_size": 0.03125,  "tick_value": 31.25,  "initial_margin": 3850, "maint_margin": 3500},
    "Euro FX (6E)":               {"multiplier": 125000, "tick_size": 0.00005, "tick_value": 6.25,  "initial_margin": 2750,  "maint_margin": 2500},
    "British Pound (6B)":         {"multiplier": 62500,  "tick_size": 0.0001,  "tick_value": 6.25,  "initial_margin": 2750,  "maint_margin": 2500},
}

st.title("Notional Futures Calculator")
st.caption("Calculate notional value, margin requirements, leverage, and P&L for futures contracts.")

col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("Contract Parameters")

    contract_name = st.selectbox("Futures Contract", list(CONTRACTS.keys()))
    info = CONTRACTS[contract_name]

    price = st.number_input(
        "Current Futures Price",
        min_value=0.01,
        value=5000.00 if "S&P" in contract_name or "Nasdaq" in contract_name or "Dow" in contract_name
              else 75.00 if "Crude" in contract_name
              else 3.00 if "Natural" in contract_name
              else 2000.00 if "Gold" in contract_name
              else 25.00 if "Silver" in contract_name
              else 110.00 if "T-Note" in contract_name
              else 120.00 if "T-Bond" in contract_name
              else 1.10 if "Euro" in contract_name
              else 1.25,
        step=0.25,
        format="%.4f",
    )

    num_contracts = st.number_input("Number of Contracts", min_value=1, value=1, step=1)

    st.divider()
    st.subheader("P&L Scenario")
    price_change = st.number_input(
        "Price Change (points / ticks in price units)",
        value=10.0,
        step=info["tick_size"],
        format="%.4f",
        help="Enter a positive or negative change in the futures price.",
    )
    direction = st.radio("Position Direction", ["Long", "Short"], horizontal=True)

with col_right:
    multiplier = info["multiplier"]
    tick_size = info["tick_size"]
    tick_value = info["tick_value"]
    initial_margin = info["initial_margin"]
    maint_margin = info["maint_margin"]

    notional = price * multiplier * num_contracts
    total_initial_margin = initial_margin * num_contracts
    total_maint_margin = maint_margin * num_contracts
    leverage = notional / total_initial_margin if total_initial_margin else 0

    num_ticks = price_change / tick_size
    raw_pnl = num_ticks * tick_value * num_contracts
    pnl = raw_pnl if direction == "Long" else -raw_pnl

    st.subheader("Results")

    m1, m2 = st.columns(2)
    m1.metric("Notional Value", f"${notional:,.2f}")
    m2.metric("Leverage Ratio", f"{leverage:.1f}x")

    m3, m4 = st.columns(2)
    m3.metric("Initial Margin (total)", f"${total_initial_margin:,.2f}")
    m4.metric("Maintenance Margin (total)", f"${total_maint_margin:,.2f}")

    pnl_color = "normal" if pnl >= 0 else "inverse"
    st.metric(
        label=f"Estimated P&L ({direction}, {price_change:+.4f} pts)",
        value=f"${pnl:,.2f}",
        delta=f"{pnl / total_initial_margin * 100:.2f}% of margin" if total_initial_margin else "N/A",
        delta_color=pnl_color,
    )

    st.divider()
    st.subheader("Contract Specs")
    specs = {
        "Multiplier": f"{multiplier:,}",
        "Tick Size": f"{tick_size}",
        "Tick Value": f"${tick_value:.3f}",
        "Initial Margin / Contract": f"${initial_margin:,}",
        "Maintenance Margin / Contract": f"${maint_margin:,}",
    }
    for k, v in specs.items():
        st.markdown(f"**{k}:** {v}")

st.divider()
st.subheader("P&L Sensitivity Table")

pct_changes = [-5, -4, -3, -2, -1, -0.5, 0.5, 1, 2, 3, 4, 5]
rows = []
for pct in pct_changes:
    chg = price * (pct / 100)
    ticks = chg / tick_size
    gross = ticks * tick_value * num_contracts
    net = gross if direction == "Long" else -gross
    margin_pct = net / total_initial_margin * 100 if total_initial_margin else 0
    rows.append({
        "Price Change %": f"{pct:+.1f}%",
        "Price Change ($)": f"${chg:,.4f}",
        "New Price": f"${price + chg:,.4f}",
        "P&L": f"${net:,.2f}",
        "% of Initial Margin": f"{margin_pct:.1f}%",
    })

df = pd.DataFrame(rows)
st.dataframe(df, use_container_width=True, hide_index=True)
