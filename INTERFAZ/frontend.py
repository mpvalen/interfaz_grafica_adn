from PyQt5.QtGui import (QKeySequence, QPalette, QFontMetrics, QStandardItem )
from PyQt5.QtCore import (pyqtSignal, QEvent, Qt)
from PyQt5.QtWidgets import (QApplication, QFileDialog, QTabWidget, QWidget, QFormLayout, QLineEdit,
                             QComboBox, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QDialog, QShortcut,
                             QSpinBox, QFrame, QSpinBox, QDoubleSpinBox, QStackedLayout, QRadioButton,
                             QStyledItemDelegate, QAction)
from PyQt5 import uic
from clases_plots import Canvas, Plot, HorizontalLine, VentanaFontSize
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
from re import A
import sys
import os
import matplotlib
import numpy as np

matplotlib.use('Qt5Agg')


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
    senal_ciclo_celular = pyqtSignal(bool)
    senal_modelo = pyqtSignal(str)
    signal_PIDE_get_info = pyqtSignal(bool)
    signal_PIDE_send_user_info = pyqtSignal(dict)
    signal_new_wang_params = pyqtSignal(dict)
    signal_PIDE_data_ML = pyqtSignal(int)
    signal_ML_survival = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.tab_widget = TabParams()
        self.setCentralWidget(self.tab_widget)
        self.inputs = dict()
        self.setWindowTitle('CELL: Cellular Effect and Lesions Linker')
        self.ventana_fontsize = VentanaFontSize(parent=self)
        self.inputs.update(self.ventana_fontsize.data)

        # Conexiones Generar input/Lanzar simulacion
        self.actionGenerar_input.triggered.connect(self.generar_input)
        self.actionLanzar_simulaciones.triggered.connect(
            self.lanzar_simulacion)
        self.actionNueva_carpeta.triggered.connect(self.nueva_carpeta)

        # Calcular supervivencia (elegir célula)
        self.actionCelula_HSG.triggered.connect(self.mcds_supervivencia_HSG)
        self.actionCelula_V79.triggered.connect(self.mcds_supervivencia_V79)

        # conexiones (MCDS)
        self.actionCelula.triggered.connect(self.param_celula)
        self.actionOxigenacion.triggered.connect(self.param_oxigenacion)
        self.actionControl_simulacion.triggered.connect(
            self.param_control_simulacion)
        self.actionCampo_de_radiacion.triggered.connect(
            self.param_campo_radiacion)
        self.actionFBL.triggered.connect(self.param_FBL)
        self.actionReductor_de_radicales.triggered.connect(
            self.param_reductor_radicales)
        # FLUKA
        self.actionFluka.triggered.connect(self.param_fluka)
        self.actionFluka_Survival.triggered.connect(self.fluka_survival)
        self.actionNueva_carpeta_proc.triggered.connect(
            self.fluka_nueva_carpeta)
        self.actionCarpeta_output_proc.triggered.connect(
            self.fluka_abrir_carpeta)
        # Plots
        self.actionInterfaz_de_ploteo.triggered.connect(self.interfaz_ploteo)
        self.tab_widget.generar_plots_button.clicked.connect(
            self.enviar_info_plots)
        self.tab_widget.plots_right.clicked.connect(self.plot_siguiente)
        self.tab_widget.plots_left.clicked.connect(self.plot_anterior)
        self.tab_widget.boton_fontsize.clicked.connect(self.change_fontsize)
        self.tab_widget.PIDE_button.clicked.connect(self.get_PIDE_exp_sets)

        # Base de datos
        self.actionGenerar_base_de_datos.triggered.connect(self.database)
        self.tab_widget.boton_generar_db.clicked.connect(
            self.generar_base_datos)

        self.actionAdd_PIDE_dataset.triggered.connect(self.add_PIDE_dataset)

        # Modelos
        self.actionParametros_originales.setChecked(True)
        self.actionParametros_originales.triggered.connect(
            self.modelo_wang_params)

        self.actionParametros_Sophia.triggered.connect(
            self.modelo_wang_params_sophia)


        self.actionChange_parameters.triggered.connect(self.change_Wang_parameters)
        self.tab_widget.change_params_button.clicked.connect(self.new_wang_params)

        self.actionTLK.triggered.connect(self.modelo_tlk)

        self.actionMachine_learning.triggered.connect(self.modelo_ML)
        self.tab_widget.button_ML_PIDE.clicked.connect(self.get_PIDE_expid_data)
        self.tab_widget.button_ML_survival.clicked.connect(self.cell_survival_ML)

        self.actions_models = [self.actionParametros_originales, self.actionParametros_Sophia, self.actionChange_parameters,
                               self.actionTLK, self.actionMachine_learning]
        # self.actionWang.setChecked(True)
        # self.actionWang.triggered.connect(self.modelo_wang)

        # Ciclo celular
        # self.actionG1.setChecked(True)
        # self.actionG1.triggered.connect(self.ciclo_celular_g1)
        # self.actionG2.triggered.connect(self.ciclo_celular_g2)

        # Shortcut
        self.shortcut_generar = QShortcut(QKeySequence('Ctrl+Q'), self)
        self.shortcut_generar.activated.connect(self.generar_input)
        self.shortcut_lanzar = QShortcut(QKeySequence('Ctrl+W'), self)
        self.shortcut_lanzar.activated.connect(self.lanzar_simulacion)


    def change_fontsize_plot(self, event):
        self.inputs.update(event)

    def enviar_info_plots(self):
        self.inputs.update(self.tab_widget.inputs)
        self.senal_info_plots.emit(self.inputs)

    def recibir_info_plots(self, event):
        # a partir del boton "generar plots", se muestra el "primer" plot del diccionario
        self.tipo_plot = event[0]['tipo_plot']
        self.info_ultimo_plot = event
        self.tab_widget.canvas.choose_plot(self.tipo_plot, event, 1)

    def plot_siguiente(self):
        self.inputs.update(self.tab_widget.inputs)
        try:
            self.tab_widget.canvas.choose_plot(
                self.tipo_plot, self.info_ultimo_plot, 1)
        except AttributeError as error:
            print('Error: Press "generate plots" first')

    def plot_anterior(self):
        self.inputs.update(self.tab_widget.inputs)
        try:
            self.tab_widget.canvas.choose_plot(
                self.tipo_plot, self.info_ultimo_plot, -1)
        except AttributeError as error:
            print('Error: Press "generate plots" first')

    def change_fontsize(self):
        self.ventana_fontsize.show()

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
        folder = QFileDialog.getExistingDirectory(self, 'Choose folder')
        self.inputs['proc_folder_path'] = folder

    def interfaz_ploteo(self, state):
        self.tab_widget.setTabVisible(7, state)

    def database(self, state):
        self.tab_widget.setTabVisible(8, state)
    
    def add_PIDE_dataset(self, state):
        self.signal_PIDE_get_info.emit(True)
        self.tab_widget.setTabVisible(9, state)
    
    def recibir_PIDE_pubnames(self, event):
        self.tab_widget.inputs['PIDE_PubNames'].addItems(event)
        self.tab_widget.inputs['PIDE_ID'].setRange(1, 1118)
    
    def get_PIDE_exp_sets(self):
        for radio in self.tab_widget.radio_PIDE_list:
            if radio.isChecked():
                self.tab_widget.inputs['PIDE_option'] = radio.text()
                self.signal_PIDE_send_user_info.emit(self.tab_widget.inputs)

    def recibir_carpeta_ident(self, event):
        tipo = event[0]
        if tipo == 1:  # nueva carpeta fluka
            self.inputs['proc_folder_path'] = event[1]
        else:
            self.inputs['ident'] = event

    def generar_input(self):
        self.inputs.update(self.tab_widget.inputs)
        self.senal_generar_input.emit(self.inputs)

    def lanzar_simulacion(self):
        buscar_carpeta = QFileDialog.getExistingDirectory(
            self, "Choose folder")
        self.senal_lanzar_simulacion.emit(buscar_carpeta)

    def mcds_supervivencia_HSG(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose folder")
        dict_surv = {'directory': directory, 'ctype': 'HSG'}
        self.senal_mcds_supervivencia.emit(dict_surv)

    def mcds_supervivencia_V79(self):
        directory = QFileDialog.getExistingDirectory(self, "Choose folder")
        dict_surv = {'directory': directory, 'ctype': 'V79'}
        self.senal_mcds_supervivencia.emit(dict_surv)
    
    def mcds_supervivencia_any_cell(self):
        for action in self.menuCalcular_supervivencia.actions():
            if action.isChecked():
                cell = action.text()
                directory = QFileDialog.getExistingDirectory(self, "Choose folder")
                dict_surv = {'directory': directory, 'ctype': cell}
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

    def modelo_wang_params(self):
        # Por ahora se usa solo Wang, por lo tanto se deja siempre marcada esta opción
        for action in self.actions_models:
            if action.isChecked():
                action.setChecked(False)
        self.actionParametros_originales.setChecked(True)
        self.senal_modelo.emit('Wang')

    def modelo_wang_params_sophia(self):
        for action in self.actions_models:
            if action.isChecked():
                action.setChecked(False)
        self.actionParametros_Sophia.setChecked(True)
        self.senal_modelo.emit('Wang-Sophia')
    
    def modelo_tlk(self):
        for action in self.actions_models:
            if action.isChecked():
                action.setChecked(False)
        self.actionTLK.setChecked(True)
        self.senal_modelo.emit('TLK')
    
    def modelo_ML(self, state):
        for action in self.actions_models:
            if action.isChecked():
                action.setChecked(False)
        self.actionMachine_learning.setChecked(True)
        self.tab_widget.setTabVisible(11, state)
        self.senal_modelo.emit('ML')

    def get_PIDE_expid_data(self):
        self.inputs.update(self.tab_widget.inputs)
        self.signal_PIDE_data_ML.emit(int(self.inputs['ML_PIDE_expid'].value()))

    def get_PIDE_values_ML(self, event):
        dict_ml = event
        self.tab_widget.change_ML_values(dict_ml)
    
    def cell_survival_ML(self):
        self.inputs.update(self.tab_widget.inputs)
        self.signal_ML_survival.emit(self.inputs)

    def change_Wang_parameters(self, state):
        self.actionParametros_Sophia.setChecked(False)
        self.actionParametros_originales.setChecked(False)
        self.tab_widget.setTabVisible(10, state)

    def new_wang_params(self):
        self.inputs.update(self.tab_widget.inputs)
        self.signal_new_wang_params.emit(self.inputs)
        self.senal_modelo.emit('Wang-modified')

    def add_new_cell_menu(self, event):
        action_new_cell = QAction(event, self)
        action_new_cell.setCheckable(True)
        self.menuCalcular_supervivencia.addAction(action_new_cell)
        action_new_cell.triggered.connect(self.mcds_supervivencia_any_cell)

    def ciclo_celular_g1(self):
        self.actionG1.setChecked(True)
        self.actionG2.setChecked(False)
        # True es etapa G1 (mantener la cantidad de ADN)
        self.senal_ciclo_celular.emit(True)

    def ciclo_celular_g2(self):
        self.actionG1.setChecked(False)
        self.actionG2.setChecked(True)
        # False es etapa G2 (multiplicar x2 el ADN)
        self.senal_ciclo_celular.emit(False)



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
        self.tab_add_PIDE = QWidget()
        self.tab_change_Wang_params = QWidget()
        self.tab_add_ML = QWidget()

        # Lista de instancias de la clase Plot
        self.inputs['plots'] = [Plot(1)]
        self.plot_actual = self.inputs['plots'][0]

        self.addTab(self.tab0, "Tab 0")
        self.addTab(self.tab1, "Tab 1")
        self.addTab(self.tab2, "Tab 2")
        self.addTab(self.tab3, "Tab 3")
        self.addTab(self.tab4, "Tab 4")
        self.addTab(self.tab5, "Tab 5")
        self.addTab(self.tab6, "Tab 6")
        self.addTab(self.tab7, "Tab 7")
        self.addTab(self.tab8, "Tab 8")
        self.addTab(self.tab_add_PIDE, "Tab PIDE")
        self.addTab(self.tab_change_Wang_params, "Tab Wang params")
        self.addTab(self.tab_add_ML, "Tab ML")

        self.tab0UI()
        self.tab1UI()
        self.tab2UI()
        self.tab3UI()
        self.tab4UI()
        self.tab5UI()
        self.tab6UI()
        self.tab7UI()
        self.tab8UI()
        self.tab_add_PIDE_UI()
        self.tab_change_Wang_params_UI()
        self.tab_add_ML_UI()

    def tab0UI(self):
        layout = QFormLayout()
        # Parámetros + explicacion (tooltip)
        dna = QLabel('DNA')
        self.inputs['dna'] = QLineEdit()
        dna.setToolTip('DNA content in Gbp')

        ndia = QLabel('NDIA')
        self.inputs['ndia'] = QLineEdit()
        ndia.setToolTip('Nucleus diameter in um')

        cdia = QLabel('CDIA')
        self.inputs['cdia'] = QLineEdit()
        cdia.setToolTip('Cell diameter in um')

        wem = QLabel('WEM')
        self.inputs['wem'] = QLineEdit()
        wem.setToolTip(
            'Water equivalent distance particle must travel to cell surface (Ej: WEM=1 => 10um in water)')

        layout.addRow(dna, self.inputs['dna'])
        layout.addRow(ndia, self.inputs['ndia'])
        layout.addRow(cdia, self.inputs['cdia'])
        layout.addRow(wem, self.inputs['wem'])
        self.setTabText(0, "Cell parameters")
        self.tab0.setLayout(layout)
        self.setTabVisible(0, False)

    def tab1UI(self):
        layout = QFormLayout()
        # Parámetros + explicacion (tooltip)
        nocs = QLabel('NOCS')
        self.inputs['nocs'] = QLineEdit()
        nocs.setToolTip('Number of simulations')

        seed = QLabel('SEED')
        self.inputs['seed'] = QLineEdit()
        seed.setToolTip('SEED for random numbers')

        layout.addRow(nocs, self.inputs['nocs'])
        layout.addRow(seed, self.inputs['seed'])
        self.setTabText(1, "Simulation parameters")
        self.tab1.setLayout(layout)
        self.setTabVisible(1, False)

    def tab2UI(self):
        layout = QFormLayout()
        # Parámetros + explicación (tooltip)
        self.inputs['par'] = QComboBox()
        self.inputs['par'].addItems(
            ['e', 'p', '2He', '4He', '12C', '14N', '16O', '20N', '56Fe'])
        par_label = QLabel('PAR')
        par_label.setToolTip('Particle type for monoenergetic beam (e,p,4He,etc)')

        ke = QLabel('KE')
        self.inputs['ke'] = QLineEdit()
        ke.setToolTip('Kinetic energy of particle for monoenergetic beam (in MeV)')

        mev = QLabel('MeV/A')
        self.inputs['mev/a'] = QLineEdit()
        mev.setToolTip('Kinetic energy specified as MeV per nucleon')

        ad = QLabel('AD')
        self.inputs['ad'] = QLineEdit()
        ad.setToolTip('Absorbed dose (Gy)')

        layout.addRow(par_label, self.inputs['par'])
        layout.addRow(ke, self.inputs['ke'])
        layout.addRow(mev, self.inputs['mev/a'])
        layout.addRow(ad, self.inputs['ad'])
        self.setTabText(2, "Radiation field")
        self.tab2.setLayout(layout)
        self.setTabVisible(2, False)

    def tab3UI(self):
        layout = QFormLayout()
        # Parámetros + explicación (tooltip)
        self.inputs['oxygen_type'] = QComboBox()
        self.inputs['oxygen_type'].addItems(['%O2', 'mmHg'])
        self.inputs['oxygen_type'].setToolTip(
            '%02: Oxygen concentration (as a percentage) %<br>mmHg: Oxygen concentration in mmHg. [100%=760mmHg]')
        self.inputs['oxygen'] = QLineEdit()
        m0 = QLabel('m0')
        self.inputs['m0'] = QLineEdit()
        m0.setToolTip('Maximum OER')
        k = QLabel('K')
        self.inputs['k'] = QLineEdit()
        k.setToolTip(
            'Concentration at which half the maximum OER occurs')
        q = QLabel('q')
        self.inputs['q'] = QLineEdit()
        q.setToolTip('First parameter for radiation quality')
        r = QLabel('r')
        self.inputs['r'] = QLineEdit()
        r.setToolTip('Second parameters for radiation quality')

        layout.addRow(self.inputs['oxygen_type'], self.inputs['oxygen'])
        layout.addRow(m0, self.inputs['m0'])
        layout.addRow(k, self.inputs['k'])
        layout.addRow(q, self.inputs['q'])
        layout.addRow(r, self.inputs['r'])
        self.setTabText(3, "Oxygen %")
        self.tab3.setLayout(layout)
        self.setTabVisible(3, False)

    def tab4UI(self):
        layout = QFormLayout()
        fbl = QLabel('FBL')
        self.inputs['fbl'] = QLineEdit()
        fbl.setToolTip('Fraction of abasic sites')

        layout.addRow(fbl, self.inputs['fbl'])
        self.setTabText(4, "Base damage")
        self.tab4.setLayout(layout)
        self.setTabVisible(4, False)

    def tab5UI(self):
        layout = QFormLayout()
        conc = QLabel('CONC')
        self.inputs['conc'] = QLineEdit()
        conc.setToolTip('DMSO concentration (in mol/dm3)')
        fnsd = QLabel('FNSD')
        self.inputs['fnsd'] = QLineEdit()
        fnsd.setToolTip('Fraction of non-scavengeable DNA damage')
        chmx = QLabel('CHMX')
        self.inputs['chmx'] = QLineEdit()
        chmx.setToolTip('Concentration at half-level (in mol/dm3)')

        layout.addRow(conc, self.inputs['conc'])
        layout.addRow(fnsd, self.inputs['fnsd'])
        layout.addRow(chmx, self.inputs['chmx'])
        self.setTabText(5, "Free radicals/scavengers")
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
        self.dose_data_path_button = QPushButton('Choose folder', self)
        self.spectrum_data_path_button = QPushButton('Choose folder', self)
        self.databasefolderpath_button = QPushButton('Choose folder', self)

        # Path seleccionado
        self.dose_data = QLabel('')
        self.spectrum_data = QLabel('')
        self.database = QLabel('')

        path_default = os.path.join(os.getcwd(), '..', 'MCDS', 'p-50-samples')
        if os.path.exists(path_default):
            self.inputs['databasefolder_path'] = path_default
            self.database.setText('{}'.format(
                self.inputs['databasefolder_path']))

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
        self.databasefolderpath_button.clicked.connect(
            self.open_databasefolder)

        layout.addRow('Minimum depth', self.inputs['depth_min'])
        layout.addRow('Maximum depth', self.inputs['depth_max'])
        layout.addRow('Point separation', self.inputs['sep_ptos'])
        layout.addRow('Cell', self.inputs['ctype'])
        layout.addRow('DNA', self.inputs['fluka_dna'])
        layout.addRow('NDIA', self.inputs['fluka_ndia'])
        layout.addRow('dose norm max', self.inputs['dose_norm_max'])

        layout_final.addLayout(layout1)
        layout_final.addLayout(layout2)
        layout_final.addLayout(layout3)
        layout_final.addLayout(layout)

        self.setTabText(6, "MC parameters")
        self.tab6.setLayout(layout_final)
        self.setTabVisible(6, False)

    def tab7UI(self):
        self.canvas = Canvas(self, width=5, height=4, dpi=100)
        # plots
        toolbar = NavigationToolbar2QT(self.canvas, self)

        layout = QHBoxLayout()
        self.v_layout_plots = QVBoxLayout()

        layout_plots = QHBoxLayout()
        self.boton_nuevo_plot = QPushButton('Add plot')
        self.boton_nuevo_plot.clicked.connect(self.nuevo_plot)
        self.plot_seleccionado = QComboBox()
        self.plot_seleccionado.activated.connect(self.cambiar_vista_plot)
        self.plot_seleccionado.addItem('Plot 1')
        self.inputs['plot_options'] = QComboBox()
        self.inputs['plot_options'].addItems(['Survival vs dose', 'Dose vs depth', 'Survival vs depth',
                                              'Yield vs depth', 'Lambda vs depth'])
        layout_plots.addWidget(self.boton_nuevo_plot)
        layout_plots.addWidget(self.plot_seleccionado)

        tipo_plot_layout = QHBoxLayout()
        tipo_plot_layout.addWidget(QLabel('Plot type'))
        tipo_plot_layout.addWidget(self.inputs['plot_options'])

        self.v_layout_plots.addLayout(layout_plots)
        self.v_layout_plots.addLayout(tipo_plot_layout)
        self.v_layout_plots.addWidget(HorizontalLine())

        self.stackedLayout = QStackedLayout()
        self.stackedLayout.addWidget(self.plot_actual)
        self.v_layout_plots.addLayout(self.stackedLayout)

        self.v_layout_plots.addWidget(HorizontalLine())

        self.boton_fontsize = QPushButton('Change font size')
        # self.v_layout_plots.addWidget(self.boton_fontsize)
        # self.v_layout_plots.addWidget(HorizontalLine())

        self.generar_plots_button = QPushButton('Generate plots')
        self.v_layout_plots.addWidget(self.generar_plots_button)

        bottom_layout = QHBoxLayout()
        self.plots_left = QPushButton('Previous plot')
        self.plots_right = QPushButton('Next plot')
        bottom_layout.addWidget(self.plots_left)
        bottom_layout.addWidget(self.plots_right)

        self.v_layout_plots.addLayout(bottom_layout)

        layout_canvas = QVBoxLayout()
        layout_canvas.addWidget(toolbar)
        layout_canvas.addWidget(self.canvas)

        layout.addLayout(self.v_layout_plots)
        layout.addLayout(layout_canvas)
        self.setTabText(7, "Plots")
        self.tab7.setLayout(layout)
        self.setTabVisible(7, False)

    def tab8UI(self):
        # Base de datos
        self.frame_rango_energias = QFrame()
        self.frame_rango_dosis = QFrame()
        layout = QFormLayout()
        layout_energies = QHBoxLayout()
        layout_dosis = QHBoxLayout()
        self.frame_ptos_energia_dosis = QFrame()
        layout_fijar_energia_dosis = QHBoxLayout()

        self.inputs['par_option_db'] = QComboBox()
        self.inputs['par_option_db'].addItems(
            ['e', 'p', '2He', '4He', '12C', '14N', '16O', '20N', '56Fe'])   # añadir más después
        self.inputs['seed_db'] = QSpinBox()
        self.inputs['seed_db'].setRange(1, 1000000000)
        self.inputs['seed_db'].setValue(987654321)
        self.inputs['nocs_db'] = QSpinBox()
        self.inputs['nocs_db'].setRange(1, 1000000)
        self.inputs['nocs_db'].setValue(1)

        self.inputs['ndia_db'] = QDoubleSpinBox()
        self.inputs['ndia_db'].setRange(0, 1000)
        self.inputs['ndia_db'].setValue(5)
        self.inputs['dna_db'] = QDoubleSpinBox()
        self.inputs['dna_db'].setRange(0, 1000)
        self.inputs['dna_db'].setValue(6)
        self.inputs['cdia_db'] = QDoubleSpinBox()
        self.inputs['cdia_db'].setRange(0, 1000)
        self.inputs['cdia_db'].setValue(0)

        self.inputs['energy_db_min'] = QLineEdit()
        self.inputs['energy_db_max'] = QLineEdit()

        self.inputs['dosis_db_min'] = QLineEdit()
        self.inputs['dosis_db_max'] = QLineEdit()

        self.inputs['db_type'] = QComboBox()
        self.inputs['db_type'].addItems(
            ['Puntos de energía', 'Puntos de dosis'])
        self.inputs['db_type'].setToolTip('Variar la energía o la dosis')
        self.inputs['N_sim'] = QLineEdit()
        self.inputs['db_energia_dosis_fija'] = QLineEdit()

        self.inputs['db_type'].activated.connect(self.fijar_energia_dosis)

        self.boton_fijar_valor = QPushButton('Fijar dosis')
        self.boton_fijar_valor.setToolTip(
            'Los valores predeterminados son el mínimo de dosis (0.1 Gy) y de energía (0.5 MeV)')
        self.boton_rangos_energia = QPushButton(
            'Cambiar intervalo de energías')
        self.boton_rangos_energia.setToolTip(
            'Los valores predeterminados son energía mínima 0.5 MeV y máxima 500 MeV')
        self.boton_rangos_dosis = QPushButton('Cambiar intervalo de dosis')
        self.boton_rangos_dosis.setToolTip(
            'Los valores predeterminados son dosis mínima 0.1 Gy y máxima 10 Gy')

        self.boton_fijar_valor.clicked.connect(
            self.fijar_energia_dosis_default)
        self.boton_rangos_energia.clicked.connect(self.db_cambiar_energias)
        self.boton_rangos_dosis.clicked.connect(self.db_cambiar_dosis)

        self.boton_generar_db = QPushButton('Generate database')

        layout.addRow('Partícula', self.inputs['par_option_db'])
        layout.addRow('SEED', self.inputs['seed_db'])
        layout.addRow('NOCS', self.inputs['nocs_db'])
        layout.addRow('NDIA', self.inputs['ndia_db'])
        layout.addRow('CDIA', self.inputs['cdia_db'])
        layout.addRow('DNA', self.inputs['dna_db'])

        layout_fijar_energia_dosis.addWidget(self.inputs['db_type'])
        layout_fijar_energia_dosis.addWidget(self.inputs['N_sim'])
        layout_fijar_energia_dosis.addWidget(self.boton_fijar_valor)
        self.frame_ptos_energia_dosis.setLayout(layout_fijar_energia_dosis)

        layout.addRow(self.frame_ptos_energia_dosis,
                      self.inputs['db_energia_dosis_fija'])

        # layout_energies.addSpacing(80)
        layout_energies.addWidget(QLabel('Min Energy:'))
        # layout_energies.addSpacing(10)
        layout_energies.addWidget(self.inputs['energy_db_min'])
        layout_energies.addWidget(QLabel('Max Energy:'))
        layout_energies.addWidget(self.inputs['energy_db_max'])
        self.frame_rango_energias.setLayout(layout_energies)
        layout.addRow(self.boton_rangos_energia, self.frame_rango_energias)

        # layout_dosis.addSpacing(80)
        layout_dosis.addWidget(QLabel('Min Dose:'))
        # layout_dosis.addSpacing(92)
        layout_dosis.addWidget(self.inputs['dosis_db_min'])
        layout_dosis.addWidget(QLabel('Max Dose:'))
        layout_dosis.addWidget(self.inputs['dosis_db_max'])
        self.frame_rango_dosis.setLayout(layout_dosis)
        layout.addRow(self.boton_rangos_dosis, self.frame_rango_dosis)

        layout.addRow(self.boton_generar_db)

        self.setTabText(8, 'Databases')
        self.frame_rango_energias.hide()
        self.frame_rango_dosis.hide()
        self.inputs['db_energia_dosis_fija'].hide()
        self.tab8.setLayout(layout)
        self.setTabVisible(8, False)

    def tab_add_PIDE_UI(self):
        main_layout = QVBoxLayout()
        hlayout = QHBoxLayout()
        layout = QFormLayout()

        self.radio_PIDE_ID = QRadioButton('#ExpID')
        self.inputs['PIDE_ID'] = QSpinBox()
        self.inputs['PIDE_ID'].setRange(1, 1118)
        self.inputs['PIDE_ID'].setValue(1)

        self.radio_PIDE_range = QRadioButton('Range of #ExpIDs')
        self.inputs['PIDE_range'] = QLineEdit(self, placeholderText='Example: 1-10')

        self.radio_PIDE_PubName = QRadioButton('Publication name')
        self.inputs['PIDE_PubNames'] = QComboBoxModified()


        self.radio_PIDE_all = QRadioButton('All')

        self.radio_PIDE_list = [self.radio_PIDE_ID, self.radio_PIDE_range, self.radio_PIDE_PubName, self.radio_PIDE_all]

        layout.addRow(self.radio_PIDE_ID, self.inputs['PIDE_ID'])
        layout.addRow(self.radio_PIDE_range, self.inputs['PIDE_range'])
        layout.addRow(self.radio_PIDE_PubName, self.inputs['PIDE_PubNames'])
        layout.addRow(self.radio_PIDE_all, QLabel(''))

        self.inputs['PIDE_ID'].hide()
        self.inputs['PIDE_range'].hide()
        self.inputs['PIDE_PubNames'].hide()

        self.radio_PIDE_ID.toggled.connect(self.PIDE_single_ExpID)
        self.radio_PIDE_range.toggled.connect(self.PIDE_range_ExpID)
        self.radio_PIDE_PubName.toggled.connect(self.PIDE_PubName)
        self.radio_PIDE_all.toggled.connect(self.PIDE_all)

        main_layout.addLayout(layout)
        self.PIDE_button = QPushButton('Add dataset')

        hlayout.addStretch()
        hlayout.addWidget(self.PIDE_button)
        hlayout.addStretch()

        main_layout.addLayout(hlayout)
        main_layout.addStretch()
        self.tab_add_PIDE.setLayout(main_layout)

        self.setTabText(9, 'PIDE')
        self.setTabVisible(9, False)

    def tab_change_Wang_params_UI(self):
        main_layout = QVBoxLayout()

        self.radio_change_params = QRadioButton('Change parameters')
        self.radio_add_cell_line = QRadioButton('Add cell line')

        main_layout.addWidget(self.radio_change_params)
        main_layout.addWidget(self.radio_add_cell_line)

        self.wang_params_frame = QFrame()
        frame_layout = QVBoxLayout()

        cell_line_layout = QHBoxLayout()
        mu_x_layout = QHBoxLayout()
        mu_y_layout = QHBoxLayout()
        zeta_layout = QHBoxLayout()
        xi_layout = QHBoxLayout()
        eta_1_layout = QHBoxLayout()
        eta_infty_layout = QHBoxLayout()

        self.inputs['change_cell_params'] = QComboBox()
        self.inputs['change_cell_params'].addItems(['V79', 'HSG'])
        self.inputs['new_cell'] = QLineEdit()

        self.inputs['mu_x'] = QDoubleSpinBox()
        self.inputs['mu_x_e'] = QDoubleSpinBox()
        self.inputs['mu_y'] = QDoubleSpinBox()
        self.inputs['mu_y_e'] = QDoubleSpinBox()
        self.inputs['zeta'] = QDoubleSpinBox()
        self.inputs['zeta_e'] = QDoubleSpinBox()
        self.inputs['xi'] = QDoubleSpinBox()
        self.inputs['xi_e'] = QDoubleSpinBox()
        self.inputs['eta_1'] = QDoubleSpinBox()
        self.inputs['eta_1_e'] = QDoubleSpinBox()
        self.inputs['eta_infty'] = QDoubleSpinBox()
        self.inputs['eta_infty_e'] = QDoubleSpinBox()


        cell_line_layout.addWidget(QLabel('Cell Line: '))
        cell_line_layout.addWidget(self.inputs['change_cell_params'])
        cell_line_layout.addWidget(self.inputs['new_cell'])
        cell_line_layout.addStretch()

        mu_x_layout.addWidget(QLabel('Mu_x: '))
        mu_x_layout.addWidget(self.inputs['mu_x'])
        mu_x_layout.addWidget(QLabel('+/-'))
        mu_x_layout.addWidget(self.inputs['mu_x_e'])

        mu_y_layout.addWidget(QLabel('Mu_y: '))
        mu_y_layout.addWidget(self.inputs['mu_y'])
        mu_y_layout.addWidget(QLabel('+/-'))
        mu_y_layout.addWidget(self.inputs['mu_y_e'])

        zeta_layout.addWidget(QLabel('Zeta: '))
        zeta_layout.addWidget(self.inputs['zeta'])
        zeta_layout.addWidget(QLabel('+/-'))
        zeta_layout.addWidget(self.inputs['zeta_e'])

        xi_layout.addWidget(QLabel('Xi: '))
        xi_layout.addWidget(self.inputs['xi'])
        xi_layout.addWidget(QLabel('+/-'))
        xi_layout.addWidget(self.inputs['xi_e'])

        eta_1_layout.addWidget(QLabel('Eta_1: '))
        eta_1_layout.addWidget(self.inputs['eta_1'])
        eta_1_layout.addWidget(QLabel('+/-'))
        eta_1_layout.addWidget(self.inputs['eta_1_e'])

        eta_infty_layout.addWidget(QLabel('Eta_infty: '))
        eta_infty_layout.addWidget(self.inputs['eta_infty'])
        eta_infty_layout.addWidget(QLabel('+/-'))
        eta_infty_layout.addWidget(self.inputs['eta_infty_e'])

        self.change_params_button = QPushButton('Change parameters')

        frame_layout.addLayout(cell_line_layout)
        frame_layout.addLayout(mu_x_layout)
        frame_layout.addLayout(mu_y_layout)
        frame_layout.addLayout(zeta_layout)
        frame_layout.addLayout(xi_layout)
        frame_layout.addLayout(eta_1_layout)
        frame_layout.addLayout(eta_infty_layout)
        frame_layout.addWidget(self.change_params_button)

        self.wang_params_frame.setLayout(frame_layout)
        main_layout.addWidget(self.wang_params_frame)

        self.radio_change_params.toggled.connect(self.change_params_frame)
        self.radio_add_cell_line.toggled.connect(self.add_cell_line_frame)

        self.inputs['change_cell_params'].hide()
        self.inputs['new_cell'].hide()
        self.wang_params_frame.hide()


        self.tab_change_Wang_params.setLayout(main_layout)
        self.setTabText(10, 'Change Wang parameters')
        self.setTabVisible(10, False)
    
    def tab_add_ML_UI(self):
        main_layout = QVBoxLayout()

        self.radio_ML_PIDE = QRadioButton('Use PIDE values for a given #ExpID')
        self.radio_ML_PIDE.toggled.connect(self.add_PIDE_expid_ML)
        self.ML_PIDE_frame = QFrame()
        frame_layout = QHBoxLayout()
        self.inputs['ML_PIDE_expid'] = QSpinBox()
        self.inputs['ML_PIDE_expid'].setRange(1, 1118)
        self.inputs['ML_PIDE_expid'].setValue(1)

        self.button_ML_PIDE = QPushButton('Get PIDE values')
        frame_layout.addWidget(QLabel('#ExpID: '))
        frame_layout.addWidget(self.inputs['ML_PIDE_expid'])
        frame_layout.addWidget(self.button_ML_PIDE)
        self.ML_PIDE_frame.setLayout(frame_layout)
        
        dose_layout = QHBoxLayout()
        self.inputs['dose_ML'] = QLineEdit(self, placeholderText='Example: 1-10')
        dose_layout.addWidget(QLabel('Doses (range) in Gy: '))
        dose_layout.addWidget(self.inputs['dose_ML'])
        
        energy_layout = QHBoxLayout()
        self.inputs['energy_ML'] = QDoubleSpinBox()
        self.inputs['energy_ML'].setRange(0, 1000)
        self.inputs['energy_ML'].setValue(0.5)
        energy_layout.addWidget(QLabel('Energy (MeV): '))
        energy_layout.addWidget(self.inputs['energy_ML'])

        charge_layout = QHBoxLayout()
        self.inputs['charge_ML'] = QSpinBox()
        self.inputs['charge_ML'].setRange(1, 100)
        self.inputs['charge_ML'].setValue(1)
        charge_layout.addWidget(QLabel('Charge: '))
        charge_layout.addWidget(self.inputs['charge_ML'])

        dna_layout = QHBoxLayout()
        self.inputs['dna_ML'] = QDoubleSpinBox()
        self.inputs['dna_ML'].setRange(0, 100)
        self.inputs['dna_ML'].setValue(6)
        dna_layout.addWidget(QLabel('DNA content (Gbp): '))
        dna_layout.addWidget(self.inputs['dna_ML'])

        ion_layout = QHBoxLayout()
        self.inputs['ion_ML'] = QComboBox()
        particles = ['12C', '20Ne', '40Ar', '4He', '1H', '2H', '3He',
                    '28Si', '56Fe', '7Li', '11B', '238U', '16O',
                    '14N', '58Ni', '48Ti', '84Kr', '10B', '6Li',
                    '13C', '132Xe', '197Au']
        self.inputs['ion_ML'].addItems(particles)
        ion_layout.addWidget(QLabel('Ion: '))
        ion_layout.addWidget(self.inputs['ion_ML'])

        irr_cond_layout = QHBoxLayout()
        self.inputs['irr_cond_ML'] = QComboBox()
        self.inputs['irr_cond_ML'].addItems(['Spread-out Bragg peak', 'Monoenergetic'])
        irr_cond_layout.addWidget(QLabel('Irradiation condition: '))
        irr_cond_layout.addWidget(self.inputs['irr_cond_ML'])

        cell_layout = QHBoxLayout()
        self.inputs['cell_ML'] = QComboBox()
        cells = ['V79', 'T1', 'CHO-10B', 'HS-23', 'C3H10T1/2', 'AG1522', 'HeLa', 'HeLaS3',
                'irs1', 'irs2', 'L5178Y', 'M10', 'LTA', 'SL3-147', 'HE20', 'NB1RGB',
                'ONS-76', 'A-172', 'U-251MG', 'TK1', 'CHO-K1', 'xrs5', 'HSG', 'HFL-III',
                'LC-1sq', 'A-549', 'C32TG', 'Marcus', 'U-251MGKO', 'SK-MG-1', 'KNS-89',
                'KS-1', 'KNS-60', 'Becker', 'T98G', 'SF126', 'HF19', 'M/10', 'SCC25', 'SQ20B',
                'RAT-1', 'IEC-6', 'EUE', 'U-87MG', 'LN229', 'SuSa', 'AT1OS', 'LS-174T',
                'CHO', 'SHE', 'H1299-wtp53', 'HL-60', 'AG1522B', 'PS1', 'B14FAF28', 'AA', 'AA8',
                'HE', 'Colo679', 'HMV-I', 'HMV-II', '92-1', 'MeWo', 'HTh7', 'B16', 'IGR', 'U-343MG',
                'DU-145', 'xrs6', 'xrs6-hamKu80', '180BR', 'ChangHL', 'M3-1', 'A-172neo',
                'A-172mp53', 'H1299wtp53', 'H1299tp53', 'H1299tp53-null', 'OCUB-M', 'CRL-1500',
                'YMB-1', 'Aprt', 'AG01522', 'SASmp53', 'SASneo', 'B16-F0', 'HEK', 'V79-4', 'irs3',
                'CGL1', 'SCC61', 'HEP2', 'U-87', 'SW-1573', 'UV41', 'irs1SF', 'V3', 'ONS76',
                'MOLT4', 'XR1', 'HepG2', 'Hep3B', 'HuH7', 'PLC', 'AT-25F', 'HTB140', 'Bcl-2',
                'Neo', 'HFIB2', 'HFIB15', 'HFIB30', 'MEF', 'HFL-I', 'Caski', 'clone431', 'AG1522D',
                'HFFF2', 'DLD1', 'HCT116', 'HSF', 'HMF', 'HT1080', 'LM8', 'PDV', 'PDVC57',
                'H4', 'HD1', 'H460']
        self.inputs['cell_ML'].addItems(cells)
        cell_layout.addWidget(QLabel('Cell line: '))
        cell_layout.addWidget(self.inputs['cell_ML'])

        cell_class_layout = QHBoxLayout()
        self.inputs['cell_class_ML'] = QComboBox()
        self.inputs['cell_class_ML'].addItems(['Normal', 'Tumor'])
        cell_class_layout.addWidget(QLabel('Cell class: '))
        cell_class_layout.addWidget(self.inputs['cell_class_ML'])

        cell_origin_layout = QHBoxLayout()
        self.inputs['cell_origin_ML'] = QComboBox()
        self.inputs['cell_origin_ML'].addItems(['human', 'rodent'])
        cell_origin_layout.addWidget(QLabel('Cell origin: '))
        cell_origin_layout.addWidget(self.inputs['cell_origin_ML'])

        cell_cycle_layout = QHBoxLayout()
        self.inputs['cell_cycle_ML'] = QComboBox()
        self.inputs['cell_cycle_ML'].addItems(['G0', 'G1', 'a', 'G1/G0', 'G0/G1', 'Se',
                                               'Sm', 'Sl', 'M', 'S', 'G1/S'])
        cell_cycle_layout.addWidget(QLabel('Cell cycle: '))
        cell_cycle_layout.addWidget(self.inputs['cell_cycle_ML'])

        self.button_ML_survival = QPushButton('Calculate cell survival')

        main_layout.addLayout(dose_layout)
        main_layout.addWidget(self.radio_ML_PIDE)
        main_layout.addWidget(self.ML_PIDE_frame)
        main_layout.addWidget(HorizontalLine())
        main_layout.addLayout(energy_layout)
        main_layout.addLayout(charge_layout)
        main_layout.addLayout(dna_layout)
        main_layout.addLayout(ion_layout)
        main_layout.addLayout(irr_cond_layout)
        main_layout.addLayout(cell_layout)
        main_layout.addLayout(cell_class_layout)
        main_layout.addLayout(cell_origin_layout)
        main_layout.addLayout(cell_cycle_layout)
        main_layout.addWidget(self.button_ML_survival)
        self.tab_add_ML.setLayout(main_layout)
        
        self.ML_PIDE_frame.hide()
        self.setTabText(11, 'Machine Learning parameters')
        self.setTabVisible(11, False)

    def db_cambiar_energias(self):
        if self.frame_rango_energias.isHidden():
            self.frame_rango_energias.show()
            self.boton_rangos_energia.setText('Use default interval')
        else:
            self.frame_rango_energias.hide()
            self.boton_rangos_energia.setText('Change energy interval')
            self.inputs['energy_db_min'].setText('')
            self.inputs['energy_db_max'].setText('')

    def db_cambiar_dosis(self):
        if self.frame_rango_dosis.isHidden():
            self.frame_rango_dosis.show()
            self.boton_rangos_dosis.setText('Use default interval')
        else:
            self.frame_rango_dosis.hide()
            self.boton_rangos_dosis.setText('Change dose interval')
            self.inputs['dosis_db_min'].setText('')
            self.inputs['dosis_db_max'].setText('')

    def nuevo_plot(self):
        # Crear una nueva instancia de Plot y guardarla
        plot = Plot(len(self.inputs['plots']) + 1)
        self.inputs['plots'].append(plot)
        num_plots = len(self.inputs['plots'])
        self.plot_seleccionado.addItem(f'Plot {num_plots}')
        self.stackedLayout.addWidget(plot)

    def cambiar_vista_plot(self):
        self.stackedLayout.setCurrentIndex(
            self.plot_seleccionado.currentIndex())
        # plot = int(self.plot_seleccionado.currentText()[5:])
        # self.plot_actual = self.inputs['plots'][plot - 1]

    def fijar_energia_dosis(self):
        if self.inputs['db_type'].currentText() == 'Puntos de energía':
            # fijar dosis
            self.boton_fijar_valor.setText('Fijar dosis')
        elif self.inputs['db_type'].currentText() == 'Puntos de dosis':
            # fijar energía
            self.boton_fijar_valor.setText('Fijar energía')

    def fijar_energia_dosis_default(self):
        if self.inputs['db_energia_dosis_fija'].isHidden():
            self.inputs['db_energia_dosis_fija'].show()
            self.boton_fijar_valor.setText('Valor predeterminado')
        else:
            self.inputs['db_energia_dosis_fija'].hide()
            if self.inputs['db_type'].currentText() == 'Puntos de energía':
                self.boton_fijar_valor.setText('Fijar dosis')
            else:
                self.boton_fijar_valor.setText('Fijar energía')

    def open_dose_data(self):
        self.inputs['dose_data_path'] = QFileDialog.getExistingDirectory(
            self, 'Choose folder')
        self.dose_data.setText('{}'.format(self.inputs['dose_data_path']))

    def open_spectrum_data(self):
        self.inputs['spectrum_data_path'] = QFileDialog.getExistingDirectory(
            self, 'Choose folder')
        self.spectrum_data.setText('{}'.format(
            self.inputs['spectrum_data_path']))

    def open_databasefolder(self):
        self.inputs['databasefolder_path'] = QFileDialog.getExistingDirectory(
            self, 'Choose folder')
        self.database.setText('{}'.format(self.inputs['databasefolder_path']))

    def open_plot_dat(self):
        self.inputs['path_plotdats'] = QFileDialog.getExistingDirectory(
            self, "Choose folder")

    def open_tab_lis(self):
        self.inputs['path_tablis'] = QFileDialog.getExistingDirectory(
            self, "Choose folder")

    def open_carpeta_plots(self):
        self.inputs['path_carpeta_plots'] = QFileDialog.getExistingDirectory(
            self, "Choose folder")

    def open_set_experimental(self):
        self.inputs['set_experimental'] = QFileDialog.getOpenFileName(
            None, 'Open file', '', '')
    
    
    def PIDE_single_ExpID(self):
        self.inputs['PIDE_ID'].show()
        self.inputs['PIDE_range'].hide()
        self.inputs['PIDE_PubNames'].hide()

    def PIDE_range_ExpID(self):
        self.inputs['PIDE_range'].show()
        self.inputs['PIDE_ID'].hide()
        self.inputs['PIDE_PubNames'].hide()
    
    def PIDE_PubName(self):
        self.inputs['PIDE_PubNames'].show()
        self.inputs['PIDE_ID'].hide()
        self.inputs['PIDE_range'].hide()
    
    def PIDE_all(self):
        self.inputs['PIDE_ID'].hide()
        self.inputs['PIDE_range'].hide()
        self.inputs['PIDE_PubNames'].hide()

    def change_params_frame(self):
        self.wang_params_frame.show()
        self.inputs['change_cell_params'].show()
        self.inputs['new_cell'].setText('')
        self.inputs['new_cell'].hide()

    def add_cell_line_frame(self):
        self.wang_params_frame.show()
        self.inputs['change_cell_params'].hide()
        self.inputs['new_cell'].show()
    
    def add_PIDE_expid_ML(self):
        if self.radio_ML_PIDE.isChecked():
            self.ML_PIDE_frame.show()
        else:
            self.ML_PIDE_frame.hide()
    
    def change_ML_values(self, dict_info):
        self.inputs['energy_ML'].setValue(dict_info['Energy'])
        self.inputs['charge_ML'].setValue(dict_info['Charge'])
        self.inputs['dna_ML'].setValue(dict_info['DNAContent'])
        self.inputs['ion_ML'].setCurrentText(dict_info['Ion'])
        self.inputs['cell_ML'].setCurrentText(dict_info['Cell'])
        self.inputs['cell_class_ML'].setCurrentText(dict_info['CellClass'])
        self.inputs['cell_origin_ML'].setCurrentText(dict_info['CellOrigin'])
        self.inputs['cell_cycle_ML'].setCurrentText(dict_info['CellCycle'])
    
    

class VentanaInicio(QDialog):

    senal_carpeta_identificadora = pyqtSignal(list)

    def __init__(self):
        super().__init__()
        self.setModal(True)
        self.setWindowTitle('Choose folder name')
        self.setFixedWidth(485)
        self.setFixedHeight(150)

        self.fluka = False

        # Configuración de layouts + widgets
        layout = QVBoxLayout()
        self.setLayout(layout)
        top_layout = QHBoxLayout()
        mid_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()

        self.txt1 = QLabel('Folder name:')
        self.name = QLineEdit()
        top_layout.addWidget(self.txt1)
        top_layout.addWidget(self.name)

        self.txt2 = QLabel('This folder will contain the inputs and outputs of the MCDS code')
        mid_layout.addSpacing(35)
        mid_layout.addWidget(self.txt2)

        self.boton_aceptar = QPushButton('Accept')
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
            self.txt2.setText('This folder will contain the outputs of the fluka tab')
            self.fluka = True
            self.show()


class QComboBoxModified(QComboBox):
    # Code adapted from: https://gis.stackexchange.com/a/351152
    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Make the combo editable to set a custom text, but readonly
        self.setEditable(True)
        self.lineEdit().setReadOnly(True)
        # Make the lineedit the same color as QPushButton
        palette = QApplication.palette()
        palette.setBrush(QPalette.Base, palette.button())
        self.lineEdit().setPalette(palette)

        # Use custom delegate
        self.setItemDelegate(QComboBoxModified.Delegate())

        # Update the text when an item is toggled
        self.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.view().viewport().installEventFilter(self)

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        super().resizeEvent(event)

    def eventFilter(self, object, event):

        if object == self.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.hidePopup()
                else:
                    self.showPopup()
                return True
            return False

        if object == self.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.view().indexAt(event.pos())
                item = self.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                return True
        return False

    def showPopup(self):
        super().showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        super().hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.killTimer(event.timerId())
        self.closeOnLineEditClick = False

    def updateText(self):
        texts = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                texts.append(self.model().item(i).text())
        text = ", ".join(texts)

        # Compute elided text (with "...")
        metrics = QFontMetrics(self.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.ElideRight, self.lineEdit().width())
        self.lineEdit().setText(elidedText)

    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.model().rowCount()):
            if self.model().item(i).checkState() == Qt.Checked:
                res.append(self.model().item(i).data())
        return res

if __name__ == '__main__':
    app = QApplication([])
    form = VentanaInicio()
    form.show()
    sys.exit(app.exec_())
