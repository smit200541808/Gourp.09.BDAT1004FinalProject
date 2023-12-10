import pandas as pd
import os

current_dir=os.getcwd()
print(current_dir)
file_path= current_dir + "\Data\Sales Transaction v.4a.csv"
print(file_path)
# Replace 'your_file.csv' with the actual path to your CSV file
# file_path = "C:/Users/raval/OneDrive/Documents/BDAT/data prog-Ethan/final_project/data/Sales Transaction v.4a.csv"

# Read the CSV file into a DataFrame
df = pd.read_csv(file_path)

# Convert the "Date" column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Define a function to adjust the year based on conditions
def adjust_year(row):
    if row['Date'].year == 2018:
        return row['Date'] + pd.DateOffset(years=6)
    elif row['Date'].year == 2019:
        return row['Date'] + pd.DateOffset(years=4)
    else:
        return row['Date']

# Replace the original "Date" column with the adjusted dates
df['Date'] = df.apply(adjust_year, axis=1)

# Split the DataFrame into separate CSV files based on unique dates
output_directory = current_dir + '\output_files'
os.makedirs(output_directory, exist_ok=True)

for date, group in df.groupby(df['Date'].dt.date):
    output_file_path = os.path.join(output_directory, f'Sales_transaction_{date}.csv')
    group.to_csv(output_file_path, index=False)

print("CSV files have been created.")
