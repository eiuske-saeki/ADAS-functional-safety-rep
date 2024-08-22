# src/scripts/run_simulation.py

import csv
import os
from tqdm import tqdm
from src.simulation.simulation_engine import SimulationEngine

def run_simulations(input_file: str, output_file: str):
    config = {
        'time_step': 0.01,
        'max_simulation_time': 10.0,
        'acceleration_jerk': 1.0 * 9.81,  # 1.0G/s を m/s^3 に変換
        'deceleration_jerk': 2.5 * 9.81,  # 2.5G/s を m/s^3 に変換
    }

    sim_engine = SimulationEngine(config)

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    input_path = os.path.join(root_dir, input_file)
    output_path = os.path.join(root_dir, output_file)
    log_dir = os.path.join(root_dir, 'data', 'output', 'logs')
    
    os.makedirs(log_dir, exist_ok=True)

    # 入力ファイルの行数を数える
    with open(input_path, 'r', encoding='utf-8-sig') as f:
        total_rows = sum(1 for _ in f) - 1  # ヘッダー行を除く

    with open(input_path, 'r', encoding='utf-8-sig') as infile, open(output_path, 'w', newline='', encoding='utf-8-sig') as outfile:
        reader = csv.DictReader(infile)
        
        # 元のフィールド名を保持し、新しい結果列を追加
        fieldnames = reader.fieldnames + [
            '衝突有無[回避無し]', '衝突時刻[回避無し]', '衝突位置[回避無し]', '有効衝突速度[回避無し]',
            '衝突有無[C0]', '衝突時刻[C0]', '衝突位置[C0]', '有効衝突速度[C0]',
            '衝突有無[C1]', '衝突時刻[C1]', '衝突位置[C1]', '有効衝突速度[C1]',
            '衝突有無[C2]', '衝突時刻[C2]', '衝突位置[C2]', '有効衝突速度[C2]'
        ]

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in tqdm(reader, total=total_rows, desc="Simulating", unit="record"):
            try:
                sim_engine.load_data(row)
                sim_engine.run_simulation()
                results = sim_engine.get_results()
                
                for key in ['回避無し', 'C0', 'C1', 'C2']:
                    row[f'衝突有無[{key}]'] = results[key]['衝突有無']
                    row[f'衝突時刻[{key}]'] = results[key]['衝突時刻']
                    row[f'衝突位置[{key}]'] = results[key]['衝突位置']
                    row[f'有効衝突速度[{key}]'] = results[key]['有効衝突速度']
                
                writer.writerow(row)
            except Exception as e:
                error_log_path = os.path.join(log_dir, 'error_log.txt')
                with open(error_log_path, 'a', encoding='utf-8') as error_file:
                    error_file.write(f"Error processing row {row.get('No', 'unknown')}: {str(e)}\n")
                continue

if __name__ == "__main__":
    run_simulations('data/input/accel_in.csv', 'data/output/simulation_results.csv')