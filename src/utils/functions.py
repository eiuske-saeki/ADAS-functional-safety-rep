def set_data(min_value: float, max_value: float, diff: float, data_set: list) -> list:
    """
    指定された範囲と間隔でデータセットを生成します。

    :param min_value: 最小値
    :param max_value: 最大値
    :param diff: 間隔
    :param data_set: データを格納するリスト
    :return: 生成されたデータセット
    """
    tmp = min_value
    while tmp < (max_value + (diff / 2)):
        data_set.append(f'{tmp:.2f}')
        tmp += diff
    return data_set  # この行を追加

def kph_to_mps(kph: float) -> float:
    """
    km/h から m/s に変換します。

    :param kph: km/h単位の速度
    :return: m/s単位の速度
    """
    return kph / 3.6

def is_valid_distance_between_cars(v: float, t: float) -> bool:
    """
    車間距離が有効かどうかを判定します。

    :param v: 速度 (km/h)
    :param t: 車間時間 (秒)
    :return: 車間距離が有効な場合True、そうでない場合False
    """
    l = (v / 3.6) * t
    if t <= 0.5 or (v <= 25.0 and t <= 0.9) or (l < 6.25 and v > 25.0):
        return False
    return True

def multiply_list_elements(lst: list, factor: float) -> list:
    """
    リストの各要素に係数を掛けます。

    :param lst: 入力リスト
    :param factor: 掛ける係数
    :return: 各要素に係数を掛けた新しいリスト
    """
    return [x * factor for x in lst]

# 以下の関数はdatamake_old.pyには直接現れていませんが、
# 他の部分で使用されている可能性があるため、念のため含めています。

def save_data_to_csv(data: list, filename: str = "output.csv"):
    """
    データをCSVファイルに保存します。

    :param data: 保存するデータのリスト
    :param filename: 出力ファイル名
    """
    import csv
    with open(filename, "w", encoding="utf-8-sig", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)