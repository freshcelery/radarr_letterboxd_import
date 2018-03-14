# Letterboxd Watchlist to Radarr

This application provides a round-about way of adding films from you Letterboxd watchlist to Radarr without any manual intervention. 
The idea is to allow users to add films to Radarr externally, and to easily add films from multiple watchlist sources.

### Prerequisites

In order to run this application you will need:

```
Python 3 installed
Radarr installed and configured for use
A Radarr API Key (obtainable via the Radarr UI)
One or more letterboxd users with watchlists
``` 

You will also need to configure your own config.ini file with your server's information.
You can configure this by changing the name of example_config.ini to config.ini and editing the fields to match your information:
```
[Letterboxd]
usernames = username1
            username2

[Radarr]
api_key = 1235232132142312
api_url = http://my_server.com:7878
movie_storage_path = C:\\Users\username\\Documents\\radarr.json
quality_profile = 1
root_folder_path = C:\\Film\\
```

Letterboxd:
 - Usernames: A list of usernames you want the application to monitor, each unique name on a new line.

Radarr:
 - api_key: Your radarr api key, obtained via the Settings->General tab in the Radarr UI. 
 - api_url = The url to your server, this can be local, an ip, or a remote server.
 - movie_storage_path: The path to a json file to store radarr data, this will be created if it does not already exist.
 - quality_profile: The id of the quality profile you want to use when adding movies to Radarr.
 - root_folder_path: the path to the location you want completed Radarr downloads to go. 

### Installing

Note: I suggest using venv to set up a virtual python environment before installing package. Learn more about venv here: https://docs.python.org/3/library/venv.html

Once all the pre-requisites are met, you can install the neccessary python modules by performing:

```
pip install -r requirements.txt
```

Once the required modules are installed, just run the main.py program at the root of the directory:

```
python main.py
```