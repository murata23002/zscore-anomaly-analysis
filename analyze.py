import pandas as pd
from scipy.stats import zscore

# データの読み込み
file_path = 'Body_tflite_model_mahalanobis_distances.csv'
data = pd.read_csv(file_path)

# Zスコアの計算
data['dist_zscore'] = zscore(data['dist'])
data['diff_zscore'] = zscore(data['diff'])

# 平均と標準偏差の計算
dist_mean = data['dist'].mean()
dist_std = data['dist'].std()
diff_mean = data['diff'].mean()
diff_std = data['diff'].std()

# Zスコアの閾値を1 ~ 5の範囲で計算
thresholds = range(1, 10)  # Zスコアの範囲を1から5まで

# 結果を保存するリスト
results = []

for z in thresholds:
    dist_thresholds = (dist_mean - z * dist_std, dist_mean + z * dist_std)
    diff_thresholds = (diff_mean - z * diff_std, diff_mean + z * diff_std)
    
    anomalies_dist = data[abs(data['dist_zscore']) > z]
    anomalies_diff = data[abs(data['diff_zscore']) > z]
    
    results.append({
        "Z-Score": z,
        "dist_lower_threshold": dist_thresholds[0],
        "dist_upper_threshold": dist_thresholds[1],
        "diff_lower_threshold": diff_thresholds[0],
        "diff_upper_threshold": diff_thresholds[1],
        "dist_anomalies_count": len(anomalies_dist),
        "diff_anomalies_count": len(anomalies_diff)
    })

# 結果をデータフレームに変換
results_df = pd.DataFrame(results)

# 結果を表示
print(results_df)

# 必要に応じてCSVファイルに保存
results_df.to_csv("z_score_thresholds.csv", index=False)
