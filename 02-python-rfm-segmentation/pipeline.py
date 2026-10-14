import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Paths configuration
DATA_DIR = "data"
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def run_pipeline():
    print("🚀 Starting Olist E-Commerce Logistics Pipeline...")

    orders_path = os.path.join(DATA_DIR, "olist_orders_dataset.csv")
    customers_path = os.path.join(DATA_DIR, "olist_customers_dataset.csv")

    if not os.path.exists(orders_path) or not os.path.exists(customers_path):
        print("❌ Error: Missing CSV files inside the 'data/' folder. Please ensure Olist files are placed there.")
        return

    # 1. Ingestion
    print("📥 Loading raw datasets...")
    orders_df = pd.read_csv(orders_path)
    customers_df = pd.read_csv(customers_path)

    # 2. Data Cleaning & Transformation
    print("🧹 Cleaning and transforming data...")
    # Convert date columns to datetime objects
    date_columns = [
        'order_purchase_timestamp', 
        'order_approved_at', 
        'order_delivered_carrier_date', 
        'order_delivered_customer_date', 
        'order_estimated_delivery_date'
    ]
    for col in date_columns:
        orders_df[col] = pd.to_datetime(orders_df[col], errors='coerce')

    # Filter for only delivered orders to analyze real shipping times
    delivered_orders = orders_df[orders_df['order_status'] == 'delivered'].copy()

    # Calculate Delivery Delay: Actual Delivery Date minus Estimated Delivery Date (in days)
    # Positive value = Late delivery, Negative/Zero = Early or On-time
    delivered_orders['delivery_delay_days'] = (
        delivered_orders['order_delivered_customer_date'] - delivered_orders['order_estimated_delivery_date']
    ).dt.total_seconds() / 86400.0

    # 3. Merge Orders with Customer Geography
    print("🔗 Merging orders with customer state data...")
    merged_df = pd.merge(delivered_orders, customers_df[['customer_id', 'customer_state']], on='customer_id', how='inner')

    # 4. Analytical Processing: Delivery Performance by State
    state_summary = merged_df.groupby('customer_state').agg(
        total_orders=('order_id', 'count'),
        avg_delay_days=('delivery_delay_days', 'mean'),
        pct_delayed=('delivery_delay_days', lambda x: (x > 0).mean() * 100)
    ).reset_index().sort_values(by='avg_delay_days', ascending=False)

    # Save summary report
    summary_csv_path = os.path.join(OUTPUT_DIR, 'state_delivery_performance.csv')
    state_summary.to_csv(summary_csv_path, index=False)
    print(f"✅ Saved summary report to {summary_csv_path}")

    # 5. Visualization Generation
    print("📈 Generating logistics bottleneck visualization...")
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")

    # Plot top 10 states with the worst average delivery delays
    top_delayed_states = state_summary.head(10)
    ax = sns.barplot(data=top_delayed_states, x='customer_state', y='avg_delay_days', hue='customer_state', palette='Reds_r', legend=False)

    plt.title('Top 10 Customer States by Average Delivery Delay (Days)', fontsize=14, fontweight='bold')
    plt.xlabel('Customer State', fontsize=12)
    plt.ylabel('Average Delay (Days)', fontsize=12)
    plt.tight_layout()

    chart_path = os.path.join(OUTPUT_DIR, 'worst_delivery_delays_by_state.png')
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"✨ Visualization saved to {chart_path}")

if __name__ == "__main__":
    run_pipeline()