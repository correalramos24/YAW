
from pathlib import Path
import shutil
import subprocess

process = None

def start_bash_console(log_file_path: Path):
    global process 
    print("Starting bash instance, output redirected to", log_file_path)
    with open(log_file_path, mode='w') as logfile:
        process= subprocess.Popen(['/bin/bash'], 
                stdin=subprocess.PIPE, stdout=logfile, stderr=logfile, text=True)

def run_bash_command(cmd:str) -> int:
    global process
    if process is None:
        Exception("Invalid state of process", process)
    
    print(">", cmd)
    process.stdin.write(cmd + '\n')


def finish_bash_console():
    global process
    process.stdin.close()
    stdout, stderr = process.communicate()
    print("Ending bash instance")
    return stdout, stderr




def copy_folder(reference_folder: Path, destination_folder: Path, force: bool):
    if not reference_folder.exists():
        raise FileNotFoundError(f"Reference folder '{reference_folder}' not found.")
    
    if not reference_folder.is_dir():
        raise NotADirectoryError(f"'{reference_folder}' isn't a folder.")

    if destination_folder.exists():
        if not force:
            raise FileExistsError(f"Destination folder '{destination_folder}' exists, use force.")
        else:
            shutil.rmtree(destination_folder)
    
    shutil.copytree(reference_folder, destination_folder)
    print(f"Generated '{destination_folder}' from '{reference_folder}'.")

def check_file_exists(filePath: Path):
    if not filePath.is_file():
        raise Exception(filePath, "not found!")

def check_path_exists(folderPath: Path):        
    if not folderPath.exists():
        raise Exception(f"{folderPath} not found!")
    