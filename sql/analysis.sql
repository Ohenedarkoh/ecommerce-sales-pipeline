--- reads PostgreSQLs metadata to show the columns and types in the four tables
SELECT 
	table_name,
	column_name,
	data_type
FROM information_schema.columns
WHERE table_schema = 'public'
	AND table_name IN ('customers','locations','products','orders')
ORDER BY table_name, ordinal_position;

-- 1   Sales and profit overview	
-- 2	Performance by product category and subcategory	(GROUP BY, ORDER BY)
-- 3	Top-performing products	(Aggregation, sorting, limiting)
-- 4	Regional sales and profitability	(JOIN, GROUP BY)
-- 5	Monthly sales and profit trends	(Date functions, aggregation)
-- 6	Top customers by sales	(Aggregation, ranking)
-- 7	Products with low or negative profit	(Filtering and business logic)
-- 8	Advanced analysis



---overall sales and profit
SELECT 
	sum(sales) as total_sales,
	sum(profit) as total_profit,
	sum(quantity) as total_quantity_sold,
	count(distinct order_id )as number_of_distinct_orders,
	round(sum(sales)/count(distinct order_id),2) as average_sales_per_order,
	round((sum(profit)/sum(sales))*100,2) as overall_profit_margin
FROM orders;


---sales and profit by category
SELECT 
	prod_cat.category,
	round(sum(sales),1) as total_sales, 
	round(sum(profit),1) as total_profit
FROM orders 
join (
	SELECT distinct 
		product_id,
		category
	FROM products
	) 
	as prod_cat
	on orders.product_id = prod_cat.product_id
group by prod_cat.category
order by total_sales desc;


---sales and profit by subcategory
SELECT 
	prod_cat.sub_category,
	round(sum(sales),1) as total_sales, 
	round(sum(profit),1) as total_profit
FROM orders 
join (
	SELECT distinct 
		product_id,
		sub_category
	FROM products
	) 
	as prod_cat
	on orders.product_id = prod_cat.product_id
group by prod_cat.sub_category
order by total_sales desc;


--validating if each product_id maps to only one sub_category
SELECT
    product_id,
    COUNT(DISTINCT sub_category) AS subcategory_count
FROM products
GROUP BY product_id
HAVING COUNT(DISTINCT sub_category) > 1;



---sales and profit by region
SELECT 
	region,
	round(sum(sales),1) as total_sales, 
	round(sum(profit),1) as total_profit
FROM orders
JOIN locations
ON orders.location_id= locations.location_id
GROUP BY region
order by total_sales desc;


--validation to confirm that location_id is unique in locations
SELECT location_id, COUNT(*)
FROM locations
GROUP BY location_id
HAVING COUNT(*) > 1;



---Monthly sales and profit trends
SELECT 
	extract(year from order_date) as order_year,
	extract(month from order_date) as order_month,
	round(sum(sales),1) as total_sales, 
	round(sum(profit),1) as total_profit
FROM orders
group by order_year,order_month
order by order_year asc, order_month asc;


---Top 10 customers by sales
SELECT 
	customers.customer_id,	
	customers.customer_name,
	round(sum(sales),1) as total_sales, 
	round(sum(profit),1) as total_profit
FROM orders
JOIN customers
ON orders.customer_id =  customers.customer_id
group by customers.customer_id,customers.customer_name
order by total_sales desc, total_profit desc
limit 10;


---Product_ids with the highest sales
SELECT
	product_id,
	round(sum(sales),1) as total_sales, 
	round(sum(profit),1) as total_profit
FROM orders
GROUP BY product_id
ORDER BY total_sales desc
limit 10;


---Products with Negative total profit
SELECT
	product_id,
	round(sum(sales),1) as total_sales, 
	round(sum(profit),1) as total_profit
FROM orders
GROUP BY product_id
HAVING round(sum(profit),1)<0
ORDER BY total_profit asc;



---Sales and Profit by Shipping Mode
SELECT
	ship_mode,
	count(distinct order_id) as number_of_orders,
	round(sum(sales),1) as total_sales, 
	round(sum(profit),1) as total_profit
FROM orders
GROUP BY ship_mode
ORDER BY total_sales desc;


---Customer sales ranking
WITH  customer_sales as (
	SELECT 
		customers.customer_id,
		customers.customer_name,
		round(sum(sales),1) as total_sales, 
		round(sum(profit),1) as total_profit
	FROM orders
	JOIN customers
		ON orders.customer_id = customers.customer_id 
	GROUP BY customers.customer_id,customers.customer_name
)
SELECT 
	customer_id,
	customer_name,
	total_sales,
	total_profit,
	RANK() OVER(ORDER BY total_sales desc) as sales_rank,
	ROUND((total_sales / 2297200.8603) * 100, 2) AS sales_contribution_pct
FROM customer_sales
ORDER BY sales_rank
limit 10;
