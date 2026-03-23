import time
from typing import Dict, List, Optional
from dataclasses import dataclass
import threading
import logging

@dataclass
class SwarmNode:
    node_id: str
    ip_address: str
    status: str
    last_heartbeat: float
    capacity: float
    current_load: float

class SwarmManager:
    def __init__(self, min_nodes: int = 3, max_nodes: int = 10):
        self.nodes: Dict[str, SwarmNode] = {}
        self.min_nodes = min_nodes
        self.max_nodes = max_nodes
        self.health_check_interval = 30  # seconds
        self.node_timeout = 90  # seconds
        self._lock = threading.Lock()
        self._running = False
        self._monitor_thread: Optional[threading.Thread] = None
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def start(self) -> None:
        """Start the swarm manager and health monitoring."""
        self._running = True
        self._monitor_thread = threading.Thread(target=self._health_monitor)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        self.logger.info('SwarmManager started')

    def stop(self) -> None:
        """Stop the swarm manager and cleanup."""
        self._running = False
        if self._monitor_thread:
            self._monitor_thread.join()
        self.logger.info('SwarmManager stopped')

    def register_node(self, node_id: str, ip_address: str, capacity: float = 1.0) -> bool:
        """Register a new node in the swarm."""
        with self._lock:
            if len(self.nodes) >= self.max_nodes:
                self.logger.warning(f'Cannot register node {node_id}: max nodes reached')
                return False
            
            self.nodes[node_id] = SwarmNode(
                node_id=node_id,
                ip_address=ip_address,
                status='active',
                last_heartbeat=time.time(),
                capacity=capacity,
                current_load=0.0
            )
            self.logger.info(f'Node {node_id} registered successfully')
            return True

    def deregister_node(self, node_id: str) -> bool:
        """Remove a node from the swarm."""
        with self._lock:
            if node_id in self.nodes:
                del self.nodes[node_id]
                self.logger.info(f'Node {node_id} deregistered')
                return True
            return False

    def update_node_heartbeat(self, node_id: str) -> bool:
        """Update the last heartbeat time for a node."""
        with self._lock:
            if node_id in self.nodes:
                self.nodes[node_id].last_heartbeat = time.time()
                return True
            return False

    def update_node_load(self, node_id: str, load: float) -> bool:
        """Update the current load for a node."""
        with self._lock:
            if node_id in self.nodes:
                self.nodes[node_id].current_load = min(max(load, 0.0), 1.0)
                return True
            return False

    def get_available_nodes(self) -> List[SwarmNode]:
        """Return list of active nodes with available capacity."""
        with self._lock:
            return [
                node for node in self.nodes.values()
                if node.status == 'active' and node.current_load < node.capacity
            ]

    def _health_monitor(self) -> None:
        """Monitor node health and manage auto-scaling."""
        while self._running:
            with self._lock:
                current_time = time.time()
                for node_id, node in list(self.nodes.items()):
                    if current_time - node.last_heartbeat > self.node_timeout:
                        node.status = 'inactive'
                        self.logger.warning(f'Node {node_id} marked inactive due to timeout')
                
                active_nodes = len([n for n in self.nodes.values() if n.status == 'active'])
                
                if active_nodes < self.min_nodes:
                    self.logger.warning(
                        f'Active nodes ({active_nodes}) below minimum threshold ({self.min_nodes})'
                    )
                    # Trigger auto-scaling mechanism here
            
            time.sleep(self.health_check_interval)

    def get_cluster_stats(self) -> Dict:
        """Return current statistics about the swarm cluster."""
        with self._lock:
            active_nodes = [n for n in self.nodes.values() if n.status == 'active']
            return {
                'total_nodes': len(self.nodes),
                'active_nodes': len(active_nodes),
                'average_load': sum(n.current_load for n in active_nodes) / len(active_nodes) if active_nodes else 0,
                'total_capacity': sum(n.capacity for n in active_nodes)
            }
