import pandas as pd
import re
import logging
from datetime import datetime
import numpy as np
from dotenv import load_dotenv
import os

load_dotenv()

def clean_excel(df: pd.DataFrame) -> pd.DataFrame:
    # Rename unnamed columns
    df.columns = [f"column_{i+1}" if "Unnamed" in str(c) else str(c).strip() for i, c in enumerate(df.columns)]

    # Strip whitespace from column names and data
    df.columns = [c.strip() for c in df.columns]
    for col in df.columns:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.strip()

    # Handle missing values more intelligently
    for col in df.columns:
        if df[col].dtype == 'object':
            # For string columns, fill with empty string
            df[col] = df[col].fillna('')
        else:
            # For numeric, fill with 0 or mean if possible
            if df[col].isna().sum() > 0:
                if df[col].dtype in [float, int]:
                    df[col] = df[col].fillna(df[col].mean() if not df[col].isna().all() else 0)
                else:
                    df[col] = df[col].fillna('')

    # Remove duplicate rows
    df = df.drop_duplicates()

    # Standardize data types if possible
    for col in df.columns:
        if df[col].dtype == 'object':
            # Try to convert to datetime
            try:
                df[col] = pd.to_datetime(df[col], errors='ignore')
            except:
                pass
            # Then try to convert to numeric
            if df[col].dtype == 'object':
                try:
                    df[col] = pd.to_numeric(df[col], errors='ignore')
                except:
                    pass

    # Handle inconsistent data: remove rows with all NaN or empty
    df = df.dropna(how='all')
    df = df.reset_index(drop=True)

    return df

def predict_data(df: pd.DataFrame, question: str) -> str:
    """Perform simple predictive analysis using linear regression."""
    question_lower = question.lower()
    predictions = []

    # Find numeric columns for prediction
    numeric_cols = df.select_dtypes(include=[float, int]).columns
    if len(numeric_cols) == 0:
        return "No numeric data available for predictions."

    # Find date/time columns for time series
    date_cols = df.select_dtypes(include=['datetime']).columns
    if len(date_cols) > 0 and len(numeric_cols) > 0:
        # Sort by date
        df_sorted = df.sort_values(by=date_cols[0])
        # Use first numeric column for prediction
        target_col = numeric_cols[0]
        # Create time index
        df_sorted['time_index'] = range(len(df_sorted))
        x = df_sorted['time_index'].values
        y = df_sorted[target_col].values

        if len(x) > 1:
            # Simple linear regression
            n = len(x)
            sum_x = np.sum(x)
            sum_y = np.sum(y)
            sum_xy = np.sum(x * y)
            sum_x2 = np.sum(x ** 2)
            m = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            b = (sum_y - m * sum_x) / n
            # Predict next value
            next_index = len(df_sorted)
            next_value = m * next_index + b
            predictions.append(f"Based on trend analysis, the predicted next value for {target_col} is approximately {next_value:.2f}.")
        else:
            predictions.append("Insufficient data points for trend prediction.")
    else:
        # Simple extrapolation if no dates
        target_col = numeric_cols[0]
        values = df[target_col].dropna().values
        if len(values) > 1:
            # Simple linear extrapolation
            x = np.arange(len(values))
            n = len(x)
            sum_x = np.sum(x)
            sum_y = np.sum(values)
            sum_xy = np.sum(x * values)
            sum_x2 = np.sum(x ** 2)
            m = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x ** 2)
            b = (sum_y - m * sum_x) / n
            next_x = len(values)
            next_value = m * next_x + b
            predictions.append(f"Extrapolating from {target_col}, the predicted next value is approximately {next_value:.2f}.")
        else:
            predictions.append("Insufficient data for prediction.")

    return "\n".join(predictions)

def analyze_data(df: pd.DataFrame, question: str) -> str:
    # Check for predictive keywords first
    question_lower = question.lower()
    predictive_keywords = ['predict', 'forecast', 'future', 'trend', 'next', 'estimate', 'projection']
    if any(keyword in question_lower for keyword in predictive_keywords):
        prediction = predict_data(df, question)
        return prediction

    # Simple analysis based on question keywords, returning a string summary
    analysis = []

    # List all supported analysis questions
    if 'list all' in question_lower and ('analysis' in question_lower or 'questions' in question_lower or 'sums' in question_lower or 'avg' in question_lower):
        supported_questions = [
            "Count questions: 'How many rows?', 'Count employees', 'Number of departments', 'Total customers', 'How many males?', 'How many females?', 'How many from United States?', 'Count by country'",
            "Sum questions: 'Total sales', 'Sum of revenue', 'Total salaries', 'Grand total', 'Sum of ages', 'Total age sum'",
            "Average questions: 'Average salary', 'Mean age', 'Average revenue', 'Avg expense', 'Average age by gender', 'Mean age by country'",
            "Min/Max questions: 'Highest salary', 'Lowest revenue', 'Top sales', 'Worst performer', 'Oldest employee', 'Youngest employee', 'Maximum age', 'Minimum age'",
            "List/Show questions: 'Show all data', 'List employees', 'First 5 rows', 'Show columns', 'Show all employees', 'List all countries', 'Display data'",
            "Filtering questions: 'Employees in sales', 'Filter by department', 'Customers from USA', 'Employees from United States', 'Males only', 'Females only', 'Employees older than 30', 'Filter by age'",
            "Grouping questions: 'Group by department', 'Average salary by dept', 'Revenue by region', 'Count by gender', 'Sum by country', 'Average by country'",
            "Sorting questions: 'Sort by age', 'Order by name', 'Sort data by country', 'Order employees by id'",
            "Correlation questions: 'Correlation between age and salary', 'Show correlations', 'Correlation matrix'",
            "Time series: 'Sales trend', 'Monthly trend', 'Compare 2022 vs 2023', 'Trend of ages', 'Date distribution'",
            "Charts: 'Bar chart', 'Line chart', 'Pie chart', 'Histogram', 'Age distribution chart'",
            "Financial: 'Profit margin', 'ROI', 'Break even', 'Net profit'",
            "Data cleaning: 'Drop missing values', 'Remove duplicates', 'Rename columns'",
            "Text analytics: 'Sentiment analysis', 'Word cloud', 'Key topics'",
            "Geo: 'Sales by city', 'Revenue by region', 'Top 5 states', 'Employees by country'",
            "Export: 'Download CSV', 'Export Excel', 'Save chart as PNG'",
            "Comparisons: 'Compare sales', 'Year over year', 'Before and after', 'Compare genders', 'Compare countries'",
            "Explainability: 'Why revenue decreasing?', 'Business insights'",
            "Shortcuts: 'Top sellers', 'Best performers', 'Biggest customer'",
            "Predictive: 'Predict next age', 'Forecast age', 'Next value prediction', 'Trend prediction'"
        ]
        analysis.append("Supported analysis questions:")
        for q in supported_questions:
            analysis.append(f"  - {q}")
        return "\n".join(analysis)

    if 'count' in question_lower or 'number' in question_lower or 'how many' in question_lower:
        total_rows = len(df)
        analysis.append(f"The dataset has {total_rows} rows.")
        # Check for department counts
        dept_col = next((c for c in df.columns if 'dept' in c.lower() or 'department' in c.lower()), None)
        if dept_col and 'department' in question_lower:
            counts = df[dept_col].value_counts()
            analysis.append("Department distribution:")
            for dept, count in counts.head(5).items():
                analysis.append(f"  - {dept}: {count} employees")

    if 'average' in question_lower or 'mean' in question_lower:
        numeric_cols = df.select_dtypes(include=[float, int]).columns
        if len(numeric_cols) > 0:
            analysis.append("Average values:")
            for col in numeric_cols[:3]:  # Limit to first 3 numeric columns
                avg = df[col].mean()
                analysis.append(f"  - {col}: {avg:.2f}")

    if 'sum' in question_lower:
        numeric_cols = df.select_dtypes(include=[float, int]).columns
        if len(numeric_cols) > 0:
            analysis.append("Total sums:")
            for col in numeric_cols[:3]:
                total = df[col].sum()
                analysis.append(f"  - {col}: {total:.2f}")

    if 'show' in question_lower or 'list' in question_lower or 'display' in question_lower:
        analysis.append(f"Dataset preview (first 5 rows):")
        preview = df.head(5).to_string(index=False)
        analysis.append(preview)
        if 'sales' in question_lower:
            dept_col = next((c for c in df.columns if 'dept' in c.lower() or 'department' in c.lower()), None)
            if dept_col:
                sales_count = len(df[df[dept_col].str.lower() == 'sales'])
                analysis.append(f"Sales department has {sales_count} employees.")

    # Handle sorting
    if 'sort' in question_lower or 'order' in question_lower:
        # Find the column to sort by
        sort_col = None
        if 'age' in question_lower:
            sort_col = next((c for c in df.columns if 'age' in c.lower()), None)
        elif 'name' in question_lower:
            sort_col = next((c for c in df.columns if 'name' in c.lower()), None)
        elif 'country' in question_lower:
            sort_col = next((c for c in df.columns if 'country' in c.lower()), None)
        elif 'id' in question_lower:
            sort_col = next((c for c in df.columns if 'id' in c.lower()), None)
        else:
            # Default to first numeric or string column
            numeric_cols = df.select_dtypes(include=[float, int]).columns
            if len(numeric_cols) > 0:
                sort_col = numeric_cols[0]
            else:
                object_cols = df.select_dtypes(include=['object']).columns
                if len(object_cols) > 0:
                    sort_col = object_cols[0]

        if sort_col:
            ascending = 'desc' not in question_lower and 'descending' not in question_lower
            df_sorted = df.sort_values(by=sort_col, ascending=ascending)
            analysis.append(f"Data sorted by '{sort_col}' {'ascending' if ascending else 'descending'}:")
            preview = df_sorted.head(10).to_string(index=False)  # Show more rows for sorted view
            analysis.append(preview)
        else:
            analysis.append("No suitable column found for sorting.")

    # Handle correlation
    if 'correlation' in question_lower:
        numeric_cols = df.select_dtypes(include=[float, int]).columns
        if len(numeric_cols) > 1:
            corr_matrix = df[numeric_cols].corr()
            analysis.append("Correlation matrix:")
            analysis.append(corr_matrix.to_string())
        else:
            analysis.append("Not enough numeric columns for correlation analysis.")



    # Handle chart requests
    if 'pie' in question_lower or 'pie chart' in question_lower:
        cat_cols = df.select_dtypes(include=['object']).columns
        if len(cat_cols) > 0:
            cat_col = cat_cols[0]
            counts = df[cat_col].value_counts()
            analysis.append(f"Pie chart distribution for {cat_col}:")
            for value, count in counts.head(10).items():
                analysis.append(f"  - {value}: {count}")
        else:
            analysis.append("No categorical data available for pie chart.")

    if 'bar' in question_lower or 'bar chart' in question_lower:
        numeric_cols = df.select_dtypes(include=[float, int]).columns
        if len(numeric_cols) > 0:
            means = df[numeric_cols].mean()
            analysis.append("Bar chart of average values:")
            for col, avg in means.items():
                analysis.append(f"  - {col}: {avg:.2f}")
        else:
            analysis.append("No numeric data available for bar chart.")

    if 'line' in question_lower or 'line chart' in question_lower:
        date_cols = df.select_dtypes(include=['datetime']).columns
        numeric_cols = df.select_dtypes(include=[float, int]).columns
        if len(date_cols) > 0 and len(numeric_cols) > 0:
            df_sorted = df.sort_values(by=date_cols[0])
            analysis.append(f"Line chart trend for {numeric_cols[0]} over {date_cols[0]}:")
            analysis.append("Data points (first 5):")
            for i in range(min(5, len(df_sorted))):
                analysis.append(f"  - {df_sorted[date_cols[0]].iloc[i]}: {df_sorted[numeric_cols[0]].iloc[i]}")
        else:
            analysis.append("No date and numeric data available for line chart.")

    if not analysis:
        analysis.append("Unable to generate a detailed response. Please try a more specific question about counts, averages, sums, sorting, or listing data. Use 'list all analysis questions' to see supported options.")

    return "\n".join(analysis)

def audit_log(action: str, user_id: int = None, details: str = None):
    """Log audit events for security and monitoring."""
    logger = logging.getLogger('audit')
    if not logger.handlers:
        handler = logging.FileHandler('audit.log')
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

    message = f"Action: {action}"
    if user_id:
        message += f", User ID: {user_id}"
    if details:
        message += f", Details: {details}"
    logger.info(message)

def sanitize_string(input_string: str) -> str:
    """Sanitize input string to prevent XSS and other attacks."""
    if not input_string:
        return ""
    # Remove HTML tags
    import html
    sanitized = html.escape(input_string)
    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>]', '', sanitized)
    return sanitized.strip()
