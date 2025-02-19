# -*- coding: utf-8 -*-

from pulp import GLPK
from pulp import LpProblem, LpMaximize, LpMinimize, LpVariable, GLPK, lpSum

# Constants
BIG_M = 100000

def lsp1(cost_h, cost_k, cost_p, init_inv, requirements):
    """Solving the uncapacitated lot sizing problem
    with time-varying production costs (ULSP_TVP).

    This function generates the ULSP_TVP formulation in PuLP
    and solves it using the GLPK solver.

    Parameters
    ----------
    cost_h       : holding costs h [EUR/kg/period]
    cost_k       : fixed setup costs K [EUR/setup]
    cost_p       : a list with the production costs P_t [EUR/kg]
    init_inv     : the initial inventory [kg]
    requirements : a list with the requirements [kg] for each period

    Returns
    -------
    obj_val      : the objective value [EUR] after optimization
    setups       : a list with the setup decision per period
    """

    # Define parameters
    nr_periods = len(requirements)

    # Model Decleration

    model = LpProblem("Period dependent production costs", LpMinimize)

    # Decision Variables 

    x1 = {i: LpVariable(name=f"x1_{i}", cat="Binary") for i in range(nr_periods)}  # Order setup
    x2 = {i: LpVariable(name=f"x2_{i}", lowBound=0) for i in range(nr_periods)}  # Inventory level
    y = {i: LpVariable(name=f"y_{i}", lowBound=0) for i in range(nr_periods)} # Production Quantity (modification to existing LP problem)

    # Objective function

    model += lpSum(cost_h * x2[i] + cost_k * x1[i] + cost_p[i]*y[i] for i in range(nr_periods))

    # Model Constraints 
    
    for i in range(nr_periods):
        if i == 0:
            model += x2[i] == init_inv + y[i] - requirements[i]
        else:
            model += x2[i] == x2[i - 1] + y[i] - requirements[i]


    for i in range(nr_periods):
        model += y[i] <= BIG_M * x1[i]  
        model += x2[i] >= 0 

    for i in range(nr_periods):
        model += y[i] >= 0
    
    # Default return values = No solution found
    obj_val = 0
    setups = [0]*nr_periods

    if model is None:
        # Worst case: produce every period with a net requirement (=L4L)
        obj_val = 0
        inventory = init_inv
        for per in range(nr_periods):
            net_req = max(0, requirements[per] - inventory)
            if net_req > 0:
                setups[per] = 1
                inventory += net_req
                obj_val += cost_k + cost_p[per]*net_req
            inventory -= requirements[per]
            obj_val += cost_h*inventory
        return obj_val, setups
    
    model.solve(GLPK(msg=False, options=['--tmlim', '10']))

    if model.status != 1:
        return model.status, setups
    
    # Retrieve the objective value
    obj_val = model.objective.value()

    # Retrieve the setup decisions   
    for i in range(nr_periods):
         setups[i] = int(x1[i].value()) 


    return obj_val, setups

def lsp2(cost_h, cost_k, init_inv, requirements):
    """Solving the uncapacitated lot sizing problem
    with non-consecutive setups (ULSP_NCS).

    This function generates the ULSP_NCS formulation in PuLP
    and solves it using the GLPK solver.

    Parameters
    ----------
    cost_h       : holding costs h [EUR/kg/period]
    cost_k       : fixed setup costs K [EUR/setup]
    init_inv     : a list with the initial inventories [kg]
    requirements : a list with the requirements [kg] for each period

    Returns
    -------
    obj_val      : the objective value [EUR] after optimization
    setups       : a list with the setup decision per period
    """

    nr_periods = len(requirements)

    # Model Decleration

    model = LpProblem("Period dependent production costs", LpMinimize)

    # Decision Variables 

    x1 = {i: LpVariable(name=f"x1_{i}", cat="Binary") for i in range(nr_periods)}  # Order setup
    x2 = {i: LpVariable(name=f"x2_{i}", lowBound=0) for i in range(nr_periods)}  # Inventory level
    y = {i: LpVariable(name=f"y_{i}", lowBound=0) for i in range(nr_periods)} # Production Quantity 

    # Objective function

    model += lpSum(cost_h * x2[i] + cost_k * x1[i] for i in range(nr_periods))

    # Model Constraints 
    
    for i in range(nr_periods):
        if i == 0:
            model += x2[i] == init_inv + y[i] - requirements[i]
        else:
            model += x2[i] == x2[i - 1] + y[i] - requirements[i]


    for i in range(nr_periods):
        model += y[i] <= BIG_M * x1[i]  
        model += x2[i] >= 0 

    for i in range(nr_periods):
        model += y[i] >= 0

    for i in range(nr_periods):
        if i % 2 == 1 or i == nr_periods - 1:
            model += x1[i] == 0
        elif i % 2 == 0:
            model += x1[i] == 1

    # Default return values = No solution found

    obj_val = 0
    setups = [0]*nr_periods
    if model is None:
        # Worst case: produce every other period
        obj_val = 0
        inventory = init_inv
        for per in range(nr_periods):
            if per % 2 == 0:
                if per + 1 == nr_periods:
                    req2 = requirements[per]
                else:
                    # Check for two periods
                    req2 = requirements[per] + requirements[per + 1]
                net_req = max(0, req2 - inventory)
                if net_req > 0:
                    setups[per] = 1
                    obj_val += cost_k
                    inventory += net_req
            inventory -= requirements[per]
            obj_val += cost_h*inventory
        return obj_val, setups
    
    # Solve the constructed model with GLPK within 10 seconds
    model.solve(GLPK(msg=False, options=['--tmlim', '10']))

    if model.status != 1:
        # Model did not result in an optimal solution
        return model.status, setups
    
    # Retrieve the objective value
    obj_val = model.objective.value()

    # Retrieve the setup decisions
    for i in range(nr_periods):
         setups[i] = int(x1[i].value()) 
 
    return obj_val, setups

def lsp3(cost_h, cost_k, init_inv, requirements): ### NOT COMPLETE 
    """Solving the uncapacitated multi-product lot sizing problem (UMLSP).

    This function generates the UMLSP formulation in PuLP
    and solves it using the GLPK solver.

    Parameters
    ----------
    cost_h       : holding costs h [EUR/kg/period]
    cost_k       : fixed setup costs K [EUR/setup]
    init_inv     : a list with the initial inventories [kg]
    requirements : a nested list with the requirements [kg] for each product
                   in each each period

    Returns
    -------
    obj_val      : the objective value [EUR] after optimization
    setups       : a list with the setup decision per period
    """

    # Define parameters
    nr_periods = len(requirements)

    # Model Decleration

    model = LpProblem("Period dependent production costs", LpMinimize)

    # Decision Variables 

    x1_p1 = {i: LpVariable(name=f"x1P1_{i}", cat="Binary") for i in range(nr_periods)}  # Order setup product 1
    x1_p2 = {i: LpVariable(name=f"x1P2_{i}", cat="Binary") for i in range(nr_periods)}   # Order setup product 2

    x2_p1 = {i: LpVariable(name=f"x2P1_{i}", lowBound=0) for i in range(nr_periods)}  # Inventory level product 1
    x2_p2 = {i: LpVariable(name=f"x2P2_{i}", lowBound=0) for i in range(nr_periods)}  # Inventory level product 2 

    y_1 = {i: LpVariable(name=f"y1_{i}", lowBound=0) for i in range(nr_periods)} # Production Quantity product 1 
    y_2 = {i: LpVariable(name=f"y2_{i}", lowBound=0) for i in range(nr_periods)} # Production Quantity product 2

    # Objective function

    model += lpSum(cost_h * (x2_p1[i] + x2_p2[i]) + cost_k * (x1_p1[i] + x1_p2[i]) for i in range(nr_periods))

    # Model Constraints 
    
    for i in range(nr_periods):
        if i == 0:
            model += x2_p1[i] == init_inv[0] + y_1[i] - requirements[i][0]
            model += x2_p2[i] == init_inv[1] + y_2[i] - requirements[i][1]
        else:
            model += x2_p1[i] == x2_p1[i - 1] + y_1[i] - requirements[i][0]
            model += x2_p2[i] == x2_p2[i - 1] + y_2[i] - requirements[i][1]

    for i in range(nr_periods):

        model += y_1[i] <= BIG_M * x1_p1[i]  
        model += x2_p1[i] >= 0 

        model += y_2[i] <= BIG_M * x1_p2[i]  
        model += x2_p2[i] >= 0 

    for i in range(nr_periods):
        model += y_1[i] >= 0
        model += y_2[i] >= 0
    
    for i in range(nr_periods):
        model += x1_p1[i] + x1_p2[i] <= 1

    obj_val = 0
    setups = [0]*nr_periods

    if model is None:
        # Worst case: produce each product every other period
        # if the net requirement is positive (=L4L)
        obj_val = 0
        inventory = []
        inventory.append(init_inv[0])
        inventory.append(init_inv[1])
        prod = 0
        for per in range(nr_periods):
            if per + 1 == nr_periods:
                req2 = requirements[per][prod]
            else:
                req2 = requirements[per][prod] + requirements[per+1][prod]
            net_req = max(0, req2 - inventory[prod])
            if net_req > 0:
                setups[per] = prod + 1
                inventory[prod] += net_req
                obj_val += cost_k
            # Inventory
            inventory[0] -= requirements[per][0]
            inventory[1] -= requirements[per][1]
            obj_val += cost_h*(inventory[0] + inventory[1])
            # Switch product
            if prod == 0:
                prod = 1
            else:
                prod = 0
        return obj_val, setups
    
    # Solve the constructed model with GLPK within 10 seconds
    model.solve(GLPK(msg=False, options=['--tmlim', '10']))
    # print(model)

    if model.status != 1:
        # Model did not result in an optimal solution
        return model.status, setups
    
    # Retrieve the objective value
    obj_val = model.objective.value()

    # Retrieve the periods in which you decide to produce

    for i in range(nr_periods):
        if (int(x1_p1[i].value()) == 1): 
            setups[i] = 1
        elif (int(x1_p2[i].value() == 1)):
            setups[i] = 2 

    return obj_val, setups

# Tests

if __name__ == '__main__':
    ex1_data = [20, 25, 14, 20, 15, 5.5, 2.5]
    pt_data = [1.0, 2.0, 2.0, 1.5, 1.0, 0.5, 1.0]
    min_cost, setup_periods = lsp1(2, 50, pt_data, 25, ex1_data)
    print(f"ULSP_TVP solution: costs={min_cost},"
          +f" with setups {setup_periods}")

    ex1_data = [20, 25, 14, 20, 15, 5.5, 2.5]
    min_cost, setup_periods = lsp2(2, 50, 25, ex1_data)
    print(f"ULSP_NCS solution: costs={min_cost},"
          +f" with setups {setup_periods}")

    ex2_data = [[20, 5], [25, 10], [14, 21], [20, 20],
                [15, 7.5], [5.5, 11], [2.5, 13]]
    min_cost, setup_periods = lsp3(2, 50, [25, 25], ex2_data)
    print(f"UMLSP    solution: costs={min_cost},"
          +f" with setups {setup_periods}")
