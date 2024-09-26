import tkinter as tk
from tkinter import ttk, filedialog
import sys
import os
import csv
from tqdm import tqdm

from src.data_generation.data_generator import DataGenerator
from src.simulation.simulation_engine import SimulationEngine
from src.utils import functions

class ADASSimulationApp:
    def __init__(self, root):
        self.root = root
        self.data_generator = DataGenerator()
        self.init_ui()
        self.generated_data = None
        self.output_path = None

    def init_ui(self):
        self.root.title('ADAS Functional Safety Simulation Tool')
        self.root.geometry('800x800')  # ウィンドウサイズをさらに大きくしました

        frame = ttk.Frame(self.root, padding="10")
        frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Data Generation Parameters
        ttk.Label(frame, text="Data Generation Parameters", font=('Helvetica', 12, 'bold')).grid(column=0, row=0, columnspan=2, pady=10)

        # Weight input
        ttk.Label(frame, text="Weight (comma-separated):").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.weight_entry = ttk.Entry(frame)
        self.weight_entry.grid(column=1, row=1, pady=5)
        self.weight_entry.insert(0, "50,55,2500")

        # Reaction time input
        ttk.Label(frame, text="Reaction time:").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.rtime_entry = ttk.Entry(frame)
        self.rtime_entry.grid(column=1, row=2, pady=5)
        self.rtime_entry.insert(0, "1.2")

        # Velocity set input
        ttk.Label(frame, text="Velocity set (start, end, step):").grid(column=0, row=3, sticky=tk.W, pady=5)
        self.vset_entry = ttk.Entry(frame)
        self.vset_entry.grid(column=1, row=3, pady=5)
        self.vset_entry.insert(0, "0.0,140,5.0")

        # Time set input
        ttk.Label(frame, text="Time set (start, end, step):").grid(column=0, row=4, sticky=tk.W, pady=5)
        self.tset_entry = ttk.Entry(frame)
        self.tset_entry.grid(column=1, row=4, pady=5)
        self.tset_entry.insert(0, "0.6,6.0,0.2")

        # Acceleration set input
        ttk.Label(frame, text="Acceleration set (start, end, step):").grid(column=0, row=5, sticky=tk.W, pady=5)
        self.accset_entry = ttk.Entry(frame)
        self.accset_entry.grid(column=1, row=5, pady=5)
        self.accset_entry.insert(0, "0.01,1.17,0.02")

        # Evasive set input
        ttk.Label(frame, text="Evasive set (comma-separated):").grid(column=0, row=6, sticky=tk.W, pady=5)
        self.evasiveset_entry = ttk.Entry(frame)
        self.evasiveset_entry.grid(column=1, row=6, pady=5)
        self.evasiveset_entry.insert(0, "0,0.4,0.8,1.0")

        generate_button = ttk.Button(frame, text='Generate Data', command=self.generate_data)
        generate_button.grid(column=1, row=7, pady=5)

        # Simulation Parameters
        ttk.Label(frame, text="Simulation Parameters", font=('Helvetica', 12, 'bold')).grid(column=0, row=8, columnspan=2, pady=10)

        # Time step input
        ttk.Label(frame, text="Time step:").grid(column=0, row=9, sticky=tk.W, pady=5)
        self.time_step_entry = ttk.Entry(frame)
        self.time_step_entry.grid(column=1, row=9, pady=5)
        self.time_step_entry.insert(0, "0.1")

        # Max simulation time input
        ttk.Label(frame, text="Max simulation time:").grid(column=0, row=10, sticky=tk.W, pady=5)
        self.max_sim_time_entry = ttk.Entry(frame)
        self.max_sim_time_entry.grid(column=1, row=10, pady=5)
        self.max_sim_time_entry.insert(0, "10.0")

        # Acceleration jerk input
        ttk.Label(frame, text="Acceleration jerk:").grid(column=0, row=11, sticky=tk.W, pady=5)
        self.acc_jerk_entry = ttk.Entry(frame)
        self.acc_jerk_entry.grid(column=1, row=11, pady=5)
        self.acc_jerk_entry.insert(0, "1.0")

        # Deceleration jerk input
        ttk.Label(frame, text="Deceleration jerk:").grid(column=0, row=12, sticky=tk.W, pady=5)
        self.dec_jerk_entry = ttk.Entry(frame)
        self.dec_jerk_entry.grid(column=1, row=12, pady=5)
        self.dec_jerk_entry.insert(0, "2.5")

        # Run Simulationボタンを追加
        simulate_button = ttk.Button(frame, text='Run Simulation', command=self.select_input_file)
        simulate_button.grid(column=1, row=13, pady=5)

        self.result_label = ttk.Label(frame, text='Results will be displayed here')
        self.result_label.grid(column=0, row=14, columnspan=2, pady=5)

        # プログレスバーを追加
        self.progress_bar = ttk.Progressbar(frame, orient="horizontal", length=300, mode="determinate")
        self.progress_bar.grid(column=0, row=15, columnspan=2, pady=5)

        # 結果表示用のテキストボックスを追加
        self.result_text = tk.Text(frame, height=10, width=80)
        self.result_text.grid(column=0, row=16, columnspan=2, pady=5)

    def generate_data(self):
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
        self.input_file = filedialog.askopenfilename(
            title="Select input CSV file",
            filetypes=[("CSV files", "*.csv")]
        )
        if self.input_file:
            self.run_simulations(self.input_file)
        else:
            self.result_text.insert(tk.END, "No file selected. Simulation cancelled.\n")

    def run_simulations(self, input_file):
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

def main():
    root = tk.Tk()
    app = ADASSimulationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()