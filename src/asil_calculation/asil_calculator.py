from typing import Dict, Any

class ASILCalculator:
    def __init__(self):
        self.severity_thresholds = {
            '車両衝突_前進': {1: 24, 2: 40, 3: float('inf')},
            '車両衝突_後進': {1: 30, 2: 40, 3: float('inf')},
            '歩行者衝突': {1: 10, 2: 24, 3: float('inf')},
            '歩行者RunOver': {1: 4, 2: 16, 3: float('inf')}
        }
        self.exposure_thresholds = {
            'headway_time': {2: 2.0, 3: 1.0, 4: 0.0}
        }
        self.controllability_levels = {0: 0, 1: 0.4, 2: 0.8, 3: 1.0}

    def calculate(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        s_value = self.calculate_severity(simulation_results)
        e_value = self.calculate_exposure(simulation_results)
        c_value = self.calculate_controllability(simulation_results)
        asil = self.determine_asil(s_value, e_value, c_value)
        
        simulation_results.update({
            'ASIL': asil,
            'S': s_value,
            'E': e_value,
            'C': c_value
        })
        
        return simulation_results

    def calculate_severity(self, collision_data: Dict[str, Any]) -> int:
        collision_type = collision_data.get('衝突タイプ', '')
        impact_velocity = self.safe_float(collision_data.get('有効衝突速度[C0]', 0))

        if impact_velocity == 0:
            return 0  # 衝突なしなら0

        if collision_type in self.severity_thresholds:
            thresholds = self.severity_thresholds[collision_type]
            for level, threshold in sorted(thresholds.items()):
                if impact_velocity <= threshold:
                    return level
        
        return 3  # 最大値

    def calculate_exposure(self, scenario_data: Dict[str, Any]) -> int:
        e_values = [
            self._get_headway_time_exposure(scenario_data),
            self._get_runover_exposure(scenario_data),
            self._get_direction_exposure(scenario_data)
        ]
        
        return min(e_values)  # 最小値を返す

    def _get_headway_time_exposure(self, scenario_data: Dict[str, Any]) -> int:
        headway_time = self.safe_float(scenario_data.get('車間時間[sec]', 0))
        thresholds = self.exposure_thresholds['headway_time']
        for level, threshold in sorted(thresholds.items(), reverse=True):
            if headway_time > threshold:
                return level
        return 4  # 最大値

    def _get_runover_exposure(self, scenario_data: Dict[str, Any]) -> int:
        return 3 if scenario_data.get('衝突タイプ') == '歩行者RunOver' else 4

    def _get_direction_exposure(self, scenario_data: Dict[str, Any]) -> int:
        return 2 if scenario_data.get('進行方向') == '後進' else 4

    def calculate_controllability(self, vehicle_data: Dict[str, Any]) -> int:
        deceleration = self.safe_float(vehicle_data.get('回避行動パラメータ[C0]', 0))
        for level, threshold in sorted(self.controllability_levels.items()):
            if deceleration <= threshold:
                return level
        return 3  # 最大値

    def determine_asil(self, s: int, e: int, c: int) -> str:
        if s == 0 or e == 0 or c == 0:
            return 'QM'

        total = s + e + c

        if total >= 10:
            return 'D'
        elif total == 9:
            return 'C'
        elif total == 8:
            return 'B'
        elif total == 7:
            return 'A'
        else:
            return 'QM'

    @staticmethod
    def safe_float(value: Any) -> float:
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0