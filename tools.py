import logging
import os
import re
from pathlib import Path
import torrent_parser as tp

from torrent_parser import create_torrent_file

from sqlite import get_connect, insert
from utils import parse_torrent


def load_torrents(path: Path):
    """ batch load torrent info to sqlite file """
    conn = get_connect()
    for name in os.listdir(path.resolve()):
        data = parse_torrent(path / name)
        logging.debug(f'{name}: {data}')
        insert(conn, **data)


def replace_torrent_info(path: Path, passkey):
    """ batch replace torrent passkey"""
    for name in os.listdir(path.resolve()):
        file = path / name
        data = tp.parse_torrent_file(file.resolve())
        data['announce'] = re.findall(r'(.*passkey=)', data['announce'])[0] + passkey
        create_torrent_file(file.resolve(), data)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    # load_torrents(Path(TORRENTS_PATH))
    path = Path(r'C:\Users\Jeson\Desktop\1')
    replace_torrent_info(path, "123")
    for name in os.listdir(path.resolve()):
        file = path / name
        data = parse_torrent(file)
        print(data)
    pass
