import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm

class conjoint_simple_analysis():
    '''
    A class to make Choice-based Conjoint analysis using logistic regression from statsmodels.

    Attributes
    ----------
    df_regress : pandas.DataFrame()
        Dataframe that contains people choices and attributes. See the proper format
        in the documentation.
    target_var : string
        Columns from dataframe that contains the chosen value (should be in 0 or 1).
    predictor_var : list
        Columns from dataframe that contains the attributes.
    compare_all : boolean
        Whether to drop one of the variables from making dummy variable process.
    

    Methods
    -------
    regression() :
        Conducting the regression and showing summary in statsmodels summary output format.
    plot(**params) :
        Make a part worth plot from regression analysis.
    prob_mix(cols) :
        Showing part worth of the variables we're interested into.


    Properties
    -------
    show_x :
        Showing x that has been converted into dummy variable.
    show_y :
        Showing y that has been converted into proper format for regression.
    '''
    
    def __init__(self, df_regress, target_var, predictor_var, anchor_var=[], compare_all=False):
        self.df_regress = df_regress
        self.target_var = target_var
        self.predictor_var = predictor_var
        self.anchor_var = anchor_var
        
        self.anal_df = df_regress.loc[:, df_regress.columns.isin(predictor_var)]
        
        self.y = df_regress[target_var]
        self.x = df_regress[[x for x in df_regress.columns if any(item in x for item in predictor_var) and x != target_var]]
        
        if compare_all == True:
            self.xdum = pd.get_dummies(self.x, columns=[c for c in self.x.columns if c != target_var], drop_first=False)
        elif compare_all == False:
            self.xdum = pd.get_dummies(self.x, columns=[c for c in self.x.columns if c != target_var], drop_first=True)
        elif compare_all == 'specific':
            self.xdum = pd.get_dummies(self.x, columns=[c for c in self.x.columns if c != target_var], drop_first=False)
            self.xdum = self.xdum[anchor_var]
        else:
            raise ValueError(f"Invalid value for compare_all: '{compare_all}'. Valid options are True, False, and 'specific'.")
    
    
    def regression(self):
        '''
        Conducting the regression and showing summary in statsmodels summary output format.

        Return
        -------
        Statsmodels summary output format.
        '''
        y = self.y
        xdum = self.xdum
        
        res = sm.OLS(y, xdum, family=sm.families.Binomial()).fit()
        self.res = res
        return res.summary()
    
    
    def plot(self, **params):
        '''
        Make a part worth plot from regression analysis.

        Attributes:
        -------
        **params :
            Attributes inherited from plt.subplots to make adjustment on the plot.
            Below shown some important parameters to adjust.
                - figsize() : tuple
                    Figure size of the plot
        
        Return
        -------
        Showing plot from matplotlib.pyplot.
        '''
        
        try:
            res
        except NameError:
            res = sm.OLS(self.y, self.xdum, family=sm.families.Binomial()).fit()
        else:
            res = self.res
        
        df_res = pd.DataFrame({
            'param_name': res.params.keys(),
            'param_w': res.params.values, 
            'pval': res.pvalues
        })

        # preparing dataframe to be passed to the plot function
        
        df_res['abs_param_w'] = np.abs(df_res['param_w'])
        df_res['is_sig_95'] = (df_res['pval'] < 0.05)
        df_res['c'] = ['tab:blue' if x else 'tab:red' for x in df_res['is_sig_95']]
        df_res = df_res.sort_values(by='abs_param_w', ascending=True)
        
        f, ax = plt.subplots(**params)
        plt.title('Part Worth')
        pwu = df_res['param_w']
        xbar = np.arange(len(pwu))
        plt.barh(xbar, pwu, color=df_res['c'])
        plt.yticks(xbar, labels=df_res['param_name'])
        
        sns.despine()
        plt.show()
        
    
    def prob_mix(self, cols):
        '''
        Showing total worth of a new alternative with the attributes
        we're interested to look into, we can set it up.

        Attributes:
        -------
        cols : list
            List of columns/attributes we want an alternative to have.
        
        Return
        -------
        Showing total worth of the new alternative.
        '''

        # convert statsmodels summary to dataframe
        results_as_html = self.res.summary().tables[1].as_html()
        mix_df = pd.read_html(results_as_html, header=0, index_col=0)[0]

        # print combinations
        mix_val = round(mix_df.loc[cols, 'coef'].sum(), 3)
        
        return mix_val
        
        
    @property
    def show_x(self):
        return self.xdum
    
    @property
    def show_y(self):
        return self.y
    

class symbridge_extended_analysis():
    '''
    A class to make an extended Choice-based Conjoint analysis with bridging using
    symbridge methodology (Francois and Maclachlan, 1999). This analysis and methodology
    is used for a conjoint analysis where we have a lot of attributes. 

    Attributes
    ----------
    df_conjoint : pandas.DataFrame()
        Dataframe that contains people choices and attributes from conjoint analysis.
    df_rating : pandas.DataFrame()
        Dataframe that contains self-ranking score for the extended attributes.
    target_var : str
        Columns from dataframe that contains the chosen value (should be in 0 or 1).
    predictor_var : list
        Columns from dataframe that contains the attributes.
    bridge_var : list
        Bridging variable from df_conjoint and df_rating. The name of the columns should be the same.
    resp_var :
        Respondent ID. Important to retain the information about the individual respondent.
    compare_all : bool
        Whether to drop one of the variables from making dummy variable process.


    Methods
    -------
    ind_utils_dataframe() :
        Create individual utility dataframe.
    ind_analysis(show_debug) :
        Make a part worth for individual utility using symbridge analysis.
    plot_overall(cols) :
        Plot every variable
    '''

    def __init__(self, df_conjoint, df_rating, target_var, predictor_var, bridge_var, resp_var, anchor_var=[], compare_all=False):
        self.df_conjoint = df_conjoint
        self.df_rating = df_rating
        self.target_var = target_var
        self.predictor_var = predictor_var
        self.bridge_var = bridge_var
        self.resp_var = resp_var
        self.anchor_var = anchor_var
        self.compare_all = compare_all


    # create individual utility using logistic regression
    # for-looping logistic regression by forcing it to calculate the utility for each individual

    def ind_utils_dataframe(self):
        '''
        Make a dataframe contains the part worth for individual utility.
        
        Return
        -------
        Dataframe contains the individual part worth.
        '''
        df_conjoint = self.df_conjoint
        df_rating = self.df_rating
        target_var = self.target_var
        resp_var = self.resp_var
        predictor_var = self.predictor_var
        anchor_var = self.anchor_var
        compare_all = self.compare_all

        ind_utils = pd.DataFrame()

        for resp in df_conjoint[resp_var].unique():
            bank_temp = df_conjoint[df_conjoint[resp_var] == resp]

            y = bank_temp[target_var]
            x = bank_temp[[x for x in df_conjoint.columns if any(item in x for item in predictor_var) and x != target_var]]
            
            if compare_all == True:
                xdum = pd.get_dummies(x, columns=[c for c in x.columns if c != target_var], drop_first=False)
            elif compare_all == False:
                xdum = pd.get_dummies(x, columns=[c for c in x.columns if c != target_var], drop_first=True)
            elif compare_all == 'specific':
                if len(anchor_var) == 0:
                    raise ValueError(f"No value passed for anchor_var. Pass the variables in a list.")
                else:
                    xdum = pd.get_dummies(x, columns=[c for c in x.columns if c != target_var], drop_first=False)
                    xdum = xdum[anchor_var]
            else:
                raise ValueError(f"Invalid value for compare_all: '{compare_all}'. Valid options are True, False, and 'specific'.")

            res = sm.OLS(y, xdum, family=sm.families.Binomial()).fit()

            results_as_html = res.summary().tables[1].as_html()
            mix_df = pd.read_html(results_as_html, header=0, index_col=0)[0]

            ind_utils = ind_utils.append(mix_df['coef'].to_frame().T.reset_index(drop=True))

        # rename columns with adding stage_1 in the front
        # because we're going to have second stage, which is stage_2

        temp_col = {}

        for col in ind_utils.columns:
            temp_col[col] = f'stage_1_{col}'
        
        ind_utils = ind_utils.rename(columns=temp_col)

        # preparing the final data frame for first stage

        ind_utils = ind_utils.reset_index(drop=True)
        ind_utils['respID'] = df_conjoint['respID'].unique()

        # for the second stage

        temp_col = {}

        for col in df_rating.columns:
            temp_col[col] = f'stage_2_{col}'
        
        df_rating = df_rating.rename(columns=temp_col)

        # final one, the merged dataframe of individual utility
        # containing the conjoint analysis and self-rating score
        
        ind_utils = ind_utils.merge(df_rating, left_index=True, right_index=True)

        # moving resp_var to the first columns

        cols = ind_utils.columns.tolist()
        cols = [resp_var] + cols[:cols.index(resp_var)] + cols[cols.index(resp_var)+1:]
        ind_utils = ind_utils[cols]

        self.ind_utils = ind_utils

        return ind_utils
    

    def ind_analysis(self, show_debug=False):
        '''
        Make a part worth for individual utility using symbridge analysis.

        Attributes:
        -------
        show_debug : bool
            Showing the debug, whether our columns were analyzed into their respective stage,
            which are stage 1 for conjoint, and stage 2 for self-ranked.
        
        Return
        -------
        Individual partworth dataframe.
        '''
        ind_utils = self.ind_utils_dataframe()
        bridge_var = self.bridge_var
        
        bridge_11 = [x for x in ind_utils.columns if f'stage_1_{bridge_var[0]}' in x][0]
        bridge_12 = [x for x in ind_utils.columns if f'stage_1_{bridge_var[1]}' in x][0]
        bridge_21 = [x for x in ind_utils.columns if f'stage_2_{bridge_var[0]}' in x][0]
        bridge_22 = [x for x in ind_utils.columns if f'stage_2_{bridge_var[1]}' in x][0]

        ind_utils['b_val'] = (ind_utils[bridge_11] + ind_utils[bridge_12]) / (ind_utils[bridge_21] + ind_utils[bridge_22])
        ind_utils['b_val_inverse'] = 1 / ind_utils['b_val']

        # for debug purpose and to check if we have done it correctly
        # will be called in the end using property

        debug = {}

        # calculating final partworth for other variables
        for col in ind_utils.columns:
            
            # if the column looped is a bridge
            if any(substring in col for substring in bridge_var):
                debug[col] = 'bridge'

                if 'stage_1' in col:
                    val = ind_utils['b_val_inverse'] * ind_utils[col]
                    col = col.replace('stage_1_', '')
                    ind_utils[f'stage_2_tf_{col}'] = val
                else:
                    val = ind_utils['b_val'] * ind_utils[col]
                    col = col.replace('stage_2_', '')
                    ind_utils[f'stage_1_tf_{col}'] = val  

            # if the column looped is from stage 1 -> conjoint analysis
            elif 'stage_1' in col:
                debug[col] = 'stage_1'

                val = ind_utils['b_val_inverse'] * ind_utils[col]
                col = col.replace('stage_1_', '')
                
                ind_utils[f'stage_2_tf_{col}'] = val
                ind_utils[f'fin_{col}'] = val + ind_utils[f'stage_1_{col}']  

            # if the column looped is from stage 2 -> self-rating
            elif 'stage_2' in col:
                debug[col] = 'stage_2'

                val = ind_utils['b_val'] * ind_utils[col]
                col = col.replace('stage_2_', '')
                
                ind_utils[f'stage_1_tf_{col}'] = val
                ind_utils[f'fin_{col}'] = val + ind_utils[f'stage_2_{col}']
            
            # if it's not the part of the bridge nor the analysis (like respID, b_val, etc.)
            else:
                debug[col] = 'skipped'

        # calculating the final partworth for the bridge
        for col in bridge_var:
            bridge_1 = [x for x in ind_utils.columns if f'stage_1_tf_{col}' in x][0]
            bridge_2 = [x for x in ind_utils.columns if f'stage_2_tf_{col}' in x][0]
            
            val = ind_utils[bridge_1] + ind_utils[bridge_2]
            ind_utils[f'fin_{col}'] = val

        if show_debug == False:
            return ind_utils
        else:
            return ind_utils, debug
    

    def plot_overall(self, method='mean', **kwargs):
        '''
        Make a part worth plot from symbdrige analysis.

        Attributes:
        -------
        method : str
            Method of the total worth calculation we want to choose.
                - mean : calculate mean from all individual part worth
                - median : calculate median from all individual part worth
        **kwargs :
            Attributes inherited from plt.subplots() to make adjustment on the plot.
            Below shown some important parameters to adjust.
                - figsize() : tuple
                    Figure size of the plot
        
        Return
        -------
        Showing plot from matplotlib.pyplot.
        '''
        ind_analysis = self.ind_analysis()
        ind_analysis = ind_analysis[[x for x in ind_analysis.columns if 'fin_' in x]]
        ind_analysis.describe().T[method].sort_values(ascending=True).plot(kind='barh', **kwargs)
        sns.despine()

    
    def prob_mix(self, cols, method='mean'):
        '''
        Showing total worth of a new alternative with the attributes
        we're interested to look into, we can set it up.

        Attributes:
        -------
        cols : list
            List of columns/attributes we want an alternative to have.
        method : str
            Method of the total worth calculation we want to choose.
                - mean : calculate mean from all individual part worth
                - median : calculate median from all individual part worth
        
        Return
        -------
        Showing total worth of the new alternative.
        '''

        ind_analysis = self.ind_analysis()
        ind_analysis = ind_analysis[[x for x in ind_analysis.columns if 'fin_' in x]]

        if method == 'mean':
            mix_val = ind_analysis.mean()[cols].sum()
        elif method == 'median':
            mix_val = ind_analysis.median()[cols].sum()
        else:
            raise ValueError(f"Invalid statistic '{method}'. Valid options are 'mean' and 'median'.")
        
        return mix_val