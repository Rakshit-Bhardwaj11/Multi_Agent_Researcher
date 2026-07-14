import streamlit as st
import time
from agents import build_reader_agent, build_search_agent, writer_chain, critic_chain

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="SignalDesk · ICE Research Assistant",
    page_icon="◇",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── ICE concept library ────────────────────────────────────────────────────────
# Core-subject topics for Instrumentation & Control Engineering, grouped by area.
ICE_TOPICS = {
    "Control Systems": [
        "PID controller tuning methods",
        "State-space feedback control",
        "Root locus design technique",
        "Bode plot stability analysis",
        "Kalman filtering for state estimation",
        "Model predictive control basics",
    ],
    "Instrumentation": [
        "Sensor calibration techniques",
        "Thermocouples vs RTDs",
        "Piezoelectric sensors",
        "LVDT displacement sensors",
        "Smart transmitters in process control",
    ],
    "Signal Processing": [
        "Digital filter design",
        "FFT-based spectral analysis",
        "Sampling and aliasing",
        "Noise reduction in sensor data",
    ],
    "Power Electronics": [
        "Interleaved bidirectional buck-boost converters",
        "SPWM inverter design",
        "MOSFET switching losses",
        "Multi-phase DC-DC converter topologies",
    ],
    "Industrial Automation": [
        "PLC ladder logic programming",
        "SCADA system architecture",
        "DCS vs PLC comparison",
        "Modbus and OPC-UA protocols",
    ],
    "Robotics & Mechatronics": [
        "Servo motor control",
        "Encoder-based position feedback",
        "Robotic arm kinematics",
    ],
}
_PLACEHOLDER = "Search the ICE concept library…"
_ICE_FLAT_OPTIONS = [_PLACEHOLDER] + [
    f"{area} · {topic}" for area, topics in ICE_TOPICS.items() for topic in topics
]

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Source+Sans+3:ital,wght@0,300;0,400;0,500;0,600;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Source Sans 3', sans-serif;
    color: #e6e2d8;
}

.stApp {
    background-color: #0a0e11;
    background-image:
        linear-gradient(rgba(255,255,255,0.025) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255,255,255,0.025) 1px, transparent 1px),
        radial-gradient(ellipse 70% 45% at 15% -8%, rgba(240,168,87,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 55% 35% at 85% 108%, rgba(92,201,184,0.07) 0%, transparent 55%);
    background-size: 42px 42px, 42px 42px, auto, auto;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 3rem 4rem; max-width: 1180px; }

/* ── Hero ── */
.hero { text-align: center; padding: 1.8rem 0 1.6rem; }
.hero-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    font-weight: 500;
    letter-spacing: 0.26em;
    text-transform: uppercase;
    color: #f0a857;
    margin-bottom: 0.9rem;
}
.hero h1 {
    font-family: 'Space Grotesk', sans-serif;
    font-size: clamp(2.2rem, 4.4vw, 3.3rem);
    font-weight: 700;
    line-height: 1.05;
    letter-spacing: -0.01em;
    color: #f2efe6;
    margin: 0 0 0.8rem;
}
.hero h1 span { color: #f0a857; }
.hero-sub {
    font-size: 0.96rem;
    font-weight: 300;
    color: #a09986;
    max-width: 560px;
    margin: 0 auto;
    line-height: 1.65;
}

/* ── Signal chain diagram ── */
.chain-wrap {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 0;
    margin: 1.8rem 0 0.4rem;
}
.chain-node {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.5rem 0.9rem;
    border: 1px solid rgba(255,255,255,0.12);
    border-radius: 3px;
    color: #8a8477;
    background: rgba(255,255,255,0.02);
}
.chain-node.io { color: #7a7364; border-style: dashed; }
.chain-node.stage { color: #d8d3c6; border-color: rgba(240,168,87,0.3); }
.chain-arrow { color: #4a453c; font-size: 0.85rem; padding: 0 0.5rem; }

/* ── Divider ── */
.divider {
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(240,168,87,0.22), transparent);
    margin: 2.1rem 0;
}

/* ── Input card ── */
.input-card {
    background: rgba(255,255,255,0.022);
    border: 1px solid rgba(240,168,87,0.16);
    border-radius: 4px;
    padding: 1.7rem 2rem;
    margin-bottom: 1rem;
}
.field-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.66rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #f0a857;
    margin: 0.9rem 0 0.3rem;
}
.field-label:first-child { margin-top: 0; }

.stTextInput > div > div > input {
    background: rgba(255,255,255,0.035) !important;
    border: 1px solid rgba(240,168,87,0.28) !important;
    border-radius: 3px !important;
    color: #f2efe6 !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 1rem !important;
    padding: 0.7rem 1rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #f0a857 !important;
    box-shadow: 0 0 0 3px rgba(240,168,87,0.1) !important;
}
.stTextInput > label { display: none !important; }

.stSelectbox > div > div {
    background: rgba(255,255,255,0.035) !important;
    border: 1px solid rgba(92,201,184,0.28) !important;
    border-radius: 3px !important;
}
.stSelectbox > label { display: none !important; }

.stButton > button {
    background: #f0a857 !important;
    color: #0a0e11 !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border: none !important;
    border-radius: 3px !important;
    padding: 0.75rem 2rem !important;
    width: 100%;
    margin-top: 0.6rem;
    transition: background 0.15s, transform 0.15s !important;
}
.stButton > button:hover { background: #f6bc7d !important; transform: translateY(-1px) !important; }

/* Small chip-style buttons for quick topics */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background: rgba(255,255,255,0.035) !important;
    color: #b8b2a2 !important;
    font-size: 0.72rem !important;
    padding: 0.4rem 0.7rem !important;
    margin-top: 0 !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    text-transform: none !important;
    letter-spacing: 0.02em !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    border-color: #f0a857 !important;
    color: #f0a857 !important;
    transform: none !important;
}

.footnote {
    font-size: 0.79rem;
    color: #6f6a5d;
    line-height: 1.6;
    padding-top: 0.7rem;
    margin-top: 0.5rem;
    border-top: 1px solid rgba(255,255,255,0.06);
}
.footnote b { color: #a09986; font-weight: 500; }

/* ── Section heading ── */
.section-heading {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #f2efe6;
    margin: 0 0 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.07);
}

/* ── Signal chain rail (pipeline status) ── */
.step-row { display: flex; align-items: stretch; gap: 1rem; margin-bottom: 0.7rem; }
.step-rail { width: 18px; flex-shrink: 0; position: relative; display: flex; justify-content: center; }
.step-dot {
    position: absolute; top: 1.3rem; width: 9px; height: 9px; border-radius: 50%;
    background: #0a0e11; border: 2px solid #3a362d; z-index: 2;
    transition: background 0.3s, border-color 0.3s, box-shadow 0.3s;
}
.step-dot.active { border-color: #f0a857; box-shadow: 0 0 0 3px rgba(240,168,87,0.15); }
.step-dot.done { background: #5cc9b8; border-color: #5cc9b8; }
.step-line {
    position: absolute; top: 1.3rem; width: 1px; height: calc(100% - 0.55rem);
    background: rgba(255,255,255,0.08); z-index: 1;
}
.step-line.done { background: #5cc9b8; }
.step-content {
    flex: 1; background: rgba(255,255,255,0.018); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 3px; padding: 1.05rem 1.3rem; transition: border-color 0.3s, background 0.3s;
}
.step-content.active { border-color: rgba(240,168,87,0.32); background: rgba(240,168,87,0.04); }
.step-content.done { border-color: rgba(92,201,184,0.28); background: rgba(92,201,184,0.035); }
.step-header { display: flex; align-items: baseline; gap: 0.85rem; margin-bottom: 0.2rem; }
.step-num {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; font-weight: 500;
    letter-spacing: 0.1em; color: #f0a857; opacity: 0.75;
}
.step-title { font-family: 'Space Grotesk', sans-serif; font-size: 0.96rem; font-weight: 600; color: #f2efe6; }
.step-status {
    margin-left: auto; font-family: 'IBM Plex Mono', monospace; font-size: 0.62rem;
    letter-spacing: 0.1em; text-transform: uppercase;
}
.status-waiting { color: #4a453c; }
.status-running { color: #f0a857; }
.status-done { color: #5cc9b8; }
.step-desc { font-size: 0.79rem; color: #756f61; margin-top: 0.25rem; }

/* ── Result panels ── */
.result-panel {
    background: rgba(255,255,255,0.016); border: 1px solid rgba(255,255,255,0.06);
    border-radius: 3px; padding: 1.5rem 1.8rem; margin-top: 0.8rem; margin-bottom: 1.2rem;
}
.result-panel-title {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.65rem; font-weight: 500;
    letter-spacing: 0.16em; text-transform: uppercase; color: #f0a857;
    margin-bottom: 0.85rem; padding-bottom: 0.55rem; border-bottom: 1px solid rgba(240,168,87,0.15);
}
.result-content {
    font-size: 0.89rem; line-height: 1.7; color: #c7c2b6; white-space: pre-wrap;
}

.report-panel {
    background: rgba(255,255,255,0.016); border: 1px solid rgba(240,168,87,0.22);
    border-radius: 4px; padding: 1.9rem 2.3rem; margin-top: 0.8rem;
}
.feedback-panel {
    background: rgba(255,255,255,0.016); border: 1px solid rgba(92,201,184,0.26);
    border-radius: 4px; padding: 1.9rem 2.3rem; margin-top: 0.8rem;
}
.panel-label {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.66rem; letter-spacing: 0.16em;
    text-transform: uppercase; margin-bottom: 1rem; padding-bottom: 0.6rem;
}
.panel-label.amber { color: #f0a857; border-bottom: 1px solid rgba(240,168,87,0.18); }
.panel-label.teal { color: #5cc9b8; border-bottom: 1px solid rgba(92,201,184,0.2); }

.stSpinner > div { color: #f0a857 !important; }
details summary {
    font-family: 'IBM Plex Mono', monospace !important; font-size: 0.71rem !important;
    color: #9c9488 !important; letter-spacing: 0.06em !important;
}
.notice {
    font-family: 'IBM Plex Mono', monospace; font-size: 0.67rem; color: #4e4a41;
    text-align: center; margin-top: 3rem; letter-spacing: 0.1em;
}
</style>
""", unsafe_allow_html=True)


# ── Helper: render a signal-chain step row ────────────────────────────────────
def step_card(num: str, title: str, state: str, desc: str = "", is_last: bool = False):
    status_map = {
        "waiting": ("PENDING", "status-waiting"),
        "running": ("IN PROGRESS", "status-running"),
        "done":    ("COMPLETE",   "status-done"),
    }
    label, cls = status_map.get(state, ("", ""))
    dot_cls = {"running": "active", "done": "done"}.get(state, "")
    line_cls = "done" if state == "done" else ""
    line_html = f'<div class="step-line {line_cls}"></div>' if not is_last else ""
    desc_html = f"<div class='step-desc'>{desc}</div>" if desc else ""
    # Built as a single unbroken line on purpose: a blank line anywhere inside
    # a markdown HTML block makes Streamlit stop parsing it as HTML and dump
    # the rest as literal text, which is what was leaking as a raw code box.
    row_html = (
        f'<div class="step-row">'
        f'<div class="step-rail"><div class="step-dot {dot_cls}"></div>{line_html}</div>'
        f'<div class="step-content {dot_cls}">'
        f'<div class="step-header">'
        f'<span class="step-num">{num}</span>'
        f'<span class="step-title">{title}</span>'
        f'<span class="step-status {cls}">{label}</span>'
        f'</div>{desc_html}</div>'
        f'</div>'
    )
    st.markdown(row_html, unsafe_allow_html=True)


# ── Session state init ────────────────────────────────────────────────────────
for key in ("results", "running", "done"):
    if key not in st.session_state:
        st.session_state[key] = {} if key == "results" else False
if "pending_topic" not in st.session_state:
    st.session_state.pending_topic = None
if "_last_concept" not in st.session_state:
    st.session_state._last_concept = _PLACEHOLDER

# Apply any pending topic (from a quick-pick chip or the ICE concept dropdown)
# BEFORE the text_input widget is instantiated below — this is the only safe
# point to set a widget's session_state value for its own key.
if st.session_state.pending_topic:
    st.session_state["topic_input"] = st.session_state.pending_topic
    st.session_state.pending_topic = None


# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">ICE Research Assistant</div>
    <h1>Signal<span>Desk</span></h1>
    <p class="hero-sub">
        A four-stage agent pipeline for Instrumentation &amp; Control Engineering
        research — search, read, draft, and review, chained like a signal path.
    </p>
    <div class="chain-wrap">
        <div class="chain-node io">Topic</div><div class="chain-arrow">→</div>
        <div class="chain-node stage">Search</div><div class="chain-arrow">→</div>
        <div class="chain-node stage">Read</div><div class="chain-arrow">→</div>
        <div class="chain-node stage">Write</div><div class="chain-arrow">→</div>
        <div class="chain-node stage">Critic</div><div class="chain-arrow">→</div>
        <div class="chain-node io">Report</div>
    </div>
</div>
""", unsafe_allow_html=True)


# ── Layout: input left, pipeline right ───────────────────────────────────────
col_input, col_spacer, col_pipeline = st.columns([5, 0.5, 4])

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)

    st.markdown('<div class="field-label">Research Topic</div>', unsafe_allow_html=True)
    topic = st.text_input(
        "Research Topic",
        placeholder="e.g. Quantum computing breakthroughs in 2025",
        key="topic_input",
        label_visibility="collapsed",
    )

    st.markdown('<div class="field-label">ICE Concept Library</div>', unsafe_allow_html=True)
    concept_choice = st.selectbox(
        "ICE Concept Library",
        _ICE_FLAT_OPTIONS,
        index=_ICE_FLAT_OPTIONS.index(st.session_state._last_concept)
              if st.session_state._last_concept in _ICE_FLAT_OPTIONS else 0,
        key="ice_concept_picker",
        label_visibility="collapsed",
    )
    if concept_choice != _PLACEHOLDER and concept_choice != st.session_state._last_concept:
        st.session_state._last_concept = concept_choice
        st.session_state.pending_topic = concept_choice.split(" · ", 1)[1]
        st.rerun()

    run_btn = st.button("Run Research Pipeline", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Quick-pick example chips (mix of general + ICE-specific, tied to your
    # own converter research)
    st.caption("Quick picks")
    examples = [
        "Interleaved bidirectional buck-boost converters",
        "PID controller tuning methods",
        "Sensor fusion for robotics",
        "Fusion energy progress",
    ]
    chip_cols = st.columns(len(examples))
    for col, ex in zip(chip_cols, examples):
        with col:
            if st.button(ex, key=f"chip_{ex}", use_container_width=True):
                st.session_state.pending_topic = ex
                st.rerun()

    st.markdown("""
    <div class="footnote">
        Type any topic freely, or use the <b>ICE Concept Library</b> above —
        it's a searchable dropdown, so typing a few letters filters it instantly.
        Every run produces a <b>downloadable Markdown report</b> plus a critic pass
        that scores the draft.
    </div>
    """, unsafe_allow_html=True)

with col_pipeline:
    st.markdown('<div class="section-heading">Signal Chain Status</div>', unsafe_allow_html=True)

    r = st.session_state.results
    done = st.session_state.done

    def s(step):
        if not r:
            return "waiting"
        steps = ["search", "reader", "writer", "critic"]
        idx = steps.index(step)
        completed = list(r.keys())
        # figure out which steps are done
        if step in r:
            return "done"
        # which step is running now (first not in r)
        if st.session_state.running:
            for i, k in enumerate(steps):
                if k not in r:
                    return "running" if k == step else "waiting"
        return "waiting"

    step_card("01", "Search Agent",  s("search"), "Gathers recent web information")
    step_card("02", "Reader Agent",  s("reader"), "Scrapes and extracts deep content")
    step_card("03", "Writer Chain",  s("writer"), "Drafts the full research report")
    step_card("04", "Critic Chain",  s("critic"), "Reviews and scores the report", is_last=True)


# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn:
    if not topic.strip():
        st.warning("Please enter a research topic first.")
    else:
        st.session_state.results = {}
        st.session_state.running = True
        st.session_state.done = False
        st.rerun()

if st.session_state.running and not st.session_state.done:
    results = {}
    topic_val = st.session_state.topic_input

    # ── Step 1: Search ──
    with st.spinner("Search Agent is gathering sources…"):
        search_agent = build_search_agent()
        sr = search_agent.invoke({
            "messages": [("user", f"Find recent, reliable and detailed information about: {topic_val}")]
        })
        results["search"] = sr["messages"][-1].content
        st.session_state.results = dict(results)
    st.rerun() if False else None   # keep inline for now

    # ── Step 2: Reader ──
    with st.spinner("Reader Agent is scraping top resources…"):
        reader_agent = build_reader_agent()
        rr = reader_agent.invoke({
            "messages": [("user",
                f"Based on the following search results about '{topic_val}', "
                f"pick the most relevant URL and scrape it for deeper content.\n\n"
                f"Search Results:\n{results['search'][:800]}"
            )]
        })
        results["reader"] = rr["messages"][-1].content
        st.session_state.results = dict(results)

    # ── Step 3: Writer ──
    with st.spinner("Writer Chain is drafting the report…"):
        research_combined = (
            f"SEARCH RESULTS:\n{results['search']}\n\n"
            f"DETAILED SCRAPED CONTENT:\n{results['reader']}"
        )
        results["writer"] = writer_chain.invoke({
            "topic": topic_val,
            "research": research_combined
        })
        st.session_state.results = dict(results)

    # ── Step 4: Critic ──
    with st.spinner("Critic Chain is reviewing the report…"):
        results["critic"] = critic_chain.invoke({
            "report": results["writer"]
        })
        st.session_state.results = dict(results)

    st.session_state.running = False
    st.session_state.done = True
    st.rerun()


# ── Results display ───────────────────────────────────────────────────────────
r = st.session_state.results

if r:
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    if "search" in r:
        with st.expander("Search Results — raw output", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Search Agent Output</div>'
                        f'<div class="result-content">{r["search"]}</div></div>', unsafe_allow_html=True)

    if "reader" in r:
        with st.expander("Scraped Content — raw output", expanded=False):
            st.markdown(f'<div class="result-panel"><div class="result-panel-title">Reader Agent Output</div>'
                        f'<div class="result-content">{r["reader"]}</div></div>', unsafe_allow_html=True)

    if "writer" in r:
        st.markdown("""
        <div class="report-panel">
            <div class="panel-label amber">Final Research Report</div>
        """, unsafe_allow_html=True)
        st.markdown(r["writer"])
        st.markdown("</div>", unsafe_allow_html=True)

        st.download_button(
            label="Download Report (.md)",
            data=r["writer"],
            file_name=f"research_report_{int(time.time())}.md",
            mime="text/markdown",
        )

    if "critic" in r:
        st.markdown("""
        <div class="feedback-panel">
            <div class="panel-label teal">Critic Feedback</div>
        """, unsafe_allow_html=True)
        st.markdown(r["critic"])
        st.markdown("</div>", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="notice">
    SIGNALDESK · LangChain multi-agent pipeline · Built with Streamlit
</div>
""", unsafe_allow_html=True)