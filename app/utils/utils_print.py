

def critical(msg: str):
    pass

def warning(*msg_args: str):
    print("WARNING!:", *msg_args)

def info(*msg_args):
    print("INFO:", *msg_args)

def error(msg: str):
    print("ERROR!", msg)

def error_and_exit(msg: str, err_code=1):
    error(msg)
    exit(err_code)