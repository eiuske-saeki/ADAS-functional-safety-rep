import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import sys
import os
import csv
from tqdm import tqdm
import pandas as pd

from src.data_generation.data_generator import DataGenerator
from src.simulation.simulation_engine import SimulationEngine
from src.asil_calculation.asil_calculator import ASILCalculator
from src.utils import functions
from src.visualization.asil_map_generator import ASILMapGenerator

class ADASSimulationApp:
    def __init__(self, root):
        self.root = root
        self.data_generator = DataGenerator()
        self.generated_data = None
        self.output_path = None
        self.asil_map_generator = ASILMapGenerator()
        self.csv_data = None
        self.csv_columns = []
        self.init_ui()

    def init_ui(self):
        """GUIの初期化と各要素の配置を行う"""
        self.root.title('ADAS Functional Safety Simulation Tool')
        self.root.geometry('800x1000')  # ウィンドウサイズを大きくした

        frame = ttk.Frame(self.root, padding="10")
        frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Data Generation Parameters
        ttk.Label(frame, text="Data Generation Parameters", font=('Helvetica', 12, 'bold')).grid(column=0, row=0, columnspan=2, pady=10)

        # 各パラメータの入力フィールドを作成
        params = [
            ("Weight (comma-separated):", "weight_entry", "50,55,2500"),
            ("Reaction time:", "rtime_entry", "1.2"),
            ("Velocity set (start, end, step):", "vset_entry", "0.0,140,5.0"),
            ("Time set (start, end, step):", "tset_entry", "0.6,6.0,0.2"),
            ("Acceleration set (start, end, step):", "accset_entry", "0.01,1.17,0.02"),
            ("Evasive set (comma-separated):", "evasiveset_entry", "0,0.4,0.8,1.0")
        ]

        for i, (label, attr, default) in enumerate(params, start=1):
            ttk.Label(frame, text=label).grid(column=0, row=i, sticky=tk.W, pady=5)
            entry = ttk.Entry(frame)
            entry.grid(column=1, row=i, pady=5)
            entry.insert(0, default)
            setattr(self, attr, entry)

        # Generate Dataボタン
        generate_button = ttk.Button(frame, text='Generate Data', command=self.generate_data)
        generate_button.grid(column=1, row=len(params)+1, pady=5)

        # Simulation Parameters
        ttk.Label(frame, text="Simulation Parameters", font=('Helvetica', 12, 'bold')).grid(column=0, row=len(params)+2, columnspan=2, pady=10)

        # シミュレーションパラメータの入力フィールドを作成
        sim_params = [
            ("Time step:", "time_step_entry", "0.1"),
            ("Max simulation time:", "max_sim_time_entry", "10.0"),
            ("Acceleration jerk:", "acc_jerk_entry", "1.0"),
            ("Deceleration jerk:", "dec_jerk_entry", "2.5")
        ]

        for i, (label, attr, default) in enumerate(sim_params, start=len(params)+3):
            ttk.Label(frame, text=label).grid(column=0, row=i, sticky=tk.W, pady=5)
            entry = ttk.Entry(frame)
            entry.grid(column=1, row=i, pady=5)
            entry.insert(0, default)
            setattr(self, attr, entry)

        # Run Simulationボタン
        simulate_button = ttk.Button(frame, text='Run Simulation', command=self.select_input_file)
        simulate_button.grid(column=1, row=len(params)+len(sim_params)+3, pady=5)

        # ASIL Calculationボタン
        asil_button = ttk.Button(frame, text='Run ASIL Calculation', command=self.run_asil_calculation)
        asil_button.grid(column=1, row=len(params)+len(sim_params)+4, pady=5)

        # CSVファイル読み込みボタンを追加
        load_csv_button = ttk.Button(frame, text='Load CSV File', command=self.load_csv_file)
        load_csv_button.grid(column=1, row=len(params)+len(sim_params)+5, pady=5)

        # パラメータ選択用のフレームを追加
        self.param_frame = ttk.LabelFrame(frame, text="ASIL Map Parameters")
        self.param_frame.grid(column=0, row=len(params)+len(sim_params)+6, columnspan=2, pady=10, padx=10, sticky="ew")
        self.create_parameter_selection()

        # ASILマップ生成ボタンを移動
        generate_asil_map_button = ttk.Button(frame, text='Generate ASIL Map', command=self.generate_asil_map)
        generate_asil_map_button.grid(column=1, row=len(params)+len(sim_params)+7, pady=5)

        # 結果表示用のラベル、プログレスバー、テキストボックス
        self.result_label = ttk.Label(frame, text='Results will be displayed here')
        self.result_label.grid(column=0, row=len(params)+len(sim_params)+8, columnspan=2, pady=5)

        self.progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(column=0, row=len(params)+len(sim_params)+9, columnspan=2, pady=5)

        self.result_text = tk.Text(frame, height=10, width=80)
        self.result_text.grid(column=0, row=len(params)+len(sim_params)+10, columnspan=2, pady=5)

    def create_parameter_selection(self):
        ttk.Label(self.param_frame, text="X-axis:").grid(column=0, row=0, padx=5, pady=5)
        self.x_param = ttk.Combobox(self.param_frame, state="readonly")
        self.x_param.grid(column=1, row=0, padx=5, pady=5)

        ttk.Label(self.param_frame, text="Y-axis:").grid(column=0, row=1, padx=5, pady=5)
        self.y_param = ttk.Combobox(self.param_frame, state="readonly")
        self.y_param.grid(column=1, row=1, padx=5, pady=5)

        ttk.Label(self.param_frame, text="Color map:").grid(column=0, row=2, padx=5, pady=5)
        self.color_map = ttk.Combobox(self.param_frame, state="readonly", values=list(self.asil_map_generator.color_maps.keys()))
        self.color_map.grid(column=1, row=2, padx=5, pady=5)
        self.color_map.set('1')  # デフォルト値を設定

    def generate_data(self):
        """データ生成を実行し、CSVファイルに保存する"""
        user_input = {
            'weight': [float(x) for x in self.weight_entry.get().split(',')],
            'rtime': [float(self.rtime_entry.get())],
            'vset_start': float(self.vset_entry.get().split(',')[0]),
            'vset_end': float(self.vset_entry.get().split(',')[1]),
            'vset_step': float(self.vset_entry.get().split(',')[2]),
            'tset_start': float(self.tset_entry.get().split(',')[0]),
            'tset_end': float(self.tset_entry.get().split(',')[1]),
            'tset_step': float(self.tset_entry.get().split(',')[2]),
            'accset_start': float(self.accset_entry.get().split(',')[0]),
            'accset_end': float(self.accset_entry.get().split(',')[1]),
            'accset_step': float(self.accset_entry.get().split(',')[2]),
            'evasiveset': [float(x) for x in self.evasiveset_entry.get().split(',')]
        }

        try:
            self.generated_data = self.data_generator.generate_data(user_input)
            
            output_dir = os.path.join('data', 'input')
            os.makedirs(output_dir, exist_ok=True)
            
            self.output_path = os.path.join(output_dir, "accel_in.csv")
            
            functions.save_data_to_csv(self.generated_data, self.output_path)
            
            self.result_label.config(text=f"Data generated: {len(self.generated_data)} records\nSaved to: {self.output_path}")
            print(f"データを {self.output_path} に保存しました。チェックしてみてください！")
        except ValueError as e:
            error_message = f"エラーが発生しました: {e}"
            self.result_label.config(text=error_message)
            print(error_message)
        except IOError as e:
            error_message = f"ファイルの書き込みに失敗しました: {e}"
            self.result_label.config(text=error_message)
            print(error_message)

    def select_input_file(self):
        """入力ファイルを選択し、シミュレーションを実行する"""
        self.input_file = filedialog.askopenfilename(
            title="Select input CSV file",
            filetypes=[("CSV files", "*.csv")]
        )
        if self.input_file:
            self.run_simulations(self.input_file)
        else:
            self.result_text.insert(tk.END, "No file selected. Simulation cancelled.\n")

    def run_simulations(self, input_file):
        """シミュレーションを実行し、結果をCSVファイルに保存する"""
        config = {
            'time_step': float(self.time_step_entry.get()),
            'max_simulation_time': float(self.max_sim_time_entry.get()),
            'acceleration_jerk': float(self.acc_jerk_entry.get()) * 9.81,
            'deceleration_jerk': float(self.dec_jerk_entry.get()) * 9.81,
        }

        output_file = os.path.join('data', 'output', 'simulation_results.csv')

        try:
            with open(input_file, 'r', encoding='utf-8-sig') as infile, \
                 open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
                
                reader = csv.DictReader(infile)
                original_fieldnames = reader.fieldnames
                result_fieldnames = ['衝突有無', '衝突時刻', '衝突位置', '有効衝突速度']
                scenario_fieldnames = ['回避無し', 'C0', 'C1', 'C2']
                
                fieldnames = original_fieldnames + [
                    f'{result}[{scenario}]' for scenario in scenario_fieldnames
                    for result in result_fieldnames
                ]
                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                total_rows = sum(1 for _ in infile) - 1  # ヘッダー行を除外
                infile.seek(0)
                next(reader)  # ヘッダーをスキップ

                self.progress_bar["maximum"] = total_rows
                self.progress_bar["value"] = 0

                for row in reader:
                    sim_engine = SimulationEngine(config)
                    sim_engine.load_data(row)
                    sim_engine.run_simulation()
                    results = sim_engine.get_results()

                    output_row = row.copy()
                    for scenario in scenario_fieldnames:
                        for result in result_fieldnames:
                            output_row[f'{result}[{scenario}]'] = results[scenario][result]
                    writer.writerow(output_row)

                    self.progress_bar["value"] += 1
                    self.root.update_idletasks()

            self.result_text.insert(tk.END, f"Simulation completed. Results saved to {output_file}\n")

        except Exception as e:
            error_message = f"シミュレーション中にエラーが発生しました: {e}"
            self.result_text.insert(tk.END, error_message + "\n")
            print(error_message)

    def run_asil_calculation(self):
        """ASIL計算を実行するためのファイル選択ダイアログを表示し、計算を開始する"""
        input_file = filedialog.askopenfilename(
            title="Select simulation results CSV file",
            filetypes=[("CSV files", "*.csv")]
        )
        if input_file:
            output_file = input_file.replace('.csv', '_with_asil.csv')
            self.calculate_and_save_asil(input_file, output_file)
        else:
            self.result_text.insert(tk.END, "No file selected. ASIL calculation cancelled.\n")

    def calculate_and_save_asil(self, input_file: str, output_file: str):
        """ASIL計算を実行し、結果をCSVファイルに保存する"""
        asil_calculator = ASILCalculator()
        
        try:
            # CSVファイルからデータを読み込む
            with open(input_file, 'r', encoding='utf-8-sig') as infile:
                reader = csv.DictReader(infile)
                data = list(reader)
            
            if not data:
                self.result_text.insert(tk.END, f"警告: 入力ファイル {input_file} にデータがありません。\n")
                return

            # ASIL計算を行う
            total_rows = len(data)
            self.progress_bar["maximum"] = total_rows
            self.progress_bar["value"] = 0

            for i, row in enumerate(data):
                try:
                    asil_results = asil_calculator.calculate(row)
                    row.update(asil_results)
                except Exception as e:
                    self.result_text.insert(tk.END, f"行 {i+1} の処理中にエラーが発生しました: {str(e)}\n")
                    continue  # エラーが発生しても次の行の処理を続ける
                self.progress_bar["value"] = i + 1
                self.root.update_idletasks()
            
            # 結果を新しいCSVファイルに書き込む
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

            self.result_text.insert(tk.END, f"ASIL calculation completed. Results saved to {output_file}\n")
        
        except FileNotFoundError:
            self.result_text.insert(tk.END, f"エラー: ファイル {input_file} が見つかりません。\n")
        except PermissionError:
            self.result_text.insert(tk.END, f"エラー: ファイル {output_file} に書き込み権限がありません。\n")
        except Exception as e:
            self.result_text.insert(tk.END, f"エラー: ASIL計算中に予期しないエラーが発生しました: {str(e)}\n")
            import traceback
            self.result_text.insert(tk.END, f"詳細なエラー情報:\n{traceback.format_exc()}\n")

    def load_csv_file(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV file for ASIL Map",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            try:
                self.csv_data = pd.read_csv(file_path)
                self.csv_columns = list(self.csv_data.columns)
                self.x_param['values'] = self.csv_columns
                self.y_param['values'] = self.csv_columns
                self.result_text.insert(tk.END, f"CSV file loaded: {file_path}\n")
                messagebox.showinfo("Success", "CSV file loaded successfully")
            except Exception as e:
                self.result_text.insert(tk.END, f"Error loading CSV file: {str(e)}\n")
                messagebox.showerror("Error", f"Failed to load CSV file: {str(e)}")

    def generate_asil_map(self):
        if self.csv_data is None:
            messagebox.showwarning("Warning", "Please load a CSV file first")
            return

        x_param = self.x_param.get()
        y_param = self.y_param.get()
        color_choice = self.color_map.get()

        if not x_param or not y_param:
            messagebox.showwarning("Warning", "Please select both X and Y parameters")
            return

        output_dir = os.path.join('data', 'output', 'asil_maps')
        os.makedirs(output_dir, exist_ok=True)

        result = self.asil_map_generator.generate_asil_map(
            data=self.csv_data,  # ここを変更
            x_param=x_param,
            y_param=y_param,
            color_choice=color_choice,
            output_dir=output_dir
        )

        self.result_text.insert(tk.END, f"ASIL Map Generation Result:\n{result}\n")

def main():
    root = tk.Tk()
    app = ADASSimulationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()