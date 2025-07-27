from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """Configuration for Help-to-Buy Monte Carlo simulation"""
    mortgage_rate: float = 0.02
    mortgage_term_years: int = 35
    equity_loan_amount: float = 240000
    mortgage_amount: float = 260000
    initial_equity: float = 20000
    
    @property
    def initial_property_value(self) -> float:
        """Calculate total initial property value"""
        return self.equity_loan_amount + self.mortgage_amount + self.initial_equity
    
    @property 
    def equity_percentage(self) -> float:
        """Calculate equity loan as percentage of property value"""
        return self.equity_loan_amount / self.initial_property_value