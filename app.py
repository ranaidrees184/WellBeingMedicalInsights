import streamlit as st
from gradio_client import Client
import re

# ------------------ CONNECT TO GRADIO API ------------------
client = Client("Muhammadidrees/MoizMedgemma27b")

# ------------------ HEADINGS ------------------
HEADINGS = [
    "Executive Summary",
    "System-Specific Analysis",
    "Personalized Action Plan",
    "Interaction Alerts",
    "Longevity Metrics",
    "Enhanced AI Insights",
    "Longitudinal Risk",
    "Tabular Mapping"
]

# ------------------ FORMATTER FUNCTION ------------------
def format_llm_response(response: str):
    """
    Post-process LLM response:
    - Headings -> st.header()
    - Bullets (-, *, +) -> st.markdown
    - Tables -> st.markdown
    - Normal text -> st.markdown
    - Skip empty lines and any variation of 'undefined'
    """
    if not response:
        st.warning("LLM returned empty response.")
        return

    lines = response.strip().split("\n")
    table_buffer = []

    def flush_table():
        nonlocal table_buffer
        if table_buffer:
            st.markdown("\n".join(table_buffer))
            table_buffer = []

    for line in lines:
        # Normalize line
        clean_line = line.strip().lower().replace("\u200b", "")
        if not clean_line or clean_line == "undefined":
            continue  # skip empty or undefined lines

        # Detect markdown tables
        if "|" in line and re.search(r"\|\s*\S+", line):
            table_buffer.append(line)
            continue

        # Flush table when switching to normal text
        flush_table()

        # Headings
        line_clean_heading = line.strip(": ")
        if line_clean_heading in HEADINGS:
            st.header(line_clean_heading)
            continue

        # Bullets
        if line.startswith(("-", "*", "+")):
            st.markdown(line)
            continue

        # Normal text
        st.markdown(line)

    # Flush any remaining table at the end
    flush_table()


# ------------------ STREAMLIT APP ------------------
st.set_page_config(page_title="LLM Medical Insights", layout="centered")
st.title("🧪 LLM Medical Insights")
st.write("Enter patient biomarkers below and click **Generate Insights**.")

# ------------------ INPUT FIELDS ------------------
col1, col2 = st.columns(2)

with col1:
    albumin = st.number_input("Albumin (g/dL)", value=3.5)
    creatinine = st.number_input("Creatinine (mg/dL)", value=1.0)
    glucose = st.number_input("Glucose (mg/dL)", value=90.0)
    crp = st.number_input("CRP (mg/L)", value=1.0)
    mcv = st.number_input("MCV (fL)", value=85.0)
    rdw = st.number_input("RDW (%)", value=12.0)

with col2:
    alp = st.number_input("ALP (U/L)", value=100.0)
    wbc = st.number_input("WBC (x10^9/μL)", value=6.0)
    lymph = st.number_input("Lymphocytes (%)", value=30.0)
    age = st.number_input("Age", value=30)
    gender = st.selectbox("Gender", ["Male", "Female"])
    height = st.number_input("Height (cm)", value=170)
    weight = st.number_input("Weight (kg)", value=70)

# ------------------ BUTTON ------------------
if st.button("Generate Insights"):
    with st.spinner("Contacting LLM..."):
        try:
            # ------------------ CALL LLM ------------------
            response = client.predict(
                albumin,
                creatinine,
                glucose,
                crp,
                mcv,
                rdw,
                alp,
                wbc,
                lymph,
                age,
                gender,
                height,
                weight,
            )

            # Only use the first element if tuple to avoid duplication
            main_response = response[0] if isinstance(response, tuple) else response

            # ------------------ DISPLAY ------------------
            st.subheader("✅ Medical Insights")
            format_llm_response(main_response)

        except Exception as e:
            st.error(f"Request failed: {e}")
