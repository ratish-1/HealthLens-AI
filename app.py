from pathlib import Path
from datetime import datetime, timezone
import json, math, sqlite3, uuid, csv, io
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None

ROOT = Path(__file__).resolve().parent
MODELS = ROOT / "models"
DB_PATH = ROOT / "healthlens.db"
UPLOAD_DIR = ROOT / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)
MAX_UPLOAD_BYTES = 10 * 1024 * 1024

app = FastAPI(title="HealthLens AI", version="2.0.0", description="Educational health-trend and risk-screening demo. Not a diagnosis.")
if (ROOT / "static").exists():
    app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")

MODEL_META = {
 "diabetes":{"title":"Diabetes Risk","description":"Uses age, BMI, glucose and HbA1c plus lifestyle factors."},
 "heart_disease":{"title":"Heart Disease Risk","description":"Uses common clinical features from a heart-disease dataset."},
 "brfss_diabetes":{"title":"Community Diabetes Risk","description":"Uses population-survey lifestyle and health indicators."},
 "stroke":{"title":"Stroke Risk","description":"Uses demographic and health indicators from a public dataset."},
 "kidney":{"title":"Kidney Disease Risk","description":"Uses clinical lab and symptom fields; unknown values may be left blank."},
 "liver":{"title":"Liver Disease Risk","description":"Uses demographic, lifestyle and liver-function indicators."},
 "hypertension":{"title":"Heart Risk (alternate dataset)","description":"A second heart-related dataset included in the workbook."}
}

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def init_db():
    with db() as con:
        con.execute('''CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, birth_year INTEGER, sex TEXT,
            created_at TEXT NOT NULL, consent INTEGER NOT NULL DEFAULT 0)''')
        con.execute('''CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT NOT NULL,
            recorded_at TEXT NOT NULL, record_type TEXT NOT NULL,
            measurements TEXT NOT NULL, note TEXT,
            FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE)''')
        con.execute('''CREATE TABLE IF NOT EXISTS uploads (
            id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT NOT NULL,
            original_name TEXT NOT NULL, stored_name TEXT NOT NULL,
            uploaded_at TEXT NOT NULL, rows_count INTEGER NOT NULL,
            columns_json TEXT NOT NULL,
            FOREIGN KEY(patient_id) REFERENCES patients(id) ON DELETE CASCADE)''')
init_db()


def extract_report_values(text: str):
    """Best-effort extraction of common lab values from text PDFs; values need verification."""
    import re
    found = {}
    units = r"(?:mg/dL|mmol/L|g/dL|g/L|ng/mL|pg/mL|µg/dL|ug/dL|U/L|IU/L|mIU/L|uIU/mL|%|mmHg|fL|/hpf|bpm|kg/m²|kg/m2|mm/hr|mL/min(?:/1\.73m2)?)"
    for raw in text.splitlines():
        line = " ".join(raw.strip().split())
        if len(line) < 4 or len(line) > 240: continue
        match = re.match(rf"^(.{{2,90}}?)\s+([<>≤≥]?\s*-?\d+(?:\.\d+)?)\s*({units})(?![A-Za-z])", line, re.IGNORECASE)
        if not match: continue
        name, raw_value, unit = match.groups()
        name = name.strip(" :-•")
        if not name or name.lower() in {"page", "patient id", "report date", "date"}: continue
        try: value = float(raw_value.replace(" ", "").replace("<", "").replace(">", "").replace("≤", "").replace("≥", ""))
        except ValueError: continue
        key = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")[:70]
        if key and key not in found: found[key] = {"value": value, "unit": unit, "display_name": name}
    return found

def now_iso():
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")

def get_artifact(name):
    path = MODELS / f"{name}.joblib"
    if not path.exists():
        raise HTTPException(503, f"Model '{name}' is not trained yet. Run: python train_models.py")
    return joblib.load(path)

class PredictionRequest(BaseModel):
    model: str
    features: dict
    patient_id: str | None = None
class BMIRequest(BaseModel):
    height_cm: float = Field(gt=0, le=260)
    weight_kg: float = Field(gt=0, le=500)
class PatientCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    birth_year: int | None = Field(default=None, ge=1900, le=2100)
    sex: str | None = Field(default=None, max_length=40)
    consent: bool
class RecordCreate(BaseModel):
    record_type: str = Field(default="checkup", min_length=1, max_length=60)
    measurements: dict
    note: str | None = Field(default=None, max_length=1000)
    recorded_at: str | None = None

@app.get("/", response_class=HTMLResponse)
def home():
    return (ROOT / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/api/health")
def health():
    available = [k for k in MODEL_META if (MODELS / f"{k}.joblib").exists()]
    with db() as con:
        count = con.execute("SELECT COUNT(*) FROM patients").fetchone()[0]
    return {"status":"ok", "app":"HealthLens AI", "version":"2.0.0", "available_models":available,
            "patient_profiles":count, "storage":"local SQLite database", "note":"Educational demonstration only; not medical advice."}

@app.get("/api/models")
def models():
    return {"models":[{"id":k, **v, "trained":(MODELS/f"{k}.joblib").exists()} for k,v in MODEL_META.items()]}

@app.get("/api/metrics")
def metrics():
    path = MODELS / "metrics.json"
    return {"metrics":json.loads(path.read_text()) if path.exists() else {}}

@app.post("/api/predict")
def predict(req: PredictionRequest):
    if req.model not in MODEL_META:
        raise HTTPException(400, "Unknown model. Check /api/models.")
    artifact = get_artifact(req.model)
    required = artifact["features"]
    row = {c:req.features.get(c, None) for c in required}
    X = pd.DataFrame([row], columns=required)
    try:
        pipeline = artifact["pipeline"]
        prediction = int(pipeline.predict(X)[0])
        probabilities = pipeline.predict_proba(X)[0] if hasattr(pipeline, "predict_proba") else None
        positive_prob = float(probabilities[1]) if probabilities is not None and len(probabilities)>1 else None
    except Exception as e:
        raise HTTPException(422, f"Could not process inputs. Check field names and values. Details: {str(e)[:180]}")
    score = round(positive_prob*100, 1) if positive_prob is not None else None
    result = {"model":req.model, "label":MODEL_META[req.model]["title"], "prediction":prediction,
        "result":"Higher model-estimated risk" if prediction==1 else "Lower model-estimated risk",
        "model_score_percent":score, "score_note":"Model score, not a clinically validated probability.",
        "algorithm":artifact["model_name"], "disclaimer":"Educational only. Not a diagnosis or substitute for a clinician."}
    if req.patient_id:
        with db() as con:
            if not con.execute("SELECT 1 FROM patients WHERE id=?", (req.patient_id,)).fetchone():
                raise HTTPException(404, "Patient ID not found. Select an existing patient or leave patient_id empty.")
            con.execute("INSERT INTO records(patient_id,recorded_at,record_type,measurements,note) VALUES(?,?,?,?,?)",
                (req.patient_id, now_iso(), "ml_prediction", json.dumps({"model":req.model,"prediction":prediction,"model_score_percent":score,"features":req.features}, default=str),
                 f"{MODEL_META[req.model]['title']} prediction using {artifact['model_name']}"))
        result["saved_to_patient_history"] = True
    else:
        result["saved_to_patient_history"] = False
    return result

@app.post("/api/bmi")
def bmi(req:BMIRequest):
    value = req.weight_kg / ((req.height_cm/100)**2)
    if value < 18.5: category = "Underweight"
    elif value < 25: category = "Normal range"
    elif value < 30: category = "Overweight"
    else: category = "Obesity range"
    return {"bmi":round(value,1), "category":category, "note":"Adult BMI categories are a screening guide, not a diagnosis."}

@app.post("/api/patients")
def create_patient(req: PatientCreate):
    if not req.consent:
        raise HTTPException(400, "Consent is required before saving a patient profile.")
    patient_id = "HL-" + uuid.uuid4().hex[:10].upper()
    with db() as con:
        con.execute("INSERT INTO patients(id,name,birth_year,sex,created_at,consent) VALUES(?,?,?,?,?,1)",
                    (patient_id, req.name.strip(), req.birth_year, req.sex, now_iso()))
    return {"id":patient_id,"name":req.name.strip(),"created_at":now_iso(),"message":"Patient profile created on this computer."}

@app.get("/api/patients")
def list_patients(q: str = ""):
    with db() as con:
        rows = con.execute("SELECT p.id,p.name,p.birth_year,p.sex,p.created_at,COUNT(r.id) AS record_count FROM patients p LEFT JOIN records r ON r.patient_id=p.id WHERE p.name LIKE ? OR p.id LIKE ? GROUP BY p.id ORDER BY p.created_at DESC LIMIT 100", (f"%{q}%", f"%{q}%")).fetchall()
    return {"patients":[dict(r) for r in rows]}

@app.get("/api/patients/{patient_id}")
def patient_detail(patient_id: str):
    with db() as con:
        row = con.execute("SELECT * FROM patients WHERE id=?", (patient_id,)).fetchone()
        if not row: raise HTTPException(404,"Patient not found")
        records = con.execute("SELECT * FROM records WHERE patient_id=? ORDER BY recorded_at DESC,id DESC", (patient_id,)).fetchall()
        uploads = con.execute("SELECT id,original_name,uploaded_at,rows_count,columns_json FROM uploads WHERE patient_id=? ORDER BY uploaded_at DESC", (patient_id,)).fetchall()
    result = dict(row)
    result["records"] = [{**dict(r),"measurements":json.loads(r["measurements"])} for r in records]
    result["uploads"] = [{**dict(u),"columns":json.loads(u["columns_json"])} for u in uploads]
    return result

@app.post("/api/patients/{patient_id}/records")
def add_record(patient_id: str, req: RecordCreate):
    if not req.measurements:
        raise HTTPException(400,"Add at least one measurement.")
    # Accept simple scalar values only; avoid silently storing complex or non-finite data.
    clean = {}
    for key, value in req.measurements.items():
        if not isinstance(key, str) or len(key) > 80: raise HTTPException(422,"Invalid measurement name")
        if isinstance(value, (dict,list)): raise HTTPException(422,"Measurements must be simple values")
        if isinstance(value, float) and not math.isfinite(value): raise HTTPException(422,"Measurements must be finite numbers")
        clean[key] = value
    recorded_at = req.recorded_at or now_iso()
    with db() as con:
        if not con.execute("SELECT 1 FROM patients WHERE id=?",(patient_id,)).fetchone(): raise HTTPException(404,"Patient not found")
        cur = con.execute("INSERT INTO records(patient_id,recorded_at,record_type,measurements,note) VALUES(?,?,?,?,?)",
            (patient_id,recorded_at,req.record_type,json.dumps(clean),req.note))
        record_id = cur.lastrowid
    return {"id":record_id,"patient_id":patient_id,"recorded_at":recorded_at,"message":"Visit saved."}

@app.delete("/api/patients/{patient_id}")
def delete_patient(patient_id: str):
    with db() as con:
        row = con.execute("SELECT id FROM patients WHERE id=?",(patient_id,)).fetchone()
        if not row: raise HTTPException(404,"Patient not found")
        stored = con.execute("SELECT stored_name FROM uploads WHERE patient_id=?",(patient_id,)).fetchall()
        con.execute("DELETE FROM patients WHERE id=?",(patient_id,))
    for item in stored:
        try: (UPLOAD_DIR / item[0]).unlink(missing_ok=True)
        except OSError: pass
    return {"deleted":True,"message":"Patient profile and records deleted from this local app."}

@app.post("/api/patients/{patient_id}/upload-csv")
async def upload_csv(patient_id: str, file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400,"For this version, upload a CSV file only.")
    with db() as con:
        if not con.execute("SELECT 1 FROM patients WHERE id=?",(patient_id,)).fetchone(): raise HTTPException(404,"Patient not found")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES: raise HTTPException(413,"CSV upload limit is 10 MB.")
    try:
        text = content.decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(text))
        columns = reader.fieldnames or []
        if not columns: raise ValueError("CSV must contain a header row")
        if len(columns) > 200: raise ValueError("Too many columns (maximum 200)")
        row_count = sum(1 for _ in reader)
    except Exception as e:
        raise HTTPException(422, f"Could not read CSV: {str(e)[:150]}")
    stored_name = f"{uuid.uuid4().hex}.csv"
    (UPLOAD_DIR / stored_name).write_bytes(content)
    with db() as con:
        con.execute("INSERT INTO uploads(patient_id,original_name,stored_name,uploaded_at,rows_count,columns_json) VALUES(?,?,?,?,?,?)",
            (patient_id, Path(file.filename).name[:200], stored_name, now_iso(), row_count, json.dumps(columns)))
    return {"message":"CSV stored locally. Contents are not automatically interpreted as medical measurements.","rows":row_count,"columns":columns,"filename":Path(file.filename).name}

@app.post("/api/patients/{patient_id}/upload-report")
async def upload_report(patient_id: str, file: UploadFile = File(...)):
    """Save a PDF and record possible extracted readings as unverified patient history."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(400, "Upload a PDF lab report. CSV files use the separate CSV option.")
    if PdfReader is None:
        raise HTTPException(503, "PDF reading library is missing. Install dependencies with: pip install -r requirements.txt")
    with db() as con:
        if not con.execute("SELECT 1 FROM patients WHERE id=?", (patient_id,)).fetchone(): raise HTTPException(404, "Patient not found")
    content = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(content) > MAX_UPLOAD_BYTES: raise HTTPException(413, "PDF upload limit is 10 MB.")
    if not content.startswith(b"%PDF"): raise HTTPException(422, "The selected file does not appear to be a valid PDF.")
    try:
        reader = PdfReader(io.BytesIO(content))
        if len(reader.pages) > 50: raise ValueError("PDF exceeds 50 pages")
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as e: raise HTTPException(422, f"Could not read PDF text: {str(e)[:140]}")
    extracted = extract_report_values(text)
    stored_name = f"{uuid.uuid4().hex}.pdf"
    (UPLOAD_DIR / stored_name).write_bytes(content)
    now = now_iso()
    with db() as con:
        cur = con.execute("INSERT INTO uploads(patient_id,original_name,stored_name,uploaded_at,rows_count,columns_json) VALUES(?,?,?,?,?,?)",
            (patient_id, Path(file.filename).name[:200], stored_name, now, len(extracted), json.dumps(list(extracted.keys()))))
        upload_id = cur.lastrowid
        if extracted:
            measurements = {k: v["value"] for k,v in extracted.items()}
            measurements["_extracted_report_values"] = extracted
            measurements["_entry_method"] = "pdf_text_extraction_unverified"
            con.execute("INSERT INTO records(patient_id,recorded_at,record_type,measurements,note) VALUES(?,?,?,?,?)",
                (patient_id, now, "uploaded_lab_report_extracted", json.dumps(measurements),
                 "Automatically extracted from PDF text and NOT verified. Check every value, unit, date and patient identity against the original report."))
    return {"message":"PDF saved locally. Possible values were extracted where readable text was available.", "upload_id":upload_id,
        "filename":Path(file.filename).name, "pages":len(reader.pages), "extracted_count":len(extracted),
        "extracted_values":extracted, "saved_to_history":bool(extracted),
        "warning":"Extraction may misread tables, units, signs or reference ranges. Verify every value against the original report. Scanned/image-only PDFs may return no values; OCR is not included."}

@app.get("/api/patients/{patient_id}/comparison")
def compare_records(patient_id: str, metric: str):
    with db() as con:
        if not con.execute("SELECT 1 FROM patients WHERE id=?",(patient_id,)).fetchone(): raise HTTPException(404,"Patient not found")
        rows = con.execute("SELECT id,recorded_at,record_type,measurements FROM records WHERE patient_id=? ORDER BY recorded_at ASC,id ASC",(patient_id,)).fetchall()
    points=[]
    for r in rows:
        m=json.loads(r["measurements"])
        value=m.get(metric)
        if isinstance(value,(int,float)) and not isinstance(value,bool):
            points.append({"record_id":r["id"],"recorded_at":r["recorded_at"],"record_type":r["record_type"],"value":value})
    change=None
    if len(points)>=2:
        change=round(points[-1]["value"]-points[-2]["value"],3)
    return {"patient_id":patient_id,"metric":metric,"points":points,"change_from_previous":change,"note":"A numeric change is descriptive only. Whether it is medically better or worse depends on the metric, units, context and clinician interpretation."}
