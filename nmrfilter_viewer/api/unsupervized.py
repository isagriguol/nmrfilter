import pandas as pd
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.cluster.hierarchy as shc

def dendrogram(df, meta, scale=True, color_block=[], xlabel='',
               filename=None, row_cluster=True, col_cluster=True):
    sns.set(font_scale=0.7)
    if scale:
        df = (df-df.mean())/df.std()

    if len(color_block):
        minha_paleta = dict(zip(meta['groups'].unique(), color_block))
        cores_linhas = meta['groups'].map(minha_paleta)
        cg = sns.clustermap(df, metric="canberra", method="ward",
                            cmap="Blues",  row_colors=cores_linhas)
    else:
        cg = sns.clustermap(df, metric="canberra", method="ward",
                            cmap="Blues", row_cluster=row_cluster,
                            col_cluster=col_cluster)
    # , xticklabels=False
    ax = cg.ax_heatmap
    ax.set_xlabel(xlabel)
    if filename is not None:
        with PdfPages(filename) as pdf:
            pdf.savefig()
            plt.close()

