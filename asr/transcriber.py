from fastapi import UploadFile
from pydantic import BaseModel
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torch
import torchaudio
import soundfile as sf
import logging

SAMPLING_RATE = 16000


class TranscribeOutput(BaseModel):
    transcription: str
    duration: float


logger = logging.getLogger(__name__)


class AudioProcessor:
    def __init__(self):
        self.processor = Wav2Vec2Processor.from_pretrained('facebook/wav2vec2-base-960h')
        self.model = Wav2Vec2ForCTC.from_pretrained('facebook/wav2vec2-base-960h')

    async def process_audio_file(self, file: UploadFile) -> TranscribeOutput:
        waveform, sample_rate = sf.read(file.file)
        waveform = torch.FloatTensor(waveform)
        duration = waveform.shape[0] / sample_rate

        if sample_rate != SAMPLING_RATE:
            resampler = torchaudio.transforms.Resample(
                orig_freq=sample_rate,
                new_freq=SAMPLING_RATE
            )
            waveform = resampler(waveform)

        audio_numpy = waveform.squeeze().numpy()

        # Process with wav2vec2
        inputs = self.processor(
            audio_numpy,
            sampling_rate=SAMPLING_RATE,
            return_tensors='pt'
        )

        with torch.no_grad():
            logits = self.model(inputs.input_values).logits

        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.batch_decode(predicted_ids)[0]

        return TranscribeOutput(
            transcription=transcription,
            duration=duration
        )

    async def cleanup(self):
        # Release model resources
        del self.model
        del self.processor
