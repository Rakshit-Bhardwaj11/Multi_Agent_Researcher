# SignalDesk — Multi-Agent Research Assistant

**Live app:** https://multi-agent-ice-research.streamlit.app/

SignalDesk is a four-agent research pipeline that takes any topic, searches the web, reads the most relevant source in depth, drafts a structured report, and critiques its own output — end to end, with no manual steps in between. I built it to speed up research for my B.Tech project (BTP) and for studying core Instrumentation & Control Engineering (ICE) subjects, alongside general-purpose research support.

## What it does

Give it a topic — anything from "quantum computing breakthroughs in 2025" to "interleaved bidirectional buck-boost converters" — and it runs a four-stage pipeline automatically:

1. **Search Agent** — queries the web (via Tavily) for recent, reliable sources and returns titles, URLs, and snippets.
2. **Reader Agent** — picks the most relevant result and scrapes the full page for deeper context (via BeautifulSoup).
3. **Writer Chain** — synthesizes the search results and scraped content into a structured report: introduction, key findings, conclusion, and sources.
4. **Critic Chain** — reviews the draft independently, scores it out of 10, and lists strengths and specific areas to improve.

The final report is rendered in the browser and available as a downloadable Markdown file. Every stage's raw output is also viewable, so you can see exactly what each agent found or produced — not just the final result.

A built-in **ICE Concept Library** — a searchable dropdown covering Control Systems, Instrumentation, Signal Processing, Power Electronics, Industrial Automation, and Robotics & Mechatronics — lets you jump straight into subject-specific research without typing a topic from scratch.

## Why I built it

Research for my BTP and coursework kept involving the same slow loop: search for sources, read through several pages, and manually turn scattered information into something structured enough to actually cite or study from. I built this to automate that loop and, at the same time, to get hands-on experience with agentic system design — using multiple specialized LLM agents instead of a single prompt-and-response chatbot.

## Tech stack

| Layer | Technology | Purpose |
|---|---|---|
| LLM | Google Gemini 2.5 Flash (via langchain-google-genai) | Powers all four agents/chains |
| Agent framework | LangChain (create_agent) + LangGraph | Builds the Search and Reader agents as tool-using ReAct-style agents |
| Orchestration | LangChain Expression Language (LCEL) | Chains the Writer and Critic prompts to the model with StrOutputParser |
| Web search | Tavily API | Retrieves recent, reliable search results |
| Web scraping | BeautifulSoup4 + requests | Extracts clean text from source pages |
| Frontend | Streamlit | Single-page web app with live pipeline status |
| Config | python-dotenv | Loads API keys from environment variables locally |
| Deployment | Streamlit Community Cloud | Hosts the live app, with secrets managed separately from local .env |

## Architecture

Topic
│
▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ Search Agent│ ──▶ │ Reader Agent│ ──▶ │ Writer Chain│ ──▶ │ Critic Chain│ ──▶ Report
│ (Tavily)    │     │ (scrape URL)│     │ (LCEL)      │     │ (LCEL)      │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘

- `agents.py` — defines the Gemini model instance and builds the four agents/chains.
- `tools.py` — defines the two LangChain tools (web_search, scrape_url) used by the agent-based stages.
- `app.py` — the Streamlit UI: topic input, ICE concept dropdown, live pipeline status, and results display.
- `requirements.txt` — pinned dependencies for reproducible local and cloud environments.

Each stage's output is stored in Streamlit's session state and passed forward as context to the next stage, so the Writer Chain sees both the search results and the scraped content, and the Critic Chain reviews the Writer's finished draft independently.

## Author

Rakshit Bhardwaj — B.Tech, Instrumentation & Control Engineering, NSUT Delhi (Class of 2027)
