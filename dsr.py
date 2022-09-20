import streamlit as st
import pandas as pd

SBUFFER_OG = 79_314_768.00
DSRLOCK_OG = 1_173_793.00
DSR_OG = 0.01


def human_format(num):
    num = float("{:.3g}".format(num))
    magnitude = 0
    while abs(num) >= 1000:
        magnitude += 1
        num /= 1000.0
    return "{}{}".format(
        "{:,.2f}".format(num).rstrip("0").rstrip("."),
        ["", "k", "m", "bn", "tn"][magnitude],
    )


st.title("DSR Reflexivity")
st.write("Balance data as of 18-Sep-2022, can be modified to match different scenarios")
st.write(
    "Baseline ROA figures should be expectation for gross interest returns on the provided balances.",
)

st.subheader("Gross Return per collateral type")
min_psm_roa = 0.8
roa1, roa2, roa3 = st.columns(3)
psm_roa = roa1.number_input("PSM (%)", min_value=0.00, format="%.2f", value=min_psm_roa)
rwa_roa = roa2.number_input("RWA (%)", min_value=0.00, format="%.2f", value=3.0)
cry_roa = roa3.number_input("Crypto (%)", min_value=0.00, format="%.2f", value=1.26)

ogbal1, ogbal2, ogbal3 = st.columns(3)
og_psm = ogbal1.number_input(
    "PSM Balance", min_value=SBUFFER_OG, format="%.2f", value=5_206_192_880.00
)
og_rwa = ogbal2.number_input(
    "RWA Balance", min_value=0.0, format="%.2f", value=139_017_410.00
)
og_cry = ogbal3.number_input(
    "Crypto Balance", min_value=0.0, format="%.2f", value=1_168_651_320.00
)

agg_roa = (og_psm * psm_roa + og_rwa * rwa_roa + og_cry * cry_roa) / (
    og_psm + og_rwa + og_cry
)

bal1, bal2, bal3 = st.columns(3)
bal1.metric("PSM Balance", value=f"{human_format(og_psm)}")
bal2.metric("RWA Balance", value=f"{human_format(og_rwa)}")
bal3.metric("Crypto Balance", value=f"{human_format(og_cry)}")

workforceExpense = st.number_input(
    "Annualized Workforce Expense (DAI)",
    min_value=0.00,
    format="%.0f",
    value=40_000_000.00,
)

og_dsrExpense = DSR_OG * DSRLOCK_OG

total_dai = og_psm + og_rwa + og_cry - SBUFFER_OG
total_rev = (og_psm * psm_roa + og_rwa * rwa_roa + og_cry * cry_roa) / 100
og_netProfit = total_rev - og_dsrExpense - workforceExpense

st.subheader("Current (Assumed) Balances")
st.write(f"Assumes PSM generates an ROA of {min_psm_roa:.2f}%")

tot1, tot2 = st.columns(2)
tot1.metric("Total DAI Outstanding", value=f"{human_format(total_dai)}")
tot2.metric("Net Profit (DAI)", value=f"{human_format(og_netProfit)}")
cur1, cur2, cur3 = st.columns(3)
cur1.metric("Total DAI Locked in DSR", value=f"{DSRLOCK_OG/total_dai:.2%}")
cur2.metric("DSR", value=f"{DSR_OG:.2}%")
cur3.metric("Annualized DSR Expense", value=f"{human_format(og_dsrExpense)}")


st.subheader("Simulated Balances")
sim1, sim2, sim3 = st.columns(3)
psm_gwth = sim1.slider(
    "Growth in PSM (%)",
    min_value=(SBUFFER_OG / og_psm - 1.0) * 100.00,
    max_value=300.00,
    value=0.0,
)
new_psm = og_psm * (1 + psm_gwth / 100)
rwa_bal = og_rwa
cry_bal = og_cry

new_bs = [
    new_psm,
    rwa_bal,
    cry_bal,
]

new_roarev = [new_psm * psm_roa, rwa_bal * rwa_roa, cry_bal * cry_roa]

new_rev = sum(new_roarev) / 100.00
new_roa = new_rev / sum(new_bs) * 100
new_dai = sum(new_bs) - SBUFFER_OG

dsr_lock = sim2.slider(
    "Dai locked in Pot (%)",
    min_value=(DSRLOCK_OG / total_dai) * 100.00,
    max_value=100.00,
    value=0.0,
)
dsr = sim3.slider("DSR - Capped at ROA (%)", min_value=DSR_OG, max_value=agg_roa)

dsr_exp = new_dai * dsr_lock / 100 * dsr / 100
new_prof = new_rev - workforceExpense - dsr_exp

nbal1, nbal2, nbal3 = st.columns(3)
nbal1.metric("New PSM Balance", value=f"{human_format(new_psm)}")
nbal2.metric("New RWA Balance", value=f"{human_format(rwa_bal)}")
nbal3.metric("New Crypto Balance", value=f"{human_format(cry_bal)}")


ntot1, ntot2, ntot3 = st.columns(3)
ntot1.metric(
    "New Total DAI Outstanding",
    value=f"{human_format(new_dai)}",
    delta=f"{(new_dai/total_dai-1)*100:.2f}%",
)
ntot2.metric(
    "New Annualized DSR Expense",
    value=f"{human_format(dsr_exp)}",
    delta=f"{(dsr_exp/og_dsrExpense-1)*100:.2f}%",
)

ntot3.metric(
    "Net Profit (DAI)",
    value=f"{human_format(new_prof)}",
    delta=f"{(new_prof/og_netProfit-1)*100:.2f}%",
)
