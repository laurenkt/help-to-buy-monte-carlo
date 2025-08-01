# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment Setup

This project uses [uv](https://docs.astral.sh/uv/) for modern Python project management:

```bash
# First-time setup (installs dependencies and creates .venv automatically)
uv sync

# Run the simulation
uv run python main.py

# Or activate the virtual environment manually
source .venv/bin/activate
python main.py
```

## Running the Simulation

```bash
# Run the full Monte Carlo simulation (1000 scenarios per year, 0-25 years)
uv run python main.py

# Or with custom parameters
uv run python main.py 10000 25 10  # 10k scenarios, 25 years, last 10 years of data
```

The simulation will:
- Generate 26,000 total scenarios (1000 per repayment year from 0-25)
- Use parallel processing across available CPU cores
- Display interactive matplotlib visualization with year slider
- Rank repayment strategies by median P&L performance

## Project Structure

The project is organized into clean directories:
- **`main.py`**: Main simulation engine and visualization
- **`datasets/`**: All historical UK economic data (CPI, property prices, mortgage rates)
- **`scripts/`**: Data processing and chart generation utilities
- **`pyproject.toml`**: Modern Python project configuration with uv

## Core Architecture

### Single-File Design
The main application is contained in `main.py` as a monolithic financial modeling tool with three main components:

### 1. SimulationConfig Class
Central configuration and execution controller that:
- Manages all financial parameters (mortgage rates, loan amounts, property values)
- Orchestrates parallel Monte Carlo execution via multiprocessing
- Handles scenario ranking and statistical analysis
- Key methods: `run_monte_carlo_scenarios()`, `_run_year_scenarios()`, `find_best_scenario()`

### 2. Financial Modeling Engine
The `generate_htb_projection()` function implements comprehensive UK Help-to-Buy loan mechanics:
- **Stochastic simulations**: Property values (±1% monthly), CPI rates (±1% monthly), mortgage rates (±1% monthly with 5-year locks)
- **HTB interest calculations**: 1.75% starting year 6, annual increases locked each April at (previous_rate × (1 + CPI + 2%))
- **Mortgage amortization**: Variable rate calculations with 5-year fixed terms and payment recalculation
- **Returns 18-tuple**: All time-series data for visualization and analysis

### 3. Interactive Visualization
The `plot_interactive_scenarios()` function creates a 4-panel matplotlib interface:
- Panel 1: HTB loan value and interest rates (with dual y-axis for rates)
- Panel 2: Property value vs mortgage balance  
- Panel 3: Net equity progression
- Panel 4: Cumulative expenditure analysis
- Year slider (0-25) to explore median scenarios by repayment year
- Real-time updates of all charts and statistics

### Financial Model Details
- **Property fluctuations**: ±1% monthly with 30% floor protection
- **CPI simulation**: Monthly variation locked annually in April for HTB rate calculations  
- **Mortgage rates**: ±1% monthly variation, locked every 60 months (5 years)
- **Parallel processing**: Uses multiprocessing.Pool for CPU-intensive Monte Carlo execution
- **Currency formatting**: Custom formatter for human-readable chart labels (£250K, £1.2M format)

### Data Flow
SimulationConfig → generate_htb_projection() → plot_interactive_scenarios()
Each scenario generates complete financial time-series → Statistical ranking → Interactive exploration

## Key Implementation Notes

- Deterministic randomness: Each scenario uses unique seeds (year × 10000 + scenario_index) for reproducible results
- Memory efficiency: Scenarios store only final P&L for ranking; full results generated on-demand for visualization
- Performance optimization: Parallel execution essential due to computational intensity (26,000 scenarios)
- Visualization responsiveness: Real-time chart updates when sliding between repayment years

## Writing Guidelines

- Commit messages and task summaries should:
  - Use clear, descriptive language
  - Include relevant emojis to add visual context
  - Highlight key technical achievements or challenges