from ortools.linear_solver import pywraplp
import numpy as np

def solve_inventory_allocation(W, M, d, cs, pr):
    # Compute derived parameters
    dv = np.array([v for (_, v) in d])
    pr_itemset = np.zeros((len(d), M))
    for s in range(len(d)):
        for m in range(M):
            items = d[s][0]
            for item in items:
                pr_itemset[s, m] += pr[item][m]
    
    # Solve the optimization problem
    solver = pywraplp.Solver.CreateSolver('GLOP')
    q = np.array([[[solver.NumVar(0.0, solver.infinity(), f'q{s}{w}{m}') 
                    for m in range(M)] 
                   for w in range(W)] 
                  for s in range(len(d))])

    for m in range(M): 
        for s in range(len(d)):
            solver.Add(np.sum(q[s, :, m]) <= dv[s][m])

    revenue = np.sum([[pr_itemset[s, m] * np.sum(q[s, :, m]) for m in range(M)] for s in range(len(d))])
    shipping_costs = np.sum(cs * np.sum(q, axis=0))
    solver.Maximize(revenue - shipping_costs)

    status = solver.Solve()

    if status == pywraplp.Solver.OPTIMAL:
        solution = {}
        for w in range(W):
            warehouse_solution = {}
            for item in pr.keys():
                warehouse_solution[item] = q[ord(item) - ord("a"), w, :].sum()
            solution[f'Warehouse {w}'] = warehouse_solution
        return solution, solver.Objective().Value()
    else:
        return None, None

# Example usage
W = 3  # Number of warehouses
M = 5  # Number of markets


# Demand by itemset and market
d = [
    ({'a'},           [10, 20, 30, 30, 20]), # orders with product a only
    ({'b'},           [20, 30, 10, 40, 10]), # orders with product b only
    ({'c'},           [40, 30, 10, 10, 20]), # orders with product c only
    ({'a', 'b'},      [5, 7, 3, 3, 8]),      # orders with a and b
    ({'b', 'c'},      [3, 9, 2, 1, 4]),      # orders with b and c
    ({'a', 'c'},      [7, 2, 5, 9, 7]),      # orders with a and c
    ({'a', 'b', 'c'}, [1, 0, 2, 1, 0])       # orders with a, b, and c
]

# Shipping costs (cost of shipping one unit from warehouse w to market m)
cs = np.array([
    [1.0, 1.0, 1.0, 1.0, 0.2],
    [1.0, 1.0, 0.5, 0.3, 0.5],
    [0.5, 0.3, 3.0, 0.5, 0.5]
])

# Product unit price by market
pr = {
    'a': [1, 2, 1, 3, 1], # product a
    'b': [2, 1, 1, 1, 2], # product b
    'c': [1, 2, 1, 1, 1]  # product c
}

solution, objective_value = solve_inventory_allocation(W, M, d, cs, pr)
if solution is not None:
    print("Optimal Solution:")
    print(f"Objective Value: {objective_value}")
    for warehouse, products in solution.items():
        print(f"{warehouse}:")
        for product, quantity in products.items():
            print(f"\t{product}: {quantity} units")
else:
    print("The problem does not have an optimal solution.")
