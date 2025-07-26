#!/usr/bin/env python3
"""
Process UK mortgage rate data to create historical dataset for Monte Carlo simulation.
Combines FRED historical data (1939-2017) with estimated recent rates based on BoE base rate + spread.
"""

from datetime import datetime
import csv
import statistics
import xlrd

def process_fred_mortgage_data():
    """Process FRED UK mortgage rate data (1939-2017)"""
    print("Processing FRED UK mortgage rate data...")
    
    mortgage_data = []
    
    with open('../datasets/uk_mortgage_rates_fred.csv', 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                date = datetime.strptime(row['observation_date'], '%Y-%m-%d')
                rate = float(row['HVMRUKM']) / 100  # Convert percentage to decimal
                
                mortgage_data.append({
                    'date': date,
                    'mortgage_rate': rate,
                    'source': 'FRED_historical'
                })
                
            except (ValueError, TypeError):
                # Skip invalid data
                continue
    
    print(f"Loaded {len(mortgage_data)} FRED mortgage rate records")
    
    if mortgage_data:
        min_date = min(record['date'] for record in mortgage_data)
        max_date = max(record['date'] for record in mortgage_data)
        print(f"FRED date range: {min_date} to {max_date}")
        
        rates = [record['mortgage_rate'] for record in mortgage_data]
        print(f"FRED rate range: {min(rates)*100:.2f}% to {max(rates)*100:.2f}%")
        print(f"FRED mean rate: {statistics.mean(rates)*100:.2f}%")
    
    return mortgage_data

def process_boe_base_rates():
    """Process Bank of England base rate data and estimate mortgage rates"""
    print("\nProcessing Bank of England base rate data...")
    
    # Try to read the Excel file
    try:
        workbook = xlrd.open_workbook('boe_base_rates.xls')
        sheet = workbook.sheet_by_index(0)
        
        base_rate_data = []
        
        # Find the data rows (skip headers)
        for row_idx in range(1, sheet.nrows):
            try:
                # Assuming date is in first column, rate in second
                date_cell = sheet.cell(row_idx, 0)
                rate_cell = sheet.cell(row_idx, 1)
                
                # Handle different date formats
                if date_cell.ctype == xlrd.XL_CELL_DATE:
                    date_tuple = xlrd.xldate_as_tuple(date_cell.value, workbook.datemode)
                    date = datetime(*date_tuple[:3])
                elif date_cell.ctype == xlrd.XL_CELL_TEXT:
                    # Try various date formats
                    date_str = str(date_cell.value).strip()
                    try:
                        date = datetime.strptime(date_str, '%d %b %Y')
                    except:
                        try:
                            date = datetime.strptime(date_str, '%d/%m/%Y')
                        except:
                            continue
                else:
                    continue
                
                # Extract rate
                if rate_cell.ctype in [xlrd.XL_CELL_NUMBER, xlrd.XL_CELL_TEXT]:
                    rate = float(rate_cell.value) / 100  # Convert to decimal
                    
                    # Estimate mortgage rate: BoE base rate + typical spread (1.5-2.5%)
                    # Use 2% spread as reasonable average
                    mortgage_rate = rate + 0.02
                    
                    base_rate_data.append({
                        'date': date,
                        'base_rate': rate,
                        'mortgage_rate': mortgage_rate,
                        'source': 'BOE_estimated'
                    })
                    
            except Exception as e:
                continue
        
        print(f"Processed {len(base_rate_data)} BoE base rate records")
        return base_rate_data
        
    except Exception as e:
        print(f"Error processing BoE data: {e}")
        return []

def combine_mortgage_datasets():
    """Combine FRED historical data with BoE estimated data"""
    print("\nCombining mortgage rate datasets...")
    
    fred_data = process_fred_mortgage_data()
    boe_data = process_boe_base_rates()
    
    # Find cutoff date (end of FRED data)
    if fred_data:
        fred_end_date = max(record['date'] for record in fred_data)
        cutoff_date = datetime(fred_end_date.year + 1, 1, 1)  # Year after FRED ends
    else:
        cutoff_date = datetime(2017, 1, 1)
    
    # Use FRED data up to cutoff, BoE estimated data after
    fred_filtered = [record for record in fred_data if record['date'] < cutoff_date]
    boe_filtered = [record for record in boe_data if record['date'] >= cutoff_date]
    
    # Combine datasets
    combined_data = fred_filtered + boe_filtered
    
    # Sort by date
    combined_data.sort(key=lambda x: x['date'])
    
    print(f"FRED data: {len(fred_filtered)} records (up to {cutoff_date.strftime('%Y')})")
    print(f"BoE estimated data: {len(boe_filtered)} records ({cutoff_date.strftime('%Y')} onwards)")
    print(f"Combined dataset: {len(combined_data)} records")
    
    if combined_data:
        min_date = min(record['date'] for record in combined_data)
        max_date = max(record['date'] for record in combined_data)
        print(f"Full date range: {min_date} to {max_date}")
        
        # Calculate statistics
        rates = [record['mortgage_rate'] for record in combined_data]
        print(f"\nMortgage Rate Statistics:")
        print(f"Mean: {statistics.mean(rates)*100:.2f}%")
        print(f"Std Dev: {statistics.stdev(rates)*100:.2f}%")
        print(f"Min: {min(rates)*100:.2f}%")
        print(f"Max: {max(rates)*100:.2f}%")
        print(f"Median: {statistics.median(rates)*100:.2f}%")
    
    return combined_data

def calculate_monthly_changes(data):
    """Calculate month-to-month mortgage rate changes"""
    print("\nCalculating monthly mortgage rate changes...")
    
    monthly_changes = []
    
    for i in range(1, len(data)):
        current = data[i]
        previous = data[i-1]
        
        # Calculate change in mortgage rate
        change = current['mortgage_rate'] - previous['mortgage_rate']
        
        monthly_changes.append({
            'date': current['date'],
            'monthly_change': change,
            'mortgage_rate': current['mortgage_rate'],
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

def save_processed_data(mortgage_data, monthly_changes):
    """Save processed mortgage data for simulation"""
    print("\nSaving processed mortgage data...")
    
    # Save full dataset
    with open('../datasets/uk_mortgage_rates_complete.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'mortgage_rate', 'source'])
        for record in mortgage_data:
            writer.writerow([
                record['date'].strftime('%Y-%m-%d'), 
                record['mortgage_rate'], 
                record['source']
            ])
    
    # Save monthly changes for simulation (primary input)
    with open('../datasets/uk_mortgage_monthly_changes.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['monthly_change'])
        for record in monthly_changes:
            writer.writerow([record['monthly_change']])
    
    # Save by source for analysis
    sources = {}
    for record in monthly_changes:
        source = record['source']
        if source not in sources:
            sources[source] = []
        sources[source].append(record)
    
    for source, source_data in sources.items():
        filename = f"../datasets/uk_mortgage_changes_{source.lower()}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'monthly_change', 'mortgage_rate'])
            for record in source_data:
                writer.writerow([
                    record['date'].strftime('%Y-%m-%d'),
                    record['monthly_change'],
                    record['mortgage_rate']
                ])
    
    print(f"Saved {len(mortgage_data)} mortgage records to uk_mortgage_rates_complete.csv")
    print(f"Saved {len(monthly_changes)} monthly changes to uk_mortgage_monthly_changes.csv")
    print(f"Saved {len(sources)} source-specific files")

if __name__ == "__main__":
    try:
        mortgage_data = combine_mortgage_datasets()
        monthly_changes = calculate_monthly_changes(mortgage_data)
        save_processed_data(mortgage_data, monthly_changes)
        print("\n✅ Mortgage data processing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error processing mortgage data: {e}")
        import traceback
        traceback.print_exc()