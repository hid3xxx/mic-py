import os
from faster_whisper import WhisperModel


class WhisperTranscriber:
    def __init__(self, model_size="large-v2", device="cuda", compute_type="float16"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = WhisperModel(model_size, device=device, compute_type=compute_type)

    def transcribe(
        self, input_file, beam_size=5, accuracy_threshold=0.9, max_retries=3
    ):
        if not os.path.isfile(input_file):
            raise FileNotFoundError(f"{input_file} not found")

        transcribed_text = []
        retries = 0

        while retries < max_retries:
            try:
                segments, info = self.model.transcribe(input_file, beam_size=beam_size)

                for segment in segments:
                    if info.language_probability > accuracy_threshold:
                        transcribed_text.append(segment.text)
                    else:
                        retries += 1

                break

            except Exception as e:
                print(f"Error during transcription: {e}")
                retries += 1

        if retries >= max_retries:
            raise Exception(f"Maximum retries reached, transcription failed")

        return " ".join(transcribed_text)
