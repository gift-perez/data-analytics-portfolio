-- =================================================================
-- Project: Coffee Shop Sales Data Analysis
-- File: analytics.sql
-- Description: Data integrity checks, menu matrix, and window functions
-- =================================================================

-- Check for missing values or invalid transaction amounts
SELECT 
    COUNT(*) AS total_rows,
    SUM(CASE WHEN coffee_name IS NULL THEN 1 ELSE 0 END) AS missing_coffee_names,
    SUM(CASE WHEN money <= 0 THEN 1 ELSE 0 END) AS invalid_money_amounts,
    COUNT(DISTINCT coffee_name) AS unique_coffee_items
FROM coffee_transactions;-- Check for missing values or invalid transaction amounts
SELECT 
    COUNT(*) AS total_rows,
    SUM(CASE WHEN coffee_name IS NULL THEN 1 ELSE 0 END) AS missing_coffee_names,
    SUM(CASE WHEN money <= 0 THEN 1 ELSE 0 END) AS invalid_money_amounts,
    COUNT(DISTINCT coffee_name) AS unique_coffee_items
FROM coffee_transactions;

-- Check for missing values or invalid transaction amounts
SELECT 
    COUNT(*) AS total_rows,
    SUM(CASE WHEN coffee_name IS NULL THEN 1 ELSE 0 END) AS missing_coffee_names,
    SUM(CASE WHEN money <= 0 THEN 1 ELSE 0 END) AS invalid_money_amounts,
    COUNT(DISTINCT coffee_name) AS unique_coffee_items
FROM coffee_transactions;

-- Check for missing values or invalid transaction amounts
SELECT 
    COUNT(*) AS total_rows,
    SUM(CASE WHEN coffee_name IS NULL THEN 1 ELSE 0 END) AS missing_coffee_names,
    SUM(CASE WHEN money <= 0 THEN 1 ELSE 0 END) AS invalid_money_amounts,
    COUNT(DISTINCT coffee_name) AS unique_coffee_items
FROM coffee_transactions;

-- =================================================================
-- 4. Advanced Ranking with Window Functions (Top Coffee by Time of Day)
-- Uses DENSE_RANK() to find the best-selling coffee for each time slot (Morning, Afternoon, Night)
-- =================================================================
WITH ranked_coffee_by_time AS (
    SELECT 
        time_of_day,
        coffee_name,
        COUNT(transaction_id) AS total_orders,
        SUM(money) AS total_revenue,
        DENSE_RANK() OVER (PARTITION BY time_of_day ORDER BY SUM(money) DESC) as revenue_rank
    FROM coffee_transactions
    WHERE time_of_day IS NOT NULL
    GROUP BY time_of_day, coffee_name
)
SELECT 
    time_of_day,
    coffee_name,
    total_orders,
    ROUND(total_revenue, 2) AS total_revenue
FROM ranked_coffee_by_time
irth WHERE revenue_rank = 1;


-- =================================================================
-- 5. Day-of-Week Revenue Performance (Categorical Aggregation)
-- Analyzes which weekdays drive the highest sales volume
-- =================================================================
SELECT 
    weekday,
    weekdaysort,
    COUNT(transaction_id) AS total_transactions,
    ROUND(SUM(money), 2) AS total_revenue,
    ROUND(AVG(money), 2) AS average_ticket_size
FROM coffee_transactions
GROUP BY weekday, weekdaysort
ORDER BY weekdaysort ASC;


-- =================================================================
-- 6. Daily Running Revenue Growth (Time-Series Cumulative Sum)
-- Tracks how total revenue accumulates day-by-day across the dataset
-- =================================================================
WITH daily_revenue AS (
    SELECT 
        transaction_date,
        SUM(money) AS daily_total
    FROM coffee_transactions
    GROUP BY transaction_date
)
SELECT 
    transaction_date,
    ROUND(daily_total, 2) AS daily_total,
    ROUND(SUM(daily_total) OVER (ORDER BY transaction_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW), 2) AS cumulative_revenue
FROM daily_revenue
ORDER BY transaction_date ASC;

-- =================================================================
-- 7. Payment Method Analysis (Cash vs. Card Impact)
-- Compares transaction volume, revenue share, and average ticket size by payment type
-- =================================================================
SELECT 
    cash_type,
    COUNT(transaction_id) AS total_transactions,
    ROUND(SUM(money), 2) AS total_revenue,
    ROUND(AVG(money), 2) AS average_ticket_size,
    ROUND(100.0 * COUNT(transaction_id) / SUM(COUNT(transaction_id)) OVER (), 2) AS transaction_percentage_share
FROM coffee_transactions
GROUP BY cash_type
ORDER BY total_revenue DESC;

-- =================================================================
-- 8. Transaction Tier Segmentation (Percentile Distribution)
-- Classifies orders into spending tiers using NTILE() to spot premium purchases
-- =================================================================
WITH categorized_transactions AS (
    SELECT 
        transaction_id,
        coffee_name,
        money,
        NTILE(4) OVER (ORDER BY money DESC) AS spending_quartile -- 1 = Top 25% highest spending orders
    FROM coffee_transactions
)
SELECT 
    spending_quartile,
    CASE 
        WHEN spending_quartile = 1 THEN 'Tier 1: Premium Orders (Top 25%)'
        WHEN spending_quartile = 2 THEN 'Tier 2: High-Mid Orders'
        WHEN spending_quartile = 3 THEN 'Tier 3: Low-Mid Orders'
        WHEN spending_quartile = 4 THEN 'Tier 4: Economy Orders (Bottom 25%)'
    END AS tier_description,
    COUNT(transaction_id) AS total_orders,
    ROUND(MIN(money), 2) AS min_order_value,
    ROUND(MAX(money), 2) AS max_order_value,
    ROUND(AVG(money), 2) AS avg_tier_value
FROM categorized_transactions
GROUP BY spending_quartile
ORDER BY spending_quartile ASC;