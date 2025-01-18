import argparse
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def log_message(message, output_file=None):
    print(message)
    if output_file:
        with open(output_file, "a") as file:
            file.write(message + "\n")


# 指定されたカラムに基づく異常判定
def detect_anomalies(df, column, threshold):
    """
    指定されたカラムの値がしきい値を超えるかどうかでデータを分割します。

    Args:
        df (pd.DataFrame): 対象のデータフレーム
        column (str): チェック対象のカラム名
        threshold (float): 異常のしきい値

    Returns:
        pd.DataFrame, pd.DataFrame: 異常データと正常データ
    """
    return df[df[column] > threshold], df[df[column] <= threshold]


# スコアを0~1の範囲で10段階にビン分けする関数
#def create_fixed_bins(df, score_column):
#    bins = np.linspace(0, 1, 11)
#    labels = [f"{i/10:.1f}~{(i+1)/10:.1f}" for i in range(10)]
#    df["score_bin"] = pd.cut(df[score_column], bins, labels=labels, include_lowest=True)
#    return df

# スコアを0~1の範囲で10段階にビン分けし、0.0~0.1を除外する関数
def create_fixed_bins(df, score_column):
    # 0.0 ~ 0.1 のデータを除外
    df = df[df[score_column] > 0.1]
    
    # 0.1 ~ 1.0 の範囲を10段階にビン分け
    bins = np.linspace(0.1, 1, 10)  # ビンの範囲を変更
    labels = [f"{i/10:.1f}~{(i+1)/10:.1f}" for i in range(1, 10)]  # 0.0~0.1は除外
    df["score_bin"] = pd.cut(df[score_column], bins, labels=labels, include_lowest=True)
    
    return df

# スコアビンごとの異常割合を可視化
def plot_anomaly_ratio_by_score_bin(anomalies, non_anomalies, save_dir, column):
    anomalies = create_fixed_bins(anomalies, "score")
    non_anomalies = create_fixed_bins(non_anomalies, "score")

    anomaly_counts = anomalies["score_bin"].value_counts(sort=False)
    non_anomaly_counts = non_anomalies["score_bin"].value_counts(sort=False)
    anomaly_ratio = anomaly_counts / (anomaly_counts + non_anomaly_counts)

    output_path = os.path.join(save_dir, f"anomaly_ratio_by_score_bin_{column}.csv")
    anomaly_ratio.to_csv(output_path, index=True)
    print(f"Anomaly ratio by score bin saved to {output_path}")

    plt.figure(figsize=(12, 6))
    anomaly_ratio.plot(kind="bar", color="blue")
    plt.title(f"Anomaly Ratio by Score Bin ({column})")
    plt.xlabel("Score Bin")
    plt.ylabel("Anomaly Ratio")
    plt.xticks(rotation=45, ha="right")

    graph_output_path = os.path.join(save_dir, f"anomaly_ratio_by_score_bin_{column}.png")
    plt.tight_layout()
    plt.savefig(graph_output_path)
    plt.close()

    print(f"Anomaly ratio by score bin saved to {graph_output_path}")


def analyze_data(input_csv, column, threshold, output_dir):
    print(f"Reading data from {input_csv}...")
    data = pd.read_csv(input_csv)

    # 異常と正常データの分離
    anomalies, non_anomalies = detect_anomalies(data, column, threshold)

    # スコアビンごとの異常割合を可視化
    plot_anomaly_ratio_by_score_bin(anomalies, non_anomalies, output_dir, column)

    # 異常データを保存 (カラム名を含む)
    anomalies_csv_path = os.path.join(output_dir, f"{column}_anomalies.csv")
    anomalies.to_csv(anomalies_csv_path, index=False)
    print(f"Anomalies saved to {anomalies_csv_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", required=True, help="Input CSV file path")
    parser.add_argument("--column", required=True, choices=["anomaly_distances", "angle_diff"], help="Column for anomaly detection")
    parser.add_argument("--threshold", type=float, required=True, help="Threshold for anomaly detection")
    parser.add_argument("--output_dir", required=True, help="Output directory for analysis results")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    analyze_data(args.input_csv, args.column, args.threshold, args.output_dir)
    print("Analysis completed.")
