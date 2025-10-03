import streamlit as st
from gradio_client import Client
import re

# ------------------ CONNECT TO GRADIO API ------------------
client = Client("Muhammadidrees/MoizMedgemma27b")

# ------------------ FORMATTER FUNCTION ------------------
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

def format_llm_response(response: str):
    """
    Post-process LLM response:
    - Headings -> st.header()
    - Bullets (-, *, +) -> st.markdown
    - Tables -> st.markdown (raw markdown, no Pandas index)
    - Normal text -> st.markdown
    """
    lines = response.strip().split("\n")
    table_buffer = []

    for line in lines:
        line = line.rstrip()
        if not line:
            continue

        # Detect table rows (Markdown tables)
        if "|" in line and re.search(r"\|\s*\S+", line):
            table_buffer.append(line)
            continue
        else:
            # Flush table buffer before printing other text
            if table_buffer:
                st.markdown("\n".join(table_buffer))
                table_buffer = []

        # Check if line matches one of the system headings
        clean_line = line.strip(": ")
        if clean_line in HEADINGS:
            st.header(clean_line)  # prominent heading
            continue

        # Bullets
        if line.startswith(("-", "*", "+")):
            st.markdown(line)
            continue

        # Normal text
        st.markdown(line)

    # Flush last table if exists
    if table_buffer:
        st.markdown("\n".join(table_buffer))


# ------------------ STREAMLIT APP ------------------
st.title("🧪 LLM Medical Insights")

# Input fields
albumin = st.number_input("Albumin", value=3.5)
creatinine = st.number_input("Creatinine", value=1.0)
glucose = st.number_input("Glucose", value=90.0)
crp = st.number_input("CRP", value=1.0)
mcv = st.number_input("MCV", value=85.0)
rdw = st.number_input("RDW", value=12.0)
alp = st.number_input("ALP", value=100.0)
wbc = st.number_input("WBC", value=6.0)
lymph = st.number_input("Lymphocytes", value=2.0)
age = st.number_input("Age", value=30)
gender = st.selectbox("Gender", ["Male", "Female"])
height = st.number_input("Height (cm)", value=170)
weight = st.number_input("Weight (kg)", value=70)

if st.button("Generate Insights"):
    with st.spinner("Contacting LLM..."):
        try:
            response = client.predict(
                albumin=albumin,
                creatinine=creatinine,
                glucose=glucose,
                crp=crp,
                mcv=mcv,
                rdw=rdw,
                alp=alp,
                wbc=wbc,
                lymph=lymph,
                age=age,
                gender=gender,
                height=height,
                weight=weight,
                api_name="/respond"
            )

            # Handle tuple response safely
            if isinstance(response, tuple):
                main_response = response[0]  # assume first element is main text
                extra = response[1:] if len(response) > 1 else None
            else:
                main_response = response
                extra = None

            # Display main insights
            st.subheader("✅ Medical Insights")
            format_llm_response(main_response)

            # Display any additional structured/text data
            if extra:
                st.subheader("📊 Additional Data")
                for item in extra:
                    if isinstance(item, str):
                        format_llm_response(item)
                    else:
                        st.json(item)

        except Exception as e:
            st.error(f"Request failed: {e}")



