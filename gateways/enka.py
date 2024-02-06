import requests
import json


def get_genshin_account(uid: str):
    try:
        response = requests.get(url=f"https://enka.network/api/uid/{uid}")
        return json.loads(response.content.decode("utf-8"))
    except:
        return False
