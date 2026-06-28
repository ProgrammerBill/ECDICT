# ECDICT

基于开源项目 skywind3000/ECDICT，改造为一个**命令行英汉词典工具**：把词典数据导入本地 SQLite 数据库，然后用 `ecd` 命令查询单词。

特点：

- **零依赖**：只需要 Python 3，不需要 MySQL、不需要服务器、不需要密码。
- **查询快**：数据存入带索引的 SQLite 数据库，查询毫秒级。
- **智能匹配**：精确查询 →（找不到时）词形还原（running → run）→（仍找不到时）按前缀给出近似单词建议。

## 安装步骤

1. 确保安装了 Python 3：
   ```
   python3 --version
   ```
2. 运行安装脚本（构建数据库并把 `ecd` 加入 PATH）：
   ```
   ./setup.sh
   source ~/.bashrc
   ```
   首次构建约需 20 秒，会生成约 100MB 的 `dicts/ecdict.db`（已在 .gitignore 中，不入库）。

## 使用方法

```
ecd hello        # 精确查询
ecd running      # 自动还原为 run / 或返回 running 自身释义
ecd helo         # 拼写不确定时给出近似单词建议
```

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
