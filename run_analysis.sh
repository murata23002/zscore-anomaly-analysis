#!/bin/bash

# 親ディレクトリの作成
PARENT_DIR="dist"
FILTERED_OUTPUT_DIR="$PARENT_DIR/filtered_output"
ANALYSIS_OUTPUT_DIR="$PARENT_DIR/analysis_output"

mkdir -p "$FILTERED_OUTPUT_DIR"
mkdir -p "$ANALYSIS_OUTPUT_DIR"

# パス設定
INPUT_CSV="./taget/output_with_category.csv"
CONFIG_YAML="config.yaml"
CATEGORY_COLUMN="class_label"  # 解析時に使用するカテゴリ列

# 1. データフィルタリング
echo "Starting data filtering..."
python3 filter_data.py --input_csv "$INPUT_CSV" --config "$CONFIG_YAML" --output_dir "$FILTERED_OUTPUT_DIR"

# 2. Zスコア法で異常値分析 (クラスラベルごとと全体 - angle_diff)
echo "Starting anomaly analysis for angle_diff (Z-score method)..."
python3 analyze_anomalies.py --input_csv "$FILTERED_OUTPUT_DIR/filtered_output.csv" \
                             --column "angle_diff" \
                             --threshold 426.2900228969236 \
                             --output_dir "$ANALYSIS_OUTPUT_DIR/angle_diff"

# 3. Zスコア法で異常値分析 (クラスラベルごとと全体 - anomaly_distances)
echo "Starting anomaly analysis for anomaly_distances (Z-score method)..."
python3 analyze_anomalies.py --input_csv "$FILTERED_OUTPUT_DIR/filtered_output.csv" \
                             --column "anomaly_distances" \
                             --threshold 207.19406350700632 \
                             --output_dir "$ANALYSIS_OUTPUT_DIR/anomaly_distances"
# 4. カテゴリ分析の実行
echo "Starting category-based analysis..."
python3 category_analysis.py --input_csv "$FILTERED_OUTPUT_DIR/filtered_output.csv" --output_dir "$ANALYSIS_OUTPUT_DIR" --category_column "$CATEGORY_COLUMN"


echo "Analysis completed."