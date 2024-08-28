
VERBOSE_LEVEL=3

def log(*msg_args):
    if VERBOSE_LEVEL >1 : return
    print("LOG:", *msg_args)

def info(*msg_args):
    print("INFO:", *msg_args)

def warning(*msg_args: str):
    print("WARNING!", *msg_args)

def error(*msg_args: str):
    print("ERROR!", *msg_args)

def critical(*msg_args: str, err_code=1):
    print("CRITICAL!", *msg_args)
    exit(err_code)    