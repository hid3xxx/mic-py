import math
import wave
import pyaudio
import webrtcvad
import numpy as np
from typing import List


class VoiceRecorder:
    def __init__(
        self,
        format: int = pyaudio.paInt16,
        channels: int = 1,
        rate: int = 16000,
        chunk: int = None,  # type: ignore
        wave_output_filename: str = "output.wav",
        vad_aggressiveness: int = 3,
        silence_duration: float = 1,
        audio_threshold: int = 300,
    ):
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk if chunk is not None else int(rate * 0.02)
        self.wave_output_filename = wave_output_filename
        self.vad_aggressiveness = vad_aggressiveness
        self.silence_duration = silence_duration
        self.audio_threshold = audio_threshold

        self.audio = pyaudio.PyAudio()
        self.stream = self.audio.open(
            format=self.format,
            channels=self.channels,
            rate=self.rate,
            input=True,
            frames_per_buffer=self.chunk,
        )

        self.vad = webrtcvad.Vad()
        self.vad.set_mode(self.vad_aggressiveness)

    def _read_chunk(self):
        try:
            return self.stream.read(self.chunk)
        except Exception as e:
            print(f"Error: {e}")
            return None

    def _audio_level(self, data: bytes) -> float:
        audio_data = np.frombuffer(data, dtype=np.int16)
        return np.average(np.abs(audio_data))  # type: ignore

    def _wait_for_voice(self) -> List[bytes]:
        print("Waiting for voice...")
        while True:
            data = self._read_chunk()
            if data is None:
                continue
            if (
                self.vad.is_speech(data, self.rate)
                and self._audio_level(data) > self.audio_threshold
            ):
                return [data]

    def _record_voice(self, frames: List[bytes]) -> List[bytes]:
        print("Start recording...")
        num_chunks_of_silence = math.ceil(
            self.silence_duration * self.rate / self.chunk
        )
        is_speech = []

        while True:
            data = self._read_chunk()
            if data is None:
                continue
            frames.append(data)

            is_speech.append(1 if self.vad.is_speech(data, self.rate) else 0)

            if len(is_speech) > num_chunks_of_silence:
                if all(speech == 0 for speech in is_speech[-num_chunks_of_silence:]):
                    break

        print("Finished recording")
        return frames

    def _save_frames_to_file(self, frames: List[bytes]):
        try:
            with wave.open(self.wave_output_filename, "wb") as wave_file:
                wave_file.setnchannels(self.channels)
                wave_file.setsampwidth(self.audio.get_sample_size(self.format))
                wave_file.setframerate(self.rate)
                wave_file.writeframes(b"".join(frames))
        except Exception as e:
            print(f"Error: {e}")

    def record_voice(self):
        while True:
            frames = self._wait_for_voice()
            frames = self._record_voice(frames)
            self._save_frames_to_file(frames)
            return self.wave_output_filename
