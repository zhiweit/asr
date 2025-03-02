# asr

## Prerequisites

- uv
- docker

## Automated Speech Recognition (ASR) API

### Running the ASR API Docker Container

```sh
cd asr
docker build --no-cache -t asr-api .
docker run -d --name asr-api -p 8001:8001 asr-api

# stop and remove the container
docker stop asr-api
docker rm asr-api

# start the container
docker start asr-api
```

Testing the API endpoint

```sh
curl -X POST "http://localhost:8001/transcribe/" -H "accept: application/json" -F "file=@/path/to/your/audio/file.mp3;type=audio/mpeg"

# example testing with sample mp3 file
curl -X POST 'http://localhost:8001/transcribe/' -H "accept: application/json" -F "file=@sample-0.mp3;type=audio/mpeg"
# expected output:
# {"transcription":"MY THOUGHT I HAVE NOBODY BY A BEAUTY AND WILL AS YOU PURED MISTER ROCHESTER IS SUB AND THAT SO DON'T FINE SEMPEST AND DEVOTED TA BOWD TO WHAT MIGHT IN A","duration":10.042630385487529}
```

API Documentation is available at `http://localhost:8001/docs`

### Transcribing audio files from a csv file

Copy the audio files to the `asr/data` directory.

Change the `CSV_FILE` variable in the `cv-decode.py` file to the path of the csv file containing the audio files to transcribe.

Run the script.

```sh
cd asr
source .venv/bin/activate # activate virtual environment
python cv-decode.py
```

### Development Setup for ASR API

Installing dependencies

```bash
cd asr
uv install 3.11 # install python 3.11
uv venv # create virtual environment
source .venv/bin/activate # activate virtual environment
uv sync # install dependencies
```

Local development of the ASR API

```bash
export ENV=dev # set environment to development to enable reloading
python asr_api.py
```

## Architecture

- Fastapi
- Docker
