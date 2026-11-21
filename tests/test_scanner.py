"""Tests for scanner.py — real FLAC fixtures, no stubs.

The fixture files are genuine FLAC streams (STREAMINFO + VORBIS_COMMENT, no audio
frames) because the scanner only ever reads tags, never decodes audio.
"""

import json
import os
import struct

import pytest

from mutagen.flac import FLAC

import scanner


# ------------------------------------------------------------------ fixtures

def _streaminfo(sample_rate=44100, total_samples=44100 * 100):
    bits = (sample_rate & 0xFFFFF) << 44
    bits |= (1 & 0x7) << 41          # channels - 1
    bits |= (15 & 0x1F) << 36        # bits per sample - 1
    bits |= total_samples & 0xFFFFFFFFF
    return (struct.pack(">HH", 4096, 4096) + b"\x00\x00\x00" + b"\x00\x00\x00"
            + bits.to_bytes(8, "big") + b"\x00" * 16)


def _vorbis_comment(tags, vendor="tmp4b-tests"):
    out = bytearray(struct.pack("<I", len(vendor)) + vendor.encode())
    out += struct.pack("<I", len(tags))
    for key, value in tags.items():
        item = f"{key}={value}".encode()
        out += struct.pack("<I", len(item)) + item
    return bytes(out)


def write_flac(path, tags=None, vendor="tmp4b-tests"):
    info = _streaminfo()
    comment = _vorbis_comment(tags or {}, vendor)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as fh:
        fh.write(b"fLaC")
        fh.write(bytes([0x00]) + len(info).to_bytes(3, "big") + info)
        fh.write(bytes([0x84]) + len(comment).to_bytes(3, "big") + comment)


COMMON = {"ARTIST": "ZUN", "ALBUM": "Test Album", "ALBUMARTIST": "ZUN",
          "DATE": "2002-08-11", "TRACKTOTAL": "2"}


def album_fixtures(root, names=("b.flac", "a.flac"), with_json=True, story=True):
    """Create one album. `names` controls which file holds which track.

    ("b.flac", "a.flac") -> directory order reverses track order (the bug's trigger)
    ("01 First.flac", "02 Second.flac") -> directory order matches track order
    """
    name1, name2 = names
    album = os.path.join(root, "Touhou", "Test Album")
    write_flac(os.path.join(album, name2), dict(COMMON, TITLE="Second", TRACKNUMBER="2"))
    write_flac(os.path.join(album, name1), dict(COMMON, TITLE="First", TRACKNUMBER="1"))

    if with_json:
        data = {
            "schema_version": 1, "id": "REPRO-0001", "title": "Test Album",
            "artist": "ZUN", "type": 2,
            "release": {"date": "2002-08-11", "event": "C62"},
            "metadata": {"disc_total": 1, "track_total": 2},
            "tracks": [{"id": "REPRO-0001-01", "track": 1, "file": name1},
                       {"id": "REPRO-0001-02", "track": 2, "file": name2}],
            "booklet": {"story": ({"1": "story of track 1", "2": "story of track 2"}
                                  if story else {})},
        }
        with open(os.path.join(album, "CollectionData.json"), "w", encoding="utf-8") as fh:
            json.dump(data, fh, ensure_ascii=False)
    return os.path.join(root, "Touhou")


# ------------------------------------------------------------------ tests

def test_template_json_is_valid():
    """A6: CollectionData.json 至少要是合法 JSON。"""
    template = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            "CollectionData.json")
    with open(template, encoding="utf-8") as fh:
        data = json.load(fh)
    assert {"id", "title", "release", "tracks"} <= data.keys()


def test_stories_follow_track_number_not_directory_order(tmp_path):
    """A1/A2: 文件名顺序与音轨顺序相反时，booklet 文本仍挂在正确曲目上。"""
    root = album_fixtures(str(tmp_path), names=("b.flac", "a.flac"))
    collection = scanner.scan_music_library(root)[0]

    mapping = {music.track: story for music, story in collection.stories.items()
               if hasattr(music, "track")}
    assert mapping == {1: "story of track 1", 2: "story of track 2"}


def test_stories_correct_when_directory_order_matches(tmp_path):
    """对照组：文件名顺序正好等于音轨顺序。"""
    root = album_fixtures(str(tmp_path), names=("01 First.flac", "02 Second.flac"))
    collection = scanner.scan_music_library(root)[0]

    mapping = {music.track: story for music, story in collection.stories.items()
               if hasattr(music, "track")}
    assert mapping == {1: "story of track 1", 2: "story of track 2"}


def test_music_ids_follow_track_number(tmp_path):
    """A2: 曲目 ID 按编号匹配，不依赖列表位置。"""
    root = album_fixtures(str(tmp_path))
    collection = scanner.scan_music_library(root)[0]

    assert [(m.track, m.music_id) for m in collection.tracks] == [
        (1, "REPRO-0001-01"), (2, "REPRO-0001-02")
    ]


def test_untagged_flac_does_not_abort_scan(tmp_path):
    """A3: 缺标签的文件用占位值，整库扫描不中断。"""
    album = os.path.join(str(tmp_path), "Touhou", "No Tags")
    write_flac(os.path.join(album, "01 untagged.flac"))          # 无任何标签
    root = album_fixtures(str(tmp_path), with_json=False)        # 同一库里再来一张正常专辑

    collections = scanner.scan_music_library(root)

    assert len(collections) == 2                       # 两张专辑都在
    titles = {c.title for c in collections}
    assert "Test Album" in titles
    untagged = next(c for c in collections if c.title == "No Tags")
    assert untagged.tracks[0].artist == "Unknown Artist"
    assert untagged.tracks[0].title == "01 untagged"


def test_combined_tracknumber_is_parsed(tmp_path):
    """A3: "1/12" 这种 Vorbis 写法解析为 1。"""
    album = os.path.join(str(tmp_path), "Touhou", "Combined")
    write_flac(os.path.join(album, "x.flac"),
               {"TITLE": "First", "ARTIST": "ZUN", "ALBUM": "Combined",
                "DATE": "2003-01-01", "TRACKNUMBER": "1/12", "TRACKTOTAL": "12"})

    collection = scanner.scan_music_library(os.path.join(str(tmp_path), "Touhou"))[0]

    assert collection.tracks[0].track == 1


def test_broken_collection_json_falls_back_to_tags(tmp_path):
    """A5: 坏 JSON 只影响该专辑，改用标签，不炸整库。"""
    root = album_fixtures(str(tmp_path))
    album = os.path.join(root, "Test Album")
    with open(os.path.join(album, "CollectionData.json"), "w", encoding="utf-8") as fh:
        fh.write('{"title": "", "event": "",}')                  # 尾逗号：非法 JSON

    collections = scanner.scan_music_library(root)

    assert len(collections) == 1
    assert collections[0].title == "Test Album"                  # 来自 FLAC 的 album 标签
    assert collections[0].tracks[0].artist == "ZUN"


def test_missing_library_root_returns_empty(tmp_path):
    """A7: 音乐库目录不存在时返回空列表，不抛异常。"""
    assert scanner.scan_music_library(str(tmp_path / "nope")) == []
