import pandas as pd
import asyncio
import httpx
from tqdm.asyncio import tqdm_asyncio
import os
import tempfile
import shutil
import logging
from transcriber import TranscribeOutput

API_ENDPOINT = "http://localhost:8001/transcribe/"
CSV_FILE = "data/cv-valid-dev.csv"
BATCH_SIZE = 20
CV_FOLDER = "data/cv-valid-dev"

logging.basicConfig(filename='cv-decode.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Silence httpx INFO logs
logging.getLogger("httpx").setLevel(logging.WARNING)


async def transcribe_audio(client: httpx.AsyncClient, file_path: str):
    try:
        with open(os.path.join(CV_FOLDER, file_path), "rb") as audio_file:
            files = {"file": (os.path.basename(file_path),
                              audio_file, "audio/mpeg")}
            response = await client.post(API_ENDPOINT, files=files, timeout=300)
            response.raise_for_status()
            return TranscribeOutput(**response.json())
    except Exception as e:
        logger.error(f"Error transcribing {file_path}: {e}")
        return None


async def process_batch(df_batch):
    async with httpx.AsyncClient(timeout=None) as client:
        tasks = [transcribe_audio(client, row["filename"])
                 for _, row in df_batch.iterrows()]
        transcriptions = await asyncio.gather(*tasks)
        return transcriptions


async def main():
    temp_fd, temp_path = tempfile.mkstemp(suffix=".csv")
    os.close(temp_fd)  # Close the file descriptor immediately

    first_batch = True

    # Calculate total number of batches
    total_rows = sum(1 for _ in open(CSV_FILE)) - 1  # subtract header
    total_batches = (total_rows + BATCH_SIZE - 1) // BATCH_SIZE

    # Iterate through CSV in batches with tqdm progress bar
    with tqdm_asyncio(total=total_batches, desc="Processing batches") as pbar:
        for df_batch in pd.read_csv(CSV_FILE, chunksize=BATCH_SIZE):
            df_batch: pd.DataFrame = df_batch

            # create columns if not exists with explicit dtypes
            if 'generated_text' not in df_batch.columns:
                df_batch['generated_text'] = pd.Series(
                    [pd.NA] * len(df_batch), dtype='object')
            if 'duration' not in df_batch.columns:
                df_batch['duration'] = pd.Series(
                    [pd.NA] * len(df_batch), dtype='float')

            # Process only rows without generated_text or duration
            df_pending = df_batch[df_batch["generated_text"].isnull(
            ) | df_batch["duration"].isnull()]

            if not df_pending.empty:
                transcriptions: list[TranscribeOutput | None] = await process_batch(df_pending)

                for idx, transcription in zip(df_pending.index, transcriptions):
                    if transcription is not None:
                        df_batch.at[idx,
                                    "generated_text"] = transcription.transcription
                        df_batch.at[idx, "duration"] = transcription.duration

            # Append or write batch to temporary CSV
            df_batch.to_csv(temp_path, mode='w' if first_batch else 'a',
                            header=first_batch, index=False)
            first_batch = False

            pbar.update(1)

    # Replace original CSV with updated CSV
    shutil.move(temp_path, CSV_FILE)
    logger.info("All batches processed and CSV updated successfully.")

if __name__ == "__main__":
    asyncio.run(main())
