import logging
import os
import subprocess
from pathlib import Path
from shutil import rmtree

import py7zr
import torrent_parser as tp

from global_var import ZIP_PATH, ROOT_PATH

FCLONE_THREAD_CNT = 8
FCLONE_LOG_FILE = ROOT_PATH / 'fclone.log'


def remove(path: Path):
    if not path.exists():
        return
    if path.is_file():
        path.unlink()
    else:
        rmtree(str(path))


def load_proxy(proxy='http://127.0.0.1:7890'):
    if proxy:
        os.environ['http_proxy'] = proxy
        os.environ['https_proxy'] = proxy


def zipfile(file: Path, target_name='test', password='lemon?all', tardir=ZIP_PATH):
    """ 压缩文件/文件夹 """
    logging.debug(f'zipfile Path: {file.resolve()} to {target_name}')
    filters = [{'id': py7zr.FILTER_COPY}, {'id': py7zr.FILTER_CRYPTO_AES256_SHA256}]
    target_path = tardir / f'{target_name}.7z'
    if target_path.exists():
        logging.debug(f'{file.name} existed')
        return target_path
    logging.debug(f'{file.name} start zip.')
    with py7zr.SevenZipFile(target_path.resolve(), 'w', filters=filters, password=password) as archive:
        archive.writeall(file.resolve(), file.name)
        logging.info(f'zipfile {file.name} => {target_path.name}')
        return target_path


def backup2gd(file: Path, type, to='lemonbk1'):
    try:
        # fclone -v -u copy --transfers {同时上传文件数} --log-file {log_dir} {本地文件} {lemonbk1}:{mv}/{id.7z}
        cmd = f'fclone -v -u copyto --transfers={FCLONE_THREAD_CNT} ' \
              f'--log-file {FCLONE_LOG_FILE} {file.resolve()} {to}:{type}/{file.name}'
        logging.debug(f'fclone {file.resolve()} type: {type} to: {to}\ncmd: {cmd}')
        ret = subprocess.run(cmd, shell=True)
        logging.debug(f'fclone {file.name} ret: {ret.returncode}')
        assert ret.returncode == 0, f'name: {file.name} ret: {ret.returncode}'

        remove(file)
        return True
    except Exception as e:
        logging.info(f'fclone file Fail {e.args}')
        return False


def parse_torrent(file: Path):
    """
        {
            'announce': 'https://announce.leaguehd.com/announce.php?passkey=fc67569039db27dabb72585070994d2d',
            'comment': '雨后双禽来占竹，秋深一蝶下寻花。', 'created by': 'LeagueWEB',
            'info': {
                'files': [
                    {'length': 612757943, 'path': ['Viva.Femina.2023.S01E23.1080p.WEB-DL.H264.AAC-LeagueWEB.mp4']},
                    {'length': 630835905, 'path': ['Viva.Femina.2023.S01E24.1080p.WEB-DL.H264.AAC-LeagueWEB.mp4']}
                ],
                'name': '耀眼的你啊.Viva.Femina.2023.S01.1080p.WEB-DL.H264.AAC-LeagueWEB',
                'piece length': 4194304,
                'pieces': [...], 'private': 1, 'source': '[lemonhd.org] LemonHD'
            }
        }
        {
            'announce': 'https://announce.leaguehd.com/announce.php?passkey=fc67569039db27dabb72585070994d2d',
            'comment': 'LeagueMV', 'created by': 'MVTool-Auto',
            'info': {
                'length': 99619241,
                'name': '连诗雅 - 路再荒你在旁.2022.1080p.WEB-DL.H264.AAC-LeagueMV.mp4',
                'piece length': 4194304,
                'pieces': [...], 'private': 1, 'source': '[lemonhd.org] LemonHD'
            }
        }
    """
    data = tp.parse_torrent_file(file.resolve())
    logging.debug(data)
    if 'length' in data['info']:
        # single file
        is_file = True
        name, length = data['info']['name'], data['info']['length']
        files = [{'length': int(length), 'path': [name]}]
    else:
        # files
        is_file = False
        files = data['info']['files']
    logging.debug(f'uid: {file.stem} name: {data["info"]["name"]}\n'
                  f'is_file: {is_file} announce: {data["announce"]}\nfiles: {files}')
    return {
        'uid': int(data['comment'].split('=')[-1]),
        'files': files,
        'is_file': is_file,
        'name': data['info']['name'],
        'announce': data['announce']
    }


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    file = Path(r'C:\Users\Jeson\Desktop\MVTools')
    tarzip = Path(r'C:\Users\Jeson\Desktop\test')
    zipfile(file, '1', '123', tarzip)
    # conn = get_connect()
    # insert(conn, **data1)
    # insert(conn, **data2)
