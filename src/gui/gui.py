import tkinter as tk
from tkinter import ttk

class ADASGui:
    def __init__(self, root):
        self.root = root
        self.root.title("ADAS Functional Safety Simulation Tool")

        self.frame = ttk.Frame(self.root, padding="10 10 10 10")
        self.frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Simulation Type
        ttk.Label(self.frame, text="Simulation Type:").grid(column=0, row=0, sticky=tk.W)
        self.simulation_type = ttk.Combobox(self.frame, values=["意図しない加速", "意図しない減速", "意図しない操舵"])
        self.simulation_type.grid(column=1, row=0, pady=5)

        # Precondition
        ttk.Label(self.frame, text="Precondition:").grid(column=0, row=1, sticky=tk.W)
        self.precondition = ttk.Combobox(self.frame, values=["両車一定速", "両者停止", "対歩行者"])
        self.precondition.grid(column=1, row=1, pady=5)

        # Speed Range
        ttk.Label(self.frame, text="Speed Range (0-140 km/h, 5 km/h steps):").grid(column=0, row=2, sticky=tk.W)
        self.speed_range = ttk.Scale(self.frame, from_=0, to=140, orient=tk.HORIZONTAL)
        self.speed_range.grid(column=1, row=2, pady=5)

        # Acceleration G Range
        ttk.Label(self.frame, text="Acceleration G Range (0-1.0 G, 0.025 G steps):").grid(column=0, row=3, sticky=tk.W)
        self.acceleration_g = ttk.Scale(self.frame, from_=0, to=1.0, orient=tk.HORIZONTAL)
        self.acceleration_g.grid(column=1, row=3, pady=5)

        # Own Vehicle Status
        ttk.Label(self.frame, text="Own Vehicle Status:").grid(column=0, row=4, sticky=tk.W)
        self.own_vehicle_weight = ttk.Entry(self.frame)
        self.own_vehicle_weight.grid(column=1, row=4, pady=5)
        ttk.Label(self.frame, text="Weight (kg)").grid(column=2, row=4, sticky=tk.W)

        self.own_vehicle_accel_jerk = ttk.Entry(self.frame)
        self.own_vehicle_accel_jerk.grid(column=1, row=5, pady=5)
        ttk.Label(self.frame, text="Accel Jerk (m/s^3)").grid(column=2, row=5, sticky=tk.W)

        self.own_vehicle_decel_jerk = ttk.Entry(self.frame)
        self.own_vehicle_decel_jerk.grid(column=1, row=6, pady=5)
        ttk.Label(self.frame, text="Decel Jerk (m/s^3)").grid(column=2, row=6, sticky=tk.W)

        # Other Vehicle Status
        ttk.Label(self.frame, text="Other Vehicle Status:").grid(column=0, row=7, sticky=tk.W)
        self.other_vehicle_weight = ttk.Entry(self.frame)
        self.other_vehicle_weight.grid(column=1, row=7, pady=5)
        ttk.Label(self.frame, text="Weight (kg)").grid(column=2, row=7, sticky=tk.W)

        self.other_vehicle_accel_jerk = ttk.Entry(self.frame)
        self.other_vehicle_accel_jerk.grid(column=1, row=8, pady=5)
        ttk.Label(self.frame, text="Accel Jerk (m/s^3)").grid(column=2, row=8, sticky=tk.W)

        self.other_vehicle_decel_jerk = ttk.Entry(self.frame)
        self.other_vehicle_decel_jerk.grid(column=1, row=9, pady=5)
        ttk.Label(self.frame, text="Decel Jerk (m/s^3)").grid(column=2, row=9, sticky=tk.W)

        # Avoidance Action
        ttk.Label(self.frame, text="Avoidance Action:").grid(column=0, row=10, sticky=tk.W)
        self.avoidance_action = ttk.Combobox(self.frame, values=["ブレーキ", "ステアリング", "アクセル"])
        self.avoidance_action.grid(column=1, row=10, pady=5)

        # Run Simulation Button
        self.run_simulation_button = ttk.Button(self.frame, text="Run Simulation", command=self.run_simulation)
        self.run_simulation_button.grid(column=1, row=11, pady=5)

        # Text area for logs
        self.log_text = tk.Text(self.frame, wrap='word', height=20, width=80)
        self.log_text.grid(column=0, row=12, columnspan=3, pady=10)

    def run_simulation(self):
        # Collect the selected values and log them
        simulation_type = self.simulation_type.get()
        precondition = self.precondition.get()
        speed = self.speed_range.get()
        acceleration_g = self.acceleration_g.get()
        own_weight = self.own_vehicle_weight.get()
        own_accel_jerk = self.own_vehicle_accel_jerk.get()
        own_decel_jerk = self.own_vehicle_decel_jerk.get()
        other_weight = self.other_vehicle_weight.get()
        other_accel_jerk = self.other_vehicle_accel_jerk.get()
        other_decel_jerk = self.other_vehicle_decel_jerk.get()
        avoidance_action = self.avoidance_action.get()

        self.log_text.insert(tk.END, f"Simulation Type: {simulation_type}\n")
        self.log_text.insert(tk.END, f"Precondition: {precondition}\n")
        self.log_text.insert(tk.END, f"Speed: {speed} km/h\n")
        self.log_text.insert(tk.END, f"Acceleration G: {acceleration_g} G\n")
        self.log_text.insert(tk.END, f"Own Vehicle Weight: {own_weight} kg\n")
        self.log_text.insert(tk.END, f"Own Vehicle Accel Jerk: {own_accel_jerk} m/s^3\n")
        self.log_text.insert(tk.END, f"Own Vehicle Decel Jerk: {own_decel_jerk} m/s^3\n")
        self.log_text.insert(tk.END, f"Other Vehicle Weight: {other_weight} kg\n")
        self.log_text.insert(tk.END, f"Other Vehicle Accel Jerk: {other_accel_jerk} m/s^3\n")
        self.log_text.insert(tk.END, f"Other Vehicle Decel Jerk: {other_decel_jerk} m/s^3\n")
        self.log_text.insert(tk.END, f"Avoidance Action: {avoidance_action}\n")
        self.log_text.insert(tk.END, "Simulation running...\n")

        # Placeholder for the actual simulation logic
        # Simulation logic should be implemented here
        self.log_text.insert(tk.END, "Simulation completed.\n")

if __name__ == "__main__":
    root = tk.Tk()
    app = ADASGui(root)
    root.mainloop()
