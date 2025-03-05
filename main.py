import pandas as pd
import numpy as np
from datetime import date


def calculate_decreasing_hours(start_date=date.today()):
    """
    Calculate decreasing hours starting from 580, reducing by 40 each week since start_date.

    Args:
        start_date (date): The reference start date (defaults to today)

    Returns:
        float: Current value after weekly deductions
    """
    initial_value = 580
    today = date.today()

    # Calculate weeks elapsed (using integer division)
    days_elapsed = (today - start_date).days
    weeks_elapsed = days_elapsed // 7

    # Calculate current value
    current_value = initial_value - (40 * weeks_elapsed)

    # Don't let it go below 0
    return max(current_value, 0)


# Example usage
today = date.today()
current_hours = 580
print(f"Today ({today}): {current_hours}")


def calc_hours(hours):
    return sum([current_hours, hours, -1875])

df = pd.read_excel("Team_Detailed_02212024.xlsx",
                   usecols=['Employee Name', 'Pay Type', 'Regular Hours'])

# Forward fill the Employee Name column
df['Employee Name'] = df['Employee Name'].replace('', np.nan).ffill()

# Filter for rows where Pay Type is "R"
filtered_df = df[df['Pay Type'] == 'R'][['Employee Name', 'Pay Type', 'Regular Hours']]

# Remove any remaining empty strings in Employee Name if any
filtered_df = filtered_df[filtered_df['Employee Name'].str.strip() != '']
filtered_df['Regular Hours'] = filtered_df['Regular Hours'].astype(str).str.replace(' ', '').astype(float)
filtered_df['Remaining Hours'] = filtered_df['Regular Hours'].apply(calc_hours)


print(filtered_df)
