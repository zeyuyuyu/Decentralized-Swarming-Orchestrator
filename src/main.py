import os
import random
import time
from typing import List

from swarm_agent import SwarmAgent
from task_scheduler import TaskScheduler

class DecentralizedSwarmOrchestrator:
    def __init__(self, num_agents: int, task_queue: List[dict]):
        self.agents = [SwarmAgent(f'agent_{i}') for i in range(num_agents)]
        self.task_scheduler = TaskScheduler(task_queue)

    def run(self):
        while True:
            for agent in self.agents:
                if not agent.is_busy():
                    task = self.task_scheduler.get_next_task()
                    if task:
                        agent.execute_task(task)
            time.sleep(1)

if __name__ == '__main__':
    num_agents = int(os.getenv('NUM_AGENTS', '10'))
    task_queue = [
        {'id': 1, 'description': 'Process sensor data'},
        {'id': 2, 'description': 'Analyze customer behavior'},
        {'id': 3, 'description': 'Train machine learning model'},
        {'id': 4, 'description': 'Generate report'}
    ]

    orchestrator = DecentralizedSwarmOrchestrator(num_agents, task_queue)
    orchestrator.run()