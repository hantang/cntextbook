#!/usr/bin/env bash
set -eu

INPUT=$1

# 配置
cp mkdocs-template.yml mkdocs.yml

# 删除不必要的md文件
find docs -name "*.md" ! -name "index.md" -type f -delete
find docs -name "*.pdf"  -type f -delete

# 生成文档和nav
python run.py --input "$INPUT"

pip install .

# 构建静态脚本
mkdocs build

echo "Done"
