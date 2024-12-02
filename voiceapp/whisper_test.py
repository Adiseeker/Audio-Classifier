# -*- coding: utf-8 -*-

import torch
from transformers import pipeline
from transformers.utils import is_flash_attn_2_available
import json
from tqdm import tqdm
import os
import time

# Read list of file paths from lista.txt
with open('voiceapp//lista.txt', 'r', encoding='utf-8') as f:
    file_paths = f.readlines()

# Create a pipeline for automatic speech recognition
pipe = pipeline(
    task="automatic-speech-recognition",
    model="openai/whisper-large-v3",
    torch_dtype=torch.float32,  # Model will use float32 precision
    device="cuda:0",  # Use CUDA GPU device 0 (change to 'mps' for Mac devices)
    model_kwargs={
        "attn_implementation": "flash_attention_2" if is_flash_attn_2_available() else "sdpa",  # Use FlashAttention if available
    },
)

# Summarize each file and save the summary
total_files = len(file_paths)
pbar = tqdm(total=total_files, desc="Transcribing files")

# Create output folder
output_folder = 'output'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

for file_path in file_paths:
    file_path = file_path.strip()
    
    # Check if file exists
    if os.path.exists(file_path):
        start_time = time.time()
        # Process the audio file with the pipeline
        outputs = pipe(
            file_path,
            chunk_length_s=30,  # Split the audio into 30-second chunks
            batch_size=24,  # Process 24 chunks in parallel
            return_timestamps=True,  # Include timestamps in the output
        )
        
        # Get the file name without extension
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Create folder for output
        output_subfolder = os.path.join(output_folder, file_name)
        if not os.path.exists(output_subfolder):
            os.makedirs(output_subfolder)
        
        # Save the output to a JSON file
        with open(os.path.join(output_subfolder, 'transcript.json'), 'w', encoding='utf-8') as f:
            json.dump(outputs, f, indent=4, ensure_ascii=False)
        
        # Update the progress bar
        pbar.update(1)
        pbar.set_postfix({'file': file_path, 'time': time.time() - start_time})
    
    else:
        print(f"File {file_path} does not exist.")
        pbar.update(1)

pbar.close()