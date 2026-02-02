from pydub import AudioSegment
import os

def convert_wav_to_mp3():
    folder_path = os.getcwd()

    for filename in os.listdir(folder_path):
        # Check if the file has a .wav extension
        if filename.endswith(".wav"):
            wav_file = os.path.join(folder_path, filename)
            audio = AudioSegment.from_wav(wav_file)
            mp3_file = os.path.splitext(wav_file)[0] + ".mp3"
            
            # Export the audio as .mp3
            audio.export(mp3_file, format="mp3")
            print(f"Converted {filename} to {mp3_file}")

convert_wav_to_mp3()