# music-dowloader
##下载虾米音乐到本地并上传至网易云音乐云盘，暂时只完成下载部分，上传还未完成
## 使用说明：
usage: download.py [-h] [-v] [-s SONG [SONG ...]] [-a ALBUM [ALBUM ...]]
                   [-p PLAYLIST [PLAYLIST ...]] [-t TO [TO ...]]

需要下载的专辑(album)ID, 歌单(playlist)ID, 歌曲(song)ID从虾米音乐的网页版获取.

optional arguments:

  -h, --help            show this help message and exit

  -v, --version         show program's version number and exit

  -s SONG [SONG ...], --song SONG [SONG ...]
                        adds songs for download

  -a ALBUM [ALBUM ...], --album ALBUM [ALBUM ...]
                        adds all songs in the albums for download

  -p PLAYLIST [PLAYLIST ...], --playlist PLAYLIST [PLAYLIST ...]
                        adds all songs in the playlists for download

  -t TO [TO ...], --to TO [TO ...]
                        adds the name of directory to save songs
## Example：
### 获取歌单ID
![res1](/img/a.png)
### 效果图
![res2](/img/b.png)
