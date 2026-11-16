"""
app.py - Streamlit dashboard for the Prescriptive Reliability Agent.

Run:  streamlit run app.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))
from pra import agent, detect                      # noqa: E402
from pra.config import load_asset                  # noqa: E402
from pra.report import to_markdown                 # noqa: E402
from pra.simulate import FAULTS, simulate          # noqa: E402

# Palette (validated reference palette - see docs): one series colour + reserved status colours
SERIES = "#2a78d6"
MUTED = "#8a8985"
WARNING = "#fab219"
CRITICAL = "#d03b3b"
GOOD = "#0ca30c"

st.set_page_config(page_title="Prescriptive Reliability Agent", page_icon="⚙️", layout="wide")
st.markdown("""<style>
.block-container {padding-top: 1.6rem;}
div[data-testid="stMetricValue"] {font-size: 1.35rem;}
.badge {display:inline-block;padding:2px 10px;border-radius:12px;font-weight:600;font-size:0.85rem;}
</style>""", unsafe_allow_html=True)

asset = load_asset()
sensors = asset["sensors"]

# ---------------- Sidebar -----------------------------------------------------
st.sidebar.title("⚙️ Scenario")
labels = {"healthy": "Healthy machine"} | {k: v["description"] for k, v in FAULTS.items()}
choice = st.sidebar.selectbox("Injected condition (ground truth)", list(labels), index=1,
                              format_func=lambda k: labels[k])
seed = st.sidebar.number_input("Random seed", 0, 9999, 1)
days_after = st.sidebar.slider("Review the alert this many days after it fired", 0.0, 10.0, 3.0, 0.5)
st.sidebar.caption("Synthetic data. The agent never sees the ground truth - pick a fault, then check "
                   "whether the agent's diagnosis matches.")


@st.cache_data(show_spinner=False)
def get_data(fault, seed):
    return simulate(None if fault == "healthy" else fault, seed=int(seed))


df = get_data(choice, seed)
p = agent.run(df, at=f"alert+{days_after}d")
z = detect.zscores(df)
hi = detect.health_index(z, detect.margin_fraction(df))

# ---------------- Header ------------------------------------------------------
a = p.asset
st.title("Prescriptive Reliability Agent")
st.caption(f"{a['tag']} {a['name']} · {a['type']} · Criticality {a['criticality']} · "
           "From anomaly alert → failure mode → engineered action")

if p.status == "healthy":
    st.success(f"✅ **Healthy** - {p.summary}")
    fig = go.Figure(go.Scatter(x=hi.index, y=hi, line=dict(color=SERIES, width=2), name="Health index",
                               hovertemplate="%{x|%d-%b %H:%M}<br>Health %{y:.0f}<extra></extra>"))
    fig.update_layout(height=280, margin=dict(l=10, r=10, t=30, b=10), title="Health index (100 = normal)",
                      yaxis=dict(range=[0, 105]), plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, width="stretch")
    st.stop()

d = p.diagnosis
pr = p.priority
prio_color = {1: CRITICAL, 2: "#ec835a", 3: WARNING, 4: GOOD}[pr["level"]]
correct = FAULTS[choice]["expected_fm"] == d["fm_id"]

c1, c2, c3, c4, c5 = st.columns([2.2, 1, 1, 1, 1.2])
c1.metric("Diagnosis", d["name"], help=f"Match {d['match_score']:.0%} with FMEA signature")
c2.metric("Priority", f"P{pr['level']} {pr['label']}")
c3.metric("Days to trip", "-" if p.days_to_trip is None else f"{p.days_to_trip:.0f}")
c4.metric("Health index", f"{hi.loc[pd.Timestamp(p.analysis_time)]:.0f} / 100")
c5.metric("Value of acting now*", f"${p.economics['value_of_acting_now_usd']/1e6:.2f} M",
          help="Illustrative estimate - see Prescription tab for basis")

st.markdown(
    f"<span class='badge' style='background:{prio_color}22;color:{prio_color};border:1px solid {prio_color}'>"
    f"● P{pr['level']} {pr['label']} - {pr['window']}</span> &nbsp; "
    f"<span class='badge' style='background:#8a898522;border:1px solid #8a8985'>"
    f"{'✓ matches' if correct else '✗ differs from'} injected ground truth</span>"
    + ("&nbsp; <span class='badge' style='background:#fab21922;border:1px solid #fab219'>⚠ Agent unsure - "
       "discriminating checks recommended</span>" if p.ambiguous else ""),
    unsafe_allow_html=True)
st.write("")
st.info(p.summary.replace("**", ""))

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🛠 Prescription", "📈 Evidence", "🗂 History", "🧠 Agent trace",
                                        "📄 Report"])

# ---------------- Prescription ------------------------------------------------
with tab1:
    titles = {"confirm": "1 · Confirm", "immediate": "2 · Immediate", "corrective": "3 · Corrective",
              "defect_elimination": "4 · Defect elimination"}
    cols = st.columns(4)
    for col, (k, t) in zip(cols, titles.items()):
        col.markdown(f"**{t}**")
        for x in p.actions[k]:
            col.markdown(f"- {x}")
    st.divider()
    left, right = st.columns([1.3, 1])
    with left:
        st.markdown("**Draft CMMS notification** (not submitted)")
        st.table(pd.DataFrame(p.notification.items(), columns=["Field", "Value"]).set_index("Field"))
    with right:
        st.markdown("**Engineer decision**")
        st.caption("The agent recommends; a competent engineer decides. Nothing is executed automatically.")
        key = f"decision_{choice}_{seed}_{days_after}"
        b1, b2, b3 = st.columns(3)
        if b1.button("Approve", type="primary", width="stretch"):
            st.session_state[key] = "Approved - notification released to planning"
        if b2.button("Modify", width="stretch"):
            st.session_state[key] = "Returned for modification"
        if b3.button("Reject", width="stretch"):
            st.session_state[key] = "Rejected - feedback logged to improve the FMEA library"
        if key in st.session_state:
            st.success(st.session_state[key])
        e = p.economics
        st.markdown("**Value of acting now (illustrative)**")
        st.markdown(f"- Run-to-failure: **${e['unplanned_cost_usd']:,.0f}**\n"
                    f"- Planned: **${e['planned_cost_usd']:,.0f}**\n"
                    f"- Avoided: **${e['value_of_acting_now_usd']:,.0f}**")
        st.caption(e["basis"])

# ---------------- Evidence ----------------------------------------------------
with tab2:
    st.markdown("**Failure-mode ranking** - how well each FMEA signature matches the observed symptoms")
    hyp = pd.DataFrame(p.hypotheses).iloc[::-1]
    colors = [SERIES if f == d["fm_id"] else "#c9c8c3" for f in hyp["fm_id"]]
    fig = go.Figure(go.Bar(x=hyp["match_score"], y=hyp["fm_id"] + " " + hyp["name"], orientation="h",
                           marker=dict(color=colors, cornerradius=4),
                           customdata=hyp[["likelihood", "support", "explained"]],
                           hovertemplate="%{y}<br>Match %{x:.0%}<br>Likelihood %{customdata[0]:.0%}"
                                         "<br>Symptom support %{customdata[1]:.0%}"
                                         "<br>Abnormality explained %{customdata[2]:.0%}<extra></extra>",
                           text=[f"{v:.0%}" for v in hyp["match_score"]], textposition="outside"))
    fig.update_layout(height=330, margin=dict(l=10, r=40, t=10, b=10), xaxis=dict(range=[0, 1.12],
                      tickformat=".0%", showgrid=False), plot_bgcolor="rgba(0,0,0,0)", showlegend=False)
    st.plotly_chart(fig, width="stretch")

    st.markdown("**Symptom trends** for the leading hypothesis - blue = data the agent saw; grey = what actually happened next (hidden from the agent, shown here to check the forecast)")
    tags = [e["sensor"] for e in d["evidence"]] + d["unexplained"][:2]
    t_alert, t_now = pd.Timestamp(p.alert_time), pd.Timestamp(p.analysis_time)
    view = df[df.index >= df.index[0] + pd.Timedelta(days=20)]
    grid = st.columns(2)
    for i, tag in enumerate(tags):
        s = sensors[tag]
        y = view[tag].rolling("6h", min_periods=1).mean()
        f = go.Figure()
        seen, after = y[y.index <= t_now], y[y.index >= t_now]
        f.add_trace(go.Scatter(x=after.index, y=after, line=dict(color="#c9c8c3", width=1.5),
                               name="What actually happened (hidden from agent)",
                               hovertemplate="%{x|%d-%b %H:%M}<br>%{y:.2f} " + s["unit"] + " (future)<extra></extra>"))
        f.add_trace(go.Scatter(x=seen.index, y=seen, line=dict(color=SERIES, width=2), name="Data seen by agent",
                               hovertemplate="%{x|%d-%b %H:%M}<br>%{y:.2f} " + s["unit"] + "<extra></extra>"))
        for lim, col, nm in ((s.get("alarm"), WARNING, "Alarm"), (s.get("trip"), CRITICAL, "Trip")):
            if lim is not None:
                f.add_hline(y=lim, line=dict(color=col, dash="dash", width=1.5),
                            annotation_text=f"{nm} {lim}", annotation_position="top left")
        f.add_vline(x=t_alert, line=dict(color=MUTED, dash="dot", width=1.5))
        f.add_vline(x=t_now, line=dict(color=MUTED, width=1.5))
        f.add_annotation(x=t_alert, y=1.02, yref="paper", text="alert", showarrow=False, font=dict(color=MUTED))
        f.add_annotation(x=t_now, y=1.02, yref="paper", text="review", showarrow=False, font=dict(color=MUTED),
                         xanchor="left")
        verdict = next((e["verdict"] for e in d["evidence"] if e["sensor"] == tag), "unexplained")
        f.update_layout(title=f"{s['label']} ({s['unit']}) - {verdict}", height=250, showlegend=False,
                        margin=dict(l=10, r=10, t=40, b=10), plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(showgrid=False), yaxis=dict(gridcolor="rgba(128,128,128,0.15)"))
        grid[i % 2].plotly_chart(f, width="stretch")

    st.markdown("**Evidence table**")
    st.dataframe(pd.DataFrame(d["evidence"]).rename(columns={"z": "observed (sigma)"}), width="stretch",
                 hide_index=True)
    if p.forecast:
        st.markdown("**Time-to-limit forecast** (conservative: earlier of linear and curved trend)")
        st.dataframe(pd.DataFrame(p.forecast), width="stretch", hide_index=True)

# ---------------- History -----------------------------------------------------
with tab3:
    h = p.history
    m1, m2, m3 = st.columns(3)
    m1.metric(f"Same failure on {a['tag']} (36 mo)", h["count"])
    m2.metric("Cost of those events", f"${h['total_cost_usd']:,.0f}")
    m3.metric("Downtime", f"{h['total_downtime_h']:.0f} h")
    if h["bad_actor"]:
        st.warning("🔁 **Bad actor** - repeat failure. The agent adds a formal RCA to the defect-elimination plan.")
    st.markdown("**Similar past work orders across the fleet** (text search - finds uncoded records too)")
    st.dataframe(pd.DataFrame(p.similar_work_orders), width="stretch", hide_index=True)

# ---------------- Trace -------------------------------------------------------
with tab4:
    st.caption("Every step the agent took, in order - auditable reasoning, no black box.")
    for t in p.trace:
        st.markdown(f"**{t['step']}** · `{t['tool']}`  \n{t['result']}")

# ---------------- Report ------------------------------------------------------
with tab5:
    md = to_markdown(p)
    st.download_button("Download report (Markdown)", md, file_name=f"{a['tag']}_{choice}_assessment.md")
    st.markdown(md)
