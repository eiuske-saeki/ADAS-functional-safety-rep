# src/simulation/simulation_engine.py

import csv
import os
from typing import Dict, List, Any
from enum import Enum
from src.models.vehicle_model import Vehicle
from src.utils import functions
from src.asil_calculation.asil_calculator import ASILCalculator

class ScenarioType(Enum):
    UNINTENDED_ACCELERATION = "unintended_acceleration"

class SimulationEngine:
    def __init__(self, config: Dict[str, Any]):
        # マジヤバイね！ここでシミュレーションの初期設定をバリバリやっちゃうよ～
        # 車両データ、時間設定、加速度設定とかをゲットして、シミュレーションの準備を整えちゃう！
        # configには時間刻み、最大シミュレーション時間、加速度変化率（jerk）とかが入ってるんだって～超細かい！
        self.config = config
        self.leading_vehicle: Vehicle = None  # 先行車のデータ、まだセットしてないからNoneだよ
        self.following_vehicle: Vehicle = None  # 後続車のデータも同じくNone
        self.results: Dict[str, Any] = {}  # シミュレーション結果を入れる箱、今は空っぽ！
        self.current_scenario = ScenarioType.UNINTENDED_ACCELERATION  # 今回は「意図しない加速」シナリオ
        self.time = 0.0  # シミュレーション時間、スタート地点は0秒だよ
        self.time_step = config['time_step']  # 時間の刻み幅、細かく見たいからちっちゃい値にしてるの
        self.max_simulation_time = config['max_simulation_time']  # シミュレーションの最大時間、ここまで来たら終了！
        self.acceleration_jerk = config['acceleration_jerk']  # 加速度の変化率、急加速するときに使うよ
        self.deceleration_jerk = config['deceleration_jerk']  # 減速度の変化率、急ブレーキのときはコレ
        self.log_data: Dict[str, List[List[str]]] = {}  # ログデータを入れる場所、後で見返すときに超便利！
        self.record_id: str = ""  # シミュレーションの記録ID、これで結果を識別するの
        self.reaction_time: float = 0.0  # ドライバーの反応時間、リアルな感じを出すためにあるんだって
        self.evasive_actions: Dict[str, float] = {}  # 回避行動のパラメータ、いろんなパターンを試すよ
        self.asil_calculator = ASILCalculator()

    def load_data(self, data: Dict[str, Any]):
        # ウェーイ！車のデータをゲットして、シミュレーションの準備をしちゃうよ～
        # 辞書型のdataから必要な情報を取り出して、車両オブジェクトを作っちゃう！
        self.record_id = data.get('No', 'unknown')  # シミュレーションの記録ID、ない場合は'unknown'
        self.leading_vehicle = Vehicle({
            'mass': float(data['先行車質量[kg]']),  # 先行車の重さ
            'initial_velocity': float(data['先行車速度[km/h]']) / 3.6,  # 初速をm/sに変換
            'initial_position': float(data['車間距離[m]'])  # 初期位置は車間距離と同じ
        })
        self.following_vehicle = Vehicle({
            'mass': float(data['後続車質量[kg]']),  # 後続車の重さ
            'initial_velocity': float(data['後続車速度[km/h]']) / 3.6,  # 初速をm/sに変換
            'max_acceleration': float(data['後続車加速度[G]']) * 9.81,  # 最大加速度をm/s^2に変換
            'initial_position': 0  # 後続車の初期位置は0m地点
        })
        self.reaction_time = float(data['後続車反応時間[sec]'])  # ドライバーの反応時間
        # 回避行動のパラメータをセット、G単位からm/s^2に変換
        self.evasive_actions = {
            '回避無し': float(data['回避行動パラメータ[回避無し]']) * 9.81,
            'C0': float(data['回避行動パラメータ[C0]']) * 9.81,
            'C1': float(data['回避行動パラメータ[C1]']) * 9.81,
            'C2': float(data['回避行動パラメータ[C2]']) * 9.81
        }
        self.log_data = {key: [] for key in self.evasive_actions.keys()}  # ログデータの初期化

    def run_simulation(self):
        # ヤバイ！シミュレーションを全力で回しちゃうよ～
        # 4つのシナリオ（回避無し、C0, C1, C2）を順番に実行するの
        scenarios = ['回避無し', 'C0', 'C1', 'C2']
        self.results = {}
        self.log_data = {scenario: [] for scenario in scenarios}  # ログデータのリセット、超イケてる！

        # まずは「回避無し」のシナリオをバリバリやっちゃうよ
        # これは基準になるシナリオだから、必ず実行するの
        self.results['回避無し'] = self.run_single_scenario(
            self.evasive_actions['回避無し'], '回避無し')

        # C0, C1, C2の順番でシミュレーションするよ～超クール！
        for scenario in scenarios[1:]:  # '回避無し'はスキップ
            self.results[scenario] = self.run_single_scenario(
                self.evasive_actions[scenario], scenario)
            if self.results[scenario]['衝突有無'] == 'なし':
                # マジ卍！衝突回避できたら残りはスキップしちゃうよ
                # 例えばC0で回避できたら、C1とC2はやらなくていいってこと
                for remaining_scenario in scenarios[scenarios.index(scenario)+1:]:
                    self.results[remaining_scenario] = {
                        '衝突有無': '不要',  # 衝突回避済みだから、これ以上のシナリオは不要
                        '衝突時刻': 'N/A',
                        '衝突位置': 'N/A',
                        '有効衝突速度': 'N/A'
                    }
                    # スキップしたシナリオもログに残すよ～超親切！
                    self.log_data[remaining_scenario].append(['不要'] * 11)  # ログの列数に合わせて調整
                break  # このbreakで残りのシナリオをスキップ

        self.write_log_to_csv()  # シミュレーション後にログを書き込むよ～超忘れずに！

    def run_single_scenario(self, max_deceleration: float, scenario_name: str):
        # 個別のシナリオをガンガン走らせちゃうよ～
        # max_decelerationは最大減速度、scenario_nameはシナリオの名前（回避無し、C0, C1, C2）
        self.reset_simulation()  # シミュレーションをリセット、新鮮な状態からスタート！
        collision_detected = False  # 衝突検出フラグ、最初はFalseだよ
        reaction_time_passed = False  # 反応時間経過フラグ、最初はFalseだよ
        while not self.is_simulation_complete(collision_detected, scenario_name):
            if not reaction_time_passed:
                self.apply_unintended_acceleration()  # 意図しない加速を適用
                if self.time >= self.reaction_time:
                    reaction_time_passed = True  # 反応時間が過ぎたらフラグをTrueに
            else:
                self.apply_evasive_action(max_deceleration)  # 回避行動を適用
            
            self.update_vehicle_states()  # 車両の状態を更新
            collision_detected = self.check_collision()  # 衝突チェック
            self.log_state(scenario_name, reaction_time_passed)  # 状態をログに記録
            self.time += self.time_step  # 時間を進める
        
        return self.get_scenario_results(collision_detected)  # シナリオの結果を返す

    def apply_unintended_acceleration(self):
        # ウッキウキで加速しちゃうよ～でも限界はあるからね！
        # 加速度を徐々に上げていくけど、最大加速度を超えないようにするの
        new_acceleration = min(
            self.following_vehicle.acceleration + self.acceleration_jerk * self.time_step,
            self.following_vehicle.max_acceleration
        )
        self.following_vehicle.acceleration = new_acceleration

    def apply_evasive_action(self, max_deceleration: float):
        # マジヤバイ！急ブレーキかけちゃうよ～でも限界はあるからね！
        # 減速度を徐々に上げていくけど、最大減速度を超えないようにするの
        new_deceleration = min(
            self.following_vehicle.deceleration + self.deceleration_jerk * self.time_step,
            max_deceleration
        )
        self.following_vehicle.deceleration = new_deceleration

    def update_vehicle_states(self):
        # 車の状態をアップデートしちゃうよ～超リアルタイム！
        # 位置と速度を更新するの。先行車と後続車、両方ね！
        self.leading_vehicle.update_state(self.time_step)
        net_acceleration = self.following_vehicle.acceleration - self.following_vehicle.deceleration
        self.following_vehicle.velocity += net_acceleration * self.time_step
        self.following_vehicle.position += self.following_vehicle.velocity * self.time_step

    def check_collision(self) -> bool:
        # ヤバイ！衝突してないかチェックしちゃうよ～
        # 後続車の位置が先行車の位置を追い越したら衝突ってこと！
        return self.following_vehicle.position >= self.leading_vehicle.position

    def log_state(self, scenario_name: str, reaction_time_passed: bool):
        # 超細かく状態をログに残しちゃうよ～後で見返すの超便利！
        # 時間、シナリオ名、反応時間経過フラグ、両車の位置と速度、加減速度、車間距離、相対速度をログに記録
        log_entry = [
            f"{self.time:.3f}",  # 時間（秒）
            scenario_name,  # シナリオ名
            "1" if reaction_time_passed else "0",  # 反応時間経過フラグ
            f"{self.leading_vehicle.position:.2f}",  # 先行車の位置（m）
            f"{self.leading_vehicle.velocity * 3.6:.2f}",  # 先行車の速度（km/h）
            f"{self.following_vehicle.position:.2f}",  # 後続車の位置（m）
            f"{self.following_vehicle.velocity * 3.6:.2f}",  # 後続車の速度（km/h）
            f"{self.following_vehicle.acceleration:.2f}",  # 後続車の加速度（m/s^2）
            f"{self.following_vehicle.deceleration:.2f}",  # 後続車の減速度（m/s^2）
            f"{self.leading_vehicle.position - self.following_vehicle.position:.2f}",  # 車間距離（m）
            f"{(self.following_vehicle.velocity - self.leading_vehicle.velocity) * 3.6:.2f}"  # 相対速度（km/h）
        ]
        self.log_data[scenario_name].append(log_entry)

    def write_log_to_csv(self):
        # ログをCSVファイルに書き込んじゃうよ～超便利！
        # 各シナリオのログを1つのCSVファイルにまとめて保存するの
        output_dir = os.path.join('data', 'output', 'logs')
        os.makedirs(output_dir, exist_ok=True)  # 出力ディレクトリがなければ作成
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
        # シナリオの結果をゲットしちゃうよ～衝突したかどうかで超重要！
        # 衝突があった場合と、なかった場合で返す情報が違うんだ
        if collision_detected:
            return {
                '衝突有無': 'あり',  # 衝突しちゃったってこと
                '衝突時刻': self.time,  # 衝突が起きた時間
                '衝突位置': self.following_vehicle.position,  # 衝突が起きた位置
                '有効衝突速度': abs(self.following_vehicle.velocity - self.leading_vehicle.velocity) * 3.6  # 衝突時の相対速度（km/h）
            }
        else:
            return {
                '衝突有無': 'なし',  # 衝突しなかったってこと
                '衝突時刻': 'N/A',  # 衝突なしだから時刻はNot Applicable
                '衝突位置': 'N/A',  # 衝突なしだから位置もNot Applicable
                '有効衝突速度': 'N/A'  # 衝突なしだから速度もNot Applicable
            }

    def is_simulation_complete(self, collision_detected: bool, scenario_name: str) -> bool:
        # シミュレーション終了？マジで重要なチェックだよ～
        # 3つの条件のどれかが満たされたら終了だよ
        return (collision_detected or  # 衝突が検出されたら終了
                self.time >= self.max_simulation_time or  # 最大シミュレーション時間に達したら終了
                (scenario_name != '回避無し' and self.is_safe_state_after_evasion()))  # 回避行動後に安全状態になったら終了（ただし「回避無し」シナリオ以外）

    def is_safe_state_after_evasion(self):
        # 回避後に安全な状態になったかチェックするよ～超安心！
        # 反応時間が過ぎていて、かつ後続車の速度が先行車より遅くなっていれば安全と判断
        return (self.time > self.reaction_time and 
                self.following_vehicle.velocity < self.leading_vehicle.velocity)

    def reset_simulation(self):
        # シミュレーションをリセットしちゃうよ～新鮮な気分で再スタート！
        # 時間をゼロに戻して、車両の状態も初期状態に戻すの
        self.time = 0.0
        self.following_vehicle.reset()
        self.leading_vehicle.reset()

    def get_results(self) -> Dict[str, Any]:
        # 全シナリオの結果をまとめてゲットしちゃうよ～超便利！
        # 「回避無し」「C0」「C1」「C2」の4つのシナリオの結果をまとめて返すの
        return {
            '回避無し': self.results['回避無し'],
            'C0': self.results['C0'],
            'C1': self.results['C1'],
            'C2': self.results['C2']
        }