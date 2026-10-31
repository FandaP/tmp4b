<h1 align="center">TMP4B</h1>

<div align="center">
  
Touhou Music Player for the Blind (or those who can't use their displays).
  
[![Author](https://img.shields.io/badge/FandaP-blue)](https://github.com/FandaP)[![Cirno](https://img.shields.io/badge/love_Cirno-forever!-blue)](https://github.com/FandaP) 

</div>

## Introduction 介绍

TMP4B is a simple music player for Touhou Project music collections, allowing users to access most of its features without a mouse. This makes it ideal for playing Touhou music in situations where using a mouse is difficult, or even when no display is available.

TMP4B 是一个简单的东方 Project 音乐专辑播放器，无需使用鼠标便能完成大部分操作。因此，它很适合在难以使用鼠标，甚至没有显示器的情况下播放东方原曲。

TMP4B is written in Python 3.10+. However, given its functionality and complexity, it would be more suitable to be implemented in C++. Rewriting TMP4B C++ is planned for the future.

TMP4B 使用 Python 3.10+ 编写。但是就其功能和复杂度而言，它更适合用 C++ 编写。未来计划中包含使用 C++ 重写 TMP4B。

## Features 功能特性

- **TTY-oriented**: Designed for GNU/Linux TTY environments, without relying on a graphical desktop.  
  **面向 TTY 环境**：专为 GNU/Linux TTY 终端设计，不依赖图形桌面环境。

- **Keyboard-driven**: Most features can be accessed entirely through the keyboard, without requiring a mouse.  
  **键盘驱动操作**：大部分功能均可通过键盘完成，无需使用鼠标。

- **Metadata-based** library scanning: Uses `mutagen` to read audio metadata instead of relying on filenames or directory naming conventions.  
  **基于元数据的音乐库扫描**：使用 `mutagen` 读取音频元数据，而非依赖文件名或目录命名规则。

- **Touhou music collection management**: Organizes music into collections, making it easier to browse and play Touhou music.  
  **东方音乐专辑管理**：将音乐组织为不同的专辑集合，方便浏览和播放东方音乐。

- **VLC-powered playback**: Uses VLC for audio playback through `python-vlc`.  
  **基于 VLC 的音频播放**：通过 `python-vlc` 调用 VLC 实现音频播放。

## Usage 使用方法

### 0. Clone the repository 克隆仓库

Clone TMP4B to your local machine:

将 TMP4B 仓库克隆到本地：

```bash
git clone https://github.com/FandaP/tmp4b.git
cd path/to/tmp4b
```

### 1. Preparing your music library 准备音乐库

Place your Touhou music files in your `~/Music/Touhou`. TMP4B scans audio files and reads their metadata to organize your music collections.

将东方音乐文件放入 `~/Music/Touhou` 目录。TMP4B 会扫描音频文件，并读取其元数据以组织音乐专辑。

### 2. Launching TMP4B 启动播放器

After installing all dependencies, run TMP4B from your terminal:

在安装好所有的依赖项后，在终端中运行 TMP4B：

```bash
# If you installed dependencies in a virtual environment
# 如果你使用虚拟环境安装了依赖
source .venv/bin/activate

# Launch TMP4B
# 启动 TMP4B
python path/to/tmp4b/front.py
```

Then you will enter a TUI (Terminal User Interface) , like:

然后，你就会进入一个 TUI （终端用户界面），就像这样：

```
                  Touhou Music Player for the Blind (TMP4B)                     
                                  by FandaP                                     
================================================================================
Collection: 蓬莱人形 ～ Dolls in Pseudo Paradise
Music List:
> 1  蓬莱伝説
  2  二色蓮花蝶～Red And White
  3  桜花之恋塚～Japanese Flower
  4  明治十七年の上海アリス
  5  東方怪奇談
  6  エニグマティクドール
  7  サーカスレヴァリエ
  8  人形の森
  9  Witch of Love Potion
  10  リーインカーネイション
  11  U.N.オーエンは彼女なのか？
  12  永遠の巫女
  13  空飛ぶ巫女の不思議な毎日
=============$------------------------------------------------------------------ 
 Track: 1
 Music: 蓬莱伝説
Artist: ZUN
================================================================================


```

The interface consists of three main sections:

界面主要由三个部分组成：

- **Music List**: Displays all tracks in the current collection.  
  **曲目列表**：显示当前专辑中的所有曲目
- **Progress Bar**: Displays the current playback progress. `|` indicates paused playback, while `$` indicates active playback.  
  **进度条**：显示当前播放进度。`|`表示暂停，`$`表示正在播放。
- **Track Information**: Displays information about the currently selected track.  
  **曲目信息**：显示当前曲目的相关信息


### 3. Keyboard Controls 键盘操作

TMP4B is designed to be operated entirely through the keyboard.

TMP4B 的设计目标是完全通过键盘进行操作。

| Key   | Function                                         |
|-------|--------------------------------------------------|
| `:`   | Enter command mode 进入命令模式                  |
| Enter | Execute the current command 执行当前命令         |
| Space | Toggle playback 切换播放/暂停                    |
| `p`   | Play the previous track 播放上一曲               |
| `n`   | Play the next track 播放下一曲                   |
| `b`   | Switch to the previous collection 切换至上一专辑 |
| `f`   | Switch to the next collection 切换至下一专辑     |
| `r`   | Restart the current music 重新播放当前曲目       |


## Platform 平台支持

TMP4B is designed specifically for the TTY environment of GNU/Linux. Compatibility with other platforms, especially Windows, is not guaranteed, as the project was never intended to support them. If you wish to use TMP4B on Windows, you may try running it through WSL (Windows Subsystem for Linux). Otherwise, please consider using another music player.

TMP4B 专为 GNU/Linux 的 TTY 环境设计，不保证在其他平台上正常运行，尤其是 Windows，因为本项目从一开始就没有考虑对 Windows 的支持。如果你希望在 Windows 上使用 TMP4B，可以尝试通过 WSL（Windows Subsystem for Linux）运行。否则，请考虑使用其他音乐播放器。

## Requirements 依赖

TMP4B is written in Python 3.10+. It uses mutagen to scan audio files and vlc for audio playback. Please make sure all libraries are installed on your system. If not, use following command to install:

TMP4B 使用 Python 3.10+ 编写，同时它使用 mutagen 库扫描音频文件，并使用 vlc 库进行音频播放。请确保你的系统中已经安装了这些库。如果你没有这些库，请使用以下命令安装：

### Debian / Ubuntu
```bash
sudo apt install python3 python3-mutagen python3-vlc vlc
```

### Fedora
```bash
sudo dnf install python3 python3-mutagen python3-vlc vlc
```

### ArchLinux
```bash
sudo pacman -Syu
sudo pacman -S --needed python python-mutagen vlc python-pip

cd /path/to/tmp4b/
python -m venv .venv
source .venv/bin/activate

python -m pip install python-vlc
```

## Project Structure 项目结构

```
TMP4B/
├── front.py             # UI & Music player                 # 用户界面与播放器
├── collection_manager.py
├── collection.py        # class Collection & class Track    # Collection 类和 Track 类的定义
├── CollectionData.json  # Collection data pattern           # 专辑数据模板
├── LICENSE
└── README.md
```

## License 许可证

TMP4B is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

TMP4B 是自由软件：您可以依据自由软件基金会发布的 GNU 通用公共许可证的条款（第三版或您选择的任何更新版本）重新发布和/或修改本软件。

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

本软件的发布是希望它能够发挥作用，但不提供任何担保；甚至不提供关于适销性或特定用途适用性的默示担保。详情请参阅 GNU 通用公共许可证。

