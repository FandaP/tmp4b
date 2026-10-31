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

import collection
from collection_manager import scan_music_library

from time import sleep
from math import ceil
import vlc
import sys
import tty
import termios
import threading
from random import randint

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

        # 新专辑的第一首曲目位于列表索引 0。
        self.current_track = self.current_collection.tracks[0]

        self.player = vlc.MediaPlayer(self.current_track.path)
        self.player.play()


class TUI:
    """负责绘制终端界面和读取用户按键。

    TUI 不直接管理 VLC 播放器的内部状态，
    而是通过 self.player 调用 MusicPlayer 的方法。
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
        sys.stdout.write("                  Touhou Music Player for the Blinds (TMP4B)                    \r\n")
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

def check_progress(tui):
    while True:
        sleep(0.2)
        tui.refresh_progress()
        

def main_loop(player,tui):
    global collections, collection_index, message
    # 主事件循环

    # 保存需要在界面底部显示的提示信息。
    message = ""

    # 保存“是否需要重绘界面”的变量。
    need_refresh = True
    
    # 每次循环先按需要重绘界面，再读取按键，最后执行相应操作。
    while True:
        if need_refresh:
            tui.refresh(message)
        need_refresh = True

        # 提示信息只显示一轮，随后清空。
        message = ""

        user_input = tui.read_key()

        # match/case 根据按键选择要执行的操作。
        match user_input:

            case " ":
                # 空格：暂停或恢复播放。
                player.pause()
                need_refresh = False

            case "s":
                # s：停止播放。
                player.stop()

            case "r":
                # r：从头播放当前曲目。
                player.restart()

            case "p":
                # p：播放上一首曲目。
                # 如果当前是第一首，change_track(0) 会产生索引错误；
                # 这里需要循环回专辑的最后一首。
                if player.current_track.track <= 1:
                    player.change_track(len(player.current_collection.tracks))
                else:
                    player.change_track(player.current_track.track - 1)

            case "n":
                # n：播放下一首曲目。
                # 如果已经是最后一首，就循环回第一首。
                if (player.current_track.track >= len(player.current_collection.tracks)):
                    player.change_track(1)
                else:
                    player.change_track(player.current_track.track + 1)                    

            case "b":
                # b：切换到音乐库列表中的上一张专辑。
                collection_index -= 1

                # 到达列表开头时，循环到最后一张专辑。
                if collection_index < 0:
                    collection_index = len(collections) - 1

                player.change_collection(collections[collection_index])

            case "f":
                # f：切换到下一张专辑。
                collection_index += 1

                # 到达列表末尾时，循环回第一张专辑。
                if collection_index >= len(collections):
                    collection_index = 0

                player.change_collection(collections[collection_index])

            case "t":
                # t：手动输入曲目编号。
                #
                # 这里需要临时使用普通的行输入，因此先恢复终端模式。
                # read_key() 返回时已经恢复了原来的终端设置。
                sys.stdout.write("\033[2K\rT ")
                sys.stdout.flush()

                user_input = sys.stdin.readline().rstrip("\n")

                try:
                    track_number = int(user_input)
                    # 检查曲目编号是否处于有效范围。
                    if (1 <= track_number <= len(player.current_collection.tracks)):                    
                        player.change_track(track_number)
                    else:
                        message = f"Please type an integer number between 1 and {len(player.current_collection.tracks)}!"
                except (ValueError,IndexError):
                    # 如果输入不能转换为整数或者超出范围
                    message = f"Please type an integer number between 1 and {len(player.current_collection.tracks)}!"

            case ":":
                # 冒号：类似于vim当中的，唤起“更丰富的指令”
                sys.stdout.write("\r\033[2K: ")
                sys.stdout.flush()
                user_input = sys.stdin.readline().rstrip("\n").split(" ")
                match user_input[0]:
                    case "pause":
                        # 暂停或恢复播放。
                        player.pause()
                        need_refresh = False
                    case "start":
                        player.start()
                    case "stop":
                        player.stop()
                    case "restart":
                        player.restart()
                    case "refresh":
                        need_refresh = True
                    case _:
                        need_refresh = False
                sys.stdout.write("\033[1A\r\033[2K")
            case _:
                need_refresh = False
                continue
                
if __name__ == "__main__":

    ############ 初始化音乐库 #############
    # 扫描指定目录，得到 Collection 对象列表。
    collections = scan_music_library("./Touhou")


    if not collections:
        exit(1)
    
    # 随机选择一张专辑作为启动时播放的专辑。
    collection_index = randint(0, len(collections) - 1)

    # 创建播放器，默认从选中专辑的第一首曲目开始。
    player = MusicPlayer(collections[collection_index])
    player.start()

    # 创建终端界面。
    tui = TUI(player)

    main_thread = threading.Thread(target=main_loop,args=(player,tui))
    check_thread = threading.Thread(target=check_progress,args=(tui,))

    main_thread.start()
    check_thread.start()
    
