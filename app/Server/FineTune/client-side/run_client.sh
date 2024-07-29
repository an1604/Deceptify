#!/bin/bash

# Function to print log messages with timestamps
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

log "Starting script execution."

# Install all the dependencies
log "Updating package lists..."
sudo apt update

log "Installing Docker..."
sudo apt install -y docker.io

log "Installing Docker Compose..."
sudo apt install -y docker-compose

log "Installing Python3 and pip..."
sudo apt install -y python3 python3-pip

log "Creating TTS directory..."
mkdir TTS
cd TTS

# Save the Python script inside the TTS directory
log "Creating generate_ljspeech.py script..."
cat << 'EOF' > generate_ljspeech.py
import os
import sys
from datetime import datetime
from shutil import copyfile
import sqlite3

def log(message):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}")

log("Starting Python script.")

# Get paths from command line arguments
directory_base_mrs = sys.argv[1]
directory_base_ljspeech = sys.argv[2]

# Get the first speaker_id from the directory
def get_first_speaker_id(directory_base_mrs):
    speaker_dir = os.path.join(directory_base_mrs, "backend", "audio_files")
    if os.path.exists(speaker_dir) and os.path.isdir(speaker_dir):
        speaker_ids = [name for name in os.listdir(speaker_dir) if os.path.isdir(os.path.join(speaker_dir, name))]
        if speaker_ids:
            return speaker_ids[0]
    return None

log("Getting first speaker ID.")
speaker_id = get_first_speaker_id(directory_base_mrs)

if speaker_id is None:
    raise Exception("No speaker_id found in the directory.")

log(f"Found speaker ID: {speaker_id}")

# Create needed folder structure for ljspeech
def folder_creation():
    now = datetime.now()
    dt_string = now.strftime("%d.%m.%Y_%H-%M-%S")

    global directory_base_ljspeech
    directory_base_ljspeech = os.path.join(directory_base_ljspeech, "LJSpeech-1.1" + dt_string)

    if not os.path.exists(directory_base_ljspeech):
        os.makedirs(directory_base_ljspeech)

    if not os.path.exists(os.path.join(directory_base_ljspeech, "wavs")):
        os.makedirs(os.path.join(directory_base_ljspeech, "wavs"))

log("Creating folder structure.")
folder_creation()

def main():
    conn = sqlite3.connect(os.path.join(directory_base_mrs, "backend", "db", "mimicstudio.db"))
    c = conn.cursor()

    log("Creating new metadata.csv for ljspeech.")
    # Create new metadata.csv for ljspeech
    metadata = open(os.path.join(directory_base_ljspeech, "metadata.csv"), mode="w", encoding="utf8")

    for row in c.execute('SELECT audio_id, prompt, lower(prompt) FROM audiomodel ORDER BY length(prompt)'):
        metadata.write(row[0] + "|" + row[1] + "|" + row[2] + "\n")
        copyfile(os.path.join(directory_base_mrs, "backend", "audio_files", speaker_id, row[0] + ".wav"), os.path.join(directory_base_ljspeech, "wavs", row[0] + ".wav"))

    metadata.close()
    log("Metadata.csv created successfully.")

if __name__ == "__main__":
    main()
    log("Python script execution finished.")
EOF

log "Cloning the mimic-recording repository."
# Cloning the mimic-recording for the record process
git clone https://github.com/MycroftAI/mimic-recording-studio.git
cd mimic-recording-studio

log "Running docker-compose to start the application."
# Run the docker-compose.yml file to run the application (in background)
sudo docker-compose up -d

# After running this command, access http://localhost:3000 to start to record.
log "You can now access http://localhost:3000 to record the mimic before finetuning the model."

# Wait for the user to finish recording
read -p "Press Enter after you have finished recording..."

log "Stopping and removing Docker containers."
# Stops and delete the containers before moving on.
sudo docker-compose down
sudo docker container prune -f

log "Creating dataset directory."
# Create the dataset directory
cd ..
mkdir dataset

log "Running the Python script to generate the LJSpeech dataset."
# Run the Python script to generate the LJSpeech dataset
python3 generate_ljspeech.py "$(pwd)/mimic-recording-studio" "$(pwd)/dataset"

log "Script execution finished."
