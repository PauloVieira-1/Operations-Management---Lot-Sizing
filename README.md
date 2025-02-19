# Operations Management - Lot Sizing Problem

This assignment focuses on the **lot sizing problem** and requires the implementation of **Mixed-Integer Linear Programming (MILP)** models using the **PuLP** package in Python. The assignment consists of three problem variants:

- **LSP1:** Period-dependent production costs
- **LSP2:** Non-consecutive periods with production
- **LSP3:** Two products on a single machine

## Problem Descriptions

### **Lot Sizing Problem (LSP) - General Formulation**

The objective is to minimize total costs:

$$ \min C = \sum_{t=1}^{T} (K \cdot z_t + h \cdot I_t) $$

Subject to the following constraints:

1. Inventory balance:
   $$ I_t - I_{t-1} + y_t = R_t, \quad \forall t \in \{1, \dots, T\} $$
   (Initial inventory is given as \( I_0 \)).

2. Production setup constraint:
   $$ y_t \leq M \cdot z_t, \quad \forall t \in \{1, \dots, T\} $$

3. Variable restrictions:
   $$ z_t \in \{0,1\}, \quad y_t, I_t \geq 0, \quad \forall t \in \{1, \dots, T\} $$

Where:
- \( K \) is the setup cost per production period.
- \( h \) is the holding cost per kg per period.
- \( I_t \) is the inventory at the end of period \( t \).
- \( y_t \) is the production quantity in period \( t \).
- \( z_t \) is a binary variable (1 if production occurs, 0 otherwise).
- \( R_t \) is the demand in period \( t \).

### **LSP1: Period-dependent production costs**

This variant introduces period-dependent production costs \( P_t \), modifying the objective function:

$$ \min C = \sum_{t=1}^{T} (K \cdot z_t + h \cdot I_t + P_t \cdot y_t) $$

#### **Function: `lsp1(cost_h, cost_k, cost_p, init_inv, requirements)`**
- **Inputs:**
  - `cost_h`: Holding cost per kg per period.
  - `cost_k`: Fixed setup cost per production period.
  - `cost_p`: List of production costs per period.
  - `init_inv`: Initial inventory (kg).
  - `requirements`: List of demand values per period.
- **Outputs:**
  - `obj_val`: Optimal total cost.
  - `setups`: List of binary values indicating production periods.

### **LSP2: Non-consecutive periods with production**

This variant **disallows production in consecutive periods**, adding the constraint:

$$ z_t + z_{t+1} \leq 1, \quad \forall t \in \{1, \dots, T-1\} $$

The objective function remains:

$$ \min C = \sum_{t=1}^{T} (K \cdot z_t + h \cdot I_t) $$

#### **Function: `lsp2(cost_h, cost_k, init_inv, requirements)`**
- **Inputs:**
  - `cost_h`: Holding cost per kg per period.
  - `cost_k`: Fixed setup cost per production period.
  - `init_inv`: Initial inventory (kg).
  - `requirements`: List of demand values per period.
- **Outputs:**
  - `obj_val`: Optimal total cost.
  - `setups`: List of binary values indicating production periods.

### **LSP3: Two products on a single machine**

This variant involves two products produced on the same machine, which **can only produce one product per period**. The inventory balance constraints become:

$$ I_{t,1} - I_{t-1,1} + y_{t,1} = R_{t,1}, \quad \forall t \in \{1, \dots, T\} $$
$$ I_{t,2} - I_{t-1,2} + y_{t,2} = R_{t,2}, \quad \forall t \in \{1, \dots, T\} $$

With an additional constraint ensuring only one product is produced per period:

$$ z_{t,1} + z_{t,2} \leq 1, \quad \forall t \in \{1, \dots, T\} $$

#### **Function: `lsp3(cost_h, cost_k, init_inv, requirements)`**
- **Inputs:**
  - `cost_h`: Holding cost per kg per period.
  - `cost_k`: Fixed setup cost per production period.
  - `init_inv`: List of initial inventories for both products.
  - `requirements`: Nested list with demand values per period per product.
- **Outputs:**
  - `obj_val`: Optimal total cost.
  - `setups`: List of values indicating production choices per period (0: no production, 1: product 1, 2: product 2).

## Implementation Details

This assignment was implemented using **PuLP** and solved using the **GLPK solver**. Each function constructs a MILP model, sets up constraints, and solves the problem using `model.solve(GLPK(msg=False, options=['--tmlim', '10']))` with a 10-second time limit.

## Running the Code

To test the implementation, run:

```bash
python fom2425hw1.py
```

Expected output format:

```
ULSP_TVP solution: costs=XXX, with setups [1, 0, 1, 0, ...]
ULSP_NCS solution: costs=XXX, with setups [0, 1, 0, 1, ...]
UMLSP solution: costs=XXX, with setups [1, 2, 0, 1, ...]
```

## Acknowledgments

This implementation was created as part of the **1CV00 FOM 2024-2025** course under the guidance of **Rob Broekmeulen**.

---
