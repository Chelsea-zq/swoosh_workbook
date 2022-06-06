# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 20:17:53 2022

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

doms_inv = pd.read_csv(r'.\doms_inv2.csv')
bz_inv = pd.read_csv(r'.\bz_inv2.csv')
doms_inv['storeCode'] = doms_inv['storeCode'].astype(object)
bz_inv['门店编号'] = bz_inv['门店编号'].astype(object)
bz_inv['bar_code'] = bz_inv['bar_code'].apply(lambda x:str(x).zfill(14)).astype(object)

inv_mapping = pd.merge(bz_inv,doms_inv,left_on = ['门店编号','bar_code'],right_on = ['storeCode','universalProductCode'],how='outer')

inv_mapping = inv_mapping[['门店编号','storeCode','bar_code','universalProductCode','货号','size','数量','onhandAvailableQuantity']]

inv_mapping['storeCode'].fillna(inv_mapping['门店编号'],inplace=True)
inv_mapping['universalProductCode'].fillna(inv_mapping['bar_code'],inplace=True)
inv_mapping.drop(columns = ['门店编号','bar_code'],inplace=True)
inv_mapping['数量'].fillna(0,inplace=True)
inv_mapping['onhandAvailableQuantity'].fillna(0,inplace=True)

inv_mapping['doms-bz'] = inv_mapping['onhandAvailableQuantity'] - inv_mapping['数量']
inv_mapping['abs(diff)'] = inv_mapping['doms-bz'].abs()
inv_diff = inv_mapping[inv_mapping['doms-bz'] != 0]

inv_diff.to_excel(r'.\inv_diff.xlsx',index=False)
