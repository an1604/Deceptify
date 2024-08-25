import os


class FilesManager(object):
    def __init__(self, audios_dir, app_dir, video_dir):
        self.audios_dir = audios_dir
        self.app_dir = app_dir
        self.video_dir = video_dir

    def get_audiofile_path_from_profile_name(self, profile_name):
        profile_name_voice_dir = os.path.join(self.audios_dir, profile_name + '-clone')
        files = os.listdir(profile_name_voice_dir)  # List all the files in the directory
        if files:
            voice_clone_file = [f for f in files if os.path.isfile(os.path.join(profile_name_voice_dir, f))][0]
            return os.path.join(profile_name_voice_dir, voice_clone_file)
        return None

    def get_clone_dir_from_profile_name(self, profile_name):
        profile_name_voice_dir = os.path.join(self.audios_dir, profile_name + '-clone')
        return profile_name_voice_dir

    def get_new_audiofile_path_from_profile_name(self, profile_name, audio_filename):
        profile_name_voice_dir = os.path.join(self.audios_dir, profile_name + '-clone')
        return os.path.join(profile_name_voice_dir, audio_filename)

    def get_unique_qr_path(self, profile_name):
        return os.path.join(self.app_dir, "static/" + profile_name + ".jpg")
