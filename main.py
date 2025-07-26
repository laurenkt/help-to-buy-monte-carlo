import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib.widgets import Slider
from multiprocessing import Pool
import multiprocessing as mp
import csv
import os
import sys
from tqdm import tqdm
from datetime import datetime, timedelta

# Global variables to cache historical data
_historical_cpi_changes = None
_historical_property_changes = None
_historical_mortgage_changes = None
_lookback_years = None

def set_lookback_years(years):
    """Set the lookback period for historical data sampling"""
    global _lookback_years
    _lookback_years = years

def load_historical_cpi_changes():
    """Load historical CPI monthly changes from CSV file for realistic sampling with optional lookback filtering"""
    global _historical_cpi_changes
    
    if _historical_cpi_changes is not None:
        return _historical_cpi_changes
    
    # Use complete historical file with dates for filtering
    cpi_file = 'datasets/uk_cpi_historical_complete.csv'
    if not os.path.exists(cpi_file):
        # Fallback to the changes-only file
        cpi_file = 'datasets/uk_cpi_monthly_changes.csv'
        if not os.path.exists(cpi_file):
            if mp.current_process().name == 'MainProcess':
                print(f"Warning: No CPI data files found, falling back to uniform random CPI changes")
            return None
    
    try:
        changes = []
        cutoff_date = None
        
        # Calculate cutoff date if lookback is specified
        if _lookback_years is not None:
            cutoff_date = datetime.now() - timedelta(days=_lookback_years * 365.25)
        
        with open(cpi_file, 'r') as f:
            reader = csv.DictReader(f)
            if 'date' in reader.fieldnames:
                # Process complete file with dates
                previous_rate = None
                for row in reader:
                    date_str = row['date']
                    current_rate = float(row['annual_rate']) / 100  # Convert to decimal
                    
                    # Apply date filtering if specified
                    if cutoff_date is not None:
                        row_date = datetime.strptime(date_str, '%Y-%m-%d')
                        if row_date < cutoff_date:
                            previous_rate = current_rate
                            continue
                    
                    # Calculate monthly change from annual rate
                    if previous_rate is not None:
                        # Convert annual rates to monthly change deltas
                        monthly_change = (current_rate - previous_rate) / 12
                        changes.append(monthly_change)
                    
                    previous_rate = current_rate
            else:
                # Fallback to changes-only file
                for row in reader:
                    changes.append(float(row[0]))
        
        _historical_cpi_changes = np.array(changes)
        
        # Only print loading message once
        if mp.current_process().name == 'MainProcess':
            lookback_msg = f" (last {_lookback_years} years)" if _lookback_years else " (full history)"
            print(f"Loaded {len(changes)} historical CPI monthly changes{lookback_msg} (mean: {np.mean(_historical_cpi_changes)*100:.4f}%, std: {np.std(_historical_cpi_changes)*100:.4f}%)")
        
        return _historical_cpi_changes
        
    except Exception as e:
        if mp.current_process().name == 'MainProcess':
            print(f"Error loading CPI changes: {e}, falling back to uniform random")
        return None

def sample_historical_cpi_change(random_state):
    """Sample a random CPI monthly change from historical distribution"""
    historical_changes = load_historical_cpi_changes()
    
    if historical_changes is None:
        # Fallback to original uniform random method
        return random_state.uniform(-0.01, 0.01)
    
    # Sample from historical distribution
    return random_state.choice(historical_changes)

def load_historical_property_changes():
    """Load historical property monthly changes from CSV file for realistic sampling with optional lookback filtering"""
    global _historical_property_changes
    
    if _historical_property_changes is not None:
        return _historical_property_changes
    
    # Use complete historical file with dates for filtering
    property_file = 'datasets/uk_property_prices_complete.csv'
    if not os.path.exists(property_file):
        # Fallback to the changes-only file
        property_file = 'datasets/uk_property_monthly_changes.csv'
        if not os.path.exists(property_file):
            if mp.current_process().name == 'MainProcess':
                print(f"Warning: No property data files found, falling back to uniform random property changes")
            return None
    
    try:
        changes = []
        cutoff_date = None
        
        # Calculate cutoff date if lookback is specified
        if _lookback_years is not None:
            cutoff_date = datetime.now() - timedelta(days=_lookback_years * 365.25)
        
        with open(property_file, 'r') as f:
            reader = csv.DictReader(f)
            if 'date' in reader.fieldnames:
                # Process complete file with dates - focus on South East region
                previous_prices = {}
                for row in reader:
                    date_str = row['date']
                    region = row['region']
                    price = float(row['flat_price'])
                    
                    # Apply date filtering if specified
                    if cutoff_date is not None:
                        row_date = datetime.strptime(date_str, '%Y-%m-%d')
                        if row_date < cutoff_date:
                            previous_prices[region] = price
                            continue
                    
                    # Calculate monthly change for South East region (most representative)
                    if region == 'South East' and region in previous_prices:
                        previous_price = previous_prices[region]
                        if previous_price > 0:
                            monthly_change = (price - previous_price) / previous_price
                            changes.append(monthly_change)
                    
                    previous_prices[region] = price
            else:
                # Fallback to changes-only file
                for row in reader:
                    changes.append(float(row[0]))
        
        _historical_property_changes = np.array(changes)
        
        # Only print loading message once
        if mp.current_process().name == 'MainProcess':
            lookback_msg = f" (last {_lookback_years} years)" if _lookback_years else " (full history)"
            print(f"Loaded {len(changes)} historical property monthly changes{lookback_msg} (mean: {np.mean(_historical_property_changes)*100:.3f}%, std: {np.std(_historical_property_changes)*100:.3f}%)")
        
        return _historical_property_changes
        
    except Exception as e:
        if mp.current_process().name == 'MainProcess':
            print(f"Error loading property changes: {e}, falling back to uniform random")
        return None

def sample_historical_property_change(random_state):
    """Sample a random property monthly change from historical distribution"""
    historical_changes = load_historical_property_changes()
    
    if historical_changes is None:
        # Fallback to original uniform random method
        return random_state.uniform(-0.01, 0.01)
    
    # Sample from historical distribution
    return random_state.choice(historical_changes)

def load_historical_mortgage_changes():
    """Load historical mortgage monthly changes from CSV file for realistic sampling with optional lookback filtering"""
    global _historical_mortgage_changes
    
    if _historical_mortgage_changes is not None:
        return _historical_mortgage_changes
    
    # Use complete historical file with dates for filtering
    mortgage_file = 'datasets/uk_mortgage_rates_complete.csv'
    if not os.path.exists(mortgage_file):
        # Fallback to the changes-only file
        mortgage_file = 'datasets/uk_mortgage_monthly_changes.csv'
        if not os.path.exists(mortgage_file):
            if mp.current_process().name == 'MainProcess':
                print(f"Warning: No mortgage data files found, falling back to uniform random mortgage changes")
            return None
    
    try:
        changes = []
        cutoff_date = None
        
        # Calculate cutoff date if lookback is specified
        if _lookback_years is not None:
            cutoff_date = datetime.now() - timedelta(days=_lookback_years * 365.25)
        
        with open(mortgage_file, 'r') as f:
            reader = csv.DictReader(f)
            if 'date' in reader.fieldnames:
                # Process complete file with dates
                previous_rate = None
                for row in reader:
                    date_str = row['date']
                    current_rate = float(row['mortgage_rate'])
                    
                    # Apply date filtering if specified
                    if cutoff_date is not None:
                        row_date = datetime.strptime(date_str, '%Y-%m-%d')
                        if row_date < cutoff_date:
                            previous_rate = current_rate
                            continue
                    
                    # Calculate monthly change from previous rate
                    if previous_rate is not None:
                        monthly_change = current_rate - previous_rate
                        changes.append(monthly_change)
                    
                    previous_rate = current_rate
            else:
                # Fallback to changes-only file
                for row in reader:
                    changes.append(float(row[0]))
        
        _historical_mortgage_changes = np.array(changes)
        
        # Only print loading message once
        if mp.current_process().name == 'MainProcess':
            lookback_msg = f" (last {_lookback_years} years)" if _lookback_years else " (full history)"
            print(f"Loaded {len(changes)} historical mortgage monthly changes{lookback_msg} (mean: {np.mean(_historical_mortgage_changes)*100:.4f}%, std: {np.std(_historical_mortgage_changes)*100:.4f}%)")
        
        return _historical_mortgage_changes
        
    except Exception as e:
        if mp.current_process().name == 'MainProcess':
            print(f"Error loading mortgage changes: {e}, falling back to uniform random")
        return None

def sample_historical_mortgage_change(random_state):
    """Sample a random mortgage monthly change from historical distribution"""
    historical_changes = load_historical_mortgage_changes()
    
    if historical_changes is None:
        # Fallback to original uniform random method
        return random_state.uniform(-0.01, 0.01)
    
    # Sample from historical distribution
    return random_state.choice(historical_changes)

class SimulationConfig:
    def __init__(self, mortgage_rate=0.02, mortgage_term_years=35, equity_loan_amount=240000, 
                 mortgage_amount=260000, initial_equity=20000):
        self.mortgage_rate = mortgage_rate
        self.mortgage_term_years = mortgage_term_years
        self.equity_loan_amount = equity_loan_amount
        self.mortgage_amount = mortgage_amount
        self.initial_equity = initial_equity
        
        # Calculate derived values
        self.initial_property_value = equity_loan_amount + mortgage_amount + initial_equity
        
    def run_scenario(self, equity_payoff_year, random_seed=None):
        """Run simulation with equity loan paid off at specified year"""
        if random_seed is None:
            random_seed = equity_payoff_year  # Use year as seed for distinct CPI paths
        return generate_htb_projection(
            self.equity_loan_amount, 
            self.initial_property_value, 
            equity_payoff_year,
            self.mortgage_amount,
            self.mortgage_rate,
            self.mortgage_term_years,
            random_seed
        )
    
    def _run_year_scenarios(self, args):
        """Helper method to run scenarios for a single year (for parallel processing)"""
        year, num_scenarios = args
        year_scenarios = []
        
        for i in range(num_scenarios):
            try:
                # Use unique seed combining year and scenario index
                seed = year * 10000 + i
                result = self.run_scenario(year, random_seed=seed)
                final_pnl = result[-5]  # final_pnl is fifth from last
                
                scenario = {
                    'scenario_id': year * num_scenarios + i,  # Unique ID
                    'year': year,
                    'final_pnl': final_pnl,
                    'result': result
                }
                
                year_scenarios.append(scenario)
                
            except Exception as e:
                print(f"Error in year {year}, scenario {i}: {e}")
                continue
        
        return year, year_scenarios

    def run_monte_carlo_scenarios(self, num_scenarios=100, max_year=25):
        """Run Monte Carlo scenarios for each repayment year in parallel, ranked by median performance"""
        # Set seed for reproducible scenario generation
        np.random.seed(123)
        
        total_scenarios = num_scenarios * (max_year + 1)
        show_progress = num_scenarios > 1000
        
        print(f"Running {num_scenarios} scenarios for each repayment year (0-{max_year}) in parallel...")
        
        # Preload historical data to avoid repeated loading in worker processes
        print("Loading historical data...")
        load_historical_property_changes()
        load_historical_cpi_changes() 
        load_historical_mortgage_changes()
        
        # Prepare arguments for parallel processing
        year_args = [(year, num_scenarios) for year in range(0, max_year + 1)]
        
        # Use multiprocessing to run years in parallel
        num_cores = min(mp.cpu_count(), len(year_args))
        print(f"Using {num_cores} CPU cores...")
        
        with Pool(num_cores) as pool:
            if show_progress:
                # Use imap_unordered for better progress tracking
                print("Starting parallel processing with progress tracking...")
                year_results = []
                pbar = tqdm(total=len(year_args), desc="Processing years", unit="year", 
                           bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}] {postfix}')
                
                for result in pool.imap_unordered(self._run_year_scenarios, year_args):
                    year_results.append(result)
                    year, scenarios = result
                    completed_scenarios = len(year_results) * num_scenarios
                    pbar.set_postfix_str(f"Year {year}: {len(scenarios):,} scenarios | Total: {completed_scenarios:,}/{total_scenarios:,}")
                    pbar.update(1)
                
                pbar.close()
                
                # Sort results by year since imap_unordered doesn't preserve order
                year_results.sort(key=lambda x: x[0])
            else:
                year_results = pool.map(self._run_year_scenarios, year_args)
        
        # Combine all results
        all_scenarios = []
        year_summaries = []
        
        for year, year_scenarios in year_results:
            if not show_progress:  # Only print if no progress bar was shown
                print(f"Processed year {year}: {len(year_scenarios)} scenarios")
            all_scenarios.extend(year_scenarios)
            
            # Calculate median performance for this year
            if year_scenarios:
                pnls = [s['final_pnl'] for s in year_scenarios]
                median_pnl = np.median(pnls)
                year_summaries.append({
                    'year': year,
                    'median_pnl': median_pnl,
                    'scenarios': year_scenarios,
                    'num_scenarios': len(year_scenarios)
                })
        
        # Sort years by median performance
        year_summaries.sort(key=lambda x: x['median_pnl'], reverse=True)
        
        # Print year rankings
        print(f"\nYear Rankings by Median P&L:")
        for i, year_data in enumerate(year_summaries[:10], 1):
            print(f"{i}. Year {year_data['year']}: £{year_data['median_pnl']:,.0f} median ({year_data['num_scenarios']} scenarios)")
        
        return all_scenarios, year_summaries
    
    def find_best_scenario(self, scenarios):
        """Find the scenario with the highest P&L"""
        if not scenarios:
            return None
        
        best = max(scenarios, key=lambda x: x['final_pnl'])
        return best

def generate_htb_projection(principal_amount, initial_property_value, repayment_year=10, 
                           mortgage_principal=260000, mortgage_rate=0.02, mortgage_years=35, random_seed=42):
    years = max(35, repayment_year + 1)  # Ensure we cover full mortgage term
    months_per_year = 12
    total_months = years * months_per_year
    
    time_months = np.arange(0, total_months + 1)
    cumulative_interest = np.zeros(len(time_months))
    
    # Property value simulation: use historical South East London flat price changes
    property_random_state = np.random.RandomState(random_seed + 2000)  # Different seed for property values
    property_values = np.zeros(len(time_months))
    
    # Start with initial property value
    current_property_value = initial_property_value
    property_values[0] = current_property_value
    
    # Apply historical property changes month by month
    for month in range(1, len(time_months)):
        # Sample a historical monthly change for South East London flats
        monthly_change = sample_historical_property_change(property_random_state)
        
        # Apply the change to current property value
        current_property_value = max(initial_property_value * 0.3,  # 30% floor protection
                                   current_property_value * (1 + monthly_change))
        property_values[month] = current_property_value
    
    # CPI simulation: use historical monthly changes to evolve CPI over time
    cpi_random_state = np.random.RandomState(random_seed)  # Different seed for each scenario
    monthly_cpi_rates = np.zeros(len(time_months))
    
    # Start with base CPI of 2%
    base_cpi = 0.02
    current_cpi = base_cpi
    monthly_cpi_rates[0] = current_cpi
    
    # Apply historical monthly changes
    for month in range(1, len(time_months)):
        # Sample a historical monthly change
        monthly_change = sample_historical_cpi_change(cpi_random_state)
        
        # Apply the change to current CPI
        current_cpi = max(0, current_cpi + monthly_change)  # Prevent negative CPI
        monthly_cpi_rates[month] = current_cpi
    
    # Mortgage rate simulation: use historical UK mortgage rate changes, locked every 5 years
    mortgage_random_state = np.random.RandomState(random_seed + 1000)  # Different seed for mortgage rates
    monthly_mortgage_rates = np.zeros(len(time_months))
    
    # Start with base mortgage rate (from parameter)
    current_mortgage_rate = mortgage_rate
    monthly_mortgage_rates[0] = current_mortgage_rate
    
    # Apply historical mortgage changes month by month, with 5-year lock periods
    for month in range(1, len(time_months)):
        # Check if we're at the start of a new 5-year period (60 months)
        if month % 60 == 0:
            # Sample a new historical monthly change for rate adjustment
            monthly_change = sample_historical_mortgage_change(mortgage_random_state)
            
            # Apply the change to get new locked rate
            current_mortgage_rate = max(0.005, current_mortgage_rate + monthly_change)  # Min 0.5%
        
        # Rate stays locked for this 5-year period
        monthly_mortgage_rates[month] = current_mortgage_rate
    
    # HTB interest rates locked in each April (based on CPI at that time)
    annual_htb_rates = np.zeros(len(time_months))
    locked_htb_rate = 0.0175  # Initial 1.75% rate
    
    for month in range(len(time_months)):
        year = month // 12
        month_in_year = month % 12
        
        # Lock in new rate each April (month 3, since 0=Jan, 1=Feb, 2=Mar, 3=Apr)
        if month_in_year == 3 and year >= 5:  # April, and after year 5 when interest starts
            # For 2021-2023 scheme: previous rate * (1 + CPI + 2%)
            april_cpi = monthly_cpi_rates[month]
            rate_increase = april_cpi + 0.02  # CPI + 2%
            locked_htb_rate = locked_htb_rate * (1 + rate_increase)
        
        annual_htb_rates[month] = locked_htb_rate
    
    # Equity loan percentage (assuming 20% Help-to-Buy loan)
    equity_percentage = principal_amount / initial_property_value
    
    # Current equity loan value based on property value
    current_loan_value = property_values * equity_percentage
    
    # Set loan value to zero after repayment
    repayment_month = repayment_year * 12
    if repayment_month < len(current_loan_value):
        current_loan_value[repayment_month:] = 0
    
    # Mortgage calculation with 5-year fixed terms
    mortgage_months = mortgage_years * 12
    locked_mortgage_rates = np.zeros(len(time_months))
    monthly_payments = np.zeros(len(time_months))
    
    # Lock in mortgage rate every 5 years (60 months)
    current_locked_rate = mortgage_rate
    for month in range(len(time_months)):
        # Check if we need to lock in a new rate (every 5 years)
        if month % 60 == 0:  # Every 60 months = 5 years
            current_locked_rate = monthly_mortgage_rates[month]
        
        locked_mortgage_rates[month] = current_locked_rate
    
    # Calculate mortgage balance over time with changing rates
    mortgage_balance = np.zeros(len(time_months))
    mortgage_balance[0] = mortgage_principal
    current_monthly_payment = 0
    
    for month in range(1, len(time_months)):
        if month <= mortgage_months:
            # Recalculate payment when rate changes (every 5 years)
            if month % 60 == 1 or month == 1:  # First month or start of new 5-year term
                remaining_months = mortgage_months - month + 1
                current_rate = locked_mortgage_rates[month] / 12
                remaining_balance = mortgage_balance[month-1]
                
                if current_rate > 0 and remaining_months > 0:
                    current_monthly_payment = (remaining_balance * current_rate * 
                                             (1 + current_rate)**remaining_months) / \
                                            ((1 + current_rate)**remaining_months - 1)
                else:
                    current_monthly_payment = remaining_balance / remaining_months if remaining_months > 0 else 0
            
            monthly_payments[month] = current_monthly_payment
            
            # Calculate interest and principal
            monthly_rate = locked_mortgage_rates[month] / 12
            interest_payment = mortgage_balance[month-1] * monthly_rate
            principal_payment = max(0, current_monthly_payment - interest_payment)
            
            # New balance
            mortgage_balance[month] = max(0, mortgage_balance[month-1] - principal_payment)
        else:
            mortgage_balance[month] = 0
            monthly_payments[month] = 0
    
    # Add equity loan repayment to mortgage at repayment year
    if repayment_month < len(mortgage_balance):
        equity_repayment = current_loan_value[repayment_month-1] if repayment_month > 0 else principal_amount
        mortgage_balance[repayment_month:] += equity_repayment
    
    repayment_month = repayment_year * 12
    
    for month in range(len(time_months)):
        year = month // 12
        
        if year >= 5 and month < repayment_month:  # Interest starts in year 6 and stops at repayment
            current_rate = annual_htb_rates[month]
            monthly_interest = (principal_amount * current_rate) / 12
            
            if month > 0:
                cumulative_interest[month] = cumulative_interest[month-1] + monthly_interest
        elif month > 0 and month >= repayment_month:
            # After repayment, interest stays constant
            cumulative_interest[month] = cumulative_interest[month-1]
    
    # Calculate total loss/gain at repayment
    if repayment_month < len(time_months):
        repayment_loan_value = current_loan_value[repayment_month]
        repayment_interest = cumulative_interest[repayment_month]
        total_repayment = repayment_loan_value + repayment_interest
        total_loss = total_repayment - principal_amount
    else:
        total_loss = 0
        total_repayment = 0
        repayment_loan_value = 0
        repayment_interest = 0
    
    # Calculate total expenditure (HTB interest + actual mortgage payments over full term)
    total_mortgage_payments = np.sum(monthly_payments[:mortgage_months])
    total_expenditure = repayment_interest + total_mortgage_payments
    
    # Calculate final values at end of mortgage term
    final_month = min(len(time_months) - 1, mortgage_months)
    final_property_value = property_values[final_month]
    final_mortgage_balance = mortgage_balance[final_month]
    final_equity = final_property_value - final_mortgage_balance
    final_pnl = final_equity - total_expenditure
    
    return (time_months, current_loan_value, cumulative_interest, property_values, 
            repayment_year, total_loss, total_repayment, repayment_loan_value, repayment_interest,
            mortgage_balance, monthly_payments, total_expenditure, final_equity, final_pnl,
            monthly_cpi_rates, annual_htb_rates, monthly_mortgage_rates, locked_mortgage_rates)

def format_currency(x, pos):
    if x >= 1e6:
        return f'£{x/1e6:.1f}M'
    elif x >= 1e3:
        return f'£{x/1e3:.0f}K'
    else:
        return f'£{x:.0f}'

def plot_projection(time_months, current_loan_value, cumulative_interest, property_values, principal_amount, 
                   repayment_year, total_loss, total_repayment, repayment_loan_value, repayment_interest,
                   mortgage_balance, monthly_payment, total_expenditure, final_equity, final_pnl):
    time_years = time_months / 12
    max_years = 35
    
    plt.figure(figsize=(16, 16))
    
    plt.subplot(4, 1, 1)
    plt.plot(time_years, current_loan_value, 'b-', linewidth=2, label='Current Equity Loan Value')
    plt.plot(time_years, cumulative_interest, 'r-', linewidth=2, label='Cumulative HTB Interest')
    plt.axhline(y=principal_amount, color='gray', linestyle='--', alpha=0.7, label='Initial Loan Amount')
    plt.axvline(x=repayment_year, color='orange', linestyle=':', linewidth=2, label=f'Repayment Year {repayment_year}')
    
    # Mark repayment point
    if repayment_year * 12 < len(time_months):
        plt.scatter([repayment_year], [repayment_loan_value], color='blue', s=100, zorder=5)
        plt.scatter([repayment_year], [repayment_interest], color='red', s=100, zorder=5)
    
    plt.title(f'Complete Property Investment Analysis')
    plt.ylabel('HTB Amount')
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, max_years)
    
    plt.subplot(4, 1, 2)
    plt.plot(time_years, property_values, 'green', linewidth=2, label='Property Value')
    plt.plot(time_years, mortgage_balance, 'purple', linewidth=2, label='Mortgage Balance')
    plt.axvline(x=repayment_year, color='orange', linestyle=':', linewidth=2, label=f'HTB Repayment Year {repayment_year}')
    plt.ylabel('Property & Mortgage')
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, max_years)
    
    plt.subplot(4, 1, 3)
    total_debt = current_loan_value + mortgage_balance
    equity_value = property_values - total_debt
    plt.plot(time_years, equity_value, 'darkgreen', linewidth=2, label='Net Equity (Property - Total Debt)')
    plt.axvline(x=repayment_year, color='orange', linestyle=':', linewidth=2, label=f'HTB Repayment Year {repayment_year}')
    plt.ylabel('Net Equity')
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, max_years)
    
    plt.subplot(4, 1, 4)
    # Show cumulative expenditure over time
    cumulative_mortgage_payments = np.minimum(time_months, len(time_months)-1) * monthly_payment
    total_expenditure_over_time = cumulative_interest + cumulative_mortgage_payments
    plt.plot(time_years, total_expenditure_over_time, 'red', linewidth=2, label='Cumulative Expenditure')
    plt.axvline(x=repayment_year, color='orange', linestyle=':', linewidth=2, label=f'HTB Repayment Year {repayment_year}')
    
    # Add final P&L summary
    pnl_color = 'green' if final_pnl >= 0 else 'red'
    pnl_text = f'Profit: £{final_pnl:,.0f}' if final_pnl >= 0 else f'Loss: £{-final_pnl:,.0f}'
    
    plt.text(0.02, 0.98, f'Final Property Value: £{property_values[-1]:,.0f}\n'
                         f'Final Equity: £{final_equity:,.0f}\n'
                         f'Total Expenditure: £{total_expenditure:,.0f}\n'
                         f'{pnl_text}', 
             transform=plt.gca().transAxes, fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    plt.xlabel('Years')
    plt.ylabel('Expenditure')
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, max_years)
    
    plt.show()

def plot_interactive_scenarios(scenarios, best_scenario, year_summaries):
    """Interactive plot with year slider to explore median scenario performance by repayment year"""
    
    fig = plt.figure(figsize=(16, 16))
    
    # Create subplots with space for slider
    ax1 = plt.subplot(4, 1, 1)
    ax2 = plt.subplot(4, 1, 2) 
    ax3 = plt.subplot(4, 1, 3)
    ax4 = plt.subplot(4, 1, 4)
    
    # Find median scenario for year 0 as starting point
    year_0_data = next((y for y in year_summaries if y['year'] == 0), year_summaries[0])
    year_0_scenarios = year_0_data['scenarios']
    year_0_pnls = [s['final_pnl'] for s in year_0_scenarios]
    median_idx = len(year_0_pnls) // 2
    sorted_year_0 = sorted(year_0_scenarios, key=lambda x: x['final_pnl'])
    current_scenario = sorted_year_0[median_idx]
    
    result = current_scenario['result']
    (time_months, current_loan_value, cumulative_interest, property_values, 
     repayment_year, total_loss, total_repayment, repayment_loan_value, repayment_interest,
     mortgage_balance, monthly_payments, total_expenditure, final_equity, final_pnl,
     monthly_cpi_rates, annual_htb_rates, monthly_mortgage_rates, locked_mortgage_rates) = result
    
    time_years = time_months / 12
    max_years = 35
    total_debt = current_loan_value + mortgage_balance
    equity_value = property_values - total_debt
    
    # Plot 1: HTB loan progression with CPI rates
    line1, = ax1.plot(time_years, current_loan_value, 'b-', linewidth=2, label='Current Equity Loan Value')
    line2, = ax1.plot(time_years, cumulative_interest, 'r-', linewidth=2, label='Cumulative HTB Interest')
    
    # Add CPI and HTB rates on secondary y-axis
    ax1_rate = ax1.twinx()
    line7, = ax1_rate.plot(time_years, monthly_cpi_rates * 100, 'orange', linewidth=1, alpha=0.7, label='Monthly CPI (%)')
    line8, = ax1_rate.plot(time_years, annual_htb_rates * 100, 'purple', linewidth=2, label='HTB Interest Rate (%)')
    line9, = ax1_rate.plot(time_years, monthly_mortgage_rates * 100, 'gray', linewidth=1, alpha=0.7, label='Monthly Mortgage Rate (%)')
    line10, = ax1_rate.plot(time_years, locked_mortgage_rates * 100, 'brown', linewidth=2, label='Locked Mortgage Rate (%)')
    
    ax1.axhline(y=240000, color='gray', linestyle='--', alpha=0.7, label='Initial Loan Amount')
    vline1 = ax1.axvline(x=current_scenario['year'], color='orange', linestyle=':', linewidth=2, 
                        label=f'Repayment Year {current_scenario["year"]}')
    
    ax1.set_title(f'Monte Carlo Analysis - Payoff Year {current_scenario["year"]} (Median Scenario: ID {current_scenario["scenario_id"]})')
    ax1.set_ylabel('HTB Amount')
    ax1_rate.set_ylabel('Interest Rate (%)')
    ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    
    # Combine legends - place inside chart at top right
    lines1 = [line1, line2] 
    lines_rate = [line7, line8, line9, line10]
    labels1 = [l.get_label() for l in lines1]
    labels_rate = [l.get_label() for l in lines_rate]
    ax1.legend(lines1 + lines_rate, labels1 + labels_rate, loc='upper right', fontsize=8, ncol=2)
    
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(0, max_years)
    
    # Plot 2: Property value vs mortgage
    line3, = ax2.plot(time_years, property_values, 'green', linewidth=2, label='Property Value')
    line4, = ax2.plot(time_years, mortgage_balance, 'purple', linewidth=2, label='Mortgage Balance')
    vline2 = ax2.axvline(x=current_scenario['year'], color='orange', linestyle=':', linewidth=2, 
                        label=f'HTB Repayment Year {current_scenario["year"]}')
    
    ax2.set_ylabel('Property & Mortgage')
    ax2.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    ax2.legend(loc='upper right')
    ax2.grid(True, alpha=0.3)
    ax2.set_xlim(0, max_years)
    
    # Plot 3: Net equity
    line5, = ax3.plot(time_years, equity_value, 'darkgreen', linewidth=2, label='Net Equity (Property - Total Debt)')
    vline3 = ax3.axvline(x=current_scenario['year'], color='orange', linestyle=':', linewidth=2, 
                        label=f'HTB Repayment Year {current_scenario["year"]}')
    
    ax3.set_ylabel('Net Equity')
    ax3.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    ax3.legend(loc='upper right')
    ax3.grid(True, alpha=0.3)
    ax3.set_xlim(0, max_years)
    
    # Plot 4: Cumulative expenditure with variable mortgage payments
    cumulative_mortgage_payments = np.cumsum(monthly_payments)
    total_expenditure_over_time = cumulative_interest + cumulative_mortgage_payments
    line6, = ax4.plot(time_years, total_expenditure_over_time, 'red', linewidth=2, label='Cumulative Expenditure')
    line11, = ax4.plot(time_years, cumulative_mortgage_payments, 'brown', linewidth=1, alpha=0.7, label='Cumulative Mortgage Payments')
    vline4 = ax4.axvline(x=current_scenario['year'], color='orange', linestyle=':', linewidth=2, 
                        label=f'HTB Repayment Year {current_scenario["year"]}')
    
    # Add P&L summary box  
    year_0_median_pnl = year_0_data['median_pnl']
    text_box = ax4.text(0.02, 0.98, f'Repayment Year: {current_scenario["year"]}\n'
                                   f'Median P&L: £{year_0_median_pnl:,.0f}\n'
                                   f'Year Rank: {next((i+1 for i, y in enumerate(year_summaries) if y["year"] == 0), "N/A")} of {len(year_summaries)}\n'
                                   f'Scenarios: {year_0_data["num_scenarios"]}', 
                       transform=ax4.transAxes, fontsize=10, verticalalignment='top',
                       bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
    
    ax4.set_xlabel('Years')
    ax4.set_ylabel('Expenditure')
    ax4.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    ax4.legend(loc='upper right')
    ax4.grid(True, alpha=0.3)
    ax4.set_xlim(0, max_years)
    
    # Add slider for repayment years (0-25) - positioned higher to avoid overlap
    ax_slider = plt.axes([0.2, 0.08, 0.6, 0.03])
    max_year = max([y['year'] for y in year_summaries])
    slider = Slider(ax_slider, 'Repayment Year', 0, max_year, valinit=0, 
                   valfmt='%d', valstep=1)
    
    # Add text summary of top 5 years to the right of slider
    summary_text = "Top 5 Repayment Years by Median P&L:\n"
    for i, year_data in enumerate(year_summaries[:5], 1):
        summary_text += f"{i}. Year {year_data['year']}: £{year_data['median_pnl']:,.0f}\n"
    
    fig.text(0.65, 0.02, summary_text, fontsize=9, verticalalignment='bottom',
             bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    # Adjust layout to prevent overlap
    plt.subplots_adjust(bottom=0.15, top=0.95)
    
    def update_plot(val):
        selected_year = int(slider.val)
        
        # Find the year data and median scenario
        year_data = next((y for y in year_summaries if y['year'] == selected_year), year_summaries[0])
        year_scenarios = year_data['scenarios']
        year_pnls = [s['final_pnl'] for s in year_scenarios]
        median_idx = len(year_pnls) // 2
        sorted_scenarios = sorted(year_scenarios, key=lambda x: x['final_pnl'])
        selected_scenario = sorted_scenarios[median_idx]
        
        # Update detailed plots
        result = selected_scenario['result']
        (time_months, current_loan_value, cumulative_interest, property_values, 
         repayment_year, total_loss, total_repayment, repayment_loan_value, repayment_interest,
         mortgage_balance, monthly_payments, total_expenditure, final_equity, final_pnl,
         monthly_cpi_rates, annual_htb_rates, monthly_mortgage_rates, locked_mortgage_rates) = result
        
        time_years = time_months / 12
        total_debt = current_loan_value + mortgage_balance
        equity_value = property_values - total_debt
        
        # Update all lines
        line1.set_ydata(current_loan_value)
        line2.set_ydata(cumulative_interest)
        line3.set_ydata(property_values)
        line4.set_ydata(mortgage_balance)
        line5.set_ydata(equity_value)
        line7.set_ydata(monthly_cpi_rates * 100)
        line8.set_ydata(annual_htb_rates * 100)
        line9.set_ydata(monthly_mortgage_rates * 100)
        line10.set_ydata(locked_mortgage_rates * 100)
        
        # Update expenditure
        cumulative_mortgage_payments = np.cumsum(monthly_payments)
        total_expenditure_over_time = cumulative_interest + cumulative_mortgage_payments
        line6.set_ydata(total_expenditure_over_time)
        line11.set_ydata(cumulative_mortgage_payments)
        
        # Update vertical lines
        for vline in [vline1, vline2, vline3, vline4]:
            vline.set_xdata([selected_scenario['year'], selected_scenario['year']])
        
        # Update title and text
        ax1.set_title(f'Monte Carlo Analysis - Payoff Year {selected_scenario["year"]} (Median Scenario: ID {selected_scenario["scenario_id"]})')
        text_box.set_text(f'Repayment Year: {selected_scenario["year"]}\n'
                         f'Median P&L: £{final_pnl:,.0f}\n'
                         f'Year Rank: {next((i+1 for i, y in enumerate(year_summaries) if y["year"] == selected_year), "N/A")} of {len(year_summaries)}\n'
                         f'Scenarios: {len(year_scenarios)}')
        
        # Update y-axis limits for better viewing
        ax2_values = np.concatenate([property_values, mortgage_balance])
        ax2.set_ylim(0, max(ax2_values) * 1.1)
        ax3.set_ylim(min(equity_value) * 1.1, max(equity_value) * 1.1)
        ax4.set_ylim(0, max(total_expenditure_over_time) * 1.1)
        
        fig.canvas.draw()
    
    slider.on_changed(update_plot)
    plt.show()

if __name__ == "__main__":
    # Parse command line arguments
    num_scenarios = 1000  # Default value
    max_year = 25        # Default value
    lookback_years = None # Default: use all historical data
    
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
    
    # Set the lookback period for historical data loading
    if lookback_years is not None:
        set_lookback_years(lookback_years)
    
    # Configure simulation parameters
    config = SimulationConfig(
        mortgage_rate=0.02,         # 2% annual
        mortgage_term_years=35,     # 35 year term
        equity_loan_amount=240000,  # £240K Help-to-Buy loan
        mortgage_amount=260000,     # £260K mortgage
        initial_equity=20000        # £20K deposit
    )
    
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
    
    # Run Monte Carlo scenarios 
    scenarios, year_summaries = config.run_monte_carlo_scenarios(num_scenarios=num_scenarios, max_year=max_year)
    
    if scenarios:
        # Find the best scenario
        best_scenario = config.find_best_scenario(scenarios)
        
        print(f"\nResults summary:")
        print(f"Best scenario: ID {best_scenario['scenario_id']}, Year {best_scenario['year']}")
        print(f"Best final P&L: £{best_scenario['final_pnl']:,.0f}")
        
        # Show top 5 scenarios
        sorted_scenarios = sorted(scenarios, key=lambda x: x['final_pnl'], reverse=True)
        print(f"\nTop 5 scenarios:")
        for i, scenario in enumerate(sorted_scenarios[:5], 1):
            print(f"{i}. ID {scenario['scenario_id']}, Year {scenario['year']}: £{scenario['final_pnl']:,.0f}")
        
        # Show distribution of payoff years
        payoff_years = [s['year'] for s in scenarios]
        print(f"\nPayoff year distribution:")
        for year in sorted(set(payoff_years)):
            count = payoff_years.count(year)
            print(f"Year {year}: {count} scenarios ({count/len(scenarios)*100:.1f}%)")
        
        # Sort scenarios by P&L (best first) for the selector
        sorted_scenarios = sorted(scenarios, key=lambda x: x['final_pnl'], reverse=True)
        
        # Plot interactive comparison with slider
        plot_interactive_scenarios(sorted_scenarios, best_scenario, year_summaries)
    else:
        print("No scenarios could be run successfully.")
