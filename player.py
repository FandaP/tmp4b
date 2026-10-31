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

import vlc
import collection

class MusicPlayer:
    """管理当前播放的专辑、曲目，以及 VLC 播放器实例。"""

    def __init__(self, collection, track_number=1):
        # 当前正在播放的专辑。
        self.current_collection: collection.Collection = collection

        # track_number 从 1 开始计数，而 Python 列表索引从 0 开始。因此需要减 1 才能访问对应的曲目。
        self.current_track: collection.Music = (
            self.current_collection.tracks[track_number - 1]
        )

        # 创建 VLC 播放器实例，并将其关联到当前曲目的文件路径。
        self.player = vlc.MediaPlayer(self.current_track.path)

    def start(self):
        """开始播放当前曲目。"""
        self.player.play()

    def pause(self):
        """暂停播放，或恢复播放（具体行为由 VLC 的 pause 接口决定）。"""
        self.player.pause()

    def stop(self):
        """停止播放当前曲目。"""
        self.player.stop()

    def restart(self):
        """从头播放当前曲目。"""
        self.player.stop()
        self.player.play()

    def change_track(self, track_number):
        """切换到当前专辑中的指定曲目，并立即开始播放。

        param:
            track_number: 从 1 开始的曲目编号。
        """
        # 先停止旧曲目，再更新当前曲目和播放器实例。
        self.player.stop()

        self.current_track = (
            self.current_collection.tracks[track_number - 1]
        )

        self.player = vlc.MediaPlayer(self.current_track.path)
        self.player.play()

    def change_track_obj(self, track):
        """直接通过 Music 对象切换曲目，而不是通过曲目编号切换。"""
        self.player.stop()
        self.current_track = track

        self.player = vlc.MediaPlayer(self.current_track.path)
        self.player.play()

    def change_collection(self, collection):
        """切换专辑，并播放新专辑的第一首曲目。"""
        self.player.stop()

        self.current_collection = collection

        # 新专辑的第一首曲目位于列表索引 0
        self.current_track = self.current_collection.tracks[0]

        self.player = vlc.MediaPlayer(self.current_track.path)
        self.player.play()

