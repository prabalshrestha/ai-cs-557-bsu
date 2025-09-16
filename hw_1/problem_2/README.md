### Problem 2 — Vacuum World Simulation

This folder contains a simple two-location Vacuum World simulation with a reflex agent and two performance measures. The script prints step-by-step logs and also writes them to `hw_1/problem_2/logs/`.

### Prerequisites

- Python 3.11+

### Setup (optional virtual environment)

From the repository root:

```bash
python3 -m venv venv
source venv/bin/activate
```

No external dependencies are required.

### How to Run

Run from the repository root:

```bash
python hw_1/problem_2/main.py
```

Or change into the folder and run:

```bash
cd hw_1/problem_2
python main.py
```

### What You’ll See

- Console output showing each time step: percept, chosen action, step reward, and cumulative score.
- Four runs in total:
  - Agent A on Sequence 1
  - Agent A on Sequence 2
  - Agent B on Sequence 1
  - Agent B on Sequence 2

### Logs

The script also writes the same output to files under `hw_1/problem_2/logs/`:

- `agent_a_sequence_1.txt`
- `agent_a_sequence_2.txt`
- `agent_b_sequence_1.txt`
- `agent_b_sequence_2.txt`
