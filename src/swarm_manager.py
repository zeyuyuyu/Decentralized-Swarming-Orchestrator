import numpy as np
from typing import List

class SwarmManager:
    def __init__(self, num_drones: int, arena_size: tuple):
        self.num_drones = num_drones
        self.arena_size = arena_size
        self.drone_positions = np.random.uniform(0, arena_size, (num_drones, 2))
        self.drone_velocities = np.random.uniform(-1, 1, (num_drones, 2))

    def update_positions(self, dt: float):
        self.drone_positions += self.drone_velocities * dt
        self.drone_positions = np.clip(self.drone_positions, 0, self.arena_size)

    def calculate_cohesion(self) -> np.ndarray:
        centroid = np.mean(self.drone_positions, axis=0)
        return centroid - self.drone_positions

    def calculate_separation(self) -> np.ndarray:
        distances = np.linalg.norm(self.drone_positions[:, None, :] - self.drone_positions[None, :, :], axis=-1)
        repulsion = np.sum(self.drone_positions[:, None, :] - self.drone_positions[None, :, :] / (distances[:, :, None] ** 2 + 1e-6), axis=1)
        return repulsion

    def calculate_alignment(self) -> np.ndarray:
        return np.mean(self.drone_velocities, axis=0) - self.drone_velocities

    def optimize_swarm(self):
        cohesion = self.calculate_cohesion()
        separation = self.calculate_separation()
        alignment = self.calculate_alignment()

        self.drone_velocities += cohesion * 0.1 + separation * 0.5 + alignment * 0.2
        self.update_positions(0.1)

    def get_drone_positions(self) -> List[tuple]:
        return [(x, y) for x, y in self.drone_positions]
