"""
vehicle/state.py

Principal state representation for VEHICLE 3D with E.I.A.R.(V).
Each node carries a 5-dimensional state: S_i = (E, I, A, R, V).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional, Tuple

import numpy as np

STATE_DIMENSION = 5
STATE_COLUMNS = ("E", "I", "A", "R", "V")


@dataclass
class NodeState:
    """
    Principal internal state of a node in VEHICLE.

    E: Spin / structural orientation.
    I: Information density.
    A: Active coupling.
    R: Relational compatibility.
    V: Verification-projection variable.
    """

    E: float = 0.0
    I: float = 0.0
    A: float = 0.0
    R: float = 0.0
    V: float = 0.0
    node_id: int = 0
    node_type: str = "base"

    def to_vector(self) -> np.ndarray:
        """Return state as a float numpy array [E, I, A, R, V]."""
        return np.array([self.E, self.I, self.A, self.R, self.V], dtype=float)

    @classmethod
    def from_vector(
        cls,
        vec: np.ndarray,
        node_id: int = 0,
        node_type: str = "base",
    ) -> "NodeState":
        """Construct NodeState from a 5-dimensional vector."""
        arr = np.asarray(vec, dtype=float).reshape(-1)
        if arr.shape[0] != STATE_DIMENSION:
            raise ValueError(f"Expected 5-dimensional vector, got {arr.shape[0]}")
        return cls(
            E=float(arr[0]),
            I=float(arr[1]),
            A=float(arr[2]),
            R=float(arr[3]),
            V=float(arr[4]),
            node_id=int(node_id),
            node_type=node_type,
        )

    def copy(self) -> "NodeState":
        """Return a deep copy of this node state."""
        return NodeState(
            E=self.E,
            I=self.I,
            A=self.A,
            R=self.R,
            V=self.V,
            node_id=self.node_id,
            node_type=self.node_type,
        )

    def __repr__(self) -> str:
        return (
            f"NodeState(id={self.node_id}, type={self.node_type}, "
            f"E={self.E:.3f}, I={self.I:.3f}, A={self.A:.3f}, "
            f"R={self.R:.3f}, V={self.V:.3f})"
        )


@dataclass
class SystemState:
    """
    Global state of the VEHICLE network: X(t) = [S_1(t), ..., S_N(t)].
    """

    nodes: list[NodeState] = field(default_factory=list)
    time: int = 0

    def __len__(self) -> int:
        return len(self.nodes)

    def add_node(self, state: NodeState) -> None:
        if self.get_node(state.node_id) is not None:
            raise ValueError(f"Duplicate node_id detected: {state.node_id}")
        self.nodes.append(state)

    def get_node(self, node_id: int) -> Optional[NodeState]:
        for node in self.nodes:
            if node.node_id == node_id:
                return node
        return None

    def node_ids(self) -> list[int]:
        return [node.node_id for node in self.nodes]

    def to_matrix(self) -> np.ndarray:
        if not self.nodes:
            return np.empty((0, STATE_DIMENSION), dtype=float)
        return np.array([node.to_vector() for node in self.nodes], dtype=float)

    def copy(self) -> "SystemState":
        return SystemState(nodes=[node.copy() for node in self.nodes], time=int(self.time))

    def __repr__(self) -> str:
        return f"SystemState(N={len(self.nodes)}, t={self.time})"


def _validate_range(name: str, value_range: Tuple[float, float]) -> tuple[float, float]:
    if len(value_range) != 2:
        raise ValueError(f"{name} must contain exactly two values.")
    low, high = float(value_range[0]), float(value_range[1])
    if low > high:
        raise ValueError(f"{name} lower bound must be <= upper bound.")
    return low, high


def initialize_random_state(
    N: int,
    seed: Optional[int] = None,
    E_range: Tuple[float, float] = (-1.0, 1.0),
    I_range: Tuple[float, float] = (0.0, 1.0),
    A_range: Tuple[float, float] = (0.0, 1.0),
    R_range: Tuple[float, float] = (0.0, 1.0),
    V_range: Tuple[float, float] = (0.0, 1.0),
) -> SystemState:
    """Initialize a system with N randomly initialized E.I.A.R.(V) nodes."""
    if N < 0:
        raise ValueError("N must be non-negative.")

    ranges = {
        "E_range": _validate_range("E_range", E_range),
        "I_range": _validate_range("I_range", I_range),
        "A_range": _validate_range("A_range", A_range),
        "R_range": _validate_range("R_range", R_range),
        "V_range": _validate_range("V_range", V_range),
    }

    rng = np.random.default_rng(seed)
    system = SystemState(time=0)

    for i in range(N):
        state = NodeState(
            E=float(rng.uniform(*ranges["E_range"])),
            I=float(rng.uniform(*ranges["I_range"])),
            A=float(rng.uniform(*ranges["A_range"])),
            R=float(rng.uniform(*ranges["R_range"])),
            V=float(rng.uniform(*ranges["V_range"])),
            node_id=i,
            node_type="base",
        )
        system.add_node(state)

    return system
