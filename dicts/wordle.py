#!/usr/bin/env python3
"""交互式单词搜索工具"""

import sqlite3
import re
import sys

DB_PATH = '/home/aw/Public/ECDICT/ecdict.db'

def get_input(prompt, default='', validator=None):
    """获取用户输入，支持默认值和验证"""
    while True:
        value = input(f"{prompt}" + (f" [{default}]" if default else "") + ": ").strip()
        if not value and default:
            value = default
        if validator is None or validator(value):
            return value
        print("  输入无效，请重试")

def main():
    print("=" * 50)
    print("  单词搜索工具 (Wordle 助手)")
    print("=" * 50)
    print()

    # 获取搜索参数
    print("【基本设置】")
    length = get_input("单词长度", "7", lambda x: x.isdigit() and 1 <= int(x) <= 20)
    length = int(length)

    print("\n【模式匹配】")
    print("  使用 . 表示任意字母，如 .o.c..t 表示 _o_c__t")
    pattern_str = get_input("匹配模式 (如 .o.c..t)", "")
    pattern = None
    if pattern_str:
        try:
            pattern = re.compile('^' + pattern_str + '$', re.IGNORECASE)
        except re.error as e:
            print(f"  正则表达式错误: {e}")
            return

    print("\n【字母约束】")
    required = get_input("必须包含的字母 (如 poecnt)", "")
    required = set(required.lower()) if required else set()

    excluded = get_input("排除的字母 (如 aiusdfghklqwrzxvb)", "")
    excluded = set(excluded.lower()) if excluded else set()

    # 开始搜索
    print("\n" + "=" * 50)
    print(f"搜索: 长度={length}, 模式={pattern_str or '无'}, 必须={required or '无'}, 排除={excluded or '无'}")
    print("=" * 50)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT word FROM ecdict WHERE LENGTH(word) = ?", (length,))

    results = []
    for (word,) in cursor.fetchall():
        w = word.strip().lower()
        w_clean = re.sub(r'[^a-z]', '', w)

        if len(w_clean) != length:
            continue
        if pattern and not pattern.match(w_clean):
            continue
        if required and not required.issubset(set(w_clean)):
            continue
        if excluded and set(w_clean) & excluded:
            continue

        results.append(w_clean)

    conn.close()

    # 输出结果
    print(f"\n找到 {len(results)} 个结果:\n")
    for i, w in enumerate(results, 1):
        print(f"  {i:3}. {w}")

    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已退出")
        sys.exit(0)