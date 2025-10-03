import gradio as gr
from gradio_client import Client
import re

# ------------------ CONNECT TO YOUR LLM API ------------------
client = Client("Muhammadidrees/MoizMedgemma27b")

# ------------------ CLEANING FUNCTION ------------------
def clean_llm_output(raw_text):
    """
    Cleans LLM output for frontend display:
    - Removes raw ranges or unwanted text at the top
    - Removes 'undefined'
    - Strips extra whitespace
    """
    # Remove everything before first 'Tabular Mapping'
    split_text = re.split(r"Tabular Mapping", raw_text, maxsplit=1)
    if len(split_text) > 1:
        cleaned_text = "Tabular Mapping" + split_text[1]
    else:
        cleaned_text = raw_text

    # Remove 'undefined'
    cleaned_text = re.sub(r"\bundefined\b", "", cleaned_text, flags=re.IGNORECASE)

    # Strip extra newlines
    cleaned_text = cleaned_text.strip()

    return cleaned_text

# ------------------ PREDICTION FUNCTION ------------------
def get_biomarker_insights(input_json):
    """
    input_json: dictionary of biomarkers, e.g.
    {
        "age": 45,
        "albumin_gL": 3.5,
        "creat_umol": 1.0,
        "glucose_mmol": 90.0,
        "lncrp": 1.0,
        "mcv": 85.0,
        "rdw": 12.0,
        "alp": 100.0,
        "wbc": 6.0,
        "lymph": 30.0
    }
    """
    try:
        # Call the LLM Gradio API
        raw_response = client.predict(input_json, api_name="/predict")
        # Clean the response
        clean_response = clean_llm_output(raw_response)
        return clean_response
    except Exception as e:
        return f"Error fetching insights: {e}"

# ------------------ GRADIO INTERFACE ------------------
with gr.Blocks() as demo:
    gr.Markdown("## 🧬 Biomarker Analysis & Insights")
    
    with gr.Row():
        with gr.Column():
            # Input: JSON textbox for biomarkers
            biomarker_input = gr.Textbox(
                label="Enter biomarkers as JSON",
                placeholder='{"age": 45, "albumin_gL": 3.5, "creat_umol": 1.0, "glucose_mmol": 90.0, "lncrp": 1.0, "mcv": 85.0, "rdw": 12.0, "alp": 100.0, "wbc": 6.0, "lymph": 30.0}',
                lines=10
            )
            submit_btn = gr.Button("Get Insights")
        
        with gr.Column():
            output_box = gr.Markdown(label="AI Insights")

    # Connect button to function
    submit_btn.click(fn=lambda x: get_biomarker_insights(eval(x)), inputs=biomarker_input, outputs=output_box)

# Launch the app
demo.launch()
