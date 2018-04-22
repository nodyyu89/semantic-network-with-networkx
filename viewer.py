try:
    # Python 3
    import tkinter as tk
    import tkinter.messagebox as tkm
    import tkinter.simpledialog as tkd
except ImportError:
    # Python 2
    import Tkinter as tk
    import tkMessageBox as tkm
    import tkSimpleDialog as tkd



import networkx as nx

from networkx_viewer.graph_canvas import GraphCanvas
from networkx_viewer.tokens import TkPassthroughEdgeToken, TkPassthroughNodeToken
from networkx_viewer.autocomplete_entry import AutocompleteEntry



class ViewerApp(tk.Tk):
    """Example simple GUI to plot a NetworkX Graph"""
    def __init__(self, graph, **kwargs):
        """Additional keyword arguments beyond graph are passed down to the
        GraphCanvas.  See it's docs for details"""
        tk.Tk.__init__(self)
        self.geometry('1000x600')
        self.title('NetworkX Viewer')

        bottom_row = 10
        self.columnconfigure(0, weight=1)
        self.rowconfigure(bottom_row, weight=1)

        self.canvas = GraphCanvas(graph, width=400, height=400, **kwargs)
        self.canvas.grid(row=0, column=0, rowspan=bottom_row+2, sticky='NESW')
        self.canvas.onNodeSelected = self.onNodeSelected
        self.canvas.onEdgeSelected = self.onEdgeSelected

        r = 0   # Current row
        tk.Label(self, text='Nodes:').grid(row=r, column=1, sticky='W')
        self.node_entry = AutocompleteEntry(self.canvas.dataG.nodes)
        self.node_entry.bind('<Return>',self.add_node, add='+')
        self.node_entry.grid(row=r, column=2, columnspan=2, sticky='NESW', pady=2)
        tk.Button(self, text='+', command=self.add_node, width=2).grid(
            row=r, column=4,sticky=tk.NW,padx=2,pady=2)

        r += 1
        nlsb = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.node_list = tk.Listbox(self, yscrollcommand=nlsb.set, height=5)
        self.node_list.grid(row=r, column=1, columnspan=3, sticky='NESW')
        self.node_list.bind('<Delete>',lambda e: self.node_list.delete(tk.ANCHOR))
        nlsb.config(command=self.node_list.yview)
        nlsb.grid(row=r, column=4, sticky='NWS')

        r += 1
        tk.Label(self, text='Neighbors Levels:').grid(row=r, column=1,
                                                    columnspan=2, sticky=tk.NW)
        self.level_entry = tk.Entry(self, width=4)
        self.level_entry.insert(0,'1')
        self.level_entry.grid(row=r, column=3, sticky=tk.NW, padx=5)

        r += 1
        tk.Button(self, text='Build New', command=self.onBuildNew).grid(
            row=r, column=1)
        tk.Button(self, text='Add to Existing', command=self.onAddToExisting
                  ).grid(row=r, column=2, columnspan=2)

        r += 1
        line = tk.Canvas(self, height=15, width=200)
        line.create_line(0,13,250,13)
        line.create_line(0,15,250,15)
        line.grid(row=r, column=1, columnspan=4, sticky='NESW')

        r += 1
        tk.Label(self, text='Filters:').grid(row=r, column=1, sticky=tk.W)
        self.filter_entry = tk.Entry(self)
        self.filter_entry.bind('<Return>',self.add_filter, add='+')
        self.filter_entry.grid(row=r, column=2, columnspan=2, sticky='NESW', pady=2)
        tk.Button(self, text='+', command=self.add_filter, width=2).grid(
            row=r, column=4,sticky=tk.NW,padx=2,pady=2)

        r += 1
        flsb = tk.Scrollbar(self, orient=tk.VERTICAL)
        self.filter_list = tk.Listbox(self, yscrollcommand=flsb.set, height=5)
        self.filter_list.grid(row=r, column=1, columnspan=3, sticky='NESW')
        self.filter_list.bind('<Delete>',self.remove_filter)
        flsb.config(command=self.node_list.yview)
        flsb.grid(row=r, column=4, sticky='NWS')

        r += 1
        tk.Button(self, text='Clear',command=self.remove_filter).grid(
                    row=r, column=1, sticky='W')
        tk.Button(self, text='?', command=self.filter_help
                  ).grid(row=r, column=4, stick='NESW', padx=2)


        r += 1
        line2 = tk.Canvas(self, height=15, width=200)
        line2.create_line(0,13,250,13)
        line2.create_line(0,15,250,15)
        line2.grid(row=r, column=1, columnspan=4, sticky='NESW')

        r += 1
        self.lbl_attr = tk.Label(self, text='Attributes',
                                 wraplength=200, anchor=tk.SW, justify=tk.LEFT)
        self.lbl_attr.grid(row=r, column=1, columnspan=4, sticky='NW')

        r += 1
        self.tbl_attr = PropertyTable(self, {})
        self.tbl_attr.grid(row=r, column=1, columnspan=4, sticky='NESW')

        assert r == bottom_row, "Set bottom_row to %d" % r

        self._build_menu()

    def _build_menu(self):
        self.menubar = tk.Menu(self)
        self.config(menu=self.menubar)

        view = tk.Menu(self.menubar, tearoff=0)
        view.add_command(label='Center on node...', command=self.center_on_node)
        view.add_separator()
        view.add_command(label='Reset Node Marks', command=self.reset_node_markings)
        view.add_command(label='Reset Edge Marks', command=self.reset_edge_markings)
        view.add_command(label='Redraw Plot', command=self.canvas.replot)
        view.add_separator()
        view.add_command(label='Grow display one level...', command=self.grow_all)

        self.menubar.add_cascade(label='View', menu=view)
        
        algorithms = tk.Menu(self.menubar, tearoff=0)
        self.menubar.add_cascade(label='Algorithms', menu=algorithms)
        algorithms.add_command(label='Clique', command=self.clique)
        algorithms.add_command(label='Clustering', command=self.clustering)
        algorithms.add_command(label='Centrality', command=self.centrality)
        algorithms.add_separator()
        
    def clique(self):
        import config
        graphs = config.graph
        file = open('clique.txt','w')
        clique_string = ["This txt file will show you the finding of cliques in your network.\n\n"+
                        "Description : In complex network, a clique is a maximal subset of the vertices or nodes in an undirected network such that every member\n"
                        +"of the set is connected by an edge or link to every other node."
                        +"The meaning of 'maximal' here means there is no other vertex or node in the network that can be added to the subset while keeping or preserving\n"
                        +"the property that every vertex or node is connected to every other.\n"]
        file.write(clique_string[0])
        
        max_clique = list(nx.make_max_clique_graph(graphs))
        max_clique_str = str(max_clique)
        max_clique_string = ["Maximal Cliques:\n-The maximal cliques and treats these cliques as nodes.\n -These nodes in a [] are connected if they have common members in the original graph.\n"+"-"+max_clique_str+'\n']
        file.write(max_clique_string[0])
        
        all_maximal_cliques = str(list(nx.find_cliques(graphs)))
        all_maximal_cliques_string = ["Cliques:\n-The possible cliques in the network.\n"+"-"+all_maximal_cliques+'\n']
        file.write(all_maximal_cliques_string[0])
        
        number_of_maximum_clique = str(nx.graph_number_of_cliques(graphs))
        number_of_node_in_largest_clique = str(nx.graph_clique_number(graphs))
        clique_number_string = ["Basic statistic of cliques in network:\n-The (largest) number of cliques in the network:"+number_of_maximum_clique+"\n"+"-The number of nodes in the largest clique in the network:"+number_of_node_in_largest_clique]
        file.write(clique_number_string[0])
        
        file.close() # this must add or only display a empty txt
        import os
        os.system("notepad.exe clique.txt")
        
    def clustering(self):
        import config
        graphs = config.graph
        file = open('clustering.txt','w')
        
        cluster_string = ['This txt file will show you the finding of clusters in your network.\n\n'+
                          "Description : In complex network, nodes tend to gather and cluster together, which is called 'small-world' phenomenon.\n"+
                          "              Therefore, different clustering coefficient is a measure of the degree to which nodes in a graph tend to cluster together.\n"]
        file.write(cluster_string[0])
        file.write("\n\n")
        
        cluster = nx.clustering(graphs)
        cluster_list = cluster.items()
        clustering_string = ["Clustering Coefficient:\n-Compute the clustering coefficient for nodes.\n-The clustering coefficient measures the average probability that two neighbors of a node are\n"
                              +"themselves neighbors. In effect it measures the density of triangles in the network.\n"+"-node name  Clustering Coefficient\n"]
        file.write(clustering_string[0])
        for i in cluster_list:
            file.write(str(i)+'\n')
        file.write("\n\n")
        
        average_cluster = nx.average_clustering(graphs)
        average_cluster_string = ["Average Clustering Coefficient:\n"
                                  +"-Compute the average clustering coefficient for the\n"
                                  +"-Average Clustering Coefficient:"+" " + str(average_cluster)+"\n\n"]
        file.write(average_cluster_string[0])
        
        transitivity = nx.transitivity(graphs)
        transitivity_string = ["Transitivity:\n"
                               +"-Compute graph transitivity, the fraction of all possible triangles present in the network.\n"
                               +"-Transitivity:"+" "+ str(transitivity)]
        file.write(transitivity_string[0])
        file.write("\n\n")
        
        triangles = nx.triangles(graphs)
        triangles_string = ["Triangles:\n"
                            +"-Compute the number of triangles.\n"
                            +"-Triangles:\n"]
        file.write(triangles_string[0])
        for i in triangles:
            file.write(str(i)+':'+str(triangles[i])+'\n')
        file.write("\n\n")
        
        file.close() # this must add or only display a empty txt
        import os
        os.system("notepad.exe clustering.txt")
    
    def centrality(self):
        import config
        graphs = config.graph
        file = open('centrality.txt','w')
        
        degree_centralitys = nx.degree_centrality(graphs)
        closeness_centralitys = nx.closeness_centrality(graphs)
        betweenness_centralitys = nx.betweenness_centrality(graphs)
        degree_centralitys_string = ["Description:\n\n"
                                     +"-Compute the centrality measures for nodes.\n"
                                     +"-Degree centrality for a node v is the fraction of nodes it is connected to.\n"
                                     +"-Closeness centrality of a node i is the reciprocal of the sum of the shortest path distances from node i to all (n-i) other nodes.\n"
                                     +"-Between centrality betweenness centrality is a measure of centrality in a graph based on shortest paths. \n"
                                     +"-node name(nn):degree centrality(dc),closeness centrality(cc),betweenness centrality(bc):\n"
                                     +"-nn:dc,cc,bc\n\n"]
        file.write(degree_centralitys_string[0])
        for i in degree_centralitys:
            file.write(str(i)+' : '
                       +str(degree_centralitys[i])+' , '
                       +str(closeness_centralitys[i])+' , '
                       +str(betweenness_centralitys[i])
                       +'\n')
        file.write("\n\n")
        
        file.close() # this must add or only display a empty txt
        import os
        os.system("notepad.exe centrality.txt")

    def center_on_node(self):
        node = NodeDialog(self, "Name of node to center on:").result
        if node is None: return
        self.canvas.center_on_node(node)

    def reset_edge_markings(self):
        for u,v,k,d in self.canvas.dispG.edges_iter(data=True, keys=True):
            token = d['token']
            if token.is_marked:
                self.canvas.mark_edge(u,v,k)

    def reset_node_markings(self):
        for u,d in self.canvas.dispG.nodes_iter(data=True):
            token = d['token']
            if token.is_marked:
                self.canvas.mark_node(u)

    def add_node(self, event=None):
        node = self.node_entry.get()

        if node.isdigit() and self.canvas.dataG.has_node(int(node)):
                node = int(node)

        if self.canvas.dataG.has_node(node):
            self.node_list.insert(tk.END, node)
            self.node_entry.delete(0, tk.END)
        else:
            tkm.showerror("Node not found", "Node '%s' not in graph."%node)

    def add_filter(self, event=None, filter_lambda=None):
        if filter_lambda is None:
            filter_lambda = self.filter_entry.get()

        if self.canvas.add_filter(filter_lambda):
            # We successfully added the filter; add to list and clear entry
            self.filter_list.insert(tk.END, filter_lambda)
            self.filter_entry.delete(0, tk.END)

    def filter_help(self, event=None):
        msg = ("Enter a lambda function which returns True if you wish\n"
               "to show nodes with ONLY a given property.\n"
               "Parameters are:\n"
               "  - u, the node's name, and \n"
               "  - d, the data dictionary.\n\n"
               "Example: \n"
               " d.get('color',None)=='red'\n"
               "would show only red nodes.\n"
               "Example 2:\n"
               " str(u).is_digit()\n"
               "would show only nodes which have a numerical name.\n\n"
               "Multiple filters are ANDed together.")
        tkm.showinfo("Filter Condition", msg)
    def remove_filter(self, event=None):
        all_items = self.filter_list.get(0, tk.END)
        if event is None:
            # When no event passed, this function was called via the "clear"
            # button.
            items = all_items
        else:
            # Remove currently selected item
            items = (self.filter_list.get(tk.ANCHOR),)

        for item in items:
            self.canvas.remove_filter(item)
            idx = all_items.index(item)
            self.filter_list.delete(idx)


    def grow_all(self):
        """Grow all visible nodes one level"""
        for u, d in self.canvas.dispG.node.copy().items():
            if not d['token'].is_complete:
                self.canvas.grow_node(u)

    def get_node_list(self):
        """Get nodes in the node list and clear"""
        # See if we forgot to hit the plus sign
        if len(self.node_entry.get()) != 0:
            self.add_node()
        nodes = self.node_list.get(0, tk.END)
        self.node_list.delete(0, tk.END)
        return nodes


    def onBuildNew(self):
        nodes = self.get_node_list()
        self.canvas.clear()

        if len(nodes) == 2:
            self.canvas.plot_path(nodes[0], nodes[1], levels=self.level)
        else:
            self.canvas.plot(nodes, levels=self.level)

    def onAddToExisting(self):
        """Add nodes to existing plot.  Prompt to include link to existing
        if possible"""
        home_nodes = set(self.get_node_list())
        self.canvas.plot_additional(home_nodes, levels=self.level)






    def goto_path(self, event):
        frm = self.node_entry.get()
        to = self.node_entry2.get()
        self.node_entry.delete(0, tk.END)
        self.node_entry2.delete(0, tk.END)

        if frm == '':
            tkm.showerror("No From Node", "Please enter a node in both "
                "boxes to plot a path.  Enter a node in only the first box "
                "to bring up nodes immediately adjacent.")
            return

        if frm.isdigit() and int(frm) in self.canvas.dataG.nodes():
            frm = int(frm)
        if to.isdigit() and int(to) in self.canvas.dataG.nodes():
            to = int(to)

        self.canvas.plot_path(frm, to, levels=self.level)

    def onNodeSelected(self, node_name, node_dict):
        self.tbl_attr.build(node_dict)
        self.lbl_attr.config(text="Attributes of node '%s'"%node_name)

    def onEdgeSelected(self, edge_name, edge_dict):
        self.tbl_attr.build(edge_dict)
        self.lbl_attr.config(text="Attributes of edge between '%s' and '%s'"%
                                    edge_name[:2])

    @property
    def level(self):
        try:
            l = int(self.level_entry.get())
        except ValueError:
            tkm.showerror("Invalid Level", "Please specify a level between "
                "greater than or equal to 0")
            raise
        return l

class TkPassthroughViewerApp(ViewerApp):
    def __init__(self, graph, **kwargs):
        ViewerApp.__init__(self, graph,
            NodeTokenClass=TkPassthroughNodeToken,
            EdgeTokenClass=TkPassthroughEdgeToken, **kwargs)


class PropertyTable(tk.Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling

    """
    def __init__(self, parent, property_dict, *args, **kw):
        tk.Frame.__init__(self, parent, *args, **kw)

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = vscrollbar = tk.Scrollbar(self, orient=tk.VERTICAL)
        vscrollbar.pack(fill=tk.Y, side=tk.RIGHT, expand=tk.FALSE)
        self.canvas = canvas = tk.Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = tk.Frame(canvas)
        self.interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor='nw')

        self.interior.bind('<Configure>', self._configure_interior)
        self.canvas.bind('<Configure>', self._configure_canvas)

        self.build(property_dict)

    def build(self, property_dict):
        for c in self.interior.winfo_children():
            c.destroy()

        def _make_pretty(value):
            ans = str(value)
            if len(ans) > 255:
                ans = ans[:253] + '...'
            return ans
        property_dict = {_make_pretty(k): _make_pretty(v)
                            for k, v in property_dict.items()}

        # Sort by key
        dict_values = sorted(property_dict.items(), key=lambda x: x[0])

        for n,(k,v) in enumerate(dict_values):
            tk.Label(self.interior, text=k, borderwidth=1, relief=tk.SOLID,
                wraplength=75, anchor=tk.E, justify=tk.RIGHT).grid(
                row=n, column=0, sticky='nesw', padx=1, pady=1, ipadx=1)
            tk.Label(self.interior, text=v, borderwidth=1,
                wraplength=125, anchor=tk.W, justify=tk.LEFT).grid(
                row=n, column=1, sticky='nesw', padx=1, pady=1, ipadx=1)


    def _configure_interior(self, event):
        """
        track changes to the canvas and frame width and sync them,
        also updating the scrollbar
        """
        # update the scrollbars to match the size of the inner frame
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the canvas's width to fit the inner frame
            self.canvas.config(width=self.interior.winfo_reqwidth())


    def _configure_canvas(self, event):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            # update the inner frame's width to fill the canvas
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())


class NodeDialog(tk.Toplevel):
    def __init__(self, main_window, msg='Please enter a node:'):
        tk.Toplevel.__init__(self)
        self.main_window = main_window
        self.title('Node Entry')
        self.geometry('170x160')
        self.rowconfigure(3, weight=1)

        tk.Label(self, text=msg).grid(row=0, column=0, columnspan=2,
                                      sticky='NESW',padx=5,pady=5)
        self.posibilities = [d['dataG_id'] for n,d in
                    main_window.canvas.dispG.nodes_iter(data=True)]
        self.entry = AutocompleteEntry(self.posibilities, self)
        self.entry.bind('<Return>', lambda e: self.destroy(), add='+')
        self.entry.grid(row=1, column=0, columnspan=2, sticky='NESW',padx=5,pady=5)

        tk.Button(self, text='Ok', command=self.destroy).grid(
            row=3, column=0, sticky='ESW',padx=5,pady=5)
        tk.Button(self, text='Cancel', command=self.cancel).grid(
            row=3, column=1, sticky='ESW',padx=5,pady=5)

        # Make modal
        self.winfo_toplevel().wait_window(self)


    def destroy(self):
        res = self.entry.get()
        if res not in self.posibilities:
            res = None
        self.result = res
        tk.Toplevel.destroy(self)

    def cancel(self):
        self.entry.delete(0,tk.END)
        self.destroy()
