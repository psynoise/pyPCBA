# pyPCBA - Version 0.1.2

## 1 Purpose

Python library for analog circuit analysis and design.

The primary use case is interactive calculations from Jupyter Notebook. The library shall support both numerical and symbolic calculations.

## 2 Introduction

Specification of function below shall have:

* Purpose

* Input parameters

* Units

* Return value

and should if possible have:

* Expression/Formula

* Error handling

* Example

## 3 Scope for this version

The following modules shall be implemented or updated if needed:

* eq2sympy

* lists.py

* values.py

The remaining modules are explicitly out of scope for this version.

## 4 General requirements

The library shall:

* Use SI base units internally.

* Accept values expressed with SI prefixes.

* Raise ValueError for invalid input values.

* Support scalar values, NumPy arrays, and SymPy expressions where applicable.

* Include type hints for all public functions.

* Include Google-style docstrings for all public functions.

* Include unit tests for all public functions.

### 4.1 Design philosophy and coding style

The library is intended for engineers performing exploratory calculations in Jupyter Notebook.

* Prefer simple implementations over complex abstractions.

* Avoid unnecessary classes.

* Use functions unless state must be maintained

* Optimize for readability and notebook usability.

Priority order:

1. Ease of use

2. Readability

3. Correctness

4. Performance

Functions shall favor clear syntax over maximum execution speed.

### 4.2 API conventions

Functions shall be callable directly after import.

Example:

    from values import optimize
    VoltageDivider = optimize(R1 | R2 = 0.5, e12.txt)
    VoltageDivider

### 4.3 SI prefix and units

All functions accepting numeric values shall also accept strings containing SI prefixes.

| Name  | Symbol | Multiple |
| ----- | ------ | -------- |
| pico  | p      | 10**-12  |
| nano  | n      | 10**-9   |
| micro | u      | 10**-6   |
| milli | m      | 10**-3   |
| kilo  | k      | 10**3    |
| mega  | M      | 10**6    |

It is important to distinguish between m for milli and M for mega.

Also following variants of symbols shall be supported:

| Name  | Symbol | Multiple |
| ----- | ------ | -------- |
| micro | µ      | 10**-6   |
| mega  | Meg    | 10**6    |

Examples of valid inputs:

    1000 "1k" "10k" "4.7u" "100n" "2.2M"

```
"1000 Ohm "1 kOhm" "10 kOhm," "4.7 uF" "4.7 uH" "100 nF" "2.2 MOhm" 
```

```
1kOhm" "10kOhm," "4.7uF" "4.7uH" "100nF" "2.2 MOhm"
```

## 5 Modules to implement

This section lists modules to be implemented now.

### 5.1 common.py

#### Function eq2sympy

ep2sympy(equations: str)

Purpose:

* Translates equations with special operators to SymPy expressions.

Input parameters:

* equations: Strings or SymPy expressions.

Algorithm: 

* Trough substitution, translate special operators defined in table below to  SymPy expressions.

Special operators:

| Operator | Definition            | Note                                 |
| -------- | --------------------- | ------------------------------------ |
| |        | x \| y = (y)/(x+y)    | Voltage or current divider operator. |
| |\|      | x \|| y = (x*y)/(x+y) | Parallel operator.                   |
| //       | x // y = (x*y)/(x+y)  | Alternative parallel operator.       |

Return value: SymPy expressions.

### 5.2 lists.py

#### Function e_series

e_series(
    series: str, 
    min_value: float,
    max_value: float,
    filename: str | None = None)

Purpose:

- Create a series of preferred values to be used by other functions.

Input parameters:

* series: one of following values: E3, E6, E12, E24, E48, E48_2, E48_4, E96, E192.
  
  * E3: Use values from the E3 preferred number series. (As listed per decade in section A1 below.)
  
  * E6: Use values from the E6 preferred number series. (As listed per decade in section A2 below.)
  
  * E12: Use values from the E12 preferred number series. (As listed per decade in section A3 below.)
  
  * E24: Use values from the E24 preferred number series. (As listed per decade in section A4 below.)
  
  * E48: Use values from the E48 preferred number series. (As listed per decade in section A5 below.)
  
  * E48_2: Use every second values from the E48 preferred number series. (As listed per decade in section A6 below.)
  
  * E48_4: Use every fourth values from the E48 preferred number series. (As listed per decade in section A7 below.)
  
  * E96: Use values from the E96 preferred number series. (As listed per decade in section A8 below.)
  
  * E192: Use values from the E192 preferred number series. (As listed per decade in section A9 below.)

* min_value: minimum value to be included in the output.

* max_value: maximum value to included in the output.

* filename: optional. If specified return value goes to an output file with filename filename. File extension shall be *.txt .

Units:

* Unitless.

Return value:  NumPy ndarray

* With numbers over several decades as specified by input parameters.

Example A:

    e_series(E12, 100, 100e3)

or

```
e_series(E12, 100, 100k)
```

Gives an array with preferred numbers according to E12-series from 100 to 100e3.

### 5.3 values.py

#### Function optimize

optimize(equations, series, num_solutions=10)

Purpose:

* List solutions with least error given one or several equations and an array of preferred numbers as input.

Input parameters:

* equations: A list of symbolic equations.
  
  * Input shall be translated to SymPy expressions with the function eq2sympy() specified above.
  
  * All SymPy symbols appearing in the equations shall be treated as optimization variables.
  
  * Example: [Eq(R2/(R1+R2), 0.5), Eq(R1*R2/(R1+R2), 50)]

* series: array of of allowed values for each optimization variable.
  
  * Example: e_series("E24", 1e3, 100e3)

* numsolutions: optional, specify number of solutions to be listed. 
  
  * If not specified, default is 10 different solutions.

Error metric (relative least squares):

* For each equation: residual_i = (calculated_i - target_i)/target_i

* Least-squares error: E = Σ(residual_i²), over all equations.

* Solutions shall be sorted in ascending order of E.

* The solution with the smallest E is considered the best solution.

Solutions and error metric:

* The implementation may use exhaustive search.

* The function shall return the best available solutions even if no exact solution exists.

* Variables are allowed to assume equal values.

* Use relative least squares according to below:
  
  * For each equation: residual_i = (calculated_i - target_i)/target_i
  - The solution with the smallest E is considered the best solution.
  
  - Least-squares error: E = Σ(residual_i²), over all equations.
- Solutions shall be sorted in ascending order of E.

Units:

* Output shall have same units as input.

Return value:

* A pandas DataFrame.

* One solution per row.

* Columns:
  
  * Rank
  
  * variable_1
  
  * variable_2
  
  * ...
  
  * error

Example A:

    optimize(R1 | R2 = 0.5, e12.txt)

Shall give a list in a table with 10 different solution to the equation  (R2)/(R1+R2) = 0.5, with variable values only within the space of the array specified in e12.txt.

Example B:

```
optimize(R1 | R2 = 0.5, R1 || R2 = 50, e24.txt)
```

Shall give a list in a table with 10 different solution to the equations (R2)/(R1+R2) = 0.5 and (x*y)/(x+y) = 50, with variable values only within the space of the array specified in e24.txt.

Example C:

```
optimize(R1 | R2 = 0.5, e_series(E48, 100, 100e3), 5)
```

Shall give a list in a table with 5 different solution to the equation (R2)/(R1+R2) = 0.5, with variable values only within the space of the array specified by the function e_series.

## 6 Future ideas

This section lists modules to be implement in the future.

### 6.1 worstcase.py

Functions:

- TBD

### 6.2 spicegenerator.py

Functions:

- TBD

### 6.3 docgenerator.py

Functions:

- TBD

### 6.4 bomanalys.py

Functions:

- TBD

### 6.4 compare.py

Functions:

- schematicdiff()

## Appendix A - Preferred numbers

This section lists quantity per decade of preferred numbers.

### A1 - E3 values

1.0, 2.2, 4.7

### A2 - E6 values

1.0, 1.5, 2.2, 3.3, 4.7, 6.8

### A3 - E12 values

1.0, 1.2, 1.5, 1.8, 2.2, 2.7, 3.3, 3.9, 4.7, 5.6, 6.8, 8.2

### A4 - E24 values

1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0, 3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1

### A5 - E48 values

1.00, 1.05, 1.10, 1.15, 1.21, 1.27, 1.33, 1.40, 1.47, 1.54, 1.62, 1.69, 1.78, 1.87, 1.96, 2.05, 2.15, 2.26, 2.37, 2.49, 2.61, 2.74, 2.87, 3.01, 3.16, 3.32, 3.48, 3.65, 3.83, 4.02, 4.22, 4.42, 4.64, 4.87, 5.11, 5.36, 5.62, 5.90, 6.19, 6.49, 6.81, 7.15, 7.50, 7.87, 8.25, 8.66, 9.09, 9.53

### A6 - E48 every other value

1.00, 1.10, 1.21, 1.33, 1.47, 1.62, 1.78, 1.96, 2.15, 2.37, 2.61, 2.87, 3.16, 3.48, 3.83, 4.22, 4.64, 5.11, 5.62, 6.19, 6.81, 7.50, 8.25, 9.09

### A7 - E48 every fourth value

1.00,  1.21,  1.47,  1.78,  2.15,  2.61,  3.16,  3.83,  4.64,  5.62,  6.81,  8.25

### A8 - E96 values

1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18, 1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43, 1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74, 1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10, 2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55, 2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09, 3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74, 3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53, 4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49, 5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65, 6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06, 8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76

### A9 - E192 values

1.00, 1.01, 1.02, 1.04, 1.05, 1.06, 1.07, 1.09, 1.10, 1.11, 1.13, 1.14, 1.15, 1.17, 1.18, 1.20, 1.21, 1.23, 1.24, 1.26, 1.27, 1.29, 1.30, 1.32, 1.33, 1.35, 1.37, 1.38, 1.40, 1.42, 1.43, 1.45, 1.47, 1.49, 1.50, 1.52, 1.54, 1.56, 1.58, 1.60, 1.62, 1.64, 1.65, 1.67, 1.69, 1.72, 1.74, 1.76, 1.78, 1.80, 1.82, 1.84, 1.87, 1.89, 1.91, 1.93, 1.96, 1.98, 2.00, 2.03, 2.05, 2.08, 2.10, 2.13, 2.15, 2.18, 2.21, 2.23, 2.26, 2.29, 2.32, 2.34, 2.37, 2.40, 2.43, 2.46, 2.49, 2.52, 2.55, 2.58, 2.61, 2.64, 2.67, 2.71, 2.74, 2.77, 2.80, 2.84, 2.87, 2.91, 2.94, 2.98, 3.01, 3.05, 3.09, 3.12, 3.16, 3.20, 3.24, 3.28, 3.32, 3.36, 3.40, 3.44, 3.48, 3.52, 3.57, 3.61, 3.65, 3.70, 3.74, 3.79, 3.83, 3.88, 3.92, 3.97, 4.02, 4.07, 4.12, 4.17, 4.22, 4.27, 4.32, 4.37, 4.42, 4.48, 4.53, 4.59, 4.64, 4.70, 4.75, 4.81, 4.87, 4.93, 4.99, 5.05, 5.11, 5.17, 5.23, 5.30, 5.36, 5.42, 5.49, 5.56, 5.62, 5.69, 5.76, 5.83, 5.90, 5.97, 6.04, 6.12, 6.19, 6.26, 6.34, 6.42, 6.49, 6.57, 6.65, 6.73, 6.81, 6.90, 6.98, 7.06, 7.15, 7.23, 7.32, 7.41, 7.50, 7.59, 7.68, 7.77, 7.87, 7.96, 8.06, 8.16, 8.25, 8.35, 8.45, 8.56, 8.66, 8.76, 8.87, 8.98, 9.09, 9.20, 9.31, 9.42, 9.53, 9.65, 9.76, 9.88

## Appendix B - Example notebooks

### B1 - Usage

from pyPCBA.lists import e_series

resistors = e_series("E24", 1 kOhm, 100 kOhm)

from pyPCBA.values import optimize

optimize( [Eq(R2/(R1+R2), 0.5)], resistors)
