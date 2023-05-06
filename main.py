import asyncio
import websockets
import concurrent.futures
from mic.record import VoiceRecorder
from mic.transcribe import WhisperTranscriber

WEBSOCKET_ENDPOINT_URL = "ws://localhost:8000/ws"


async def send_data(data):
    async with websockets.connect(WEBSOCKET_ENDPOINT_URL) as websocket:
        await websocket.send(data)


def transcribe_file(transcriber, audio_file):
    try:
        transcribe_text = transcriber.transcribe(audio_file)
        print(transcribe_text)

        if "終了" in transcribe_text:
            print("Stop the server")
            return True

        if transcribe_text:
            asyncio.run(send_data(transcribe_text))
        else:
            print("Speech could not be detected!")

    except Exception as e:
        print(f"Error: {e}")

    return False


def main():
    voice_recorder = VoiceRecorder()
    transcriber = WhisperTranscriber()

    with concurrent.futures.ThreadPoolExecutor() as executor:
        while True:
            audio_file = voice_recorder.record_voice()
            future = executor.submit(transcribe_file, transcriber, audio_file)

            if future.result():
                break


if __name__ == "__main__":
    main()
