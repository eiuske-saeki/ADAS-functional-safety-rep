from typing import Dict, Any

class ASILCalculator:
    def __init__(self):
        self.severity_thresholds = {
            '車両衝突_前進': {
                'S1': 24,
                'S2': 40,
                'S3': float('inf')
            },
            '車両衝突_後進': {
                'S1': 30,
                'S2': 40,
                'S3': float('inf')
            },
            '歩行者衝突': {
                'S1': 10,
                'S2': 24,
                'S3': float('inf')
            },
            '歩行者RunOver': {
                'S1': 4,
                'S2': 16,
                'S3': float('inf')
            }
        }
        self.exposure_thresholds = {
            'headway_time': {
                'E2': 2.0,
                'E3': 1.0,
                'E4': 0.0
            }
        }
        self.controllability_levels = {
            'C0': 0,
            'C1': 0.4,
            'C2': 0.8,
            'C3': 1.0
        }

    def calculate(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
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
        collision_type = collision_data.get('衝突タイプ', '')
        impact_velocity = collision_data.get('有効衝突速度[C0]', 0)

        if impact_velocity == 0:
            return 'S0'

        if collision_type in self.severity_thresholds:
            thresholds = self.severity_thresholds[collision_type]
            for level, threshold in sorted(thresholds.items(), key=lambda x: x[1]):
                if impact_velocity <= threshold:
                    return level
        
        return 'S3'

    def calculate_exposure(self, scenario_data: Dict[str, Any]) -> str:
        e_value = self._calculate_exposure_value(scenario_data)
        return f'E{e_value}'

    def _calculate_exposure_value(self, scenario_data: Dict[str, Any]) -> int:
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
        e_combination = {
            (4, 4): 4, (4, 3): 3, (4, 2): 2, (4, 1): 1,
            (3, 4): 3, (3, 3): 2, (3, 2): 1, (3, 1): 1,
            (2, 4): 2, (2, 3): 1, (2, 2): 1, (2, 1): 1,
            (1, 4): 1, (1, 3): 1, (1, 2): 1, (1, 1): 1
        }
        return e_combination.get((e1, e2), 1)

    def _get_headway_time_exposure(self, scenario_data: Dict[str, Any]) -> int:
        headway_time = scenario_data.get('車間時間[sec]', 0)
        thresholds = self.exposure_thresholds['headway_time']
        for level, threshold in sorted(thresholds.items(), key=lambda x: x[1], reverse=True):
            if headway_time > threshold:
                return int(level[1])
        return 4

    def _get_runover_exposure(self, scenario_data: Dict[str, Any]) -> int:
        return 3 if scenario_data.get('衝突タイプ') == '歩行者RunOver' else 4

    def _get_direction_exposure(self, scenario_data: Dict[str, Any]) -> int:
        return 2 if scenario_data.get('進行方向') == '後進' else 4

    def calculate_controllability(self, vehicle_data: Dict[str, Any]) -> str:
        deceleration = vehicle_data.get('回避行動パラメータ[C0]', 0)
        for level, threshold in sorted(self.controllability_levels.items(), key=lambda x: x[1]):
            if deceleration <= threshold:
                return level
        return 'C3'

    def determine_asil(self, s: str, e: str, c: str) -> str:
        s_value = int(s[1]) if s != 'S0' else 0
        e_value = int(e[1])
        c_value = int(c[1]) if c != 'C0' else 0

        if s_value == 0 or e_value == 0 or c_value == 0:
            return 'QM'

        total = s_value + e_value + c_value

        if total == 10:
            return 'D'
        elif total == 9:
            return 'C'
        elif total == 8:
            return 'B'
        elif total == 7:
            return 'A'
        else:
            return 'QM'