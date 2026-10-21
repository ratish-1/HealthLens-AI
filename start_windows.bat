@echo off
if not exist .venv\Scripts\python.exe py -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe train_models.py
.venv\Scripts\python.exe -m uvicorn app:app --reload
pause
