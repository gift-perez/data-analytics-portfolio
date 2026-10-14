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
    print("🚀 Starting Advanced Olist Logistics & Freight Pipeline...")

    orders_path = os.path.join(DATA_DIR, "olist_orders_dataset.csv")
    customers_path = os.path.join(DATA_DIR, "olist_customers_dataset.csv")
    items_path = os.path.join(DATA_DIR, "olist_order_items_dataset.csv")

    if not os.path.exists(orders_path) or not os.path.exists(customers_path) or not os.path.exists(items_path):
        print("❌ Error: Missing Olist CSV files inside the 'data/' folder.")
        return

    # 1. Ingestion
    print("📥 Loading multi-table datasets...")
    orders_df = pd.read_csv(orders_path)
    customers_df = pd.read_csv(customers_path)
    items_df = pd.read_csv(items_path)

    # 2. Data Cleaning & Transformation
    print("🧹 Cleaning timestamps and filtering delivered orders...")
    date_columns = [
        'order_purchase_timestamp', 
        'order_approved_at', 
        'order_delivered_carrier_date', 
        'order_delivered_customer_date', 
        'order_estimated_delivery_date'
    ]
    for col in date_columns:
        orders_df[col] = pd.to_datetime(orders_df[col], errors='coerce')

    delivered_orders = orders_df[orders_df['order_status'] == 'delivered'].copy()

    # Calculate Delivery Delay (Actual vs Estimated in Days)
    delivered_orders['delivery_delay_days'] = (
        delivered_orders['order_delivered_customer_date'] - delivered_orders['order_estimated_delivery_date']
    ).dt.total_seconds() / 86400.0

    # 3. Aggregate Item & Freight Costs per Order
    print("📦 Aggregating order items and freight costs...")
    order_freight_summary = items_df.groupby('order_id').agg(
        total_items=('order_item_id', 'count'),
        total_freight_value=('freight_value', 'sum'),
        total_product_value=('price', 'sum')
    ).reset_index()

    # 4. Multi-Table Relational Merges
    print("🔗 Performing multi-table relational joins...")
    # Merge orders with freight metrics
    orders_with_freight = pd.merge(delivered_orders, order_freight_summary, on='order_id', how='left')
    # Merge with customer states
    full_merged_df = pd.merge(orders_with_freight, customers_df[['customer_id', 'customer_state']], on='customer_id', how='inner')

    # 5. Advanced Analytical Processing
    state_summary = full_merged_df.groupby('customer_state').agg(
        total_orders=('order_id', 'count'),
        avg_delay_days=('delivery_delay_days', 'mean'),
        median_delay_days=('delivery_delay_days', 'median'),
        avg_freight_value=('total_freight_value', 'mean')
    ).reset_index().sort_values(by='avg_delay_days', ascending=False)

    summary_csv_path = os.path.join(OUTPUT_DIR, 'advanced_state_logistics_summary.csv')
    state_summary.to_csv(summary_csv_path, index=False)
    print(f"✅ Saved advanced summary report to {summary_csv_path}")

    # 6. Visualization 1: Average Delays Barplot
    print("📈 Generating average delivery delay visualization...")
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")
    top_delayed_states = state_summary.head(10)
    sns.barplot(
        data=top_delayed_states, 
        x='customer_state', 
        y='avg_delay_days', 
        hue='customer_state', 
        palette='Reds_r', 
        legend=False
    )
    plt.title('Top 10 Customer States by Average Delivery Delay (Days)', fontsize=14, fontweight='bold')
    plt.xlabel('Customer State', fontsize=12)
    plt.ylabel('Average Delay (Days)', fontsize=12)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'worst_delivery_delays_by_state.png'), dpi=300)
    plt.close()

    # 7. Visualization 2: Statistical Boxplot (Delay Variance & Outliers)
    print("📊 Generating statistical boxplot for delay distribution...")
    plt.figure(figsize=(12, 6))
    # Select top 8 states by order volume to keep the boxplot readable
    top_volume_states = full_merged_df['customer_state'].value_counts().head(8).index
    filtered_states_df = full_merged_df[full_merged_df['customer_state'].isin(top_volume_states)]

    sns.boxplot(
        data=filtered_states_df, 
        x='customer_state', 
        y='delivery_delay_days', 
        hue='customer_state',
        palette='Blues',
        legend=False,
        showfliers=False # Hides extreme outliers for clean executive presentation
    )
    plt.axhline(0, color='red', linestyle='--', linewidth=1.5, label='On-Time Threshold (0 Days)')
    plt.title('Delivery Delay Variance & Distribution Across Top 8 States', fontsize=14, fontweight='bold')
    plt.xlabel('Customer State', fontsize=12)
    plt.ylabel('Delivery Delay (Days)', fontsize=12)
    plt.legend(loc='upper right')
    plt.tight_layout()
    
    boxplot_path = os.path.join(OUTPUT_DIR, 'delivery_delay_distribution.png')
    plt.savefig(boxplot_path, dpi=300)
    plt.close()
    print(f"✨ Statistical boxplot saved to {boxplot_path}")
    print("✨ Advanced Olist Pipeline completed successfully!")

if __name__ == "__main__":
    run_pipeline()