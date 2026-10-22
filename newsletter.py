import os
import streamlit as st
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai_tools import SerperDevTool

# Load environment variables automatically from .env
load_dotenv()

# Streamlit Page Setup
st.set_page_config(
    page_title="TechPulse | AI Tech Newsletter Crew",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS for News Portal Styling
st.markdown("""
<style>
    /* Header Banner Styling */
    .news-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .news-header h1 {
        margin: 0;
        font-size: 2.5rem;
        font-weight: 800;
        letter-spacing: -0.5px;
    }
    .news-header p {
        margin-top: 0.5rem;
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* News Story Card Styling */
    .story-card {
        background-color: #ffffff;
        border-left: 5px solid #2a5298;
        padding: 1.25rem 1.5rem;
        border-radius: 8px;
        margin-bottom: 1.2rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        color: #1a1a1a;
    }
    
    /* Impact Box Styling */
    .impact-card {
        background: linear-gradient(135deg, #f6d365 0%, #fda085 100%);
        padding: 1.25rem 1.5rem;
        border-radius: 8px;
        color: #2c3e50;
        font-weight: 600;
        margin-top: 1.5rem;
        box-shadow: 0 4px 12px rgba(253, 160, 133, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# News Portal Header UI
st.markdown("""
<div class="news-header">
    <h1>⚡ TechPulse Daily Newsletter</h1>
    <p>Autonomous AI Multi-Agent Intelligence • Powered by CrewAI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar - Agent Pipeline Information
with st.sidebar:
    st.image("https://img.icons8.com/color/96/news.png", width=70)
    st.title("Crew Configuration")
    st.markdown("---")
    
    st.subheader("🕵️ Agent 1: Researcher")
    st.caption("**Tool:** SerperDevTool\n**Role:** Finds today's top 3 tech stories across the web.")
    
    st.markdown("---")
    
    st.subheader("✍️ Agent 2: Writer")
    st.caption("**Tool:** None (Pure Synthesis)\n**Role:** Formats research into a concise 5-line newsletter.")
    
    st.markdown("---")
    st.info("🔒 API keys are safely loaded from environment variables (`.env`).")

# Main Action Area
col1, col2 = st.columns([3, 1])
with col1:
    st.subheader("Today's Edition")
    st.caption("Click the button below to trigger the two-agent sequential workflow.")

with col2:
    run_button = st.button("🔄 Generate Daily News", type="primary", use_container_width=True)

st.markdown("---")

# Execution Workflow
if run_button:
    openai_key = os.getenv("OPENAI_API_KEY")
    serper_key = os.getenv("SERPER_API_KEY")

    if not openai_key or not serper_key:
        st.error("⚠️ Missing API Key(s) in `.env` file! Please ensure `OPENAI_API_KEY` and `SERPER_API_KEY` are defined.")
    else:
        with st.status("🚀 Running Multi-Agent Workflow...", expanded=True) as status:
            st.write("🔍 **Researcher Agent:** Searching the live web via SerperDevTool...")
            search = SerperDevTool(api_key=serper_key)

            researcher = Agent(
                role="Senior Tech Researcher",
                goal="Find today's top 3 most important and trending tech news stories using web search.",
                backstory="An expert tech scout with a keen eye for groundbreaking developments, artificial intelligence breakthroughs, and major industry shifts.",
                tools=[search],
                verbose=True
            )

            writer = Agent(
                role="Tech Newsletter Writer",
                goal="Transform tech news research into a punchy, exactly 5-line newsletter format.",
                backstory="A talented writer who specializes in making complex technology updates crisp, engaging, and easy to digest in a strict 5-line structure.",
                verbose=True
            )

            find = Task(
                description="Search the web for today's top 3 trending tech news stories. Extract clear headlines and brief descriptions for each.",
                expected_output="A structured list of today's top 3 tech news stories with their headlines and key details.",
                agent=researcher
            )

            st.write("✍️ **Writer Agent:** Synthesizing research into a strict 5-line newsletter format...")
            write = Task(
                description="Using the research provided, draft a newsletter that strictly adheres to this exact 5-line format:\n"
                            "Tech in 5 lines\n"
                            "1. [First story summary]\n"
                            "2. [Second story summary]\n"
                            "3. [Third story summary]\n"
                            "Why it matters: [A concise concluding thought or impact statement]\n\n"
                            "Do not include any extra text, intros, or conversational filler outside of these 5 lines.",
                expected_output="A 5-line newsletter strictly matching the specified template.",
                agent=writer,
                context=[find]
            )

            crew = Crew(
                agents=[researcher, writer],
                tasks=[find, write],
                process=Process.sequential,
                verbose=True
            )

            try:
                raw_result = str(crew.kickoff())
                status.update(label="✅ Edition Published Successfully!", state="complete", expanded=False)
                st.session_state["newsletter_output"] = raw_result
            except Exception as e:
                status.update(label="❌ Pipeline Execution Error", state="error", expanded=True)
                st.error(f"Execution error: {e}")

# Render Interactive News UI
if "newsletter_output" in st.session_state:
    raw_text = st.session_state["newsletter_output"].strip()
    lines = [line.strip() for line in raw_text.split("\n") if line.strip()]

    st.markdown("### 📰 Featured Stories")
    
    for line in lines:
        if line.startswith("Tech in 5 lines"):
            st.caption(f"**Edition Format:** `{line}`")
        elif line.startswith("1.") or line.startswith("2.") or line.startswith("3."):
            st.markdown(f"""
            <div class="story-card">
                <span style="font-size: 1.1rem; font-weight: 600;">{line}</span>
            </div>
            """, unsafe_allow_html=True)
        elif line.lower().startswith("why it matters:"):
            st.markdown(f"""
            <div class="impact-card">
                📌 <strong>{line}</strong>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    with st.expander("📄 View Raw 5-Line Text Output (Assignment Check)"):
        st.code(raw_text, language="text")