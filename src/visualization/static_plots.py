import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from typing import Any

from .formatters import format_currency


def plot_projection(result: Any, config: Any):
    """Plot static projection for a single scenario"""
    
    time_years = result.time_months / 12
    max_years = 35
    
    plt.figure(figsize=(16, 16))
    
    # Panel 1: HTB loan progression
    plt.subplot(4, 1, 1)
    plt.plot(time_years, result.current_loan_value, 'b-', linewidth=2, label='Current Equity Loan Value')
    plt.plot(time_years, result.cumulative_interest, 'r-', linewidth=2, label='Cumulative HTB Interest')
    plt.axhline(y=config.equity_loan_amount, color='gray', linestyle='--', alpha=0.7, label='Initial Loan Amount')
    plt.axvline(x=result.repayment_year, color='orange', linestyle=':', linewidth=2, 
                label=f'Repayment Year {result.repayment_year}')
    
    # Mark repayment point
    if result.repayment_year * 12 < len(result.time_months):
        plt.scatter([result.repayment_year], [result.repayment_loan_value], color='blue', s=100, zorder=5)
        plt.scatter([result.repayment_year], [result.repayment_interest], color='red', s=100, zorder=5)
    
    plt.title(f'Complete Property Investment Analysis')
    plt.ylabel('HTB Amount')
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, max_years)
    
    # Panel 2: Property vs mortgage
    plt.subplot(4, 1, 2)
    plt.plot(time_years, result.property_values, 'green', linewidth=2, label='Property Value')
    plt.plot(time_years, result.mortgage_balance, 'purple', linewidth=2, label='Mortgage Balance')
    plt.axvline(x=result.repayment_year, color='orange', linestyle=':', linewidth=2, 
                label=f'HTB Repayment Year {result.repayment_year}')
    plt.ylabel('Property & Mortgage')
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, max_years)
    
    # Panel 3: Net equity
    plt.subplot(4, 1, 3)
    total_debt = result.current_loan_value + result.mortgage_balance
    equity_value = result.property_values - total_debt
    plt.plot(time_years, equity_value, 'darkgreen', linewidth=2, label='Net Equity (Property - Total Debt)')
    plt.axvline(x=result.repayment_year, color='orange', linestyle=':', linewidth=2, 
                label=f'HTB Repayment Year {result.repayment_year}')
    plt.ylabel('Net Equity')
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xlim(0, max_years)
    
    # Panel 4: Cumulative expenditure
    plt.subplot(4, 1, 4)
    cumulative_mortgage_payments = np.minimum(result.time_months, len(result.time_months)-1) * result.monthly_payments
    total_expenditure_over_time = result.cumulative_interest + cumulative_mortgage_payments
    plt.plot(time_years, total_expenditure_over_time, 'red', linewidth=2, label='Cumulative Expenditure')
    plt.axvline(x=result.repayment_year, color='orange', linestyle=':', linewidth=2, 
                label=f'HTB Repayment Year {result.repayment_year}')
    
    # Add final P&L summary
    pnl_color = 'green' if result.final_pnl >= 0 else 'red'
    pnl_text = f'Profit: £{result.final_pnl:,.0f}' if result.final_pnl >= 0 else f'Loss: £{-result.final_pnl:,.0f}'
    
    plt.text(0.02, 0.98, f'Final Property Value: £{result.property_values[-1]:,.0f}\n'
                         f'Final Equity: £{result.final_equity:,.0f}\n'
                         f'Total Expenditure: £{result.total_expenditure:,.0f}\n'
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