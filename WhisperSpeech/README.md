# WhisperSpeech Remote Server

This repository contains a remote server designed to create profiles and generate high-accuracy voice clones from a given audio recording. The server utilizes the WhisperSpeech voice model to achieve high fidelity in voice cloning.

## Features

- **Profile Creation**: Create user profiles for personalized voice cloning.
- **High-Accuracy Voice Cloning**: Generate high-quality voice clones from provided audio samples using the WhisperSpeech model.
- **Remote Server Capabilities**: Offers a remote endpoint for voice cloning requests, requiring significant computing resources.

## Technology Stack

- ![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white) - A deep learning framework for building and training machine learning models.
- ![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) - A micro web framework for Python.
- ![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFCA28?style=for-the-badge&logo=huggingface&logoColor=black) - A platform providing state-of-the-art NLP models and tools.
- ![Ollama](https://img.shields.io/badge/Ollama-008080?style=for-the-badge) - Used for model deployment and inference.

## Requirements

- A machine with a GPU is recommended for optimal performance, as the server requires significant computing resources to produce high-level responses.

## Getting Started

To set up and run the WhisperSpeech Remote Server, follow these steps:

1. **Clone the repository**:  
   Download the repository to your local machine by running:  
   ```bash
   git clone https://github.com/an1604/Deceptify/tree/main/Remote_Server
   ```

2. **Install the required dependencies**:  
   Ensure you have Python and the necessary libraries installed, then run the following command to install all dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server**:  
   Start the remote server by running:  
   ```bash
   python server.py
   ```

## Usage

Once the server is running, it will be ready to handle requests for profile creation and voice cloning. Make sure that the machine has a GPU to handle the intensive computing tasks required for high-accuracy voice cloning.
