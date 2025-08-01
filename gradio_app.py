# If you don't use pipenv, uncomment the following:
# from dotenv import load_dotenv
# load_dotenv()

# VoiceBot UI with Gradio
import os
import gradio as gr
import logging

from brain_of_the_doctor import encode_image, analyze_image_with_query
from voice_of_the_patient import record_audio, transcribe_with_groq
from voice_of_the_doctor import text_to_speech_with_gtts

# load_dotenv()  # Uncomment if you're using .env file

# System prompt for image analysis
system_prompt = """You have to act as a professional doctor, I know you are not but this is for learning purpose. 
            What's in this image? Do you find anything wrong with it medically? 
            If you make a differential, suggest some remedies for them. Don’t add any numbers or special characters in 
            your response. Your response should be in one long paragraph. Also, always answer as if you are answering to a real person.
            Don’t say 'In the image I see' but say 'With what I see, I think you have ....'
            Don't respond as an AI model in markdown, your answer should mimic that of an actual doctor not an AI bot. 
            Keep your answer concise (max 2 sentences). No preamble, start your answer right away please."""

def process_inputs(audio_filepath, image_filepath):
    if not audio_filepath or not os.path.exists(audio_filepath):
        speech_to_text_output = "No audio provided."
        doctor_response = "I didn't get your voice input. Please try speaking again."
        output_audio_path = text_to_speech_with_gtts(doctor_response) or "final.wav"
        return speech_to_text_output, doctor_response, output_audio_path

    # Transcribe voice to text
    speech_to_text_output = transcribe_with_groq(
        stt_model="whisper-large-v3",
        audio_filepath=audio_filepath,
        GROQ_API_KEY=os.environ.get("GROQ_API_KEY")
    )

    # Image analysis
    if image_filepath and os.path.exists(image_filepath):
        try:
            encoded_image = encode_image(image_filepath)
            doctor_response = analyze_image_with_query(
                query=system_prompt + " " + speech_to_text_output,
                encoded_image=encoded_image,
                model="llama-3.2-11b-vision-preview"
            )
        except Exception as e:
            logging.error(f"Image analysis failed: {e}")
            doctor_response = "I had trouble analyzing the image."
    else:
        doctor_response = "No image provided for me to analyze."

    # Text to speech
    # Clean up and check the doctor's response
    if doctor_response and isinstance(doctor_response, str) and doctor_response.strip():
        def sanitize_text_for_tts(text):
            import re
            return re.sub(r'[^\x00-\x7F]+', ' ', text)  # Removes non-ASCII characters

        max_tts_chars = 400
        if doctor_response and isinstance(doctor_response, str) and doctor_response.strip():
            safe_response = sanitize_text_for_tts(doctor_response.strip())[:max_tts_chars]
            logging.info(f"Sending this to TTS: {safe_response}")
            output_audio_path = text_to_speech_with_gtts(safe_response)
        else:
            logging.warning("Empty or invalid doctor_response for TTS.")
            doctor_response = "Sorry, I could not generate a response. Please try again."
            output_audio_path = text_to_speech_with_gtts(doctor_response)
    else:
        logging.warning("Empty or invalid doctor_response for TTS.")
        doctor_response = "Sorry, I could not generate a response. Please try again."
        output_audio_path = text_to_speech_with_gtts(doctor_response)

    if not output_audio_path:
        output_audio_path = "final.wav"

    return speech_to_text_output, doctor_response, output_audio_path

# Create the interface
iface = gr.Interface( 
    fn=process_inputs,
    inputs=[
        gr.Audio(sources=["microphone"], type="filepath", label="Your Voice"),
        gr.Image(type="filepath", label="Upload Medical Image")
    ],
    outputs=[
        gr.Textbox(label="Speech to Text"),
        gr.Textbox(label="Doctor's Response"),
        gr.Audio(label="Doctor's Voice", type="filepath")
    ],
    title="Welcome to MediBud - Your Bot Doctor"
)

iface.launch(debug=True)
