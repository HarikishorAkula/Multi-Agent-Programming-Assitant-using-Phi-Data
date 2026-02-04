import inspect
import re
import streamlit as st

if not hasattr(inspect, "getargspec"):
    inspect.getargspec = inspect.getfullargspec

from phi.agent import Agent
from phi.model.ollama import Ollama

# Extract python code safely
def extract_code(text):
    if not text:
        return ""

    match = re.search(r"```python(.*?)```", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    return text.strip()

# Run agent safely

def run_agent(agent, prompt):
    try:
        response = agent.run(prompt)

        # Phi returns RunResponse object
        if hasattr(response, "content"):
            return response.content.strip()
        return str(response).strip()

    except Exception as e:
        return f"ERROR: {e}"



# -------------------------------
# LLM
# -------------------------------
llm = Ollama(
    id="tinyllama",
    temperature=0.2
)
# -------------------------------
# Agents
# -------------------------------
explainer = Agent(
    name="Explainer",
    model=llm,
    instructions="Explain problem simply in bullets. NO code."
)

developer = Agent(
    name="Developer",
    model=llm,
    instructions="Write Python code only. Wrap inside ```python```."
)

debugger = Agent(
    name="Debugger",
    model=llm,
    instructions="Fix bugs and return FULL python code inside ```python```."
)

reviewer = Agent(
    name="Reviewer",
    model=llm,
    instructions="Reply STATUS: APPROVED if code is correct."
)

usecase = Agent(
    name="UseCase",
    model=llm,
    instructions="Give exactly 3 real world examples: Input → Output"
)


# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Multi Agent Code Generator", layout="wide")

st.title("🤖 Phi Multi-Agent Python Generator")

task = st.text_area(
    "Describe your Python problem:",
    placeholder="Example: enter your python program"
)

if st.button("Generate"):

    if not task.strip():
        st.error("Enter problem first")
        st.stop()

    # Step 1
    with st.spinner("Understanding..."):
        explanation = run_agent(explainer, task)

    st.subheader("1️⃣ Explanation")
    st.markdown(explanation)

    # Step 2
    with st.spinner("Writing code..."):
        raw = run_agent(developer, task)
        code = extract_code(raw)

    if not code:
        st.error("Model returned empty code. Try again.")
        st.stop()

    st.subheader("2️⃣ Initial Code")
    st.code(code, "python")

    # Step 3
    with st.spinner("Debugging..."):
        improved = run_agent(debugger, code)
        code = extract_code(improved)

    st.subheader("3️⃣ Improved Code")
    st.code(code, "python")

    # Step 4
    with st.spinner("Reviewing..."):
        review = run_agent(reviewer, code)

    st.subheader("4️⃣ Review")
    st.success(review)

    # Step 5
    with st.spinner("Generating use cases..."):
        cases = run_agent(usecase, code)

    st.subheader("5️⃣ Use Cases")
    st.markdown(cases)

    # Final
    st.subheader("✅ Final Python Code")
    st.code(code, "python")
