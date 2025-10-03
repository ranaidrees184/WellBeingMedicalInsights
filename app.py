from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
from gradio_client import Client
import re

# -------------------------------
# Enum for gender
# -------------------------------
class Gender(str, Enum):
    male = "Male"
    female = "Female"

# -------------------------------
# Individual biomarker input
# -------------------------------
class BiomarkerInput(BaseModel):
    age: int
    albumin_gL: float
    creat_umol: float
    glucose_mmol: float
    lncrp: float
    lymph: float
    mcv: float
    rdw: float
    alp: float
    wbc: float
    gender: Gender = Field(..., description="Select 'Male' or 'Female'")
    height: Optional[float] = None
    weight: Optional[float] = None

# -------------------------------
# Request model: List of patients
# -------------------------------
class BiomarkerListRequest(BaseModel):
    patients: List[BiomarkerInput]

# -------------------------------
# Gradio client
# -------------------------------
client = Client("Muhammadidrees/MoizMedgemma27b")

# -------------------------------
# Parse LLM markdown into JSON
# -------------------------------
def parse_result_to_json(result_text: str):
    data = {
        "normal_ranges": {},
        "biomarker_table": [],
        "executive_summary": {"top_priorities": [], "key_strengths": []},
        "system_analysis": {"status": "", "explanation": ""},
        "action_plan": {"nutrition": "", "lifestyle": "", "medical": "", "testing": ""},
        "interaction_alerts": []
    }

    # Normal ranges
    normal_ranges = re.findall(r"- ([A-Za-z ]+): ([0-9.\-–]+.*)", result_text)
    for biomarker, value in normal_ranges:
        data["normal_ranges"][biomarker.strip()] = value.strip()

    # Biomarker table
    table_match = re.search(r"\| Biomarker \| Value \|.*?\|\n((?:\|.*\|\n)+)", result_text, re.S)
    if table_match:
        rows = table_match.group(1).strip().split("\n")
        for row in rows:
            parts = [p.strip() for p in row.strip("|").split("|")]
            if len(parts) == 4:
                data["biomarker_table"].append({
                    "biomarker": parts[0],
                    "value": parts[1],
                    "status": parts[2],
                    "insight": parts[3],
                })

    # Executive summary
    priorities = re.findall(r"\d+\.\s+(.*)", result_text)
    data["executive_summary"]["top_priorities"] = priorities[:3]
    strengths = re.findall(r"- Normal (.*)", result_text)
    data["executive_summary"]["key_strengths"] = strengths

    # System analysis
    sys_match = re.search(r"System-Specific Analysis\n- Status: (.*?)\n- Explanation: (.*?)\n", result_text, re.S)
    if sys_match:
        data["system_analysis"]["status"] = sys_match.group(1).strip()
        data["system_analysis"]["explanation"] = sys_match.group(2).strip()

    # Action plan
    plan_matches = re.findall(r"- (\w+): (.*)", result_text)
    for category, content in plan_matches:
        key = category.lower()
        if key in data["action_plan"]:
            data["action_plan"][key] = content.strip()

    # Interaction alerts
    interactions = re.findall(r"- (The .*?)\n", result_text)
    data["interaction_alerts"] = interactions

    return data

# -------------------------------
# FastAPI app
# -------------------------------
app = FastAPI(title="Multi-Patient Biomarker Analysis API", version="1.0")

@app.post("/analyze_patients")
async def analyze_patients(request: BiomarkerListRequest):
    results = []
    for patient in request.patients:
        try:
            # Call LLM
            result_text = client.predict(
                albumin=patient.albumin_gL,
                creatinine=patient.creat_umol,
                glucose=patient.glucose_mmol,
                crp=patient.lncrp,
                mcv=patient.mcv,
                rdw=patient.rdw,
                alp=patient.alp,
                wbc=patient.wbc,
                lymphocytes=patient.lymph,
                age=patient.age,
                gender=patient.gender.value,
                height=patient.height or 0,
                weight=patient.weight or 0,
                api_name="/respond"
            )

            # Parse markdown into structured JSON
            parsed_json = parse_result_to_json(result_text)
            results.append({"patient": patient.dict(), "analysis": parsed_json})

        except Exception as e:
            results.append({"patient": patient.dict(), "error": str(e)})

    return {"results": results}
