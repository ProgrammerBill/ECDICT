#!/bin/bash
#########################################################################
# setup.sh - 构建 SQLite 词典数据库并把 ecd 命令加入 PATH
#
# 不再依赖 MySQL / Python2，只需要 Python 3。
#########################################################################
set -e

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. 检查 Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "未检测到 python3，请先安装 Python 3。"
    exit 1
fi

# 2. 构建数据库 (dicts/ecdict.csv -> dicts/ecdict.db)
echo "==> 构建词典数据库 ..."
python3 "$HERE/build_db.py"

# 3. 把仓库目录加入 PATH，使 ecd 命令可全局使用
if ! grep -qF "export PATH=\"$HERE:\$PATH\"" ~/.bashrc 2>/dev/null; then
    echo "export PATH=\"$HERE:\$PATH\"" >> ~/.bashrc
    echo "==> 已把 $HERE 加入 ~/.bashrc 的 PATH"
fi

echo "setup.sh 完成! 请打开新终端或运行: source ~/.bashrc"
echo "然后即可使用: ecd hello"
