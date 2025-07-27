import numpy as np
import multiprocessing as mp
from multiprocessing import Pool
from tqdm import tqdm
from typing import List, Dict, Tuple, Any
from dataclasses import dataclass

from ..config.simulation_config import SimulationConfig
from ..data.loaders import load_historical_cpi_changes, load_historical_property_changes, load_historical_mortgage_changes
from .financial import generate_htb_projection


@dataclass
class MonteCarloScenario:
    """Single Monte Carlo scenario result"""
    scenario_id: int
    year: int
    final_pnl: float
    result: Any  # FinancialProjectionResult


@dataclass
class YearSummary:
    """Summary statistics for a repayment year"""
    year: int
    median_pnl: float
    scenarios: List[MonteCarloScenario]
    num_scenarios: int


class MonteCarloEngine:
    """Monte Carlo simulation engine for Help-to-Buy analysis"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
    
    def run_scenario(self, equity_payoff_year: int, random_seed: int = None) -> Any:
        """Run single simulation scenario"""
        if random_seed is None:
            random_seed = equity_payoff_year
        
        return generate_htb_projection(
            config=self.config,
            repayment_year=equity_payoff_year,
            random_seed=random_seed
        )
    
    def _run_year_scenarios(self, args: Tuple[int, int]) -> Tuple[int, List[MonteCarloScenario]]:
        """Helper method to run scenarios for a single year (for parallel processing)"""
        year, num_scenarios = args
        year_scenarios = []
        
        for i in range(num_scenarios):
            try:
                seed = year * 10000 + i
                result = self.run_scenario(year, random_seed=seed)
                final_pnl = result.final_pnl
                
                scenario = MonteCarloScenario(
                    scenario_id=year * num_scenarios + i,
                    year=year,
                    final_pnl=final_pnl,
                    result=result
                )
                
                year_scenarios.append(scenario)
                
            except Exception as e:
                print(f"Error in year {year}, scenario {i}: {e}")
                continue
        
        return year, year_scenarios
    
    def run_monte_carlo_scenarios(
        self, 
        num_scenarios: int = 100, 
        max_year: int = 25
    ) -> Tuple[List[MonteCarloScenario], List[YearSummary]]:
        """Run Monte Carlo scenarios for each repayment year in parallel"""
        
        np.random.seed(123)
        
        total_scenarios = num_scenarios * (max_year + 1)
        show_progress = num_scenarios > 1000
        
        print(f"Running {num_scenarios} scenarios for each repayment year (0-{max_year}) in parallel...")
        
        # Preload historical data to avoid repeated loading
        print("Loading historical data...")
        load_historical_property_changes()
        load_historical_cpi_changes() 
        load_historical_mortgage_changes()
        
        # Prepare arguments for parallel processing
        year_args = [(year, num_scenarios) for year in range(0, max_year + 1)]
        
        # Use multiprocessing for parallel execution
        num_cores = min(mp.cpu_count(), len(year_args))
        print(f"Using {num_cores} CPU cores...")
        
        with Pool(num_cores) as pool:
            if show_progress:
                print("Starting parallel processing with progress tracking...")
                year_results = []
                pbar = tqdm(
                    total=len(year_args), 
                    desc="Processing years", 
                    unit="year",
                    bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}'
                )
                
                for result in pool.imap_unordered(self._run_year_scenarios, year_args):
                    year_results.append(result)
                    year, scenarios = result
                    completed_scenarios = len(year_results) * num_scenarios
                    pbar.set_postfix_str(
                        f"Year {year}: {len(scenarios):,} scenarios | Total: {completed_scenarios:,}/{total_scenarios:,}"
                    )
                    pbar.update(1)
                
                pbar.close()
                
                # Sort results by year since imap_unordered doesn't preserve order
                year_results.sort(key=lambda x: x[0])
            else:
                year_results = pool.map(self._run_year_scenarios, year_args)
        
        # Combine results and create summaries
        all_scenarios = []
        year_summaries = []
        
        for year, year_scenarios in year_results:
            if not show_progress:
                print(f"Processed year {year}: {len(year_scenarios)} scenarios")
            
            all_scenarios.extend(year_scenarios)
            
            if year_scenarios:
                pnls = [s.final_pnl for s in year_scenarios]
                median_pnl = np.median(pnls)
                year_summaries.append(YearSummary(
                    year=year,
                    median_pnl=median_pnl,
                    scenarios=year_scenarios,
                    num_scenarios=len(year_scenarios)
                ))
        
        # Sort years by median performance
        year_summaries.sort(key=lambda x: x.median_pnl, reverse=True)
        
        # Print year rankings
        print(f"\nYear Rankings by Median P&L:")
        for i, year_data in enumerate(year_summaries[:10], 1):
            print(f"{i}. Year {year_data.year}: £{year_data.median_pnl:,.0f} median ({year_data.num_scenarios} scenarios)")
        
        return all_scenarios, year_summaries
    
    def find_best_scenario(self, scenarios: List[MonteCarloScenario]) -> MonteCarloScenario:
        """Find the scenario with the highest P&L"""
        if not scenarios:
            return None
        
        return max(scenarios, key=lambda x: x.final_pnl)