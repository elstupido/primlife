from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
from biots import biots


graphviz = GraphvizOutput()
graphviz.output_file = 'E:/pygraph/test.png'

with PyCallGraph(output=graphviz):
    biots.main()
    
    
    