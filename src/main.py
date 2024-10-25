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
        self.root.geometry('1024x768')

        # メインフレームの作成
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # タブの作成
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 各タブのフレームを作成
        self.overview_tab = ttk.Frame(self.notebook)
        self.data_gen_tab = ttk.Frame(self.notebook)
        self.simulation_tab = ttk.Frame(self.notebook)
        self.asil_tab = ttk.Frame(self.notebook)
        self.visual_tab = ttk.Frame(self.notebook)

        # タブの追加
        self.notebook.add(self.overview_tab, text='Overview')
        self.notebook.add(self.data_gen_tab, text='Data Generation')
        self.notebook.add(self.simulation_tab, text='Simulation')
        self.notebook.add(self.asil_tab, text='ASIL Calculation')
        self.notebook.add(self.visual_tab, text='Visualization')

        # 各タブの内容を初期化
        self.init_overview_tab()
        self.init_data_gen_tab()
        self.init_simulation_tab()
        self.init_asil_tab()
        self.init_visualization_tab()

        # ウィンドウのリサイズ設定
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1)
    
    def init_overview_tab(self):
        """Overview タブの初期化"""
        frame = ttk.Frame(self.overview_tab, padding="10")
        frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # ステータス表示部分
        status_frame = ttk.LabelFrame(frame, text="Current Status", padding="5")
        status_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.status_text = tk.Text(status_frame, height=4, width=60)
        self.status_text.grid(column=0, row=0, padx=5, pady=5)
        self.status_text.insert('1.0', 'Ready to start...')
        
        # クイックアクションボタン
        actions_frame = ttk.LabelFrame(frame, text="Quick Actions", padding="5")
        actions_frame.grid(column=0, row=1, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        ttk.Button(actions_frame, text="Generate New Data", 
                   command=lambda: self.notebook.select(1)).grid(column=0, row=0, padx=5, pady=5)
        ttk.Button(actions_frame, text="Run Simulation", 
                   command=lambda: self.notebook.select(2)).grid(column=1, row=0, padx=5, pady=5)
        ttk.Button(actions_frame, text="Calculate ASIL", 
                   command=lambda: self.notebook.select(3)).grid(column=2, row=0, padx=5, pady=5)
        
        # 結果表示部分
        results_frame = ttk.LabelFrame(frame, text="Latest Results", padding="5")
        results_frame.grid(column=0, row=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)
        
        self.results_text = tk.Text(results_frame, height=10, width=60)
        self.results_text.grid(column=0, row=0, padx=5, pady=5)

    def init_data_gen_tab(self):
        """Data Generation タブの初期化"""
        frame = ttk.Frame(self.data_gen_tab, padding="10")
        frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Weight Parameters
        weight_frame = ttk.LabelFrame(frame, text="Vehicle Weights", padding="5")
        weight_frame.grid(column=0, row=0, sticky=(tk.W, tk.E), pady=5)

        # Weight entries (動的に追加可能)
        self.weight_entries = []
        self.weight_frame = weight_frame
        ttk.Button(weight_frame, text="Add Weight", 
                command=self.add_weight_entry).grid(column=0, row=0, padx=5, pady=5)

        # Range Parameters
        ranges_frame = ttk.LabelFrame(frame, text="Range Parameters", padding="5")
        ranges_frame.grid(column=0, row=1, sticky=(tk.W, tk.E), pady=5)

        # Velocity Range
        ttk.Label(ranges_frame, text="Velocity Range (km/h)").grid(column=0, row=0, padx=5, pady=5)
        self.vset_start = ttk.Entry(ranges_frame, width=10)
        self.vset_start.grid(column=1, row=0, padx=5)
        self.vset_start.insert(0, "0.0")
        
        ttk.Label(ranges_frame, text="to").grid(column=2, row=0)
        self.vset_end = ttk.Entry(ranges_frame, width=10)
        self.vset_end.grid(column=3, row=0, padx=5)
        self.vset_end.insert(0, "140")
        
        ttk.Label(ranges_frame, text="step").grid(column=4, row=0)
        self.vset_step = ttk.Entry(ranges_frame, width=10)
        self.vset_step.grid(column=5, row=0, padx=5)
        self.vset_step.insert(0, "5.0")

        # Time Range
        ttk.Label(ranges_frame, text="Time Range (sec)").grid(column=0, row=1, padx=5, pady=5)
        self.tset_start = ttk.Entry(ranges_frame, width=10)
        self.tset_start.grid(column=1, row=1, padx=5)
        self.tset_start.insert(0, "0.6")
        
        ttk.Label(ranges_frame, text="to").grid(column=2, row=1)
        self.tset_end = ttk.Entry(ranges_frame, width=10)
        self.tset_end.grid(column=3, row=1, padx=5)
        self.tset_end.insert(0, "6.0")
        
        ttk.Label(ranges_frame, text="step").grid(column=4, row=1)
        self.tset_step = ttk.Entry(ranges_frame, width=10)
        self.tset_step.grid(column=5, row=1, padx=5)
        self.tset_step.insert(0, "0.2")

        # Acceleration Range
        ttk.Label(ranges_frame, text="Acceleration Range (G)").grid(column=0, row=2, padx=5, pady=5)
        self.accset_start = ttk.Entry(ranges_frame, width=10)
        self.accset_start.grid(column=1, row=2, padx=5)
        self.accset_start.insert(0, "0.01")
        
        ttk.Label(ranges_frame, text="to").grid(column=2, row=2)
        self.accset_end = ttk.Entry(ranges_frame, width=10)
        self.accset_end.grid(column=3, row=2, padx=5)
        self.accset_end.insert(0, "1.17")
        
        ttk.Label(ranges_frame, text="step").grid(column=4, row=2)
        self.accset_step = ttk.Entry(ranges_frame, width=10)
        self.accset_step.grid(column=5, row=2, padx=5)
        self.accset_step.insert(0, "0.02")

        # Evasive Parameters
        evasive_frame = ttk.LabelFrame(frame, text="Evasive Parameters", padding="5")
        evasive_frame.grid(column=0, row=2, sticky=(tk.W, tk.E), pady=5)

        evasive_labels = ["No evasion", "C0", "C1", "C2"]
        self.evasive_entries = []
        for i, label in enumerate(evasive_labels):
            ttk.Label(evasive_frame, text=label).grid(column=0, row=i, padx=5, pady=5)
            entry = ttk.Entry(evasive_frame, width=10)
            entry.grid(column=1, row=i, padx=5, pady=5)
            entry.insert(0, ["0", "0.4", "0.8", "1.0"][i])
            self.evasive_entries.append(entry)

        # Reaction Time
        reaction_frame = ttk.LabelFrame(frame, text="Reaction Time", padding="5")
        reaction_frame.grid(column=0, row=3, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(reaction_frame, text="Reaction time (sec)").grid(column=0, row=0, padx=5, pady=5)
        self.rtime_entry = ttk.Entry(reaction_frame, width=10)
        self.rtime_entry.grid(column=1, row=0, padx=5)
        self.rtime_entry.insert(0, "1.2")

        # Generate Button
        ttk.Button(frame, text="Generate Data", 
                command=self.generate_data).grid(column=0, row=4, pady=10)

        # Results
        results_frame = ttk.LabelFrame(frame, text="Results", padding="5")
        results_frame.grid(column=0, row=5, sticky=(tk.W, tk.E), pady=5)
        
        self.data_gen_result = tk.Text(results_frame, height=10, width=60)
        self.data_gen_result.grid(column=0, row=0, sticky=(tk.W, tk.E), pady=5, padx=5)
    
    def init_simulation_tab(self):
        """Simulation タブの初期化"""
        frame = ttk.Frame(self.simulation_tab, padding="10")
        frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # シミュレーションパラメータ
        sim_params_frame = ttk.LabelFrame(frame, text="Simulation Parameters", padding="5")
        sim_params_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5)

        sim_params = [
            ("Time step (sec):", "time_step_entry", "0.1"),
            ("Max simulation time (sec):", "max_sim_time_entry", "10.0"),
            ("Acceleration jerk (G):", "acc_jerk_entry", "1.0"),
            ("Deceleration jerk (G):", "dec_jerk_entry", "2.5")
        ]

        for i, (label, attr, default) in enumerate(sim_params):
            ttk.Label(sim_params_frame, text=label).grid(column=0, row=i, sticky=tk.W, pady=5)
            entry = ttk.Entry(sim_params_frame, width=10)
            entry.grid(column=1, row=i, pady=5, padx=5)
            entry.insert(0, default)
            setattr(self, attr, entry)

        # ファイル選択と実行ボタン
        button_frame = ttk.Frame(frame)
        button_frame.grid(column=0, row=1, sticky=(tk.W, tk.E), pady=10)

        ttk.Button(button_frame, text="Select Input & Run Simulation", 
                   command=self.select_input_file).grid(column=0, row=0, padx=5)

        # プログレス表示
        progress_frame = ttk.LabelFrame(frame, text="Progress", padding="5")
        progress_frame.grid(column=0, row=2, sticky=(tk.W, tk.E), pady=5)

        self.sim_progress = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.sim_progress.grid(column=0, row=0, pady=5, padx=5)

        # 結果表示
        results_frame = ttk.LabelFrame(frame, text="Results", padding="5")
        results_frame.grid(column=0, row=3, sticky=(tk.W, tk.E), pady=5)

        self.sim_result = tk.Text(results_frame, height=10, width=60)
        self.sim_result.grid(column=0, row=0, sticky=(tk.W, tk.E), pady=5, padx=5)

    def init_asil_tab(self):
        """ASIL Calculation タブの初期化"""
        frame = ttk.Frame(self.asil_tab, padding="10")
        frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # 操作ボタン
        buttons_frame = ttk.Frame(frame)
        buttons_frame.grid(column=0, row=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(buttons_frame, text="Run ASIL Calculation", 
                   command=self.run_asil_calculation).grid(column=0, row=0, padx=5)

        # プログレスバー
        progress_frame = ttk.LabelFrame(frame, text="Progress", padding="5")
        progress_frame.grid(column=0, row=1, sticky=(tk.W, tk.E), pady=5)

        self.asil_progress = ttk.Progressbar(progress_frame, length=300, mode='determinate')
        self.asil_progress.grid(column=0, row=0, pady=5, padx=5)

        # 結果表示
        results_frame = ttk.LabelFrame(frame, text="Results", padding="5")
        results_frame.grid(column=0, row=2, sticky=(tk.W, tk.E), pady=5)

        self.asil_result = tk.Text(results_frame, height=10, width=60)
        self.asil_result.grid(column=0, row=0, sticky=(tk.W, tk.E), pady=5, padx=5)

    def init_visualization_tab(self):
        """Visualization タブの初期化"""
        frame = ttk.Frame(self.visual_tab, padding="10")
        frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # データ読み込みボタン
        ttk.Button(frame, text="Load CSV File", 
                   command=self.load_csv_file).grid(column=0, row=0, pady=10)

        # パラメータ選択
        param_frame = ttk.LabelFrame(frame, text="ASIL Map Parameters", padding="5")
        param_frame.grid(column=0, row=1, sticky=(tk.W, tk.E), pady=5)

        # X軸パラメータ
        ttk.Label(param_frame, text="X-axis:").grid(column=0, row=0, padx=5, pady=5)
        self.x_param = ttk.Combobox(param_frame, state="readonly")
        self.x_param.grid(column=1, row=0, padx=5, pady=5)

        # Y軸パラメータ
        ttk.Label(param_frame, text="Y-axis:").grid(column=0, row=1, padx=5, pady=5)
        self.y_param = ttk.Combobox(param_frame, state="readonly")
        self.y_param.grid(column=1, row=1, padx=5, pady=5)

        # カラーマップ選択
        ttk.Label(param_frame, text="Color map:").grid(column=0, row=2, padx=5, pady=5)
        self.color_map = ttk.Combobox(param_frame, state="readonly", 
                                     values=list(self.asil_map_generator.color_maps.keys()))
        self.color_map.grid(column=1, row=2, padx=5, pady=5)
        self.color_map.set('1')

        # マップ生成ボタン
        ttk.Button(frame, text="Generate ASIL Map", 
                   command=self.generate_asil_map).grid(column=0, row=2, pady=10)

        # 結果表示
        results_frame = ttk.LabelFrame(frame, text="Results", padding="5")
        results_frame.grid(column=0, row=3, sticky=(tk.W, tk.E), pady=5)

        self.visual_result = tk.Text(results_frame, height=10, width=60)
        self.visual_result.grid(column=0, row=0, sticky=(tk.W, tk.E), pady=5, padx=5)
    
    def add_weight_entry(self):
        """新しい重量入力フィールドを追加"""
        index = len(self.weight_entries)
        frame = ttk.Frame(self.weight_frame)
        frame.grid(column=0, row=index+1, sticky=(tk.W, tk.E), pady=2)
        
        entry = ttk.Entry(frame, width=10)
        entry.grid(column=0, row=0, padx=5)
        
        delete_btn = ttk.Button(frame, text="×", width=3,
                            command=lambda: self.remove_weight_entry(frame, entry))
        delete_btn.grid(column=1, row=0, padx=5)
        
        self.weight_entries.append(entry)

    def remove_weight_entry(self, frame, entry):
        """重量入力フィールドを削除"""
        frame.destroy()
        self.weight_entries.remove(entry)

    def generate_data(self):
        """データ生成を実行し、CSVファイルに保存する"""
        try:
            # Weight値の取得
            weights = [float(entry.get()) for entry in self.weight_entries if entry.get()]
            if not weights:
                messagebox.showwarning("Warning", "Please add at least one weight value")
                return

            user_input = {
                'weight': weights,
                'rtime': [float(self.rtime_entry.get())],
                'vset_start': float(self.vset_start.get()),
                'vset_end': float(self.vset_end.get()),
                'vset_step': float(self.vset_step.get()),
                'tset_start': float(self.tset_start.get()),
                'tset_end': float(self.tset_end.get()),
                'tset_step': float(self.tset_step.get()),
                'accset_start': float(self.accset_start.get()),
                'accset_end': float(self.accset_end.get()),
                'accset_step': float(self.accset_step.get()),
                'evasiveset': [float(entry.get()) for entry in self.evasive_entries]
            }
            self.generated_data = self.data_generator.generate_data(user_input)
            
            output_dir = os.path.join('data', 'input')
            os.makedirs(output_dir, exist_ok=True)
            
            self.output_path = os.path.join(output_dir, "accel_in.csv")
            
            functions.save_data_to_csv(self.generated_data, self.output_path)
            
            message = f"Data generated: {len(self.generated_data)} records\nSaved to: {self.output_path}"
            self.data_gen_result.insert(tk.END, message + "\n")
            self.status_text.delete('1.0', tk.END)
            self.status_text.insert('1.0', "Data generation completed")
            
        except ValueError as e:
            error_message = f"エラーが発生しました: {e}"
            self.data_gen_result.insert(tk.END, error_message + "\n")
            messagebox.showerror("Error", error_message)
        except IOError as e:
            error_message = f"ファイルの書き込みに失敗しました: {e}"
            self.data_gen_result.insert(tk.END, error_message + "\n")
            messagebox.showerror("Error", error_message)

    def run_simulations(self, input_file):
        """シミュレーションを実行し、結果をCSVファイルに保存する"""
        config = {
            'time_step': float(self.time_step_entry.get()),
            'max_simulation_time': float(self.max_sim_time_entry.get()),
            'acceleration_jerk': float(self.acc_jerk_entry.get()) * 9.81,
            'deceleration_jerk': float(self.dec_jerk_entry.get()) * 9.81,
        }

        output_file = os.path.join('data', 'output', 'simulation_results.csv')
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        try:
            with open(input_file, 'r', encoding='utf-8-sig') as infile:
                reader = csv.DictReader(infile)
                total_rows = sum(1 for _ in infile) - 1  # ヘッダー行を除外
                infile.seek(0)
                data = list(reader)

            self.sim_progress["maximum"] = total_rows
            self.sim_progress["value"] = 0
            
            results = []
            for i, row in enumerate(data):
                sim_engine = SimulationEngine(config)
                sim_engine.load_data(row)
                sim_engine.run_simulation()
                results.append((row, sim_engine.get_results()))
                self.sim_progress["value"] = i + 1
                self.root.update_idletasks()

            # 結果をファイルに書き込み
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
                fieldnames = list(data[0].keys())
                result_fieldnames = ['衝突有無', '衝突時刻', '衝突位置', '有効衝突速度']
                scenario_fieldnames = ['回避無し', 'C0', 'C1', 'C2']
                
                for scenario in scenario_fieldnames:
                    for result in result_fieldnames:
                        fieldnames.append(f'{result}[{scenario}]')

                writer = csv.DictWriter(outfile, fieldnames=fieldnames)
                writer.writeheader()

                for original_row, sim_results in results:
                    output_row = original_row.copy()
                    for scenario in scenario_fieldnames:
                        for result in result_fieldnames:
                            output_row[f'{result}[{scenario}]'] = sim_results[scenario][result]
                    writer.writerow(output_row)

            message = f"Simulation completed. Results saved to {output_file}"
            self.sim_result.insert(tk.END, message + "\n")
            self.status_text.delete('1.0', tk.END)
            self.status_text.insert('1.0', "Simulation completed")

        except Exception as e:
            error_message = f"シミュレーション中にエラーが発生しました: {e}"
            self.sim_result.insert(tk.END, error_message + "\n")
            messagebox.showerror("Error", error_message)
    
    def select_input_file(self):
        """入力ファイルを選択し、シミュレーションを実行する"""
        input_file = filedialog.askopenfilename(
            title="Select input CSV file",
            filetypes=[("CSV files", "*.csv")],
            initialdir=os.path.join(os.getcwd(), 'data', 'input')
        )
        if input_file:
            self.sim_result.delete('1.0', tk.END)
            self.sim_result.insert(tk.END, f"Selected file: {input_file}\nStarting simulation...\n")
            self.run_simulations(input_file)
        else:
            self.sim_result.insert(tk.END, "No file selected. Simulation cancelled.\n")

    def run_asil_calculation(self):
        """ASIL計算を実行するためのファイル選択ダイアログを表示し、計算を開始する"""
        input_file = filedialog.askopenfilename(
            title="Select simulation results CSV file",
            filetypes=[("CSV files", "*.csv")],
            initialdir=os.path.join(os.getcwd(), 'data', 'output')
        )
        if input_file:
            output_file = input_file.replace('.csv', '_with_asil.csv')
            self.calculate_and_save_asil(input_file, output_file)
        else:
            self.asil_result.insert(tk.END, "No file selected. ASIL calculation cancelled.\n")

    def calculate_and_save_asil(self, input_file: str, output_file: str):
        """ASIL計算を実行し、結果をCSVファイルに保存する"""
        asil_calculator = ASILCalculator()
        
        try:
            # CSVファイルからデータを読み込む
            with open(input_file, 'r', encoding='utf-8-sig') as infile:
                reader = csv.DictReader(infile)
                data = list(reader)
            
            if not data:
                self.asil_result.insert(tk.END, f"警告: 入力ファイル {input_file} にデータがありません。\n")
                return

            # ASIL計算を行う
            total_rows = len(data)
            self.asil_progress["maximum"] = total_rows
            self.asil_progress["value"] = 0

            for i, row in enumerate(data):
                try:
                    asil_results = asil_calculator.calculate(row)
                    row.update(asil_results)
                except Exception as e:
                    self.asil_result.insert(tk.END, f"行 {i+1} の処理中にエラーが発生しました: {str(e)}\n")
                    continue
                self.asil_progress["value"] = i + 1
                self.root.update_idletasks()
            
            # 結果を新しいCSVファイルに書き込む
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', newline='', encoding='utf-8-sig') as outfile:
                writer = csv.DictWriter(outfile, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

            message = f"ASIL calculation completed. Results saved to {output_file}"
            self.asil_result.insert(tk.END, message + "\n")
            self.status_text.delete('1.0', tk.END)
            self.status_text.insert('1.0', "ASIL calculation completed")
        
        except Exception as e:
            error_message = f"ASIL計算中にエラーが発生しました: {str(e)}"
            self.asil_result.insert(tk.END, error_message + "\n")
            messagebox.showerror("Error", error_message)

    def load_csv_file(self):
        file_path = filedialog.askopenfilename(
            title="Select CSV file for ASIL Map",
            filetypes=[("CSV files", "*.csv")],
            initialdir=os.path.join(os.getcwd(), 'data', 'output')
        )
        if file_path:
            try:
                self.csv_data = pd.read_csv(file_path)
                self.csv_columns = list(self.csv_data.columns)
                self.x_param['values'] = self.csv_columns
                self.y_param['values'] = self.csv_columns
                self.visual_result.insert(tk.END, f"CSV file loaded: {file_path}\n")
                messagebox.showinfo("Success", "CSV file loaded successfully")
            except Exception as e:
                error_message = f"Error loading CSV file: {str(e)}"
                self.visual_result.insert(tk.END, error_message + "\n")
                messagebox.showerror("Error", error_message)

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

        try:
            result = self.asil_map_generator.generate_asil_map(
                data=self.csv_data,
                x_param=x_param,
                y_param=y_param,
                color_choice=color_choice,
                output_dir=output_dir
            )
            self.visual_result.insert(tk.END, f"ASIL Map Generation Result:\n{result}\n")
            self.status_text.delete('1.0', tk.END)
            self.status_text.insert('1.0', "ASIL map generation completed")
        except Exception as e:
            error_message = f"Error generating ASIL map: {str(e)}"
            self.visual_result.insert(tk.END, error_message + "\n")
            messagebox.showerror("Error", error_message)

def main():
    root = tk.Tk()
    app = ADASSimulationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()