import logging
import re
from pathlib import Path

from qbittorrentapi import Client, LoginFailed

from global_var import RAW_PATH

QBT_USER = 'lemonall'
QBT_PWD = 'lemonall'
QBT_HOST = 'localhost'
QBT_PORT = '12000'


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


def download_from_file(qbt_client: Client, file: Path, save_path=RAW_PATH):
    ret = qbt_client.torrents_add(torrent_files=file.read_bytes(), save_path=save_path)
    logging.info(f'download from file: {file.name} ret: {ret}')


def download_from_link(qbt_client: Client, urls, save_path=RAW_PATH):
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
            torrent_hash = torrent['hash']
            path = torrent['content_path']
            properties = qbt_client.torrents_properties(torrent_hash=torrent_hash)

            comment = properties['comment']
            uid = int(comment.split('=')[-1])
            type = re.match(r'.*details_(.*?)\..*', comment).groups()[0]
            data = {
                'uid': uid,
                'name': torrent['name'],
                'type': type,
                'size': properties['total_size'],
                'hash': torrent_hash,
                'time': time,
                'state': 1
            }
            complete_list.append((path, data))

    return complete_list


def delete_torrent(qbt_client: Client, hash: str):
    qbt_client.torrents_delete(delete_files=False, torrent_hashes=hash)


if __name__ == '__main__':
    # load_proxy()
    file = Path('resources/torrents/1.torrent')
    urls = ['https://lemonhd.org/download.php?id=369974&passkey=fc67569039db27dabb72585070994d2d']
    qbt_client = get_qbt_client()
    # download_from_file(qbt_client, file)
    # download_from_link(qbt_client, urls)
    for torrent in qbt_client.torrents_info():
        # for k, v in torrent.items():
        #     print(k, v)
        torrent_hash = torrent['hash']
        print('- - - -- - - - - - - -- - - - - - - - - - - - -  -- - -')
        properties = qbt_client.torrents_properties(torrent_hash=torrent_hash)
        comment = properties['comment']
        uid = int(comment.split('=')[-1])
        type = re.match(r'.*details_(.*?)\..*', comment).groups()[0]
        print(torrent_hash, uid, type)
        # for k, v in data.items():
        #     print(k, v)
        print('---------------------------------------------------------')
    # print(get_complete_list(qbt_client))
    # print(qbt_client.torrents_info())

