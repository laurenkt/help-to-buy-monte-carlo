#!/usr/bin/env python3
"""
Generate histogram of UK property price monthly changes for data validation
"""

import csv
import matplotlib.pyplot as plt
import numpy as np

def load_property_data():
    """Load property price monthly changes from CSV file"""
    monthly_changes = []
    with open('../datasets/uk_property_monthly_changes.csv', 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if row and row[0].strip():  # Check if row exists and is not empty
                try:
                    monthly_changes.append(float(row[0]))
                except ValueError:
                    continue  # Skip invalid values
    return np.array(monthly_changes)

def generate_histogram():
    """Generate and save histogram of property price monthly changes"""
    # Load data
    monthly_changes = load_property_data()
    
    # Remove any NaN values
    monthly_changes = monthly_changes[~np.isnan(monthly_changes)]
    
    # Calculate statistics
    mean_change = np.mean(monthly_changes)
    std_change = np.std(monthly_changes)
    min_change = np.min(monthly_changes)
    max_change = np.max(monthly_changes)
    n_observations = len(monthly_changes)
    
    # Calculate positive vs negative months
    positive_months = len(monthly_changes[monthly_changes > 0])
    negative_months = len(monthly_changes[monthly_changes < 0])
    zero_months = len(monthly_changes[monthly_changes == 0])
    
    # Create figure with larger size for better readability
    plt.figure(figsize=(12, 8))
    
    # Create histogram with 50 bins
    n, bins, patches = plt.hist(monthly_changes, bins=50, alpha=0.7, color='lightgreen', 
                               edgecolor='black', linewidth=0.5)
    
    # Add vertical lines for mean and ±1, ±2 standard deviations
    plt.axvline(mean_change, color='red', linestyle='--', linewidth=2, 
               label=f'Mean: {mean_change:.6f}')
    plt.axvline(mean_change + std_change, color='orange', linestyle='--', linewidth=1.5,
               label=f'+1σ: {mean_change + std_change:.6f}')
    plt.axvline(mean_change - std_change, color='orange', linestyle='--', linewidth=1.5,
               label=f'-1σ: {mean_change - std_change:.6f}')
    plt.axvline(mean_change + 2*std_change, color='purple', linestyle=':', linewidth=1.5,
               label=f'+2σ: {mean_change + 2*std_change:.6f}')
    plt.axvline(mean_change - 2*std_change, color='purple', linestyle=':', linewidth=1.5,
               label=f'-2σ: {mean_change - 2*std_change:.6f}')
    
    # Add vertical line at zero for reference
    plt.axvline(0, color='black', linestyle='-', linewidth=1, alpha=0.5, label='Zero change')
    
    # Formatting
    plt.title('Distribution of UK Property Price Monthly Changes (1995-2024)\nSouth East London Flats - Historical Data for Monte Carlo Simulation', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Monthly Property Price Change Rate', fontsize=14)
    plt.ylabel('Frequency', fontsize=14)
    plt.grid(True, alpha=0.3)
    plt.legend(loc='upper right', fontsize=10)
    
    # Add statistics text box
    stats_text = f"""Dataset Statistics:
Observations: {n_observations:,}
Mean: {mean_change:.6f}
Std Dev: {std_change:.6f}
Min: {min_change:.6f}
Max: {max_change:.6f}
Range: {max_change - min_change:.6f}
Positive: {positive_months} ({positive_months/n_observations*100:.1f}%)
Negative: {negative_months} ({negative_months/n_observations*100:.1f}%)
Zero: {zero_months} ({zero_months/n_observations*100:.1f}%)"""
    
    plt.text(0.02, 0.98, stats_text, transform=plt.gca().transAxes, 
             fontsize=10, verticalalignment='top', fontfamily='monospace',
             bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    # Improve layout
    plt.tight_layout()
    
    # Save as high-quality PNG
    plt.savefig('../uk_property_distribution.png', dpi=300, bbox_inches='tight')
    print(f"Histogram saved as 'uk_property_distribution.png'")
    print(f"Dataset contains {n_observations} observations spanning 1995-2024")
    print(f"Mean monthly change: {mean_change:.6f} ({mean_change*100:.4f}%)")
    print(f"Standard deviation: {std_change:.6f} ({std_change*100:.4f}%)")
    print(f"Range: {min_change:.6f} to {max_change:.6f}")
    print(f"Positive months: {positive_months} ({positive_months/n_observations*100:.1f}%)")
    print(f"Negative months: {negative_months} ({negative_months/n_observations*100:.1f}%)")
    
    # Show plot
    plt.show()

if __name__ == "__main__":
    generate_histogram()