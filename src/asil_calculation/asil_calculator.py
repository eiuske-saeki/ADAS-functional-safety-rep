from typing import Dict, Any

class ASILCalculator:
    def __init__(self):
        # ヤバイ！超重要な閾値をセットアップしちゃうよ～
        self.severity_thresholds = {
            '車両衝突_前進': {
                'S1': 24,  # 24km/h以下ならS1、ちょっと怖いレベル
                'S2': 40,  # 40km/h以下ならS2、かなりヤバイレベル
                'S3': float('inf')  # それ以上はS3、マジでヤバイレベル
            },
            '車両衝突_後進': {
                'S1': 30,  # 後ろ向きは前より少し基準が緩いんだって
                'S2': 40,
                'S3': float('inf')
            },
            '歩行者衝突': {
                'S1': 10,  # 歩行者には厳しめの基準
                'S2': 24,
                'S3': float('inf')
            },
            '歩行者RunOver': {
                'S1': 4,   # 轢過はマジでヤバイから超厳しい基準
                'S2': 16,
                'S3': float('inf')
            }
        }
        self.exposure_thresholds = {
            'headway_time': {
                'E2': 2.0,  # 2秒以上の車間時間ならE2
                'E3': 1.0,  # 1秒以上ならE3
                'E4': 0.0   # それ以下はE4、超ヤバイ頻度
            }
        }
        self.controllability_levels = {
            'C0': 0,    # 完全制御可能
            'C1': 0.4,  # ほぼ制御可能
            'C2': 0.8,  # ちょっと制御難しい
            'C3': 1.0   # 制御超難しい
        }

    def calculate(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        # マジヤバイ！ASILの計算をフルコースで実行しちゃうよ～
        s_value = self.calculate_severity(simulation_results)
        e_value = self.calculate_exposure(simulation_results)
        c_value = self.calculate_controllability(simulation_results)
        asil = self.determine_asil(s_value, e_value, c_value)
        
        return {
            'ASIL': asil,
            'S': s_value,
            'E': e_value,
            'C': c_value
        }

    def calculate_severity(self, collision_data: Dict[str, Any]) -> str:
        # 衝突の厳しさを計算しちゃうよ～どのくらいヤバイか見てみよう！
        collision_type = collision_data.get('衝突タイプ', '')
        impact_velocity = collision_data.get('有効衝突速度[C0]', 0)

        if impact_velocity == 0:
            return 'S0'  # 衝突なしならS0、超ラッキー！

        if collision_type in self.severity_thresholds:
            thresholds = self.severity_thresholds[collision_type]
            for level, threshold in sorted(thresholds.items(), key=lambda x: x[1]):
                if impact_velocity <= threshold:
                    return level  # 該当するレベルを返す
        
        return 'S3'  # どれにも当てはまらなければS3、マジでヤバイ！

    def calculate_exposure(self, scenario_data: Dict[str, Any]) -> str:
        # 露出度を計算しちゃうよ～どのくらいの頻度で起こりそう？
        e_value = self._calculate_exposure_value(scenario_data)
        return f'E{e_value}'

    def _calculate_exposure_value(self, scenario_data: Dict[str, Any]) -> int:
        # 露出度の詳細計算、いろんな要素を考慮しちゃう！
        e_values = [
            self._get_headway_time_exposure(scenario_data),
            self._get_runover_exposure(scenario_data),
            self._get_direction_exposure(scenario_data)
        ]
        
        final_e_value = e_values[0]
        for e_value in e_values[1:]:
            final_e_value = self._combine_e_values(final_e_value, e_value)
        
        return final_e_value

    def _combine_e_values(self, e1: int, e2: int) -> int:
        # E値を組み合わせちゃうよ～複雑だけどルールがあるの！
        e_combination = {
            (4, 4): 4, (4, 3): 3, (4, 2): 2, (4, 1): 1,
            (3, 4): 3, (3, 3): 2, (3, 2): 1, (3, 1): 1,
            (2, 4): 2, (2, 3): 1, (2, 2): 1, (2, 1): 1,
            (1, 4): 1, (1, 3): 1, (1, 2): 1, (1, 1): 1
        }
        return e_combination.get((e1, e2), 1)

    def _get_headway_time_exposure(self, scenario_data: Dict[str, Any]) -> int:
        # 車間時間でE値を決めちゃうよ～近すぎると危ないからね！
        headway_time = scenario_data.get('車間時間[sec]', 0)
        thresholds = self.exposure_thresholds['headway_time']
        for level, threshold in sorted(thresholds.items(), key=lambda x: x[1], reverse=True):
            if headway_time > threshold:
                return int(level[1])
        return 4  # どれにも当てはまらなければE4、超頻繁に起こりそう！

    def _get_runover_exposure(self, scenario_data: Dict[str, Any]) -> int:
        # 轢過のE値、マジでヤバイから特別扱い！
        return 3 if scenario_data.get('衝突タイプ') == '歩行者RunOver' else 4

    def _get_direction_exposure(self, scenario_data: Dict[str, Any]) -> int:
        # 進行方向でE値変わるの！後ろ向きの方が珍しいからね
        return 2 if scenario_data.get('進行方向') == '後進' else 4

    def calculate_controllability(self, vehicle_data: Dict[str, Any]) -> str:
        # 制御可能性を計算しちゃうよ～どのくらい止められそう？
        deceleration = vehicle_data.get('回避行動パラメータ[C0]', 0)
        for level, threshold in sorted(self.controllability_levels.items(), key=lambda x: x[1]):
            if deceleration <= threshold:
                return level
        return 'C3'  # どれにも当てはまらなければC3、制御超難しい！

    def determine_asil(self, s: str, e: str, c: str) -> str:
        # 最終的なASILを決定しちゃうよ～S, E, Cの組み合わせで決まるの！
        s_value = int(s[1]) if s != 'S0' else 0
        e_value = int(e[1])
        c_value = int(c[1]) if c != 'C0' else 0

        if s_value == 0 or e_value == 0 or c_value == 0:
            return 'QM'  # どれかが0ならQM、一番軽いレベル

        total = s_value + e_value + c_value

        if total == 10:
            return 'D'  # 合計10ならD、マジでヤバイレベル！
        elif total == 9:
            return 'C'  # 合計9ならC、かなりヤバイレベル！
        elif total == 8:
            return 'B'  # 合計8ならB、ちょっとヤバイレベル！
        elif total == 7:
            return 'A'  # 合計7ならA、気をつけるレベル！
        else:
            return 'QM'  # それ以外はQM、でもちゃんと確認しようね！