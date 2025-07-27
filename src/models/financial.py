import numpy as np
from dataclasses import dataclass
from typing import Tuple
from ..config.simulation_config import SimulationConfig
from ..data.samplers import sample_historical_cpi_change, sample_historical_property_change, sample_historical_mortgage_change


@dataclass
class FinancialProjectionResult:
    """Results from a Help-to-Buy financial projection"""
    time_months: np.ndarray
    current_loan_value: np.ndarray
    cumulative_interest: np.ndarray
    property_values: np.ndarray
    repayment_year: int
    total_loss: float
    total_repayment: float
    repayment_loan_value: float
    repayment_interest: float
    mortgage_balance: np.ndarray
    monthly_payments: np.ndarray
    total_expenditure: float
    final_equity: float
    final_pnl: float
    monthly_cpi_rates: np.ndarray
    annual_htb_rates: np.ndarray
    monthly_mortgage_rates: np.ndarray
    locked_mortgage_rates: np.ndarray
    
    def to_tuple(self) -> Tuple:
        """Convert to 18-tuple for backward compatibility"""
        return (
            self.time_months, self.current_loan_value, self.cumulative_interest, 
            self.property_values, self.repayment_year, self.total_loss, 
            self.total_repayment, self.repayment_loan_value, self.repayment_interest,
            self.mortgage_balance, self.monthly_payments, self.total_expenditure, 
            self.final_equity, self.final_pnl, self.monthly_cpi_rates, 
            self.annual_htb_rates, self.monthly_mortgage_rates, self.locked_mortgage_rates
        )


def generate_htb_projection(
    config: SimulationConfig,
    repayment_year: int = 10,
    random_seed: int = 42
) -> FinancialProjectionResult:
    """Generate comprehensive Help-to-Buy financial projection with stochastic modeling"""
    
    years = max(config.mortgage_term_years, repayment_year + 1)
    months_per_year = 12
    total_months = years * months_per_year
    
    time_months = np.arange(0, total_months + 1)
    cumulative_interest = np.zeros(len(time_months))
    
    # Property value simulation using historical South East London flat price changes
    property_random_state = np.random.RandomState(random_seed + 2000)
    property_values = np.zeros(len(time_months))
    
    current_property_value = config.initial_property_value
    property_values[0] = current_property_value
    
    for month in range(1, len(time_months)):
        monthly_change = sample_historical_property_change(property_random_state)
        current_property_value = max(
            config.initial_property_value * 0.3,  # 30% floor protection
            current_property_value * (1 + monthly_change)
        )
        property_values[month] = current_property_value
    
    # CPI simulation using historical monthly changes
    cpi_random_state = np.random.RandomState(random_seed)
    monthly_cpi_rates = np.zeros(len(time_months))
    
    base_cpi = 0.02
    current_cpi = base_cpi
    monthly_cpi_rates[0] = current_cpi
    
    for month in range(1, len(time_months)):
        monthly_change = sample_historical_cpi_change(cpi_random_state)
        current_cpi = max(0, current_cpi + monthly_change)
        monthly_cpi_rates[month] = current_cpi
    
    # Mortgage rate simulation with 5-year lock periods
    mortgage_random_state = np.random.RandomState(random_seed + 1000)
    monthly_mortgage_rates = np.zeros(len(time_months))
    
    current_mortgage_rate = config.mortgage_rate
    monthly_mortgage_rates[0] = current_mortgage_rate
    
    for month in range(1, len(time_months)):
        if month % 60 == 0:  # New 5-year period
            monthly_change = sample_historical_mortgage_change(mortgage_random_state)
            current_mortgage_rate = max(0.005, current_mortgage_rate + monthly_change)
        
        monthly_mortgage_rates[month] = current_mortgage_rate
    
    # HTB interest rates locked each April
    annual_htb_rates = np.zeros(len(time_months))
    locked_htb_rate = 0.0175  # Initial 1.75% rate
    
    for month in range(len(time_months)):
        year = month // 12
        month_in_year = month % 12
        
        if month_in_year == 3 and year >= 5:  # April, after year 5
            april_cpi = monthly_cpi_rates[month]
            rate_increase = april_cpi + 0.02  # CPI + 2%
            locked_htb_rate = locked_htb_rate * (1 + rate_increase)
        
        annual_htb_rates[month] = locked_htb_rate
    
    # Current equity loan value based on property value
    current_loan_value = property_values * config.equity_percentage
    
    # Set loan value to zero after repayment
    repayment_month = repayment_year * 12
    if repayment_month < len(current_loan_value):
        current_loan_value[repayment_month:] = 0
    
    # Mortgage calculation with variable rates
    mortgage_months = config.mortgage_term_years * 12
    locked_mortgage_rates = np.zeros(len(time_months))
    monthly_payments = np.zeros(len(time_months))
    
    current_locked_rate = config.mortgage_rate
    for month in range(len(time_months)):
        if month % 60 == 0:  # Lock new rate every 5 years
            current_locked_rate = monthly_mortgage_rates[month]
        locked_mortgage_rates[month] = current_locked_rate
    
    # Calculate mortgage balance over time
    mortgage_balance = np.zeros(len(time_months))
    mortgage_balance[0] = config.mortgage_amount
    current_monthly_payment = 0
    
    for month in range(1, len(time_months)):
        if month <= mortgage_months:
            if month % 60 == 1 or month == 1:  # Recalculate payment
                remaining_months = mortgage_months - month + 1
                current_rate = locked_mortgage_rates[month] / 12
                remaining_balance = mortgage_balance[month-1]
                
                if current_rate > 0 and remaining_months > 0:
                    current_monthly_payment = (
                        remaining_balance * current_rate * 
                        (1 + current_rate)**remaining_months
                    ) / ((1 + current_rate)**remaining_months - 1)
                else:
                    current_monthly_payment = (
                        remaining_balance / remaining_months if remaining_months > 0 else 0
                    )
            
            monthly_payments[month] = current_monthly_payment
            
            monthly_rate = locked_mortgage_rates[month] / 12
            interest_payment = mortgage_balance[month-1] * monthly_rate
            principal_payment = max(0, current_monthly_payment - interest_payment)
            
            mortgage_balance[month] = max(0, mortgage_balance[month-1] - principal_payment)
        else:
            mortgage_balance[month] = 0
            monthly_payments[month] = 0
    
    # Add equity loan repayment to mortgage balance
    if repayment_month < len(mortgage_balance):
        equity_repayment = (
            current_loan_value[repayment_month-1] if repayment_month > 0 
            else config.equity_loan_amount
        )
        mortgage_balance[repayment_month:] += equity_repayment
    
    # Calculate HTB interest accumulation
    for month in range(len(time_months)):
        year = month // 12
        
        if year >= 5 and month < repayment_month:
            current_rate = annual_htb_rates[month]
            monthly_interest = (config.equity_loan_amount * current_rate) / 12
            
            if month > 0:
                cumulative_interest[month] = cumulative_interest[month-1] + monthly_interest
        elif month > 0 and month >= repayment_month:
            cumulative_interest[month] = cumulative_interest[month-1]
    
    # Calculate financial outcomes
    if repayment_month < len(time_months):
        repayment_loan_value = current_loan_value[repayment_month]
        repayment_interest = cumulative_interest[repayment_month]
        total_repayment = repayment_loan_value + repayment_interest
        total_loss = total_repayment - config.equity_loan_amount
    else:
        total_loss = 0
        total_repayment = 0
        repayment_loan_value = 0
        repayment_interest = 0
    
    # Calculate final values
    total_mortgage_payments = np.sum(monthly_payments[:mortgage_months])
    total_expenditure = repayment_interest + total_mortgage_payments
    
    final_month = min(len(time_months) - 1, mortgage_months)
    final_property_value = property_values[final_month]
    final_mortgage_balance = mortgage_balance[final_month]
    final_equity = final_property_value - final_mortgage_balance
    final_pnl = final_equity - total_expenditure
    
    return FinancialProjectionResult(
        time_months=time_months,
        current_loan_value=current_loan_value,
        cumulative_interest=cumulative_interest,
        property_values=property_values,
        repayment_year=repayment_year,
        total_loss=total_loss,
        total_repayment=total_repayment,
        repayment_loan_value=repayment_loan_value,
        repayment_interest=repayment_interest,
        mortgage_balance=mortgage_balance,
        monthly_payments=monthly_payments,
        total_expenditure=total_expenditure,
        final_equity=final_equity,
        final_pnl=final_pnl,
        monthly_cpi_rates=monthly_cpi_rates,
        annual_htb_rates=annual_htb_rates,
        monthly_mortgage_rates=monthly_mortgage_rates,
        locked_mortgage_rates=locked_mortgage_rates
    )