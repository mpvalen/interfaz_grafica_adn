import matplotlib
import numpy as np
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (QFileDialog, QWidget, QFormLayout, QLabel, QPushButton, QFrame, QComboBox,
                            QLineEdit, QSpinBox)


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
        self.axes.clear()
        self.axes.set_xlabel('Depth [mm]')
        self.axes.set_ylabel('Dose [Gy]')
        for v in info_plots:
            doses = v['doses']
            doseserr = v['doseserr']
            depth = v['depth']
            set_experimental = v['set_experimental']
            num_puntos = v['num_puntos']
            self.axes.plot(depth, doses, color='black', markevery= num_puntos)
            self.axes.errorbar(depth, doses, doseserr, color='black', errorevery= num_puntos)
            if set_experimental != '':
                set_depth = set_experimental['set_x']
                set_doses = set_experimental['set_y']
                label_set = set_experimental['label_set_experimental']
                self.axes.scatter(set_depth, set_doses, color='green', label= label_set)
                self.axes.legend()

    
    def survival_vs_dose(self, info_plots):
        # info_plots es una lista con al menos 1 diccionario con información para graficar
        self.axes.clear()
        self.axes.set_xlabel('Dose [Gy]')
        self.axes.set_ylabel('Survival fraction')
        for v in info_plots:
            doses = v['doses']
            surv = v['survival']
            set_experimental = v['set_experimental']
            num_puntos = v['num_puntos']
            # Función para graficar supervivencia vs dosis
            doses_sorted_id = np.argsort(doses)
            survival = surv[doses_sorted_id]
            #survivalerr = surverr[doses_sorted_id]
            doses.sort()
            self.axes.plot(doses, survival, color='black')
            #self.axes.errorbar(doses, survival, survivalerr, color='black', errorevery= num_puntos)
            if set_experimental != '':
                set_doses = set_experimental['set_x']
                set_survival = set_experimental['set_y']
                label_set = set_experimental['label_set_experimental']
                self.axes.scatter(set_doses, set_survival, color='green', label= label_set)
                self.axes.legend()

    
    def survival_vs_depth(self, info_plots):
        # Función para graficar supervivencia vs profundidad
        self.axes.clear()
        self.axes.set_xlabel('Depth [mm]')
        self.axes.set_ylabel('Survival fraction')
        for v in info_plots:
            survival = v['survival']
            depth = v['depth']
            survivalerr = v['survivalerr']
            set_experimental = v['set_experimental']
            num_puntos = v['num_puntos']
            dose = v['dosis']
            self.axes.plot(depth, survival, color='black', markevery= num_puntos)
            self.axes.errorbar(depth, survival, survivalerr, color='black', errorevery= num_puntos)
            if set_experimental != '':
                set_depth = set_experimental['set_x']
                set_survival = set_experimental['set_y']
                label_set = set_experimental['label_set_experimental']
                self.axes.scatter(set_depth, set_survival, color='green', label= label_set)
                self.axes.legend()
        self.axes.set_title(f'{dose} Gy')

    def yield_vs_depth(self, info_plots):
        # Función para graficar yield (número de DSBs) vs profundidad
        self.axes.clear()
        self.axes.set_xlabel('Depth [mm]')
        self.axes.set_ylabel('DSB Yield')
        for v in info_plots:
            depth = v['depth']
            dsbyields = v['dsbyields']
            dsbyieldserr = v['dsbyieldserr']
            set_experimental = v['set_experimental']
            num_puntos = v['num_puntos']
            self.axes.plot(depth, dsbyields, color='black', markevery= num_puntos)
            self.axes.errorbar(depth, dsbyields, dsbyieldserr, color='black', errorevery= num_puntos)
            if set_experimental != '':
                set_depth = set_experimental['set_x']
                set_dsbyields = set_experimental['set_y']
                label_set = set_experimental['label_set_experimental']
                self.axes.scatter(set_depth, set_dsbyields, color='green', label= label_set)
                self.axes.legend()

    def lambda_vs_depth(self, info_plots):
        # Función para graficar lambda vs profundidad
        self.axes.clear()
        self.axes.set_xlabel('Depth [mm]')
        self.axes.set_ylabel('Lambda')
        for v in info_plots:
            lmbda = v['lambda']
            lmbdaerr = v['lambdaerr']
            depth = v['depth']
            set_experimental = v['set_experimental']
            num_puntos = v['num_puntos']
            self.axes.plot(depth, lmbda, color='black', markevery= num_puntos)
            self.axes.errorbar(depth, lmbda, lmbdaerr, color='black', errorevery= num_puntos)
            if set_experimental != '':
                set_depth = set_experimental['set_x']
                set_lmbda = set_experimental['set_y']
                label_set = set_experimental['label_set_experimental']
                self.axes.scatter(set_depth, set_lmbda, color='green', label= label_set)
                self.axes.legend()
    

class Plot(QFrame):

    def __init__(self, id):
        super().__init__()
        self.id = id # Número identificador del plot
        self.new_plot = QFormLayout()

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