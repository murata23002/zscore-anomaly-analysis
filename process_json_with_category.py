import csv
import json
import os
import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
import shutil
import pandas as pd
import glob

# 画像の幅と高さを定義
IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

# CSVファイルに書き込むためのヘッダー
header = [
    "category",
    "filename",
    "class_id",
    "class_label",
    "score",
    "anomaly_distances",
    "angle_diff",
    "box_x1",
    "box_y1",
    "box_x2",
    "box_y2",
    "box_width",
    "box_height",
    "box_area",
    "box_area_percentage",
]

# バウンディングボックスのサイズを計算する関数
def calculate_box_size_area_and_percentage(box):
    # 負の値は0に置き換える
    x1 = max(box.get("x1", 0), 0)
    y1 = max(box.get("y1", 0), 0)
    x2 = max(box.get("x2", 0), 0)
    y2 = max(box.get("y2", 0), 0)

    # 矩形の幅と高さを計算
    width = x2 - x1
    height = y2 - y1

    # 面積を計算
    box_area = width * height

    # 画像全体に対する矩形の領域の割合を計算
    image_area = IMAGE_WIDTH * IMAGE_HEIGHT
    percentage = (box_area / image_area) * 100 if image_area > 0 else 0

    return width, height, box_area, percentage


def process_category(category, category_path, tmp_dir):
    """カテゴリごとの処理"""
    tmp_output_csv = os.path.join(tmp_dir, f"{category}_output.csv")
    
    with open(tmp_output_csv, mode="w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(header)

        # カテゴリディレクトリ内に "detect" ディレクトリが存在する場合
        detect_dir = os.path.join(category_path, "detect")
        if os.path.isdir(detect_dir):
            # JSONファイルを処理
            for filename in os.listdir(detect_dir):
                if filename.endswith(".json"):
                    with open(os.path.join(detect_dir, filename), "r") as file:
                        data = json.load(file)

                        # 各データエントリを処理
                        for item in data:
                            # バウンディングボックスのサイズ、面積、割合を計算
                            box = item.get("box", {})
                            width, height, box_area, percentage = (
                                calculate_box_size_area_and_percentage(box)
                            )

                            row = [
                                category,  # カテゴリ名
                                filename,  # ファイル名
                                item.get("class_id", ""),  # クラスID
                                item.get("class_label", ""),  # クラスラベル
                                item.get("score", ""),  # スコア
                                item.get("anomaly_distances", ""),  # 異常距離
                                item.get("angle_diff", ""),  # 角度差
                                box.get("x1", ""),  # バウンディングボックスのx1
                                box.get("y1", ""),  # バウンディングボックスのy1
                                box.get("x2", ""),  # バウンディングボックスのx2
                                box.get("y2", ""),  # バウンディングボックスのy2
                                width,  # 矩形の幅
                                height,  # 矩形の高さ
                                box_area,  # 矩形の面積
                                percentage,  # 矩形の画像に占める割合（％）
                            ]

                            # データをCSVに書き込む
                            writer.writerow(row)
    
    return tmp_output_csv


def combine_csv_files(output_csv, tmp_dir):
    """一時CSVファイルを結合して最終的なCSVを作成"""
    all_files = glob.glob(os.path.join(tmp_dir, "*.csv"))
    combined_csv = pd.concat([pd.read_csv(f) for f in all_files])
    combined_csv.to_csv(output_csv, index=False)
    print(f"All temporary CSVs combined into {output_csv}")


def main(base_dir, output_csv):
    # 一時ディレクトリの作成
    tmp_dir = "tmp_csvs"
    os.makedirs(tmp_dir, exist_ok=True)

    # カテゴリごとの処理を並列で実行
    with ProcessPoolExecutor() as executor:
        futures = {
            executor.submit(process_category, category, os.path.join(base_dir, category), tmp_dir): category
            for category in os.listdir(base_dir)
            if os.path.isdir(os.path.join(base_dir, category))
        }

        # 処理の進行状況を表示
        for future in as_completed(futures):
            category = futures[future]
            try:
                result = future.result()
                print(f"Category {category}: Processed successfully, saved to {result}")
            except Exception as exc:
                print(f"Category {category}: Generated an exception: {exc}")

    # 一時CSVファイルを結合して最終的なCSVファイルを作成
    combine_csv_files(output_csv, tmp_dir)

    # 一時ディレクトリを削除
    #shutil.rmtree(tmp_dir)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process JSON files into CSV with categories.")
    parser.add_argument("--base_dir", required=True, help="Base directory containing categories.")
    parser.add_argument("--output_csv", required=True, help="Output CSV file path.")
    args = parser.parse_args()

    main(args.base_dir, args.output_csv)
