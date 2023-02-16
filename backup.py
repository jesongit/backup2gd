import time
import logging
import threading
from os import mkdir

from pathlib import Path
from sqlite3 import Connection
from qbittorrentapi import Client

from global_var import TORRENTS_PATH, RAW_PATH, ZIP_PATH
from sqlite import get_connect, update, select, insert
from qbittorrent import get_qbt_client, get_complete_list, download_from_file, delete_torrent
from utils import zipfile, backup2gd, remove

MAX_DOWNLOAD_TASK = 500

PRODUCER_SEMAPHORE = threading.Semaphore(10)  # 限制线程最大数量


def deal_download_file(conn: Connection, qbt_client: Client, path: Path, data):
    try:
        logging.info(f'start deal {data}')
        # 记录到数据库
        name = data['name']
        path = Path(path)
        assert path.exists(), 'file no exist.'
        insert(conn, **data)
        logging.info(f'insert to db. {name}')

        # 压缩文件
        uid = data['uid']
        where = [('uid', uid)]
        zip_path = zipfile(path, uid)
        update(conn, where=where, state=2)
        logging.info(f'zip complete. {name}')

        # 删除源文件
        remove(path)
        delete_torrent(qbt_client, hash=data['hash'])
        logging.info(f'delete complete. {name}')

        # 备份到gd
        if backup2gd(zip_path, data['type']):
            update(conn, where=where, state=3)
            logging.info(f'backup complete. {name}')
    except Exception as e:
        logging.error(f'deal file error {e.args}')


def download_from_lemon(conn: Connection, qbt_client: Client):
    download_list = select(conn, ['uid'], [('state', 0)])
    while download_list:
        try:
            while len(qbt_client.torrents_info()) > MAX_DOWNLOAD_TASK:
                time.sleep(60)
            for uid in download_list:
                file = TORRENTS_PATH / f'{uid}.torrent'
                download_from_file(qbt_client, file, RAW_PATH / 'uid')
            download_list = select(conn, ['uid'], [('state', 0)])
        except Exception as e:
            logging.error(f'download file error {e.args}')


if __name__ == '__main__':

    logging.basicConfig(level=logging.DEBUG)
    # logging.basicConfig(level=logging.INFO, filename='resources/backup.log')

    if not ZIP_PATH.exists():
        mkdir(ZIP_PATH.resolve())
    conn = get_connect()
    qbt_client = get_qbt_client()
    assert qbt_client, 'qbittorrent connect fail'

    while True:
        deal_list = get_complete_list(qbt_client)
        for path, data in deal_list:
            with PRODUCER_SEMAPHORE:
                deal_thread = threading.Thread(target=deal_download_file,
                                               args=(conn, qbt_client, path, data), daemon=True)
                deal_thread.start()
        time.sleep(300)

    # download_thread = threading.Thread(target=download_from_lemon, args=(conn, qbt_client), daemon=True)
    # download_thread.start()
    # download_thread.join()
