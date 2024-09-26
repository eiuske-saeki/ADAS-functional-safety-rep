# src/data_generation/data_generator.py

import os
from typing import Dict, Any, List, Generator
from src.utils import functions

class DataGenerator:
    def __init__(self):
        pass
        # 何もないけど、これがないとクラスっぽくないからね～

    def generate_data(self, user_input: Dict[str, Any]) -> Generator[Dict[str, Any], None, None]:
        """
        ユーザー入力使ってシミュレーションデータをバリバリ作っちゃうよ～

        :param user_input: ユーザーが決めたパラメータ、超大事！
        :return: 作ったデータのジェネレータ、省メモリでイケてるでしょ？
        :raises ValueError: ユーザー入力がおかしかったらエラー出すよ～気をつけてね！
        """
        self._validate_user_input(user_input)  # まずは入力チェック、間違ってたらダメだからね！

        # パラメータをゲット、これでデータを作るよ～
        weight = user_input['weight']
        rtime = user_input['rtime']
        vset = self._generate_range(user_input['vset_start'], user_input['vset_end'], user_input['vset_step'])
        tset = self._generate_range(user_input['tset_start'], user_input['tset_end'], user_input['tset_step'])
        accset = self._generate_range(user_input['accset_start'], user_input['accset_end'], user_input['accset_step'])

        evasiveset = user_input['evasiveset']
        no = 1  # データのナンバリング、1から始まるよ～

        # ここからがメインのループ、全パターンを網羅しちゃうよ！
        for kg in weight:
            for rt in rtime:
                for v in vset:
                    if float(kg) < 100 and float(v) > 60.0:
                        continue  # この条件だとスキップ、現実的じゃないからね～

                    for t in tset:
                        if not self._is_valid_scenario(kg, v, t):
                            continue  # 無効なシナリオはスキップ、変なデータは作らないよ！

                        for acc in accset:
                            yield self._create_data_point(no, kg, v, acc, rt, t, evasiveset)
                            no += 1  # ナンバーを増やして次へ、どんどん作るよ～

    def _validate_user_input(self, user_input: Dict[str, Any]) -> None:
        """ユーザー入力をチェックしちゃうよ～間違ってたらダメだからね！"""
        required_keys = ['weight', 'rtime', 'vset_start', 'vset_end', 'vset_step',
                         'tset_start', 'tset_end', 'tset_step', 'accset_start',
                         'accset_end', 'accset_step', 'evasiveset']
        for key in required_keys:
            if key not in user_input:
                raise ValueError(f"ごめん！{key}が見つからないよ～入力してね！")

    def _generate_range(self, start: float, end: float, step: float) -> List[float]:
        """指定された範囲でリストを作っちゃうよ～超便利！"""
        return [round(float(x), 2) for x in functions.set_data(start, end, step, [])]

    def _is_valid_scenario(self, kg: float, v: float, t: float) -> bool:
        """このシナリオ、大丈夫？チェックしちゃうよ～"""
        if float(kg) >= 100 and float(v) >= 10.0 and not functions.is_valid_distance_between_cars(float(v), float(t)):
            return False  # 車間距離が不適切ならアウト！

        if float(kg) < 100:
            min_time = {
                0.0: 1.2, 5.0: 2.6, 10.0: 2.0, 15.0: 2.0, 20.0: 2.0,
                25.0: 2.2, 30.0: 2.2, 35.0: 2.4, 40.0: 2.6, 45.0: 2.8,
                50.0: 2.8, 55.0: 3.0, 60.0: 3.2
            }
            if float(v) in min_time and float(t) < min_time[float(v)]:
                return False  # 最小車間時間を下回ってたらアウト！
        elif float(v) == 0.0 and float(t) < 1.8:
            return False  # 停止時の最小車間時間を下回ってたらアウト！

        return True  # 全部クリアしたらOK！

    def _create_data_point(self, no: int, kg: float, v: float, acc: float, rt: float, t: float, evasiveset: List[float]) -> Dict[str, Any]:
        """1つのデータポイントを作っちゃうよ～ここが肝心！"""
        return {
            "No": float(no),
            "先行車質量[kg]": float(kg),
            "先行車速度[km/h]": 0.0 if float(kg) < 100 else float(v),  # 歩行者なら速度0
            "先行車減速度[G]": 0.0,
            "後続車質量[kg]": 1500.0,  # 後続車の質量は固定
            "後続車速度[km/h]": float(v),
            "後続車加速度[G]": float(acc),
            "後続車反応時間[sec]": float(rt),
            "車間時間[sec]": float(t),
            "車間距離[m]": float(f'{functions.kph_to_mps(float(v)) * float(t):.2f}') if float(v) > 0.0 else float(f'{functions.kph_to_mps(6) * float(t):.2f}'),
            "回避行動": "後続車減速",
            "回避行動パラメータ[回避無し]": float(evasiveset[0]),
            "回避行動パラメータ[C0]": float(evasiveset[1]),
            "回避行動パラメータ[C1]": float(evasiveset[2]),
            "回避行動パラメータ[C2]": float(evasiveset[3]),
            "E": None,
            "C": None,
            "S": None,
            "コメント": "意図しない加速"
        }

    def main(self) -> None:
        """
        DataGeneratorのメイン関数だよ～ここから全部始まるの！
        ユーザー入力を設定して、データを作って、CSVファイルに保存しちゃうよ～
        """
        user_input = {
            'weight': [50, 55, 2500],  # 歩行者と車両の重さ
            'rtime': [1.2],  # 反応時間
            'vset_start': 0.0, 'vset_end': 140, 'vset_step': 5.0,  # 速度の範囲
            'tset_start': 0.6, 'tset_end': 6.0, 'tset_step': 0.2,  # 車間時間の範囲
            'accset_start': 0.01, 'accset_end': 1.17, 'accset_step': 0.02,  # 加速度の範囲
            'evasiveset': [0, 0.4, 0.8, 1.0]  # 回避行動のパラメータ
        }
        
        try:
            data = list(self.generate_data(user_input))  # データを生成
            
            output_dir = os.path.join('data', 'input')
            os.makedirs(output_dir, exist_ok=True)  # 出力ディレクトリを作成
            
            output_path = os.path.join(output_dir, "accel_in.csv")
            
            functions.save_data_to_csv(data, output_path)  # CSVファイルに保存
            print(f"データを {output_path} に保存したよ～チェックしてみてね！")
        except ValueError as e:
            print(f"エラーが出ちゃった！: {e}")
        except IOError as e:
            print(f"ファイルに書き込めなかった！ごめんね！: {e}")

if __name__ == "__main__":
    data_generator = DataGenerator()
    data_generator.main()