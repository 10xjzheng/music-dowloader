# -*- coding: utf-8 -*-

import os
from urllib.request import urlopen
import requests
import re
from tqdm import tqdm
import json
import html.parser
import urllib.parse

URL_PATTERN_ID = 'http://www.xiami.com/song/playlist/id/%d'
URL_PATTERN_SONG = URL_PATTERN_ID + '/object_name/default/object_id/0/cat/json'
URL_PATTERN_PLAYLIST = URL_PATTERN_ID + '/type/3/cat/json'
URL_PATTERN_ALBUM = URL_PATTERN_ID + '/type/1/cat/json'
# http头信息
HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 7.1; Trident/5.0)',
    'Referer': 'http://www.xiami.com/song/play'
}


def parse_arguments():
    """
    命令的帮助信息设置
    :return:
    """
    note = '需要下载的专辑(album)ID, 歌单(playlist)ID, 歌曲(song)ID' \
           '从虾米音乐的网页版获取.'
    parser = argparse.ArgumentParser(description=note)

    parser.add_argument('-v', '--version', action='version',
                        version='1.0')
    parser.add_argument('-s', '--song', action='append',
                        help='adds songs for download',
                        nargs='+')
    parser.add_argument('-a', '--album', action='append',
                        help='adds all songs in the albums for download',
                        nargs='+')
    parser.add_argument('-p', '--playlist', action='append',
                        help='adds all songs in the playlists for download',
                        nargs='+')
    parser.add_argument('-t', '--to', action='append',
                        help='adds name of directory to save songs',
                        nargs='+')
    return parser.parse_args()


def download_from_url(url, dst):
    """
    @param: 下载地址
    @param: 保存路径
    """
    file_info = urlopen(url).info()
    file_size = int(file_info.get('Content-Length', -1))
    os.path.exists(save_path)

    if os.path.exists(dst):
        first_byte = os.path.getsize(dst)
    else:
        first_byte = 0
    if first_byte >= file_size:
        return file_size
    header = {"Range": "bytes=%s-%s" % (first_byte, file_size)}
    pbar = tqdm(
        total=file_size, initial=first_byte,
        unit='B', unit_scale=True, desc=dst)
    req = requests.get(url, headers=header, stream=True)
    with(open(dst, 'ab')) as f:
        for chunk in req.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)
                pbar.update(1024)
    pbar.close()
    return file_size


def parse_playlist(playlist):
    """
    歌单解析
    :param playlist:
    :return:
    """
    data = json.loads(playlist)
    if not data['status']:
        return []

    # trackList would be `null` if no tracks
    track_list = data['data']['trackList']
    if not track_list:
        return []

    return map(create_song, track_list)


def get_response(url):
    """
    获取http请求的返回文本
    :param url: 请求地址
    :return:
    """
    return requests.get(url, headers=HEADERS).text


def get_songs(url):
    """
    根据url解析出歌曲信息
    :param url:
    :return:
    """
    return parse_playlist(get_response(url))


class Song(object):
    """
    歌曲类
    """
    def __init__(self):
        self.title = u'Unknown Song'
        self.song_id = 0
        self.track = 0
        self.album_id = 0
        self.album_tracks = 0
        self.album_name = u'Unknown Album'
        self.artist = u'Unknown Artist'
        self.location = None
        self.lyric_url = None
        self.pic_url = None

    @property
    def location(self):
        return self._location

    @location.setter
    def location(self, value):
        self._location = value
        self.url = decode_location(self._location)


def create_song(raw):
    """
    创建歌曲类
    :param raw:
    :return:
    """
    parser = html.parser
    song = Song()
    song.title = parser.unescape(raw['songName'])
    song.artist = parser.unescape(raw['artist'])
    song.album_name = parser.unescape(raw['album_name'])
    song.song_id = raw['song_id']
    song.album_id = raw['album_id']
    song.location = raw['location']
    song.lyric_url = raw['lyric_url']
    song.pic_url = raw['pic']
    return song


def decode_location(location):
    """
    :param location:
    :return:
    """
    if not location:
        return None
    url = location[1:]
    urllen = len(url)
    rows = int(location[0:1])

    cols_base = urllen / rows  # basic column count
    rows_ex = urllen % rows    # count of rows that have 1 more column

    matrix = []
    for r in range(rows):
        length = (int) (cols_base + 1 if r < rows_ex else cols_base)
        matrix.append(url[:length])
        url = url[length:]

    url = ''
    for i in range(urllen):
        url += matrix[(int)(i % rows)][(int)(i / rows)]

    return urllib.parse.unquote(url).replace('^', '0')


def get_entity_id(category, id_or_code):
    """
    :param id_or_code:
    :return:
    """
    try:
        return int(id_or_code)
    except Exception:
        code = id_or_code

    base_url = 'http://www.xiami.com/{}'.format(category)

    url = '{}/{}'.format(base_url, code)
    html = get_response(url)

    pattern = r'<link[^>]+href="{}/(\d+)"'.format(base_url)
    match = re.search(pattern, html)
    if not match:
        raise ValueError('ID not found for {}: {}'.format(category, id_or_code))

    return int(match.group(1))


def build_url_list(category, l):
    """
    生成歌曲的url地址列表
    :param category: 类别
    :param l: 用户命令行的参数值
    :return:
    """
    patterns = {
        'album': URL_PATTERN_ALBUM,
        'song': URL_PATTERN_SONG,
        'playlist': URL_PATTERN_PLAYLIST,
    }
    pattern = patterns[category]
    return [
        pattern % get_entity_id(category, item)
        for group in l
        for item in group
    ]


if __name__ == '__main__':
    import argparse
    args = parse_arguments()
    urls = []
    if args.song:
        urls.extend(build_url_list('song', args.song))
    if args.album:
        urls.extend(build_url_list('album', args.album))
    if args.playlist:
        urls.extend(build_url_list('playlist', args.playlist))
    songs = [
        song
        for playlist_url in urls
        for song in get_songs(playlist_url)
    ]
    save_path = args.to[0][0] if args.to else 'downloads'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    for i, song in enumerate(songs):
        download_from_url(song.url, save_path + '/' +song.title + '.mp3')
    print('================================下载完成===============================')