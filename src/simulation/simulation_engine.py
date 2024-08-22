# src/simulation/simulation_engine.py

import csv
import os
from typing import Dict, List, Any
from enum import Enum
from src.models.vehicle_model import Vehicle
from src.utils import functions

class ScenarioType(Enum):
    UNINTENDED_ACCELERATION = "unintended_acceleration"

class SimulationEngine:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.leading_vehicle: Vehicle = None
        self.following_vehicle: Vehicle = None
        self.results: Dict[str, Any] = {}
        self.current_scenario = ScenarioType.UNINTENDED_ACCELERATION
        self.time = 0.0
        self.time_step = config['time_step']
        self.max_simulation_time = config['max_simulation_time']
        self.acceleration_jerk = config['acceleration_jerk']
        self.deceleration_jerk = config['deceleration_jerk']
        self.log_data: Dict[str, List[List[str]]] = {}
        self.record_id: str = ""

    def load_data(self, data: Dict[str, Any]):
        self.record_id = data.get('No', 'unknown')
        self.leading_vehicle = Vehicle({
            'mass': float(data['先行車質量[kg]']),
            'initial_velocity': float(data['先行車速度[km/h]']) / 3.6,
            'initial_position': float(data['車間距離[m]'])
        })
        self.following_vehicle = Vehicle({
            'mass': float(data['後続車質量[kg]']),
            'initial_velocity': float(data['後続車速度[km/h]']) / 3.6,
            'max_acceleration': float(data['後続車加速度[G]']) * 9.81,
            'initial_position': 0
        })
        self.reaction_time = float(data['後続車反応時間[sec]'])
        self.evasive_actions = {
            '回避無し': float(data['回避行動パラメータ[回避無し]']) * 9.81,
            'C0': float(data['回避行動パラメータ[C0]']) * 9.81,
            'C1': float(data['回避行動パラメータ[C1]']) * 9.81,
            'C2': float(data['回避行動パラメータ[C2]']) * 9.81
        }
        self.log_data = {key: [] for key in self.evasive_actions.keys()}

    def run_simulation(self):
        self.results = {}
        for scenario, max_deceleration in self.evasive_actions.items():
            self.results[scenario] = self.run_single_scenario(max_deceleration, scenario)
        self.write_log_to_csv()

    def run_single_scenario(self, max_deceleration: float, scenario_name: str):
        self.time = 0.0
        self.following_vehicle.reset()
        self.leading_vehicle.reset()
        collision_detected = False
        reaction_time_passed = False
        
        while not self.is_simulation_complete(collision_detected):
            if not reaction_time_passed:
                self.apply_unintended_acceleration()
                if self.time >= self.reaction_time:
                    reaction_time_passed = True
            else:
                self.apply_evasive_action(max_deceleration)
            
            self.update_vehicle_states()
            collision_detected = self.check_collision()
            self.log_state(scenario_name, reaction_time_passed)
            self.time += self.time_step
        
        return self.get_scenario_results(collision_detected)

    def apply_unintended_acceleration(self):
        new_acceleration = min(
            self.following_vehicle.acceleration + self.acceleration_jerk * self.time_step,
            self.following_vehicle.max_acceleration
        )
        self.following_vehicle.acceleration = new_acceleration

    def apply_evasive_action(self, max_deceleration: float):
        new_deceleration = min(
            self.following_vehicle.deceleration + self.deceleration_jerk * self.time_step,
            max_deceleration
        )
        self.following_vehicle.deceleration = new_deceleration

    def update_vehicle_states(self):
        self.leading_vehicle.update_state(self.time_step)
        net_acceleration = self.following_vehicle.acceleration - self.following_vehicle.deceleration
        self.following_vehicle.velocity += net_acceleration * self.time_step
        self.following_vehicle.position += self.following_vehicle.velocity * self.time_step

    def check_collision(self) -> bool:
        return self.following_vehicle.position >= self.leading_vehicle.position

    def log_state(self, scenario_name: str, reaction_time_passed: bool):
        log_entry = [
            f"{self.time:.3f}",
            scenario_name,
            "1" if reaction_time_passed else "0",
            f"{self.leading_vehicle.position:.2f}",
            f"{self.leading_vehicle.velocity * 3.6:.2f}",
            f"{self.following_vehicle.position:.2f}",
            f"{self.following_vehicle.velocity * 3.6:.2f}",
            f"{self.following_vehicle.acceleration:.2f}",
            f"{self.following_vehicle.deceleration:.2f}",
            f"{self.leading_vehicle.position - self.following_vehicle.position:.2f}",
            f"{(self.following_vehicle.velocity - self.leading_vehicle.velocity) * 3.6:.2f}"
        ]
        self.log_data[scenario_name].append(log_entry)

    def write_log_to_csv(self):
        output_dir = os.path.join('data', 'output', 'logs')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f'simulation_log_record{self.record_id}.csv')

        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                '時間[s]', 'シナリオ', '反応時間経過', '先行車位置[m]', '先行車速度[km/h]',
                '後続車位置[m]', '後続車速度[km/h]', '後続車加速度[m/s^2]', '後続車減速度[m/s^2]',
                '車間距離[m]', '相対速度[km/h]'
            ])
            for scenario in self.evasive_actions.keys():
                writer.writerows(self.log_data[scenario])

    def get_scenario_results(self, collision_detected: bool) -> Dict[str, Any]:
        if collision_detected:
            return {
                '衝突有無': 'あり',
                '衝突時刻': self.time,
                '衝突位置': self.following_vehicle.position,
                '有効衝突速度': abs(self.following_vehicle.velocity - self.leading_vehicle.velocity) * 3.6
            }
        else:
            return {
                '衝突有無': 'なし',
                '衝突時刻': 'N/A',
                '衝突位置': 'N/A',
                '有効衝突速度': 'N/A'
            }

    def is_simulation_complete(self, collision_detected: bool) -> bool:
        return collision_detected or self.time >= self.max_simulation_time

    def get_results(self) -> Dict[str, Any]:
        return self.results