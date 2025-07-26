#!/usr/bin/env python3
"""
Process UK property price data to create historical dataset for Monte Carlo simulation.
Focuses on flats in South East London and surrounding areas.
"""

from datetime import datetime
import csv
import statistics

def process_property_data():
    """Process HM Land Registry property data for South East London flats"""
    print("Processing UK property price data...")
    
    # Target regions: prioritize South East London areas
    target_regions = [
        'London',           # Overall London
        'Inner London',     # Central/South London areas 
        'Outer London',     # Including South East London
        'South East'        # Southeast England region
    ]
    
    property_data = []
    
    with open('uk_house_prices_property_type.csv', 'r') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            region = row['Region_Name']
            
            # Focus on target regions
            if region in target_regions:
                # Extract flat data (our target property type)
                flat_price = row['Flat_Average_Price']
                flat_monthly_change = row['Flat_Monthly_Change']
                
                if flat_price and flat_price.strip():  # Skip empty values
                    try:
                        date = datetime.strptime(row['Date'], '%Y-%m-%d')
                        price = float(flat_price)
                        
                        # Monthly change (if available)
                        monthly_change = None
                        if flat_monthly_change and flat_monthly_change.strip():
                            monthly_change = float(flat_monthly_change) / 100  # Convert % to decimal
                        
                        property_data.append({
                            'date': date,
                            'region': region,
                            'flat_price': price,
                            'monthly_change': monthly_change
                        })
                        
                    except (ValueError, TypeError) as e:
                        # Skip invalid data
                        continue
    
    # Sort by date
    property_data.sort(key=lambda x: x['date'])
    
    print(f"Loaded {len(property_data)} property price records")
    
    if property_data:
        min_date = min(record['date'] for record in property_data)
        max_date = max(record['date'] for record in property_data)
        print(f"Date range: {min_date} to {max_date}")
        
        # Show regions covered
        regions = set(record['region'] for record in property_data)
        print(f"Regions: {', '.join(sorted(regions))}")
    
    return property_data

def calculate_monthly_changes(data):
    """Calculate month-to-month property price changes by region"""
    print("\nCalculating monthly property price changes...")
    
    # Group by region for better calculations
    regions = {}
    for record in data:
        region = record['region']
        if region not in regions:
            regions[region] = []
        regions[region].append(record)
    
    # Sort each region by date
    for region in regions:
        regions[region].sort(key=lambda x: x['date'])
    
    all_changes = []
    
    # Calculate changes for each region
    for region, region_data in regions.items():
        print(f"\nProcessing {region}:")
        region_changes = []
        
        for i in range(1, len(region_data)):
            current = region_data[i]
            previous = region_data[i-1]
            
            # Use provided monthly change if available, otherwise calculate
            if current['monthly_change'] is not None:
                change = current['monthly_change']
            else:
                # Calculate percentage change
                change = (current['flat_price'] - previous['flat_price']) / previous['flat_price']
            
            change_record = {
                'date': current['date'],
                'region': region,
                'monthly_change': change,
                'flat_price': current['flat_price']
            }
            
            region_changes.append(change_record)
            all_changes.append(change_record)
        
        if region_changes:
            changes = [r['monthly_change'] for r in region_changes]
            print(f"  {len(region_changes)} monthly changes")
            print(f"  Mean: {statistics.mean(changes)*100:.3f}%")
            print(f"  Std Dev: {statistics.stdev(changes)*100:.3f}%")
            print(f"  Min: {min(changes)*100:.3f}%")
            print(f"  Max: {max(changes)*100:.3f}%")
    
    # Overall statistics
    if all_changes:
        all_change_values = [record['monthly_change'] for record in all_changes]
        print(f"\nOverall Monthly Change Statistics:")
        print(f"Total changes: {len(all_change_values)}")
        print(f"Mean: {statistics.mean(all_change_values)*100:.3f}%")
        print(f"Std Dev: {statistics.stdev(all_change_values)*100:.3f}%")
        print(f"Min: {min(all_change_values)*100:.3f}%")
        print(f"Max: {max(all_change_values)*100:.3f}%")
        print(f"Median: {statistics.median(all_change_values)*100:.3f}%")
    
    return all_changes

def save_processed_data(property_data, monthly_changes):
    """Save processed property data for simulation"""
    print("\nSaving processed property data...")
    
    # Save full dataset
    with open('uk_property_prices_complete.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['date', 'region', 'flat_price'])
        for record in property_data:
            writer.writerow([
                record['date'].strftime('%Y-%m-%d'), 
                record['region'], 
                record['flat_price']
            ])
    
    # Save monthly changes for simulation (primary input)
    with open('uk_property_monthly_changes.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['monthly_change'])
        for record in monthly_changes:
            writer.writerow([record['monthly_change']])
    
    # Save by region for analysis
    regions = {}
    for record in monthly_changes:
        region = record['region']
        if region not in regions:
            regions[region] = []
        regions[region].append(record)
    
    for region, region_data in regions.items():
        filename = f"uk_property_changes_{region.lower().replace(' ', '_')}.csv"
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['date', 'monthly_change', 'flat_price'])
            for record in region_data:
                writer.writerow([
                    record['date'].strftime('%Y-%m-%d'),
                    record['monthly_change'],
                    record['flat_price']
                ])
    
    print(f"Saved {len(property_data)} property records to uk_property_prices_complete.csv")
    print(f"Saved {len(monthly_changes)} monthly changes to uk_property_monthly_changes.csv")
    print(f"Saved {len(regions)} regional files")

if __name__ == "__main__":
    try:
        property_data = process_property_data()
        monthly_changes = calculate_monthly_changes(property_data)
        save_processed_data(property_data, monthly_changes)
        print("\n✅ Property data processing completed successfully!")
        
    except Exception as e:
        print(f"❌ Error processing property data: {e}")
        import traceback
        traceback.print_exc()