
from pathlib import Path
import subprocess

def run_bash_command(cmd:str, log_file_path: Path) -> int:
    with open(log_file_path, mode='w') as logfile:
        return subprocess.call(cmd, stdout=logfile, shell=False)

def run_bash_command_exception(cmd:str, log_file_path: Path) -> int:
    with open(log_file_path, mode='w') as logfile:
        if subprocess.call(cmd, stdout=logfile, shell=False) != 0:
            raise Exception("Non-0 return of command", cmd)

def copy_folder(reference_folder: Path, destination_foder: Path, force: bool):
    pass

def check_file_exists(filePath: Path):
    pass

def check_path_exists(folderPath: Path):
    pass