
from pathlib import Path

class RunIfsBundle():

    type: str = "RunIfsBundle"
    model_dir  : Path = None
    resolution  : str = None
    io_task_ifs : int = 0
    io_task_nemo: int = 0
    