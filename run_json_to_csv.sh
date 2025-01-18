#!/bin/bash

# 親ディレクトリの作成
PARENT_DIR="taget"
OUTPUT_CSV="$PARENT_DIR/output_with_category.csv"
BASE_DIR="./detect/"

mkdir -p "$PARENT_DIR"

# JSON -> CSV 変換処理
echo "Starting JSON to CSV conversion with categories..."
python3 process_json_with_category.py --base_dir "$BASE_DIR" --output_csv "$OUTPUT_CSV"

echo "Conversion completed. Output CSV saved in $OUTPUT_CSV"
