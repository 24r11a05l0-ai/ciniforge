"""CineForge — AI Film Pre-Production Factory
Main Streamlit Application.
"""

import os
import json
import streamlit as st
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import pipeline and tools
from schemas import PipelineState
from pipeline import run_pipeline
from tools import extract_pdf_text, calculate_budget, generate_report, RATE_CARD, ACTOR_AVAILABILITY

# ═══════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="CineForge — AI Film Pre-Production Factory",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════════════════
# CUSTOM STYLING (CINEMATIC DARK MODE)
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
    /* Global Styles */
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }
    
    /* Header Banner */
    .header-banner {
        background: linear-gradient(135deg, #1e1b4b 0%, #311042 50%, #0f172a 100%);
        border: 1px solid #4338ca;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(67, 56, 202, 0.25);
    }
    .header-title {
        font-size: 2.4rem;
        font-weight: 800;
        background: linear-gradient(90deg, #818cf8, #c084fc, #f472b6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        letter-spacing: -0.02em;
    }
    .header-subtitle {
        color: #94a3b8;
        font-size: 1.05rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    
    /* Status Badges */
    .badge-pass {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        border: 1px solid #10b981;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-fail {
        background-color: rgba(239, 68, 68, 0.15);
        color: #ef4444;
        border: 1px solid #ef4444;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-repair {
        background-color: rgba(245, 158, 11, 0.15);
        color: #f59e0b;
        border: 1px solid #f59e0b;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    .badge-waiting {
        background-color: rgba(100, 116, 139, 0.15);
        color: #94a3b8;
        border: 1px solid #475569;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #6366f1;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38bdf8;
    }
    .metric-label {
        color: #94a3b8;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-top: 4px;
    }

    /* Agent Card Flow */
    .agent-card {
        background: #111827;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 14px;
        margin-bottom: 10px;
    }
    .agent-card-active {
        border-color: #818cf8;
        box-shadow: 0 0 12px rgba(129, 140, 248, 0.2);
    }
    .agent-card-success {
        border-color: #10b981;
    }
    .agent-card-repair {
        border-color: #f59e0b;
    }
    
    /* Logs & Code container */
    .log-box {
        background-color: #030712;
        border: 1px solid #1f2937;
        border-radius: 8px;
        padding: 12px;
        font-family: 'JetBrains Mono', monospace, sans-serif;
        font-size: 0.82rem;
        max-height: 250px;
        overflow-y: auto;
        color: #a7f3d0;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0f172a;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 6px;
        color: #94a3b8;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e1b4b !important;
        color: #818cf8 !important;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# INITIALIZE SESSION STATE
# ═══════════════════════════════════════════════════════════════════════
if "pipeline_state" not in st.session_state:
    st.session_state.pipeline_state = None
if "is_running" not in st.session_state:
    st.session_state.is_running = False


# ═══════════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("### 🎬 **CineForge Control**")
    st.caption("AI Pre-Production Factory")
    st.divider()

    # API Key Configuration
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        api_key_input = st.text_input("OpenAI API Key", type="password", help="Required to execute LLM agent pipeline")
        if api_key_input:
            os.environ["OPENAI_API_KEY"] = api_key_input
            api_key = api_key_input
    else:
        st.success("🔑 API Key Loaded", icon="✅")

    st.divider()

    # Input Screenplay Selection
    st.markdown("#### **1. Screenplay Source**")
    input_mode = st.radio(
        "Select Source",
        options=["Demo Screenplay (Conflict Test)", "Upload PDF Screenplay"],
        index=0
    )

    file_bytes = None
    file_name = ""

    if input_mode == "Demo Screenplay (Conflict Test)":
        demo_path = os.path.join("sample_data", "demo_screenplay.pdf")
        if os.path.exists(demo_path):
            with open(demo_path, "rb") as f:
                file_bytes = f.read()
            file_name = "demo_screenplay.pdf"
            st.info("💡 Demo Screenplay contains a deliberate scheduling conflict: *Sarah unavailable after 17:00 on Day 1*.", icon="🎭")
        else:
            st.error("Demo PDF not found. Click 'Generate Demo PDF' below.")
            if st.button("Generate Demo PDF"):
                import subprocess
                subprocess.run(["python", "create_demo_pdf.py"], check=True)
                st.rerun()
    else:
        uploaded_file = st.file_uploader("Upload Screenplay PDF", type=["pdf"])
        if uploaded_file is not None:
            file_bytes = uploaded_file.getvalue()
            file_name = uploaded_file.name

    st.divider()

    # Rate Card Customization Expander
    with st.expander("⚙️ Production Rate Card Settings"):
        st.caption("Standard rates used by Budget Agent")
        camera_rate = st.number_input("Camera / Day (₹)", value=RATE_CARD["camera_per_day"], step=500)
        crew_rate = st.number_input("Crew / Day (₹)", value=RATE_CARD["crew_per_day"], step=500)
        catering_rate = st.number_input("Catering / Person / Day (₹)", value=RATE_CARD["catering_per_person_per_day"], step=50)
        contingency_pct = st.slider("Contingency %", 5, 20, RATE_CARD["contingency_percent"])

    st.divider()

    # Action Buttons
    col_run, col_reset = st.columns([3, 1])
    with col_run:
        start_btn = st.button(
            "🚀 Run Pipeline",
            type="primary",
            use_container_width=True,
            disabled=(file_bytes is None or not api_key)
        )
    with col_reset:
        if st.button("🔄", help="Reset state"):
            st.session_state.pipeline_state = None
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# MAIN HEADER
# ═══════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="header-banner">
    <div class="header-title">🎬 CineForge</div>
    <div class="header-subtitle">Multi-Agent AI Film Pre-Production Factory • Screenplay to Production Package</div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════
# PIPELINE EXECUTION HANDLER
# ═══════════════════════════════════════════════════════════════════════
if start_btn and file_bytes:
    st.session_state.is_running = True
    progress_placeholder = st.empty()
    status_box = st.empty()

    def update_ui_status(agent, status, message):
        status_box.markdown(f"**Current Step:** `{agent}` — *{status}* — {message}")

    with st.spinner("⚡ Multi-Agent Pipeline active... Processing screenplay through agents..."):
        try:
            state = run_pipeline(file_bytes, status_callback=update_ui_status)
            st.session_state.pipeline_state = state
            st.success("🎉 Pre-production package generation complete!")
        except Exception as e:
            st.error(f"❌ Pipeline execution error: {e}")
        finally:
            st.session_state.is_running = False
            status_box.empty()
            st.rerun()


# ═══════════════════════════════════════════════════════════════════════
# MAIN CONTENT DISPLAY TABS
# ═══════════════════════════════════════════════════════════════════════
state: PipelineState = st.session_state.pipeline_state

if state is None:
    st.info("👈 **Get Started:** Select the Demo Screenplay or upload a script PDF in the sidebar and click **Run Pipeline**.", icon="💡")
    
    # Feature showcase grid when idle
    st.markdown("### 🛠️ Architecture & Multi-Agent Workflow")
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown("#### 🎭 1. Script Analyst")
        st.caption("Parses screenplay structure into structured Scenes, Characters, Locations, and Props.")
    with c2:
        st.markdown("#### 🎥 2. Shot Planner")
        st.caption("Generates cinematic shot list with camera movement, shot types, framing, & equipment.")
    with c3:
        st.markdown("#### 📅 3. Production Planner")
        st.caption("Groups scenes by location and optimizes daily shoot schedules against actor constraints.")
    with c4:
        st.markdown("#### 💰 4. Budget Agent")
        st.caption("Calculates equipment, crew, location, catering & contingency budget deterministically.")
    with c5:
        st.markdown("#### 🧪 5. Consistency Engine")
        st.caption("Runs deterministic validators & LLM checks, triggering self-repair loop on errors.")

else:
    # Top Overview Metrics Bar
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        scene_cnt = len(state.script_analysis.scenes) if state.script_analysis else 0
        st.markdown(f'<div class="metric-card"><div class="metric-value">{scene_cnt}</div><div class="metric-label">Scenes</div></div>', unsafe_allow_html=True)
    with m2:
        shot_cnt = len(state.shot_plan.shots) if state.shot_plan else 0
        st.markdown(f'<div class="metric-card"><div class="metric-value">{shot_cnt}</div><div class="metric-label">Total Shots</div></div>', unsafe_allow_html=True)
    with m3:
        days_cnt = state.production_schedule.total_shoot_days if state.production_schedule else 0
        st.markdown(f'<div class="metric-card"><div class="metric-value">{days_cnt}</div><div class="metric-label">Shoot Days</div></div>', unsafe_allow_html=True)
    with m4:
        budget_amt = f"₹{state.budget.total:,.0f}" if state.budget else "₹0"
        st.markdown(f'<div class="metric-card"><div class="metric-value">{budget_amt}</div><div class="metric-label">Total Budget</div></div>', unsafe_allow_html=True)
    with m5:
        status_html = ""
        if state.final_status == "PASS":
            status_html = '<span class="badge-pass">PASS ✓</span>'
        elif state.final_status == "HUMAN_REVIEW_REQUIRED":
            status_html = '<span class="badge-repair">REVIEW REQD ⚠</span>'
        else:
            status_html = '<span class="badge-fail">FAIL ❌</span>'
        st.markdown(f'<div class="metric-card"><div class="metric-value">{status_html}</div><div class="metric-label">Validation Status</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # TABS
    tab_ctrl, tab_script, tab_shots, tab_sched, tab_budget, tab_val, tab_export = st.tabs([
        "📊 Control Center",
        "🎭 Script Analysis",
        "🎥 Shot List",
        "📅 Shoot Schedule",
        "💰 Budget Breakdown",
        "🧪 Validation & Repair",
        "📦 Package & Export"
    ])

    # ═══════════════════════════════════════════════════════════════════
    # TAB 1: CONTROL CENTER
    # ═══════════════════════════════════════════════════════════════════
    with tab_ctrl:
        st.subheader("🤖 Agent Pipeline Status & Trace")
        
        col_flow, col_logs = st.columns([1, 1])
        
        with col_flow:
            st.markdown("##### **Agent Execution Hierarchy**")
            agents_info = [
                ("script_analyst", "🎭 1. Script Analyst Agent"),
                ("shot_planner", "🎥 2. Shot Planner Agent"),
                ("production_planner", "📅 3. Production Planner Agent"),
                ("budget_agent", "💰 4. Budget Calculation Agent"),
                ("consistency_agent", "🧪 5. Validation & Consistency Agent"),
            ]
            
            for key, label in agents_info:
                status = state.agent_statuses.get(key, "waiting")
                badge = f'<span class="badge-{status}">{status.upper()}</span>'
                css_cls = f"agent-card agent-card-{status}"
                st.markdown(
                    f'<div class="{css_cls}"><b>{label}</b> <div style="float:right;">{badge}</div></div>',
                    unsafe_allow_html=True
                )
            
            if state.repair_count > 0:
                st.warning(f"🔄 Self-Repair Triggered: Executed {state.repair_count} repair iteration(s).", icon="⚠")

        with col_logs:
            st.markdown("##### **Execution Console Log**")
            logs_str = "\n".join(state.execution_log)
            st.code(logs_str, language="bash")
            
            if state.repair_history:
                st.markdown("##### **Repair Loop Trace**")
                for item in state.repair_history:
                    st.text(f"• {item}")

    # ═══════════════════════════════════════════════════════════════════
    # TAB 2: SCRIPT ANALYSIS
    # ═══════════════════════════════════════════════════════════════════
    with tab_script:
        if state.script_analysis:
            st.markdown(f"### Screenplay: **{state.script_analysis.title}**")
            st.caption(f"Total Pages: {state.script_analysis.total_pages} | Overview: {state.script_analysis.summary}")
            
            st.divider()
            
            c_sec1, c_sec2 = st.columns([2, 1])
            
            with c_sec1:
                st.markdown("#### 🎬 Scene Breakdown")
                scenes_data = []
                for s in state.script_analysis.scenes:
                    scenes_data.append({
                        "Scene #": s.scene_number,
                        "Heading": s.heading,
                        "INT/EXT": s.int_ext,
                        "Time": s.time_of_day,
                        "Characters": ", ".join(s.character_names),
                        "Props": ", ".join(s.prop_names) if s.prop_names else "—",
                        "Est. Min": s.estimated_duration_minutes,
                    })
                st.dataframe(pd.DataFrame(scenes_data), use_container_width=True, hide_index=True)
            
            with c_sec2:
                st.markdown("#### 👥 Character Roster")
                for c in state.script_analysis.characters:
                    st.markdown(f"• **{c.name}** (`{c.id}`)")
                    if c.description:
                        st.caption(f"  {c.description}")
                
                st.markdown("#### 📍 Locations")
                for loc in state.script_analysis.locations:
                    st.markdown(f"• **{loc.name}** (`{loc.int_ext}`)")
                
                if state.script_analysis.props:
                    st.markdown("#### 📦 Key Props")
                    for pr in state.script_analysis.props:
                        st.markdown(f"• {pr.name}")

    # ═══════════════════════════════════════════════════════════════════
    # TAB 3: SHOT LIST
    # ═══════════════════════════════════════════════════════════════════
    with tab_shots:
        if state.shot_plan:
            st.markdown("### 🎥 Production Shot List")
            st.caption(f"Total Shots Planned: {state.shot_plan.total_shots}")
            
            shots_data = []
            for sh in state.shot_plan.shots:
                shots_data.append({
                    "Shot ID": sh.id,
                    "Scene ID": sh.scene_id,
                    "Shot Type": sh.shot_type,
                    "Camera Angle": sh.camera_angle,
                    "Camera Movement": sh.camera_movement,
                    "Subjects": ", ".join(sh.subjects),
                    "Equipment Required": ", ".join(sh.equipment),
                    "Est. Setup (min)": sh.estimated_setup_minutes,
                    "Direct Fact?": "Yes" if sh.is_screenplay_fact else "Inferred",
                    "Rationale": sh.rationale
                })
            
            df_shots = pd.DataFrame(shots_data)
            
            # Filter by Scene
            scene_filter = st.selectbox(
                "Filter Shots by Scene",
                options=["All Scenes"] + sorted(list(set(df_shots["Scene ID"])))
            )
            
            if scene_filter != "All Scenes":
                df_shots = df_shots[df_shots["Scene ID"] == scene_filter]
                
            st.dataframe(df_shots, use_container_width=True, hide_index=True)

    # ═══════════════════════════════════════════════════════════════════
    # TAB 4: SHOOT SCHEDULE
    # ═══════════════════════════════════════════════════════════════════
    with tab_sched:
        if state.production_schedule:
            st.markdown("### 📅 Production Shooting Schedule")
            st.caption(f"Total Shoot Days: {state.production_schedule.total_shoot_days} | Optimized for Location Continuity")
            
            # Display days as tabs
            day_tabs = st.tabs([f"Day {d.day_number}: {d.location_name}" for d in state.production_schedule.shoot_days])
            
            for idx, day in enumerate(state.production_schedule.shoot_days):
                with day_tabs[idx]:
                    st.markdown(f"#### **Day {day.day_number} — Location: {day.location_name}**")
                    st.caption(f"Total Estimated Shooting Time: {day.estimated_total_minutes} minutes ({day.estimated_total_minutes/60:.1f} hrs)")
                    if day.notes:
                        st.info(f"📌 Schedule Notes: {day.notes}")
                    
                    sc_data = []
                    for sc in day.scenes:
                        # Find original scene info
                        orig_sc = next((s for s in state.script_analysis.scenes if s.id == sc.scene_id), None) if state.script_analysis else None
                        chars = ", ".join(orig_sc.character_names) if orig_sc else "N/A"
                        heading = orig_sc.heading if orig_sc else "N/A"
                        
                        sc_data.append({
                            "Start Time": sc.start_time,
                            "Scene ID": sc.scene_id,
                            "Scene Heading": heading,
                            "Cast Members": chars,
                            "Shots Count": len(sc.shots),
                            "Duration (min)": sc.estimated_duration_minutes
                        })
                    st.dataframe(pd.DataFrame(sc_data), use_container_width=True, hide_index=True)

    # ═══════════════════════════════════════════════════════════════════
    # TAB 5: BUDGET BREAKDOWN
    # ═══════════════════════════════════════════════════════════════════
    with tab_budget:
        if state.budget:
            st.markdown("### 💰 Production Budget")
            
            b_col1, b_col2, b_col3 = st.columns(3)
            with b_col1:
                st.metric("Subtotal Cost", f"₹{state.budget.subtotal:,.2f}")
            with b_col2:
                st.metric(f"Contingency ({state.budget.contingency_percent}%)", f"₹{state.budget.contingency_amount:,.2f}")
            with b_col3:
                st.metric("Grand Total Cost", f"₹{state.budget.total:,.2f}")
                
            st.divider()
            
            budget_items = []
            for item in state.budget.line_items:
                budget_items.append({
                    "Category": item.category,
                    "Description": item.description,
                    "Quantity": item.quantity,
                    "Unit Cost (₹)": f"₹{item.unit_cost:,.2f}",
                    "Total Cost (₹)": f"₹{item.total_cost:,.2f}"
                })
            
            st.dataframe(pd.DataFrame(budget_items), use_container_width=True, hide_index=True)

    # ═══════════════════════════════════════════════════════════════════
    # TAB 6: VALIDATION & REPAIR ENGINE
    # ═══════════════════════════════════════════════════════════════════
    with tab_val:
        if state.validation_result:
            st.markdown("### 🧪 Validation & Multi-Agent Consistency Report")
            
            if state.validation_result.status == "PASS":
                st.success("✅ **VALIDATION PASSED** — All scenes, cast availability, setup times, and budget items are aligned!", icon="🎉")
            else:
                st.error(f"❌ **VALIDATION ISSUES DETECTED** ({len(state.validation_result.issues)} issues found)", icon="⚠️")
                
            st.caption(f"Summary: {state.validation_result.summary}")
            
            st.divider()
            
            if state.validation_result.issues:
                st.markdown("#### **Detailed Issues Audit**")
                for issue in state.validation_result.issues:
                    sev_icon = "🔴" if issue.severity == "ERROR" else ("🟡" if issue.severity == "WARNING" else "🔵")
                    with st.expander(f"{sev_icon} [{issue.severity}] {issue.category}: {issue.message[:80]}..."):
                        st.write(f"**Full Description:** {issue.message}")
                        st.write(f"**Affected Scenes:** {', '.join(issue.scene_ids) if issue.scene_ids else 'N/A'}")
                        st.write(f"**Responsible Agent:** `{issue.responsible_agent}`")
                        if issue.suggested_fix:
                            st.info(f"💡 **Suggested Fix:** {issue.suggested_fix}")

    # ═══════════════════════════════════════════════════════════════════
    # TAB 7: PACKAGE & EXPORT
    # ═══════════════════════════════════════════════════════════════════
    with tab_export:
        st.markdown("### 📦 Export Production Package")
        st.caption("Download the complete pre-production package for distribution to crew & department heads.")
        
        ex_col1, ex_col2 = st.columns(2)
        
        with ex_col1:
            st.markdown("#### 📄 Executive Summary Report (PDF)")
            st.caption("Includes Scene Breakdown, Daily Call Sheet, Shot Summary & Budget Total.")
            
            pdf_bytes = generate_report(state)
            st.download_button(
                label="📥 Download Production Report (PDF)",
                data=pdf_bytes,
                file_name="CineForge_Production_Package.pdf",
                mime="application/pdf",
                use_container_width=True
            )
            
        with ex_col2:
            st.markdown("#### 🤖 Full Production Data (JSON)")
            st.caption("Complete raw JSON schema output for integration into film scheduling software.")
            
            json_str = state.model_dump_json(indent=2)
            st.download_button(
                label="📥 Download Data Package (JSON)",
                data=json_str,
                file_name="cineforge_package.json",
                mime="application/json",
                use_container_width=True
            )
