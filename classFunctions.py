#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 31 14:17:38 2022

@author: rnguymon

Contains functions that we have used in ACCY 576
"""
#%% Required modules
import re as re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
#%% tidyUpCols Function
def tidyUpCols(myList, keepNums = False):
    '''
    Parameters
    ----------
    myList : List
        List of column names, like df.columns
    keepNums : Bool
        Whether we want to keep numbers in column names. The default is False.

    Returns
    -------
    ml2 : List
        List of tidy column names.
    '''
    ml2 = []
    for i in range(len(myList)):
        if myList[i] != None:
            ti = myList[i].strip().lower().replace('.', '').replace('/', '_').replace(' ', '_').replace('$', '')
        else:
            continue # Goes to the next iteration in the for loop
        
        if '--' in ti:
            ti2 = ti.split('--')
            [ml2.append(x) for x in ti2]
        elif keepNums == True:
            ti = re.sub('[^a-zA-Z_0-9]', '', ti)
            ml2.append(ti)
        else:
            ti = re.sub('[^a-zA-Z_]', '', ti)
            ml2.append(ti)
    return ml2

#%% Importing module from other path on machine
'''
import sys
sys.path.insert(0, '/Users/rnguymon/Box Sync/ACCY 576/')
import classFunctions as cf
'''
#%% Converting data types
'''
\https://stackoverflow.com/questions/15891038/change-column-type-in-pandas
to_numeric()
astype()
infer_objects()
convert_dtypes()
'''
#%% 8 most used functions
'''
https://towardsdatascience.com/i-have-been-using-pandas-for-3-years-here-are-the-8-functions-i-use-the-most-4e54f4db5656
1. pd.read_csv()
2. value_counts()
3. astype()
4. isna()
5. dropna()
6. fillna()
7. groupby()
8. unique() and nunique()
'''
#%% assignmentPlots function
def assignmentPlots(filePath, numAssignments, startColIndex, ydIndex=None):
    '''
    This function uses an export from canvas to create boxplots and stripplots
    of assignments.

    Parameters
    ----------
    filePath : Str
        Full path to the location of the Canvas gradebook file.
    numAssignments : Int
        The number of assignments for which you want to create box plots.
    startColIndex : Int
        The column index where the assignments start. This assumes that all 
        of the assignment columns are adjacent.
    ydIndex : Int
        The column index for the yellowdig assignment, if there is one.

    Returns
    -------
    A box and whisker plot on the left and a stripplot on the right.

    '''
    df = pd.read_csv(filePath)
    # numAssignments = 4 # Number of homework assignments
    
    # Extract only student name and homework columns and remove first two rows
    colNums = [0]
    if ydIndex is not None:
        colNums.append(ydIndex)
    colNums.extend(list(range(startColIndex,startColIndex+numAssignments))) # Adds items of a list to a list without nesting
    df = df.iloc[2:,colNums]
        
    # Create new column names for homework assignments
    colNames = ['Student']
    hwCols = ['h'+ str(i) for i in range(1,numAssignments+1)]
    if ydIndex is not None:
        hwCols.insert(0,'yd')
    colNames.extend(hwCols)
    df.columns = colNames
    
    # Remove test student
    df = df[df.Student != 'Student, Test']
    
    # Convert hw columns to numeric
    df[hwCols] = df[hwCols].apply(pd.to_numeric)
    # df.info() # Check to make sure it looks correct
    
    # Convert from wide to long
    hw = df.melt(value_vars=hwCols, var_name='Homework', value_name='Score')
    
    # Create canvas with two columns
    fig, axs = plt.subplots(figsize = (15, 5), ncols=2)
    fig.tight_layout(pad = 2)
    
    # Boxplot on left side
    sns.boxplot(data = hw, x = 'Homework', y = 'Score', hue='Homework'
                , ax = axs[0], showmeans = True
               , meanprops={'markeredgecolor': 'black'})
    axs[0].set_title('Boxplot of Homework Scores');
    
    # Stripplot on right side
    sns.stripplot(data = hw, x = 'Homework', y = 'Score', hue = 'Homework'
                  , ax = axs[1])
    axs[1].set_title('Stripplot of Homework Scores')
    
# Test out the function
# assignmentPlots('/Users/rnguymon/Downloads/htdy2.csv', 5, 9)
    
#%% relocate function
def relocate(df, old_index, new_index):
    '''
    This function relocates one column of a dataframe based on index number.

    Parameters
    ----------
    df : Pandas dataframe
        This is the dataframe object that has a column you would like to 
        relocate.
    old_index : INT
        This is th eindex number of the column that you want to relocate.
    new_index : INT
        This is the destination index number of the relocated column.

    Returns
    -------
    df : Pandas dataframe
        The same dataframe with the relocated column.

    '''
    # Convert column names to a list, col_names
    col_names = df.columns.tolist()
    # Remove the column and insert it into a new location
    col_names.insert(new_index, col_names.pop(old_index))
    # Slice the dataframe using the col_names list
    df = df.loc[:,col_names]
    # Return the dataframe
    return df


