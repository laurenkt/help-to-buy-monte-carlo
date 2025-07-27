import numpy as np
import csv
import os
import multiprocessing as mp
from datetime import datetime, timedelta
from typing import Optional


class HistoricalDataManager:
    """Manages loading and caching of historical economic data"""
    
    def __init__(self):
        self._historical_cpi_changes: Optional[np.ndarray] = None
        self._historical_property_changes: Optional[np.ndarray] = None
        self._historical_mortgage_changes: Optional[np.ndarray] = None
        self._lookback_years: Optional[int] = None
    
    def set_lookback_years(self, years: int) -> None:
        """Set the lookback period for historical data sampling"""
        self._lookback_years = years
    
    def load_historical_cpi_changes(self) -> Optional[np.ndarray]:
        """Load historical CPI monthly changes from CSV file for realistic sampling with optional lookback filtering"""
        if self._historical_cpi_changes is not None:
            return self._historical_cpi_changes
        
        cpi_file = 'datasets/uk_cpi_historical_complete.csv'
        if not os.path.exists(cpi_file):
            cpi_file = 'datasets/uk_cpi_monthly_changes.csv'
            if not os.path.exists(cpi_file):
                if mp.current_process().name == 'MainProcess':
                    print(f"Warning: No CPI data files found, falling back to uniform random CPI changes")
                return None
        
        try:
            changes = []
            cutoff_date = None
            
            if self._lookback_years is not None:
                cutoff_date = datetime.now() - timedelta(days=self._lookback_years * 365.25)
            
            with open(cpi_file, 'r') as f:
                reader = csv.DictReader(f)
                if 'date' in reader.fieldnames:
                    previous_rate = None
                    for row in reader:
                        date_str = row['date']
                        current_rate = float(row['annual_rate']) / 100
                        
                        if cutoff_date is not None:
                            row_date = datetime.strptime(date_str, '%Y-%m-%d')
                            if row_date < cutoff_date:
                                previous_rate = current_rate
                                continue
                        
                        if previous_rate is not None:
                            monthly_change = (current_rate - previous_rate) / 12
                            changes.append(monthly_change)
                        
                        previous_rate = current_rate
                else:
                    for row in reader:
                        changes.append(float(row[0]))
            
            self._historical_cpi_changes = np.array(changes)
            
            if mp.current_process().name == 'MainProcess':
                lookback_msg = f" (last {self._lookback_years} years)" if self._lookback_years else " (full history)"
                print(f"Loaded {len(changes)} historical CPI monthly changes{lookback_msg} (mean: {np.mean(self._historical_cpi_changes)*100:.4f}%, std: {np.std(self._historical_cpi_changes)*100:.4f}%)")
            
            return self._historical_cpi_changes
            
        except Exception as e:
            if mp.current_process().name == 'MainProcess':
                print(f"Error loading CPI changes: {e}, falling back to uniform random")
            return None

    def load_historical_property_changes(self) -> Optional[np.ndarray]:
        """Load historical property monthly changes from CSV file for realistic sampling with optional lookback filtering"""
        if self._historical_property_changes is not None:
            return self._historical_property_changes
        
        property_file = 'datasets/uk_property_prices_complete.csv'
        if not os.path.exists(property_file):
            property_file = 'datasets/uk_property_monthly_changes.csv'
            if not os.path.exists(property_file):
                if mp.current_process().name == 'MainProcess':
                    print(f"Warning: No property data files found, falling back to uniform random property changes")
                return None
        
        try:
            changes = []
            cutoff_date = None
            
            if self._lookback_years is not None:
                cutoff_date = datetime.now() - timedelta(days=self._lookback_years * 365.25)
            
            with open(property_file, 'r') as f:
                reader = csv.DictReader(f)
                if 'date' in reader.fieldnames:
                    previous_prices = {}
                    for row in reader:
                        date_str = row['date']
                        region = row['region']
                        price = float(row['flat_price'])
                        
                        if cutoff_date is not None:
                            row_date = datetime.strptime(date_str, '%Y-%m-%d')
                            if row_date < cutoff_date:
                                previous_prices[region] = price
                                continue
                        
                        if region == 'South East' and region in previous_prices:
                            previous_price = previous_prices[region]
                            if previous_price > 0:
                                monthly_change = (price - previous_price) / previous_price
                                changes.append(monthly_change)
                        
                        previous_prices[region] = price
                else:
                    for row in reader:
                        changes.append(float(row[0]))
            
            self._historical_property_changes = np.array(changes)
            
            if mp.current_process().name == 'MainProcess':
                lookback_msg = f" (last {self._lookback_years} years)" if self._lookback_years else " (full history)"
                print(f"Loaded {len(changes)} historical property monthly changes{lookback_msg} (mean: {np.mean(self._historical_property_changes)*100:.3f}%, std: {np.std(self._historical_property_changes)*100:.3f}%)")
            
            return self._historical_property_changes
            
        except Exception as e:
            if mp.current_process().name == 'MainProcess':
                print(f"Error loading property changes: {e}, falling back to uniform random")
            return None

    def load_historical_mortgage_changes(self) -> Optional[np.ndarray]:
        """Load historical mortgage monthly changes from CSV file for realistic sampling with optional lookback filtering"""
        if self._historical_mortgage_changes is not None:
            return self._historical_mortgage_changes
        
        mortgage_file = 'datasets/uk_mortgage_rates_complete.csv'
        if not os.path.exists(mortgage_file):
            mortgage_file = 'datasets/uk_mortgage_monthly_changes.csv'
            if not os.path.exists(mortgage_file):
                if mp.current_process().name == 'MainProcess':
                    print(f"Warning: No mortgage data files found, falling back to uniform random mortgage changes")
                return None
        
        try:
            changes = []
            cutoff_date = None
            
            if self._lookback_years is not None:
                cutoff_date = datetime.now() - timedelta(days=self._lookback_years * 365.25)
            
            with open(mortgage_file, 'r') as f:
                reader = csv.DictReader(f)
                if 'date' in reader.fieldnames:
                    previous_rate = None
                    for row in reader:
                        date_str = row['date']
                        current_rate = float(row['mortgage_rate'])
                        
                        if cutoff_date is not None:
                            row_date = datetime.strptime(date_str, '%Y-%m-%d')
                            if row_date < cutoff_date:
                                previous_rate = current_rate
                                continue
                        
                        if previous_rate is not None:
                            monthly_change = current_rate - previous_rate
                            changes.append(monthly_change)
                        
                        previous_rate = current_rate
                else:
                    for row in reader:
                        changes.append(float(row[0]))
            
            self._historical_mortgage_changes = np.array(changes)
            
            if mp.current_process().name == 'MainProcess':
                lookback_msg = f" (last {self._lookback_years} years)" if self._lookback_years else " (full history)"
                print(f"Loaded {len(changes)} historical mortgage monthly changes{lookback_msg} (mean: {np.mean(self._historical_mortgage_changes)*100:.4f}%, std: {np.std(self._historical_mortgage_changes)*100:.4f}%)")
            
            return self._historical_mortgage_changes
            
        except Exception as e:
            if mp.current_process().name == 'MainProcess':
                print(f"Error loading mortgage changes: {e}, falling back to uniform random")
            return None


# Global instance for multiprocessing compatibility
_data_manager = HistoricalDataManager()


def set_lookback_years(years: int) -> None:
    """Set the lookback period for historical data sampling"""
    _data_manager.set_lookback_years(years)


def load_historical_cpi_changes() -> Optional[np.ndarray]:
    """Load historical CPI monthly changes"""
    return _data_manager.load_historical_cpi_changes()


def load_historical_property_changes() -> Optional[np.ndarray]:
    """Load historical property monthly changes"""
    return _data_manager.load_historical_property_changes()


def load_historical_mortgage_changes() -> Optional[np.ndarray]:
    """Load historical mortgage monthly changes"""
    return _data_manager.load_historical_mortgage_changes()