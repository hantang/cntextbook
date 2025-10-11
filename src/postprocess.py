"""
清除html注释
"""

import argparse
import logging
from pathlib import Path
import re


def clean_docs(docs_dir):
    files = Path(docs_dir).rglob("*.md")
    files = sorted(files)
    count = 0
    logging.info(f"clean docs = {len(files)}")
    for file in files:
        with open(file, encoding="utf-8") as f:
            text = f.read()
        if "<!--" not in text:
            continue
        count += 1
        text = re.sub(r"<!--[^>]*-->\n", "", text)
        with open(file, "w", encoding="utf-8") as f:
            f.write(text)
    logging.info(f"Cleaned = {count}")

if __name__ == "__main__":
    fmt = "%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s %(message)s"
    logging.basicConfig(level=logging.INFO, format=fmt)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--docs", type=str, default="docs", help="网站文档目录")
    args = parser.parse_args()

    logging.info(f"args = {args}")
    clean_docs(args.docs)
