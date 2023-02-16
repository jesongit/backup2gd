import logging
import sqlite3
from pathlib import Path
from sqlite3 import Connection

TAB_NAME = 'backup'


CREATE_TABLE_SQL = f'''
    create table if not exists {TAB_NAME}(
        uid integer primary key not null,               -- torrent_id
        name text not null,                             -- 种子名
        type text not null,                             -- 文件分类
        size integer default 0,                         -- 文件大小
        hash text default '',                           -- Hash
        time integer default 0,                         -- 下载完成时间
        state integer default 0,                       -- 状态 1 下载完成 2 压缩完成 3 上传完成
        create_time integer default current_timestamp   -- 添加时间
    );'''


def get_connect():
    """ connect sqlite file """
    conn = sqlite3.connect(f'resources/{TAB_NAME}.db')
    cursor = conn.cursor()
    cursor.execute(CREATE_TABLE_SQL)
    conn.commit()
    return conn


def find_by_uid(conn: Connection, uid: int):
    return select(conn, where=[('uid', uid)])


def find_by_name(conn: Connection, name: str):
    return select(conn, where=[('name', name)])


def select(conn: Connection, fields=None, where=None, limit=100):
    """
        :param limit: limit about row
        :param conn: sqlite.Connection
        :param fields: ['uid', 'name'] => `uid`, `name`;
                select all fields when it's None.
        :param where: [('uid', 1), ('name', 'test')] => where `uid`=1 and `name`='test';
                select all rows when it's None.
        :return List
    """
    if fields is None:
        fields = '*'
    else:
        fields = ','.join([parse_field(field) for field in fields])
    sql = f'select {fields} from {TAB_NAME}{parse_where(where)} limit {limit};'
    logging.debug(f'select sql: {sql}')

    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def insert(conn: Connection, **kwargs):
    """
        if row exist will be ignore
        :param conn: sqlite.Connection
        :param kwargs: All database fields are required
                PS: uid=1, name='test_name' and so on
    """
    fields, values = parse_kwargs(kwargs)
    sql = f"insert or ignore into {TAB_NAME} ({fields}) values ({values});"
    exec_sql(conn, sql)


def delete(conn: Connection, where=None):
    """
        :param conn: sqlite.Connection
        :param where: [('uid', 1), ('name', 'test')] => where `uid`=1 and `name`='test';
                delete all rows when it's None.
    """
    if type(where) == int:
        where = parse_where([('uid', where)])
    else:
        where = parse_where(where)
    sql = f'delete from {TAB_NAME}{where}'
    exec_sql(conn, sql)


def update(conn: Connection, where=None, **kwargs):
    """
        :param conn: sqlite.Connection
        :param where: [('uid', 1), ('name', 'test')] => where `uid`=1 and `name`='test';
                update all rows when it's None.
        :param kwargs: Fields while want to update
                PS: uid=1, name='test_name' and so on
    """
    field_value = [(field, value) for field, value in kwargs.items()]
    exec_sql(conn, f"update {TAB_NAME} set {parse_field_value(field_value)}{parse_where(where)};")


def replace(conn: Connection, **kwargs):
    """
        :param conn:
        :param kwargs: All database fields are required
                PS: uid=1, name='test_name' and so on
    """
    fields, values = parse_kwargs(kwargs)
    exec_sql(conn, f"replace into {TAB_NAME} ({fields}) values ({values});")


def exec_sql(conn: Connection, sql: str):
    logging.debug(f'exec sql: {sql}')
    cursor = conn.cursor()
    cursor.execute(sql)
    conn.commit()


def parse_kwargs(kwargs):
    fields, values = [], []
    for field, value in kwargs.items():
        fields.append(parse_field(field))
        values.append(parse_value(value))
    logging.debug(f'fields: {fields}')
    logging.debug(f'values: {values}')
    return ','.join(fields), ','.join(values)


def parse_where(where):
    if not where:
        return ''
    if type(where) == str:
        return ' where ' + where
    return ' where ' + parse_field_value(where)


def parse_field_value(field_value):
    if type(field_value) == tuple:
        field_value = [field_value]
    assert type(field_value) == list, f'field_value is {field_value}'
    logging.debug(f'parse_field_value {field_value}')
    return ' and '.join([f'{parse_field(field)}={parse_value(value)}' for field, value in field_value])


def parse_field(field):
    return f'`{field}`'


def parse_value(value):
    if type(value) == bool:
        return '1' if value else '0'
    value = str(value).replace('\'', '\'\'')
    return f'\'{value}\''
    # return value
    # else:
    #     return
    # if type(value) == int:
    #     return value
    # elif type(value) == bool:
    #     return 1 if value else 0
    # else:
    #     # 单引号替换为2个单引号
    #     value = str(value).replace('\'', '\'\'')
    #     return f'\'{value}\''


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    file = Path('D:\\AppData\\QBDownload\\耀眼的你啊.Viva.Femina.2023.S01.1080p.WEB-DL.H264.AAC-LeagueWEB')
    with get_connect() as conn:
        print(select(conn))
        # print(select(conn, where=[('name', file.name)]))
        # insert(conn, uid=1, name='test', announce='test', is_file=False, files=[])
        # insert(conn, uid=2, name='test2', announce='test2', is_file=True, files=[1])
        # insert(conn, uid=3, name='test3', announce='test3', is_file=False, files=[])
        # print(type(select(conn, ['uid'])[0][0]))
        # print(select(conn))
        # update(conn, [('uid', 1)], length=10)
        # print(select(conn))
        # replace(conn, uid=2, name='test4', length=4, announce='test4')
        # print(select(conn))
        # delete(conn, 1)
        # print(select(conn))
        # delete(conn, [('name', 'test4')])
        # print(select(conn))
        # delete(conn)
        # print(select(conn))
