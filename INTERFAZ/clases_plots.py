import matplotlib
import matplotlib.pylab as pylab
import numpy as np
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QFileDialog, QWidget, QFormLayout, QLabel, QPushButton, QFrame, QComboBox,
                            QLineEdit, QSpinBox, QVBoxLayout, QHBoxLayout, QFormLayout)
from PyQt5.QtCore import pyqtSignal


class Canvas(FigureCanvasQTAgg):
    # Clase necesaria para la interfaz de ploteo. Contiene las funciones para graficar las distintas opciones

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.num_plot = 0
        super(Canvas, self).__init__(fig)


    def choose_plot(self, option, info, num_plot):
        # Función que recibe información sobre cuál tipo de plot quiere el user y la información de este
        # (directorios con info, labels, etc)
        
        # Primera parte de la función es para escoger el plot a mostrar de todos los posibles
        # dada una carpeta con archivos, manteniendo el orden de estos
        # avanzar o retroceder de plot depende del largo de la lista info.keys (para no tener errores)
        n_min = 1
        n_max = len(info[0].keys()) - 1
        if (self.num_plot + num_plot) > n_max:
            self.num_plot = n_min
        elif (self.num_plot + num_plot) < n_min:
            self.num_plot = n_max
        else:
            self.num_plot += num_plot

        info_plots = []
        for plot in info:
            dosis_key = list(plot.keys())[self.num_plot - 1]
            v = plot[dosis_key]
            v['dosis'] = dosis_key
            info_plots.append(v)
        if option == 'Survival vs depth':
            self.survival_vs_depth(info_plots)
            self.draw()
        
        elif option == 'Dose vs depth':
            self.dose_vs_depth(info_plots)
            self.draw()
        
        elif option == 'Survival vs dose':
            self.survival_vs_dose(info_plots)
            self.draw()
        
        elif option == 'Yield vs depth':
            self.yield_vs_depth(info_plots)
            self.draw()

        elif option == 'Lambda vs depth':
            self.lambda_vs_depth(info_plots)
            self.draw()
        


    def dose_vs_depth(self, info_plots):
        # Función para graficar dosis vs profundidad
        self.title = self.axes.get_title()
        self.axes.clear()
        for v in info_plots:
            doses = v['doses']
            doseserr = v['doseserr']
            depth = v['depth']
            set_experimental = v['set_experimental']
            num_puntos = v['num_puntos']
            if set_experimental['values']:
                set_depth = set_experimental['set_x']
                set_doses = set_experimental['set_y']
                label_set = set_experimental['label_set_experimental']
                self.axes.scatter(set_depth, set_doses, color='green', label= label_set)
            else:
                label_set = set_experimental['label_set_experimental']
            self.axes.set_xlabel('Depth [mm]', fontsize=set_experimental['axistext_fontsize'])
            self.axes.set_ylabel('Dose [Gy]', fontsize=set_experimental['axistext_fontsize'])
            self.axes.set_title(self.title, fontsize=set_experimental['title_fontsize'])
            self.axes.tick_params(axis='both', labelsize=set_experimental['axisticks_fontsize'])
            self.axes.errorbar(depth, doses, doseserr, errorevery= num_puntos, label=label_set)
            self.axes.legend(fontsize=set_experimental['labels_fontsize'])

    
    def survival_vs_dose(self, info_plots):
        # info_plots es una lista con al menos 1 diccionario con información para graficar
        self.title = self.axes.get_title()
        self.axes.clear()
        for v in info_plots:
            doses = v['doses']
            surv = v['survival']
            #survivalerr = v['surverr']
            set_experimental = v['set_experimental']
            num_puntos = v['num_puntos']
            # Función para graficar supervivencia vs dosis
            doses_sorted_id = np.argsort(doses)
            survival = surv[doses_sorted_id]
            #survivalerr = surverr[doses_sorted_id]
            doses.sort()
            #self.axes.errorbar(doses, survival, survivalerr, color='black', errorevery= num_puntos)
            if set_experimental['values'] == True:
                set_doses = set_experimental['set_x']
                set_survival = set_experimental['set_y']
                label_set = set_experimental['label_set_experimental']
                self.axes.scatter(set_doses, set_survival, label= label_set)
            else:
                label_set = set_experimental['label_set_experimental']

            self.axes.set_xlabel('Dose [Gy]', fontsize=set_experimental['axistext_fontsize'])
            self.axes.set_ylabel('Survival fraction', fontsize=set_experimental['axistext_fontsize'])
            self.axes.set_title(self.title, fontsize=set_experimental['title_fontsize'])
            self.axes.tick_params(axis='both', labelsize=set_experimental['axisticks_fontsize'])
            self.axes.plot(doses, survival, label=label_set)
            #self.axes.errorbar(doses, survivalerr, label=label_set)
            self.axes.legend(fontsize=set_experimental['labels_fontsize'])

    
    def survival_vs_depth(self, info_plots):
        # Función para graficar supervivencia vs profundidad
        self.title = self.axes.get_title()
        self.axes.clear()
        for v in info_plots:
            survival = v['survival']
            depth = v['depth']
            survivalerr = v['survivalerr']
            set_experimental = v['set_experimental']
            num_puntos = v['num_puntos']
            dose = v['dosis']
            if set_experimental['values']:
                set_depth = set_experimental['set_x']
                set_survival = set_experimental['set_y']
                label_set = set_experimental['label_set_experimental']
                self.axes.scatter(set_depth, set_survival, color='green', label= label_set)
            else:
                label_set = set_experimental['label_set_experimental']
            self.axes.set_xlabel('Depth [mm]', fontsize=set_experimental['axistext_fontsize'])
            self.axes.set_ylabel('Survival fraction', fontsize=set_experimental['axistext_fontsize'])
            self.axes.tick_params(axis='both', labelsize=set_experimental['axisticks_fontsize'])
            self.axes.errorbar(depth, survival, survivalerr, errorevery= int(num_puntos), label=label_set)
            self.axes.legend(fontsize=set_experimental['labels_fontsize'])
        self.axes.set_title(f'Dosis {dose} Gy', fontsize=set_experimental['title_fontsize'])

    def yield_vs_depth(self, info_plots):
        # Función para graficar yield (número de DSBs) vs profundidad
        self.title = self.axes.get_title()
        self.axes.clear()
        for v in info_plots:
            depth = v['depth']
            dsbyields = v['dsbyields']
            dsbyieldserr = v['dsbyieldserr']
            set_experimental = v['set_experimental']
            num_puntos = v['num_puntos']
            if set_experimental['values']:
                set_depth = set_experimental['set_x']
                set_dsbyields = set_experimental['set_y']
                label_set = set_experimental['label_set_experimental']
                self.axes.scatter(set_depth, set_dsbyields, color='green', label= label_set)
            else:
                label_set = set_experimental['label_set_experimental']

            self.axes.set_xlabel('Depth [mm]', fontsize=set_experimental['axistext_fontsize'])
            self.axes.set_ylabel('DSB Yield', fontsize=set_experimental['axistext_fontsize'])
            self.axes.tick_params(axis='both', labelsize=set_experimental['axisticks_fontsize'])
            self.axes.set_title(self.title, fontsize=set_experimental['title_fontsize'])
            self.axes.errorbar(depth, dsbyields, dsbyieldserr, errorevery= num_puntos)
            self.axes.legend(fontsize=set_experimental['labels_fontsize'])

    def lambda_vs_depth(self, info_plots):
        # Función para graficar lambda vs profundidad
        self.title = self.axes.get_title()
        self.axes.clear()
        for v in info_plots:
            lmbda = v['lambda']
            lmbdaerr = v['lambdaerr']
            depth = v['depth']
            set_experimental = v['set_experimental']
            num_puntos = v['num_puntos']
            if set_experimental['values']:
                set_depth = set_experimental['set_x']
                set_lmbda = set_experimental['set_y']
                label_set = set_experimental['label_set_experimental']
                self.axes.scatter(set_depth, set_lmbda, color='green', label= label_set)
            else:
                label_set = set_experimental['label_set_experimental']
            self.axes.set_xlabel('Depth [mm]', fontsize=set_experimental['axistext_fontsize'])
            self.axes.set_ylabel('Lambda', fontsize=set_experimental['axistext_fontsize'])
            self.axes.tick_params(axis='both', labelsize=set_experimental['axisticks_fontsize'])
            self.axes.set_title(self.title, fontsize=set_experimental['title_fontsize'])
            self.axes.errorbar(depth, lmbda, lmbdaerr, errorevery= num_puntos, label=label_set)
            self.axes.legend(fontsize=set_experimental['labels_fontsize'])
    

class Plot(QFrame):

    def __init__(self, id):
        super().__init__()
        self.id = id # Número identificador del plot
        self.new_plot = QFormLayout()
        self.set_experimental = ''

        carpeta = QLabel('Carpeta')
        carpeta.setToolTip('La carpeta que contiene los archivos output')
        self.carpeta_plot = QPushButton('Elegir carpeta', self)
        self.carpeta_plot.clicked.connect(self.open_carpeta_plots)

        set_experimental = QLabel('Set experimental')
        set_experimental.setToolTip('Archivo con datos experimentales, se genera un scatter de puntos')
        self.set_experimental_button = QPushButton(f'Elegir archivo', self)
        self.set_experimental_button.clicked.connect(self.open_set_experimental)

        label_name = QLabel('Label del set')
        self.label = QLineEdit()

        label_puntos = QLabel('Separación de puntos')
        self.num_puntos_plot = QSpinBox()
        self.num_puntos_plot.setValue(10)
        self.num_puntos_plot.setMinimum(1)

        self.new_plot.addRow(carpeta, self.carpeta_plot)
        self.new_plot.addRow(set_experimental, self.set_experimental_button)
        self.new_plot.addRow(label_name, self.label)
        self.new_plot.addRow(label_puntos, self.num_puntos_plot)

        self.setLayout(self.new_plot)

    def open_carpeta_plots(self):
        self.path_carpeta_plots = QFileDialog.getExistingDirectory(self, "Elegir carpeta")

    def open_set_experimental(self):
        self.set_experimental = QFileDialog.getOpenFileName(None, 'Abrir archivo', '', '')

class HorizontalLine(QFrame):

    def __init__(self):
        super().__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)


class VentanaFontSize(QWidget):

    senal_fontsize_plot = pyqtSignal(dict)    

    def __init__(self, parent=None):
        self.parent = parent
        super().__init__()
        self.setWindowTitle('Cambiar tamaño de letra')
        prect1 = self.parent.geometry()
        center = prect1.center()
        self.move(center)
        self.data = dict()

        layout_principal = QVBoxLayout()
        layout_botones = QHBoxLayout()
        layout_texto = QFormLayout()

        self.data['title_fontsize'] = QSpinBox()
        self.data['title_fontsize'].setValue(10)
        
        self.data['labels_fontsize'] = QSpinBox()
        self.data['labels_fontsize'].setValue(10)

        self.data['axisticks_fontsize'] = QSpinBox()
        self.data['axisticks_fontsize'].setValue(10)

        self.data['axistext_fontsize'] = QSpinBox()
        self.data['axistext_fontsize'].setValue(10)

        layout_texto.addRow(QLabel('Título'), self.data['title_fontsize'])
        layout_texto.addRow(QLabel('Labels'), self.data['labels_fontsize'])
        layout_texto.addRow(QLabel('Ejes (Números)'), self.data['axisticks_fontsize'])
        layout_texto.addRow(QLabel('Ejes (texto)'), self.data['axistext_fontsize'])
        layout_principal.addLayout(layout_texto)

        self.boton_ok = QPushButton('Ok')
        self.boton_ok.clicked.connect(self.opcion_ok)
        self.boton_cancelar = QPushButton('Cancelar')
        self.boton_cancelar.clicked.connect(self.cerrar_ventana)

        layout_botones.addWidget(self.boton_ok)
        layout_botones.addWidget(self.boton_cancelar)
        layout_principal.addLayout(layout_botones)

        self.setLayout(layout_principal)

    def cerrar_ventana(self):
        self.hide()
    
    def opcion_ok(self):
        self.senal_fontsize_plot.emit(self.data)
        self.hide()