# src/models/vehicle_model.py

class Vehicle:
    def __init__(self, config: dict):
        # マジヤバイ！車の基本データをセットアップしちゃうよ～
        self.mass = config['mass']  # 車の重さ、重いと止まりにくいんだって！
        self.initial_position = config['initial_position']  # 最初の位置、スタート地点ってこと！
        self.position = self.initial_position  # 現在の位置、最初はスタート地点と同じ
        self.initial_velocity = config['initial_velocity']  # 初速、ゼロからスタートじゃないかも！
        self.velocity = self.initial_velocity  # 現在の速度、最初は初速と同じ
        self.acceleration = 0.0  # 加速度、最初はゼロ、これから変わるよ！
        self.deceleration = 0.0  # 減速度、最初はゼロ、ブレーキかけたら変わるよ！
        self.max_acceleration = config.get('max_acceleration', 0.0)  # 最大加速度、車によって違うんだって！

    def update_state(self, time_step: float):
        # 超ヤバイ！車の状態をリアルタイムでアップデートしちゃうよ～
        net_acceleration = self.acceleration - self.deceleration  # 正味の加速度、加速とブレーキの差し引き
        self.velocity += net_acceleration * time_step  # 速度の変化、物理の公式そのまんま！
        self.position += self.velocity * time_step  # 位置の変化、これも物理の公式！

    def reset(self):
        # ウッキウキ！車の状態を最初からやり直しちゃうよ～
        self.acceleration = 0.0  # 加速度をリセット、止まった状態から始めるの
        self.deceleration = 0.0  # 減速度もリセット、ブレーキかけてない状態
        self.velocity = self.initial_velocity  # 速度を初期値に戻す、スタート時点の速さに
        self.position = self.initial_position  # 位置も初期値に戻す、スタート地点に戻るってこと！