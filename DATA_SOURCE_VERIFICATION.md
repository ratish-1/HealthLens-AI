# Dataset source verification and limitations (HealthLens AI)

## Important conclusion

The workbook and CSV exports do **not** contain a complete provenance manifest (original download URLs, exact dataset version, author, license, download date, transformations, and checksums). Therefore, source matching below is a **best-effort identification from column names and row counts**, not proof that each local file is an unchanged copy of an original public dataset. Before academic submission, add the exact download URL and license for the copy actually used.

## Best-effort source map

| Local file / module | Likely match | Verification notes |
|---|---|---|
| `data/diabetes.csv` (100,000 rows; gender, age, hypertension, heart_disease, smoking_history, bmi, HbA1c_level, blood_glucose_level, diabetes) | The commonly circulated Diabetes Prediction Dataset (often attributed to `iammustafatz` on Kaggle) | The schema and row count match the widely used 100k-row copy. The local workbook does not prove the download URL or license. Do not describe it as hospital/EHR data unless the actual source says so. See [schema reference](https://github.com/whitewalker01/simple_data_history_diabetes_prediction) and the original dataset listing should be recorded from the actual download page. |
| `data/heart_disease.csv` (920 rows) | UCI Heart Disease combined data | UCI documents heart-disease datasets and target `num` (0–4); the well-known Cleveland subset alone has 303 instances, so the local 920-row version likely represents a combined version. Verify exact release and transformation. [UCI Heart Disease](https://archive.ics.uci.edu/dataset/45/heart+disease). |
| `data/brfss_diabetes.csv` (~70,692 rows) | BRFSS 2015 Diabetes Health Indicators balanced binary subset | Row count and survey-style columns resemble the balanced 70,692-row BRFSS2015 derivative. The primary survey is from CDC; a prepared ML CSV may have been redistributed by a third party. Record both the derivative download URL and CDC source documentation. [CDC 2015 BRFSS data](https://www.cdc.gov/brfss/annual_data/annual_2015.html), [dataset schema reference](https://gedeck.github.io/DS-6030/datasets/diabetes.html). |
| `data/stroke.csv` (40,910 rows) | Stroke prediction dataset, exact source uncertain | Common public stroke datasets have different sizes (one frequently used version has 5,110 rows). The 40,910-row file cannot be confidently matched from the workbook alone; inspect its row construction, duplicate rate, target balance, and any resampling/augmentation history before using its metrics. [Example public stroke dataset listing](https://www.kaggle.com/competitions/stroke-prediction-competition/data). |
| `data/kidney.csv` (400 rows, 24 clinical features plus class) | UCI Chronic Kidney Disease | Row count and clinical feature names match the UCI CKD dataset. It contains missing values and is small; a perfect score needs careful validation and duplicate/leakage checks. [UCI Chronic Kidney Disease](https://archive.ics.uci.edu/dataset/336/chronic+kidney+disease). |
| `data/liver.csv` (1,700 rows; Age, Gender, BMI, AlcoholConsumption, GeneticRisk, PhysicalActivity, Diabetes, Hypertension, LiverFunctionTest, Diagnosis) | Kazakhstan open-data liver-disease dataset | Column names and row count match a public Kazakhstan open-data listing. Confirm the original download and reuse terms for the exact file. [Kazakhstan open-data listing](https://ashyq.data.gov.kz/dataset/magda-ds-8ec6e917-d808-494a-b84d-177dd857d7c4). |
| `data/hypertension.csv` (26,083 rows) | Alternate heart/health dataset, exact source uncertain | The current model metadata calls this “Heart Risk (alternate dataset)” rather than hypertension. The exact source, target meaning, class mapping and licensing are not proven by local metadata. Verify the original workbook sheet notes and source URL before naming the model as hypertension. |
| `data/bmi_reference.csv` | BMI reference table | Likely a reference/lookup table, not a patient-level training set. Record the origin and intended use; BMI categories are screening conventions and depend on age/population context. |

## Mandatory quality checks before presenting results

1. Store source URL, author/organization, dataset version/date, license, citation, checksum, and all local transformations in a provenance manifest.
2. Reconcile every local CSV with its original source: row/column counts, column names, target definition, and value ranges.
3. For `stroke.csv`, check whether the positive class was oversampled or records duplicated; never allow copies of the same source record to appear in both train and test.
4. For kidney and alternate-heart datasets, investigate perfect F1 scores for leakage, target-derived features, duplicates, and split mistakes. Use a fixed holdout and repeated cross-validation where appropriate.
5. Report precision, recall, F1, confusion matrix, ROC-AUC where meaningful, class prevalence, and confidence intervals. A model score is not a clinical probability.
6. Keep these public training datasets separate from actual app users' records. Never append private patient records to training data without a documented, consented, ethical data-governance process.

## References

- CDC, 2015 BRFSS Survey Data and Documentation: https://www.cdc.gov/brfss/annual_data/annual_2015.html
- UCI Heart Disease: https://archive.ics.uci.edu/dataset/45/heart+disease
- UCI Chronic Kidney Disease: https://archive.ics.uci.edu/dataset/336/chronic+kidney+disease
- CDC Diabetes Health Indicators data dictionary mirror: https://gedeck.github.io/DS-6030/datasets/diabetes.html
- Kazakhstan open-data liver disease listing: https://ashyq.data.gov.kz/dataset/magda-ds-8ec6e917-d808-494a-b84d-177dd857d7c4
- Example public stroke prediction competition dataset: https://www.kaggle.com/competitions/stroke-prediction-competition/data
