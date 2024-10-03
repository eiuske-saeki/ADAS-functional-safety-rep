import pandas as pd
import matplotlib
matplotlib.use('Agg')  # グラフィカルなバックエンドを使用しない
import matplotlib.pyplot as plt
import seaborn as sns
import os
import tkinter as tk
from tkinter import filedialog

def select_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="CSVファイルを選択してください",
        filetypes=[("CSV files", "*.csv")]
    )
    return file_path

# カラーマップの選択肢
color_maps = {
    '1': 'YlOrRd',   # 黄色-オレンジ-赤 (デフォルト)
    '2': 'RdYlGn_r', # 赤-黄-緑 (反転)
    '3': 'Blues',    # 青のグラデーション
    '4': 'Greens',   # 緑のグラデーション
    '5': 'Purples',  # 紫のグラデーション
    '6': 'coolwarm', # 寒色-暖色
}

# ファイル選択と読み込み
file_path = select_file()
if not file_path:
    print("ファイルが選択されませんでした。")
    exit(1)

try:
    df = pd.read_csv(file_path)
except Exception as e:
    print(f"ファイルの読み込み中にエラーが発生しました: {e}")
    exit(1)

# 利用可能なパラメータを表示
print("利用可能なパラメータ:")
for column in df.columns:
    print(f"- {column}")

# ユーザーがパラメータを指定
x_param = input("横軸のパラメータを入力してください: ")
y_param = input("縦軸のパラメータを入力してください: ")

# パラメータの確認
if x_param not in df.columns or y_param not in df.columns:
    print("エラー: 指定されたパラメータがデータに存在しません。")
    exit(1)

# ASILの順序を定義
asil_order = ['QM', 'A', 'B', 'C', 'D']

# 重複を確認
duplicates = df.duplicated(subset=[x_param, y_param])
if duplicates.any():
    print(f"警告: 選択されたパラメータ（{x_param}, {y_param}）に重複があります。")
    print("最も厳しいASIL値を使用して集約します。")
    
    # ASIL値を数値に変換
    df['ASIL_num'] = pd.Categorical(df['ASIL'], categories=asil_order, ordered=True).codes
    
    # 重複を集約（最大のASIL値を選択）
    df_agg = df.groupby([x_param, y_param])['ASIL_num'].max().reset_index()
    
    # 数値を再びASILカテゴリに変換
    df_agg['ASIL'] = pd.Categorical.from_codes(df_agg['ASIL_num'], categories=asil_order, ordered=True)
else:
    df_agg = df

# ユーザーにカラーマップを選択させる
print("カラーマップを選択してください:")
for key, value in color_maps.items():
    print(f"{key}: {value}")

color_choice = input("選択してください (1-6): ")
cmap = color_maps.get(color_choice, 'YlOrRd')  # デフォルトは 'YlOrRd'

try:
    # ピボットテーブルの作成
    pivot = df_agg.pivot(index=y_param, columns=x_param, values='ASIL')
    pivot_numeric = pivot.apply(lambda x: pd.Categorical(x, categories=asil_order).codes)

    # Y軸を逆順にする
    pivot = pivot.sort_index(ascending=False)
    pivot_numeric = pivot_numeric.sort_index(ascending=False)

    # ヒートマップを描画
    plt.figure(figsize=(12, 8))
    heatmap = sns.heatmap(pivot_numeric, cmap=cmap, annot=pivot.values, fmt='', cbar=False)

    # カラーバーをカスタマイズ
    cbar = plt.colorbar(heatmap.collections[0], ticks=range(len(asil_order)))
    cbar.set_ticklabels(asil_order)

    plt.title(f'ASIL Map (Colormap: {cmap})')
    plt.xlabel(x_param)
    plt.ylabel(y_param)
    plt.tight_layout()

    # 結果を保存
    output_dir = os.path.dirname(file_path)
    output_image = os.path.join(output_dir, f'asil_map_{cmap}.png')
    plt.savefig(output_image)
    plt.close()

    print(f"ASILマップが '{output_image}' として保存されました。")

    # CSVファイルの作成
    # ピボットテーブルをそのまま使用（既に逆順になっている）
    csv_data = pivot

    # インデックス名を設定
    csv_data.index.name = y_param

    # CSVファイルとして保存（カスタムフォーマット）
    output_csv = os.path.join(output_dir, 'asil_map_data.csv')
    
    with open(output_csv, 'w', newline='') as f:
        # データ部分を書き込む
        csv_data.to_csv(f, header=False)
        
        # 列名を最後の行として追加
        f.write(f"{y_param},{','.join(map(str, csv_data.columns))}\n")

    print(f"データが '{output_csv}' として保存されました。")

    # 散布図の作成（カラーマップも同じものを使用）
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(df[x_param], df[y_param], c=pd.Categorical(df['ASIL'], categories=asil_order).codes, cmap=cmap)
    plt.colorbar(scatter, ticks=range(len(asil_order)), label='ASIL')
    plt.clim(-0.5, len(asil_order)-0.5)
    plt.gca().get_yaxis().get_major_formatter().set_useOffset(False)
    plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
    plt.gca().invert_yaxis()  # Y軸を逆順にする
    plt.title(f'ASIL Scatter Plot (Colormap: {cmap})')
    plt.xlabel(x_param)
    plt.ylabel(y_param)
    plt.tight_layout()

    # 散布図を保存
    scatter_output = os.path.join(output_dir, f'asil_scatter_plot_{cmap}.png')
    plt.savefig(scatter_output)
    plt.close()

    print(f"ASIL散布図が '{scatter_output}' として保存されました。")

except Exception as e:
    print(f"グラフの生成中にエラーが発生しました: {e}")
    exit(1)
    