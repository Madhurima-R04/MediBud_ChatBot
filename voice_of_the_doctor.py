import os
import platform
import subprocess
from gtts import gTTS
from pydub import AudioSegment
import logging

def text_to_speech_with_gtts(input_text, output_filepath="final.wav", autoplay=False):
    if not input_text or not input_text.strip():
        logging.warning("No input text provided to TTS.")
        return None

    try:
        temp_mp3 = "temp.mp3"
        tts = gTTS(text=input_text, lang="en")
        tts.save(temp_mp3)

        # Convert MP3 to WAV
        sound = AudioSegment.from_mp3(temp_mp3)
        sound.export(output_filepath, format="wav")

        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)

        return output_filepath
    except Exception as e:
        logging.error(f"TTS conversion error: {e}")
        return None


 
# input_text = "Hi, this is Madhurima, autoplay testing!"
# text_to_speech_with_gtts(input_text=input_text, output_filepath="gtts_testing_autoplay.wav", autoplay=True)


if __name__ == "__main__":
    response_text = "Hello, your prescription is ready."
    text_to_speech_with_gtts(response_text, autoplay=True)

