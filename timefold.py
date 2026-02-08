import streamlit as st
import google.generativeai as genai
from pydantic import BaseModel, Field
from typing import List, Optional
from graphviz import Digraph
import json
import time
from PIL import Image
import io
import random

st.set_page_config(page_title="TIMEFOLD: Neural Strategy Engine", page_icon="🔮", layout="wide")

st.markdown("""
<style>



:root{
  --bg0:#070A10;
  --bg1:#0B1020;
  --glass: rgba(255,255,255,0.06);
  --glass2: rgba(255,255,255,0.10);
  --stroke: rgba(255,255,255,0.14);
  --stroke2: rgba(0,201,255,0.35);
  --text:#DCE6F2;
  --muted:#9DB0C6;
  --cyan:#00C9FF;
  --mint:#92FE9D;
  --violet:#8A5CFF;
  --pink:#FF4FD8;
  --shadow: 0 18px 60px rgba(0,0,0,0.55);
  --shadow2: 0 10px 30px rgba(0,0,0,0.35);
  --radius: 18px;
  --radius2: 26px;
}

html, body, [data-testid="stAppViewContainer"]{
  background: radial-gradient(1200px 800px at 10% 10%, rgba(0,201,255,0.12), transparent 55%),
              radial-gradient(1000px 700px at 90% 20%, rgba(146,254,157,0.10), transparent 60%),
              radial-gradient(900px 700px at 60% 90%, rgba(138,92,255,0.12), transparent 55%),
              linear-gradient(180deg, var(--bg0), var(--bg1));
  color: var(--text) !important;
}

[data-testid="stAppViewContainer"]::before{
  content:"";
  position: fixed;
  inset: -40%;
  background:
    radial-gradient(closest-side at 20% 20%, rgba(0,201,255,0.14), transparent 60%),
    radial-gradient(closest-side at 80% 30%, rgba(255,79,216,0.10), transparent 60%),
    radial-gradient(closest-side at 60% 80%, rgba(146,254,157,0.12), transparent 60%),
    radial-gradient(closest-side at 30% 70%, rgba(138,92,255,0.12), transparent 60%);
  filter: blur(45px);
  opacity: 0.9;
  animation: aurora 12s ease-in-out infinite alternate;
  pointer-events:none;
  z-index: 0;
}

@keyframes aurora{
  0% { transform: translate3d(-2%, -1%, 0) scale(1.00) rotate(0deg); }
  100%{ transform: translate3d(2%, 1%, 0) scale(1.05) rotate(10deg); }
}


[data-testid="stAppViewContainer"] > .main{
  position: relative;
  z-index: 1;
}
.main { background: transparent !important; }


h1, h2, h3, h4, h5, h6 { letter-spacing: 0.3px; }
h1{
  background: linear-gradient(90deg, var(--cyan), var(--mint), var(--violet));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-weight: 800;
  text-shadow: 0 0 22px rgba(0,201,255,0.18);
}


section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.03)) !important;
  border-right: 1px solid rgba(255,255,255,0.08);
  backdrop-filter: blur(18px);
}
section[data-testid="stSidebar"] *{ color: var(--text) !important; }


[data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"]{
  border-radius: var(--radius2);
  border: 1px solid rgba(255,255,255,0.06);
  background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.03));
  box-shadow: var(--shadow2);
  backdrop-filter: blur(18px);
}


.block-container{
  padding-top: 1.6rem !important;
  padding-bottom: 2.2rem !important;
}


.stButton > button{
  border: 1px solid rgba(0,201,255,0.55) !important;
  border-radius: 14px !important;
  background: linear-gradient(180deg, rgba(0,201,255,0.08), rgba(255,255,255,0.02)) !important;
  color: var(--text) !important;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-weight: 800 !important;
  letter-spacing: 0.4px;
  padding: 0.70rem 0.95rem !important;
  box-shadow: 0 0 0 rgba(0,0,0,0);
  transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease, filter .18s ease;
  position: relative;
  overflow: hidden;
}

.stButton > button::before{
  content:"";
  position:absolute;
  inset:-2px;
  background: radial-gradient(closest-side at 30% 20%, rgba(0,201,255,0.35), transparent 60%),
              radial-gradient(closest-side at 80% 60%, rgba(146,254,157,0.22), transparent 62%),
              radial-gradient(closest-side at 50% 120%, rgba(138,92,255,0.22), transparent 60%);
  opacity: 0.0;
  transition: opacity .18s ease;
}

.stButton > button:hover{
  transform: translateY(-2px) scale(1.01);
  border-color: rgba(146,254,157,0.70) !important;
  box-shadow: 0 16px 40px rgba(0,201,255,0.18), 0 10px 24px rgba(146,254,157,0.10);
  filter: brightness(1.08);
}
.stButton > button:hover::before{ opacity: 0.9; }

.stButton > button:active{
  transform: translateY(0px) scale(0.995);
  box-shadow: 0 10px 24px rgba(0,0,0,0.35);
}


button[kind="primary"]{
  border: 1px solid rgba(146,254,157,0.75) !important;
  background: linear-gradient(90deg, rgba(0,201,255,0.18), rgba(146,254,157,0.18)) !important;
  box-shadow: 0 18px 50px rgba(0,201,255,0.15);
}


textarea, input, .stTextArea textarea, .stTextInput input{
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  border-radius: 16px !important;
  color: var(--text) !important;
  backdrop-filter: blur(12px);
}
textarea:focus, input:focus{
  border-color: rgba(0,201,255,0.45) !important;
  box-shadow: 0 0 0 4px rgba(0,201,255,0.08) !important;
}


button[data-baseweb="tab"]{
  border-radius: 999px !important;
  background: rgba(255,255,255,0.05) !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  color: var(--muted) !important;
  transition: all .18s ease;
}
button[data-baseweb="tab"][aria-selected="true"]{
  color: var(--text) !important;
  border-color: rgba(0,201,255,0.45) !important;
  background: linear-gradient(90deg, rgba(0,201,255,0.14), rgba(146,254,157,0.10)) !important;
  box-shadow: 0 10px 26px rgba(0,201,255,0.14);
}


.agent-card{
  padding: 20px;
  border-radius: 22px;
  background: linear-gradient(180deg, rgba(255,255,255,0.07), rgba(255,255,255,0.03));
  border: 1px solid rgba(255,255,255,0.10);
  box-shadow: var(--shadow2);
  backdrop-filter: blur(18px);
  position: relative;
  overflow: hidden;
  transform: translateY(0);
  transition: transform .20s ease, box-shadow .20s ease, border-color .20s ease;
}
.agent-card::before{
  content:"";
  position:absolute;
  inset:-2px;
  background: radial-gradient(closest-side at 20% 10%, rgba(0,201,255,0.20), transparent 55%),
              radial-gradient(closest-side at 80% 30%, rgba(146,254,157,0.14), transparent 60%),
              radial-gradient(closest-side at 60% 90%, rgba(138,92,255,0.14), transparent 55%);
  filter: blur(18px);
  opacity: 0.7;
  pointer-events:none;
}
.agent-card:hover{
  transform: translateY(-6px);
  box-shadow: 0 22px 60px rgba(0,0,0,0.55), 0 14px 40px rgba(0,201,255,0.10);
  border-color: rgba(0,201,255,0.26);
}


.trace-box{
  background: linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.03));
  border: 1px solid rgba(255,255,255,0.10);
  border-left: 3px solid rgba(255,165,0,0.90);
  padding: 12px;
  font-size: 0.86em;
  margin-top: 10px;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  color: var(--text);
  border-radius: 16px;
  position: relative;
  overflow: hidden;
}
.trace-box::after{
  content:"";
  position:absolute;
  inset:0;
  background: repeating-linear-gradient(
    to bottom,
    rgba(255,255,255,0.035),
    rgba(255,255,255,0.035) 1px,
    transparent 1px,
    transparent 6px
  );
  opacity: 0.12;
  pointer-events:none;
  animation: scan 4.5s linear infinite;
}
@keyframes scan{
  0%{ transform: translateY(-6px); }
  100%{ transform: translateY(6px); }
}


[data-testid="stMetric"]{
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 18px;
  padding: 12px 14px;
  box-shadow: 0 10px 24px rgba(0,0,0,0.25);
  backdrop-filter: blur(14px);
}
[data-testid="stMetricValue"]{
  color: var(--text);
  text-shadow: 0 0 18px rgba(0,201,255,0.10);
}


[data-testid="stFileUploaderDropzone"]{
  background: rgba(255,255,255,0.04) !important;
  border: 1px dashed rgba(0,201,255,0.35) !important;
  border-radius: 18px !important;
  box-shadow: 0 10px 24px rgba(0,0,0,0.20);
}


[data-testid="stStatusWidget"]{
  border-radius: 18px !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  background: rgba(255,255,255,0.05) !important;
  backdrop-filter: blur(14px);
  box-shadow: var(--shadow2);
}


[data-testid="stAlert"]{
  border-radius: 18px !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
  background: rgba(255,255,255,0.05) !important;
  backdrop-filter: blur(14px);
  box-shadow: 0 10px 24px rgba(0,0,0,0.20);
}


hr{
  border-color: rgba(255,255,255,0.12) !important;
}


p, li, label, span, div { color: var(--text); }
small, .stCaption, [data-testid="stCaptionContainer"]{ color: var(--muted) !important; }


[data-testid="stGraphvizChart"]{
  border-radius: 22px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.10);
  background: rgba(255,255,255,0.04);
  box-shadow: var(--shadow2);
}


@keyframes fadeInUp{
  from{ opacity: 0; transform: translateY(8px); }
  to{ opacity: 1; transform: translateY(0px); }
}
.block-container{
  animation: fadeInUp .42s ease both;
}


</style>
""", unsafe_allow_html=True)

try:
    api_key = st.secrets["GOOGLE_API_KEY"]
except:
    api_key = None

if not api_key:
    st.error("SECURITY ALERT: API Key not found. Please set `GOOGLE_API_KEY` in Streamlit secrets")
    st.info("If running locally create a `.streamlit/secrets.toml` file")
    st.stop()

genai.configure(api_key=api_key)

class AgentProfile(BaseModel):
    name: str = Field(description="Name of the expert (No titles like Dr./Prof., use generic or code names)")
    role: str = Field(description="Specific Expertise (e.g., Supply Chain Analyst)")
    stance: str = Field(description="Strategic stance (e.g., Risk-Averse, Disruptive)")
    avatar: str = Field(description="Single emoji representing the persona")

class Council(BaseModel):
    agents: List[AgentProfile]

class ScenarioNode(BaseModel):
    id: str
    title: str = Field(description="Short, punchy title")
    description: str
    probability: int
    time_horizon: str = Field(description="Short Term (0-6m), Mid Term (1-2y), or Long Term (5y+)")
    risk_level: str = Field(description="Low, Medium, High, Critical")
    impact_score: int = Field(description="1-10")
    data_confidence: int = Field(description="Confidence in underlying data (0-100)")
    assumption_stability: int = Field(description="How stable are the assumptions? (0-100)")
    reasoning_trace: str = Field(description="Brief explanation of the logic chain and rejected alternatives.")

class SimulationOutput(BaseModel):
    scenarios: List[ScenarioNode]
    synthesis: str
    black_swan_alert: Optional[str] = Field(description="If a low probability high impact event was detected, describe it here.")

def recruit_agents(context, image_part=None):
    model = genai.GenerativeModel(
        model_name='gemini-3-pro-preview',
        generation_config={"response_mime_type": "application/json", "response_schema": Council}
    )
    prompt = f"MISSION: Recruit 3 distinct strategic experts to analyze: {context}. RULES: No honorifics. Diverse perspectives."
    inputs = [prompt]
    if image_part:
        inputs.append(image_part)
        inputs.append("Analyze visual data.")

    response = model.generate_content(inputs)
    return json.loads(response.text)

def run_simulation(context, agents, image_part=None, inject_chaos=False):
    model = genai.GenerativeModel(
        model_name='gemini-3-pro-preview',
        generation_config={"response_mime_type": "application/json", "response_schema": SimulationOutput}
    )

    agents_desc = "\n".join([f"- {a['name']} ({a['role']}): {a['stance']}" for a in agents['agents']])

    chaos_prompt = ""
    if inject_chaos:
        chaos_prompt = "⚠️ INJECT A BLACK SWAN EVENT: Introduce a low-probability, high-impact disruption into the scenarios."

    prompt = f"""
    You are TIMEFOLD, an Advanced Strategic Foresight Engine.
    ACTIVE COUNCIL: {agents_desc}
    TASK: Simulate a debate, generate 3 divergent future scenarios. Include reasoning traces and confidence metrics.
    {chaos_prompt}
    CURRENT STATE: {context}
    """

    inputs = [prompt]
    if image_part: inputs.extend([image_part, "Incorporate visual insights."])

    try:
        response = model.generate_content(inputs)
        return json.loads(response.text)
    except Exception as e:
        st.error(f"Simulation Error: {e}")
        return None

def generate_markdown_report(history):
    report = "# TIMEFOLD STRATEGIC REPORT\n"
    report += f"**Date:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    for i, step in enumerate(history):
        report += f"## Step {i+1}: {step.get('title', 'UNTITLED')}\n"
        report += f"_{step.get('description', '')}_\n\n"
        if 'reasoning_trace' in step and step.get('reasoning_trace') is not None:
            report += f"> **Reasoning:** {step.get('reasoning_trace','')}\n\n"
        if 'risk_level' in step:
            report += f"**Metrics:** Risk: {step.get('risk_level','Unknown')} | Prob: {step.get('probability','N/A')}%\n"
        report += "---\n"
    return report

def draw_advanced_tree(history, options):
    dot = Digraph(format='png')
    dot.attr(bgcolor='#0E1117', rankdir='LR')
    dot.attr('node', fontname='Helvetica', fontcolor='white')
    dot.attr('edge', color='#555555', arrowsize='0.7', fontcolor='#AAAAAA')

    for i, step in enumerate(history):
        node_id = f"H_{i}"
        label = f"{step.get('title', 'UNTITLED')}"
        dot.node(node_id, label=label, shape='box', style='filled', fillcolor='#21262D', penwidth='2.0', color='white')
        if i > 0: dot.edge(f"H_{i-1}", node_id)

    last_id = f"H_{len(history)-1}"
    if options:
        for opt in options.get("scenarios", []):
            
            opt_id_val = opt.get("id", str(random.randint(1000, 9999)))
            opt_id = f"OPT_{opt_id_val}"

            risk_level = opt.get("risk_level", "Unknown")
            risk = (risk_level or "").lower()

            color = '#8B0000' if 'critical' in risk else '#B22222' if 'high' in risk else '#006400' if 'low' in risk else '#003366'

            title = opt.get("title", "Untitled")
            time_horizon = opt.get("time_horizon", "N/A")
            probability = opt.get("probability", "N/A")

            label = f"""<<TABLE BORDER="0" CELLBORDER="0" CELLSPACING="0"><TR><TD><B>{title}</B></TD></TR>
            <TR><TD><FONT POINT-SIZE="10">{time_horizon}</FONT></TD></TR>
            <TR><TD><FONT POINT-SIZE="10">Prob: {probability}%</FONT></TD></TR></TABLE>>"""

            dot.node(opt_id, label=label, shape='note', style='filled', fillcolor=color)
            dot.edge(last_id, opt_id, label=f"Risk: {risk_level}")
    return dot

with st.sidebar:
    st.header("⚙️ Configuration")
    show_reasoning = st.toggle("🧠 Show Reasoning Trace", value=True)
    st.markdown("### Vision Input")
    uploaded_file = st.file_uploader("Upload Chart/Map/Photo", type=["jpg", "png", "jpeg"])

    image_part = None
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="Visual Context Loaded", use_column_width=True)
        image_part = image

    st.divider()
    if st.button("🔄 Reset System", type="primary"):
        st.session_state.clear()
        st.rerun()

if 'stage' not in st.session_state: st.session_state.stage = 'INPUT'
if 'history' not in st.session_state: st.session_state.history = []
if 'agents' not in st.session_state: st.session_state.agents = None
if 'simulation' not in st.session_state: st.session_state.simulation = None

st.title("TIMEFOLD")
st.caption("Multimodal Strategic Foresight Engine | Powered by Gemini 3 Preview")

if st.session_state.stage == 'INPUT':
    st.markdown("### Initialize Simulation")

    st.markdown("Or choose a preset:")
    c1, c2, c3 = st.columns(3)
    if c1.button("📉 Crypto Crash"):
        st.session_state.history.append({"title": "START", "description": "Bitcoin crashes below $30k, triggering global regulatory crackdown."})
        st.session_state.stage = 'RECRUITING'
        st.rerun()
    if c2.button("🦠 Pandemic 2.0"):
        st.session_state.history.append({"title": "START", "description": "A new respiratory virus with high transmission rate is detected in major transit hubs."})
        st.session_state.stage = 'RECRUITING'
        st.rerun()
    if c3.button("🤖 AI Ban"):
        st.session_state.history.append({"title": "START", "description": "UN passes a resolution banning autonomous AI development above a certain compute threshold."})
        st.session_state.stage = 'RECRUITING'
        st.rerun()

    user_input = st.text_area("Define your own scenario:", placeholder="E.g., A sudden collapse in the global lithium supply chain...", height=100)

    if st.button("INITIALIZE SYSTEM", use_container_width=True):
        if user_input or image_part:
            input_text = user_input if user_input else "Analyze the uploaded visual data."
            st.session_state.history.append({"title": "START", "description": input_text})
            st.session_state.stage = 'RECRUITING'
            st.rerun()
        else:
            st.warning("Please enter text or upload an image.")


elif st.session_state.stage == 'RECRUITING':
    last_context = st.session_state.history[-1].get('description', '')

    with st.status("📡 Establishing Neural Link...", expanded=True) as status:
        st.write("Processing context and visual data...")
        time.sleep(0.5)
        st.write("Recruiting domain experts...")
        st.session_state.agents = recruit_agents(last_context, image_part)
        status.update(label="✅ Council Assembled", state="complete", expanded=False)

    st.subheader("🧠 The Strategic Council")
    cols = st.columns(3)
    for i, agent in enumerate(st.session_state.agents['agents']):
        with cols[i]:
            st.markdown(f"""
            <div class="agent-card">
                <div style="font-size: 2.5em; text-align:center;">{agent.get('avatar','🧠')}</div>
                <div style="font-weight: bold; color: #00C9FF; text-align:center; font-size: 1.1em;">{agent.get('name','Agent')}</div>
                <div style="font-size: 0.9em; opacity: 0.8; text-align:center;">{agent.get('role','')}</div>
                <hr style="border-color: #333;">
                <div style="font-size: 0.85em; font-style: italic;">"{agent.get('stance','')}"</div>
            </div>
            """, unsafe_allow_html=True)

    if st.button("START SIMULATION ➡️", use_container_width=True):
        st.session_state.stage = 'SIMULATING'
        st.rerun()

elif st.session_state.stage == 'SIMULATING':
    last_context = st.session_state.history[-1].get('description', '')

    inject_chaos = False
    if st.button("Inject Chaos (Black Swan Event)", type="secondary"):
        inject_chaos = True
        st.session_state.simulation = None

    if not st.session_state.simulation:
        with st.spinner("Simulating Futures... (Agents debating)"):
            st.session_state.simulation = run_simulation(last_context, st.session_state.agents, image_part, inject_chaos)

    
    if not st.session_state.simulation:
        st.error("Simulation failed (no valid output). Please try again or reset the system.")
        cA, cB = st.columns(2)
        with cA:
            if st.button("🔁 Retry Simulation", use_container_width=True):
                st.session_state.simulation = None
                st.rerun()
        with cB:
            if st.button("🔄 Reset System (Hard)", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        st.stop()

    tab1, tab2 = st.tabs(["🕸️ Interactive Graph", "📋 Executive Summary"])

    with tab1:
        st.graphviz_chart(draw_advanced_tree(st.session_state.history, st.session_state.simulation), use_container_width=True)

    with tab2:
        st.success("Council Synthesis")
        st.write(st.session_state.simulation.get('synthesis', ''))
        if st.session_state.simulation.get('black_swan_alert') or inject_chaos:
            st.error(f"⚠️ BLACK SWAN / CHAOS DETECTED: {st.session_state.simulation.get('black_swan_alert', 'Chaos Injection Active')}")

    st.divider()

    st.subheader("📍 Select Future Path")
    scenarios = st.session_state.simulation.get("scenarios", [])

    if scenarios:
        cols = st.columns(len(scenarios))
        for i, sc in enumerate(scenarios):
            with cols[i]:
                with st.container(border=True):
                    risk_level = sc.get('risk_level', 'Unknown')
                    risk_color = ":red" if "Critical" in risk_level else ":orange" if "High" in risk_level else ":green"
                    st.markdown(f"#### {risk_color}[{sc.get('title','Untitled')}]")
                    st.caption(f"Time Horizon: {sc.get('time_horizon','N/A')}")

                    c1, c2 = st.columns(2)
                    c1.metric("Prob", f"{sc.get('probability','N/A')}%")
                    c2.metric("Impact", f"{sc.get('impact_score','N/A')}/10")

                    st.write(sc.get('description', ''))

                    if show_reasoning:
                        with st.expander("🔍 Reasoning Trace"):
                            st.markdown(f"""
                            <div class="trace-box">
                            <b>Logic:</b> {sc.get('reasoning_trace','')}<br>
                            <b>Data Conf:</b> {sc.get('data_confidence','N/A')}%<br>
                            <b>Assumption Stability:</b> {sc.get('assumption_stability','N/A')}%
                            </div>
                            """, unsafe_allow_html=True)

                    if st.button("Explore This Path", key=f"btn_{i}", use_container_width=True):
                        st.session_state.history.append(sc)
                        st.session_state.simulation = None
                        st.session_state.agents = None
                        st.session_state.stage = 'RECRUITING'
                        st.rerun()
    else:
        st.warning("No scenarios returned by the model. Try again.")

    st.divider()
    report_md = generate_markdown_report(st.session_state.history)
    st.download_button(
        label="📄 Download Strategic Report (Markdown)",
        data=report_md,
        file_name="timefold_report.md",
        mime="text/markdown"
    )
