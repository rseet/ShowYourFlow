import streamlit as st
import json
from datetime import datetime, date
import os

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Show Your Flow",
    page_icon="⚜️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── Styling ───────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,400;0,600;1,400;1,600&family=DM+Mono:wght@300;400&display=swap');

html, body, [class*="css"] {
    font-family: 'Georgia', serif;
    background-color: #0e0c0a;
    color: #e8e0d4;
}

.stApp { background-color: #0e0c0a; }

h1, h2, h3 {
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    color: #f0e8dc !important;
}

.stButton > button {
    background-color: #C4A55A;
    color: #1a1510;
    border: none;
    border-radius: 8px;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 10px 24px;
    transition: all 0.2s;
}
.stButton > button:hover { background-color: #d4b56a; }

.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
    background-color: #1a1510 !important;
    border: 1px solid #2e2820 !important;
    border-radius: 8px !important;
    color: #ddd5c5 !important;
    font-family: 'Georgia', serif !important;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: #C4A55A !important;
}

.stRadio > div { flex-direction: row; gap: 20px; }
.stRadio label { color: #c8bfb0 !important; }

div[data-testid="stHorizontalBlock"] { gap: 16px; }

.metric-card {
    background: #161210;
    border: 1px solid #2e2820;
    border-radius: 12px;
    padding: 16px 20px;
    margin-bottom: 12px;
}

.gold-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    color: #C4A55A;
    margin-bottom: 4px;
}

.submission-card {
    background: #161210;
    border: 1px solid #2e2820;
    border-left: 3px solid #C4A55A;
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 14px;
}

.submission-card.selected { border-left-color: #4caf78; }
.submission-card.pending  { border-left-color: #c4852a; }
.submission-card.passed   { border-left-color: #3a3028; }

.badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    padding: 2px 10px;
    border-radius: 20px;
    border: 1px solid;
}

.divider {
    border: none;
    border-top: 1px solid #2e2820;
    margin: 20px 0;
}

[data-testid="stSidebar"] { background-color: #0e0c0a; }
.stTabs [data-baseweb="tab-list"] { background-color: #0e0c0a; gap: 8px; }
.stTabs [data-baseweb="tab"] {
    background-color: #161210;
    border-radius: 20px;
    border: 1px solid #2e2820;
    color: #7a7060;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 6px 16px;
}
.stTabs [aria-selected="true"] {
    background-color: #2a2318 !important;
    border-color: #C4A55A !important;
    color: #C4A55A !important;
}

.stCheckbox label { color: #c8bfb0 !important; font-size: 13px; }
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
TEAMS = [
    "Equities", "Fixed Income", "Private Equity", "Real Assets",
    "Multi-Asset", "Research", "Risk", "Portfolio Management", "Other"
]

ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "aiworkingteam2026")

PRINCIPLES = [
    ("Show, don't tell", "The output speaks for itself. No slides explaining what you did. Show the actual thing."),
    ("Business outcome first", "Every showcase must answer: so what? Time saved, decision improved, work elevated."),
    ("Real work only", "No toy examples built for the session. It must have solved a real problem at KNB."),
    ("Concise by design", "10 minutes per showcase maximum. Respect the room's time."),
    ("No polish required", "Messy workflows are fine. We're here to learn, not to impress."),
    ("Scalability lens", "The facilitator will always ask: could this work for other teams? That's the point."),
    ("Failures welcome", "If Claude didn't work, or you hit a blocker — that's worth sharing too. Honest beats polished."),
]

CHECKLIST_SUBMIT = [
    "I can describe my problem in one sentence",
    "I have the actual output ready to show — not a description of it",
    "I know my before/after — time, effort, or quality difference",
    "I have noted any blockers or failures encountered along the way",
    "I have decided: live demo or screen recording",
]

CHECKLIST_LIVE = [
    "Claude is open and ready on my screen",
    "I have the original input / prompt ready to walk through",
    "I can show the output side by side with the original problem",
    "I have timed myself — under 10 minutes",
    "I can answer: which other teams could use this?",
    "If I hit a blocker or failure, I'm prepared to share what I tried and what didn't work",
]

# ── Data helpers ──────────────────────────────────────────────────────────────
DATA_FILE = "submissions.json"

def load_submissions():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []

def save_submissions(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def get_week_label():
    today = date.today()
    week = today.isocalendar()[1]
    return f"{today.year}-W{str(week).padStart(2, '0')}" if False else f"{today.year}-W{week:02d}"

def status_emoji(status):
    return {"selected": "🟢", "pending": "🟡", "passed": "⚫"}.get(status, "⚫")

# ── Session state ─────────────────────────────────────────────────────────────
if "submissions" not in st.session_state:
    st.session_state.submissions = load_submissions()
if "admin_unlocked" not in st.session_state:
    st.session_state.admin_unlocked = False

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="border-bottom: 1px solid #2e2820; padding-bottom: 20px; margin-bottom: 28px;">
    <div class="gold-label">KNB Investments · Claude Enterprise</div>
    <h1 style="font-size: 36px; font-weight: 600; margin: 4px 0 0;">Show Your Flow ⚜️</h1>
    <div style="font-family: 'DM Mono', monospace; font-size: 11px; color: #7a7060; margin-top: 6px;">
        Submit by EOD Wednesday · Session every Friday · No slides — show the real thing
    </div>
</div>
""", unsafe_allow_html=True)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab_submit, tab_review, tab_log, tab_guide = st.tabs(["📤 Submit", "🔍 Review", "📋 All Submissions", "📖 Guide"])

# ════════════════════════════════════════════════════════════════════════════════
# TAB 1 — SUBMIT
# ════════════════════════════════════════════════════════════════════════════════
with tab_submit:
    st.markdown("### Submit your flow")
    st.markdown("<div style='font-family: DM Mono, monospace; font-size: 11px; color: #7a7060; margin-bottom: 24px;'>Fill in the form below. Fields marked * are required.</div>", unsafe_allow_html=True)

    # Pre-submit checklist
    with st.expander("✅ Before you submit — checklist", expanded=False):
        for item in CHECKLIST_SUBMIT:
            st.checkbox(item, key=f"check_submit_{item[:20]}")

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Your name *", placeholder="e.g. Sarah Tan")
    with col2:
        team = st.selectbox("Your team *", [""] + TEAMS)

    problem = st.text_area("What problem were you solving? *",
        placeholder="One clear sentence — what was the task or pain point?", height=80)

    output = st.text_area("What did you produce? Show the output. *",
        placeholder="Describe the actual output — a doc, analysis, draft, summary. Be specific.", height=100)

    before = st.text_input("How long / painful was this before Claude? *",
        placeholder="e.g. 2 hours of manual work, now done in 5 minutes")

    blocker = st.text_area("Any blockers or failures? (optional but encouraged)",
        placeholder="What didn't work? Where did Claude fall short? What did you have to work around? Honest answers make better sessions.",
        height=80)

    prompt = st.text_area("Share your prompt or workflow (optional — helps us scale what works)",
        placeholder="Paste the prompt or workflow you used. No Git required — just copy and paste.",
        height=100)

    format_choice = st.radio("How will you present?", ["🎤 Live demo", "🎬 Screen recording"])

    if format_choice == "🎤 Live demo":
        with st.expander("✅ If presenting live — checklist", expanded=False):
            for item in CHECKLIST_LIVE:
                st.checkbox(item, key=f"check_live_{item[:20]}")

    st.markdown("<br>", unsafe_allow_html=True)

    if st.button("Submit My Flow →", use_container_width=True):
        if not name or not team or not problem or not output or not before:
            st.error("Please fill in all required fields before submitting.")
        else:
            entry = {
                "id": str(datetime.now().timestamp()),
                "name": name,
                "team": team,
                "week": get_week_label(),
                "problem": problem,
                "output": output,
                "before": before,
                "blocker": blocker,
                "prompt": prompt,
                "format": "live" if "Live" in format_choice else "recorded",
                "status": "pending",
                "submitted_at": datetime.now().isoformat()
            }
            st.session_state.submissions.append(entry)
            save_submissions(st.session_state.submissions)
            st.success("⚜️ Flow submitted. The AI Working Team will review and confirm selected showcases by Thursday.")
            st.balloons()

# ════════════════════════════════════════════════════════════════════════════════
# TAB 2 — REVIEW (Admin)
# ════════════════════════════════════════════════════════════════════════════════
with tab_review:
    st.markdown("### Review submissions")

    if not st.session_state.admin_unlocked:
        st.markdown("<div style='max-width: 360px; margin: 40px auto; text-align: center;'>", unsafe_allow_html=True)
        st.markdown("🔒 **AI Working Team access only**")
        pwd = st.text_input("Access code", type="password", key="admin_pwd")
        if st.button("Unlock", key="unlock_btn"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.admin_unlocked = True
                st.rerun()
            else:
                st.error("Incorrect code")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        current_week = get_week_label()
        week_subs = [s for s in st.session_state.submissions if s.get("week") == current_week]

        selected = [s for s in week_subs if s["status"] == "selected"]
        pending  = [s for s in week_subs if s["status"] == "pending"]
        passed   = [s for s in week_subs if s["status"] == "passed"]

        col1, col2, col3 = st.columns(3)
        col1.metric("🟢 Selected", len(selected))
        col2.metric("🟡 Pending", len(pending))
        col3.metric("⚫ Passed", len(passed))

        st.markdown("<hr class='divider'>", unsafe_allow_html=True)

        if not week_subs:
            st.info("No submissions yet this week.")
        else:
            for s in week_subs:
                with st.container():
                    st.markdown(f"""
                    <div class="submission-card {s['status']}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                            <div>
                                <span style="font-family: Cormorant Garamond, serif; font-size: 18px; font-weight: 600; color: #f0e8dc;">{s['name']}</span>
                                <span style="font-family: DM Mono, monospace; font-size: 10px; color: #7a7060; margin-left: 10px;">{s['team']} · {'🎤 Live' if s['format'] == 'live' else '🎬 Recorded'}</span>
                            </div>
                            <span style="font-family: DM Mono, monospace; font-size: 10px; color: #7a7060;">{status_emoji(s['status'])} {s['status'].upper()}</span>
                        </div>
                        <div class="gold-label">Problem</div>
                        <div style="font-size: 13.5px; color: #c8bfb0; margin-bottom: 10px; line-height: 1.65;">{s['problem']}</div>
                        <div class="gold-label">Output</div>
                        <div style="font-size: 13.5px; color: #c8bfb0; margin-bottom: 10px; line-height: 1.65;">{s['output']}</div>
                        <div class="gold-label">Before Claude</div>
                        <div style="font-size: 13.5px; color: #c8bfb0; margin-bottom: 10px; line-height: 1.65;">{s['before']}</div>
                        {f'<div class="gold-label" style="color: #e07070;">Blocker / Failure</div><div style="font-size: 13.5px; color: #c8bfb0; margin-bottom: 10px; line-height: 1.65;">{s["blocker"]}</div>' if s.get("blocker") else ""}
                        {f'<div class="gold-label" style="color: #5a8ab0;">Prompt / Workflow</div><div style="font-size: 13px; color: #c8bfb0; margin-bottom: 10px; line-height: 1.65; font-family: DM Mono, monospace; white-space: pre-wrap;">{s["prompt"]}</div>' if s.get("prompt") else ""}
                    </div>
                    """, unsafe_allow_html=True)

                    c1, c2, c3, _ = st.columns([1, 1, 1, 3])
                    with c1:
                        if s["status"] != "selected":
                            if st.button("✅ Select", key=f"sel_{s['id']}"):
                                for sub in st.session_state.submissions:
                                    if sub["id"] == s["id"]: sub["status"] = "selected"
                                save_submissions(st.session_state.submissions)
                                st.rerun()
                    with c2:
                        if s["status"] != "pending":
                            if st.button("↩ Reset", key=f"res_{s['id']}"):
                                for sub in st.session_state.submissions:
                                    if sub["id"] == s["id"]: sub["status"] = "pending"
                                save_submissions(st.session_state.submissions)
                                st.rerun()
                    with c3:
                        if s["status"] != "passed":
                            if st.button("✖ Pass", key=f"pass_{s['id']}"):
                                for sub in st.session_state.submissions:
                                    if sub["id"] == s["id"]: sub["status"] = "passed"
                                save_submissions(st.session_state.submissions)
                                st.rerun()

# ════════════════════════════════════════════════════════════════════════════════
# TAB 3 — ALL SUBMISSIONS LOG
# ════════════════════════════════════════════════════════════════════════════════
with tab_log:
    st.markdown("### All submissions")
    st.markdown(f"<div style='font-family: DM Mono, monospace; font-size: 11px; color: #7a7060; margin-bottom: 24px;'>{len(st.session_state.submissions)} total · Your evidence base for the Steerco</div>", unsafe_allow_html=True)

    if not st.session_state.submissions:
        st.info("No submissions yet.")
    else:
        # Group by week
        weeks = {}
        for s in st.session_state.submissions:
            w = s.get("week", "Unknown")
            if w not in weeks: weeks[w] = []
            weeks[w].append(s)

        for week in sorted(weeks.keys(), reverse=True):
            st.markdown(f"<div class='gold-label' style='margin-bottom: 12px;'>{week}</div>", unsafe_allow_html=True)
            for s in weeks[week]:
                with st.expander(f"{status_emoji(s['status'])}  {s['name']} — {s['team']}"):
                    st.markdown(f"**Problem:** {s['problem']}")
                    st.markdown(f"**Output:** {s['output']}")
                    st.markdown(f"**Before Claude:** {s['before']}")
                    if s.get("blocker"):
                        st.markdown(f"🔴 **Blocker:** {s['blocker']}")
                    if s.get("prompt"):
                        st.markdown(f"🔵 **Prompt / Workflow:**")
                        st.code(s["prompt"], language=None)
                    st.markdown(f"*Format: {'Live demo' if s['format'] == 'live' else 'Screen recording'} · Status: {s['status'].upper()}*")
            st.markdown("<hr class='divider'>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB 4 — GUIDE
# ════════════════════════════════════════════════════════════════════════════════
with tab_guide:
    st.markdown("### How Show Your Flow works")
    st.markdown("<div style='font-family: DM Mono, monospace; font-size: 11px; color: #7a7060; margin-bottom: 28px;'>Read this before your first submission.</div>", unsafe_allow_html=True)

    st.markdown("#### Principles")
    for i, (title, desc) in enumerate(PRINCIPLES):
        st.markdown(f"""
        <div style="display: flex; gap: 16px; padding: 12px 0; border-bottom: 1px solid #1e1a12;">
            <div style="font-family: DM Mono, monospace; font-size: 10px; color: #C4A55A; width: 24px; flex-shrink: 0; margin-top: 3px;">{str(i+1).zfill(2)}</div>
            <div>
                <div style="font-family: Cormorant Garamond, serif; font-size: 16px; font-style: italic; font-weight: 600; color: #f0e8dc; margin-bottom: 4px;">{title}</div>
                <div style="font-size: 13px; color: #c8bfb0; line-height: 1.65;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Before you submit")
    for item in CHECKLIST_SUBMIT:
        st.markdown(f"→ {item}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### If presenting live on Friday")
    for item in CHECKLIST_LIVE:
        st.markdown(f"→ {item}")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Weekly cadence")
    st.markdown("""
    | Day | What happens |
    |-----|-------------|
    | Wednesday EOD | Submit your flow via this app |
    | Thursday | AI Working Team reviews and selects showcases |
    | Friday | Show Your Flow — 60 min, hybrid session |
    """)
