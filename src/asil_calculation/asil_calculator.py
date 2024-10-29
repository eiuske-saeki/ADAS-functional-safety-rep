from typing import Dict, Any
import logging

class ASILCalculator:
    def __init__(self):
        self.severity_thresholds = {
            '車両衝突_前進': {
                0: 4,    # S0: 0-4 km/h
                1: 20,   # S1: 4-20 km/h
                2: 40,   # S2: 20-40 km/h
                3: float('inf')  # S3: 40 km/h以上
            },
            '車両衝突_後進': {
                0: 4,    # S0: 0-4 km/h
                1: 20,   # S1: 4-20 km/h
                2: 40,   # S2: 20-40 km/h
                3: float('inf')  # S3: 40 km/h以上
            },
            '歩行者衝突': {
                1: 10,   # S1: 0-10 km/h
                2: 30,   # S2: 10-30 km/h
                3: float('inf')  # S3: 30 km/h以上
            },
            '歩行者RunOver': {
                2: 8,    # S2: 0-8 km/h
                3: float('inf')  # S3: 8 km/h以上
            }
        }
        
        self.required_fields = {
            'basic': [
                '後続車速度[km/h]',
                '車間距離[m]',
                '車間時間[sec]',
                '衝突タイプ',
                '進行方向',
                '衝突有無[C0]',
                '衝突有無[C1]',
                '衝突有無[C2]',
                '有効衝突速度[回避無し]'
            ],
            'ranges': {
                '後続車速度[km/h]': (0, 200),  # 0-200 km/h
                '車間距離[m]': (0, 100),       # 0-100 m
                '車間時間[sec]': (0, 10),      # 0-10 sec
                '有効衝突速度[回避無し]': (0, 200)  # 0-200 km/h
            }
        }
        
        self.exposure_calculators = {
            'headway_time': self._get_headway_time_exposure,
            'runover': self._get_runover_exposure,
            'direction': self._get_direction_exposure
        }
        self.active_exposure_calculators = set([
            'headway_time', 'runover', 'direction'
        ])

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        入力データのバリデーションを行う
        
        Args:
            data: 検証するシナリオデータ
        
        Returns:
            bool: データが有効な場合True、無効な場合False
        """
        # 必須フィールドの存在チェック
        for field in self.required_fields['basic']:
            if field not in data:
                logging.error(f"必須フィールド '{field}' が見つかりません")
                return False
            if data[field] is None:
                logging.error(f"フィールド '{field}' の値がNullです")
                return False

        # 数値フィールドの範囲チェック
        for field, (min_val, max_val) in self.required_fields['ranges'].items():
            try:
                value = self.safe_float(data[field])
                if not min_val <= value <= max_val:
                    logging.error(f"フィールド '{field}' の値 {value} が有効範囲 ({min_val}-{max_val}) 外です")
                    return False
            except ValueError as e:
                logging.error(f"フィールド '{field}' の値の変換に失敗しました: {e}")
                return False

        # 衝突有無フィールドの値チェック
        valid_collision_values = {'あり', 'なし', '不要'}
        for field in ['衝突有無[C0]', '衝突有無[C1]', '衝突有無[C2]']:
            if data[field] not in valid_collision_values:
                logging.error(f"フィールド '{field}' の値 '{data[field]}' が不正です")
                return False

        return True

    def calculate(self, simulation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        ASILを計算する
        
        Args:
            simulation_results: シミュレーション結果データ
        
        Returns:
            Dict[str, Any]: ASIL計算結果を含むデータ
        """
        # データのバリデーション
        if not self.validate_data(simulation_results):
            logging.error("入力データが無効です")
            # デフォルト値を設定
            simulation_results.update({
                'ASIL': 'QM',
                'S': 0,
                'E': 4,
                'C': 3
            })
            return simulation_results

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
        """
        衝突の重大度（S値）を計算
        """
        collision_type = collision_data.get('衝突タイプ', '')
        impact_velocity = self.safe_float(collision_data.get('有効衝突速度[回避無し]', 0))

        if collision_type not in self.severity_thresholds:
            return 3  # 不明な衝突タイプの場合は最大値

        # 歩行者の場合、衝突があればS0にはならない
        if collision_type in ['歩行者衝突', '歩行者RunOver'] and impact_velocity > 0:
            thresholds = self.severity_thresholds[collision_type]
            for level, threshold in sorted(thresholds.items()):
                if impact_velocity <= threshold:
                    return level
            return 3

        # 車両衝突の場合
        thresholds = self.severity_thresholds[collision_type]
        if impact_velocity == 0:
            return 0  # 衝突なしの場合
        
        for level, threshold in sorted(thresholds.items()):
            if impact_velocity <= threshold:
                return level
        
        return 3  # 最大閾値を超えた場合

    def calculate_exposure(self, scenario_data: Dict[str, Any]) -> int:
        """
        シナリオデータに基づいてE値を計算
        
        掛け合わせルール：
        - E4は影響を与えない
        - E3は1段階下げる
        - E2は2段階下げる
        - E1は3段階下げる（ただしE1未満にはならない）
        
        Args:
            scenario_data: シナリオデータを含む辞書
        
        Returns:
            計算されたE値（1-4の整数）
        """
        exposure_values = []

        # アクティブな評価要素のみを使用してE値を収集
        for calculator_name in self.active_exposure_calculators:
            if calculator_name in self.exposure_calculators:
                calculator = self.exposure_calculators[calculator_name]
                try:
                    value = calculator(scenario_data)
                    exposure_values.append(value)
                except Exception as e:
                    logging.warning(f"Error calculating exposure for {calculator_name}: {e}")
                    continue

        if not exposure_values:
            return 4  # デフォルトは最も緩い値

        # E値の掛け合わせ計算
        final_e = 4  # 初期値は最大値
        for e_value in exposure_values:
            final_e = self._combine_e_values(final_e, e_value)

        return final_e

    def _combine_e_values(self, e1: int, e2: int) -> int:
        """
        2つのE値を掛け合わせて新しいE値を算出
        
        Args:
            e1: 1つ目のE値
            e2: 2つ目のE値
        
        Returns:
            掛け合わせ後のE値
        """
        # より小さいE値を基準に計算
        base_e = min(e1, e2)
        higher_e = max(e1, e2)

        if base_e == 4:
            return higher_e  # E4は影響を与えない
        elif base_e == 3:
            return max(1, higher_e - 1)  # 1段階下げる
        elif base_e == 2:
            return max(1, higher_e - 2)  # 2段階下げる
        else:  # base_e == 1
            return 1  # E1が含まれる場合は必ずE1
    def _get_headway_time_exposure(self, scenario_data: Dict[str, Any]) -> int:
        """
        車間距離/時間に基づくE値を計算
        停車時は車間距離、走行時は車間時間で判定
        """
        velocity = self.safe_float(scenario_data.get('後続車速度[km/h]', 0))
        
        # 停車時（velocity = 0）
        if velocity == 0:
            distance = self.safe_float(scenario_data.get('車間距離[m]', 0))
            return self._get_stationary_exposure(distance)
        
        # 走行時
        headway_time = self.safe_float(scenario_data.get('車間時間[sec]', 0))
        return self._get_moving_exposure(velocity, headway_time)

    def _get_stationary_exposure(self, distance: float) -> int:
        """
        停車時の車間距離に基づくE値を計算
        """
        if distance < 0.6 or distance >= 7.1:
            return 1
        elif (0.6 <= distance < 0.7) or (6.2 <= distance < 7.1):
            return 2
        elif (0.7 <= distance < 1.0) or (4.3 <= distance < 6.2):
            return 3
        elif 1.0 <= distance < 4.3:
            return 4
        return 4  # 想定外の値の場合は最も緩い評価

    def _get_moving_exposure(self, velocity: float, headway_time: float) -> int:
        """
        走行時の速度と車間時間に基づくE値を計算
        """
        if velocity <= 1.0:  # 1km/h以下は停車とみなす
            return self._get_stationary_exposure(headway_time)
        elif 1.0 < velocity <= 10.0:
            return self._get_low_speed_exposure(headway_time)
        elif 10.0 < velocity <= 70.0:
            return self._get_medium_speed_exposure(headway_time)
        else:  # velocity > 70.0
            return self._get_high_speed_exposure(headway_time)

    def _get_low_speed_exposure(self, headway_time: float) -> int:
        """
        低速(1-10kph)時の車間時間に基づくE値を計算
        """
        if headway_time < 0.8 or headway_time >= 6.9:
            return 1
        elif 6.1 <= headway_time < 6.9:
            return 2
        elif (0.8 <= headway_time < 2.0) or (4.9 <= headway_time < 6.1):
            return 3
        elif 2.0 <= headway_time < 4.9:
            return 4
        return 4  # 想定外の値の場合は最も緩い評価

    def _get_medium_speed_exposure(self, headway_time: float) -> int:
        """
        中速(10-70kph)時の車間時間に基づくE値を計算
        """
        if headway_time < 0.4 or headway_time >= 4.2:
            return 1
        elif 3.7 <= headway_time < 4.2:
            return 2
        elif (0.4 <= headway_time < 1.0) or (2.9 <= headway_time < 3.7):
            return 3
        elif 1.0 <= headway_time < 2.9:
            return 4
        return 4  # 想定外の値の場合は最も緩い評価

    def _get_high_speed_exposure(self, headway_time: float) -> int:
        """
        高速(70kph-)時の車間時間に基づくE値を計算
        """
        if headway_time < 0.4 or headway_time >= 2.3:
            return 1
        elif 2.0 <= headway_time < 2.3:
            return 2
        elif (0.4 <= headway_time < 0.7) or (1.7 <= headway_time < 2.0):
            return 3
        elif 0.7 <= headway_time < 1.7:
            return 4
        return 4  # 想定外の値の場合は最も緩い評価

    ######################################################3
    #もしかしたらトラックの場合の車間時間の計算も入れたほうが良い？    
    ######################################################
    
    
    
    def _get_runover_exposure(self, scenario_data: Dict[str, Any]) -> int:
        return 3 if scenario_data.get('衝突タイプ') == '歩行者RunOver' else 4

    def _get_direction_exposure(self, scenario_data: Dict[str, Any]) -> int:
        return 2 if scenario_data.get('進行方向') == '後進' else 4

    def calculate_controllability(self, vehicle_data: Dict[str, Any]) -> int:
        """
        制御可能性（C値）を計算
        各回避行動パラメータ（C0→C1→C2）の結果を順に確認し、
        衝突なしとなった最初のパラメータのCレベルを採用する
        全て衝突ありの場合はC3とする
        
        Args:
            vehicle_data: シミュレーション結果を含む辞書
        
        Returns:
            C値（0-3の整数）
        """
        # C0から順に確認
        if vehicle_data.get('衝突有無[C0]') == 'なし':
            return 0
        elif vehicle_data.get('衝突有無[C1]') == 'なし':
            return 1
        elif vehicle_data.get('衝突有無[C2]') == 'なし':
            return 2
        else:
            return 3

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