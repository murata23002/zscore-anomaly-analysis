import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split

# データの読み込み
file_path_body = "face.csv"
body_data = pd.read_csv(file_path_body)

# 特徴量とターゲット変数の準備
X = body_data[["anomaly_distances", "angle_diff", "box_area"]]
y = body_data["score"]

# 訓練データとテストデータに分割
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 1. ランダムフォレスト回帰モデル
rf_model = RandomForestRegressor(n_estimators=100, random_state=42)
rf_model.fit(X_train, y_train)
y_pred_rf = rf_model.predict(X_test)
rmse_rf = mean_squared_error(y_test, y_pred_rf, squared=False)

print(f"Random Forest RMSE: {rmse_rf}")

# 残差を使用した異常値検出
# 残差の計算（実際の値 - 予測値）
residuals_rf = np.abs(y_test - y_pred_rf)

# 残差の標準偏差を使用して閾値を設定 (例: 残差が2標準偏差以上を異常とみなす)
threshold_rf = 2 * np.std(residuals_rf)

# 異常値の判定
anomalies_rf = residuals_rf > threshold_rf

# 異常データと代表データの取得（行番号を含めて）
anomalous_data_rf = X_test[anomalies_rf]
representative_data_rf = X_test[~anomalies_rf]

# 異常データに対応する y_test と予測値を取得
anomalous_y_test = y_test[anomalies_rf]
anomalous_y_pred = y_pred_rf[anomalies_rf]

# 代表データに対応する y_test と予測値を取得
representative_y_test = y_test[~anomalies_rf]
representative_y_pred = y_pred_rf[~anomalies_rf]

# 異常データとその y_test, y_pred の表示
print(f"異常データ (Random Forest):\n{anomalous_data_rf}")
print(f"異常データの実際のスコア (y_test):\n{anomalous_y_test}")
print(f"異常データの予測値 (y_pred):\n{anomalous_y_pred}")

# 代表データとその y_test, y_pred の表示
print(f"代表データ (Random Forest):\n{representative_data_rf}")
print(f"代表データの実際のスコア (y_test):\n{representative_y_test}")
print(f"代表データの予測値 (y_pred):\n{representative_y_pred}")
