import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
import csv
import os
import traceback

class SimulationApp:
    def __init__(self, master):
        self.master = master
        master.title("Vehicle Simulation Tool")

        # パラメータ入力用のラベルとエントリ（デフォルト値を追加）
        self.create_label_entry("Maximum Acceleration (G):", 0, default_value=0.95)
        self.create_label_entry("Acceleration Jerk (G/s):", 1, default_value=5.56)
        self.create_label_entry("Maximum Deceleration (G):", 2, default_value=1.0)
        self.create_label_entry("Deceleration Jerk (G/s):", 3, default_value=2.5)
        self.create_label_entry("Initial Distance (m):", 4, default_value=18.06)
        self.create_label_entry("Initial Speed (km/h):", 5, default_value=25)
        self.create_label_entry("Deceleration Start Time (s):", 6, default_value=1.0)
        self.create_label_entry("Time Step (s):", 7, default_value=0.01)
        self.create_label_entry("Acceleration Threshold Speed (km/h):", 8, default_value=70.0)
        self.create_label_entry("New Maximum Acceleration (G):", 9, default_value=0.90)
        self.create_label_entry("Lead Vehicle Weight (kg):", 10, default_value=2500.0)
        self.create_label_entry("Following Vehicle Weight (kg):", 11, default_value=1500.0)

        # シミュレーション開始ボタン
        self.start_button = tk.Button(master, text="Start Simulation", command=self.run_simulation)
        self.start_button.grid(row=12, column=0, columnspan=2)

    def create_label_entry(self, text, row, default_value=""):
        label = tk.Label(self.master, text=text)
        label.grid(row=row, column=0, sticky=tk.W)
        entry = tk.Entry(self.master)
        entry.grid(row=row, column=1)
        entry.insert(0, str(default_value))  # デフォルト値を入力欄に挿入
        setattr(self, f"entry_{row}", entry)

    def run_simulation(self):
        try:
            # パラメータの取得と変換
            max_accel = float(self.entry_0.get()) * 9.80665  # Gをm/s^2に変換
            accel_jerk = float(self.entry_1.get()) * 9.80665  # G/sをm/s^3に変換
            max_decel = float(self.entry_2.get()) * 9.80665
            decel_jerk = float(self.entry_3.get()) * 9.80665
            distance = float(self.entry_4.get())
            initial_speed = float(self.entry_5.get()) / 3.6  # km/hをm/sに変換
            decel_start_time = float(self.entry_6.get())
            time_step = float(self.entry_7.get())
            accel_threshold_speed = float(self.entry_8.get()) / 3.6  # km/hをm/sに変換
            new_max_accel = float(self.entry_9.get()) * 9.80665  # Gをm/s^2に変換
            m1 = float(self.entry_10.get())  # 先行車の重量
            m2 = float(self.entry_11.get())  # 後続車の重量

            # 入力値のバリデーション
            if time_step <= 0:
                messagebox.showerror("Input Error", "Time Step must be greater than zero.")
                return
            if m1 <= 0 or m2 <= 0:
                messagebox.showerror("Input Error", "Vehicle weights must be greater than zero.")
                return

            # シミュレーションの初期化
            time = 0.0
            positions_lead = [0.0]
            positions_follow = [-distance]
            speeds_lead = [initial_speed]
            speeds_follow = [initial_speed]
            accel = 0.0
            decel = 0.0
            accelerations = [0.0]
            times = [0.0]

            current_max_accel = max_accel

            collision_occurred = False
            collision_time = 0.0  # collision_timeを初期化

            # データ保存用のリスト
            data_records = []

            # シミュレーションループ
            while True:
                try:
                    time += time_step
                    times.append(time)

                    # 先行車は一定速度
                    speeds_lead.append(speeds_lead[-1])
                    positions_lead.append(positions_lead[-1] + speeds_lead[-1] * time_step)

                    # 速度がしきい値に達したら最大加速度を変更
                    if speeds_follow[-1] >= accel_threshold_speed:
                        current_max_accel = new_max_accel

                    # 加速フェーズ
                    if accel < current_max_accel:
                        accel += accel_jerk * time_step
                        if accel > current_max_accel:
                            accel = current_max_accel
                    else:
                        accel = current_max_accel

                    # 減速開始
                    if time >= decel_start_time:
                        if decel < max_decel:
                            decel += decel_jerk * time_step
                            if decel > max_decel:
                                decel = max_decel
                        else:
                            decel = max_decel
                    else:
                        decel = 0.0

                    # 総加速度
                    net_accel = accel - decel
                    accelerations.append(net_accel)

                    # 後続車の速度と位置の更新
                    new_speed = speeds_follow[-1] + net_accel * time_step
                    speeds_follow.append(new_speed)
                    new_position = positions_follow[-1] + new_speed * time_step
                    positions_follow.append(new_position)

                    # データを保存
                    data_records.append({
                        "Time (s)": time,
                        "Lead Position (m)": positions_lead[-1],
                        "Following Position (m)": positions_follow[-1],
                        "Lead Speed (m/s)": speeds_lead[-1],
                        "Following Speed (m/s)": speeds_follow[-1],
                        "Acceleration (m/s^2)": net_accel  # '²' を '^2' に変更
                    })

                    # 衝突判定
                    if new_position >= positions_lead[-1]:
                        collision_occurred = True
                        collision_time = time
                        v1 = speeds_lead[-1]
                        v2 = speeds_follow[-1]
                        break

                    # 後続車の速度が先行車より小さくなった場合
                    if new_speed <= speeds_lead[-1]:
                        collision_occurred = False
                        collision_time = time
                        break

                    # シミュレーションが発散しないように制限
                    if time > 1000:
                        messagebox.showwarning("Simulation Warning", "Simulation time exceeded 1000 seconds.")
                        break

                except Exception as e:
                    # シミュレーションループ内での例外処理
                    messagebox.showerror("Simulation Error", f"An error occurred during simulation:\n{str(e)}")
                    traceback.print_exc()
                    return

            # 有効衝突速度の計算
            if collision_occurred:
                try:
                    # 衝突時の速度（m/s）
                    v1 = speeds_lead[-1]
                    v2 = speeds_follow[-1]

                    # 有効衝突速度の計算
                    d = (m1 * v2 + m2 * v1) / (m1 + m2)
                    effective_collision_speed = max(abs(v1 - d), abs(v2 - d))
                    effective_collision_speed *= 3.6  # m/sをkm/hに変換
                    # 結果の表示
                    messagebox.showinfo(
                        "Result",
                        f"Vehicles have collided.\n"
                        f"Time until collision: {collision_time:.2f} s\n"
                        f"Effective Collision Speed: {effective_collision_speed:.2f} m/s"
                    )
                except Exception as e:
                    messagebox.showerror("Calculation Error", f"An error occurred during collision calculation:\n{str(e)}")
                    traceback.print_exc()
                    return
            else:
                messagebox.showinfo(
                    "Result",
                    f"Following vehicle speed has dropped below lead vehicle speed.\n"
                    f"Time elapsed: {collision_time:.2f} s"
                )

            # データをCSVファイルに保存
            if data_records:
                self.save_data_to_csv(data_records)
            else:
                messagebox.showinfo("No Data", "No simulation data to save.")

            # 結果のプロット
            if times and positions_lead and positions_follow and speeds_follow and accelerations:
                self.plot_results(times, positions_lead, positions_follow, speeds_follow, accelerations)
            else:
                messagebox.showinfo("No Data", "No simulation data to plot.")

        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numerical values.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred:\n{str(e)}")
            traceback.print_exc()

    def plot_results(self, times, positions_lead, positions_follow, speeds_follow, accelerations):
        fig, axs = plt.subplots(3, 1, figsize=(10, 8))

        # 位置のプロット
        axs[0].plot(times, positions_lead, label="Lead Vehicle Position")
        axs[0].plot(times, positions_follow, label="Following Vehicle Position")
        axs[0].set_ylabel("Position (m)")
        axs[0].legend()

        # 速度のプロット
        axs[1].plot(times, speeds_follow, label="Following Vehicle Speed")
        axs[1].set_ylabel("Speed (m/s)")
        axs[1].legend()

        # 加速度のプロット
        axs[2].plot(times, accelerations, label="Following Vehicle Acceleration")
        axs[2].set_xlabel("Time (s)")
        axs[2].set_ylabel("Acceleration (m/s^2)")  # '²' を '^2' に変更
        axs[2].legend()

        plt.tight_layout()
        plt.show()

    def save_data_to_csv(self, data_records):
        # ファイル名を決定
        filename = "simulation_data.csv"
        # 同じ名前のファイルが存在する場合、番号を付けて保存
        i = 1
        while os.path.exists(filename):
            filename = f"simulation_data_{i}.csv"
            i += 1

        # CSVファイルにデータを保存
        try:
            with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    "Time (s)",
                    "Lead Position (m)",
                    "Following Position (m)",
                    "Lead Speed (m/s)",
                    "Following Speed (m/s)",
                    "Acceleration (m/s^2)"  # '²' を '^2' に変更
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for record in data_records:
                    writer.writerow(record)

            messagebox.showinfo("Data Saved", f"Simulation data saved to {filename}")
        except Exception as e:
            messagebox.showerror("File Error", f"An error occurred while saving data:\n{str(e)}")
            traceback.print_exc()

import sys

if __name__ == "__main__":
    root = tk.Tk()
    app = SimulationApp(root)
    root.mainloop()
