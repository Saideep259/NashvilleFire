# Cluster - hexagons

import pandas as pd
import numpy as np
import pickle
import itertools

firedf = pd.read_csv('hexTable.csv',usecols=range(1,24))

# get column headers
header_list = list(firedf)

# collect data according to cluster
nclusters = len(set(firedf.Cluster))

## ================================================================
## Hex location should be based on several attributes such as Weather, Disc TOD, Day, Month, Intersection Dist
## Within each cluster, we need to define location probabilities based on these attributes

# Weather: 10
# Disc TOD: 4
# Day: 7
# Month: 12
# Total number of combinations: 10 x 4 x 7 x 12 = 3360 combinations

unique_weather = list(np.unique(firedf['Weather Enum']))
unique_tod = list(np.unique(firedf['Disc TOD']))
unique_day = list(np.unique(firedf['Day']))
unique_month = list(np.unique(firedf['Month']))

list_attributes = [unique_weather,unique_tod,unique_day,unique_month]
list_all_combs = list(itertools.product(*list_attributes))

dict_cluster_hexprob = {}

for i1 in range(nclusters):
    data_clust = firedf.loc[(firedf['Cluster']==i1+1)]
    value_dict = {} #key: combination, value = dictionary of location and prob
    
    for i2 in range(len(list_all_combs)):
        subset_data = data_clust.loc[(data_clust['Weather Enum']==list_all_combs[i2][0]) & (data_clust['Disc TOD']==list_all_combs[i2][1]) & (data_clust['Day']==list_all_combs[i2][2])& (data_clust['Month']==list_all_combs[i2][3])]
        hexdata_mat = subset_data['hexWhereIncidentOccurred'].as_matrix()
        ndata_subset = len(hexdata_mat)
        
        if ndata_subset > 0:
            ones1 = (1./ndata_subset)*np.ones(ndata_subset,)
            
            # Create dummy df
            dum = {'ones': ones1, 'hex': hexdata_mat}
            dum_df = pd.DataFrame(data=dum)
            dum_df2 = dum_df.groupby(dum_df.hex).sum()
            dum_dict = dict([(i,j) for i,j in zip(dum_df2.index, dum_df2.ones)])
            value_dict[str(list_all_combs[i2])] = dum_dict
        else:
            value_dict[str(list_all_combs[i2])] = {}
        

    dict_cluster_hexprob[i1+1] = value_dict

## ================================================
# Save as pickle

with open("dict_hexdata_prob.pickle","wb") as freq1:
    pickle.dump(dict_cluster_hexprob, freq1)