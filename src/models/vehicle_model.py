# src/models/vehicle_model.py

class Vehicle:
    def __init__(self, config: dict):
        self.mass = config['mass']
        self.initial_position = config['initial_position']
        self.position = self.initial_position
        self.initial_velocity = config['initial_velocity']
        self.velocity = self.initial_velocity
        self.acceleration = 0.0
        self.deceleration = 0.0
        self.max_acceleration = config.get('max_acceleration', 0.0)

    def update_state(self, time_step: float):
        net_acceleration = self.acceleration - self.deceleration
        self.velocity += net_acceleration * time_step
        self.position += self.velocity * time_step

    def reset(self):
        self.acceleration = 0.0
        self.deceleration = 0.0
        self.velocity = self.initial_velocity
        self.position = self.initial_position