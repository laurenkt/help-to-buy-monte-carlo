import numpy as np
from typing import Optional
from .loaders import load_historical_cpi_changes, load_historical_property_changes, load_historical_mortgage_changes


def sample_historical_cpi_change(random_state: np.random.RandomState) -> float:
    """Sample a random CPI monthly change from historical distribution"""
    historical_changes = load_historical_cpi_changes()
    
    if historical_changes is None:
        return random_state.uniform(-0.01, 0.01)
    
    return random_state.choice(historical_changes)


def sample_historical_property_change(random_state: np.random.RandomState) -> float:
    """Sample a random property monthly change from historical distribution"""
    historical_changes = load_historical_property_changes()
    
    if historical_changes is None:
        return random_state.uniform(-0.01, 0.01)
    
    return random_state.choice(historical_changes)


def sample_historical_mortgage_change(random_state: np.random.RandomState) -> float:
    """Sample a random mortgage monthly change from historical distribution"""
    historical_changes = load_historical_mortgage_changes()
    
    if historical_changes is None:
        return random_state.uniform(-0.01, 0.01)
    
    return random_state.choice(historical_changes)