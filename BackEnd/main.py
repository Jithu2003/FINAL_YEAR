from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
import shutil
import os
import uuid
from googletrans import Translator
from utils import handle_prediction, generate_pdf_report

app = FastAPI()

# CORS settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Backend is running. Use POST /predict to upload and get a report."}

@app.post("/predict")
async def predict(
    name: str = Form(...),
    dob: str = Form(...),
    gender: str = Form(...),
    age: int = Form(...),
    organ: str = Form(...),
    file: UploadFile = File(...),
    language: str = Form(...),
):
    try:
        # Save uploaded file
        unique_name = str(uuid.uuid4()) + "_" + file.filename
        upload_path = os.path.join("uploads", unique_name)
        os.makedirs("uploads", exist_ok=True)
        with open(upload_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Step 1: Get the report text from prediction (English report)
        report_text = handle_prediction(organ, upload_path, name, dob, gender, age)

        # Step 2: Translate if needed (only if language is not 'en')
        if language.lower() != 'en':
            translator = Translator()
            translated_text = []
            for line in report_text.split('\n'):
                # Avoid translating file paths or technical lines
                if "generated_reports" in line or line.strip().endswith(".pdf"):
                    translated_text.append(line)
                else:
                    try:
                        translated_line = translator.translate(line, dest=language).text
                        translated_text.append(translated_line)
                    except Exception as e:
                        # If translation fails, keep the original line
                        print(f"Error translating line: {e}")
                        translated_text.append(line)
            report_text = "\n".join(translated_text)

        # Step 3: Generate the PDF report (whether it's translated or not)
        report_dir = os.path.join('backend', 'generated_reports')
        os.makedirs(report_dir, exist_ok=True)
        pdf_filename = f"{str(uuid.uuid4())}_report.pdf"
        pdf_path = os.path.join(report_dir, pdf_filename)

        # Step 4: Generate the PDF using the final report text
        generate_pdf_report(report_text, pdf_path)

        # Step 5: Return the file for download
        return FileResponse(
            path=pdf_path,
            filename=os.path.basename(pdf_path),
            media_type='application/pdf'
        )

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
