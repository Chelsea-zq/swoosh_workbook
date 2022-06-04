# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 19:15:39 2022

@author: zhang
"""

import pandas as pd
import numpy as np
import os
import json
import time

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)

os.getcwd()
path = r'C:\Users\zhang\Desktop\inventory mapping'
os.chdir(path)

jsonpath = r'.\json'
filelist = os.listdir(jsonpath)

data_json = pd.DataFrame([])
data_json_all = pd.DataFrame([])

time1 = time.time()

for json_file in filelist:
    with open(os.path.join(jsonpath,json_file),'r') as f:
        data = json.loads(f.read())
        data_json = pd.json_normalize(data,record_path=['items'],meta=['businessUnit'])
        data_json_all = pd.concat([data_json,data_json_all])

time2 = time.time()    
time_=(time2 - time1)/60.0
    
doms_inv = data_json_all.groupby(['businessUnit','universalProductCode']).sum().reset_index()

uuid = pd.read_excel(r'.\UUID.xlsx')

doms_inv1 = pd.merge(doms_inv,uuid,left_on = 'businessUnit',right_on = 'STORE_ID',how='inner')

doms_inv1['storeCode'] = doms_inv1['STORE_NUMBER'].astype(object)

doms_inv2 = doms_inv1[['storeCode','universalProductCode','onhandAvailableQuantity']]

byStore_inv = doms_inv2.groupby(['storeCode']).sum().reset_index()

byStore_inv.to_excel(r'.\byStore_inv.xlsx')

doms_inv2.to_csv(r'.\doms_inv2.csv')