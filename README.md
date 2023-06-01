# Handling a Large Number of Attributes in Conjoint Analysis with Symbridge Calculation

Python library (not yet deployed) to make a conjoint analysis and extended calculation if we have a lot of attributes using symbridge analysis. A little bit snippet on how to do it:

    ```target_var = 'chosen'
    x_var = ['price', 'brand', 'keyless', 'electric', 'warranty']
    bridge_var = ['brand', 'electric']
    
    sym_analysis = conjoint.symbridge_extended_analysis(df_conjoint=df_choice, 
                                                        df_rating=df_rating, 
                                                        target_var=target_var, 
                                                        predictor_var=x_var, 
                                                        bridge_var=bridge_var,
                                                        anchor_var=anchor_var,
                                                        resp_var='respID',
                                                        compare_all='specific')```

## Background

Conjoint analysis is one of market research methods to know the part worth of an attribute of a product from the perspective of customers. The way it works is by asking a respondent to choose from several choices provided by the researcher, and these choices have different attributes, set beforehand either by randomized design or bayesian probability occurence. Based on several sources, maximum attributes we can put on the choices is up to seven. But, what if we want to investigate a lot of attributes, let's say 20 attributes?

## Objectives

This library was inspired by <a href='http://www.macroinc.com/english/papers/A%20Method%20for%20Handling%20a%20Large%20Number%20of%20Attributes%20in%20Full%20Profile%20Trade-Off%20Studies.pdf'>McCullough (2000) paper</a> on how to tackle this problem. Off the computer (during the data collection process), we can extend this conjoint analysis into 2 stages:

1. Choice based study
2. Self-rating attributes

More precisely, he explained in the paper the steps on how to do the data collection:

1. Using any of a variety of available conjoint or choice6 software, utility weights for each feature in the trade-off exercise (data step 2) can be estimated for each respondent.
2. Utilities are then bridged from data step 1 with data step 2. On a per respondent basis, a scalar can be estimated using the common features in data step 1 and data step 2. Numerous algorithms for bridging exist. We typically use the Symbridge7 method.
3. The scalar reduces the feature scores in data step 1 to a scale equivalent with data step 2 utility weights.
4. On a per respondent basis, this scalar is multiplied by each score in data step 1 to achieve utility weights comparable to data step 2 utility weights.
5. Data step 1 and data step 2 utility weights are then merged to create one set of bridged utility weights (with the utility values from data step 2 used for the attributes common to both steps).
6. These merged utility weights define the conjoint or choice model from which all subsequent simulations will be based.

The important part here where we can connect these two different stages is by **bridging** calculation:

## Bridging

There's a lot of bridging method we can pick to integrate these two stages into one. But one of the most popular bridging method is Symbridge Analysis, introduced by Francois and MacLachlan (1997). 

Create a scalar value to make a bridging. There are two alternatives we can go:

- $B = (R_{11} / R_{21}) + (R_{12} / R_{22})$
- $B = (R_{11} + R_{12}) / (R_{21} + R_{22})$

Where $R_{ij}$ is the range of partworths of bridging attribute j in subdesign i. Or in a simpler way, it's the **estimate for each features in conjoint design**, and **self-explicated score given by respondents in rating design**. As recommended, it's preferable to **go with the second one**, as it's more stable and consistent. 
