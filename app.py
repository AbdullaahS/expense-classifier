import os
import json
import streamlit as st
from dotenv import load_dotenv
from google import genai

# --------------------
# Setup
# --------------------
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
if not API_KEY:
    st.error("Missing GEMINI_API_KEY. Add it to your .env file, then restart Streamlit.")
    st.stop()

client = genai.Client(api_key=API_KEY)

st.set_page_config(page_title="UK Tax Triage Agent", layout="wide")
st.title("UK Tax Triage Agent (Demo)")
st.caption("Day 3: Streamlit UI — structured triage output for UK tax queries")

# --------------------
# Helpers
# --------------------
def strip_code_fences(text: str) -> str:
    """Remove ```json ... ``` or ``` ... ``` wrappers if the model adds them."""
    t = text.strip()
    if t.startswith("```"):
        # remove first fence line
        t = t.split("\n", 1)[1] if "\n" in t else ""
        # remove last fence
        if t.strip().endswith("```"):
            t = t.rsplit("```", 1)[0]
    return t.strip()

def build_prompt(client_query: str, max_questions: int) -> str:
    return f"""
You are a UK Tax Triage Agent working at a UK accountancy firm.

Analyse the client query and return a triage summary.

OUTPUT RULES:
- Return ONLY valid JSON
- No markdown
- No explanations
- No extra text before or after JSON

JSON KEYS (use exactly these, snake_case):
- tax_areas (array of strings)
- primary_tax_area (string)
- confidence (string: "high", "medium", or "low")
- summary_of_client_issue (string)
- clarifying_questions (array of strings, max {max_questions})
- evidence_checklist (array of strings)
- risk_flags (array of strings)
- deadlines_or_time_sensitivity (array of strings)
- next_actions (array of strings)
- escalate_to_senior (boolean)
- internal_note_to_manager (string)

RULES:
- confidence MUST be lowercase
- deadlines_or_time_sensitivity MUST be an array (even if one item)
- Do NOT invent new keys
- Return ONE JSON object only

Client query:
{client_query}
""".strip()

# --------------------
# Sidebar controls
# --------------------
st.sidebar.header("Settings")
model_name = st.sidebar.selectbox(
    "Model",
    options=[
        "gemini-2.0-flash",
        "gemini-2.0-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-pro",
    ],
    index=0,
)
max_questions = st.sidebar.slider("Max clarifying questions", 1, 8, 5)

st.sidebar.markdown("---")
st.sidebar.markdown("Tip: Paste a messy client message and click **Run triage**.")

# --------------------
# Main UI
# --------------------
default_query = "We’re a subcontractor — the contractor deducted CIS but we think we’re gross. Help."
user_query = st.text_area("Client query", value=default_query, height=160)

run = st.button("Run triage", type="primary")

if run:
    with st.spinner("Running triage..."):
        prompt = build_prompt(user_query, max_questions)

        try:
            resp = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            text = (resp.text or "").strip()
            text = strip_code_fences(text)

            data = json.loads(text)

        except json.JSONDecodeError:
            st.error("Model did not return valid JSON. Showing raw output below:")
            st.code(text)
            st.stop()

        except Exception as e:
            st.error(f"Error calling model: {e}")
            st.stop()

    st.success("Triage complete.")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Structured JSON output")
        st.json(data)

    with col2:
        st.subheader("Quick view")
        st.write("**Primary tax area:**", data.get("primary_tax_area"))
        st.write("**Confidence:**", data.get("confidence"))
        st.write("**Escalate to senior:**", data.get("escalate_to_senior"))

        st.markdown("### Summary")
        st.write(data.get("summary_of_client_issue", ""))

        st.markdown("### Clarifying questions")
        for q in data.get("clarifying_questions", []):
            st.write("–", q)

        st.markdown("### Evidence checklist")
        for item in data.get("evidence_checklist", []):
            st.write("–", item)

        st.markdown("### Risk flags")
        for item in data.get("risk_flags", []):
            st.write("–", item)

        st.markdown("### Deadlines / time sensitivity")
        for item in data.get("deadlines_or_time_sensitivity", []):
            st.write("–", item)

        st.markdown("### Next actions")
        for item in data.get("next_actions", []):
            st.write("–", item)

        st.markdown("### Internal note to manager")
        st.write(data.get("internal_note_to_manager", ""))

python -m streamlit run app.py



