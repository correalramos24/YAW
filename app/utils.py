
from pathlib import Path
import shutil
import subprocess

process = None

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

def copy_file(source: Path, destination: Path):
    if not source.is_file():
        raise FileNotFoundError(f"Unable to find {source}")
    try:
        shutil.copy2(source, destination)
    except PermissionError:
        print(f"Bad permisions either for {source} or {destination}.")
    except FileExistsError:
        print(f"{destination} already exists")
    except Exception as e:
        print(f"Error: {e}")

def check_path_exists(folderPath: Path):
    return folderPath.exists()

def create_dir(folderPath: Path):
    if not folderPath.exists():
        folderPath.mkdir(parents=True, exist_ok=True)
    else:
        raise Exception("Creating an already existing dir!")

def check_path_exists_exception(folderPath: Path):        
    if not folderPath.exists():
        raise Exception(f"{folderPath} not found!")
    
def execute_script(script, args, rundir, log_file=None):

    if log_file is not None:
        print(f"Executing {script} with {args} at {rundir}, writting STDOUT to {log_file}")
        fdesc_stdout = open(log_file, mode="w") 
    else:
        print(f"Executing {script} with {args} at {rundir}")
        fdesc_stdout = None

    r = subprocess.run(f"/bin/bash {script} {args}", cwd=rundir, 
            shell=True, text=True,
            stderr=subprocess.STDOUT, stdout=fdesc_stdout)

    if log_file is not None:
        fdesc_stdout.close()

    print("Completed with return code: ", r.returncode)

def execute_command(cmd: str, rundir: Path):
    subprocess.run(f"/bin/bash {cmd}", cwd=rundir, 
            shell=True, text=True,
            stderr=subprocess.STDOUT)