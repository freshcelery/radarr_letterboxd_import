import os

def log_to_file(error_message):
    with open('./logs/error.log', 'a') as outfile:
        outfile.write(error_message)
        outfile.close()