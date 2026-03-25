import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import logging

@dataclass
class SwarmNode:
    id: str
    capacity: float
    current_load: float
    tasks: List[str]
    status: str

class SwarmManager:
    def __init__(self):
        self.nodes: Dict[str, SwarmNode] = {}
        self.min_nodes = 2
        self.max_nodes = 10
        self.load_threshold = 0.8
        self.logger = logging.getLogger(__name__)

    async def register_node(self, node_id: str, capacity: float = 1.0) -> None:
        self.nodes[node_id] = SwarmNode(
            id=node_id,
            capacity=capacity,
            current_load=0.0,
            tasks=[],
            status='active'
        )
        self.logger.info(f'Node {node_id} registered with capacity {capacity}')

    async def remove_node(self, node_id: str) -> None:
        if node_id in self.nodes:
            await self._redistribute_tasks(node_id)
            del self.nodes[node_id]
            self.logger.info(f'Node {node_id} removed from swarm')

    async def assign_task(self, task_id: str, load: float = 0.1) -> Optional[str]:
        if not self.nodes:
            return None

        best_node = min(
            self.nodes.values(),
            key=lambda n: n.current_load / n.capacity
        )

        if best_node.current_load + load > best_node.capacity:
            await self._trigger_scaling()
            return None

        best_node.tasks.append(task_id)
        best_node.current_load += load
        self.logger.info(f'Task {task_id} assigned to node {best_node.id}')
        return best_node.id

    async def _redistribute_tasks(self, node_id: str) -> None:
        if node_id not in self.nodes:
            return

        tasks = self.nodes[node_id].tasks
        for task in tasks:
            await self.assign_task(task)

    async def _trigger_scaling(self) -> None:
        total_load = sum(n.current_load for n in self.nodes.values())
        total_capacity = sum(n.capacity for n in self.nodes.values())
        load_ratio = total_load / total_capacity if total_capacity > 0 else 1

        if load_ratio > self.load_threshold and len(self.nodes) < self.max_nodes:
            new_node_id = f'node_{len(self.nodes) + 1}'
            await self.register_node(new_node_id)
            self.logger.info('Scaling up: Added new node')

        elif load_ratio < 0.3 and len(self.nodes) > self.min_nodes:
            least_loaded = min(
                self.nodes.values(),
                key=lambda n: n.current_load
            )
            await self.remove_node(least_loaded.id)
            self.logger.info('Scaling down: Removed underutilized node')

    async def get_swarm_status(self) -> Dict:
        return {
            'node_count': len(self.nodes),
            'total_load': sum(n.current_load for n in self.nodes.values()),
            'total_capacity': sum(n.capacity for n in self.nodes.values()),
            'nodes': {
                nid: {
                    'load': node.current_load,
                    'capacity': node.capacity,
                    'task_count': len(node.tasks)
                } for nid, node in self.nodes.items()
            }
        }

    async def monitor_swarm(self) -> None:
        while True:
            status = await self.get_swarm_status()
            self.logger.info(f'Swarm status: {status}')
            await self._trigger_scaling()
            await asyncio.sleep(60)
