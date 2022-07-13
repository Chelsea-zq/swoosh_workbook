# -*- coding: utf-8 -*-
"""
Created on Mon Nov 15 23:02:01 2021

@author: CZHA43
"""

import pandas as pd
import numpy as np

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


data1 = pd.read_table(r'C:\Users\czha43\Desktop\2211883262676_1639372498358.xls', sep='$',engine='python',encoding = 'gb18030',usecols = [0,1,5,7,10,11,23,31,32,33],converters = {0:str,1:str,2:str,3:str,4:int,5:str,6:str,7:str,8:str,9:str})
# data2 = pd.read_table(r'C:\Users\czha43\Desktop\2211883262676_1638776375100.xls',sep='$',engine='python',encoding = 'gb18030',usecols = [0,1,5,7,10,11,23,31,32,33],converters = {0:str,1:str,2:str,3:str,4:int,5:str,6:str,7:str,8:str,9:str})

data = pd.concat([data1])
data = data.drop_duplicates().reset_index()

# get date from datetime
def splitdatetime(timecolser):
    timelist = []
    for value in timecolser:
        datestr = value.split(' ')[0]
        timelist.append(datestr)
    timeser=pd.Series(timelist)
    return timeser

timeser = data.loc[:,'订单支付时间']
datestr = splitdatetime(timeser)
data.loc[:,'订单支付日期']=datestr
data.loc[:,'订单支付时间'] = pd.to_datetime(data.loc[:,'订单支付时间'],format = '%Y-%m-%d',errors = 'coerce')
data.loc[:,'订单支付日期'] = pd.to_datetime(data.loc[:,'订单支付日期'],format = '%Y-%m-%d',errors = 'coerce')


values = {'派单门店':'NIKEWH','派单门店自定义ID':'NIKEWH'}
data = data.fillna(value=values)

def sourcetype(df):
    if df['派单门店自定义ID'] == 'CLC001':
        return 'Store'
    elif df['派单门店自定义ID'] == 'NIKEWH':
        return 'NIKEWH'
    else:
        return 'Store'

data['sourcetype'] = data.apply(sourcetype, axis=1)

# keep raw data
data_raw = data

# add store province & city info
store_info = pd.read_excel(r'C:\Users\czha43\Desktop\Chelsea Working file\Table\Store Info.xlsx',usecols = [3,11,12],converters = {0:str,1:str,2:str})

data = pd.merge(data, store_info, left_on = '派单门店自定义ID',right_on = 'Pos Code',how = 'left')
data.drop(['Pos Code'], axis=1, inplace = True)


def sourcescope(df):
    if df['sourcetype'] == 'NIKEWH':
        return 'NIKEWH'
    elif (df['sourcetype'] == 'Store') & (df['市'] == df['City']):
        return 'Within City'
    elif (df['sourcetype'] == 'Store') & (df['省'] == df['Province']):
        return 'Within Province'
    elif (df['sourcetype'] == 'Store') & (df['省'] != df['Province']):
        return 'Out of Province'
    else:
        return 'Need to verify'
    
data['sourcescope'] = data.apply(sourcescope, axis=1)

data.to_csv(r'C:\Users\czha43\Desktop\result3.csv',index=False)

# calculate metrics
so_cnt = data.drop_duplicates(subset = ['交易主订单ID','订单支付日期'])
so_cnt = so_cnt['交易主订单ID'].groupby(so_cnt['订单支付日期']).count()
so_cnt = so_cnt.reset_index()

cn_cnt = data.drop_duplicates(subset = ['交易主订单ID','派单门店自定义ID','订单支付日期'])
cn_cnt = cn_cnt.groupby(['订单支付日期','派单门店自定义ID']).aggregate({'交易主订单ID':'count'}).reset_index()
cn_cnt_wh = cn_cnt[cn_cnt['派单门店自定义ID']=='NIKEWH'].reset_index()

line_cnt = data.drop_duplicates(subset = ['交易主订单ID','交易子订单ID','订单支付日期'])
line_cnt = line_cnt.groupby(['订单支付日期','sourcetype']).aggregate({'交易子订单ID':'count'}).reset_index()

units = data['购买数量'].groupby(data['订单支付日期']).sum()
units_sourcetype = data.groupby(['订单支付日期','sourcetype']).aggregate({'购买数量':'sum','交易子订单ID':'count'}).reset_index()

source = data.drop_duplicates(subset = ['交易主订单ID','sourcescope','订单支付日期'])[['交易主订单ID','sourcescope','订单支付日期']]
source = source.sort_values(by ='sourcescope')

sourcelogic = source.groupby(['订单支付日期','交易主订单ID'])['sourcescope'].apply(lambda x:x.tolist())
sourcelogic = sourcelogic.reset_index()
        
sourcelogic['sourcescope'] = sourcelogic['sourcescope'].apply(lambda x:tuple(x))
source_cnt = pd.pivot_table(sourcelogic,values = '交易主订单ID',index = 'sourcescope',columns='订单支付日期',aggfunc='count',margins=True)
source_cnt = source_cnt.sort_values(by ='All',ascending=False).reset_index()
source_cnt.to_excel(r'C:\Users\czha43\Desktop\source_cnt.xlsx',index=False)

a = sourcelogic.iloc[:,2]
sourcelogic_set = []
for i in a:
    if i not in sourcelogic_set:
        sourcelogic_set.append(i)

sourcelogic_set = pd.Series(sourcelogic_set,name = 'sourcescope')

source_merge = pd.merge(sourcelogic,sourcelogic_set,how='left',on = 'sourcescope')

source_mu = sourcelogic[(sourcelogic['sourcescope']!=sourcelogic_set[0]) & (sourcelogic['sourcescope']!=sourcelogic_set[1]) & (sourcelogic['sourcescope']!=sourcelogic_set[2]) & (sourcelogic['sourcescope']!=sourcelogic_set[4])]
source_mu = pd.merge(source_mu,data,how = 'inner',on='交易主订单ID')
# source_mu.to_excel(r'C:\Users\czha43\Desktop\source_mu.xlsx',index=False)

source_storecnt = data.drop_duplicates(subset = ['交易主订单ID','派单门店自定义ID','sourcescope','订单支付日期'])
source_storecnt = source_storecnt.groupby(['订单支付日期','交易主订单ID','sourcescope']).aggregate({'派单门店自定义ID':'count'}).reset_index()
source_storecnt.rename(columns = {'派单门店自定义ID': 'cnt_by_source'},inplace=True)
source_storecnt = source_storecnt.groupby(['订单支付日期','sourcescope','cnt_by_source']).aggregate({'交易主订单ID':'count'}).reset_index()


source_ttlcnt = data.drop_duplicates(subset = ['交易主订单ID','派单门店自定义ID','订单支付日期'])
source_ttlcnt = source_ttlcnt.groupby(['订单支付日期','交易主订单ID']).aggregate({'派单门店自定义ID':'count'}).reset_index()
source_ttlcnt.rename(columns = {'派单门店自定义ID': 'cnt_ttl'},inplace=True)
source_ttlcnt = source_ttlcnt.groupby(['订单支付日期','cnt_ttl']).aggregate({'交易主订单ID':'count'}).reset_index()

source_storecnt.to_excel(r'C:\Users\czha43\Desktop\source_storecnt.xlsx',index=False)
source_ttlcnt.to_excel(r'C:\Users\czha43\Desktop\source_ttlcnt.xlsx',index=False)

cn_cnt.to_excel(r'C:\Users\czha43\Desktop\cn_cnt.xlsx',index=False)
line_cnt.to_excel(r'C:\Users\czha43\Desktop\line_cnt.xlsx',index=False)
units_sourcetype.to_excel(r'C:\Users\czha43\Desktop\units_sourcetype.xlsx',index=False)
