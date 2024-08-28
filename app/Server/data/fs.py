import os
import logging

import re


def clean_filename(filename):
    """
    Clean a string from punctuations or other characters that can cause exceptions
    while writing into a file.

    :param filename: The original filename string.
    :return: A cleaned version of the filename with unsafe characters removed.
    """
    # Replace unsafe characters with an underscore
    cleaned_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)

    # Remove any leading or trailing whitespace
    cleaned_filename = cleaned_filename.strip()

    # Optionally, you can add additional rules or truncate the filename if needed.
    return cleaned_filename


class FilesManager(object):
    def __init__(self, audios_dir, app_dir, video_dir,
                 attack_records_dir):
        self.audios_dir = audios_dir
        logging.critical(f"Audio directory is: {audios_dir}")
        self.app_dir = app_dir
        logging.critical(f"App directory is: {app_dir}")
        self.video_dir = video_dir
        logging.critical(f"Video directory is: {video_dir}")
        self.attack_records_dir = attack_records_dir
        logging.critical(f"Attack records directory is: {attack_records_dir}")

    def get_audiofile_path_from_profile_name(self, profile_name):
        default_record = r"C:\Users\adina\PycharmProjects\docker_app\Deceptify_update\app\Server\AudioFiles\Drake.mp3"
        try:
            profile_name_voice_dir = os.path.join(self.audios_dir, profile_name + '-clone')
            files = os.listdir(profile_name_voice_dir)  # List all the files in the directory
            if files:
                voice_clone_file = [f for f in files if os.path.isfile(os.path.join(profile_name_voice_dir, f))][0]
                return os.path.join(profile_name_voice_dir, voice_clone_file)
            return None
        except Exception as e:
            print(f"Exception in get_audiofile_path_from_profile_name for profile '{profile_name}': {str(e)}")
            return default_record

    def get_clone_dir_from_profile_name(self, profile_name):
        try:
            profile_name_voice_dir = os.path.join(self.audios_dir, profile_name + '-clone')
            return profile_name_voice_dir
        except Exception as e:
            print(f"Exception in get_clone_dir_from_profile_name for profile '{profile_name}': {str(e)}")
            return None

    def get_new_audiofile_path_from_profile_name(self, profile_name, audio_filename):
        try:
            profile_name_voice_dir = os.path.join(self.audios_dir, profile_name + '-clone')
            self.create_directory(profile_name_voice_dir)
            return os.path.join(profile_name_voice_dir,
                                clean_filename(audio_filename))
        except Exception as e:
            print(
                f"Exception in get_new_audiofile_path_from_profile_name for profile '{profile_name}' with filename '{audio_filename}': {str(e)}")
            return None

    def get_unique_qr_path(self, profile_name):
        try:
            return os.path.join(self.app_dir, "static", profile_name + ".jpg")
        except Exception as e:
            print(f"Exception in get_unique_qr_path for profile '{profile_name}': {str(e)}")
            return None

    def get_file_from_audio_dir(self, filename):
        try:
            return self.audios_dir + filename
        except Exception as e:
            print(f"Exception in get_file_from_voice_folder for filename '{filename}': {str(e)}")
            return None

    def prompt_rec_exists_in_audio_dir(self, prompt):
        try:
            return os.path.exists(os.path.join(self.audios_dir, prompt + ".wav"))
        except Exception as e:
            print(f"Exception in prompt_rec_exists_in_audio_dir for prompt '{prompt}': {str(e)}")
            return False

    def generate_path_for_clone_dir(self, profile_name):
        try:
            return os.path.join(self.audios_dir, profile_name + '-clone')
        except Exception as e:
            print(f"Exception in generate_path_for_clone_dir for profile '{profile_name}': {str(e)}")
            return None

    def create_directory(self, dir_path):
        try:
            os.makedirs(dir_path, exist_ok=True)
        except Exception as e:
            print(f"Exception in create_directory for path '{dir_path}': {str(e)}")

    def get_file_from_attack_dir(self, filename):
        return os.path.join(self.attack_records_dir, filename)

    def get_file_from_video_dir(self, filename):
        return os.path.join(self.video_dir, filename)

    def init_new_speaker(self, profile_name):
        new_dir_path = self.generate_path_for_clone_dir(profile_name)
        self.create_directory(new_dir_path)
        return new_dir_path

    def rename_file(self, dir_name, file_name, new_file_name):
        if 'attack' in dir_name.lower():
            os.rename(os.path.join(self.attack_records_dir, file_name),
                      os.path.join(self.attack_records_dir, new_file_name))
        elif 'audio' in dir_name.lower():
            os.rename(os.path.join(self.audios_dir, file_name), os.path.join(self.attack_records_dir, new_file_name))
        elif 'video' in dir_name.lower():
            os.rename(os.path.join(self.video_dir, file_name), new_file_name)
