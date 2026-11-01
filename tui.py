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

import sys
import tty
import termios
from math import ceil

import player

class TUI:
    """负责绘制终端界面和读取用户按键。

    TUI 不直接管理 VLC 播放器的内部状态，
    而是通过 self.player 调用 player.MusicPlayer 的方法。
    """

    def __init__(self, player):
        # 保存播放器对象，以便显示当前专辑和曲目信息。
        self.player = player

    def refresh(self, message):
        """清屏并重新绘制整个界面。

        参数：
            message：显示在界面底部的提示信息。
        """

        # CSI 2 J：清除可见屏幕。
        # CSI H：将光标移动到左上角。
        sys.stdout.write("\033[2J\033[H")

        # ---------- 标题区域 ----------
        sys.stdout.write("                  Touhou Music Player for the Blind (TMP4B)                     \r\n")
        sys.stdout.write("                                  by FandaP                                     \r\n")
        sys.stdout.write("=" * 80 + "\r\n")

        # ---------- 专辑信息 ----------
        sys.stdout.write(f"Collection: {self.player.current_collection.title}\r\n")
        sys.stdout.write("Music List:\r\n")

        # ---------- 曲目列表 ----------
        # 当前播放曲目前面显示 >，其余曲目前面显示空格。
        # 这里只负责显示，不会在循环中切换曲目。
        for track in self.player.current_collection.tracks:
            if self.player.current_track == track:
                sys.stdout.write(f"> {track.track}  {track.title}\r\n")
            else:
                sys.stdout.write(f"  {track.track}  {track.title}\r\n")

        # ------------进度条-------------
        if self.player.player.get_time() > 0:
            scale_current_duration = self.player.player.get_time() / self.player.player.get_length()
            sys.stdout.write("="*ceil(80 * scale_current_duration))
            if self.player.player.is_playing():
                sys.stdout.write("$")
            else:
                sys.stdout.write("|")
            sys.stdout.write("-" * (79 - ceil(80 * scale_current_duration)) + "\r\n")
        else:
            sys.stdout.write("-" * 80+"\r\n")

        # ---------- 当前曲目详情 ----------
        sys.stdout.write(f" Track: {self.player.current_track.track}\r\n")
        sys.stdout.write(f" Music: {self.player.current_track.title}\r\n")
        sys.stdout.write(f"Artist: {self.player.current_track.artist}\r\n")

        # ---------- 操作提示区域 ----------
        sys.stdout.write("=" * 80 + "\r\n")
        sys.stdout.write(message)

        # 确保缓冲区中的内容立即显示到终端。
        sys.stdout.flush()

    def refresh_progress(self):
        """只重绘进度条"""
        if self.player.player.get_length() <= 0 or self.player.player.get_time() < 0:
            progress = 0.0
        else:
            progress = self.player.player.get_time() / self.player.player.get_length()

        marker = "$" if self.player.player.is_playing() else "|"

        sys.stdout.write("\0337") # 保存光标位置
        sys.stdout.write("\033[5A") # 回到进度条所在行
        if progress >= 0.95:
            sys.stdout.write("\r" + "="*80 + "\r\n") # 绘制进度条
        else:
            sys.stdout.write("\r" + "="*ceil(80*progress) + marker + "-"*(79-ceil(80*progress)) + "\r\n") # 绘制进度条
        sys.stdout.write("\0338") # 返回到保存的光标位置
        sys.stdout.flush()
        

    def read_key(self):
        """读取一个按键，并在读取结束后恢复终端输入设置。

        tty.setraw() 会临时让终端进入原始输入模式，
        使单个字符可以立即被读取，而不必等待 Enter。
        """

        fd = sys.stdin.fileno()

        # 保存当前终端设置，避免程序改变终端状态后无法恢复。
        old_settings = termios.tcgetattr(fd)

        try:
            tty.setraw(fd)
            key = sys.stdin.read(1)
        finally:
            # 即使读取按键时发生异常，也尝试恢复原来的终端设置。
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return key

