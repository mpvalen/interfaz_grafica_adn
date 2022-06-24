from re import A
import sys
import os
import matplotlib
import numpy as np
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure
from PyQt5 import uic
from PyQt5.QtWidgets import (QApplication, QFileDialog, QTabWidget, QWidget, QFormLayout, QLineEdit,
                             QComboBox, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QDialog, QShortcut,
                             QSpinBox)
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QKeySequence


class Canvas(FigureCanvasQTAgg):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.num_plot = 0
        super(Canvas, self).__init__(fig)


    def choose_plot(self, option, info, num_plot):
        # avanzar o retroceder de plot depende del largo de la lista info.keys (para no tener errores)
        n_min = 1
        n_max = len(info.keys()) - 1
        if (self.num_plot + num_plot) > n_max:
            self.num_plot = n_min
        elif (self.num_plot + num_plot) < n_min:
            self.num_plot = n_max
        else:
            self.num_plot += num_plot

        dosis_key = list(info.keys())[self.num_plot]
        v = info[dosis_key]
        v['dosis'] = dosis_key
        if option == 'Survival vs depth':
            self.survival_vs_depth(v['survival'], v['depth'], v['survivalerr'], v['set_experimental'],
                                   v['num_puntos'])
            self.draw()
        
        elif option == 'Dose vs depth':
            self.dose_vs_depth(v['doses'], v['doseserr'], v['depth'], v['set_experimental'],
                               v['num_puntos'])
            self.draw()
        
        elif option == 'Survival vs dose':
            self.survival_vs_dose(v['doses'], v['survival'], v['survivalerr'], v['set_experimental'],
                                  v['num_puntos'])
            self.draw()
        
        elif option == 'Yield vs depth':
            self.yield_vs_depth(v['depth'], v['dsbyields'], v['dsbyieldserr'], v['set_experimental'],
                                v['num_puntos'])
            self.draw()

        elif option == 'Lambda vs depth':
            self.lambda_vs_depth(v['lambda'], v['lambdaerr'], v['depth'], v['set_experimental'],
                                 v['num_puntos'])
            self.draw()
        
        elif option == 'Test plot':
            self.test_plot_survival(v['depth'], v['survival'], v['survivalerr'], v['set_experimental'],
                                    v['num_puntos'], v['dosis'])
            self.draw()
        
        elif option == 'Test plot 2':
            self.test_plot_survival_dose(v['doses'], v['survival'], v['set_experimental'],
                                    v['num_puntos'])
            self.draw()


    def dose_vs_depth(self, doses, doseserr, depth, set_experimental, num_puntos):
        self.axes.clear()
        self.axes.plot(depth, doses, color='black', markevery= num_puntos)
        self.axes.errorbar(depth, doses, doseserr, color='black', errorevery= num_puntos)
        self.axes.set_xlabel('Depth [mm]')
        self.axes.set_ylabel('Dose [Gy]')
        if set_experimental != '':
            set_depth = set_experimental['set_x']
            set_doses = set_experimental['set_y']
            label_set = set_experimental['label_set_experimental']
            self.axes.scatter(set_depth, set_doses, color='green', label= label_set)
            self.axes.legend()

    
    def survival_vs_dose(self, doses, surv, surverr, set_experimental, num_puntos):
        doses_sorted_id = np.argsort(doses)
        survival = surv[doses_sorted_id]
        survivalerr = surverr[doses_sorted_id]
        doses.sort()
        self.axes.clear()
        self.axes.plot(doses, survival, color='black')
        self.axes.errorbar(doses, survival, survivalerr, color='black', errorevery= num_puntos)
        self.axes.set_xlabel('Dose [Gy]')
        self.axes.set_ylabel('Survival fraction')
        if set_experimental != '':
            set_doses = set_experimental['set_x']
            set_survival = set_experimental['set_y']
            label_set = set_experimental['label_set_experimental']
            self.axes.scatter(set_doses, set_survival, color='green', label= label_set)
            self.axes.legend()

    
    def survival_vs_depth(self, survival, depth, survivalerr, set_experimental, num_puntos):
        self.axes.clear()
        self.axes.plot(depth, survival, color='black', markevery= num_puntos)
        self.axes.errorbar(depth, survival, survivalerr, color='black', errorevery= num_puntos)
        self.axes.set_xlabel('Depth [mm]')
        self.axes.set_ylabel('Survival fraction')
        if set_experimental != '':
            set_depth = set_experimental['set_x']
            set_survival = set_experimental['set_y']
            label_set = set_experimental['label_set_experimental']
            self.axes.scatter(set_depth, set_survival, color='green', label= label_set)
            self.axes.legend()

    def yield_vs_depth(self, depth, dsbyields, dsbyieldserr, set_experimental, num_puntos):
        self.axes.clear()
        self.axes.plot(depth, dsbyields, color='black', markevery= num_puntos)
        self.axes.errorbar(depth, dsbyields, dsbyieldserr, color='black', errorevery= num_puntos)
        self.axes.set_xlabel('Depth [mm]')
        self.axes.set_ylabel('DSB Yield')
        if set_experimental != '':
            set_depth = set_experimental['set_x']
            set_dsbyields = set_experimental['set_y']
            label_set = set_experimental['label_set_experimental']
            self.axes.scatter(set_depth, set_dsbyields, color='green', label= label_set)
            self.axes.legend()


    def lambda_vs_depth(self, lmbda, lmbdaerr, depth, set_experimental, num_puntos):
        self.axes.clear()
        self.axes.plot(depth, lmbda, color='black', markevery= num_puntos)
        self.axes.errorbar(depth, lmbda, lmbdaerr, color='black', errorevery= num_puntos)
        self.axes.set_xlabel('Depth [mm]')
        self.axes.set_ylabel('Lambda')
        if set_experimental != '':
            set_depth = set_experimental['set_x']
            set_lmbda = set_experimental['set_y']
            label_set = set_experimental['label_set_experimental']
            self.axes.scatter(set_depth, set_lmbda, color='green', label= label_set)
            self.axes.legend()
    
    def test_plot_survival(self, depth, SF_sim, SFerr_sim, comp_file, num_puntos, dosis, wouters2014_mode=0, wouters2014E=230, 
                           yscale='log', depth_elongation_factor=1.0, plot=1):
        
        self.axes.clear()
        depths_sim = [i * depth_elongation_factor for i in depth]
        depths_exp = comp_file['set_x']
        SF_exp = comp_file['set_y']
        label_set = comp_file['label_set_experimental']

        if wouters2014_mode == 1:
            avg_SF_sim = []
            avg_SFerr_sim = []
            for index_exp, de in enumerate(depths_exp):
                avg_SF_list = []
                avg_SFerr_list = []
                for index_sim, ds in enumerate(depths_sim):
                    if wouters2014E == 230:
                        if index_exp == 14:
                            if de - 1 < ds and de + 1 > ds:
                                avg_SF_list.append(SF_sim[index_sim])
                                avg_SFerr_list.append(SFerr_sim[index_sim])
                        else:
                            if de - 2 < ds and de + 2 > ds:
                                avg_SF_list.append(SF_sim[index_sim])
                                avg_SFerr_list.append(SFerr_sim[index_sim])
                    elif wouters2014E == 160:
                        if index_exp == 10:
                            if de - 1 < ds and de + 1 > ds:
                                avg_SF_list.append(SF_sim[index_sim])
                                avg_SFerr_list.append(SFerr_sim[index_sim])
                        else:
                            if de - 2 < ds and de + 2 > ds:
                                avg_SF_list.append(SF_sim[index_sim])
                                avg_SFerr_list.append(SFerr_sim[index_sim])
                avg_SF_sim.append(np.mean(avg_SF_list))
                avg_SFerr_sim.append(np.mean(avg_SFerr_list))
            if plot == 1:
                self.axes.errorbar(depths_exp, avg_SF_sim, avg_SFerr_sim, label='Sim', linewidth=0.5, capsize=3,
                                   color='black', errorevery= num_puntos)
        else:
            if plot == 1:
                self.axes.errorbar(depths_sim, SF_sim, SFerr_sim, label='Sim', linewidth=0.5, capsize=3, 
                                   color='black', errorevery= num_puntos)
        if plot == 1:
            self.axes.scatter(depths_exp, SF_exp, marker='D', facecolor='none', label=label_set, color='green')
            self.axes.set_xlabel('Depth[mm]')
            self.axes.set_ylabel('Survival Fraction')
            self.axes.set_yscale(yscale)
            self.axes.legend()
            self.axes.set_title(f'{dosis} Gy')
            #self.axes.tight_layout()
            #self.axes.set_ylim([0, 1.05])
        if wouters2014_mode == 1:
            return depths_exp, avg_SF_sim, avg_SFerr_sim, SF_exp
        else:
            return depths_sim, SF_sim, SFerr_sim, SF_exp

    def test_plot_survival_dose(self, dose, surv, set_experimental, num_puntos):
        self.axes.clear()
        self.axes.plot(dose, surv, color='black', markevery=num_puntos)
        #self.axes.errorbar(dose, surv, surverr, color='black', errorevery = num_puntos)
        self.axes.set_xlabel('Dose (Gy)')
        self.axes.set_ylabel('Survival fraction')
        self.axes.set_yscale('log')
        if set_experimental != '':
            set_dose = set_experimental['set_x']
            set_survival = set_experimental['set_y']
            label_set = set_experimental['label_set_experimental']
            self.axes.scatter(set_dose, set_survival, color='green', label=label_set)
            self.axes.legend()
    


window_name, base_class = uic.loadUiType('ventana_principal.ui')

class VentanaPrincipal(window_name, base_class):

    senal_generar_input = pyqtSignal(dict)
    senal_lanzar_simulacion = pyqtSignal(str)
    senal_fluka_yield = pyqtSignal(dict)
    senal_fluka_survival = pyqtSignal(dict)
    senal_yield_survival = pyqtSignal(dict)
    senal_info_plots = pyqtSignal(dict)
    senal_avanzar_plot = pyqtSignal(float)
    senal_generar_db = pyqtSignal(dict)
    senal_nueva_carpeta = pyqtSignal(bool)
    senal_fluka_abrir_carpeta = pyqtSignal(str)
    senal_fluka_nueva_carpeta = pyqtSignal(bool)
    senal_mcds_supervivencia = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.tab_widget = TabParams()
        self.setCentralWidget(self.tab_widget)
        self.inputs = dict()

        # Conexiones Generar input/Lanzar simulacion
        self.actionGenerar_input.triggered.connect(self.generar_input)
        self.actionLanzar_simulaciones.triggered.connect(self.lanzar_simulacion)
        self.actionNueva_carpeta.triggered.connect(self.nueva_carpeta)
        
        
        # Calcular supervivencia (elegir célula)
        self.actionCelula_HSG.triggered.connect(self.mcds_supervivencia_HSG)
        self.actionCelula_V79.triggered.connect(self.mcds_supervivencia_V79)

        # conexiones (MCDS)
        self.actionCelula.triggered.connect(self.param_celula)
        self.actionOxigenacion.triggered.connect(self.param_oxigenacion)
        self.actionControl_simulacion.triggered.connect(self.param_control_simulacion)
        self.actionCampo_de_radiacion.triggered.connect(self.param_campo_radiacion)
        self.actionFBL.triggered.connect(self.param_FBL)
        self.actionReductor_de_radicales.triggered.connect(self.param_reductor_radicales)
        # FLUKA
        self.actionFluka.triggered.connect(self.param_fluka)
        self.actionFluka_Survival.triggered.connect(self.fluka_survival)
        self.actionNueva_carpeta_proc.triggered.connect(self.fluka_nueva_carpeta)
        self.actionCarpeta_output_proc.triggered.connect(self.fluka_abrir_carpeta)
        # Plots
        self.actionInterfaz_de_ploteo.triggered.connect(self.interfaz_ploteo)
        self.tab_widget.generar_plots_button.clicked.connect(self.enviar_info_plots)
        self.tab_widget.plots_right.clicked.connect(self.plot_siguiente)
        self.tab_widget.plots_left.clicked.connect(self.plot_anterior)

        # Base de datos
        self.actionGenerar_base_de_datos.triggered.connect(self.database)
        self.tab_widget.boton_generar_db.clicked.connect(self.generar_base_datos)

        # Modelos
        self.actionWang.setChecked(True)
        self.actionWang.triggered.connect(self.modelo_wang)

        # Shortcut
        self.shortcut_generar = QShortcut(QKeySequence('Ctrl+Q'), self)
        self.shortcut_generar.activated.connect(self.generar_input)
        self.shortcut_lanzar = QShortcut(QKeySequence('Ctrl+W'), self)
        self.shortcut_lanzar.activated.connect(self.lanzar_simulacion)


    def enviar_info_plots(self):
        self.inputs.update(self.tab_widget.inputs)
        self.senal_info_plots.emit(self.inputs)
    
    def recibir_info_plots(self, event):
        # a partir del boton "generar plots", se muestra el "primer" plot del diccionario
        self.tipo_plot = event['tipo_plot']
        self.info_ultimo_plot = event
        self.tab_widget.canvas.choose_plot(self.tipo_plot, event, 1)

    def plot_siguiente(self):
        self.inputs.update(self.tab_widget.inputs)
        try:
            self.tab_widget.canvas.choose_plot(self.tipo_plot, self.info_ultimo_plot, 1)
        except AttributeError as error:
            print('Primero se debe presionar "generar plots')

    def plot_anterior(self):
        self.inputs.update(self.tab_widget.inputs)
        try:
            self.tab_widget.canvas.choose_plot(self.tipo_plot, self.info_ultimo_plot, -1)
        except AttributeError as error:
            print('Primero se debe presionar "generar plots')
    
    def generar_base_datos(self):
        self.inputs.update(self.tab_widget.inputs)
        self.senal_generar_db.emit(self.inputs)
    
    def param_celula(self, state):
        self.tab_widget.setTabVisible(0, state)
    
    def param_control_simulacion(self, state):
        self.tab_widget.setTabVisible(1, state)
    
    def param_campo_radiacion(self, state):
        self.tab_widget.setTabVisible(2, state)

    def param_oxigenacion(self, state):
        self.tab_widget.setTabVisible(3, state)
    
    def param_FBL(self, state):
        self.tab_widget.setTabVisible(4, state)

    def param_reductor_radicales(self, state):
        self.tab_widget.setTabVisible(5, state)
    
    def param_fluka(self, state):
        self.tab_widget.setTabVisible(6, state)
    
    def fluka_nueva_carpeta(self):
        self.senal_fluka_nueva_carpeta.emit(True)

    def fluka_abrir_carpeta(self):
        folder = QFileDialog.getExistingDirectory(self, 'Elegir carpeta')
        self.inputs['proc_folder_path'] = folder
    
    def interfaz_ploteo(self, state):
        self.tab_widget.setTabVisible(7, state)

    def database(self, state):
        self.tab_widget.setTabVisible(8, state)
    
    def recibir_carpeta_ident(self, event):
        tipo = event[0]
        if tipo == 1: # nueva carpeta fluka
            self.inputs['proc_folder_path'] = event[1]
        else:
            self.inputs['ident'] = event

    def generar_input(self):
        self.inputs.update(self.tab_widget.inputs)
        self.senal_generar_input.emit(self.inputs)

    def lanzar_simulacion(self):
        buscar_carpeta = QFileDialog.getExistingDirectory(self, "Elegir carpeta")
        self.senal_lanzar_simulacion.emit(buscar_carpeta)
    
    def mcds_supervivencia_HSG(self):
        directory = QFileDialog.getExistingDirectory(self, "Elegir carpeta")
        dict_surv = {'directory': directory, 'ctype': 'HSG'}
        self.senal_mcds_supervivencia.emit(dict_surv)


    def mcds_supervivencia_V79(self):
        directory = QFileDialog.getExistingDirectory(self, "Elegir carpeta")
        dict_surv = {'directory': directory, 'ctype': 'v79'}
        self.senal_mcds_supervivencia.emit(dict_surv)

    
    def nueva_carpeta(self):
        self.senal_nueva_carpeta.emit(True)
    
    def fluka_to_yield(self):
        self.inputs.update(self.tab_widget.inputs)
        self.senal_fluka_yield.emit(self.inputs)

    def fluka_survival(self):
        self.inputs.update(self.tab_widget.inputs)
        self.senal_fluka_survival.emit(self.inputs)

    def yield_to_survival(self):
        self.inputs.update(self.tab_widget.inputs)
        self.senal_yield_survival.emit(self.inputs)
    
    def modelo_wang(self):
        # Por ahora se usa solo Wang, por lo tanto se deja siempre marcada esta opción
        self.actionWang.setChecked(True)
    

class TabParams(QTabWidget):

    def __init__(self):
        super().__init__()
        self.inputs = dict()
        self.tab0 = QWidget()
        self.tab1 = QWidget()
        self.tab2 = QWidget()
        self.tab3 = QWidget()
        self.tab4 = QWidget()
        self.tab5 = QWidget()
        self.tab6 = QWidget()
        self.tab7 = QWidget()
        self.tab8 = QWidget()

        self.addTab(self.tab0, "Tab 0")
        self.addTab(self.tab1, "Tab 1")
        self.addTab(self.tab2, "Tab 2")
        self.addTab(self.tab3, "Tab 3")
        self.addTab(self.tab4, "Tab 4")
        self.addTab(self.tab5, "Tab 5")
        self.addTab(self.tab6, "Tab 6")
        self.addTab(self.tab7, "Tab 7")
        self.addTab(self.tab8, "Tab 8")

        self.tab0UI()
        self.tab1UI()
        self.tab2UI()
        self.tab3UI()
        self.tab4UI()
        self.tab5UI()
        self.tab6UI()
        self.tab7UI()
        self.tab8UI()

    def tab0UI(self):
        layout = QFormLayout()
        # Parámetros + explicacion (tooltip)
        dna = QLabel('DNA')
        self.inputs['dna'] = QLineEdit()
        dna.setToolTip('cantidad de ADN en Gbp')

        ndia = QLabel('NDIA')
        self.inputs['ndia'] = QLineEdit()
        ndia.setToolTip('Diametro nuclear en um')

        cdia = QLabel('CDIA')
        self.inputs['cdia'] = QLineEdit()
        cdia.setToolTip('Diametro celular en um')

        wem = QLabel('WEM')
        self.inputs['wem'] = QLineEdit()
        wem.setToolTip('Profundidad de la capa de agua en 10um (Ej: WEM=1 = 10um de agua)')

        layout.addRow(dna, self.inputs['dna'])
        layout.addRow(ndia, self.inputs['ndia'])
        layout.addRow(cdia, self.inputs['cdia'])
        layout.addRow(wem, self.inputs['wem'])
        self.setTabText(0,"Parámetros célula")
        self.tab0.setLayout(layout)
        self.setTabVisible(0, False)
    
    def tab1UI(self):
        layout = QFormLayout()
        # Parámetros + explicacion (tooltip)
        nocs = QLabel('NOCS')
        self.inputs['nocs'] = QLineEdit()
        nocs.setToolTip('Número de simulaciones')

        seed = QLabel('SEED')
        self.inputs['seed'] = QLineEdit()
        seed.setToolTip('Semilla de números aleatorios')

        layout.addRow(nocs, self.inputs['nocs'])
        layout.addRow(seed, self.inputs['seed'])
        self.setTabText(1, "Control simulación")
        self.tab1.setLayout(layout)
        self.setTabVisible(1, False)

    def tab2UI(self):
        layout = QFormLayout()
        # Parámetros + explicación (tooltip)
        self.inputs['par'] = QComboBox()
        self.inputs['par'].addItems(['e', 'p', '2He', '4He', '12C', '14N', '16O', '20N', '56Fe'])
        par_label = QLabel('PAR')
        par_label.setToolTip('Partícula para haz monoenergético (e,p,4He,etc)')

        ke = QLabel('KE')
        self.inputs['ke'] = QLineEdit()
        ke.setToolTip('Energía cinética para haz monoenergético en MeV')

        mev = QLabel('MeV/A')
        self.inputs['mev/a'] = QLineEdit()
        mev.setToolTip('Energía cinética por nucleón del haz en MeV')

        ad = QLabel('AD')
        self.inputs['ad'] = QLineEdit()
        ad.setToolTip('Dosis absorbida en Gy')

        layout.addRow(par_label, self.inputs['par'])
        layout.addRow(ke, self.inputs['ke'])
        layout.addRow(mev, self.inputs['mev/a'])
        layout.addRow(ad, self.inputs['ad'])
        self.setTabText(2,"Campo de radiación")
        self.tab2.setLayout(layout)
        self.setTabVisible(2, False)

    def tab3UI(self):
        layout = QFormLayout()
        # Parámetros + explicación (tooltip)
        self.inputs['oxygen_type'] = QComboBox()
        self.inputs['oxygen_type'].addItems(['%O2', 'mmHg'])
        self.inputs['oxygen_type'].setToolTip('%02: Concentración de oxígeno en %<br>mmHg: Concentración de oxígeno en mmHg, 100%=760mmHg')
        self.inputs['oxygen'] = QLineEdit()
        m0 = QLabel('m0')
        self.inputs['m0'] = QLineEdit()
        m0.setToolTip('OER máximo')
        k = QLabel('K')
        self.inputs['k'] = QLineEdit()
        k.setToolTip('Concentración de referencia para la función de rep. química')
        q = QLabel('q')
        self.inputs['q'] = QLineEdit()
        q.setToolTip('Primer parámetro de calidad de radiación')
        r = QLabel('r')
        self.inputs['r'] = QLineEdit()
        r.setToolTip('Segundo parámetro de calidad de radiación')

        layout.addRow(self.inputs['oxygen_type'], self.inputs['oxygen'])
        layout.addRow(m0, self.inputs['m0'])
        layout.addRow(k, self.inputs['k'])
        layout.addRow(q, self.inputs['q'])
        layout.addRow(r, self.inputs['r'])
        self.setTabText(3,"Oxigenación")
        self.tab3.setLayout(layout)
        self.setTabVisible(3, False)

    def tab4UI(self):
        layout = QFormLayout()
        fbl = QLabel('FBL')
        self.inputs['fbl'] = QLineEdit()
        fbl.setToolTip('Fracción de sitios abásicos')

        layout.addRow(fbl, self.inputs['fbl'])
        self.setTabText(4,"Tipo de daño a bases")
        self.tab4.setLayout(layout)
        self.setTabVisible(4, False)

    def tab5UI(self):
        layout = QFormLayout()
        conc = QLabel('CONC')
        self.inputs['conc'] = QLineEdit()
        conc.setToolTip('Concentración de reductor en mol/dm3')
        fnsd = QLabel('FNSD')
        self.inputs['fnsd'] = QLineEdit()
        fnsd.setToolTip('Fracción de radicales no reducible')
        chmx = QLabel('CHMX')
        self.inputs['chmx'] = QLineEdit()
        chmx.setToolTip('Concentración a nivel medio de reductor')

        layout.addRow(conc, self.inputs['conc'])
        layout.addRow(fnsd, self.inputs['fnsd'])
        layout.addRow(chmx, self.inputs['chmx'])
        self.setTabText(5,"Reductor de radicales")
        self.tab5.setLayout(layout)
        self.setTabVisible(5, False)
    
    def tab6UI(self):
        # FLUKA 
        layout1 = QHBoxLayout()
        layout2 = QHBoxLayout()
        layout3 = QHBoxLayout()
        layout4 = QHBoxLayout()
        layout = QFormLayout()
        layout_final = QVBoxLayout()
        self.dose_data_path_button = QPushButton('Elegir carpeta', self)
        self.spectrum_data_path_button = QPushButton('Elegir carpeta', self)
        self.databasefolderpath_button = QPushButton('Elegir carpeta', self)

        # Path seleccionado
        self.dose_data = QLabel('')
        self.spectrum_data = QLabel('')
        self.database = QLabel('')

        path_default = os.path.join(os.getcwd(), '..', 'MCDS', 'p-50-samples')
        if os.path.exists(path_default):
            self.inputs['databasefolder_path'] = path_default
            self.database.setText('{}'.format(self.inputs['databasefolder_path']))

        # Layouts
        layout1.addWidget(QLabel('Dose data'))
        layout1.addSpacing(50)
        layout1.addWidget(self.dose_data_path_button)
        layout1.addWidget(self.dose_data)

        layout2.addWidget(QLabel('Spectrum data'))
        layout2.addSpacing(50)
        layout2.addWidget(self.spectrum_data_path_button)
        layout2.addWidget(self.spectrum_data)

        layout3.addWidget(QLabel('Database'))
        layout3.addSpacing(50)
        layout3.addWidget(self.databasefolderpath_button)
        layout3.addWidget(self.database)

        # Parámetros
        self.inputs['depth_min'] = QLineEdit()
        self.inputs['depth_max'] = QLineEdit()
        self.inputs['sep_ptos'] = QLineEdit()

        self.inputs['ctype'] = QComboBox()
        self.inputs['ctype'].addItems(['v79', 'hsg'])
        self.inputs['fluka_dna'] = QLineEdit()
        self.inputs['fluka_ndia'] = QLineEdit()
        self.inputs['dose_norm_max'] = QLineEdit()


        # Conexion botones
        self.dose_data_path_button.clicked.connect(self.open_dose_data)
        self.spectrum_data_path_button.clicked.connect(self.open_spectrum_data)
        self.databasefolderpath_button.clicked.connect(self.open_databasefolder)


        layout.addRow('Profundidad mínima', self.inputs['depth_min'])
        layout.addRow('Profundidad máxima', self.inputs['depth_max'])
        layout.addRow('Separación puntos', self.inputs['sep_ptos'])
        layout.addRow('Célula', self.inputs['ctype'])
        layout.addRow('DNA', self.inputs['fluka_dna'])
        layout.addRow('NDIA', self.inputs['fluka_ndia'])
        layout.addRow('dose norm max', self.inputs['dose_norm_max'])


        layout_final.addLayout(layout1)
        layout_final.addLayout(layout2)
        layout_final.addLayout(layout3)
        layout_final.addLayout(layout)

        self.setTabText(6,"Parámetros Fluka")
        self.tab6.setLayout(layout_final)
        self.setTabVisible(6, False)
    
    def tab7UI(self):
        self.canvas = Canvas(self, width=5, height=4, dpi=100)
        # plots
        #self.canvas.axes.plot([0,1,2,3,4], [10,1,20,3,40])
        toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QHBoxLayout()
        v_layout = QVBoxLayout()
        
        top_layout = QFormLayout()
        tipo_plot = QLabel('Tipo de plot')
        self.inputs['plot_options'] = QComboBox()
        self.inputs['plot_options'].addItems(['Survival vs dose', 'Dose vs depth', 'Survival vs depth',
                                              'Yield vs depth', 'Lambda vs depth', 'Test plot',
                                             'Test plot 2'])
        carpeta = QLabel('Carpeta')
        carpeta.setToolTip('La carpeta que contiene los archivos output')
        self.carpeta_plot = QPushButton('Elegir carpeta', self)
        self.carpeta_plot.clicked.connect(self.open_carpeta_plots)

        set_experimental = QLabel('Set experimental')
        set_experimental.setToolTip('Archivo con datos experimentales, se genera un scatter de puntos')
        self.set_experimental_button = QPushButton('Elegir archivo', self)
        self.set_experimental_button.clicked.connect(self.open_set_experimental)

        label_name = QLabel('Label del set')
        self.inputs['label_set_experimental'] = QLineEdit()

        label_puntos = QLabel('Separación de puntos')
        self.inputs['num_puntos_plot'] = QSpinBox()
        self.inputs['num_puntos_plot'].setValue(10)
        self.inputs['num_puntos_plot'].setMinimum(1)

        top_layout.addRow(tipo_plot, self.inputs['plot_options'])
        top_layout.addRow(carpeta, self.carpeta_plot)
        top_layout.addRow(set_experimental, self.set_experimental_button)
        top_layout.addRow(label_name, self.inputs['label_set_experimental'])
        top_layout.addRow(label_puntos, self.inputs['num_puntos_plot'])

        v_layout.addLayout(top_layout)
        
        self.generar_plots_button = QPushButton('Generar plots')
        v_layout.addWidget(self.generar_plots_button)

        bottom_layout = QHBoxLayout()
        self.plots_left = QPushButton('Volver atras')
        self.plots_right = QPushButton('Siguiente plot')
        bottom_layout.addWidget(self.plots_left)
        bottom_layout.addWidget(self.plots_right)

        v_layout.addLayout(bottom_layout)

        layout_canvas = QVBoxLayout()
        layout_canvas.addWidget(toolbar)
        layout_canvas.addWidget(self.canvas)

        layout.addLayout(v_layout)
        layout.addLayout(layout_canvas)
        self.setTabText(7,"Plots")
        self.tab7.setLayout(layout)
        self.setTabVisible(7, False)
    
    def tab8UI(self):
        # Base de datos
        layout = QFormLayout()

        self.inputs['par_option_db'] = QComboBox()
        self.inputs['par_option_db'].addItems(['p', '12C'])   # añadir más después
        self.inputs['seed_db'] = QLineEdit()
        self.inputs['nocs'] = QLineEdit()
        self.inputs['db_type'] = QComboBox()
        self.inputs['db_type'].addItems(['Puntos de energía', 'Puntos de dosis'])
        self.inputs['N_sim'] = QLineEdit()
        self.inputs['db_tipo_dato_fijo'] = QComboBox()
        self.inputs['db_tipo_dato_fijo'].addItems(['Default', 'Fijar energía cinética', 'Fijar dosis'])
        self.inputs['db_dato_fijo'] = QLineEdit()
        self.boton_generar_db = QPushButton('Generar base de datos')

        layout.addRow('Partícula', self.inputs['par_option_db'])
        layout.addRow('SEED', self.inputs['seed_db'])
        layout.addRow('NOCS', self.inputs['nocs'])
        layout.addRow(self.inputs['db_type'], self.inputs['N_sim'])
        layout.addRow(self.inputs['db_tipo_dato_fijo'], self.inputs['db_dato_fijo'])
        layout.addRow(self.boton_generar_db)

        self.setTabText(8, 'Base de datos')
        self.tab8.setLayout(layout)
        self.setTabVisible(8, False)

    def open_dose_data(self):
        self.inputs['dose_data_path'] = QFileDialog.getExistingDirectory(self, 'Elegir carpeta')
        self.dose_data.setText('{}'.format(self.inputs['dose_data_path']))

    def open_spectrum_data(self):
        self.inputs['spectrum_data_path'] = QFileDialog.getExistingDirectory(self, 'Elegir carpeta')
        self.spectrum_data.setText('{}'.format(self.inputs['spectrum_data_path']))

    def open_databasefolder(self):
        self.inputs['databasefolder_path'] = QFileDialog.getExistingDirectory(self, 'Elegir carpeta')
        self.database.setText('{}'.format(self.inputs['databasefolder_path']))

    def open_plot_dat(self):
        self.inputs['path_plotdats'] = QFileDialog.getExistingDirectory(self, "Elegir carpeta")

    def open_tab_lis(self):
        self.inputs['path_tablis'] = QFileDialog.getExistingDirectory(self, "Elegir carpeta")

    def open_carpeta_plots(self):
        self.inputs['path_carpeta_plots'] = QFileDialog.getExistingDirectory(self, "Elegir carpeta")
    
    def open_set_experimental(self):
        self.inputs['set_experimental'] = QFileDialog.getOpenFileName(None, 'Abrir archivo', '', '')
    

class VentanaInicio(QDialog):

    senal_carpeta_identificadora = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setModal(True)
        self.setWindowTitle('Elección nombre de carpeta')
        self.setFixedWidth(485)
        self.setFixedHeight(150)

        self.fluka = False

        # Configuración de layouts + widgets
        layout = QVBoxLayout()
        self.setLayout(layout)
        top_layout = QHBoxLayout()
        mid_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        self.txt1 = QLabel('Nombre de la carpeta:')
        self.name = QLineEdit()
        top_layout.addWidget(self.txt1)
        top_layout.addWidget(self.name)

        self.txt2 = QLabel('La carpeta contendrá los inputs y outputs de MCDS')
        mid_layout.addSpacing(35)
        mid_layout.addWidget(self.txt2)

        self.boton_aceptar = QPushButton('Aceptar')
        bottom_layout.addSpacing(95)
        bottom_layout.addWidget(self.boton_aceptar)
        bottom_layout.addSpacing(95)

        layout.addLayout(top_layout)
        layout.addLayout(mid_layout)
        layout.addLayout(bottom_layout)

        # conexión de señal botón
        self.boton_aceptar.clicked.connect(self.recibir_carpeta)

    def recibir_carpeta(self, event):
        # recibe el nombre de una carpeta al hacer click en "Aceptar"
        nombre = self.name.text()
        if self.fluka:
            info = [1, nombre]
        else:
            info = [0, nombre]
        self.senal_carpeta_identificadora.emit(info)
        self.hide()
    
    def closeEvent(self, event):
        info = [0, 'default']
        self.senal_carpeta_identificadora.emit(info)
        event.accept()
    
    def nueva_carpeta(self, event):
        if event:
            self.fluka = False
            self.show()
        
    def nueva_carpeta_fluka(self, event):
        if event:
            self.txt2.setText('La carpeta contendrá los outputs proc')
            self.fluka = True
            self.show()

if __name__ == '__main__':
    app = QApplication([])
    form = VentanaInicio()
    form.show()
    sys.exit(app.exec_())