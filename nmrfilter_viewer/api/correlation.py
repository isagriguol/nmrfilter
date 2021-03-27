# https://stackoverflow.com/questions/52229220/partial-correlation-in-python
import networkx as nx
import pandas as pd

def correlation_network(df, thr = 0.5, aux=None, aux_field='',
                        pos=None, node_scale=1, filename=None):
    cor = df.corr()
    G = nx.from_numpy_matrix(cor.values)
    edlist = list(nx.to_edgelist(G))
    edmatrix = pd.DataFrame([list(x)[:2]+[x[2]['weight']] for x in edlist])
    edmatrix = edmatrix[edmatrix[0]!=edmatrix[1]]
    edmatrix = edmatrix[abs(edmatrix[2]) > thr]
    edmatrix[0] = df.columns[edmatrix[0]]
    edmatrix[1] = df.columns[edmatrix[1]]

    G = nx.DiGraph((x, y, {'weight': v}) for x, y, v in edmatrix.apply(lambda a: tuple(a), axis=1).tolist())

    if type(pos)==str:
        pos = pd.read_csv(pos, sep='\t', header=None)
    elif type(pos)==type(None):
        # need to be tested
        pos = nx.spring_layout(G)
        pos = pd.DataFrame(pos).T
    for i in edmatrix.index:
        x, y, v = edmatrix.loc[i,:]
        G.add_edge(x, y, graphics={
            'width': v, 'fill': '"#0000ff"', 'type': '"line"'
        })
    #    if v<0:
    #        G.add_edge(x, y, EDGE_LINE_TYPE="LONG_DASH")
    #    else:
    #        G.add_edge(x, y, EDGE_LINE_TYPE="SOLID")

    if aux is not None:
        for n in pos.index:
            x, y = pos.loc[n, :]
            if aux.loc[n, 'pval'] < 0.05:
                wth = 5
            else:
                wth = 0
            nx.set_node_attributes(G, {
                n: {'x': x, 'y': y, 'w': node_scale*aux.loc[n,aux_field],
                    'h': node_scale*aux.loc[n,aux_field], 'type':"ELLIPSE",
                    'type': '"ellipse"', 'outline':"#000000", 'fill':"#89D0F5",
                    'width':wth, 'label_font_size':100
                    },
                }, 'graphics')
            #nx.set_node_attributes(G, {n:"S,N,c,0.00,0.00"} , "NODE_LABEL_POSITION")

    if filename is not None:
        nx.write_gml(G, '%s.gml' % filename)

    return G

