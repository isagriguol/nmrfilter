import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multitest import multipletests
import xmltodict
import requests
import io
import os
import yaml
import json

import qiime2
from qiime2 import Artifact
import pandas as pd
from qiime2.plugins import metadata, feature_table, diversity, emperor
from scipy.spatial.distance import squareform, pdist
import os
import sys
import yaml
import requests
import xmltodict
import json
import io
import re
import skbio

import matplotlib.pyplot as plt
import seaborn as sns;
from matplotlib.backends.backend_pdf import PdfPages

def multi_class(data, cn, features, method):
#    if len(data.groupby(cn)) <= 2:
#        raise Exception('ANOVA requires a secondary index with three or more values')
    if method=='anova':
        func = stats.f_oneway
    elif method=='kruskal':
        func = stats.kruskal
    vstats = []
    for col in features:
        cls = []
        for k, v in data[[cn,col]].groupby(cn):
            cls.append(v[col])
        vstats.append(func(*cls))
    return pd.DataFrame(vstats)

def univariate(feat, meta, params):
    """ Performs the selected univariate test in all features.
    Parameters
    ----------
    feat : pd.DataFrame
       Feature dataframe with sample names as index
       and features in the columns
    meta : pd.DataFrame
       Sample names as index, followed by metadata fields
       on the columns
    params : dict
    Returns
    -------
    summary table : pd.DataFrame
       Dataframe containing the summary statistics for
       selected test
    """
    # Replace missin values
    # should think about different scales of variables
    #mnfeat = feat[feat!=0].min().min()
    #feat.replace(0, mnfeat*(2/3), inplace=True)

    if params['normalization']['perform'] and \
       params['normalization']['type']=='TIC':
        feat = feat.apply(lambda a: a/sum(a), axis=1)

    # should transformations be applied?
    #feat = feat.transform(np.log10)
    fnames = feat.columns
    feat = pd.merge(meta, feat, left_index=True,
                     right_index=True)

    if 'filter' in params.keys():
        if params['filter']['perform']:
            fvalues = params['filter']['value'].split(',')
            meta = meta[~meta[params['filter']['field']].isin(fvalues)]

    if 'keep' in params.keys():
        if params['keep']['perform']:
            fvalues = params['keep']['value'].split(',')
            meta = meta[meta[params['keep']['field']].isin(fvalues)]

    if 'filter' in params.keys() or 'keep' in params.keys():
        feat = feat[feat.index.isin(meta.index)]

    if params['comparison']['test']=='ttest':
        cs = params['comparison']['classes'].split(',')
        cn = params['comparison']['field']
        idx0 = feat.index[feat[cn].isin([cs[0]])]
        idx1 = feat.index[feat[cn].isin([cs[1]])]
        ttest = feat[fnames].apply(lambda a: stats.ttest_ind(a[idx0], a[idx1]))
        ttest = pd.DataFrame(ttest.tolist())
        pvals = ttest['pvalue']
        pcor = multipletests(pvals, method='fdr_bh')[1]
    elif params['comparison']['test']=='wilcox':
        cs = params['comparison']['classes'].split(',')
        cn = params['comparison']['field']
        idx0 = feat.index[feat[cn].isin([cs[0]])]
        idx1 = feat.index[feat[cn].isin([cs[1]])]
        tkruskal = feat[fnames].apply(lambda a: stats.kruskal(a[idx0], a[idx1]))
        tkruskal = pd.DataFrame(tkruskal.tolist())
        pvals = tkruskal['pvalue']
        pcor = multipletests(pvals, method='fdr_bh')[1]
    elif params['comparison']['test']=='anova':
        cn = params['comparison']['field']
        if params['comparison']['classes']=='all':
            cs = feat[cn].value_counts()
            cs = cs[cs>2].index.tolist()
        else:
            cs = params['comparison']['classes'].split(',')
        feat2 = feat[feat[cn].isin(cs)]
        tanova = multi_class(feat2, cn, fnames, 'anova')
        pvals = tanova['pvalue']
        pcor = multipletests(pvals, method='fdr_bh')[1]
    elif params['comparison']['test']=='kruskal':
        cn = params['comparison']['field']
        if params['comparison']['classes']=='all':
            cs = feat[cn].value_counts()
            cs = cs[cs>2].index.tolist()
        else:
            cs = params['comparison']['classes'].split(',')
        feat2 = feat[feat[cn].isin(cs)]
        tkruskal = multi_class(feat2, cn, fnames, 'kruskal')
        pvals = tkruskal['pvalue']
        pcor = multipletests(pvals, method='fdr_bh')[1]

    ctabsel = pd.DataFrame(index=fnames)
    #ctabsel['fchange'] = fchange
    ctabsel['pval'] =  pvals.tolist()
    ctabsel['cpval'] = pcor

    return ctabsel

nonphyl_metrics = {'braycurtis', 'canberra', 'chebyshev', 'cityblock', 'correlation', 'cosine',
                       'dice', 'euclidean', 'hamming', 'jaccard', 'kulsinski', 'mahalanobis', 'matching',
                       'rogerstanimoto', 'russellrao', 'seuclidean', 'sokalmichener', 'sokalsneath',
                       'sqeuclidean', 'wminkowski', 'yule'}

def plot_emperor(data, meta, dout, metric='euclidean'):
    """ Creates emperor plot from quantification table.
    Parameters
    ----------
    data : pd.DataFrame
       Quantitative data
    meta : pd.DataFrame
       Metadata
    metric : str
      Dissimilarity measure, options available in nonphyl_metrics dict
    Returns
    -------
    .qzv : file
       uncompressed qsv file
    """


    #if params['pcoa_norm']:
    #    data = data.apply(lambda a: a/sum(a), axis=1)

    #if params['pcoa_scale']:
    #    data = (data-data.mean())/data.std()
    data = (data-data.mean())/data.std()

    meta_order = pd.merge(data, meta, left_index=True,
                     right_index=True)
    meta = meta.loc[meta_order.index]
    qsample_metadata = qiime2.metadata.Metadata(meta.apply(lambda a: a.str.replace(' $', '')))

    data = data.loc[meta_order.index]

    dm1 = squareform(pdist(data, metric=metric))
    dm1 = skbio.DistanceMatrix(dm1, ids=data.index.tolist())
    dm1 = Artifact.import_data("DistanceMatrix", dm1)
    pcoa = diversity.methods.pcoa(dm1)
    emperor_plot = emperor.visualizers.plot(pcoa.pcoa,
                                            qsample_metadata,
                                            ignore_missing_samples=True)
    emperor_plot.visualization.export_data(dout)


def boxplot(data, meta, data_field, meta_field, out):
    tmp = pd.merge(meta, data, left_index=True,
                     right_index=True)

    ax = sns.boxplot(x=meta_field, y=data_field, data=tmp)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    with PdfPages(out) as pdf:
        pdf.savefig()
        plt.close()
    #fig.clf()
    #ax = sns.barplot(x="groups", y=tmp.columns[0], data=tmp, capsize=.2)
    #ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
    #fig = ax.get_figure()
    #fig.savefig("figs/g%s.png" % i)



