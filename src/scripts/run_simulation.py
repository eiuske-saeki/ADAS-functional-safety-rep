# src/scripts/run_simulation.py

import csv
import os
import multiprocessing
from functools import partial
from tqdm import tqdm
from src.simulation.simulation_engine import SimulationEngine

def process_row(row, config):
    # マジヤバイ！1行分のデータを爆速で処理しちゃうよ～
    sim_engine = SimulationEngine(config)  # シミュレーションエンジンを作成
    sim_engine.load_data(row)  # データをロード
    sim_engine.run_simulation()  # シミュレーション実行
    return sim_engine.get_results()  # 結果をゲット

def process_batch(batch, config):
    # 超ヤバイ！複数の行を同時に処理しちゃうよ～マルチプロセスで爆速！
    with multiprocessing.Pool() as pool:
        # poolを使って複数のプロセスで同時に処理するの
        return list(pool.map(partial(process_row, config=config), batch))

def run_simulations(input_file: str, output_file: str, batch_size: int = 1000):
    # シミュレーションの設定をセットアップ、マジ重要！
    config = {
        'time_step': 0.1,  # 時間の刻み幅、0.1秒ごとにシミュレーション
        'max_simulation_time': 10.0,  # 最大シミュレーション時間、10秒で打ち切り
        'acceleration_jerk': 1.0 * 9.81,  # 加速度の変化率、重力加速度の1.0倍
        'deceleration_jerk': 2.5 * 9.81,  # 減速度の変化率、重力加速度の2.5倍
    }

    # ファイルのパスを設定、超便利！
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    input_path = os.path.join(root_dir, input_file)
    output_path = os.path.join(root_dir, output_file)
    log_dir = os.path.join(root_dir, 'data', 'output', 'logs')
    
    os.makedirs(log_dir, exist_ok=True)  # ログディレクトリを作成

    # 入力ファイルの行数をカウント、進捗バーのために必要なの！
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        total_rows = sum(1 for _ in f) - 1  # ヘッダー行を除外

    with open(input_path, 'r', encoding='utf-8-sig') as infile, \
         open(output_path, 'w', newline='', encoding='utf-8-sig') as outfile:
        
        reader = csv.DictReader(infile)
        original_fieldnames = reader.fieldnames
        result_fieldnames = [
            '衝突有無', '衝突時刻', '衝突位置', '有効衝突速度'
        ]
        scenario_fieldnames = ['回避無し', 'C0', 'C1', 'C2']
        
        # 出力用のフィールド名を作成、元のフィールド + シミュレーション結果
        fieldnames = original_fieldnames + [
            f'{result}[{scenario}]' for scenario in scenario_fieldnames
            for result in result_fieldnames
        ]
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()  # ヘッダーを書き込み

        batch = []
        for row in tqdm(reader, total=total_rows, desc="Processing", unit="row"):
            batch.append(row)
            if len(batch) >= batch_size:
                # バッチサイズに達したら処理開始！超効率的！
                results = process_batch(batch, config)
                for original_row, result_row in zip(batch, results):
                    output_row = original_row.copy()
                    for scenario in scenario_fieldnames:
                        for result in result_fieldnames:
                            output_row[f'{result}[{scenario}]'] = result_row[scenario][result]
                    writer.writerow(output_row)
                batch = []  # バッチをリセット

        # 残りのデータを処理、最後までしっかりやるよ！
        if batch:
            results = process_batch(batch, config)
            for original_row, result_row in zip(batch, results):
                output_row = original_row.copy()
                for scenario in scenario_fieldnames:
                    for result in result_fieldnames:
                        output_row[f'{result}[{scenario}]'] = result_row[scenario][result]
                writer.writerow(output_row)

    print(f"シミュレーション完了。結果は {output_path} に保存されました。")
    
if __name__ == "__main__":
    run_simulations('data/input/accel_in.csv', 'data/output/simulation_results.csv')