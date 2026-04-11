import colorama
from colorama import Fore
import os

def delete_dynamic_models():
    colorama.init(autoreset=True)
    files_to_delete = [
        "models/bldc_pid_tuner_with_dynamic_SP.zip",
        "models/bldc_pid_tuner_with_dynamic_LOAD.zip",
        "models/bldc_pid_tuner_with_dynamic_PARAMS.zip",
    ]

    for file_path in files_to_delete:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(Fore.GREEN+ f"Success: Deleted {file_path}")
            else:
                print(f"Info: File {file_path} doesn't exist.")
        except Exception as e:
            print(Fore.RED + f"ERROR:Coulnd't delete {file_path}. Reason: {e}")

    
if __name__ == "__main__":
    delete_dynamic_models()