import os
import uuid
import whisper
import threading
import queue
from fastapi import FastAPI, UploadFile

app = FastAPI()

# -----------------------------
# Shared resources
# -----------------------------
job_queue = queue.Queue()
results = {}

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Load model once (important optimization)
model = whisper.load_model("base")


# =====================================================
# PART 1: CORE TRANSCRIPTION ENGINE (REUSED)
# =====================================================
def transcribe_audio(audio_path: str) -> dict:
    """
    Core transcription logic (Part 1).
    This is independent of API or system design.
    """

    result = model.transcribe(audio_path)

    return {
        "text": result["text"].strip(),
        "segments": [
            {
                "start": seg["start"],
                "end": seg["end"],
                "text": seg["text"].strip()
            }
            for seg in result["segments"]
        ]
    }


# =====================================================
# STORAGE LAYER
# =====================================================
def save_file(file: UploadFile, file_id: str) -> str:
    path = f"{UPLOAD_DIR}/{file_id}.mp3"

    with open(path, "wb") as f:
        f.write(file.file.read())

    return path


# =====================================================
# BACKGROUND WORKER
# =====================================================
def worker():
    while True:
        job_id, file_path = job_queue.get()

        try:
            output = transcribe_audio(file_path)  # <-- REUSING PART 1

            results[job_id] = {
                "status": "completed",
                "data": output
            }

        except Exception as e:
            results[job_id] = {
                "status": "failed",
                "error": str(e)
            }

        job_queue.task_done()


threading.Thread(target=worker, daemon=True).start()


# =====================================================
# API LAYER
# =====================================================
@app.post("/upload")
async def upload(file: UploadFile):
    file_id = str(uuid.uuid4())
    path = save_file(file, file_id)

    job_id = str(uuid.uuid4())
    job_queue.put((job_id, path))

    results[job_id] = {"status": "processing"}

    return {"job_id": job_id}


@app.get("/result/{job_id}")
def get_result(job_id: str):
    return results.get(job_id, {"status": "not_found"})


# Run with:
# uvicorn main:app --reload