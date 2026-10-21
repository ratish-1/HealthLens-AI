"""Train separate disease models from the workbook's independent datasets."""
from pathlib import Path
import json, warnings
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
import joblib

ROOT = Path(__file__).resolve().parent
DATA, MODELS = ROOT / "data", ROOT / "models"
MODELS.mkdir(exist_ok=True)
CONFIGS = {
 "diabetes": ("diabetes.csv", "diabetes", ["gender","age","hypertension","heart_disease","smoking_history","bmi","HbA1c_level","blood_glucose_level"], "Diabetes"),
 "heart_disease": ("heart_disease.csv", "num", ["age","sex","cp","trestbps","chol","fbs","restecg","thalch","exang","oldpeak","slope","ca","thal"], "Heart Disease"),
 "brfss_diabetes": ("brfss_diabetes.csv", "Diabetes", ["Age","Sex","HighChol","CholCheck","BMI","Smoker","HeartDiseaseorAttack","PhysActivity","Fruits","Veggies","HvyAlcoholConsump","GenHlth","MentHlth","PhysHlth","DiffWalk","Stroke","HighBP"], "Community Diabetes"),
 "stroke": ("stroke.csv", "stroke", ["sex","age","hypertension","heart_disease","ever_married","work_type","Residence_type","avg_glucose_level","bmi","smoking_status"], "Stroke"),
 "kidney": ("kidney.csv", "classification", ["age","bp","sg","al","su","rbc","pc","pcc","ba","bgr","bu","sc","sod","pot","hemo","pcv","wc","rc","htn","dm","cad","appet","pe","ane"], "Kidney Disease"),
 "liver": ("liver.csv", "Diagnosis", ["Age","Gender","BMI","AlcoholConsumption","Smoking","GeneticRisk","PhysicalActivity","Diabetes","Hypertension","LiverFunctionTest"], "Liver Disease"),
 "hypertension": ("hypertension.csv", "target", ["age","sex","cp","trestbps","chol","fbs","restecg","thalach","exang","oldpeak","slope","ca","thal"], "Heart Risk (alternate dataset)")
}
def normalize_target(name, y):
    if name == "heart_disease": return (pd.to_numeric(y, errors="coerce").fillna(0) > 0).astype(int)
    if name == "kidney":
        return y.astype(str).str.strip().str.lower().map(lambda v: 1 if v in ("ckd","ckd\t","1","yes") else 0)
    if name == "brfss_diabetes":
        # CDC BRFSS: 0 = no diabetes, 1 = diabetes, 2 = prediabetes
        return pd.to_numeric(y, errors="coerce").fillna(0).map(lambda v: 0 if v == 0 else 1).astype(int)
    return pd.to_numeric(y, errors="coerce") if pd.api.types.is_numeric_dtype(y) else y
def main():
    report={}
    for key,(filename,target,features,label) in CONFIGS.items():
        df=pd.read_csv(DATA/filename)
        df=df[features+[target]].copy()
        df=df.replace(["?", " ", "None", "nan"], np.nan)
        y=normalize_target(key, df.pop(target))
        valid=y.notna()
        X=df.loc[valid].copy(); y=y.loc[valid]
        # Exclude rows where the target is not represented and make binary labels.
        if key == "liver":
            y=(pd.to_numeric(y,errors="coerce").fillna(0)>0).astype(int)
        elif key == "kidney":
            y=y.astype(int)
        elif key not in ("heart_disease","brfss_diabetes"):
            y=(pd.to_numeric(y,errors="coerce").fillna(0)>0).astype(int)
        else:
            y=y.astype(int)
        # Remove rows with a single target class after cleaning.
        if y.nunique()<2:
            print("Skipping",key,"because only one target class remains"); continue
        # Cap very large datasets to keep training practical on ordinary laptops.
        if len(X)>45000:
            sample_idx = X.sample(n=45000, random_state=42).index
            X,y=X.loc[sample_idx],y.loc[sample_idx]
        # Clean common category labels and force sensible data types.
        for col in X.columns:
            if X[col].dtype == "object":
                X[col]=X[col].astype(str).str.strip().replace({"":np.nan, "nan":np.nan, "<NA>":np.nan})
                # Convert numeric-looking object columns to numeric if most values parse.
                parsed=pd.to_numeric(X[col],errors="coerce")
                if parsed.notna().mean() > .9: X[col]=parsed
        num_cols=X.select_dtypes(include=["number","bool"]).columns.tolist()
        cat_cols=[c for c in X.columns if c not in num_cols]
        pre=ColumnTransformer([
            ("num",Pipeline([("imputer",SimpleImputer(strategy="median")),("scale",StandardScaler())]),num_cols),
            ("cat",Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore", min_frequency=2))]),cat_cols)
        ])
        Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
        candidates={
            "Logistic Regression": Pipeline([("prep",pre),("model",LogisticRegression(max_iter=1200,class_weight="balanced"))]),
            "Random Forest": Pipeline([("prep",pre),("model",RandomForestClassifier(n_estimators=120,min_samples_leaf=2,class_weight="balanced_subsample",random_state=42,n_jobs=-1,max_features="sqrt"))])
        }
        scores={}
        best_name,best_model,best_f1=None,None,-1
        for model_name,pipe in candidates.items():
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                pipe.fit(Xtr,ytr)
            pred=pipe.predict(Xte)
            f1=f1_score(yte,pred,zero_division=0)
            try: auc=roc_auc_score(yte,pipe.predict_proba(Xte)[:,1])
            except Exception: auc=None
            scores[model_name]={
                "accuracy":round(float(accuracy_score(yte,pred)),4),
                "precision":round(float(precision_score(yte,pred,zero_division=0)),4),
                "recall":round(float(recall_score(yte,pred,zero_division=0)),4),
                "f1":round(float(f1),4),
                "roc_auc":round(float(auc),4) if auc is not None else None
            }
            if f1>best_f1: best_name,best_model,best_f1=model_name,pipe,f1
        joblib.dump({"pipeline":best_model,"features":features,"label":label,"model_name":best_name,"target":target}, MODELS/f"{key}.joblib")
        report[key]={"label":label,"rows_used":int(len(X)),"features":features,"positive_rate":round(float(y.mean()),4),"best_model":best_name,"metrics":scores}
        print(f"{key}: best={best_name}, rows={len(X)}, f1={best_f1:.3f}")
    (MODELS/"metrics.json").write_text(json.dumps(report,indent=2))
    print("Saved model artifacts and metrics to",MODELS)
if __name__=="__main__": main()
