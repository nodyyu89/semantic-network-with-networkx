# -*- coding: utf-8 -*-
"""
Created on Sun Apr 22 16:23:07 2018

@author: Nody
"""


from PyQt5 import QtCore, QtGui, QtWidgets
import spacy
#import neuralcoref
#from neuralcoref import Coref
import networkx as nx
from networkx_viewer import Viewer
import sys
sys.setrecursionlimit(50000)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1329, 805)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
# =============================================================================
#         self.pushButton = QtWidgets.QPushButton(self.centralwidget)
#         self.pushButton.setGeometry(QtCore.QRect(50, 310, 101, 31))
#         self.pushButton.setObjectName("pushButton")
#         self.pushButton.clicked.connect(self.neuralcoref_push)
# =============================================================================
        
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(1050, 687, 250, 41))
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.clicked.connect(self.network)
        
        self.pushButton_3 = QtWidgets.QPushButton(self.centralwidget)
        #self.pushButton_3.setGeometry(QtCore.QRect(50, 600, 250, 31))
        self.pushButton_3.setGeometry(QtCore.QRect(50, 320, 250, 31))
        self.pushButton_3.setObjectName("pushButton_3")
        self.pushButton_3.clicked.connect(self.output_table)
        
        
        self.textEdit = QtWidgets.QTextEdit(self.centralwidget)
        self.textEdit.setGeometry(QtCore.QRect(40, 10, 861, 291))
        self.textEdit.setObjectName("textEdit")
        
# =============================================================================
#         self.textEdit_2 = QtWidgets.QTextEdit(self.centralwidget)
#         self.textEdit_2.setGeometry(QtCore.QRect(40, 350, 861, 291))
#         self.textEdit_2.setObjectName("textEdit_2")
# =============================================================================
        
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(920, 10, 391, 631))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(1)
        self.tableWidget.setHorizontalHeaderLabels(['In Concept','Relation','Out Concept'])
               
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1329, 26))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionInput_text = QtWidgets.QAction(MainWindow)
        self.actionInput_text.setObjectName("actionInput_text")
        self.menuFile.addAction(self.actionInput_text)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
    
    def display_closeness(self):
        if self.radiobutton1.isChecked():
            Ui_MainWindow.radiobutton1_signal = 1
            print(Ui_MainWindow.radiobutton1_signal)
        else:
            Ui_MainWindow.radiobutton1_signal = 0
            print('radiobut1 signal:0')
        
    def closeness_change(self):
        Ui_MainWindow.combobox_signal = self.combobox.currentText()
        print(Ui_MainWindow.combobox_signal)
    
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        #self.pushButton.setText(_translate("MainWindow", "Coreference"))
        self.pushButton_2.setText(_translate("MainWindow", "Construct Network Graph"))
        self.pushButton_3.setText(_translate("MainWindow", "Concept-Relation Seperation"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuHelp.setTitle(_translate("MainWindow", "Help"))
        self.actionInput_text.setText(_translate("MainWindow", "Input text"))
    
# =============================================================================
#     def neuralcoref_push(self):
#         raw = self.textEdit.toPlainText()
#         print(raw)
#         coref = Coref()
#         clusters = coref.continuous_coref(raw)
#         resolved_utterance_text = coref.get_resolved_utterances()
#         resolved_utterance_text2 = str(resolved_utterance_text)
#         resolved_utterance_text2 = resolved_utterance_text2.replace('\r', '')
#         resolved_utterance_text2 = resolved_utterance_text2.replace('\n', '')
#         resolved_utterance_text2 = resolved_utterance_text2.replace("['", '')
#         resolved_utterance_text2 = resolved_utterance_text2.replace("']", '')
#         self.textEdit_2.setText(str(resolved_utterance_text2))    
# =============================================================================
    
    def network(self):
        row_no = self.tableWidget.rowCount()
        column_no = self.tableWidget.columnCount()
        row_no_list = list(range(0,row_no))
        column_no_list = list(range(0,column_no))
        in_concpets = []
        out_concepts = []
        relations = []
        for i in row_no_list:
            in_concpets.append(str(self.tableWidget.item(i,0).text()))
        for j in row_no_list:
            out_concepts.append(str(self.tableWidget.item(j,2).text()))
        for k in row_no_list:
            relations.append(str(self.tableWidget.item(k,1).text()))
        print(in_concpets)
        G = nx.Graph()
        for i in list(zip(in_concpets,relations, out_concepts)):
            G.add_edge(i[0],i[1])
            G.add_edge(i[1],i[2])
            G.node[i[1]]['color'] = 'green'
            G.node[i[1]]['fill'] = 'green'
        G.remove_nodes_from(['.'])
        import config
        config.graph = G
        graph = G
        Ui_MainWindow.graph = G
        app = Viewer(G)
        app.mainloop()
    
    def output_table(self):
        nlp = spacy.load('en_core_web_md')
        #resolved_utterance_text = self.textEdit_2.toPlainText()
        resolved_utterance_text = self.textEdit.toPlainText()
        doc = nlp(resolved_utterance_text)
        result_text=[]
        result_lemma=[]
        result_pos=[]
        result_tag=[]
        result_dep=[]
        result_shape=[]
        result_alpha=[]
        result_is_stop=[]
        result_root_dlp=[]
        result_child=[]
                    
        for np in doc.noun_chunks:
            np.merge(np.root.tag_, np.text, np.root.ent_type_) 
        for tok in doc:
            result_text.append(tok.text)
            result_lemma.append(tok.lemma)
            result_pos.append(tok.pos_)
            result_tag.append(tok.tag_)
            result_dep.append(tok.dep_)
            result_shape.append(tok.shape_)
            result_alpha.append(tok.is_alpha)
            result_is_stop.append(tok.is_stop)
            result_child.append([child for child in tok.children])
        
        result_list=list(zip(result_text,result_lemma,result_pos,result_tag,result_dep,result_shape,result_alpha,result_is_stop,result_child))
        noun_index=[]
        not_noun_index=[]
        for position, item in enumerate(result_pos):
            if (item != "NOUN")*(item != "PRON")*(item != "PROPN"):
               not_noun_index.append(position)
            if (item == "NOUN" or item == "PRON" or item == "PROPN"):
               noun_index.append(position)
        
        def split_list(n):#"""will return the list index"""
            return [(x+1) for x,y in zip(n, n[1:]) if y-x != 1]
        
        def get_sub_list(my_list):
    #"""will split the list base on the index"""
            my_index = split_list(my_list)
            output = list()
            prev = 0
            for index in my_index:
                new_list = [ x for x in my_list[prev:] if x < index]
                output.append(new_list)
                prev += len(new_list)
            output.append([ x for x in my_list[prev:]])
            return output
        
        not_noun_index_continous=get_sub_list(not_noun_index)
        noun_index_continous=get_sub_list(noun_index)
        noun_continous_index_start=[]
        not_noun_continous_index_start=[]
        for item in not_noun_index_continous:
            if len(item) > 1 :
               not_noun_continous_index_start.append(item)
        for item in noun_index_continous:
            if len(item) > 1 :
               noun_continous_index_start.append(item)
        not_noun_continous_index_start2=[element[0] for element in not_noun_continous_index_start]
        not_noun_continous_index_end=[element[-1] for element in not_noun_continous_index_start]
        noun_continous_index_start2=[element[0] for element in noun_continous_index_start]
        noun_continous_index_end=[element[-1] for element in noun_continous_index_start]
        number=list(range(len(not_noun_continous_index_end)))
        number_noun=list(range(len(noun_continous_index_end)))
        
        for items in number:
            result_text[not_noun_continous_index_start2[items]]=' '.join(result_text[not_noun_continous_index_start2[items]:not_noun_continous_index_end[items]+1])

# I add one at end because it start from 0 but end with missing one value
        for items in number_noun:
            result_text[noun_continous_index_start2[items]]=' '.join(result_text[noun_continous_index_start2[items]:noun_continous_index_end[items]+1])
        
        not_noun_continous_index_start3=[]#take all non first one index for delating process in result_text
        noun_continous_index_start3=[]
        for items in not_noun_continous_index_start:
           not_noun_continous_index_start3.append(items[1:])
        noun_continous_index_start3=[]
        for items in noun_continous_index_start:
           noun_continous_index_start3.append(items[1:])
        
        output2=str(not_noun_continous_index_start3)
        output3=output2.replace("[","")
        output4=output3.replace("]","")
        output5=output4.split(',')
        output6=[]
        output22=str(noun_continous_index_start3)
        output33=output22.replace("[","")
        output44=output33.replace("]","")
        output55=output44.split(',')
        output66=[]
        
        for items in output5:
           output6.append(eval(items))
        for items in output55:
           output66.append(eval(items))
        for terms in output6:
           result_text[terms]=''
        for terms in output66:
           result_text[terms]=''
        
        result_text2 = [x for x in result_text if x != '']
        extract_noun=result_text2[0::2]
        tokens_to_pair=zip(extract_noun, extract_noun[1:])
        tokens_paired=list(tokens_to_pair)
        tokens_paired1 = []
        tokens_paired2 = []
        for i in tokens_paired:
           tokens_paired1.append(i[0])
           tokens_paired2.append(i[1])
        
        tokens_range = list(range(0,len(tokens_paired)))
        extract_noun=result_text2[0::2]
        link=result_text2[1::2]
        link[-1] = []
        link2 = [x for x in link if x != []]
        
        self.tableWidget.setRowCount(len(tokens_paired))
        self.tableWidget.setColumnCount(3)
        tokens_paired1_list_index=[]
        tokens_paired2_list_index=[]
        tokens_paired3_list_index=[]
        for i,j in enumerate(tokens_paired1):
            tokens_paired1_list_index.append([i,j])
        for k,m in enumerate(tokens_paired2):
            tokens_paired2_list_index.append([k,m])
        for i in tokens_paired1_list_index:
            self.tableWidget.setItem(i[0],0,QtWidgets.QTableWidgetItem(str(i[1])))
        for j in tokens_paired2_list_index:
            self.tableWidget.setItem(j[0],2,QtWidgets.QTableWidgetItem(str(j[1])))
        for i,j in enumerate(link2):
            tokens_paired3_list_index.append([i,j])
        for k in tokens_paired3_list_index:
            self.tableWidget.setItem(k[0],1,QtWidgets.QTableWidgetItem(str(k[1])))
#find index start end





if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())