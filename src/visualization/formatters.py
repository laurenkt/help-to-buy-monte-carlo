def format_currency(x, pos):
    """Format currency values for chart labels (£250K, £1.2M format)"""
    if x >= 1e6:
        return f'£{x/1e6:.1f}M'
    elif x >= 1e3:
        return f'£{x/1e3:.0f}K'
    else:
        return f'£{x:.0f}'