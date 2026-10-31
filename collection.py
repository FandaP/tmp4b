#!/usr/bin/python3
# -*-coding:utf-8-*-

'''
TMP4B, a Touhou Music Player for those who can't use their screen.
Copyright (C) 2026

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

        self.duration: float = duration  # [修改] length -> duration
        self.track: int = track
        self.path: str = path

        self.story: str = story
        self.music_id: str = music_id  # [修改] mid -> music_id

    # [修改] 保留原有字段含义，将专辑中的曲目统一称为 tracks
    # 这样可以与 Collection.tracks 保持一致
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

        self.track_count: int = track_count  # [修改] track_total -> track_count
        self.collection_id: str = collection_id  # [修改] cid -> collection_id
        self.collection_type: CollectionType = collection_type  # [修改] ctype -> collection_type

        self.tracks = []  # [修改] musics -> tracks

    # [修改] add_music -> add_track，与 tracks 的命名保持一致
    def add_track(self, *tracks):
        self.tracks.extend(tracks)
