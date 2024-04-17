import tkinter as tk
from tkinter import messagebox, Canvas
from ortools.linear_solver import pywraplp
import numpy as np

def populate_gui_with_sample_input():
    warehouses_entry.insert(0, str(W))  # Number of warehouses
    markets_entry.insert(0, str(M))     # Number of markets

    # Populate demand data into GUI
    for i in range(len(d)):
        items, demands = d[i]
        itemset_entries[i].insert(0, ",".join(items))
        demand_entries[i].insert(0, ",".join(map(str, demands)))

    # Populate shipping costs into GUI
    for i in range(W):  # Number of warehouses
        for j in range(M):  # Number of markets
            shipping_cost_entries[i][j].insert(0, str(cs[i][j]))

    # Populate product unit prices into GUI
    for item, prices in pr.items():
        pr_entries[item].insert(0, ",".join(map(str, prices)))

def solve_allocation():
    try:
        # Copy the script provided
        W = 3 
        M = 5

        d = [
            ({'a'},           [10, 20, 30, 30, 20]), 
            ({'b'},           [20, 30, 10, 40, 10]), 
            ({'c'},           [40, 30, 10, 10, 20]), 
            ({'a', 'b'},      [5, 7, 3, 3, 8]),      
            ({'b', 'c'},      [3, 9, 2, 1, 4]),      
            ({'a', 'c'},      [7, 2, 5, 9, 7]),      
            ({'a', 'b', 'c'}, [1, 0, 2, 1, 0])       
        ]

        S = len(d)

        cs = np.array([
            [1.0, 1.0, 1.0, 1.0, 0.2],
            [1.0, 1.0, 0.5, 0.3, 0.5],
            [0.5, 0.3, 3.0, 0.5, 0.5]
        ])

        pr = {
            'a': [1, 2, 1, 3, 1],
            'b': [2, 1, 1, 1, 2],
            'c': [1, 2, 1, 1, 1]
        }

        dv = np.array([v for (k,v) in d])

        pr_itemset = np.zeros((S, M))
        for s in range(S):
            for m in range(M):
                items = d[s][0]
                for item in items:
                    pr_itemset[s, m] += pr[item][m]

        solver = pywraplp.Solver.CreateSolver('GLOP')

        q = np.array([[[solver.NumVar(0.0, solver.infinity(), f'q{s}{w}{m}') 
                        for m in range(M)] 
                       for w in range(W)] 
                      for s in range(S)])

        for m in range(M): 
            for s in range(S):
                solver.Add(np.sum(q[s, :, m]) <= dv[s, m])

        revenue = np.sum([[pr_itemset[s, m] * np.sum(q[s, :, m]) for m in range(M)] for s in range(S)])
        shipping_costs = np.sum(cs * np.sum(q, axis = 0) )
        solver.Maximize(revenue - shipping_costs)

        status = solver.Solve()

        if status == pywraplp.Solver.OPTIMAL:
            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, 'Solution:\n')
            output_text.insert(tk.END, f'Objective value = {solver.Objective().Value()}\n\n')
            for w in range(W):
                output_text.insert(tk.END, f'\nWarehouse {w}:\n')
                
                total_units = {}
                for item in pr.keys():
                    total_units[item] = 0
                
                for s in range(S):
                    quantity = sum(q[s, w, m].solution_value() for m in range(M))
                    items = d[s][0]
                    for item in items:
                        total_units[item] += quantity
                    
                for item in pr.keys():
                    output_text.insert(tk.END, f'\tProduct {item} : {total_units[item]} units\n')
                
                output_text.insert(tk.END, '\tBreakdown by itemsets:\n')
                for s in range(S):
                    quantity = sum(q[s, w, m].solution_value() for m in range(M))
                    output_text.insert(tk.END, f'\t\t{d[s][0]} : {quantity} units\n')
                
        else:
            messagebox.showerror("Error", "The problem does not have an optimal solution.")
    except ValueError:
        messagebox.showerror("Error", "Please enter valid numerical values.")


# Create the GUI
root = tk.Tk()
root.title("Inventory Allocation Solver")

# Create a canvas widget with a horizontal scrollbar
canvas = Canvas(root)
canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

scrollbar = tk.Scrollbar(root, orient=tk.HORIZONTAL, command=canvas.xview)
scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

canvas.configure(xscrollcommand=scrollbar.set)
canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

# Frame inside the canvas
frame = tk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor="nw")

# Labels and Entry for Number of Warehouses and Markets
tk.Label(frame, text="Number of Warehouses:").grid(row=0, column=0)
warehouses_entry = tk.Entry(frame)
warehouses_entry.grid(row=0, column=1)

tk.Label(frame, text="Number of Markets:").grid(row=1, column=0)
markets_entry = tk.Entry(frame)
markets_entry.grid(row=1, column=1)

# Itemset Labels and Entry
itemset_labels = []
itemset_entries = []

# Add itemset labels
for i in range(7): # Number of itemsets
    itemset_labels.append(tk.Label(frame, text=f"Itemset {i+1} (comma-separated items):"))
    itemset_labels[-1].grid(row=i+2, column=0)

    itemset_entries.append(tk.Entry(frame))
    itemset_entries[-1].grid(row=i+2, column=1)

# Labels and Entry for Demand
demand_labels = []
demand_entries = []
for i in range(7): # Number of itemsets
    demand_labels.append(tk.Label(frame, text=f"Demand for Itemset {i+1} (comma-separated values):"))
    demand_labels[-1].grid(row=i+9, column=0)

    demand_entries.append(tk.Entry(frame))
    demand_entries[-1].grid(row=i+9, column=1)

# Labels and Entry for Shipping Costs
shipping_cost_labels = []
shipping_cost_entries = []

for i in range(3): # Number of warehouses
    shipping_cost_labels.append(tk.Label(frame, text=f"Shipping Costs for Warehouse {i} (comma-separated values):"))
    shipping_cost_labels[-1].grid(row=i, column=3)

    shipping_cost_entries.append([])
    for j in range(5): # Number of markets
        shipping_cost_entries[-1].append(tk.Entry(frame))
        shipping_cost_entries[-1][-1].grid(row=i, column=j+4)

# Labels and Entry for Product Unit Prices
pr_labels = {}
pr_entries = {}

for i, item in enumerate(['a', 'b', 'c']):
    pr_labels[item] = tk.Label(frame, text=f"Unit Prices for Product {item} (comma-separated values):")
    pr_labels[item].grid(row=i, column=9) # Adjust column position

    pr_entries[item] = tk.Entry(frame)
    pr_entries[item].grid(row=i, column=10) # Adjust column position

# Button to solve
solve_button = tk.Button(frame, text="Solve", command=solve_allocation)
solve_button.grid(row=16, columnspan=3) # Adjusted row position

# Output Text Area
output_text = tk.Text(frame, height=10, width=80)
output_text.grid(row=17, columnspan=5) # Adjusted row position

# Populate GUI with sample input values
populate_gui_with_sample_input()

root.mainloop()

