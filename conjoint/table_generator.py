import pandas as pd
import os
import string
import plotly.figure_factory as ff


def table_generator(input_path:str,
                    label:str,
                    col_id:str,
                    path_to_save:str
                    ):
    '''
    A function to generate choice table to be asked to the respondents.

    Attributes
    ----------
    input_path : string
        File that contains all the options for the question later. Should be in csv file.
    label : string
        Label name regarding the topic, for example cars, banks, computers.
    col_id : string
        Question ID, indicating that one choice is a group of a set of choice.
    path_to_save : string
        Location to save the tables.
    '''
    
    # reading the csv file first
    if input_path.endswith('.csv'):
        df = pd.read_csv(input_path)
    else:
        raise ValueError('Input file should be a csv!')


    # create labels on all the options
    # by giving it sequential letter from A-Z
    letters = string.ascii_uppercase
    for i in range(len(df)):
        df.loc[i, 'label'] = f'{letters[i]} {label}'


    # create the directory of path_to_save if it doesn't exist
    if not os.path.exists(path_to_save):
        os.makedirs(path_to_save)


    # save all the files into tables in png format
    for id in range(df[col_id].min(), df[col_id].max() + 1):
        temp = df[df[col_id] == id]
        temp = temp.drop(col_id, axis=1)
        temp = temp.set_index('label').T
        
        # create table and save it
        
        fig = ff.create_table(temp, index=True, height_constant=40)
        fig.update_layout(width=800)
        
        # fig.show() 
        fig.write_image(f'{path_to_save}/table_options_{id}.png', scale=2)