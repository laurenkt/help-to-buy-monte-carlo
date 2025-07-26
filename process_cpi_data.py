#!/usr/bin/env python3
"""
Process UK CPI data to create a unified historical dataset for Monte Carlo simulation.
Combines historical annual rates (1950-1988) with recent CPIH index data (1988-2025).
"""

from datetime import datetime
import csv
import statistics

def process_historical_rates():
    """Load and clean historical CPI annual rates (1950-1988)"""
    print("Processing historical CPI rates...")
    
    # Read historical annual rates
    hist_data = []
    with open('uk_historical_cpi_rates.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            period_str = row[0].strip('"')
            rate = float(row[1].strip('"'))
            
            # Parse period (e.g., "1950 JAN")
            year, month = period_str.split()
            month_num = {
                'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
            }[month]
            
            date = datetime(int(year), month_num, 1)
            hist_data.append({
                'date': date,
                'annual_rate': rate,
                'source': 'historical'
            })
    
    return hist_data

def process_recent_index():
    """Load and convert recent CPIH index data to annual rates"""
    print("Processing recent CPIH index data...")
    
    # Read recent index data
    recent_data = []
    with open('cpih_overall_index.csv', 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            index_value = float(row[0])
            period_str = row[1]  # e.g., "Jun-25"
            
            # Parse period
            month_abbr, year_short = period_str.split('-')
            month_num = {
                'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4, 'May': 5, 'Jun': 6,
                'Jul': 7, 'Aug': 8, 'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
            }[month_abbr]
            
            # Convert 2-digit year to 4-digit (25 = 2025, 88 = 1988)
            year = int(year_short)
            if year < 50:  # Assume years 00-49 are 2000-2049
                year += 2000
            else:  # Years 50-99 are 1950-1999
                year += 1900
            
            date = datetime(year, month_num, 1)
            recent_data.append({
                'date': date,
                'index_value': index_value
            })
    
    # Sort by date
    recent_data.sort(key=lambda x: x['date'])
    
    # Calculate year-over-year percentage changes
    processed_data = []
    for i in range(12, len(recent_data)):  # Skip first 12 months
        current = recent_data[i]
        year_ago = recent_data[i-12]
        
        # Calculate percentage change
        annual_rate = ((current['index_value'] - year_ago['index_value']) / year_ago['index_value']) * 100
        
        processed_data.append({
            'date': current['date'],
            'annual_rate': annual_rate,
            'source': 'recent'
        })
    
    return processed_data

def combine_datasets():
    """Combine historical and recent data into unified dataset"""
    print("Combining datasets...")
    
    # Load both datasets
    hist_data = process_historical_rates()
    recent_data = process_recent_index()
    
    # Find overlap period (1988) and choose which data to use
    # Historical data goes up to Dec 1988, recent starts from around 1988
    cutoff_date = datetime(1989, 1, 1)
    
    # Use historical data before cutoff, recent data after
    hist_filtered = [record for record in hist_data if record['date'] < cutoff_date]
    recent_filtered = [record for record in recent_data if record['date'] >= cutoff_date]
    
    # Combine datasets
    combined_data = hist_filtered + recent_filtered
    
    # Sort by date
    combined_data.sort(key=lambda x: x['date'])
    
    print(f"Historical data: {len(hist_filtered)} records (1950-1988)")
    print(f"Recent data: {len(recent_filtered)} records (1989-2025)")
    print(f"Combined dataset: {len(combined_data)} records")
    
    if combined_data:
        min_date = min(record['date'] for record in combined_data)
        max_date = max(record['date'] for record in combined_data)
        print(f"Date range: {min_date} to {max_date}")
        
        # Calculate some statistics
        rates = [record['annual_rate'] for record in combined_data]
        print(f"\nCPI Annual Rate Statistics:")
        print(f"Mean: {statistics.mean(rates):.2f}%")
        print(f"Std Dev: {statistics.stdev(rates):.2f}%")
        print(f"Min: {min(rates):.2f}%")
        print(f"Max: {max(rates):.2f}%")
        print(f"Median: {statistics.median(rates):.2f}%")
    
    return combined_data

def calculate_monthly_changes(data):
    """Calculate month-to-month percentage changes from annual rates"""
    print("\nCalculating monthly CPI changes...")
    
    # Sort data by date to ensure proper ordering
    data.sort(key=lambda x: x['date'])
    
    monthly_changes = []
    for i in range(1, len(data)):
        current = data[i]
        previous = data[i-1]
        
        # Calculate monthly change: convert annual rates to monthly equivalent changes
        # Simple approximation: monthly_change = annual_rate / 12
        current_monthly = current['annual_rate'] / 12 / 100  # Convert % to decimal monthly
        previous_monthly = previous['annual_rate'] / 12 / 100
        
        # Calculate the change in monthly rate
        change = current_monthly - previous_monthly
        
        monthly_changes.append({
            'date': current['date'],
            'monthly_change': change,
            'source': current['source']
        })
    
    print(f"Calculated {len(monthly_changes)} monthly changes")
    
    if monthly_changes:
        changes = [record['monthly_change'] for record in monthly_changes]
        print(f"Monthly Change Statistics:")
        print(f"Mean: {statistics.mean(changes)*100:.4f}%")
        print(f"Std Dev: {statistics.stdev(changes)*100:.4f}%")
        print(f"Min: {min(changes)*100:.4f}%")
        print(f"Max: {max(changes)*100:.4f}%")
        print(f"Median: {statistics.median(changes)*100:.4f}%")
    
    return monthly_changes

def save_processed_data(data, monthly_changes):
    """Save the processed data for use in simulation"""
    print("\nSaving processed data...")
    
    # Save full dataset
    with open('uk_cpi_historical_complete.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'annual_rate', 'source'])
        for record in data:
            writer.writerow([record['date'].strftime('%Y-%m-%d'), record['annual_rate'], record['source']])
    
    # Save just the annual rates for reference
    with open('uk_cpi_annual_rates.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['annual_rate'])
        for record in data:
            writer.writerow([record['annual_rate']])
    
    # Save monthly changes for simulation (this is what we'll actually use)
    with open('uk_cpi_monthly_changes.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['monthly_change'])
        for record in monthly_changes:
            writer.writerow([record['monthly_change']])
    
    print(f"Saved {len(data)} records to uk_cpi_historical_complete.csv")
    print(f"Saved annual rates: uk_cpi_annual_rates.csv")
    print(f"Saved {len(monthly_changes)} monthly changes: uk_cpi_monthly_changes.csv")

if __name__ == "__main__":
    try:
        combined_data = combine_datasets()
        monthly_changes = calculate_monthly_changes(combined_data)
        save_processed_data(combined_data, monthly_changes)
        print("\n✅ CPI data processing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error processing CPI data: {e}")
        import traceback
        traceback.print_exc()