#!/usr/bin/python3
# -*-coding:utf-8-*-

'''
TMP4B, a Touhou Music Player for those who can't use their screen.
Copyright (C) 2026 FandaP

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

from enum import Enum

class CollectionType(Enum):
    UNKNOWN = 0
    GAME = 1
    ALBUM = 2
    PUBLICATION = 3


class Music:
    def __init__(
        self,
        title,
        artist,
        publish_date,
        duration,
        track,
        path,
        music_id=None,
        story=None
    ):
        self.title: str = title
        self.artist: str = artist
        self.publish_date: str = publish_date

        self.duration: float = duration
        self.track: int = track
        self.path: str = path

        self.story: str = story
        self.music_id: str = music_id

    # （本类不需要额外的方法）


class Collection:
    def __init__(
        self,
        title,
        artist,
        publish_date,
        track_count,
        collection_id=None,
        collection_type=CollectionType.UNKNOWN
    ):
        self.title: str = title
        self.artist: str = artist
        self.publish_date: str = publish_date

        self.track_count: int = track_count
        self.collection_id: str = collection_id
        self.collection_type: CollectionType = collection_type

        self.tracks = []

    def add_track(self, *tracks):
        self.tracks.extend(tracks)
