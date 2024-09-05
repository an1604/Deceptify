# Deceptify

Deceptify is a project focused on using AI to conduct social engineering attacks, leveraging generative AI content like deepfakes. The primary goal is to enhance organizational awareness and preparedness against evolving digital threats.

## Features

- **AI-driven Social Engineering Attacks**: Simulates realistic social engineering scenarios.
- **Generative AI Content (Deepfakes)**: Creates deepfakes to test and improve resilience against such attacks.
- **Organizational Awareness and Readiness**: Helps develop awareness and readiness against digital threats.
- **Active Learning and Model Improvement**: Uses helper components to enhance model responses:
  1. [Telegram Chatbot for Model Response Analysis](https://github.com/an1604/llm-telegram-chatbot-.git): A Telegram chatbot used to evaluate the model's performance.
  2. [Telegram Client for Voice Clone Attacks](https://github.com/an1604/telegram-client-flask-socketio.git): Utilizes WhisperSpeech for voice cloning. The server is located in the root directory 'WhisperSpeech.'
  3. [Remote Server for Resource-Intensive Tasks](https://github.com/GurLurye/Remote_Server.git): Manages computationally heavy tasks, such as record generation from the voice model and voice cloning.

## Technology Stack: 

<img  src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white
"/> 

![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)


## Getting Started

To get started with Deceptify, follow these steps:

1. Clone the repository: `git clone https://github.com/OmerBart/Deceptify.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the application: Navigate to the Server folder and run `python deceptify.py`

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

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

## Badges  
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](https://choosealicense.com/licenses/mit/)  
[![GPLv3 License](https://img.shields.io/badge/License-GPL%20v3-yellow.svg)](https://choosealicense.com/licenses/gpl-3.0/)  
[![AGPL License](https://img.shields.io/badge/license-AGPL-blue.svg)](https://choosealicense.com/licenses/gpl-3.0/)  


)  

