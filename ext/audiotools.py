import asyncio
import concurrent.futures
from pydub import AudioSegment
import soundfile as sf
import asyncio
import numpy as np
import base64
import audioread


async def get_audio_length(filename):
    loop = asyncio.get_event_loop()
    with open(filename, 'rb') as file:
        audio_data, sample_rate = await loop.run_in_executor(None, sf.read, file)
    length_in_seconds = len(audio_data) / sample_rate
    return round(length_in_seconds, 2)

async def convert_to_ogg(input_file, output_file):
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, _convert_to_ogg_sync, input_file, output_file)

def _convert_to_ogg_sync(input_file, output_file):
    if input_file.split(".")[-1].lower() == "mp3":
        audio = AudioSegment.from_file(input_file, format="mp3")
        audio.export(output_file, format="ogg", codec="libvorbis")

        return
    audio = AudioSegment.from_file(input_file)
    audio = audio.set_frame_rate(48000)
    audio.export(output_file, format="ogg")

def ogg_to_waveform_blocking(file_path):
    # Load the OGG file
    audio = AudioSegment.from_file(file_path)

    # Extract raw audio data
    raw_data = audio.get_array_of_samples()

    # Convert raw data to numpy array
    audio_array = np.array(raw_data)

    # Normalize audio data (optional)
    audio_array = audio_array / np.max(np.abs(audio_array))

    # Convert audio array to base64 encoded string
    encoded_audio = base64.b64encode(audio_array).decode('utf-8')

    return encoded_audio

async def ogg_to_waveform(file_path):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as pool:
        return await loop.run_in_executor(pool, ogg_to_waveform_blocking, file_path)
