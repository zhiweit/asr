from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse

from transcriber import AudioProcessor
import torch
models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    models["audio_processor"] = AudioProcessor()
    try:
        yield
    finally:
        # Clean up the ML models and release the resources
        for model in models.values():
            if hasattr(model, 'cleanup'):
                print('cleaning up')
                await model.cleanup()
        models.clear()
        # Force cleanup of torch resources
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print('emptied torch cuda cache')

app = FastAPI(lifespan=lifespan)


@app.get('/')
async def read_root():
    return {'Hello': 'World'}


@app.get('/ping')
async def ping():
    return 'pong'


@app.post('/transcribe/')
async def transcribe_audio(
    file: UploadFile = File(...),
):
    """
    Endpoint to transcribe audio file
    - file: Audio file (MP3, WAV, etc.)
    """
    # Validate file type
    if not file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=400,
            detail='File must be an audio file'
        )
    
    # Process audio
    try:
        audio_processor = models["audio_processor"]
        result = await audio_processor.process_audio_file(file)
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail=f'Error processing audio file: {e}'
        )
    
    return JSONResponse(result)
