# Handling a Large Number of Attributes in Conjoint Analysis with Symbridge Calculation

This Python module is designed by the author to perform conjoint analysis and extended calculations when dealing with numerous attributes using Symbridge Analysis. Below is a brief example of how to use it:

```python
from conjoint import conjoint

target_var = 'chosen'
x_var = ['price', 'brand', 'keyless', 'electric', 'warranty']
bridge_var = ['brand', 'electric']

sym_analysis = conjoint.symbridge_extended_analysis(df_conjoint=df_choice, 
                                                    df_rating=df_rating, 
                                                    target_var=target_var, 
                                                    predictor_var=x_var, 
                                                    bridge_var=bridge_var,
                                                    anchor_var=anchor_var,
                                                    resp_var='respID',
                                                    compare_all='specific')
```

Additionally, this module is equipped with a "table_generator" program, which is used to create a formatted table from choice data for choice-based conjoint analysis. You can generate the choice data by using cbcTools package in R. For more information about the cbcTools package, please visit the following <a href="https://jhelvy.github.io/cbcTools/">link.</a>

Below is a brief example of how to use table_generator:

```python
from conjoint import table_generator

table_generator.table_generator(input_path='car_options_example.csv',
                                label='Cars',
                                col_id='qID',
                                path_to_save='tables')
```

## Background

Conjoint analysis is a market research method used to determine the value of product attributes from the customer's perspective. It involves presenting respondents with multiple choice scenarios, each representing a product with different attribute combinations. Traditionally, conjoint analysis is limited to a smaller number of attributes, typically up to seven. However, when investigating a larger number of attributes, such as 20, traditional conjoint analysis methods may become impractical as it will cause choice fatigue.

## Objectives

This library draws inspiration from <a href='http://www.macroinc.com/english/papers/A%20Method%20for%20Handling%20a%20Large%20Number%20of%20Attributes%20in%20Full%20Profile%20Trade-Off%20Studies.pdf'>McCullough (2000) paper</a> on handling a large number of attributes in full-profile trade-off studies. The approach extends traditional conjoint analysis into two stages:

1. Choice based study
2. Self-rating attributes

More precisely, he explained in the paper the steps on how to do the data collection:

1. Use conjoint or choice software to estimate utility weights for each feature in the trade-off exercise for each respondent.
2. Bridge utilities from the choice-based study with self-rating attributes. A scalar is estimated per respondent using common features between the two data sets. The Symbridge method is often used for this purpose.
3. The scalar is used to adjust the feature scores from the choice-based study to a scale equivalent to the self-rating attributes.
4. The scalar is multiplied by each score in the choice-based study to achieve utility weights comparable to the self-rating attributes.
5. The utility weights from both data sets are merged to create a single set of bridged utility weights.
6. These merged utility weights define the conjoint or choice model for subsequent simulations.

The **bridging calculation** is a crucial step in connecting these two stages.

## Bridging

One of the most popular bridging methods is Symbridge Analysis, introduced by <a href='http://staff.washington.edu/macl/BRIDG97.pdf'>Francois and MacLachlan (1997) paper.</a> This method aims to create a scalar value for bridging between the choice-based study and the self-rating attributes.

There are two alternatives for creating this scalar value:

- $B = (R_{11} / R_{21}) + (R_{12} / R_{22})$
- $B = (R_{11} + R_{12}) / (R_{21} + R_{22})$

Where $R_{ij}$ is the range of partworths of bridging attribute j in subdesign i. Or in a simpler way, it's the **estimate for each features in conjoint design**, and **self-explicated score given by respondents in rating design**. As recommended, it's preferable to **go with the second one**, as it's more stable and consistent. Thus, this notebook shows the calculation result from second method.

## About this Library

This library is utilized to compute the part worth from conjoint analysis and the extended self-rating score. For detailed examples, please refer to the docs folder and check out some examples provided in the Jupyter notebook file.
