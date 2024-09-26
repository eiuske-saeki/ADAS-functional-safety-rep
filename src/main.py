import tkinter as tk
from tkinter import ttk
import sys
import os


from src.data_generation.data_generator import DataGenerator
from src.utils import functions

class ADASSimulationApp:
    def __init__(self, root):
        self.root = root
        self.data_generator = DataGenerator()
        self.init_ui()

    def init_ui(self):
        self.root.title('ADAS Functional Safety Simulation Tool')
        self.root.geometry('800x600')

        frame = ttk.Frame(self.root, padding="10")
        frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Weight input
        ttk.Label(frame, text="Weight (comma-separated):").grid(column=0, row=0, sticky=tk.W, pady=5)
        self.weight_entry = ttk.Entry(frame)
        self.weight_entry.grid(column=1, row=0, pady=5)
        self.weight_entry.insert(0, "50,55,2500")

        # Reaction time input
        ttk.Label(frame, text="Reaction time:").grid(column=0, row=1, sticky=tk.W, pady=5)
        self.rtime_entry = ttk.Entry(frame)
        self.rtime_entry.grid(column=1, row=1, pady=5)
        self.rtime_entry.insert(0, "1.2")

        # Velocity set input
        ttk.Label(frame, text="Velocity set (start, end, step):").grid(column=0, row=2, sticky=tk.W, pady=5)
        self.vset_entry = ttk.Entry(frame)
        self.vset_entry.grid(column=1, row=2, pady=5)
        self.vset_entry.insert(0, "0.0,140,5.0")

        # Time set input
        ttk.Label(frame, text="Time set (start, end, step):").grid(column=0, row=3, sticky=tk.W, pady=5)
        self.tset_entry = ttk.Entry(frame)
        self.tset_entry.grid(column=1, row=3, pady=5)
        self.tset_entry.insert(0, "0.6,6.0,0.2")

        # Acceleration set input
        ttk.Label(frame, text="Acceleration set (start, end, step):").grid(column=0, row=4, sticky=tk.W, pady=5)
        self.accset_entry = ttk.Entry(frame)
        self.accset_entry.grid(column=1, row=4, pady=5)
        self.accset_entry.insert(0, "0.01,1.17,0.02")

        # Evasive set input
        ttk.Label(frame, text="Evasive set (comma-separated):").grid(column=0, row=5, sticky=tk.W, pady=5)
        self.evasiveset_entry = ttk.Entry(frame)
        self.evasiveset_entry.grid(column=1, row=5, pady=5)
        self.evasiveset_entry.insert(0, "0,0.4,0.8,1.0")

        generate_button = ttk.Button(frame, text='Generate Data', command=self.generate_data)
        generate_button.grid(column=1, row=6, pady=5)

        self.result_label = ttk.Label(frame, text='Results will be displayed here')
        self.result_label.grid(column=0, row=7, columnspan=2, pady=5)

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
            data = self.data_generator.generate_data(user_input)
            
            output_dir = os.path.join('data', 'input')
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, "accel_in.csv")
            
            functions.save_data_to_csv(data, output_path)
            
            self.result_label.config(text=f"Data generated: {len(data)} records\nSaved to: {output_path}")
            print(f"データを {output_path} に保存しました。チェックしてみてください！")
        except ValueError as e:
            error_message = f"エラーが発生しました: {e}"
            self.result_label.config(text=error_message)
            print(error_message)
        except IOError as e:
            error_message = f"ファイルの書き込みに失敗しました: {e}"
            self.result_label.config(text=error_message)
            print(error_message)


def main():
    root = tk.Tk()
    app = ADASSimulationApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()