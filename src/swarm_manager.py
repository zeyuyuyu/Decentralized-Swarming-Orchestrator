import asyncio
import random
from typing import List

class SwarmNode:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.neighbors = set()
        self.state = 'IDLE'
        self.task = None

    def add_neighbor(self, neighbor_id: str):
        self.neighbors.add(neighbor_id)

    async def coordinate_swarm(self):
        while True:
            if self.state == 'IDLE':
                await self.find_task()
            elif self.state == 'WORKING':
                await self.execute_task()
            await asyncio.sleep(random.uniform(0.1, 1.0))

    async def find_task(self):
        # Communicate with neighbors to find a suitable task
        task_proposals = await asyncio.gather(*[self.get_task_proposal(neighbor) for neighbor in self.neighbors])
        best_task = max(task_proposals, key=lambda t: t.priority)
        if best_task.priority > 0:
            self.task = best_task
            self.state = 'WORKING'

    async def execute_task(self):
        # Execute the current task
        await self.task.execute()
        self.state = 'IDLE'
        self.task = None

    async def get_task_proposal(self, neighbor_id: str) -> Task:
        # Communicate with a neighbor to get a task proposal
        return Task(priority=random.randint(1, 10))

class Task:
    def __init__(self, priority: int):
        self.priority = priority

    async def execute(self):
        # Execute the task
        await asyncio.sleep(random.uniform(1.0, 5.0))