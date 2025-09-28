import pandas as pd
import numpy as np

# Create sample data
data = {
    'Name': ['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
    'Age': [25, 30, 35, 40, 45],
    'Salary': [50000, 60000, 70000, 80000, 90000],
    'Department': ['HR', 'IT', 'Sales', 'IT', 'HR'],
    'Country': ['USA', 'Canada', 'USA', 'UK', 'Canada']
}

df = pd.DataFrame(data)
df.to_excel('sample.xlsx', index=False)
print("sample.xlsx created")
