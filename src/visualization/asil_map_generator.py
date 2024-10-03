# src/visualization/asil_map_generator.py

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # グラフィカルなバックエンドを使用しない
import matplotlib.pyplot as plt
import seaborn as sns
import os

class ASILMapGenerator:
    def __init__(self):
        self.color_maps = {
            '1': 'YlOrRd',   # 黄色-オレンジ-赤 (デフォルト)
            '2': 'RdYlGn_r', # 赤-黄-緑 (反転)
            '3': 'Blues',    # 青のグラデーション
            '4': 'Greens',   # 緑のグラデーション
            '5': 'Purples',  # 紫のグラデーション
            '6': 'coolwarm', # 寒色-暖色
        }
        self.asil_order = ['QM', 'A', 'B', 'C', 'D']

    def generate_asil_map(self, data, x_param, y_param, color_choice, output_dir):
        try:
            if isinstance(data, str):
                df = pd.read_csv(data)
            elif isinstance(data, pd.DataFrame):
                df = data
            else:
                raise ValueError("Invalid data type. Expected string (file path) or DataFrame.")
        except Exception as e:
            return f"データの読み込み中にエラーが発生しました: {e}"

        if x_param not in df.columns or y_param not in df.columns:
            return f"エラー: 指定されたパラメータ ({x_param}, {y_param}) がデータに存在しません。"

        # 重複の確認と処理
        duplicates = df.duplicated(subset=[x_param, y_param])
        if duplicates.any():
            df['ASIL_num'] = pd.Categorical(df['ASIL'], categories=self.asil_order, ordered=True).codes
            df_agg = df.groupby([x_param, y_param])['ASIL_num'].max().reset_index()
            df_agg['ASIL'] = pd.Categorical.from_codes(df_agg['ASIL_num'], categories=self.asil_order, ordered=True)
        else:
            df_agg = df

        cmap = self.color_maps.get(color_choice, 'YlOrRd')

        try:
            # ピボットテーブルの作成
            pivot = df_agg.pivot(index=y_param, columns=x_param, values='ASIL')
            pivot_numeric = pivot.apply(lambda x: pd.Categorical(x, categories=self.asil_order).codes)

            # Y軸を逆順にする
            pivot = pivot.sort_index(ascending=False)
            pivot_numeric = pivot_numeric.sort_index(ascending=False)

            # ヒートマップを描画
            plt.figure(figsize=(12, 8))
            heatmap = sns.heatmap(pivot_numeric, cmap=cmap, annot=pivot.values, fmt='', cbar=False)

            # カラーバーをカスタマイズ
            cbar = plt.colorbar(heatmap.collections[0], ticks=range(len(self.asil_order)))
            cbar.set_ticklabels(self.asil_order)

            plt.title(f'ASIL Map (Colormap: {cmap})')
            plt.xlabel(x_param)
            plt.ylabel(y_param)
            plt.tight_layout()

            # 結果を保存
            output_image = os.path.join(output_dir, f'asil_map_{cmap}.png')
            plt.savefig(output_image)
            plt.close()

            # CSVファイルの作成
            csv_data = pivot
            csv_data.index.name = y_param
            output_csv = os.path.join(output_dir, 'asil_map_data.csv')
            
            with open(output_csv, 'w', newline='') as f:
                csv_data.to_csv(f, header=False)
                f.write(f"{y_param},{','.join(map(str, csv_data.columns))}\n")

            # 散布図の作成
            plt.figure(figsize=(12, 8))
            scatter = plt.scatter(df_agg[x_param], df_agg[y_param], c=df_agg['ASIL_num'], cmap=cmap, s=50)
            plt.colorbar(scatter, ticks=range(len(self.asil_order)), label='ASIL')
            plt.gca().get_xaxis().get_major_formatter().set_useOffset(False)
            plt.gca().invert_yaxis()
            plt.title(f'ASIL Scatter Plot (Colormap: {cmap})')
            plt.xlabel(x_param)
            plt.ylabel(y_param)
            plt.tight_layout()

            scatter_output = os.path.join(output_dir, f'asil_scatter_plot_{cmap}.png')
            plt.savefig(scatter_output)
            plt.close()

            return f"ASILマップが '{output_image}' として、\n" \
                   f"データが '{output_csv}' として、\n" \
                   f"ASIL散布図が '{scatter_output}' として保存されました。"

        except Exception as e:
            return f"グラフの生成中にエラーが発生しました: {e}"

# 使用例（main.pyから呼び出される場合は不要）
if __name__ == "__main__":
    generator = ASILMapGenerator()
    result = generator.generate_asil_map(
        file_path="path/to/your/csv",
        x_param="横軸パラメータ",
        y_param="縦軸パラメータ",
        color_choice="1",
        output_dir="path/to/output/directory"
    )
    print(result)