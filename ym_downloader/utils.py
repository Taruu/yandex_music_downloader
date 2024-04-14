import os
import music_tag
import time
from typing import Union

from loguru import logger
from yandex_music.exceptions import UnauthorizedError
from yandex_music.track.track import Track
from yandex_music.track_short import TrackShort
from yandex_music.album.album import Album
from yandex_music.playlist.playlist import Playlist
from urllib.parse import urlparse
from config.loader import client


def url_to_playlist(url_text: str) -> Playlist:
    path_url = urlparse(url_text)
    if path_url.netloc != 'music.yandex.ru':
        return None
    path = path_url.path.split('/')
    path.pop(0)
    print('path', path)

    if 'album' in path:
        album_id = int(path[-1])
        return client.albums_with_tracks(album_id)
    elif 'users' in path:
        album_id = int(path[-1])
        user = path[1]
        return client.users_playlists(album_id, user)
    else:
        ValueError("not correct url")


class AlbumDownloader:
    def __init__(self, playlist: Union[Playlist, Album], out_folder=None,
                 bit_rate=192,
                 codec='mp3'):
        self.bit_rate = bit_rate
        self.out_folder = out_folder

        if playlist.__class__ is Album:

            album = playlist.with_tracks()
            self.tracks = album.volumes[0]

            if self.out_folder is None:
                self.out_folder = album.id
        elif playlist.__class__ is Playlist:
            self.tracks = playlist.fetch_tracks()
            if self.out_folder is None:
                self.out_folder = playlist.playlist_id

        self.codec = codec

    def download_tracks(self):

        for track_short in self.tracks:
            self.download_track(track_short)

    def download_track(self, track: Union[TrackShort, Track]):
        path_file = f"{self.out_folder}/{track.track_id}.{self.codec}"

        if os.path.exists(path_file):
            logger.info(f"track already exists {track.track_id}")
            return
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
                self.write_metadata(path_file, track)

            except Exception as e:
                if e.__class__ is UnauthorizedError:
                    break
                logger.error(e)
                time.sleep(5)

    @staticmethod
    def write_metadata(path, track):
        cover_bytes = track.download_cover_bytes(size='200x200')
        music_file = music_tag.load_file(path)

        music_file.append_tag('artwork', cover_bytes)
        music_file.append_tag('title', track.title)

        for artist_data in track.artists:
            music_file.append_tag('artist', artist_data['name'])

        music_file.save()
