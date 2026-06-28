# ECDICT

基于开源项目 skywind3000/ECDICT，改造为一个**命令行英汉词典工具**：把词典数据导入本地 SQLite 数据库，然后用 `ecd` 命令查询单词。

特点：

- **零依赖**：只需要 Python 3，不需要 MySQL、不需要服务器、不需要密码。
- **查询快**：数据存入带索引的 SQLite 数据库，查询毫秒级。
- **智能匹配**：精确查询 → 词形还原（'ve → have）→ 拼写纠错与前缀补全（recieve → receive，seperate → separate）。基于 Damerau-Levenshtein 编辑距离，能识别相邻字母换位等常见笔误，并按编辑距离与词频排序。
- **彩色输出**：单词、音标、标签、Collins/Oxford 星级分色显示（管道输出或设置 `NO_COLOR` 时自动关闭）。
- **真人发音**：查到单词后自动朗读（有道在线发音，默认美音，可切英音）。需要本地有 `ffplay`/`mpv`/`mpg123` 任一播放器。
- **开机即用**：安装为系统命令后，任何终端、重启后都能直接使用 `ecd`。

## 安装步骤

1. 确保安装了 Python 3：
   ```
   python3 --version
   ```
2. 运行安装脚本（构建数据库并把 `ecd` 安装为全局命令）：
   ```
   ./setup.sh
   ```
   脚本会：① 构建数据库（约 20 秒，生成约 100MB 的 `dicts/ecdict.db`，已在 .gitignore 中不入库）；② 把 `ecd` 软链接到 `/usr/local/bin`（需要 sudo；无法 sudo 时回退到 `~/.local/bin`）。安装后**所有终端、重启后**都能直接使用 `ecd`，打开新终端即可生效。

## 使用方法

```
ecd hello        # 精确查询，并自动朗读发音（美音）
ecd running      # 自动还原为 run / 或返回 running 自身释义
ecd helo         # 拼写不确定时给出近似单词建议
ecd --uk hello   # 用英式发音
ecd -n hello     # 本次不发声
```

发音相关选项：

| 选项 / 环境变量 | 作用 |
| --- | --- |
| `-n` / `--no-audio` | 本次查询不发声 |
| `--uk` / `--us` | 临时切换英式 / 美式发音 |
| `ECDICT_NO_AUDIO=1` | 默认关闭发音 |
| `ECDICT_ACCENT=uk` | 默认使用英式发音 |

> 发音需要本地安装 `ffplay`（ffmpeg 自带）、`mpv` 或 `mpg123` 之一，并能联网访问有道发音接口。管道/脚本（非交互终端）下不会发声。

![示例图片](example.png)

## 工作原理

| 文件 | 作用 |
| --- | --- |
| `build_db.py` | 把 `dicts/ecdict.csv` 与 `lemma.en.txt` 构建为 `dicts/ecdict.db`（SQLite） |
| `ecd` | 命令行查询入口（Python 3），按 精确 → 词形还原 → 近似建议 的顺序匹配 |
| `setup.sh` | 一键构建数据库并把命令加入 PATH |

如需重建数据库（例如更新了 CSV）：

```
python3 build_db.py
```

可用环境变量 `ECDICT_DB` 指定数据库路径。

具体词典介绍可参考原介绍 [ECDICT](README-ORIGINAL.md)。
