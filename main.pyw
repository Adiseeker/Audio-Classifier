import os
import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import re

def browse_directory():
    directory = filedialog.askdirectory()
    if directory:
        list_audio_files(directory)

def list_audio_files(directory):
    audio_extensions = ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma')
    audio_files = []

    for root, _, files in os.walk(directory):
        for file in files:
            if file.lower().endswith(audio_extensions):
                audio_files.append(os.path.join(root, file))

    if audio_files:
        result_text.set('\n'.join(audio_files))
        save_button.config(state=tk.NORMAL)  # Enable save button
    else:
        result_text.set("No audio files found.")
        save_button.config(state=tk.DISABLED)  # Disable save button

def save_to_file():
    audio_files = result_text.get().split('\n')
    if audio_files and audio_files[0]:  # Check if the list is not empty
        save_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 filetypes=[("Text files", "*.txt"),
                                                            ("All files", "*.*")])
        if save_path:
            with open(save_path, 'w') as f:
                for file in audio_files:
                    f.write(file + '\n')
            messagebox.showinfo("Save Successful", f"Audio file list saved to {save_path}")
    else:
        messagebox.showwarning("Save Failed", "No audio files to save.")

def run_whisper():
    exit_code = os.system('run_whisper.bat')

    if exit_code == 0:
        print("Batch file executed successfully")
    else:
        print(f"Error occurred while executing batch file. Exit code: {exit_code}")

    try:
        with open('lista.txt', 'r') as f:
            audio_files = f.read().splitlines()

        srt_files = [os.path.splitext(file)[0] + '.srt' for file in audio_files]

        for srt_file in srt_files:
            if os.path.exists(srt_file):
                txt_file = os.path.splitext(srt_file)[0] + '.txt'
                with open(srt_file, 'r', encoding='utf-8') as srt:
                    with open(txt_file, 'w', encoding='utf-8') as txt:
                        for line in srt:
                            if not (line.strip().isdigit() or '-->' in line or line.strip() == ''):
                                txt.write(line)
                print(f"Converted {srt_file} to {txt_file}")
            else:
                print(f"Subtitle file {srt_file} not found.")

        messagebox.showinfo("Conversion Completed", "Subtitle files have been converted to text files.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")


    # Load the HTML content from the file
    with open("output.html", "r", encoding="utf-8") as file:
        html_content = file.read()

    # Split the content by the '[00:00:00.000' timestamp
    blocks = re.split(r'(?=\[00:00:00\.000)', html_content)

    # Ensure the first block is included correctly (it might contain important preamble information)
    if not blocks[0].strip().startswith('[00:00:00.000'):
        blocks = blocks[1:]  # Remove the first block if it's not starting with timestamp

    # Read the list of filenames from lista.txt and remove existing extensions
    file_names = []
    with open("lista.txt", "r") as list_file:
        file_names = list_file.read().splitlines()

    # Remove existing extensions from filenames
    file_names = [re.sub(r'\.\w+$', '', filename) for filename in file_names]

    # Modify the filenames to have HTML extension
    file_names = [filename + ".html" for filename in file_names]

    # Write each block to a separate HTML file using the filenames from lista.txt
    for i, (block, filename) in enumerate(zip(blocks, file_names)):
        with open(filename, "w", encoding="utf-8") as new_file:
            new_file.write(block)

    # Print the list of created file names
    print("Files written successfully:", file_names)

    # Remove output.html if it exists
    if os.path.exists('output.html'):
        os.remove('output.html')
        print("Removed output.html")



app = tk.Tk()
app.title("Audio File Browser")

browse_button = tk.Button(app, text="Browse Directory", command=browse_directory)
browse_button.pack(pady=20)

save_button = tk.Button(app, text="Save List", command=save_to_file, state=tk.DISABLED)
save_button.pack(pady=20)

whisper_button = tk.Button(app, text="Run Whisper", command=run_whisper)
whisper_button.pack(pady=20)

result_text = tk.StringVar()
result_label = tk.Label(app, textvariable=result_text, justify=tk.LEFT, anchor="w")
result_label.pack(padx=20, pady=20, fill=tk.BOTH)

app.mainloop()
