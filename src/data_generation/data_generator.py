import os
from typing import Dict, Any, List
from src.utils import functions

class DataGenerator:
    def __init__(self):
        pass

    def generate_data(self, user_input: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        ユーザー入力に基づいてシミュレーションデータを生成します。

        :param user_input: ユーザーが指定したパラメータ
        :return: 生成されたデータのリスト
        """
        data = []
        weight = user_input['weight']
        rtime = user_input['rtime']
        vset, tset, accset = [], [], []

        functions.set_data(user_input['vset_start'], user_input['vset_end'], user_input['vset_step'], vset)
        functions.set_data(user_input['tset_start'], user_input['tset_end'], user_input['tset_step'], tset)
        functions.set_data(user_input['accset_start'], user_input['accset_end'], user_input['accset_step'], accset)

        evasiveset = user_input['evasiveset']
        no = 1

        for kg in weight:
            for rt in rtime:
                for v in vset:
                    if float(kg) < 100 and float(v) > 60.0:
                        continue

                    for t in tset:
                        if float(kg) >= 100 and float(v) >= 10.0 and not functions.is_valid_distance_between_cars(float(v), float(t)):
                            continue

                        if float(kg) < 100:
                            min_time = {
                                0.0: 1.2, 5.0: 2.6, 10.0: 2.0, 15.0: 2.0, 20.0: 2.0,
                                25.0: 2.2, 30.0: 2.2, 35.0: 2.4, 40.0: 2.6, 45.0: 2.8,
                                50.0: 2.8, 55.0: 3.0, 60.0: 3.2
                            }
                            if float(v) in min_time and float(t) < min_time[float(v)]:
                                continue
                        elif float(v) == 0.0 and float(t) < 1.8:
                            continue

                        for acc in accset:
                            d = self._create_data_point(no, kg, v, acc, rt, t, evasiveset)
                            data.append(d)
                            no += 1
                            
        return data

    def _create_data_point(self, no: float, kg: float, v: float, acc: float, rt: float, t: float, evasiveset: List[float]) -> Dict[str, Any]:
        """
        単一のデータポイントを作成します。

        :param no: データポイント番号
        :param kg: 車両質量
        :param v: 速度
        :param acc: 加速度
        :param rt: 反応時間
        :param t: 車間時間
        :param evasiveset: 回避行動パラメータ
        :return: 生成されたデータポイント
        """
        return {
            "No": float(no),
            "先行車質量[kg]": float(kg),
            "先行車速度[km/h]": 0.0 if float(kg) < 100 else float(v),
            "先行車減速度[G]": 0.0,
            "後続車質量[kg]": 1500.0,
            "後続車速度[km/h]": float(v),
            "後続車加速度[G]": float(acc),
            "後続車反応時間[sec]": float(rt),
            "車間時間[sec]": float(t),
            "車間距離[m]": float(f'{functions.kph_to_mps(float(v)) * float(t):.2f}') if float(v) > 0.0 else float(f'{functions.kph_to_mps(6) * float(t):.2f}'),
            "回避行動": "後続車減速",
            "回避行動パラメータ[回避無し]": float(evasiveset[0]),
            "衝突有無[回避無し]" : None,
            "衝突位置[回避無し]" : None,
            "衝突時刻[回避無し]" : None,
            "有効衝突速度[回避無し]" : None, 
            "回避行動パラメータ[C0]": float(evasiveset[1]),
            "衝突有無[C0]" : None,
            "衝突位置[C0]" : None,
            "衝突時刻[C0]" : None,
            "有効衝突速度[C0]" : None,
            "回避行動パラメータ[C1]": float(evasiveset[2]),
            "衝突有無[C1]" : None,
            "衝突位置[C1]" : None,
            "衝突時刻[C1]" : None,
            "有効衝突速度[C1]" : None,
            "回避行動パラメータ[C2]": float(evasiveset[3]),
            "衝突有無[C2]" : None,
            "衝突位置[C2]" : None,
            "衝突時刻[C2]" : None,
            "有効衝突速度[C2]" : None,
            "E": None,
            "C": None,
            "S": None,
            "コメント": "意図しない加速"
        }

    def main(self):
        """
        DataGeneratorのメイン実行関数。
        ユーザー入力を設定し、データを生成してCSVファイルに保存します。
        """
        user_input = {
            'weight': [50, 55, 2500],
            'rtime': [1.2],
            'vset_start': 0.0, 'vset_end': 140, 'vset_step': 5.0,
            'tset_start': 0.6, 'tset_end': 6.0, 'tset_step': 0.2,
            'accset_start': 0.01, 'accset_end': 1.17, 'accset_step': 0.02,
            'evasiveset': [0, 0.4, 0.8, 1.0]
        }
        data = self.generate_data(user_input)
        
        # 出力ディレクトリを作成（存在しない場合）
        output_dir = os.path.join('data', 'output')
        os.makedirs(output_dir, exist_ok=True)
        
        # 出力ファイルのフルパスを作成
        output_path = os.path.join(output_dir, "accel_in.csv")
        
        # functions.pyのsave_data_to_csv関数を使用
        functions.save_data_to_csv(data, output_path)
        print(f"Data saved to {output_path}")

# スクリプトが直接実行された場合にmain関数を呼び出す
if __name__ == "__main__":
    data_generator = DataGenerator()
    data_generator.main()