import logging
from pathlib import Path

from qbittorrentapi import Client, LoginFailed

QBT_USER = 'lemonall'
QBT_PWD = 'lemonall'
QBT_HOST = 'localhost'
QBT_PORT = '23333'

DATA_DIR = r'D:\AppData\QBDownload\raw'


def get_qbt_client():
    qbt_client = Client(
        host=QBT_HOST,
        port=QBT_PORT,
        username=QBT_USER,
        password=QBT_PWD
    )
    try:
        qbt_client.auth_log_in()
        return qbt_client
    except LoginFailed as e:
        logging.info(e.args)
        return None


def download_from_file(qbt_client: Client, file: Path, save_path=DATA_DIR):
    ret = qbt_client.torrents_add(torrent_files=file.read_bytes(), save_path=save_path)
    logging.info(f'download from file: {file.name} ret: {ret}')


def download_from_link(qbt_client: Client, urls, save_path=DATA_DIR):
    ret = qbt_client.torrents_add(urls=urls, save_path=save_path)
    logging.info(f'download from urls: {urls} ret: {ret}')


def get_complete_list(qbt_client: Client):
    """
        :return: [(path, completion_time, hash, size)]
    """
    complete_list = []
    for torrent in qbt_client.torrents_info():
        if len(complete_list) > 100:
            return complete_list
        time = torrent['completion_on']
        if time > 0:
            path = torrent['content_path']
            hash = torrent['hash']
            size = torrent['size']
            complete_list.append((path, time, hash, size))

    return complete_list


def delete_torrent(qbt_client: Client, hash: str):
    qbt_client.torrents_delete(delete_files=True, torrent_hashes=hash)


if __name__ == '__main__':
    # load_proxy()
    file = Path('resources/torrents/1.torrent')
    urls = ['https://lemonhd.org/download.php?id=369974&passkey=fc67569039db27dabb72585070994d2d']
    qbt_client = get_qbt_client()
    # download_from_file(qbt_client, file)
    # download_from_link(qbt_client, urls)
    for torrent in qbt_client.torrents_info():
        for k, v in torrent.items():
            print(k, v)
        finish_time = torrent['completion_on']
        path = Path(torrent['content_path'])
        hash = torrent['hash']
        size = torrent['size']
        print('---------------------------------------------------------')
    # print(get_complete_list(qbt_client))
    # print(qbt_client.torrents_info())

