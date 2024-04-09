import tkinter as tk
from tkinter import messagebox
from ortools.linear_solver import pywraplp
import numpy as np

def solve_allocation():
    try:
        # Retrieve inputs from the GUI
        W = int(warehouses_entry.get())  # Number of warehouses
        M = int(markets_entry.get())     # Number of markets
        
        # Parse demand data
        d = []
        for i in range(M):
            items = set(itemset_entries[i].get().split(','))
            demands = list(map(int, demand_entries[i].get().split(',')))
            d.append((items, demands))
        
        # Parse shipping costs
        cs = np.zeros((W, M))
        for i in range(W):
            for j in range(M):
                cs[i, j] = float(shipping_cost_entries[i][j].get())
        
        # Parse product unit prices
        pr = {}
        for item in pr_entries.keys():
            prices = list(map(int, pr_entries[item].get().split(',')))
            pr[item] = prices
        
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
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, 'Optimal Solution:\n')
            output_text.insert(tk.END, f'Objective value = {solver.Objective().Value()}\n\n')
            for w in range(W):
                output_text.insert(tk.END, f'Warehouse {w}:\n')
                for item in pr.keys():
                    output_text.insert(tk.END, f'\tProduct {item} : {q[ord(item) - ord("a"), w, :].sum()} units\n')
                output_text.insert(tk.END, '\n')
        else:
            messagebox.showerror("Error", "The problem does not have an optimal solution.")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numerical values.")

def add_itemset():
    itemset_labels.append(tk.Label(root, text=f"Itemset {len(itemset_labels)+1} (comma-separated items):"))
    itemset_labels[-1].grid(row=len(itemset_labels)+1, column=0)
    
    itemset_entries.append(tk.Entry(root))
    itemset_entries[-1].grid(row=len(itemset_entries)+1, column=1)

# Create the GUI
root = tk.Tk()
root.title("Inventory Allocation Solver")

# Labels and Entry for Number of Warehouses and Markets
tk.Label(root, text="Number of Warehouses:").grid(row=0, column=0)
warehouses_entry = tk.Entry(root)
warehouses_entry.grid(row=0, column=1)

tk.Label(root, text="Number of Markets:").grid(row=1, column=0)
markets_entry = tk.Entry(root)
markets_entry.grid(row=1, column=1)

# Button to add itemset
add_itemset_button = tk.Button(root, text="Add Itemset", command=add_itemset)
add_itemset_button.grid(row=2, column=2)

# Itemset Labels and Entry
itemset_labels = []
itemset_entries = []

# Add initial itemset fields
add_itemset()

# Labels and Entry for Demand
demand_labels = []
demand_entries = []
for i in range(5):
    demand_labels.append(tk.Label(root, text=f"Demand for Itemset {i+1} (comma-separated values):"))
    demand_labels[-1].grid(row=i+3, column=0)
    
    demand_entries.append(tk.Entry(root))
    demand_entries[-1].grid(row=i+3, column=1)

# Labels and Entry for Shipping Costs
shipping_cost_labels = []
shipping_cost_entries = []

for i in range(3):
    shipping_cost_labels.append(tk.Label(root, text=f"Shipping Costs for Warehouse {i} (comma-separated values):"))
    shipping_cost_labels[-1].grid(row=i, column=3)
    
    shipping_cost_entries.append([])
    for j in range(5):  # Assuming 5 markets
        shipping_cost_entries[-1].append(tk.Entry(root))
        shipping_cost_entries[-1][-1].grid(row=i, column=j+4)

# Labels and Entry for Product Unit Prices
pr_labels = {}
pr_entries = {}

for i, item in enumerate(['a', 'b', 'c']):
    pr_labels[item] = tk.Label(root, text=f"Unit Prices for Product {item} (comma-separated values):")
    pr_labels[item].grid(row=i, column=8)  # Adjust column position
    
    pr_entries[item] = tk.Entry(root)
    pr_entries[item].grid(row=i, column=9)  # Adjust column position

# Button to solve
solve_button = tk.Button(root, text="Solve", command=solve_allocation)
solve_button.grid(row=10, columnspan=3)

# Output Text Area
output_text = tk.Text(root, height=10, width=80)
output_text.grid(row=11, columnspan=5)

root.mainloop()
