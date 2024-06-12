#print(f"Server URL: {SERVER_URL}")


#def create_user(username, password):
#    try:
#        url = f"{SERVER_URL}/data"
#        data = {"username": username, "password": password}
#        response = requests.post(url, json=data)
#        if response.status_code == 409:
#            return False
#        response.raise_for_status()
#        try:
#            result = response.json()
#        except requests.exceptions.JSONDecodeError:
#            print(f"Server response: {response.text}")
#            return False
#        return True
#    except requests.exceptions.RequestException as e:
#        return False


#def generate_voice(prompt, description):
#    try:
#        # Send request to generate voice and get job ID
#        url = f"{SERVER_URL}/generate_voice"
#        data = {"prompt": prompt, "description": description}
#        response = requests.post(url, json=data)
#        response.raise_for_status()
#        job_id = response.json().get("job_id")
#
#        # Polling the job status
#        while True:
#            status_url = f"{SERVER_URL}/result/{job_id}"
#            status_response = requests.get(status_url)
#            if status_response.status_code == 200:
#                with open("AudioFiles/" + prompt + ".wav", "wb") as f:
#                    f.write(status_response.content)
#                return True
#            elif status_response.status_code == 202:
#                time.sleep(1)  # Wait a second before polling again
#            else:
#                print("Error", "Failed to retrieve the generated voice.")
#                return False
#    except requests.exceptions.RequestException as e:
#        print(None, "Error", f"Failed to generate voice: {str(e)}")
#        return False

# def get_voice_profile(username, profile_name, prompt, app, prompt_filename):
#     url = f"{SERVER_URL}/voice_profile"
#     params = {'username': username, 'profile_name': profile_name, 'prompt_filename': prompt_filename}
#     response = requests.get(url, params=params)
#     response.raise_for_status()
#     file_path = app.config['UPLOAD_FOLDER'] + '\\' + prompt + '.wav'
#     with open(file_path, 'wb') as f:
#         f.write(response.content)
#     return file_path