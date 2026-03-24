# Linear Regression

- regression.py : uses libraries to perform the Regression
- regression\_scratch.py : algorithm for regression for transparency
- sample.csv : a very simple example to show regression with different loss types
- placement.csv : Kaggle data (https://www.kaggle.com/) about salaray for engineers and scientists.


For command line execution of regression.py, which will perform regression then graph 
the results using a random subset of input (for visualization).


```
python3 regression.py sample.csv --x x --y y --loss all
```

OR 

```
python3 regression.py placement.csv --x tech_skills soft_skills work_exp --y salary --loss L2          
```

The list following --x correspond to the columns to use in the .csv 
file for the input vector.

The list following --y is the column that is the target.

Loss options are:
- L0 : p==a ? 1 : 0
- L1 : abs(p-a)
- L2 : (p-a)^2
- Linf : max(p-a) over all examples

where p is the predicted value of the model and a is the actual (target) value.