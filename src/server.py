from flask import Flask, render_template, request, redirect, url_for, send_file,jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from gtts import gTTS
from gtts.lang import tts_langs
from googletrans import Translator
from pydub import AudioSegment
import numpy as np
import os,json
from pytube import YouTube
from moviepy.editor import VideoFileClip, AudioFileClip, clips_array
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def generate_audio(text, lang, duration):
    # Generate audio using gTTS
    tts = gTTS(text=text, lang=lang, slow=True)
    tts.save("temp_output.mp3")
    print()
    # Load the generated audio
    audio = AudioSegment.from_file("temp_output.mp3")

    # Trim or pad the audio to match the specified duration
    if len(audio) < duration:
        silence = AudioSegment.silent(duration=duration - len(audio))
        segment_audio = audio + silence
    else:
        segment_audio = audio[:duration]
    return segment_audio

@app.route("/", methods=["GET", "POST"])
def index():
    languages = tts_langs()
    if request.method == "POST":
        try:
            data = request.get_data(as_text=True)
            data = json.loads(data)
            link = data["link"]
            dest_lang = data["target_lang"]
            print(link,dest_lang)
            video_id = link.split("v=")[1]
            srt = YouTubeTranscriptApi.get_transcript(video_id)
            lis = []
            y = []
            for i in srt:
                lis.append(i)
                y.append(i["duration"])
            translator = Translator()
            current_time = 0
            segment_audios = []
            audio = AudioSegment.silent(duration=0)
            for idx, caption in enumerate(lis):
                text = caption["text"]
                duration = caption["duration"] * 1000
                start = caption["start"] * 1000

                # Translate the English text to the destination language
                translated_text = translator.translate(text, src='en', dest=dest_lang).text
                segment_audio = generate_audio(translated_text, dest_lang, duration)
                semitones_to_shift = -3

                # Perform pitch shift
                '''segment_audio = pitch_shift(segment_audi, semitones_to_shift)'''
                silence_duration = start - current_time
                if silence_duration > 0:
                    # Pad with silence if needed to match start time

                    silence = AudioSegment.silent(duration=silence_duration)
                    audio += silence
                    current_time += silence_duration
                print(translated_text)

                if idx == 0:
                    # For the first audio file, extract the segment before the time_to_join
                    audio += segment_audio[:duration]
                else:
                    # For intermediate audio files, include the full segment
                    audio_before = audio[:start]
                    audio = audio_before + segment_audio
                current_time += duration

            audio.export("merged_output.mp3", format="mp3")
            yt = YouTube(link)
            print("YouTube Link: ",link)
            # Choose the stream (resolution and format) you want to download
            stream = yt.streams.get_highest_resolution()

            # Specify the path where you want to save the downloaded video
            file_name = 'new_video'

            # Download the video
            stream.download(filename=file_name)

            print(f'Downloaded: {yt.title}')
            video_clip = VideoFileClip(file_name)
            audio_clip = AudioFileClip("merged_output.mp3")

            # Ensure the audio duration matches the video duration (trim or pad as needed)
            if audio_clip.duration > video_clip.duration:
                audio_clip = audio_clip.subclip(0, video_clip.duration)
            elif audio_clip.duration < video_clip.duration:
                video_clip = video_clip.subclip(0,audio_clip.duration)

            # Set the audio of the video to the synchronized audio
            video_clip = video_clip.set_audio(audio_clip)
            video_name = "trans_video_" + video_id + ".mp4"
            # Write the synchronized video with audio to a new file
            video_clip.write_videofile(video_name, codec="libx264")
            return jsonify({"message": "Video processed successfully!", "video_name": video_name}),200
        except Exception as e:
            return jsonify({"error": "Failed to process video."}),500
    return redirect(url_for("play_audio"))

@app.route("/video/<video_name>")
def get_video(video_name):
    return send_file(video_name, mimetype='video/mp4')

@app.route("/play_audio")
def play_audio():
    os.system("start synchronized_video.mp4")
    return send_file("synchronized_video.mp4", as_attachment=True)

@app.route('/api/languages', methods=['GET'])
def get_languages():
    languages = {'af': 'Afrikaans', 'ar': 'Arabic', 'bg': 'Bulgarian', 'bn': 'Bengali', 'bs': 'Bosnian', 'ca': 'Catalan', 'cs': 'Czech', 'da': 'Danish', 'de': 'German', 'el': 'Greek', 'en': 'English', 'es': 'Spanish', 'et': 'Estonian', 'fi': 'Finnish', 'fr': 'French', 'gu': 'Gujarati', 'hi': 'Hindi', 'hr': 'Croatian', 'hu': 'Hungarian', 'id': 'Indonesian', 'is': 'Icelandic', 'it': 'Italian', 'iw': 'Hebrew', 'ja': 'Japanese', 'jw': 'Javanese', 'km': 'Khmer', 'kn': 'Kannada', 'ko': 'Korean', 'la': 'Latin', 'lv': 'Latvian', 'ml': 'Malayalam', 'mr': 'Marathi', 'ms': 'Malay', 'my': 'Myanmar (Burmese)', 'ne': 'Nepali', 'nl': 'Dutch', 'no': 'Norwegian', 'pl': 'Polish', 'pt': 'Portuguese', 'ro': 'Romanian', 'ru': 'Russian', 'si': 'Sinhala', 'sk': 'Slovak', 'sq': 'Albanian', 'sr': 'Serbian', 'su': 'Sundanese', 'sv': 'Swedish', 'sw': 'Swahili', 'ta': 'Tamil', 'te': 'Telugu', 'th': 'Thai', 'tl': 'Filipino', 'tr': 'Turkish', 'uk': 'Ukrainian', 'ur': 'Urdu', 'vi': 'Vietnamese', 'zh-CN': 'Chinese (Simplified)', 'zh-TW': 'Chinese (Mandarin/Taiwan)', 'zh': 'Chinese (Mandarin)'}
    return jsonify(languages)

if __name__ == "__main__":
    app.run(debug=True)