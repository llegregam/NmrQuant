from threading import Thread
import requests
import pathlib

import nmrquant

__version__ = "1.2.11"

def get_last_version():
    """Get last package version."""
    try:
        pf_path = pathlib.Path(nmrquant.__file__).parent
        # Get the version from pypi
        response = requests.get('https://pypi.org/pypi/nmrquant/json')
        latest_version = response.json()['info']['version']
        if latest_version != __version__:
            print(f"A new version of NMRQuant is available: v{latest_version}\n"
                  f"Use 'pip install --upgrade nmrquant' to update.\n"
                  f"Current version: v{__version__}")
        else:
            print(f"NMRQuant version v{__version__}")
    except Exception as e:
        print(f"Error checking version from pypi: \n {e}")


thread = Thread(target=get_last_version)
thread.start()
