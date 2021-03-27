#!/home/rsilva/miniconda3/envs/qiime2-2020.2/bin/python
##/opt/conda/envs/qiime2-2020.2/bin/python

from sklearn import tree
from sklearn.externals.six import StringIO
#import pydot
import pandas as pd
import pydotplus
import os
import sys
from datetime import datetime

RESULTS = '/home/rsilva/pylipids_lmscc/api/static/results'

def decision_tree(uid, meta_field):
    fls = os.listdir(RESULTS)
    feat = [x for x in fls if uid in x and '_feat' in x][0]
    meta = [x for x in fls if uid in x and '_meta' in x][0]
    feat = os.path.join(RESULTS, feat)
    meta = os.path.join(RESULTS, meta)
    feat2 = pd.read_csv(feat, sep='\t')
    meta2 = pd.read_csv(meta, sep='\t')
    meta_order = pd.merge(meta2, feat2, left_index=True,
                     right_index=True)
    feat2 = feat2.loc[meta_order.index]
    clf = tree.DecisionTreeClassifier()
    clf = clf.fit(feat2, meta_order[meta_field])

    now = datetime.now().strftime("%d|%m|%Y-%H:%M:%S")
    filename = f"{uid}###decision-tree###All###{now}.pdf"
    dout = os.path.join(RESULTS, filename)

    dot_data = StringIO()
    tree.export_graphviz(clf, out_file=dot_data,
                      feature_names=feat2.columns,
                      class_names=meta_order[meta_field],
                      filled=True, rounded=True,
                      special_characters=True)
    graph = pydotplus.graph_from_dot_data(dot_data.getvalue())
    graph.write_pdf(dout)
    os.remove(feat)
    os.remove(meta)
    #graph = pydot.graph_from_dot_data(dot_data)
    #graph[0].write_pdf(dout)

if __name__=='__main__':
    print(sys.argv)
    decision_tree(sys.argv[1], sys.argv[2])

