
<h1 align="center">Deceptify</h1>

<p align="center">
  <img src="https://raw.githubusercontent.com/an1604/Deceptify/main/logo.jpeg" alt="Deceptify Logo" width="200" height="auto"/>
</p>
<div style="font-size: 22px;">
Deceptify is a project focused on using AI to conduct social engineering attacks, leveraging generative AI content like deepfakes. The primary goal is to enhance organizational awareness and preparedness against evolving digital threats.
</div>

## Features

- **AI-driven Social Engineering Attacks**: Simulates realistic social engineering scenarios.
- **Generative AI Content (Deepfakes)**: Creates deepfakes to test and improve resilience against such attacks.
- **Organizational Awareness and Readiness**: Helps develop awareness and readiness against digital threats.
- **Active Learning and Model Improvement**: Uses helper components to enhance model responses:
  1. [Telegram Chatbot for Model Response Analysis](https://github.com/an1604/llm-telegram-chatbot-.git): A Telegram chatbot used to evaluate the model's performance.
  2. [Telegram Client for Voice Clone Attacks](https://github.com/an1604/telegram-client-flask-socketio.git): Utilizes WhisperSpeech for voice cloning. The server is located in the root directory 'WhisperSpeech.'


## Technology Stack

![Flask](https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white) 
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue) 
![PyTorch](https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white) 
![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFCA28?style=for-the-badge&logo=huggingface&logoColor=black)

## Getting Started

To start using **Deceptify**, follow these steps:

1. **Clone the repository**:  
   ```bash
   git clone https://github.com/an1604/Deceptify.git
   ```

2. **Install the required dependencies**:  
   Navigate to the project directory and run the following command to install all necessary dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables for Flask**:  
   Define the `FLASK_APP` variable to point to `deceptify.py` and set the `FLASK_DEBUG` variable for development mode:  
   ```bash
   export FLASK_APP=deceptify.py
   export FLASK_DEBUG=1
   ```

4. **Navigate to the application directory**:  
   Change the directory to the app folder where the Flask application is located:  
   ```bash
   cd app
   ```

5. **Run the Flask application**:  
   Start the server by running:  
   ```bash
   flask run
   ```

6. **Set up the WhisperSpeech server**:  
   To run the WhisperSpeech server, follow these steps:

   - **Navigate to the WhisperSpeech directory**:  
     ```bash
     cd WhisperSpeech
     ```

   - **Install the required dependencies for WhisperSpeech**:  
     ```bash
     pip install -r requirements.txt
     ```

   - **Run the WhisperSpeech server**:  
     Start the server by running:  
     ```bash
     python server.py
     ```

## VB-Cable Virtual Audio Device

To create a virtual audio cable for audio processing in this project, we use **VB-Cable**.

### Download and Install VB-Cable

1. **Download VB-Cable**:  
   Visit the official website and download the VB-Cable software: [VB-Cable Download](https://vb-audio.com/Cable/).

2. **Install VB-Cable**:  
   Follow the installation instructions on the VB-Cable website to install the virtual audio driver on your system.

3. **Set Up VB-Cable for Deceptify**:  
   After installation, set VB-Cable as your default audio input and output device in your system sound settings. This will allow you to route audio through the virtual cable for processing in the Deceptify project.

## Usage

Once the application is running, you can perform the following actions:

- Create and manage social engineering campaigns
- Generate deep fake content
- Monitor and analyze campaign results

## Contributing

We welcome contributions from the community! If you'd like to contribute to Deceptify, please follow these guidelines:

1. Fork the repository
2. Create a new branch: `git checkout -b feature/your-feature-name`
3. Make your changes and commit them: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

## Docker and Containerization

We are in the process of containerizing **Deceptify** to simplify deployment and enhance scalability. 
### Current Status

- The Docker setup for **Deceptify** is still under development. We are working on creating Dockerfiles and related configurations to ensure a smooth containerization process.
- Once completed, the repository will be updated with the necessary Dockerfiles, along with detailed instructions for building and running the Docker containers.

### Next Steps

1. **Creating Dockerfiles**: Define Dockerfiles for each project component, including the server, chatbot, and remote server.
2. **Integrate Stable Diffusion**: Implement a stable diffusion model to generate deepfakes in real-time, providing a cost-effective alternative to current solutions.
3. **Utilize AI Web Scraper**: Leverage our existing AI-powered web scraper to gather relevant data on speech patterns, language use, and communication styles, enhancing the authenticity and effectiveness of mimicked content.
4. **Use your imagination**: Use your imagination to create real-world scenarios using our technologies.
5. **Improve technologies**: We are open to every technological improvement, for our models and even more.

## Disclaimer

**We take NO responsibility for the use of this project. This code is intended for educational purposes. Please DO NOT use this program for malicious purposes.**