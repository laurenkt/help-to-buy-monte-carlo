import sys
from datetime import datetime
from typing import Tuple, Optional

from .config.simulation_config import SimulationConfig
from .data.loaders import set_lookback_years
from .models.monte_carlo import MonteCarloEngine
from .visualization.interactive_plots import plot_interactive_scenarios


def parse_command_line_args() -> Tuple[int, int, Optional[int]]:
    """Parse command line arguments for simulation parameters"""
    num_scenarios = 1000
    max_year = 25
    lookback_years = None
    
    if len(sys.argv) > 1:
        try:
            num_scenarios = int(sys.argv[1])
            if num_scenarios <= 0:
                print("Error: Number of scenarios must be positive")
                sys.exit(1)
        except ValueError:
            print("Error: First argument must be a valid integer (number of scenarios)")
            print("Usage: python main.py [num_scenarios] [max_year] [lookback_years]")
            print("Example: python main.py 10000")
            print("Example: python main.py 5000 20")
            print("Example: python main.py 10000 25 10  # Use only last 10 years of data")
            sys.exit(1)
    
    if len(sys.argv) > 2:
        try:
            max_year = int(sys.argv[2])
            if max_year < 0 or max_year > 30:
                print("Error: Max year must be between 0 and 30")
                sys.exit(1)
        except ValueError:
            print("Error: Second argument must be a valid integer (max repayment year)")
            print("Usage: python main.py [num_scenarios] [max_year] [lookback_years]")
            sys.exit(1)
    
    if len(sys.argv) > 3:
        try:
            lookback_years = int(sys.argv[3])
            if lookback_years <= 0 or lookback_years > 100:
                print("Error: Lookback years must be between 1 and 100")
                sys.exit(1)
        except ValueError:
            print("Error: Third argument must be a valid integer (lookback years)")
            print("Usage: python main.py [num_scenarios] [max_year] [lookback_years]")
            print("Example: python main.py 10000 25 10  # Use only last 10 years of data")
            sys.exit(1)
    
    return num_scenarios, max_year, lookback_years


def print_simulation_summary(config: SimulationConfig, num_scenarios: int, max_year: int, lookback_years: Optional[int]):
    """Print simulation configuration summary"""
    print(f"Initial property value: £{config.initial_property_value:,}")
    print(f"Equity loan: £{config.equity_loan_amount:,} ({config.equity_loan_amount/config.initial_property_value*100:.1f}%)")
    print(f"Mortgage: £{config.mortgage_amount:,} ({config.mortgage_amount/config.initial_property_value*100:.1f}%)")
    print(f"Initial equity: £{config.initial_equity:,} ({config.initial_equity/config.initial_property_value*100:.1f}%)")
    print(f"\nRunning Monte Carlo analysis...")
    print(f"Scenarios per year: {num_scenarios:,}")
    print(f"Repayment years: 0-{max_year}")
    print(f"Total scenarios: {num_scenarios * (max_year + 1):,}")
    if lookback_years is not None:
        print(f"Historical data lookback: {lookback_years} years (from {datetime.now().year - lookback_years} onwards)")
    else:
        print("Historical data lookback: Full history (all available data)")


def print_results_summary(scenarios, best_scenario, year_summaries):
    """Print simulation results summary"""
    print(f"\nResults summary:")
    print(f"Best scenario: ID {best_scenario.scenario_id}, Year {best_scenario.year}")
    print(f"Best final P&L: £{best_scenario.final_pnl:,.0f}")
    
    # Show top 5 scenarios
    sorted_scenarios = sorted(scenarios, key=lambda x: x.final_pnl, reverse=True)
    print(f"\nTop 5 scenarios:")
    for i, scenario in enumerate(sorted_scenarios[:5], 1):
        print(f"{i}. ID {scenario.scenario_id}, Year {scenario.year}: £{scenario.final_pnl:,.0f}")
    
    # Show distribution of payoff years
    payoff_years = [s.year for s in scenarios]
    print(f"\nPayoff year distribution:")
    for year in sorted(set(payoff_years)):
        count = payoff_years.count(year)
        print(f"Year {year}: {count} scenarios ({count/len(scenarios)*100:.1f}%)")


def run_cli():
    """Main CLI entry point"""
    # Parse command line arguments
    num_scenarios, max_year, lookback_years = parse_command_line_args()
    
    # Set lookback period if specified
    if lookback_years is not None:
        set_lookback_years(lookback_years)
    
    # Configure simulation
    config = SimulationConfig(
        mortgage_rate=0.02,
        mortgage_term_years=35,
        equity_loan_amount=240000,
        mortgage_amount=260000,
        initial_equity=20000
    )
    
    # Print configuration summary
    print_simulation_summary(config, num_scenarios, max_year, lookback_years)
    
    # Run Monte Carlo simulation
    engine = MonteCarloEngine(config)
    scenarios, year_summaries = engine.run_monte_carlo_scenarios(
        num_scenarios=num_scenarios, 
        max_year=max_year
    )
    
    if scenarios:
        # Find best scenario and print results
        best_scenario = engine.find_best_scenario(scenarios)
        print_results_summary(scenarios, best_scenario, year_summaries)
        
        # Sort scenarios by P&L for visualization
        sorted_scenarios = sorted(scenarios, key=lambda x: x.final_pnl, reverse=True)
        
        # Show interactive visualization
        plot_interactive_scenarios(sorted_scenarios, best_scenario, year_summaries)
    else:
        print("No scenarios could be run successfully.")