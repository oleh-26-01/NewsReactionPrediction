import os
import time
import json
import pickle

from pyrogram import Client
from pyrogram.types import Message
from threading import Thread


def log_in(auth_data_path: str, update_session_string: bool = False) -> Client:
    """
    Log in to Telegram and return the app object.
    Did not start the app.

    Parameters
    ----------
    auth_data_path : str
        Path to the json file that contains the authentication data.
    update_session_string : bool, optional
        Whether to update the session string in the json file, by default False
    """
    # print current directory
    print("Current directory:", os.getcwd())

    auth_data = open(auth_data_path, "r").read()
    auth_data = json.loads(auth_data)
    app_name = auth_data["app_name"]
    session_string = auth_data["session_string"]
    try:
        app = Client(app_name, session_string=session_string)
    except:
        api_id = auth_data["api_id"]
        api_hash = auth_data["api_hash"]
        app = Client(app_name, api_id, api_hash)

    if update_session_string:
        app.start()
        auth_data["session_string"] = app.export_session_string()
        open(auth_data_path, "w").write(json.dumps(auth_data, indent=4))
        app.stop()
    return app


def save_message(path: str, message: Message):
    """
    Save the message to a json file.

    Parameters
    ----------
    path : str
        Path to the json file.
    message : pyrogram.types.Message
        The message to be saved.
    """
    string = message.__str__()
    # remove all uncompatible characters
    string = string.encode("ascii", "ignore").decode()
    open(path, "w").write(string)


def save_pickle(path: str, data):
    """
    Save the data to a pickle file.

    Parameters
    ----------
    path : str
        Path to the pickle file.
    data : Any
        The data to be saved.
    """
    with open(path, "wb") as f:
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)


def load_pickle(path: str):
    """
    Load the data from a pickle file.

    Parameters
    ----------
    path : str
        Path to the pickle file.
    """
    with open(path, "rb") as f:
        return pickle.load(f)


def delete_message_with_delay(message: Message, delay: int = 3):
    """
    Delete the message after a delay.

    Parameters
    ----------
    message : pyrogram.types.Message
        The message to be deleted.
    delay : int, optional
        Delay in seconds, by default 3
    """

    def delete(message: Message):
        time.sleep(delay)
        message.delete()

    Thread(target=delete, args=(message,)).start()