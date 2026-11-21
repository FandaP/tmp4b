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

from collection import *
import os
import sys
import json
from mutagen.flac import FLAC


def _tag(audio_file, key, default=None):
    """读取一个 FLAC 标签；标签缺失或为空时返回 default。"""
    values = audio_file.get(key)
    if not values:
        return default
    return values[0] if values[0] not in (None, "") else default


def _parse_int(value, default=0):
    """把 "1" 或 Vorbis 约定的 "1/12" 解析为整数。"""
    if value is None:
        return default
    try:
        return int(str(value).split("/")[0])
    except (TypeError, ValueError):
        return default


def _load_collection_data(path):
    """读取专辑 JSON；文件损坏时只影响该专辑，不中断整个扫描。"""
    try:
        with open(path, "r", encoding="utf-8") as collection_data_file:
            return json.load(collection_data_file)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"warning: cannot read {path}: {exc}", file=sys.stderr)
        return {}


# 扫描所有音乐文件
def scan_music_library(library_root):

    collections = []

    # 将 ~/foo/bar 路径展开为完整路径
    library_root = os.path.expanduser(library_root)

    # 音乐库不存在时返回空列表，由调用方决定如何提示
    if not os.path.isdir(library_root):
        print(f"warning: music library {library_root} not found", file=sys.stderr)
        return collections

    # 扫描整个音乐库目录
    with os.scandir(library_root) as album_dirs:
        for album_dir in album_dirs:

            if not album_dir.is_dir():
                continue

            collection_data = {}
            track_paths = []

            with os.scandir(album_dir.path) as directory_entries:
                for file_entry in directory_entries:

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
                        collection_data = _load_collection_data(file_entry.path)

                    else:
                        continue

            # 如果没有音乐文件，就跳过当前目录
            if not track_paths:
                continue

            if collection_data:
                # 如果识别到了 JSON 文件，就使用其中的专辑信息
                # 同时将 JSON 中的类型值转换为 CollectionType 枚举

                collection = Collection(
                    title=collection_data.get("title") or album_dir.name,
                    artist=collection_data.get("artist") or "Unknown Artist",
                    publish_date=(
                        collection_data.get("release", {}).get("date")
                        or "0000-00-00"
                    ),
                    track_count=(
                        collection_data.get("metadata", {}).get("track_total")
                        or len(track_paths)
                    ),
                    collection_id=collection_data.get("id"),
                    collection_type=(
                        CollectionType[collection_data["type"]]
                        if isinstance(collection_data.get("type"), str)
                        and collection_data["type"] in CollectionType.__members__
                        else CollectionType(collection_data.get("type", 0))
                        if isinstance(collection_data.get("type"), int)
                        else CollectionType.UNKNOWN
                    )
                )

            else:
                # 如果没有 JSON 文件，就读取任意 FLAC 文件中的专辑信息
                try:
                    first_audio_file = FLAC(track_paths[0])
                except Exception as exc:
                    print(
                        f"warning: skipping album {album_dir.path}: {exc}",
                        file=sys.stderr
                    )
                    continue

                collection = Collection(
                    title=_tag(first_audio_file, "album", album_dir.name),
                    artist=_tag(first_audio_file, "albumartist", "Unknown Artist"),
                    publish_date=_tag(first_audio_file, "date", "0000-00-00"),
                    track_count=_parse_int(
                        _tag(first_audio_file, "tracktotal"), len(track_paths)
                    )
                )

            # 遍历当前专辑目录中的曲目文件
            for track_path in track_paths:

                if not os.path.isfile(track_path):
                    continue

                # 用于获取 FLAC 文件的元数据与信息
                # 单个文件损坏或标签异常时跳过，不影响同一专辑的其它曲目
                try:
                    audio_file = FLAC(track_path)
                except Exception as exc:
                    print(
                        f"warning: skipping unreadable file {track_path}: {exc}",
                        file=sys.stderr
                    )
                    continue

                # 创建 Music 实例
                music = Music(
                    title=_tag(
                        audio_file,
                        "title",
                        os.path.splitext(os.path.basename(track_path))[0]
                    ),
                    artist=_tag(audio_file, "artist", "Unknown Artist"),
                    publish_date=_tag(audio_file, "date", "0000-00-00"),
                    duration=audio_file.info.length,
                    track=_parse_int(_tag(audio_file, "tracknumber"), 0),
                    path=track_path
                )

                # 如果有专辑信息文件，就添加其中的曲目 ID
                if collection_data:
                    entries = collection_data.get("tracks") or []
                    if 1 <= music.track <= len(entries):
                        music.music_id = entries[music.track - 1].get("id")

                collection.add_track(music)

            # 按曲目编号排序
            collection.tracks = sorted(
                collection.tracks,
                key=lambda music: music.track
            )

            # 如果有专辑信息文件，就添加完整的故事
            if collection_data:
                for track, story in collection_data["booklet"]["story"].items():
                    try:
                        if int(track) == 0:
                            raise ValueError
                        collection.add_story(collection.tracks[int(track)-1], story)
                    except (ValueError, TypeError):
                        collection.add_story(track, story)
                    finally:
                        pass

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
        print(f"{collection.title}, by {collection.artist}\n")
        for track, story in collection.stories.items():
            print("\n")
            if type(track) == Music:
                print(f"Track {track.track}  {track.title}\n\n{story}")
            else:
                print(f"{track}\n\n{story}")
