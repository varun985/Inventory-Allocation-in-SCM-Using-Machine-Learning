# Inventory-Allocation-in-SCM-Using-Machine-Learning
Using Linear Programming
Problem Definition: The problem involves allocating inventory across multiple warehouses to serve various markets. There are different products (SKUs) and itemsets (combinations of products) with different demands in each market. 

Data Setup: The number of warehouses (W) and markets (M) is defined. Demand for each itemset in each market is specified (d). Shipping costs from each warehouse to each market are provided (cs). Product unit prices by market are defined (pr). 

Derived Parameters: The derived parameters include demand by itemset and market (dv) and prices for all itemsets (pr_itemset). 

Optimization Problem Setup: The problem is formulated as a linear programming task using the Google OR-Tools library (pywraplp). Decision variables (q) are defined to represent the quantity of each itemset allocated in each warehouse for each market. Constraints are set to ensure that the total quantity of each itemset allocated in all warehouses does not exceed the demand for that itemset in each market. The objective function is defined to maximize revenue (total sales) minus shipping costs. 

Solution: The linear programming solver (GLOP) is used to find the optimal solution. If an optimal solution is found, the results are printed, including the objective value (total profit) and the allocation breakdown for each warehouse, product, and itemset.
