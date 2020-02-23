# -*- coding: utf-8 -*-
"""
Created on Fri Jan 24 16:16:31 2020

@author: A1029301
"""
import json
j="[1,2,3]"
print(json.loads(j))

try:
    j=json.loads(j)
except:
    j=j
    
    
    
<form class="d-flex justify-content-left">
              <!-- default input -->
              <input type="number" value="1" aria-label="search" class="form-control" style="width: 100px">
              <button class="btn btn-primary btn-md my-0 p" type="submit">add to cart
                <i class="fas fa-shopping-cart ml-1"></i>
              </button>

            </form>
            
            
cols = df.columns

num_cols = df._get_numeric_data().columns

num_cols
Index([u'0', u'1', u'2'], dtype='object')

list(set(cols) - set(num_cols))
['3', '4']




import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import gridspec
plt.style.use('ggplot')
df=pd.read_csv("adult.test.csv")
#df.head()
df.shape
anam_features=df.loc[:,0:11].columns
#t=anam_features[0]

for i in range(0,len(anam_features)):
    print(anam_features)
    if df.anam_features[i].dtype == 'category':
        print("True")
    else:
        print("False")
    
df["Sex"].name in df.select_dtypes(include='category').columns

plt.figure(figsize=(12,28*4))
gs=gridspec.GridSpec(28,1)
for i, cn in enumerate(df[anam_features]):
    #ax=plt.subplot(gs[i])
    #sns.distplot(df[cn][df.Class==1],bins=50)
    #sns.distplot(df[cn][df.Class==0],bins=50)
    ax.set_xlabel('')
    ax.set_title



import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib import gridspec
plt.style.use('ggplot')
df=pd.read_csv("adult.test.csv")
cols = df.columns
num_cols = df._get_numeric_data().columns
print(cols)
print(num_cols)
print(list(set(cols) - set(num_cols)))
cat_var = [key for key in dict(df.dtypes)
             if dict(df.dtypes)[key] in ['object'] ] 
for i in cols:
    t=0
    for j in df[i]:
        print(j)
    break
li=[df[df.nunique()>8]]





