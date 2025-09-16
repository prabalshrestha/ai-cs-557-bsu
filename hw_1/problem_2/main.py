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
class VacuumMainState:
    """Mutable main state for the two-location vacuum environment.

    Stores cleanliness status for locations "A" and "B".
    """
    location_status: dict

    @staticmethod
    def new(initial_status: Status = "Dirty") -> "VacuumMainState":
        """Create a new main state where both locations share an initial status."""
        return VacuumMainState(
            location_status={"A": initial_status, "B": initial_status}
        )

    def set_status(self, location: Location, status: Status) -> None:
        """Set the cleanliness status for a given location."""
        self.location_status[location] = status

    def get_status(self, location: Location) -> Status:
        """Return the cleanliness status for a given location."""
        return self.location_status[location]

    def count_clean_squares(self) -> int:
        """Count how many locations are currently clean."""
        return sum(1 for s in self.location_status.values() if s == "Clean")


class PerformanceMeasure:
    def step_reward(
        self, action: Action, state: VacuumMainState, current_location: Location
    ) -> int:
        raise NotImplementedError


class MeasureCleanIfVacuum(PerformanceMeasure):
    """Agent A: +1 for each location cleaned in time T (reward only when a successful vacuum occurs)."""

    def step_reward(
        self, action: Action, state: VacuumMainState, current_location: Location
    ) -> int:
        # Reward is granted only when we vacuum and the square ends up clean
        if action == "Vacuum":
            return 1
        return 0


class MeasureCleanMinusMove(PerformanceMeasure):
    """Agent B: +1 for cleaning or moving toward a dirty destination; -1 for moving to a clean destination."""

    def step_reward(
        self, action: Action, state: VacuumMainState, current_location: Location
    ) -> int:
        # +1 whenever we successfully vacuum
        if action == "Vacuum":
            return 1
        if action in {"Left", "Right"}:
            # Determine where the agent is moving next
            dest = "B" if current_location == "A" else "A"
            # Reward moving toward dirt; penalize moving toward clean
            return 1 if state.get_status(dest) == "Dirty" else -1
        return 0


class VacuumAgent:
    """Simple reflex agent for the vacuum main.

    Policy: If current location is dirty, vacuum. Otherwise, move to the other
    location based on the provided `next_location` function.
    """
    def __init__(self, next_location: Callable[[Location], Location]):
        self.next_location = next_location

    def policy(self, percept: Percept) -> Action:
        location, status = percept
        # Clean immediately if the current square is dirty
        if status == "Dirty":
            return "Vacuum"

        # Otherwise decide which way to move based on the next location
        nxt = self.next_location(location)
        return "Right" if location == "A" and nxt == "B" else "Left"


def simulate(
    percepts: Iterable[Percept],
    agent: VacuumAgent,
    measure: PerformanceMeasure,
    initial_main_status: Status = "Dirty",
) -> List[str]:
    """Run a simulation over a stream of percepts and return log lines.

    Parameters:
        percepts: Iterable of (location, status) inputs observed at each time step.
        agent: Agent that selects actions based on the current percept.
        measure: Performance measure that provides per-step rewards.
        initial_main_status: Initial cleanliness for both locations.

    Returns:
        A list of human-readable log lines, including a final score line.
    """
    log_lines: List[str] = []
    state = VacuumMainState.new(initial_main_status)
    score = 0

    def apply_action(location: Location, action: Action) -> None:
        # Only vacuum changes the environment in this model
        if action == "Vacuum":
            state.set_status(location, "Clean")

    for t, percept in enumerate(percepts, start=1):
        location, status = percept

        # Update state with what the agent perceives for the current location
        state.set_status(location, status)

        # Choose an action according to the agent's policy
        action = agent.policy(percept)

        # Apply the chosen action to the state
        apply_action(location, action)

        # Score the step according to the selected performance measure
        step_reward = measure.step_reward(action, state, location)
        score += step_reward

        # Record a readable log line for this time step
        log_lines.append(
            f"t={t} Percept=[{location}, {status}] Action={action} StepReward={step_reward:+d} Score={score:+d}"
        )

    # Append the final cumulative score line
    log_lines.append(f"FINAL SCORE: {score:+d}")
    return log_lines


def build_sequence_1(steps: int = 100) -> List[Percept]:
    """Alternating dirty percepts: A dirty, B dirty, repeated up to `steps`."""
    sequence: List[Percept] = []
    pair: List[Percept] = [("A", "Dirty"), ("B", "Dirty")]
    # Keep appending the pair until we reach desired length
    while len(sequence) < steps:
        sequence.extend(pair)
    return sequence[:steps]


def build_sequence_2(steps: int = 100) -> List[Percept]:
    """One dirty pair followed by repeating clean pairs up to `steps`."""
    sequence: List[Percept] = [("A", "Dirty"), ("B", "Dirty")]
    pair_clean: List[Percept] = [("A", "Clean"), ("B", "Clean")]
    # After the initial dirty pair, repeat clean pairs
    while len(sequence) < steps:
        sequence.extend(pair_clean)
    return sequence[:steps]


def main() -> None:
    """Execute predefined runs and write logs under `logs/` for analysis."""
    def next_loc(loc: Location) -> Location:
        # Toggle between locations A and B
        return "B" if loc == "A" else "A"

    agent = VacuumAgent(next_location=next_loc)

    seq1 = build_sequence_1()
    seq2 = build_sequence_2()

    # Define the experiment configurations (agent label, measure label, sequence, measure)
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
        # Identify which sequence is used for labeling/logging
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

        # Ensure logs directory exists and write the output file
        logs_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(logs_dir, exist_ok=True)
        filename = os.path.join(logs_dir, f"{agent_name}_sequence_{sequence_id}.txt")
        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(header) + "\n")
            f.write("\n".join(sim_lines) + "\n")


if __name__ == "__main__":
    main()
