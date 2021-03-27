from datetime import datetime
import pandas as pd
import unidecode
import os

from api.stats import *
from api.unsupervized import dendrogram
from api.correlation import correlation_network
from api.supervised import decision_tree
from statsmodels.stats.multicomp import MultiComparison

import subprocess

UPLOADS = 'api/static/uploads'
RESULTS = 'api/static/results'

def compute(params, data_list, uid):
    if len(data_list) < 2:
        raise Exception('Um dos arquivos não foi selecionado')

    metaname = [x for x in data_list if 'metadados' in x][0]
    if metaname:
        meta = pd.read_csv(os.path.join(UPLOADS, metaname), sep='\t')
    else:
        raise ValueError('metadados or dados tags not fount')

    if any(meta.ID.duplicated()):
        raise ValueError('metadados or dados tags not fount')

    meta.set_index('ID', inplace=True)
    meta.fillna('NA', inplace=True)
    meta = meta.astype(str)
    #meta.columns = [unidecode.unidecode(x) for x in meta.columns]
    #meta.columns = meta.columns.str.replace(' \(.+$', '')
    #meta.columns = meta.columns.str.replace('^ ', '')
    #meta.columns = meta.columns.str.replace(' ', '_')

    dataname = [x for x in data_list if '_dados' in x][0]
    if dataname:
        data = pd.read_csv(os.path.join(UPLOADS, dataname), sep='\t')
    else:
        raise ValueError('metadados or dados tags not fount')

    if any(data.ID.duplicated()):
        data = data.groupby('ID').mean()
    else:
        data.set_index('ID', inplace=True)

    data.fillna(0, inplace=True)
    data = data[data.columns[~data.apply(lambda a: sum(a)==0)]]

    # check indexes
    if params['analise']=='univariada':
        if params['univar']=='boxplot':
            now = datetime.now().strftime("%d|%m|%Y-%H:%M:%S")
            filename = f"{uid}###boxplot###{params['dfield']}-{params['mfield']}###{now}.pdf"
            dout = os.path.join(RESULTS, filename)
            boxplot(data, meta, params['dfield'], params['mfield'], dout)
        elif params['univar']=='tukey':
            cts = meta[params['mfield']].value_counts()
            meta.index = meta.index.str.replace(' ', '')
            data.index = data.index.str.replace(' ', '')
            cmeta = meta[meta[params['mfield']].isin(cts.index[cts>3])]
            cdata = data.loc[cmeta.index, params['dfield']]
            cmult = MultiComparison(cdata, cmeta[params['mfield']])
            results = cmult.tukeyhsd()
            now = datetime.now().strftime("%d|%m|%Y-%H:%M:%S")
            filename = f"{uid}###tukey###{params['dfield']}-{params['mfield']}###{now}.tsv"
            dout = os.path.join(RESULTS, filename)
            with open(dout, 'w+') as f:
                f.write(results.summary().as_text())
        elif params['univar']=='boxplot_tukey':
            cts = meta[params['mfield']].value_counts()
            meta.index = meta.index.str.replace(' ', '')
            data.index = data.index.str.replace(' ', '')
            cmeta = meta[meta[params['mfield']].isin(cts.index[cts>3])]
            cdata = data.loc[cmeta.index, params['dfield']]
            df = pd.concat([cdata, cmeta[params['mfield']]], axis=1)
            df.columns = ['value', 'treatment']

            now = datetime.now().strftime("%d|%m|%Y-%H:%M:%S")
            filename = f"{uid}###boxplot-tukey###All###{now}.pdf"
            ffeat = os.path.join(RESULTS,
                                 f"{uid}###boxplot-tukey###{params['dfield']}-{params['mfield']}###{now}_feat.tsv")

            df.to_csv(ffeat, sep='\t', index=None)
            dout = os.path.join(RESULTS, filename)
            fin = os.path.join(RESULTS,
                                f"{uid}###boxplot-tukey###All###{now}_feat.tsv")
            #call = f'/home/pylipids/api/supervised_script.py {ffeat} {fmeta} {params["mfield"]} {dout}'
            #os.system(call)
            subprocess.call(['Rscript', 'api/tukey_plot.r',
                             fin, dout])
        else:
            params['normalization'] = {}
            params['normalization']['perform'] = False
            params['normalization']['type'] = None

            params['comparison'] = {}
            params['comparison']['test'] = params['univar']
            params['comparison']['field'] = params['mfield']
            params['comparison']['classes'] = 'all'

            ctabsel = univariate(data, meta, params)

            now = datetime.now().strftime("%d|%m|%Y-%H:%M:%S")

            filename = f"{uid}###{params['comparison']['test']}###{params['comparison']['field']}###{now}.tsv"

            ctabsel.to_csv(os.path.join(RESULTS, filename), sep='\t')
    elif params['analise']=='multivariada':
        if params['mult']=='pcoa':
            now = datetime.now().strftime("%d|%m|%Y-%H:%M:%S")
            filename = f"{uid}###PCoA###All###{now}"
            dout = os.path.join(RESULTS, filename)
            plot_emperor(data, meta, dout)
        elif params['mult']=='heat':
            now = datetime.now().strftime("%d|%m|%Y-%H:%M:%S")
            filename = f"{uid}###heatmap###All###{now}.pdf"
            dout = os.path.join(RESULTS, filename)
            dendrogram(data, meta, filename=dout)
        elif params['mult']=='arv':
            now = datetime.now().strftime("%d|%m|%Y-%H:%M:%S")
            filename = f"{uid}###decision-tree###All###{now}.pdf"
            ffeat = os.path.join(RESULTS,
                                 f"{uid}###decision-tree###All###{now}_feat.tsv")
            fmeta = os.path.join(RESULTS,
                                 f"{uid}###decision-tree###All###{now}_meta.tsv")

            data.to_csv(ffeat, sep='\t', index=None)
            meta.to_csv(fmeta, sep='\t', index=None)
            dout = os.path.join(RESULTS, filename)
            #call = f'/home/pylipids/api/supervised_script.py {ffeat} {fmeta} {params["mfield"]} {dout}'
            #os.system(call)
            subprocess.call(['/home/pylipids/api/supervised_script.py', ffeat,
                             fmeta, params['mfield'], dout])
            #decision_tree(data, meta, params['mfield'], dout=dout)

    elif params['analise']=='correlacao':
        now = datetime.now().strftime("%d|%m|%Y-%H:%M:%S")
        filename = f"{uid}###correlation###All###{now}"
        dout = os.path.join(RESULTS, filename)
        correlation_network(data, filename=dout)


