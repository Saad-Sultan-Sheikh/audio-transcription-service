# Audio Transcription Service

A minimal FastAPI-based audio transcription service using OpenAI Whisper.

## Overview

This service accepts audio uploads, processes them asynchronously in a background worker, and exposes a result endpoint to retrieve transcription output.

## Features

- Upload audio files via `/upload`
- Run transcription in a background thread
- Retrieve job results via `/result/{job_id}`
- Returns transcription text and timestamps for segments

## Requirements

- Python 3.10+ (recommended)
- `fastapi`
- `uvicorn`
- `whisper`
- `torch` (or `torch` compatible with Whisper)

## Installation

1. Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install fastapi uvicorn openai-whisper torch
```

> If you already have another Whisper package installed, use the package name that matches your environment.

## Running the Service

Start the app with Uvicorn:

```bash
uvicorn main:app --reload
```

The service will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Upload audio

`POST /upload`

- Request: `multipart/form-data` with file field `file`
- Response:
  - `job_id`: unique ID used to poll the result

Example using `curl`:

```bash
curl -F "file=@audio.mp3" http://127.0.0.1:8000/upload
```

### Get transcription result

`GET /result/{job_id}`

- Returns job status and transcription data when complete.
- Possible statuses:
  - `processing`
  - `completed`
  - `failed`
  - `not_found`

Example:

```bash
curl http://127.0.0.1:8000/result/<job_id>
```

## Notes

- Uploaded files are stored in the `uploads/` directory.
- The Whisper model is loaded once at startup for improved performance.
- The service currently saves uploads as `.mp3` files, so incoming audio should be compatible with that format.

## License

This project is provided as-is.
