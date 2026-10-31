import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="Employee Engagement & Burnout Diagnostics", page_icon="📊", layout="wide")
st.title("Employee Engagement, Satisfaction & Burnout Diagnostics")
st.caption("HR analytics dashboard | Dataset-driven exploratory analysis")

@st.cache_data
def load_data(uploaded_file=None):
    if uploaded_file is not None:
        return pd.read_csv(uploaded_file)
    p = Path(__file__).parent / "data" / "Palo Alto Networks.csv"
    if p.exists():
        return pd.read_csv(p)
    return pd.read_csv("Palo Alto Networks.csv")

uploaded = st.sidebar.file_uploader("Upload employee CSV (optional)", type=["csv"])
try:
    raw = load_data(uploaded)
except Exception as e:
    st.error(f"Could not load dataset: {e}")
    st.stop()

required = ["JobInvolvement","JobSatisfaction","EnvironmentSatisfaction","RelationshipSatisfaction",
            "OverTime","WorkLifeBalance","Attrition","Department"]
missing = [c for c in required if c not in raw.columns]
if missing:
    st.error("Dataset is missing required columns: " + ", ".join(missing))
    st.stop()

df = raw.copy()
score_cols = ["JobInvolvement","JobSatisfaction","EnvironmentSatisfaction","RelationshipSatisfaction"]
for c in score_cols + ["WorkLifeBalance"]:
    df[c] = pd.to_numeric(df[c], errors="coerce")
df["EngagementIndex"] = ((df[score_cols].mean(axis=1) - 1) / 3 * 100).round(1)
df["BurnoutRisk"] = np.select(
    [(df["OverTime"].astype(str).str.lower().eq("yes")) & (df["WorkLifeBalance"] <= 2),
     (df["OverTime"].astype(str).str.lower().eq("yes")) | (df["WorkLifeBalance"] <= 2)],
    ["High", "Medium"], default="Low"
)
# Normalize common attrition encodings to readable labels.
df["AttritionLabel"] = df["Attrition"].astype(str).str.strip().str.lower().map(
    {"1":"Left","0":"Stayed","yes":"Left","no":"Stayed","true":"Left","false":"Stayed"}
).fillna(df["Attrition"].astype(str))

st.sidebar.header("Filters")
departments = sorted(df["Department"].dropna().astype(str).unique())
selected_depts = st.sidebar.multiselect("Department", departments, default=departments)
risk_options = ["Low","Medium","High"]
selected_risks = st.sidebar.multiselect("Burnout risk", risk_options, default=risk_options)
filtered = df[df["Department"].astype(str).isin(selected_depts) & df["BurnoutRisk"].isin(selected_risks)].copy()

if filtered.empty:
    st.warning("No employees match the selected filters.")
    st.stop()

left, mid, right, fourth = st.columns(4)
left.metric("Employees in view", f"{len(filtered):,}")
mid.metric("Average engagement", f"{filtered['EngagementIndex'].mean():.1f}/100")
right.metric("High burnout-risk group", f"{(filtered['BurnoutRisk']=='High').sum():,}")
# Attrition metric supports numeric 0/1 and Yes/No data.
attr_map = {"1":1,"yes":1,"true":1,"0":0,"no":0,"false":0}
attr_num = filtered["Attrition"].astype(str).str.lower().map(attr_map)
fourth.metric("Attrition rate", f"{attr_num.mean()*100:.1f}%" if attr_num.notna().any() else "N/A")

tab1, tab2, tab3, tab4 = st.tabs(["Engagement overview","Burnout & workload","Satisfaction","Career & attrition"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        fig = px.histogram(filtered, x="EngagementIndex", nbins=15, title="Distribution of employee engagement",
                           labels={"EngagementIndex":"Engagement index (0–100)"})
        st.plotly_chart(fig, width="stretch")
    with c2:
        by_dept = filtered.groupby("Department", as_index=False)["EngagementIndex"].mean()
        fig = px.bar(by_dept, x="Department", y="EngagementIndex", title="Average engagement by department",
                     range_y=[0,100])
        st.plotly_chart(fig, width="stretch")
    st.info("Engagement Index is the unweighted average of four 1–4 survey dimensions, rescaled to 0–100.")

with tab2:
    c1, c2 = st.columns(2)
    with c1:
        risk = filtered["BurnoutRisk"].value_counts().reindex(risk_options, fill_value=0).rename_axis("Risk").reset_index(name="Employees")
        fig = px.bar(risk, x="Risk", y="Employees", color="Risk", title="Employees by heuristic burnout-risk group")
        st.plotly_chart(fig, width="stretch")
    with c2:
        if "OverTime" in filtered and "WorkLifeBalance" in filtered:
            fig = px.histogram(filtered, x="WorkLifeBalance", color="OverTime", barmode="group",
                               title="Work-life balance by overtime status")
            st.plotly_chart(fig, width="stretch")
    st.warning("Burnout risk is a screening heuristic, not a clinical diagnosis: High = overtime AND work-life balance ≤2; Medium = either condition; Low = neither.")

with tab3:
    sat_long = filtered[score_cols].melt(var_name="Dimension", value_name="Score")
    fig = px.box(sat_long, x="Dimension", y="Score", title="Distribution of engagement-related dimensions")
    st.plotly_chart(fig, width="stretch")
    st.dataframe(filtered[score_cols].mean().round(2).rename("Average score").to_frame(), width="stretch")

with tab4:
    if "JobLevel" in filtered.columns:
        c1, c2 = st.columns(2)
        with c1:
            by_level = filtered.groupby("JobLevel", as_index=False)["EngagementIndex"].mean()
            fig = px.line(by_level, x="JobLevel", y="EngagementIndex", markers=True, title="Engagement by job level")
            fig.update_xaxes(tickmode="linear", dtick=1)
            st.plotly_chart(fig, width="stretch")
        with c2:
            if attr_num.notna().any():
                attr_view = filtered.assign(_attr=attr_num).groupby("Department", as_index=False)["_attr"].mean()
                attr_view["_attr"] *= 100
                fig = px.bar(attr_view, x="Department", y="_attr", title="Attrition rate by department",
                             labels={"_attr":"Attrition rate (%)"})
                st.plotly_chart(fig, width="stretch")
    if "YearsAtCompany" in filtered.columns:
        fig = px.scatter(filtered, x="YearsAtCompany", y="EngagementIndex", color="AttritionLabel",
                         title="Engagement vs. tenure", hover_data=["Department"])
        st.plotly_chart(fig, width="stretch")

st.subheader("Filtered employee records")
display_cols = [c for c in ["Age","Department","JobRole","EngagementIndex","BurnoutRisk","OverTime","WorkLifeBalance","AttritionLabel"] if c in filtered.columns]
st.dataframe(filtered[display_cols], width="stretch", hide_index=True)
st.caption("Use this dashboard for aggregate workforce diagnostics. Avoid using a heuristic score as the sole basis for individual employment decisions.")
