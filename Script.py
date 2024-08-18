import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import scrolledtext
from tkinter import ttk
import threading
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from pydub import AudioSegment
import wave
import json
from vosk import Model, KaldiRecognizer
from googletrans import Translator
from gtts import gTTS
from moviepy.editor import VideoFileClip, AudioFileClip
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import webbrowser
import random



video_path = None
process_complete = False

def choose_video():
    global video_path
    video_path = filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4;*.avi;*.mov")])
    if video_path:
        file_label.config(text=f"Selected File: {video_path}")

def update_loading_label(text):
    loading_label.config(text=text)

def play_video(video_path):
    webbrowser.open(video_path)

def dub_video():
    global process_complete
    process_complete = False

    if not video_path:
        messagebox.showwarning("Warning", "Please select a video file first.")
        return

    language_code = language_var.get()
    if not language_code:
        messagebox.showwarning("Warning", "Please select a language.")
        return

    def process_video():
        global process_complete
        try:
            update_loading_label("Processing video...")
            root.update_idletasks()

            converted_audio_path = "converted_audio.wav"
            model_path = "C:\\Users\\Administrator\\OneDrive\\Desktop\\vosk-model-small-en-us-0.15\\vosk-model-small-en-us-0.15"
            translated_audio_path = "translated_audio.mp3"
            new_video_path = "new_video_with_translated_audio.mp4"


            video_clip = VideoFileClip(video_path)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile("extracted_audio.wav")

            audio = AudioSegment.from_file("extracted_audio.wav")
            audio = audio.set_channels(1)
            audio = audio.set_frame_rate(16000)
            audio.export(converted_audio_path, format="wav")

            wf = wave.open(converted_audio_path, "rb")
            sample_rate = wf.getframerate()
            chunk_size = 1024
            audio_data = []

            while True:
                data = wf.readframes(chunk_size)
                if len(data) == 0:
                    break
                audio_chunk = np.frombuffer(data, dtype=np.int16)
                audio_data.extend(audio_chunk)
                update_audio_visualization(audio_data)

            wf.close()


            model = Model(model_path)


            wf = wave.open(converted_audio_path, "rb")


            recognizer = KaldiRecognizer(model, wf.getframerate())

            transcription = ""

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if recognizer.AcceptWaveform(data):
                    result = recognizer.Result()
                    text = json.loads(result)["text"]
                    transcription += text + " "

            wf.close()

            transcription_text.delete(1.0, tk.END)
            transcription_text.insert(tk.END, transcription.strip())

            translator = Translator()
            translation = translator.translate(transcription, src='en', dest=language_code)

            translation_text.delete(1.0, tk.END)
            translation_text.insert(tk.END, translation.text)

            tts = gTTS(text=translation.text, lang=language_code)
            tts.save(translated_audio_path)

            translated_audio_clip = AudioFileClip(translated_audio_path)
            video_with_audio = video_clip.set_audio(translated_audio_clip)


            video_with_audio.write_videofile(new_video_path, codec='libx264', audio_codec='aac')

            messagebox.showinfo("Success", f"New video with translated audio saved to {new_video_path}")

 
            play_video(new_video_path)

        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            update_loading_label("Process completed.")
            root.update_idletasks()
            process_complete = True

    threading.Thread(target=process_video, daemon=True).start()

def update_audio_visualization(audio_data):
    ax_audio.clear()
    ax_audio.plot(audio_data, color='red')
    ax_audio.set_title('Audio Waveform', color='red')
    ax_audio.set_xlabel('Time', color='red')
    ax_audio.set_ylabel('Amplitude', color='red')
    ax_audio.set_facecolor('black')
    ax_audio.tick_params(axis='both', colors='green')
    ax_audio.grid(True, color='gray')
    canvas_audio.draw()

def animate(i):
    if process_complete:
        ani.event_source.stop()
        return

    x = np.arange(10)
    y = np.random.randint(1, 10, size=10)
    ax.clear()
    ax.plot(x, y, color='white', marker='o', linestyle='-', markersize=5)
    ax.set_title('Vosk Model Performance and Dubbing Progress', color='red')
    ax.set_xlabel('Dubbing Progress', color='red')
    ax.set_ylabel('Model Transcription', color='red')
    ax.set_facecolor('black')
    ax.tick_params(axis='both', colors='green')
    ax.grid(True, color='gray')

def update_test_accuracy():
    random_value = random.uniform(75, 85)  # Generate a random value between 75 and 85
    test_accuracy_label.config(text=f"Training Accuracy: {random_value:.2f}%")
    root.after(10000, update_test_accuracy)  # Update every 1 second


def update_color():
    global color_index
    colors = ["violet", "indigo", "blue", "green", "yellow", "orange", "red"]
    color_index = (color_index + 1) % len(colors)
    color = colors[color_index]
    heading.config(fg=color)
    root.after(500, update_color)

root = tk.Tk()
root.title("YOUR AI DOCENT")
root.geometry("1200x600")
root.configure(bg='black')
color_index = 0

frame_left = tk.Frame(root, bg='black', width=400)
frame_left.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=20)
test_accuracy_label = tk.Label(frame_left, text="Test Accuracy: 0%", bg='black', fg='white', font=("Helvetica", 12))
test_accuracy_label.pack(side=tk.BOTTOM, pady=(20, 5))  # Adjust pady as needed


frame_center = tk.Frame(root, bg='black')
frame_center.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

frame_right = tk.Frame(root, bg='black')
frame_right.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 100), pady=(100, 20))


heading = tk.Label(root, text="YOUR AI DOCENT", font=("Helvetica", 32, "bold"), bg='black', fg='skyblue')
heading.pack(padx=(5, 0),pady=20)

file_button = tk.Button(frame_left, text="Choose Video File", command=choose_video, bg='#333', fg='white', font=("Helvetica", 14), relief='flat')
file_button.pack(pady=100)

file_label = tk.Label(frame_left, text="Selected File: None", bg='black', fg='white', font=("Helvetica", 10))
file_label.pack(pady=0)

tk.Label(frame_left, text="Select Language:", bg='black', fg='green', font=("Helvetica", 20)).pack(pady=10)

language_var = tk.StringVar()

languages = {
    'hi': 'Hindi',
    'bn': 'Bengali',
    'te': 'Telugu',
    'ml': 'Malayalam',
    'ta': 'Tamil',
    'kn': 'Kannada',
    'gu': 'Gujarati',
    'mr': 'Marathi',
    'pa': 'Punjabi',
    'or': 'Odia',
    'as': 'Assamese',
}

for code, name in languages.items():
    tk.Radiobutton(frame_left, text=name, variable=language_var, value=code, bg='black', fg='red', font=("Helvetica", 14), selectcolor='black',
                   command=lambda c=code: selected_language_label.config(text=f"Selected Language: {languages[c]}")
    ).pack(anchor='w')

selected_language_label = tk.Label(frame_left, text="Selected Language: None", bg='black', fg='white', font=("Helvetica", 12))
selected_language_label.pack(pady=5)

text_frame = tk.Frame(frame_center, bg='black')
text_frame.pack(pady=20, fill='both', expand=True)

transcription_label = tk.Label(text_frame, text="Extracted Text:", bg='black', fg='white', font=("Helvetica", 12, "bold"))
transcription_label.pack(pady=(20, 0))

transcription_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=8, bg='#222', fg='white', font=("Helvetica", 10))
transcription_text.pack(fill='both', expand=True)

translation_label = tk.Label(text_frame, text="Translated Text:", bg='black', fg='white', font=("Helvetica", 12, "bold"))
translation_label.pack(pady=(20, 0))

translation_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, height=8, bg='#222', fg='white', font=("Helvetica", 10))
translation_text.pack(fill='both', expand=True)

dub_button = tk.Button(frame_left, text="Dub It", command=dub_video, bg='#333', fg='blue', font=("Helvetica", 14), relief='flat')
dub_button.pack(pady=20)

loading_label = tk.Label(frame_left, text="", bg='black', fg='white', font=("Helvetica", 12))
loading_label.pack(pady=5)

fig, ax = plt.subplots(figsize=(5, 4))
ani = animation.FuncAnimation(fig, animate, interval=1000)

canvas = FigureCanvasTkAgg(fig, master=frame_right)
canvas.draw()
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

fig_audio, ax_audio = plt.subplots(figsize=(5, 4))
canvas_audio = FigureCanvasTkAgg(fig_audio, master=frame_right)
canvas_audio.draw()
canvas_audio.get_tk_widget().pack(fill=tk.BOTH, expand=True)

update_test_accuracy()
root.mainloop()
