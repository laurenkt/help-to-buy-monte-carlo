# Help-to-Buy Equity Loan Loss Projection Model

## Overview
This project implements a **stochastic Monte Carlo simulation** to project potential financial outcomes (losses/returns) of Help-to-Buy (HTB) equity loans.  
It models the evolution of **house prices**, **inflation**, **interest rates**, **mortgage balances**, and **HTB loan repayments** over time, generating a distribution of potential future scenarios.

The aim is to understand risk exposure under various economic conditions and assess the 5th, 50th, and 95th percentile outcomes for loan repayments.

---

## Features
- **Stochastic modeling** using Monte Carlo:
  - House prices (Geometric Brownian Motion or mean-reverting processes)
  - Inflation (random walk with drift)
  - Interest rates (simple stochastic or Vasicek/CIR process)
- **Help-to-Buy equity loan logic**:
  - Initial loan as a % of property value (typically 20% in England, 20% in Wales)
  - Equity-based repayment (loan amount grows/shrinks with property value)
  - Interest-free for first 5 years (£1/month management fee only)
  - Interest starts in year 6 at 1.75%, increases annually each April by:
    - 2013-2021 scheme: RPI + 1%
    - 2021-2023 scheme: CPI + 2%
  - Minimum partial repayment: 10% of current property value
  - Full repayment required within 25 years or on sale
  - £200 administration fee for repayments/remortgaging
  - Optional stochastic part-repayments or remortgaging events
- **Mortgage balance simulation** with amortization and refinancing
- **Cash flow tracking** for mortgage + HTB payments
- **Visual outputs**:
  - Distribution of total repayment amounts
  - Percentile bands of outcomes
  - Stress test scenarios (e.g., house price crash + high inflation)

---

## Objectives
- Estimate potential **loss or return** on Help-to-Buy loans under uncertainty.
- Quantify the impact of:
  - **Inflation**
  - **House price growth/decline**
  - **Remortgaging events**
  - **Early repayments**
- Provide **percentile-based projections** (5th, 50th, 95th) for repayments and cash flows.
- Support **stress testing** against extreme but plausible scenarios.

---

## Setup

First-time setup:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

For subsequent runs:
```bash
source activate.sh
python main.py
```

## Configuration

Edit main.py to configure:
- Number of simulations (e.g., 10,000)
- Time horizon (e.g., 25 years)
- Economic assumptions (house price volatility, inflation drift, interest rate process)
- Borrower behavior (probability of remortgaging, part-repayments)
