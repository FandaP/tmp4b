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

import collection
from scanner import *
import player
import tui
import sys

from time import sleep
import threading
from random import randint


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
    player = player.MusicPlayer(collections[collection_index])
    player.start()

    # 创建终端界面。
    tui = tui.TUI(player)

    main_thread = threading.Thread(target=main_loop,args=(player,tui))
    check_thread = threading.Thread(target=check_progress,args=(tui,))

    main_thread.start()
    check_thread.start()
    
