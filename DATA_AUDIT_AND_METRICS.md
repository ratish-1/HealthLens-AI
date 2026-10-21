# Data audit and model evaluation

## Dataset audit

The workbook contains separate source datasets. They are modeled independently; records are not joined across sheets.

| Module | Rows | Columns | Missing cells | Duplicate rows | Target candidate |
|---|---:|---:|---:|---:|---|
| Diabetes_Model | 100000 | 9 | 0 | 3854 | diabetes |
| Heart_Disease_Model | 920 | 16 | 1759 | 0 | num (0–4) |
| BRFSS_Diabetes | 70692 | 18 | 0 | 6672 | Diabetes |
| BRFSS_Hypertension | 26083 | 14 | 25 | 0 | target |
| Stroke_Model | 40910 | 11 | 3 | 0 | stroke |
| Kidney_Model | 400 | 26 | 1009 | 0 | classification |
| Liver_Model | 1700 | 11 | 0 | 0 | Diagnosis |
| BMI_Calculator | 500 | 4 | 0 | 11 | Index |

## Hold-out metrics

An 80/20 stratified train/test split is used where possible. The larger datasets are capped at a reproducible 45,000-row sample for local training speed. Metrics are from the current run and should be treated as development diagnostics, not clinical validation.

### Diabetes
- Rows used: 45,000; positive-label fraction: 8.5%; selected model: Random Forest

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.889 | 0.424 | 0.899 | 0.577 | 0.968 |
| Random Forest | 0.970 | 0.848 | 0.780 | 0.813 | 0.9749 |

### Heart Disease
- Rows used: 920; positive-label fraction: 55.3%; selected model: Random Forest

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.832 | 0.838 | 0.863 | 0.850 | 0.9035 |
| Random Forest | 0.870 | 0.855 | 0.922 | 0.887 | 0.9254 |

### Community Diabetes
- Rows used: 45,000; positive-label fraction: 50.2%; selected model: Random Forest

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.750 | 0.740 | 0.773 | 0.756 | 0.827 |
| Random Forest | 0.747 | 0.728 | 0.791 | 0.758 | 0.8201 |

### Stroke
- Rows used: 40,910; positive-label fraction: 50.0%; selected model: Random Forest

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.689 | 0.714 | 0.632 | 0.670 | 0.747 |
| Random Forest | 0.997 | 0.993 | 1.000 | 0.997 | 1.0 |

### Kidney Disease
- Rows used: 400; positive-label fraction: 62.5%; selected model: Random Forest

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.988 | 1.000 | 0.980 | 0.990 | 1.0 |
| Random Forest | 1.000 | 1.000 | 1.000 | 1.000 | 1.0 |

### Liver Disease
- Rows used: 1,700; positive-label fraction: 55.1%; selected model: Random Forest

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.821 | 0.862 | 0.802 | 0.831 | 0.8957 |
| Random Forest | 0.891 | 0.936 | 0.861 | 0.897 | 0.9555 |

### Heart Risk (alternate dataset)
- Rows used: 26,083; positive-label fraction: 54.7%; selected model: Random Forest

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Logistic Regression | 0.836 | 0.826 | 0.888 | 0.856 | 0.905 |
| Random Forest | 1.000 | 1.000 | 1.000 | 1.000 | 1.0 |

## Interpretation cautions
- Very high scores on some small or synthetic-looking datasets may indicate easy patterns, target leakage, duplicated patterns, or source-specific shortcuts. Investigate before presenting as evidence of real-world performance.
- Dataset-specific codes are not globally standardized. Inputs use original source fields and should be verified against source documentation before clinical interpretation.
- The model score is not calibrated and must not be presented as a real-world disease probability.
- A stronger project extension is repeated cross-validation, class-wise confusion matrices, calibration curves, feature-importance analysis, subgroup performance and external validation.