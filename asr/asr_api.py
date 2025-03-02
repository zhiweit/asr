import asyncio
import os
import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from transcriber import AudioProcessor
import torch
import logging

models = {}

logger = logging.getLogger(__name__)


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
                await model.cleanup()
        models.clear()
        # Force cleanup of torch resources
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info('emptied torch cuda cache')

app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def timeout_middleware(request: Request, call_next):
    # Longer timeout for /transcribe endpoint
    timeout = 300 if request.url.path == "/transcribe" else 60
    try:
        return await asyncio.wait_for(call_next(request), timeout=timeout)
    except asyncio.TimeoutError:
        return JSONResponse(
            status_code=504,
            content={"detail": "Request timed out"}
        )


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

    # Transcribe audio
    try:
        audio_processor: AudioProcessor = models["audio_processor"]
        result = await audio_processor.process_audio_file(file)
        return result
    except Exception as e:
        logger.error(f'Error processing audio file: {e}')
        raise HTTPException(
            status_code=500,
            detail=f'Error processing audio file: {e}'
        )

if __name__ == '__main__':
    dev = os.environ.get('ENVIRONMENT', 'dev') == 'dev'
    workers = 1 if dev else 4
    logger.info(f'Environment: {dev}')
    uvicorn.run('asr_api:app', host='0.0.0.0', port=8001, workers=workers,
                reload=dev)
