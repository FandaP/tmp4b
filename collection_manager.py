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

from collection import *
import os
from mutagen.flac import FLAC
import json


# 扫描所有音乐文件
def scan_music_library(library_root):  # [修改] root -> library_root

    collections = []

    # 将 ~/foo/bar 路径展开为完整路径
    library_root = os.path.expanduser(library_root)

    # 扫描整个音乐库目录
    with os.scandir(library_root) as album_dirs:  # [修改] entries -> album_dirs
        for album_dir in album_dirs:  # [修改] entry -> album_dir

            # 如果扫描到的不是目录，就跳过
            if not album_dir.is_dir():
                continue

            # [修改] info -> collection_data
            # 暂存当前目录中的专辑信息与曲目文件路径
            collection_data = {}
            track_paths = []  # [修改] music_files -> track_paths

            with os.scandir(album_dir.path) as directory_entries:  # [修改] files -> directory_entries
                for file_entry in directory_entries:  # [修改] file -> file_entry

                    if (
                        file_entry.is_file()
                        and file_entry.name.lower().endswith(".flac")
                    ):
                        # 如果读取到的是音乐文件
                        track_paths.append(file_entry.path)

                    elif (
                        file_entry.is_file()
                        and file_entry.name == "CollectionData.json"
                    ):
                        # 如果读取到的是专辑 JSON 文件
                        with open(
                            file_entry.path,
                            "r",
                            encoding="utf-8"
                        ) as collection_data_file:
                            collection_data = json.load(collection_data_file)

                    else:
                        continue

            # 如果没有音乐文件，就跳过当前目录
            if not track_paths:
                continue

            if collection_data:
                # 如果识别到了 JSON 文件，就使用其中的专辑信息

                # [修改] ctype -> collection_type
                # 同时将 JSON 中的类型值转换为 CollectionType 枚举
                collection = Collection(
                    title=collection_data["title"],
                    artist=collection_data["artist"],
                    publish_date=collection_data["release"]["date"],
                    track_count=collection_data["metadata"]["track_total"],
                    collection_id=collection_data["id"],
                    collection_type=(
                        CollectionType[collection_data["type"]]
                        if isinstance(collection_data["type"], str)
                        else CollectionType(collection_data["type"])
                    )
                )

            else:
                # 如果没有 JSON 文件，就读取任意 FLAC 文件中的专辑信息

                # [修改] album_audio -> first_audio_file
                first_audio_file = FLAC(track_paths[0])

                collection = Collection(
                    title=first_audio_file.get("album")[0],
                    artist=first_audio_file.get("albumartist")[0],
                    publish_date=first_audio_file.get("date")[0],
                    track_count=int(first_audio_file.get("tracktotal")[0])
                )

            # 遍历当前专辑目录中的曲目文件
            for track_path in track_paths:  # [修改] filepath -> track_path

                if not os.path.isfile(track_path):
                    continue

                # [修改] audio -> audio_file
                # 用于获取 FLAC 文件的元数据与信息
                audio_file = FLAC(track_path)

                # 创建 Music 实例
                music = Music(
                    title=audio_file.get("title")[0],
                    artist=audio_file.get("artist")[0],
                    publish_date=audio_file.get("date")[0],  # [修改] 统一为字符串
                    duration=audio_file.info.length,  # [修改] length -> duration
                    track=int(audio_file.get("tracknumber")[0]),
                    path=track_path
                )

                # 如果有专辑信息文件，就添加其中的故事与曲目 ID
                if collection_data:
                    # [修改] mid -> music_id
                    # 修复原代码末尾多余逗号导致赋值结果成为元组的问题
                    music.music_id = collection_data["tracks"][music.track - 1]["id"]

                    music.story = collection_data["booklet"]["story"][str(music.track)]

                # [修改] add_music -> add_track
                collection.add_track(music)

            # 按曲目编号排序
            # [修改] musics -> tracks
            collection.tracks = sorted(
                collection.tracks,
                key=lambda music: music.track
            )

            # 将当前专辑添加至专辑列表
            collections.append(collection)

    # 按发行年份排序
    collections = sorted(
        collections,
        key=lambda collection: collection.publish_date.split("-")[0]
    )

    return collections

if __name__ == "__main__":
    collections = scan_music_library("./Touhou")
    
    for collection in collections:
        print(f"{collection.title}, by {collection.artist}")
        for music in collection.tracks:
            print(f"  Track {music.track}: {music.title}")
            print("  ", music.path.split("/")[-1])
    
            
