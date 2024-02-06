SERVERS = {"6": "America", "7": "Europe", "8": "Asia", "9": "TW, HK, MO"}


def get_server(uid):
    id = uid[0]
    for i in SERVERS.items():
        if i[0] == id:
            return i[1]

    return False
