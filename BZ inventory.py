# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 19:14:48 2022

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

excel_name = r'.\Tmall SFS BZ received 0530.xlsx'
wb = openpyxl.load_workbook(excel_name)
sheets = wb.get_sheet_names()
# open_wb = xlrd.open_workbook(excel_name)
# sheets = open_wb.sheet_names()
excel_all = pd.DataFrame()


time_begin = time.time()

for i in range(len(sheets)):
    inv = pd.read_excel(excel_name,sheet_name=i,usecols = [3,4,5,6,7,9],engine='openpyxl')
    # inv = pd.read_excel(excel_name,sheet_name=i,usecols = [3,4,5,6,7,9])
    excel_all = pd.concat([inv,excel_all])
    
time_end = time.time()

time = (time_end - time_begin)/60.0

excel_all = excel_all.drop_duplicates()
excel_all['bar_code'] = excel_all['bar_code'].apply(lambda x:str(x).zfill(14))
excel_all['门店编号'] = excel_all['门店编号'].astype(object)
excel_all['create_time'] = excel_all['create_time'].astype('datetime64[ns]')
bz_inv1 = excel_all.sort_values(by='create_time')

bz_inv2 = bz_inv1.drop_duplicates(['bar_code','门店编号'],keep = 'last')

bz_inv2.to_csv(r'.\bz_inv2.csv')

