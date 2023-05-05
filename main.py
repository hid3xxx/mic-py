import math
import wave
import requests
import pyaudio
import webrtcvad

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = int(RATE * 0.02)
WAVE_OUTPUT_FILENAME = "output.wav"
VAD_AGGRESSIVENESS = 3
SILENCE_DURATION = 0.75

audio = pyaudio.PyAudio()

stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

print("Waiting for voice...")

vad = webrtcvad.Vad()
vad.set_mode(VAD_AGGRESSIVENESS)

while True:
    data = stream.read(CHUNK)
    if vad.is_speech(data, RATE):
        frames = [data]
        break

print("Start recording...")

num_chunks_of_silence = math.ceil(SILENCE_DURATION * RATE / CHUNK)
is_speech = []

while True:
    data = stream.read(CHUNK)
    frames.append(data)

    is_speech.append(1 if vad.is_speech(data, RATE) else 0)

    if len(is_speech) > num_chunks_of_silence:
        if all(speech == 0 for speech in is_speech[-num_chunks_of_silence:]):
            break

print("Finished recording")

stream.stop_stream()
stream.close()
audio.terminate()

waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
waveFile.setnchannels(CHANNELS)
waveFile.setsampwidth(audio.get_sample_size(FORMAT))
waveFile.setframerate(RATE)
waveFile.writeframes(b''.join(frames))
waveFile.close()

url = "http://localhost:8000"
with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
    response = requests.post(url, files={"audio_file": audio_file})
