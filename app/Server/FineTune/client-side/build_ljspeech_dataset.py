import subprocess
import os

bash_script_path = r"C:\Users\adina\PycharmProjects\docker_app\Deceptify\FineTune\client-side\run_client.sh"
wsl_bash_script_path = bash_script_path.replace("\\", "/").replace("C:", "/mnt/c")

print("Running the bash script...")
result = subprocess.run(["bash", wsl_bash_script_path], capture_output=True, shell=True,
                        executable="/bin/bash")

print("Output:\n", result.stdout)
print("Error:\n", result.stderr)
print("Return Code:", result.returncode)
