import argparse
import operator
import os
import shutil
import pandas as pd
import yaml

def filter_data(input_csv, config_yaml, output_dir):
    # YAMLのフィルタ条件を読み込む
    print(f"Loading filter conditions from {config_yaml}...")
    with open(config_yaml) as file:
        conditions = yaml.safe_load(file)

    operators = {
        "==": operator.eq,
        "!=": operator.ne,
        ">": operator.gt,
        "<": operator.lt,
        ">=": operator.ge,
        "<=": operator.le,
    }

    # CSVファイルを読み込む
    print(f"Reading data from {input_csv}...")
    data = pd.read_csv(input_csv)

    # フィルタリング処理
    print("Starting filtering process...")
    filtered_data = data.copy()
    for condition in conditions["filters"]:
        field = condition["field"]
        op = operators[condition["operator"]]
        value = condition["value"]
        print(f"Applying filter: {field} {condition['operator']} {value}")
        filtered_data = filtered_data[op(filtered_data[field], value)]

    # フィルタリング後の件数を表示
    print(f"Number of records after filtering: {len(filtered_data)}")

    # "filename" から時間情報を抽出
    print("Extracting time information from 'filename' column...")
    filtered_data["time"] = filtered_data["filename"].str.extract(r"_(\d{6})\.json")

    # 出力ディレクトリを作成
    print(f"Creating output directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)

    # フィルタリングされたデータをCSVに保存
    csv_output_path = os.path.join(output_dir, "filtered_output.csv")
    print(f"Saving filtered data to {csv_output_path}...")
    filtered_data.to_csv(csv_output_path, index=False)

    # config.yamlをコピー
    print(f"Copying {config_yaml} to {output_dir}...")
    shutil.copy(config_yaml, output_dir)

    print("Filtering process completed.")
    return csv_output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", required=True, help="Input CSV file path")
    parser.add_argument("--config", required=True, help="YAML config file path")
    parser.add_argument("--output_dir", required=True, help="Output directory for filtered data")
    args = parser.parse_args()

    filter_data(args.input_csv, args.config, args.output_dir)
