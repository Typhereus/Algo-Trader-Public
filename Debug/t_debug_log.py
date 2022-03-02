import sys

def log(log):
    file_object = open(sys.path[1] + "/Debug/debug_log.txt", "a+")
    log = str(log) + "\n"
    file_object.write(log)
    file_object.close()