import os

def log_to_file(error_message):
    with open('error.log', 'a') as outfile:
        outfile.write(error_message)
        outfile.close()

if __name__ == '__main__':
    log_to_file('This is a test \n')