from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Tuple
import os


# Types
Location = str  # "A" or "B"
Status = str  # "Dirty" or "Clean"
Percept = Tuple[Location, Status]
Action = str  # "Left", "Right", "Vacuum", "NoOp"


@dataclass
class VacuumWorldState:
    location_status: dict

    @staticmethod
    def new(initial_status: Status = "Dirty") -> "VacuumWorldState":
        return VacuumWorldState(
            location_status={"A": initial_status, "B": initial_status}
        )

    def set_status(self, location: Location, status: Status) -> None:
        self.location_status[location] = status

    def get_status(self, location: Location) -> Status:
        return self.location_status[location]

    def count_clean_squares(self) -> int:
        return sum(1 for s in self.location_status.values() if s == "Clean")


class PerformanceMeasure:
    def step_reward(
        self, action: Action, state: VacuumWorldState, current_location: Location
    ) -> int:
        raise NotImplementedError


class MeasureCleanIfVacuum(PerformanceMeasure):
    """+1 for each location cleaned in time T (reward only when a successful vacuum occurs)."""

    def step_reward(
        self, action: Action, state: VacuumWorldState, current_location: Location
    ) -> int:
        # Reward is granted only when we vacuum and the square ends up clean
        if action == "Vacuum":
            return 1
        return 0


class MeasureCleanMinusMove(PerformanceMeasure):
    """Agent B: +1 for cleaning or moving toward a dirty destination; -1 for moving to a clean destination."""

    def step_reward(
        self, action: Action, state: VacuumWorldState, current_location: Location
    ) -> int:
        if action == "Vacuum":
            return 1
        if action in {"Left", "Right"}:
            dest = "B" if current_location == "A" else "A"
            return 1 if state.get_status(dest) == "Dirty" else -1
        return 0


class VacuumAgent:
    def __init__(self, next_location: Callable[[Location], Location]):
        self.next_location = next_location

    def policy(self, percept: Percept) -> Action:
        location, status = percept
        if status == "Dirty":
            return "Vacuum"

        nxt = self.next_location(location)
        return "Right" if location == "A" and nxt == "B" else "Left"


def simulate(
    percepts: Iterable[Percept],
    agent: VacuumAgent,
    measure: PerformanceMeasure,
    initial_world_status: Status = "Dirty",
) -> List[str]:
    log_lines: List[str] = []
    world = VacuumWorldState.new(initial_world_status)
    score = 0

    def apply_action(location: Location, action: Action) -> None:
        if action == "Vacuum":
            world.set_status(location, "Clean")

    for t, percept in enumerate(percepts, start=1):
        location, status = percept

        world.set_status(location, status)

        action = agent.policy(percept)

        apply_action(location, action)

        step_reward = measure.step_reward(action, world, location)
        score += step_reward

        log_lines.append(
            f"t={t} Percept=[{location}, {status}] Action={action} StepReward={step_reward:+d} Score={score:+d}"
        )

    log_lines.append(f"FINAL SCORE: {score:+d}")
    return log_lines


def build_sequence_1(steps: int = 100) -> List[Percept]:
    sequence: List[Percept] = []
    pair: List[Percept] = [("A", "Dirty"), ("B", "Dirty")]
    while len(sequence) < steps:
        sequence.extend(pair)
    return sequence[:steps]


def build_sequence_2(steps: int = 100) -> List[Percept]:
    sequence: List[Percept] = [("A", "Dirty"), ("B", "Dirty")]
    pair_clean: List[Percept] = [("A", "Clean"), ("B", "Clean")]
    while len(sequence) < steps:
        sequence.extend(pair_clean)
    return sequence[:steps]


def main() -> None:
    def next_loc(loc: Location) -> Location:
        return "B" if loc == "A" else "A"

    agent = VacuumAgent(next_location=next_loc)

    seq1 = build_sequence_1()
    seq2 = build_sequence_2()

    runs = [
        (
            "agent_a",
            "+1 for each location cleaned in time",
            seq1,
            MeasureCleanIfVacuum(),
        ),
        (
            "agent_a",
            "+1 for each location cleaned in time",
            seq2,
            MeasureCleanIfVacuum(),
        ),
        (
            "agent_b",
            "+1 per clean square per step; -1 per move",
            seq1,
            MeasureCleanMinusMove(),
        ),
        (
            "agent_b",
            "+1 per clean square per step; -1 per move",
            seq2,
            MeasureCleanMinusMove(),
        ),
    ]

    for i, (agent_name, measure_name, sequence, measure) in enumerate(runs, start=1):
        sequence_id = "1" if sequence is seq1 else "2"
        header = [
            f'Run {i}: Measure="{measure_name}"',
            f"Sequence={sequence_id}",
        ]
        print("\n".join(header))
        sim_lines = simulate(sequence, agent, measure)
        for line in sim_lines:
            print(line)
        print()

        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        filename = os.path.join(logs_dir, f"{agent_name}_sequence_{sequence_id}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(header) + "\n")
            f.write("\n".join(sim_lines) + "\n")


if __name__ == "__main__":
    main()
