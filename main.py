from ortools.linear_solver import pywraplp
import numpy as np

def solve_optimization(W, M, demands, shipping_costs, prices):
    S = len(demands)  # Number of itemsets

    # Compute derived parameters
    demands_vector = np.array([v for (_, v) in demands])
    pr_itemset = np.zeros((S, M))
    for s in range(S):
        for m in range(M):
            items = demands[s][0]
            for item in items:
                pr_itemset[s, m] += prices[item][m]

    # Solve the optimization problem
    solver = pywraplp.Solver.CreateSolver('GLOP')

    # Define variables
    q = np.array([[[solver.NumVar(0.0, solver.infinity(), f'q{s}{w}{m}') 
                    for m in range(M)] 
                   for w in range(W)] 
                  for s in range(S)])

    # Define constraints
    for m in range(M): 
        for s in range(S):
            solver.Add(np.sum(q[s, :, m]) <= demands_vector[s, m])

    # Define the objective
    revenue = np.sum([[pr_itemset[s, m] * np.sum(q[s, :, m]) for m in range(M)] for s in range(S)])
    shipping_costs_total = np.sum(shipping_costs * np.sum(q, axis=0))
    solver.Maximize(revenue - shipping_costs_total)

    # Solve 
    status = solver.Solve()

    # Print the results
    solution_value = np.vectorize(lambda x: x.solution_value())
    
    if status == pywraplp.Solver.OPTIMAL:
        print('Solution:')
        print('Objective value =', solver.Objective().Value())

        q_sw = np.zeros((S, W))
        for s in range(S):
            for w in range(W):
                q_sw[s, w] = np.sum(solution_value(q[s, w, :]))

        q_pw = {p : np.zeros(W) for p in prices.keys()}
        for w in range(W):
            for s in range(S):
                for i in demands[s][0]:
                    q_pw[i][w] += q_sw[s, w]

        for w in range(W):
            print(f'\nWarehouse {w}:')
            for k,v in q_pw.items():
                print(f'\tProduct {k} : {v[w]} units')

            print(f'\tBreakdown by itemsets:')
            for s in range(S):
                print(f'\t\t{demands[s][0]} : {q_sw[s, w]}')
            
    else:
        print('The problem does not have an optimal solution.')

# Example usage
W = 3  # Number of warehouses
M = 5  # Number of markets

# Demand by itemset and market
demands = [
    ({'a'},           [10, 20, 30, 30, 20]), # orders with product a only
    ({'b'},           [20, 30, 10, 40, 10]), # orders with product b only
    ({'c'},           [40, 30, 10, 10, 20]), # orders with product c only
    ({'a', 'b'},      [5, 7, 3, 3, 8]),      # orders with a and b
    ({'b', 'c'},      [3, 9, 2, 1, 4]),      # orders with b and c
    ({'a', 'c'},      [7, 2, 5, 9, 7]),      # orders with a and c
    ({'a', 'b', 'c'}, [1, 0, 2, 1, 0])       # orders with a, b, and c
]

# Shipping costs (cost of shipping one unit from warehouse w to market m)
shipping_costs = np.array([
    [1.0, 1.0, 1.0, 1.0, 0.2],
    [1.0, 1.0, 0.5, 0.3, 0.5],
    [0.5, 0.3, 3.0, 0.5, 0.5]
])

# Product unit price by market
prices = {
    'a': [1, 2, 1, 3, 1], # product a
    'b': [2, 1, 1, 1, 2], # product b
    'c': [1, 2, 1, 1, 1]  # product c
}

# Solve the optimization problem
solve_optimization(W, M, demands, shipping_costs, prices)
