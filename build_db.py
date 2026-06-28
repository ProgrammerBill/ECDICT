#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# build_db.py - 将 ecdict.csv 与 lemma.en.txt 构建为 SQLite 数据库
#
# 用法:
#   python3 build_db.py                       # 用默认路径构建
#   python3 build_db.py <csv> <lemma> <db>    # 指定路径
#

import csv
import os
import sqlite3
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

# CSV 中的列顺序（与表头一致）
COLUMNS = ('word', 'phonetic', 'definition', 'translation', 'pos',
           'collins', 'oxford', 'tag', 'bnc', 'frq', 'exchange',
           'detail', 'audio')


def stripword(word):
    """只保留字母数字并转小写，用于模糊/前缀匹配。"""
    return ''.join(c for c in word if c.isalnum()).lower()


def create_schema(conn):
    conn.executescript('''
    DROP TABLE IF EXISTS ecdict;
    DROP TABLE IF EXISTS lemma;

    CREATE TABLE ecdict (
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        word VARCHAR(64) COLLATE NOCASE NOT NULL,
        sw VARCHAR(64) COLLATE NOCASE NOT NULL,
        phonetic VARCHAR(64),
        definition TEXT,
        translation TEXT,
        pos VARCHAR(16),
        collins INTEGER,
        oxford INTEGER,
        tag VARCHAR(64),
        bnc INTEGER,
        frq INTEGER,
        exchange TEXT,
        detail TEXT,
        audio TEXT
    );

    CREATE TABLE lemma (
        form TEXT PRIMARY KEY COLLATE NOCASE,
        base TEXT NOT NULL
    );
    ''')


def to_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def normalize_row(fields):
    """按位置映射到 COLUMNS。某些导出的 CSV 数据行带有未在表头声明的
    前导 id 列（14 列），需要丢弃；正常为 13 列。"""
    n = len(COLUMNS)
    if len(fields) == n + 1:
        fields = fields[1:]
    if len(fields) < n:
        fields = fields + [''] * (n - len(fields))
    return dict(zip(COLUMNS, fields))


def load_csv(conn, csv_path):
    insert = ('INSERT INTO ecdict '
              '(word, sw, phonetic, definition, translation, pos, '
              'collins, oxford, tag, bnc, frq, exchange, detail, audio) '
              'VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)')
    batch = []
    count = 0
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)  # 跳过表头
        for fields in reader:
            row = normalize_row(fields)
            word = (row.get('word') or '').strip()
            if not word:
                continue
            batch.append((
                word, stripword(word),
                row.get('phonetic'), row.get('definition'),
                row.get('translation'), row.get('pos'),
                to_int(row.get('collins')), to_int(row.get('oxford')),
                row.get('tag'), to_int(row.get('bnc')),
                to_int(row.get('frq')), row.get('exchange'),
                row.get('detail'), row.get('audio'),
            ))
            if len(batch) >= 2000:
                conn.executemany(insert, batch)
                count += len(batch)
                batch = []
    if batch:
        conn.executemany(insert, batch)
        count += len(batch)
    conn.commit()
    return count


def load_lemma(conn, lemma_path):
    """lemma.en.txt 行格式: `base/freq -> form1,form2,...`，反向建立 form -> base。"""
    if not os.path.exists(lemma_path):
        return 0
    rows = {}
    with open(lemma_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith(';') or '->' not in line:
                continue
            head, forms = line.split('->', 1)
            base = head.split('/', 1)[0].strip().lower()
            if not base:
                continue
            for form in forms.split(','):
                form = form.split('/', 1)[0].strip().lower()
                if form and form != base:
                    rows.setdefault(form, base)
    conn.executemany('INSERT OR IGNORE INTO lemma (form, base) VALUES (?, ?)',
                     list(rows.items()))
    conn.commit()
    return len(rows)


def create_indexes(conn):
    conn.executescript('''
    CREATE UNIQUE INDEX idx_word ON ecdict (word COLLATE NOCASE);
    CREATE INDEX idx_sw ON ecdict (sw COLLATE NOCASE);
    ''')
    conn.commit()


def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, 'dicts', 'ecdict.csv')
    lemma_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(HERE, 'lemma.en.txt')
    db_path = sys.argv[3] if len(sys.argv) > 3 else os.path.join(HERE, 'dicts', 'ecdict.db')

    if not os.path.exists(csv_path):
        print('找不到 CSV 文件: %s' % csv_path)
        return 1

    print('构建数据库: %s' % db_path)
    print('  词典来源: %s' % csv_path)
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    try:
        create_schema(conn)
        words = load_csv(conn, csv_path)
        print('  已导入单词: %d' % words)
        lemmas = load_lemma(conn, lemma_path)
        print('  已导入词形映射: %d' % lemmas)
        print('  建立索引中 ...')
        create_indexes(conn)
    finally:
        conn.close()
    print('完成!')
    return 0


if __name__ == '__main__':
    sys.exit(main())
