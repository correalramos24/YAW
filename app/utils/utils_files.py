

from pathlib import Path
import shutil

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
    
    shutil.copytree(reference_folder, destination_folder, symlinks=True)
    print(f"Generated '{destination_folder}' from '{reference_folder}'.")


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

def check_file_exists(filePath: Path):
    return filePath.is_file()

def check_file_exists_exception(filePath: Path):
    if not filePath.is_file():
        raise Exception(filePath, "not found!")

def check_path_exists(folderPath: Path):
    return folderPath.exists()

def check_path_exists_exception(folderPath: Path):        
    if not folderPath.exists():
        raise Exception(f"{folderPath} not found!")
    
def create_dir(folderPath: Path):
    if not folderPath.exists():
        folderPath.mkdir(parents=True, exist_ok=True)
    else:
        raise Exception("Creating an already existing dir!")