# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 17:03:52 2022

@author: zhang
"""

import pandas as pd
import xlrd
import os
import time

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

os.getcwd()
path = r'C:\Users\zhang\Desktop\inventory mapping'
os.chdir(path)

bz_inv = pd.read_csv(r'.\bz_inv2.csv',usecols = [1,2,4,5])
bz_inv['门店编号'] = bz_inv['门店编号'].astype(str)
bz_inv['size'] = bz_inv['size'].apply(lambda x:x.split(',')[1])

old = ['XSA/C','XLD/E','XLC/E','XLA/B','SD/E','SA/C','MD/E']
new = ['XSA-C','XLD-E','XLC-E','XLA-B','SD-E','SA-C','MD-E']

bz_inv['size'] = bz_inv['size'].replace(old,new)

store_list = pd.read_excel(r'.\store_list.xlsx',dtype=str)

store_available = pd.merge(bz_inv,store_list,left_on = ['门店编号'],right_on = ['STORE_NUMBER'],how='inner')

store_available.drop(columns = ['STORE_NUMBER'],inplace=True)

store_available.to_excel(r'.\store_available.xlsx',index=False)