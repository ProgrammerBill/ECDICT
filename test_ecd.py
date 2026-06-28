#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# test_ecd.py - 用一个临时小型数据库验证 ecd 的三条查询路径
#   1. 精确查询  2. 词形还原回退  3. 近似建议
#
import os
import subprocess
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))


def build_fixture(db_path):
    """直接构建一个最小数据库，避免依赖完整 CSV。"""
    conn = sqlite3.connect(db_path)
    conn.executescript('''
    CREATE TABLE ecdict (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word VARCHAR(64) COLLATE NOCASE NOT NULL,
        sw VARCHAR(64) COLLATE NOCASE NOT NULL,
        phonetic TEXT, definition TEXT, translation TEXT, pos TEXT,
        collins INTEGER, oxford INTEGER, tag TEXT, bnc INTEGER, frq INTEGER,
        exchange TEXT, detail TEXT, audio TEXT
    );
    CREATE TABLE lemma (form TEXT PRIMARY KEY COLLATE NOCASE, base TEXT NOT NULL);
    CREATE UNIQUE INDEX idx_word ON ecdict (word COLLATE NOCASE);
    CREATE INDEX idx_sw ON ecdict (sw COLLATE NOCASE);
    ''')
    conn.execute("INSERT INTO ecdict (word, sw, phonetic, translation) "
                 "VALUES ('have', 'have', 'hæv', 'vt. 有')")
    conn.execute("INSERT INTO ecdict (word, sw, phonetic, translation) "
                 "VALUES ('hello', 'hello', 'hə''ləu', 'interj. 喂')")
    conn.execute("INSERT INTO lemma (form, base) VALUES ('had', 'have')")
    conn.commit()
    conn.close()


def run(db_path, word):
    r = subprocess.run([sys.executable, os.path.join(HERE, 'ecd'), word],
                       env={**os.environ, 'ECDICT_DB': db_path,
                            'ECDICT_NO_AUDIO': '1'},
                       capture_output=True, text=True)
    return r.stdout


def main():
    failures = []
    with tempfile.TemporaryDirectory() as d:
        db = os.path.join(d, 'fixture.db')
        build_fixture(db)

        out = run(db, 'hello')
        if 'interj. 喂' not in out:
            failures.append('精确查询失败: %r' % out)

        out = run(db, 'had')           # had 不是词条，应还原到 have
        if 'have' not in out or '原型' not in out:
            failures.append('词形还原失败: %r' % out)

        out = run(db, 'hel')           # 非词条，应给出 hello 建议
        if 'hello' not in out or '是否想查' not in out:
            failures.append('近似建议失败: %r' % out)

    if failures:
        for f in failures:
            print('FAIL:', f)
        return 1
    print('全部测试通过 (精确 / 词形还原 / 近似建议)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
