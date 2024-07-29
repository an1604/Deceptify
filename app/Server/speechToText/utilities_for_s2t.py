import json

end_call_phrases = [
    "goodbye",
    "bye",
    "see you soon",
    "talk to you later",
    "take care",
    "have a great day",
    "catch you later",
    "farewell",
    "all the best",
    "thanks for calling",
    "see you next time",
    "until next time",
    "stay safe",
    "have a good one",
    "see you around",
    "bye for now",
    "keep in touch",
    "it was nice talking to you",
    "speak soon",
    "have a nice day"]


def save_conversation_to_json(file_path, conversation_history):
    with open(file_path, 'w') as file:
        json.dump(conversation_history, file, indent=4)
