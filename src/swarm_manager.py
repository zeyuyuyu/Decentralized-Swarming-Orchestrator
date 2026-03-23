import asyncio
from typing import Dict, List, Optional
from dataclasses import dataclass
import random

@dataclass
class SwarmNode:
    id: str
    capacity: float
    current_load: float
    tasks: List[str]
    last_heartbeat: float

class SwarmManager:
    def __init__(self):
        self.nodes: Dict[str, SwarmNode] = {}
        self.task_queue: List[str] = []
        self.load_threshold = 0.8

    async def register_node(self, node_id: str, capacity: float = 1.0) -> None:
        """Register a new node in the swarm"""
        self.nodes[node_id] = SwarmNode(
            id=node_id,
            capacity=capacity,
            current_load=0.0,
            tasks=[],
            last_heartbeat=asyncio.get_event_loop().time()
        )

    async def schedule_task(self, task_id: str) -> Optional[str]:
        """Schedule a task to the most suitable node using load balancing"""
        if not self.nodes:
            self.task_queue.append(task_id)
            return None

        # Find eligible nodes (not overloaded)
        eligible_nodes = [
            node for node in self.nodes.values()
            if node.current_load < self.load_threshold * node.capacity
        ]

        if not eligible_nodes:
            self.task_queue.append(task_id)
            return None

        # Select node with lowest current load relative to capacity
        selected_node = min(
            eligible_nodes,
            key=lambda n: n.current_load / n.capacity
        )

        # Assign task
        selected_node.tasks.append(task_id)
        selected_node.current_load += 1.0 / selected_node.capacity
        return selected_node.id

    async def rebalance_tasks(self) -> None:
        """Redistribute tasks among nodes for optimal load balance"""
        if len(self.nodes) < 2:
            return

        # Find overloaded and underloaded nodes
        overloaded = [n for n in self.nodes.values() 
                     if n.current_load > self.load_threshold * n.capacity]
        underloaded = [n for n in self.nodes.values()
                      if n.current_load < self.load_threshold * n.capacity]

        for source in overloaded:
            while source.current_load > self.load_threshold * source.capacity:
                if not underloaded:
                    break
                    
                target = min(underloaded, 
                            key=lambda n: n.current_load / n.capacity)
                
                # Move task from source to target
                task = source.tasks.pop()
                target.tasks.append(task)
                source.current_load -= 1.0 / source.capacity
                target.current_load += 1.0 / target.capacity

    async def heartbeat(self, node_id: str) -> None:
        """Update node's last heartbeat timestamp"""
        if node_id in self.nodes:
            self.nodes[node_id].last_heartbeat = \
                asyncio.get_event_loop().time()

    async def cleanup_dead_nodes(self, timeout: float = 30.0) -> None:
        """Remove nodes that haven't sent heartbeat recently"""
        current_time = asyncio.get_event_loop().time()
        dead_nodes = [
            node_id for node_id, node in self.nodes.items()
            if current_time - node.last_heartbeat > timeout
        ]

        for node_id in dead_nodes:
            node = self.nodes.pop(node_id)
            # Requeue tasks from dead node
            self.task_queue.extend(node.tasks)
