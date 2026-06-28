#!/bin/bash
#########################################################################
# setup.sh - 构建 SQLite 词典数据库并把 ecd 命令安装为全局命令
#
# 不再依赖 MySQL / Python2，只需要 Python 3。
# 安装后任何终端（重启后依然有效）都可以直接使用 ecd。
#########################################################################
set -e

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET="$HERE/ecd"

# 1. 检查 Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "未检测到 python3，请先安装 Python 3。"
    exit 1
fi

# 2. 构建数据库 (dicts/ecdict.csv -> dicts/ecdict.db)
echo "==> 构建词典数据库 ..."
python3 "$HERE/build_db.py"

# 3. 安装 ecd 命令，让它在所有终端、重启后都可用
install_ecd() {
    # 优先：系统级软链接到 /usr/local/bin（所有用户、所有 shell 可用）
    if command -v sudo >/dev/null 2>&1; then
        if sudo ln -sf "$TARGET" /usr/local/bin/ecd 2>/dev/null; then
            echo "==> 已安装为系统命令: /usr/local/bin/ecd"
            return 0
        fi
    elif [ -w /usr/local/bin ]; then
        ln -sf "$TARGET" /usr/local/bin/ecd
        echo "==> 已安装为系统命令: /usr/local/bin/ecd"
        return 0
    fi

    # 其次：用户级软链接到 ~/.local/bin（无需 sudo）
    mkdir -p "$HOME/.local/bin"
    ln -sf "$TARGET" "$HOME/.local/bin/ecd"
    echo "==> 已安装到 ~/.local/bin/ecd"
    if ! echo ":$PATH:" | grep -q ":$HOME/.local/bin:"; then
        # ~/.local/bin 不在 PATH，写入 ~/.profile 与 ~/.bashrc 保证登录后生效
        local line='export PATH="$HOME/.local/bin:$PATH"'
        for rc in "$HOME/.profile" "$HOME/.bashrc"; do
            grep -qF "$line" "$rc" 2>/dev/null || echo "$line" >> "$rc"
        done
        echo "    已把 ~/.local/bin 加入 PATH（重新登录后生效）"
    fi
    return 0
}

install_ecd

echo
echo "setup.sh 完成! 现在即可使用 (新终端中):"
echo "    ecd hello"
