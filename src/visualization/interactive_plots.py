import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from matplotlib.widgets import Slider
from typing import List, Any

from .formatters import format_currency


class InteractiveVisualizer:
    """Interactive visualization with year slider for Monte Carlo scenarios"""
    
    def __init__(self, scenarios: List[Any], best_scenario: Any, year_summaries: List[Any]):
        self.scenarios = scenarios
        self.best_scenario = best_scenario
        self.year_summaries = year_summaries
        
        # Setup figure and subplots
        self.fig = plt.figure(figsize=(16, 16))
        self.ax1 = plt.subplot(4, 1, 1)
        self.ax2 = plt.subplot(4, 1, 2)
        self.ax3 = plt.subplot(4, 1, 3)
        self.ax4 = plt.subplot(4, 1, 4)
        
        # Initialize with year 0 median scenario
        self._setup_initial_scenario()
        self._create_plots()
        self._setup_slider()
        self._add_summary_text()
        plt.subplots_adjust(bottom=0.15, top=0.95)
    
    def _setup_initial_scenario(self):
        """Find and setup initial scenario (year 0 median)"""
        year_0_data = next((y for y in self.year_summaries if y.year == 0), self.year_summaries[0])
        year_0_scenarios = year_0_data.scenarios
        year_0_pnls = [s.final_pnl for s in year_0_scenarios]
        median_idx = len(year_0_pnls) // 2
        sorted_year_0 = sorted(year_0_scenarios, key=lambda x: x.final_pnl)
        self.current_scenario = sorted_year_0[median_idx]
        self.current_year_data = year_0_data
    
    def _create_plots(self):
        """Create all plot elements"""
        result = self.current_scenario.result
        time_years = result.time_months / 12
        max_years = 35
        
        # Plot 1: HTB loan progression with rates
        self.line1, = self.ax1.plot(time_years, result.current_loan_value, 'b-', linewidth=2, 
                                   label='Current Equity Loan Value')
        self.line2, = self.ax1.plot(time_years, result.cumulative_interest, 'r-', linewidth=2, 
                                   label='Cumulative HTB Interest')
        
        # Secondary y-axis for rates
        self.ax1_rate = self.ax1.twinx()
        self.line7, = self.ax1_rate.plot(time_years, result.monthly_cpi_rates * 100, 'orange', 
                                        linewidth=1, alpha=0.7, label='Monthly CPI (%)')
        self.line8, = self.ax1_rate.plot(time_years, result.annual_htb_rates * 100, 'purple', 
                                        linewidth=2, label='HTB Interest Rate (%)')
        self.line9, = self.ax1_rate.plot(time_years, result.monthly_mortgage_rates * 100, 'gray', 
                                        linewidth=1, alpha=0.7, label='Monthly Mortgage Rate (%)')
        self.line10, = self.ax1_rate.plot(time_years, result.locked_mortgage_rates * 100, 'brown', 
                                         linewidth=2, label='Locked Mortgage Rate (%)')
        
        self.ax1.axhline(y=240000, color='gray', linestyle='--', alpha=0.7, label='Initial Loan Amount')
        self.vline1 = self.ax1.axvline(x=self.current_scenario.year, color='orange', linestyle=':', 
                                      linewidth=2, label=f'Repayment Year {self.current_scenario.year}')
        
        self.ax1.set_title(f'Monte Carlo Analysis - Payoff Year {self.current_scenario.year} (Median Scenario: ID {self.current_scenario.scenario_id})')
        self.ax1.set_ylabel('HTB Amount')
        self.ax1_rate.set_ylabel('Interest Rate (%)')
        self.ax1.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
        
        # Combine legends
        lines1 = [self.line1, self.line2] 
        lines_rate = [self.line7, self.line8, self.line9, self.line10]
        labels1 = [l.get_label() for l in lines1]
        labels_rate = [l.get_label() for l in lines_rate]
        self.ax1.legend(lines1 + lines_rate, labels1 + labels_rate, loc='upper right', fontsize=8, ncol=2)
        
        self.ax1.grid(True, alpha=0.3)
        self.ax1.set_xlim(0, max_years)
        
        # Plot 2: Property value vs mortgage
        self.line3, = self.ax2.plot(time_years, result.property_values, 'green', linewidth=2, label='Property Value')
        self.line4, = self.ax2.plot(time_years, result.mortgage_balance, 'purple', linewidth=2, label='Mortgage Balance')
        self.vline2 = self.ax2.axvline(x=self.current_scenario.year, color='orange', linestyle=':', 
                                      linewidth=2, label=f'HTB Repayment Year {self.current_scenario.year}')
        
        self.ax2.set_ylabel('Property & Mortgage')
        self.ax2.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
        self.ax2.legend(loc='upper right')
        self.ax2.grid(True, alpha=0.3)
        self.ax2.set_xlim(0, max_years)
        
        # Plot 3: Net equity
        total_debt = result.current_loan_value + result.mortgage_balance
        equity_value = result.property_values - total_debt
        self.line5, = self.ax3.plot(time_years, equity_value, 'darkgreen', linewidth=2, 
                                   label='Net Equity (Property - Total Debt)')
        self.vline3 = self.ax3.axvline(x=self.current_scenario.year, color='orange', linestyle=':', 
                                      linewidth=2, label=f'HTB Repayment Year {self.current_scenario.year}')
        
        self.ax3.set_ylabel('Net Equity')
        self.ax3.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
        self.ax3.legend(loc='upper right')
        self.ax3.grid(True, alpha=0.3)
        self.ax3.set_xlim(0, max_years)
        
        # Plot 4: Cumulative expenditure
        cumulative_mortgage_payments = np.cumsum(result.monthly_payments)
        total_expenditure_over_time = result.cumulative_interest + cumulative_mortgage_payments
        self.line6, = self.ax4.plot(time_years, total_expenditure_over_time, 'red', linewidth=2, 
                                   label='Cumulative Expenditure')
        self.line11, = self.ax4.plot(time_years, cumulative_mortgage_payments, 'brown', linewidth=1, 
                                    alpha=0.7, label='Cumulative Mortgage Payments')
        self.vline4 = self.ax4.axvline(x=self.current_scenario.year, color='orange', linestyle=':', 
                                      linewidth=2, label=f'HTB Repayment Year {self.current_scenario.year}')
        
        # Add P&L summary box  
        median_pnl = self.current_year_data.median_pnl
        self.text_box = self.ax4.text(0.02, 0.98, 
                                     f'Repayment Year: {self.current_scenario.year}\n'
                                     f'Median P&L: £{median_pnl:,.0f}\n'
                                     f'Year Rank: {next((i+1 for i, y in enumerate(self.year_summaries) if y.year == 0), "N/A")} of {len(self.year_summaries)}\n'
                                     f'Scenarios: {self.current_year_data.num_scenarios}', 
                                     transform=self.ax4.transAxes, fontsize=10, verticalalignment='top',
                                     bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
        
        self.ax4.set_xlabel('Years')
        self.ax4.set_ylabel('Expenditure')
        self.ax4.yaxis.set_major_formatter(ticker.FuncFormatter(format_currency))
        self.ax4.legend(loc='upper right')
        self.ax4.grid(True, alpha=0.3)
        self.ax4.set_xlim(0, max_years)
    
    def _setup_slider(self):
        """Setup the year selection slider"""
        ax_slider = plt.axes([0.2, 0.08, 0.6, 0.03])
        max_year = max([y.year for y in self.year_summaries])
        self.slider = Slider(ax_slider, 'Repayment Year', 0, max_year, valinit=0, 
                            valfmt='%d', valstep=1)
        self.slider.on_changed(self._update_plot)
    
    def _add_summary_text(self):
        """Add summary text of top 5 years"""
        summary_text = "Top 5 Repayment Years by Median P&L:\n"
        for i, year_data in enumerate(self.year_summaries[:5], 1):
            summary_text += f"{i}. Year {year_data.year}: £{year_data.median_pnl:,.0f}\n"
        
        self.fig.text(0.65, 0.02, summary_text, fontsize=9, verticalalignment='bottom',
                     bbox=dict(boxstyle='round', facecolor='lightyellow', alpha=0.8))
    
    def _update_plot(self, val):
        """Update plot when slider changes"""
        selected_year = int(self.slider.val)
        
        # Find the year data and median scenario
        year_data = next((y for y in self.year_summaries if y.year == selected_year), self.year_summaries[0])
        year_scenarios = year_data.scenarios
        year_pnls = [s.final_pnl for s in year_scenarios]
        median_idx = len(year_pnls) // 2
        sorted_scenarios = sorted(year_scenarios, key=lambda x: x.final_pnl)
        selected_scenario = sorted_scenarios[median_idx]
        
        # Update scenario data
        result = selected_scenario.result
        time_years = result.time_months / 12
        total_debt = result.current_loan_value + result.mortgage_balance
        equity_value = result.property_values - total_debt
        
        # Update all lines
        self.line1.set_ydata(result.current_loan_value)
        self.line2.set_ydata(result.cumulative_interest)
        self.line3.set_ydata(result.property_values)
        self.line4.set_ydata(result.mortgage_balance)
        self.line5.set_ydata(equity_value)
        self.line7.set_ydata(result.monthly_cpi_rates * 100)
        self.line8.set_ydata(result.annual_htb_rates * 100)
        self.line9.set_ydata(result.monthly_mortgage_rates * 100)
        self.line10.set_ydata(result.locked_mortgage_rates * 100)
        
        # Update expenditure
        cumulative_mortgage_payments = np.cumsum(result.monthly_payments)
        total_expenditure_over_time = result.cumulative_interest + cumulative_mortgage_payments
        self.line6.set_ydata(total_expenditure_over_time)
        self.line11.set_ydata(cumulative_mortgage_payments)
        
        # Update vertical lines
        for vline in [self.vline1, self.vline2, self.vline3, self.vline4]:
            vline.set_xdata([selected_scenario.year, selected_scenario.year])
        
        # Update title and text
        self.ax1.set_title(f'Monte Carlo Analysis - Payoff Year {selected_scenario.year} (Median Scenario: ID {selected_scenario.scenario_id})')
        self.text_box.set_text(f'Repayment Year: {selected_scenario.year}\n'
                              f'Median P&L: £{result.final_pnl:,.0f}\n'
                              f'Year Rank: {next((i+1 for i, y in enumerate(self.year_summaries) if y.year == selected_year), "N/A")} of {len(self.year_summaries)}\n'
                              f'Scenarios: {len(year_scenarios)}')
        
        # Update y-axis limits for better viewing
        ax2_values = np.concatenate([result.property_values, result.mortgage_balance])
        self.ax2.set_ylim(0, max(ax2_values) * 1.1)
        self.ax3.set_ylim(min(equity_value) * 1.1, max(equity_value) * 1.1)
        self.ax4.set_ylim(0, max(total_expenditure_over_time) * 1.1)
        
        self.fig.canvas.draw()
    
    def show(self):
        """Display the interactive plot"""
        plt.show()


def plot_interactive_scenarios(scenarios: List[Any], best_scenario: Any, year_summaries: List[Any]):
    """Create and show interactive scenario visualization"""
    visualizer = InteractiveVisualizer(scenarios, best_scenario, year_summaries)
    visualizer.show()