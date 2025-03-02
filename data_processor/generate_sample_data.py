import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import uuid
import os

# Generate sample sales data
def generate_sales_data(num_records=100):
    # Generate random order IDs
    order_ids = [str(uuid.uuid4())[:8] for _ in range(num_records)]
    
    # Generate random product IDs
    product_ids = [f"PROD-{np.random.randint(1000, 9999)}" for _ in range(num_records)]
    
    # Generate quantities (between 1 and 10)
    quantities = np.random.randint(1, 11, num_records)
    
    # Generate prices (between $10 and $1000)
    prices = np.round(np.random.uniform(10, 1000, num_records), 2)
    
    # Generate order dates (past 30 days)
    today = datetime.now()
    order_dates = [(today - timedelta(days=np.random.randint(0, 30))).strftime('%Y-%m-%d') 
                   for _ in range(num_records)]
    
    # Create DataFrame
    df = pd.DataFrame({
        'order_id': order_ids,
        'product_id': product_ids,
        'quantity': quantities,
        'price': prices,
        'order_date': order_dates
    })
    
    return df

# Save to CSV
if __name__ == "__main__":
    # Create sample data directory if it doesn't exist
    os.makedirs("sample_data", exist_ok=True)
    
    # Generate and save multiple sample reports
    for i in range(3):
        df = generate_sales_data(num_records=50)
        filename = f"sample_data/sales_report_{i+1}.csv"
        df.to_csv(filename, index=False)
        print(f"Generated {filename}") 