# HealthLens AI — Health Risk Prediction Web App

A portfolio-ready Data Science project built from `Health_Prediction_Project_Master_Workbook.xlsx`. It includes dataset auditing, preprocessing, exploratory analysis, model comparison, saved ML pipelines, a FastAPI backend, and a lightweight responsive frontend.

> **Medical safety:** This is an educational screening demo, not a medical device. Predictions are not diagnoses, the displayed score is not a clinically validated probability, and users should consult qualified clinicians for medical decisions. Do not use it for emergency triage or treatment decisions.

## Important dataset design choice
The workbook contains different datasets from different sources and with different feature sets. The project **does not merge these rows into one pretend patient table**. Each model is trained independently on its corresponding sheet/export.

## Features
- Independent models: diabetes, UCI heart disease, BRFSS diabetes, stroke, kidney disease, liver disease, and an alternate heart-risk dataset.
- Data Science workflow: missing-value imputation, categorical one-hot encoding, scaling numeric features, stratified train/test split, Logistic Regression vs Random Forest comparison.
- Metrics: accuracy, precision, recall, F1, ROC-AUC where available.
- FastAPI REST endpoints with interactive Swagger docs.
- Responsive frontend with model selection, dynamic input fields, prediction result and BMI calculator.
- `/api/health`, `/api/models`, `/api/metrics`, `/api/predict`, `/api/bmi`.

## Run locally (Windows)
1. Install Python 3.10+.
2. Open this project folder in VS Code.
3. Create and activate a virtual environment:
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
5. Train models (first run can take a few minutes):
   ```powershell
   python train_models.py
   ```
6. Start the API:
   ```powershell
   uvicorn app:app --reload
   ```
7. Open `http://127.0.0.1:8000` for the app and `http://127.0.0.1:8000/docs` for API docs.

If PowerShell blocks activation, use `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.\.venv\Scripts\python.exe -m uvicorn app:app --reload`.

## API example
`POST /api/predict`
```json
{
  "model": "diabetes",
  "features": {
    "gender": "Female",
    "age": 45,
    "hypertension": 0,
    "heart_disease": 0,
    "smoking_history": "never",
    "bmi": 26.2,
    "HbA1c_level": 5.7,
    "blood_glucose_level": 110
  }
}
```
The exact accepted feature keys are listed by `/api/models` and are the original feature names from each dataset.

## Project structure
```text
health_prediction_app/
├── app.py
├── train_models.py
├── requirements.txt
├── README.md
├── data/                 # separate CSV exports from workbook sheets
├── models/               # trained pipelines + metrics.json after training
└── static/
    ├── index.html
    ├── style.css
    └── app.js
```

## Portfolio talking points
- Why separate datasets/models instead of row-wise merging?
- Why impute missing values and one-hot encode categories inside a Pipeline?
- Why compare precision, recall and F1 in addition to accuracy?
- Why stratify the train/test split?
- Why keep model artifacts and API serving separate?
- Limitations: dataset bias, source/label quality, model calibration, leakage risk in some public datasets, and no external clinical validation.

## Disclaimer
The app is intended for learning and portfolio demonstration only. It is not validated for clinical use.

## Version 2.0: patient history and longitudinal tracking

This version adds a local SQLite database (`healthlens.db`) for patient profiles and dated visits, optional saving of a prediction to a selected patient's history, CSV upload metadata/storage, history browsing, numeric measurement comparison, and patient deletion. The database is created automatically on first startup.

### New features
- Create a patient profile with a generated `HL-...` patient ID; consent checkbox is required.
- Save dated check-up records as simple JSON measurements, for example `{"bmi": 24.8, "systolic_bp": 120, "diastolic_bp": 80, "glucose_mg_dl": 95}`.
- Select a patient in the prediction form to store the model, input features, prediction, score and timestamp in history.
- Upload CSV files (max 10 MB). This demo stores the CSV and its column/row metadata; it does not claim to interpret or verify uploaded medical results.
- Compare an exact numeric key (for example `bmi`) across saved visits. It reports the numerical change, not a medical “better/worse” verdict, because direction and clinical meaning depend on metric, units, and context.
- API routes: `POST/GET /api/patients`, `GET /api/patients/{patient_id}`, `POST /api/patients/{patient_id}/records`, `GET /api/patients/{patient_id}/comparison?metric=bmi`, `POST /api/patients/{patient_id}/upload-csv`, `DELETE /api/patients/{patient_id}`.

### Run after updating
From the `health_prediction_app` folder in VS Code:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

Then open `http://127.0.0.1:8000`. Existing trained models are reused; you do not need to retrain unless you change the model pipeline or dataset.

### Local storage and privacy limitations
- Profiles and visits persist in `healthlens.db`; uploaded CSV files are saved under `uploads/`.
- This is a classroom prototype with no user login, role-based access, encryption-at-rest, audit log, or production backup system. Anyone with access to the same Windows account/files can potentially access stored data.
- Use synthetic/demo records only. Do not expose this development server to the public internet or store real patient data until authentication, authorization, encryption, retention/deletion workflows, backups, and applicable privacy/legal requirements are implemented and reviewed.
- Uploaded data is separate from public model-training datasets. It is not used to retrain models automatically.

## Dataset provenance
See `DATA_SOURCE_VERIFICATION.md`. The workbook does not include complete original URLs/version/license metadata for every file. Several datasets can be matched by schema/row count, but the exact local copies and licenses must be confirmed from the original download locations before academic redistribution. The hypertension-named dataset appears to have heart-disease features; do not describe it as a hypertension model without resolving its target/source.


## Basic manual readings (no report required)

Patients can save only the readings they actually know: height, weight, systolic/diastolic blood pressure, pulse, temperature, and blood glucose. Unknown fields remain blank; the app never fills in guessed values. BMI is calculated only when both height and weight are supplied. These readings are tagged as manually entered/self-reported and are not automatically used as ML inputs. A saved reading history is not a diagnosis; only use synthetic demo data until proper authentication, encryption, and privacy safeguards are added.
