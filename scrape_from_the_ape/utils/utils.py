"""
Title: Utility Functions
Desc:  A collection of generic helper functions for parsing scraped data
"""

import re

def parse_price(price):
    """Extracts price from string & returns the full fare value
    
    NOTES: 
        - This currently excludes concession rates & returns the full fare rate
        - Free is treated as $0

    Args:
        price (str): price string
    
    Returns:
        float: Cleaned price
    """

    price = price.lower()

    if price == '':
        return 0
    elif "free" in price:
        return 0
    else:
        matches = re.findall(r"\$\d+(?:\.\d+)?", price)
        matches = [float(x.replace("$","")) for x in matches if x != '']
        return max(matches)