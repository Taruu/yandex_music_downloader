import os
import time
from typing import Union

import yandex_music
from loguru import logger
from yandex_music.exceptions import UnauthorizedError
from yandex_music.track.track import Track
from yandex_music.track_short import TrackShort
from yandex_music.album.album import Album
from yandex_music.playlist.playlist import Playlist
from urllib.parse import urlparse
from config.loader import client


def url_to_playlist(url_text: str) -> Playlist:
    link = urlparse(url_text)

    if link.netloc != 'music.yandex.ru':
        return None
    path = link.path.split('/')
    path.pop(0)

    print(path)
    if 'album' in path:
        album_id = int(path[-1])
        return client.albums_with_tracks(album_id)
    elif 'users' in path:
        album_id = int(path[-1])
        user = path[1]
        print(path)
        print(album_id, user)
        return client.users_playlists(album_id, user)
    else:
        ValueError("not correct url")


class AlbumDownloader:
    def __init__(self, playlist: Union[Playlist, Album], out_folder=None,
                 bit_rate=192,
                 codec='mp3'):
        self.bit_rate = bit_rate
        self.out_folder = out_folder

        print(type(playlist))
        if playlist.__class__ is Album:

            album = playlist.with_tracks()
            self.tracks = album.volumes[0]

            if self.out_folder is None:
                self.out_folder = album.id
        else:
            self.tracks = playlist.fetch_tracks()
            if self.out_folder is None:
                self.out_folder = playlist.playlist_id
        self.cwd = os.getcwd()
        self.codec = codec

    def download_tracks(self):
        print(self.out_folder)
        folder_path = f"{self.cwd}/{self.out_folder}/"
        if not os.path.exists(folder_path):
            os.mkdir(folder_path)
        for track_short in self.tracks:
            self.download_track(track_short)
            pass

    def download_track(self, track: Union[TrackShort, Track]):
        path_file = f"{self.cwd}/{self.out_folder}/{track.track_id}.{self.codec}"
        print('type ', type(track))
        logger.info(f"download track {track.track_id}")
        while not os.path.isfile(path_file):
            while track.__class__ is TrackShort:
                try:
                    track = track.fetch_track()
                except Exception as e:
                    logger.error(type(e))
                    time.sleep(5)
            try:
                track.download(path_file, self.codec, self.bit_rate)
            except Exception as e:
                if e.__class__ is UnauthorizedError:
                    break
                logger.error(e)
                time.sleep(5)

        pass

    def write_metadata(self):
        pass
