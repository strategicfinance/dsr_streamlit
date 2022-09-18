import streamlit as st
import pandas as pd


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
st.write("Balance data as of 18-Sep-2022")

st.subheader("Gross Return per collateral type")
min_psm_roa = 0.8
roa1, roa2, roa3 = st.columns(3)
psm_roa = roa1.number_input("PSM (%)", min_value=0.00, format="%.2f", value=min_psm_roa)
rwa_roa = roa2.number_input("RWA (%)", min_value=0.00, format="%.2f", value=3.0)
cry_roa = roa3.number_input("Crypto (%)", min_value=0.00, format="%.2f", value=1.26)

bs_18_sep_2022 = [
    ["PSM", 5_206_192_880, psm_roa],
    ["RWA", 139_017_410, rwa_roa],
    ["Crypto", 1_168_651_320, cry_roa],
]

bal1, bal2, bal3 = st.columns(3)
bal1.metric("PSM Balance", value=f"{human_format(bs_18_sep_2022[0][1])}")
bal2.metric("RWA Balance", value=f"{human_format(bs_18_sep_2022[1][1])}")
bal3.metric("Crypto Balance", value=f"{human_format(bs_18_sep_2022[2][1])}")

work = st.number_input(
    "Annualized Workforce Expense (DAI)",
    min_value=0.00,
    format="%.0f",
    value=40_000_000.00,
)
sbuffer_18_sep_2022 = 79_314_768.00
dsrlock_18_sep_2022 = 1_173_793.00
dsr_18_sep_2022 = 0.01
dsr_expense_18_sep_2022 = dsr_18_sep_2022 * dsrlock_18_sep_2022

data = pd.DataFrame(bs_18_sep_2022, columns=["label", "balance", "roa"])
data["ann_rev"] = data["balance"] * data["roa"] / 100
# st.table(data)


total_dai = sum(data[["balance"]].values)[0] - sbuffer_18_sep_2022
total_rev = sum(data["ann_rev"])
nprofit_18_sep_2022 = total_rev - dsr_expense_18_sep_2022 - work

st.subheader("Current Balances")
st.write(f"Assumes PSM generates an ROA of {min_psm_roa:.2f}")

tot1, tot2 = st.columns(2)
tot1.metric("Total DAI Outstanding", value=f"{human_format(total_dai)}")
tot2.metric("Net Profit (DAI)", value=f"{human_format(nprofit_18_sep_2022)}")
cur1, cur2, cur3 = st.columns(3)
cur1.metric("Total DAI Locked in DSR", value=f"{dsrlock_18_sep_2022/total_dai:.2%}")
cur2.metric("DSR", value=f"{dsr_18_sep_2022:.2}%")
cur3.metric("Annualized DSR Expense", value=f"{human_format(dsr_expense_18_sep_2022)}")


st.subheader("Simulated Balances")
sim1, sim2, sim3 = st.columns(3)
psm_gwth = sim1.slider(
    "Growth in PSM (%)",
    min_value=(
        sbuffer_18_sep_2022 / data[data["label"] == "PSM"]["balance"].values[0] - 1.0
    )
    * 100.00,
    max_value=300.00,
    value=0.0,
)
new_psm = data[data["label"] == "PSM"]["balance"].values[0] * (1 + psm_gwth / 100)
rwa_bal = data[data["label"] == "RWA"]["balance"].values[0]
cry_bal = data[data["label"] == "Crypto"]["balance"].values[0]
new_bs = [
    new_psm,
    rwa_bal,
    cry_bal,
]
new_rev = sum(new_bs * data["roa"] / 100)
new_roa = new_rev / sum(new_bs) * 100
new_dai = sum(new_bs) - sbuffer_18_sep_2022

dsr_lock = sim2.slider(
    "Dai locked in Pot (%)",
    min_value=(dsrlock_18_sep_2022 / total_dai) * 100.00,
    max_value=100.00,
    value=0.0,
)
dsr = sim3.slider(
    "DSR - Capped at ROA (%)", min_value=dsr_18_sep_2022, max_value=new_roa
)

dsr_exp = new_dai * dsr_lock / 100 * dsr / 100
new_prof = new_rev - work - dsr_exp

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
    delta=f"{(dsr_exp/dsr_expense_18_sep_2022-1)*100:.2f}%",
)

ntot3.metric(
    "Net Profit (DAI)",
    value=f"{human_format(new_prof)}",
    delta=f"{(new_prof/nprofit_18_sep_2022-1)*100:.2f}%",
)
