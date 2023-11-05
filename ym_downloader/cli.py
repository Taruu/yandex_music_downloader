import argparse
import asyncio
import os.path
import sys
from utils import url_to_playlist, AlbumDownloader
from yandex_music import Client

from config.loader import settings
from signal import SIGINT, SIGTERM

from loguru import logger

parser = argparse.ArgumentParser(
    prog='Yandex music album downloader',
    description='Download music from yandex music',
    epilog='Text at the bottom of help')

parser.add_argument('urls', metavar='url1 url2 url3',
                    type=str, nargs='+',
                    help='yandex music album id')

parser.add_argument('-out-path', '-o', metavar='path/to/out', type=str,
                    default=None,
                    nargs='?',
                    help='target folder to download all music tracks')

parser.add_argument('-work-dir', '-wd', default=None, help='work dir')

parser.add_argument('-cs', '-cover-size', metavar='cover size for tracks',
                    type=str,
                    default='256x256',
                    nargs='?',
                    help='target folder to download music')

parser.add_argument('-file_extension', '-ext', metavar='folder for tracks',
                    type=str,
                    choices=['mp3', 'acc'],
                    default='mp3',
                    nargs='?',
                    help='target folder to download music')

parser.add_argument('-files_bitrate', '-bit', metavar='folder for tracks',
                    type=int,
                    choices=[192, 320, 128],
                    default=192,
                    nargs='?',
                    help='tracks bitrate')


def run():
    args = parser.parse_args()
    logger.info(args)

    playlists = [url_to_playlist(url) for url in args.urls]

    for playlist in playlists:
        AlbumDownloader(playlist,
                        os.path.abspath(args.out_path)).download_tracks()


sys.exit(run())
