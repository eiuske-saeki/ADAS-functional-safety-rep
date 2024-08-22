# src/scripts/run_simulation.py

import csv
import os
import multiprocessing
from functools import partial
from tqdm import tqdm
from src.simulation.simulation_engine import SimulationEngine

def process_chunk(chunk, config):
    sim_engine = SimulationEngine(config)
    results = []
    for row in chunk:
        sim_engine.load_data(row)
        sim_engine.run_simulation()
        result = sim_engine.get_results()
        for key in ['回避無し', 'C0', 'C1', 'C2']:
            row[f'衝突有無[{key}]'] = result[key]['衝突有無']
            row[f'衝突時刻[{key}]'] = result[key]['衝突時刻']
            row[f'衝突位置[{key}]'] = result[key]['衝突位置']
            row[f'有効衝突速度[{key}]'] = result[key]['有効衝突速度']
        results.append(row)
    return results

def run_simulations(input_file: str, output_file: str):
    config = {
        'time_step': 0.1,  # タイムステップを0.1秒に変更
        'max_simulation_time': 10.0,
        'acceleration_jerk': 1.0 * 9.81,  # 1.0G/s を m/s^3 に変換
        'deceleration_jerk': 2.5 * 9.81,  # 2.5G/s を m/s^3 に変換
    }

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    input_path = os.path.join(root_dir, input_file)
    output_path = os.path.join(root_dir, output_file)
    log_dir = os.path.join(root_dir, 'data', 'output', 'logs')
    
    os.makedirs(log_dir, exist_ok=True)

    # 入力ファイルの行数を数える
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        total_rows = sum(1 for _ in f) - 1  # ヘッダー行を除く

    # データを読み込み、チャンクに分割
    with open(input_path, 'r', encoding='utf-8-sig') as infile:
        reader = csv.DictReader(infile)
        data = list(reader)

    # チャンクサイズを決定（例：CPUコア数で割る）
    chunk_size = max(1, total_rows // multiprocessing.cpu_count())
    chunks = [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    # マルチプロセッシングを使用してシミュレーションを実行
    with multiprocessing.Pool() as pool:
        all_results = list(tqdm(
            pool.imap(partial(process_chunk, config=config), chunks),
            total=len(chunks),
            desc="Processing chunks"
        ))

    # 結果をフラット化
    all_results = [item for sublist in all_results for item in sublist]

    # 結果をCSVファイルに書き込む
    with open(output_path, 'w', newline='', encoding='utf-8-sig') as outfile:
        if all_results:
            writer = csv.DictWriter(outfile, fieldnames=all_results[0].keys())
            writer.writeheader()
            writer.writerows(all_results)

    print(f"シミュレーション完了。結果は {output_path} に保存されました。")

if __name__ == "__main__":
    run_simulations('data/input/accel_in.csv', 'data/output/simulation_results.csv')