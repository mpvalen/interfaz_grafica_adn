from PyQt5.QtGui import QKeySequence
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (QApplication, QFileDialog, QTabWidget, QWidget, QFormLayout, QLineEdit,
                             QComboBox, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QDialog, QShortcut,
                             QSpinBox, QFrame, QSpinBox, QDoubleSpinBox, QStackedLayout)
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

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.tab_widget = TabParams()
        self.setCentralWidget(self.tab_widget)
        self.inputs = dict()
        self.setWindowTitle('CELL: Interfaz para simular daño al ADN')
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

        # Base de datos
        self.actionGenerar_base_de_datos.triggered.connect(self.database)
        self.tab_widget.boton_generar_db.clicked.connect(
            self.generar_base_datos)

        # Modelos
        self.actionParametros_originales.setChecked(True)
        self.actionParametros_originales.triggered.connect(
            self.modelo_wang_params)

        self.actionParametros_Sophia.triggered.connect(
            self.modelo_wang_params_sophia)
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
            print('Primero se debe presionar "generar plots')

    def plot_anterior(self):
        self.inputs.update(self.tab_widget.inputs)
        try:
            self.tab_widget.canvas.choose_plot(
                self.tipo_plot, self.info_ultimo_plot, -1)
        except AttributeError as error:
            print('Primero se debe presionar "generar plots')

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
        folder = QFileDialog.getExistingDirectory(self, 'Elegir carpeta')
        self.inputs['proc_folder_path'] = folder

    def interfaz_ploteo(self, state):
        self.tab_widget.setTabVisible(7, state)

    def database(self, state):
        self.tab_widget.setTabVisible(8, state)

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
            self, "Elegir carpeta")
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

    def modelo_wang_params(self):
        # Por ahora se usa solo Wang, por lo tanto se deja siempre marcada esta opción
        self.actionParametros_originales.setChecked(True)
        self.actionParametros_Sophia.setChecked(False)
        self.senal_modelo.emit('Wang')

    def modelo_wang_params_sophia(self):
        self.actionParametros_Sophia.setChecked(True)
        self.actionParametros_originales.setChecked(False)
        self.senal_modelo.emit('Wang-Sophia')

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
        wem.setToolTip(
            'Profundidad de la capa de agua en 10um (Ej: WEM=1 = 10um de agua)')

        layout.addRow(dna, self.inputs['dna'])
        layout.addRow(ndia, self.inputs['ndia'])
        layout.addRow(cdia, self.inputs['cdia'])
        layout.addRow(wem, self.inputs['wem'])
        self.setTabText(0, "Parámetros célula")
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
        self.inputs['par'].addItems(
            ['e', 'p', '2He', '4He', '12C', '14N', '16O', '20N', '56Fe'])
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
        self.setTabText(2, "Campo de radiación")
        self.tab2.setLayout(layout)
        self.setTabVisible(2, False)

    def tab3UI(self):
        layout = QFormLayout()
        # Parámetros + explicación (tooltip)
        self.inputs['oxygen_type'] = QComboBox()
        self.inputs['oxygen_type'].addItems(['%O2', 'mmHg'])
        self.inputs['oxygen_type'].setToolTip(
            '%02: Concentración de oxígeno en %<br>mmHg: Concentración de oxígeno en mmHg, 100%=760mmHg')
        self.inputs['oxygen'] = QLineEdit()
        m0 = QLabel('m0')
        self.inputs['m0'] = QLineEdit()
        m0.setToolTip('OER máximo')
        k = QLabel('K')
        self.inputs['k'] = QLineEdit()
        k.setToolTip(
            'Concentración de referencia para la función de rep. química')
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
        self.setTabText(3, "Oxigenación")
        self.tab3.setLayout(layout)
        self.setTabVisible(3, False)

    def tab4UI(self):
        layout = QFormLayout()
        fbl = QLabel('FBL')
        self.inputs['fbl'] = QLineEdit()
        fbl.setToolTip('Fracción de sitios abásicos')

        layout.addRow(fbl, self.inputs['fbl'])
        self.setTabText(4, "Tipo de daño a bases")
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
        self.setTabText(5, "Reductor de radicales")
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

        self.setTabText(6, "Parámetros Fluka")
        self.tab6.setLayout(layout_final)
        self.setTabVisible(6, False)

    def tab7UI(self):
        self.canvas = Canvas(self, width=5, height=4, dpi=100)
        # plots
        toolbar = NavigationToolbar2QT(self.canvas, self)
        # toolbar.addWidget(QLineEdit('uwu'))

        layout = QHBoxLayout()
        self.v_layout_plots = QVBoxLayout()

        layout_plots = QHBoxLayout()
        self.boton_nuevo_plot = QPushButton('Añadir otro plot')
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
        tipo_plot_layout.addWidget(QLabel('Tipo plot'))
        tipo_plot_layout.addWidget(self.inputs['plot_options'])

        self.v_layout_plots.addLayout(layout_plots)
        self.v_layout_plots.addLayout(tipo_plot_layout)
        self.v_layout_plots.addWidget(HorizontalLine())

        self.stackedLayout = QStackedLayout()
        self.stackedLayout.addWidget(self.plot_actual)
        self.v_layout_plots.addLayout(self.stackedLayout)

        self.v_layout_plots.addWidget(HorizontalLine())

        self.boton_fontsize = QPushButton('Cambiar tamaño de letra')
        # self.v_layout_plots.addWidget(self.boton_fontsize)
        # self.v_layout_plots.addWidget(HorizontalLine())

        self.generar_plots_button = QPushButton('Generar plots')
        self.v_layout_plots.addWidget(self.generar_plots_button)

        bottom_layout = QHBoxLayout()
        self.plots_left = QPushButton('Volver atras')
        self.plots_right = QPushButton('Siguiente plot')
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
        self.inputs['nocs'] = QSpinBox()
        self.inputs['nocs'].setRange(1, 1000000)
        self.inputs['nocs'].setValue(1)

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

        self.boton_generar_db = QPushButton('Generar base de datos')

        layout.addRow('Partícula', self.inputs['par_option_db'])
        layout.addRow('SEED', self.inputs['seed_db'])
        layout.addRow('NOCS', self.inputs['nocs'])
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
        layout_energies.addWidget(QLabel('Energía min:'))
        # layout_energies.addSpacing(10)
        layout_energies.addWidget(self.inputs['energy_db_min'])
        layout_energies.addWidget(QLabel('Energía max:'))
        layout_energies.addWidget(self.inputs['energy_db_max'])
        self.frame_rango_energias.setLayout(layout_energies)
        layout.addRow(self.boton_rangos_energia, self.frame_rango_energias)

        # layout_dosis.addSpacing(80)
        layout_dosis.addWidget(QLabel('Dosis min:'))
        # layout_dosis.addSpacing(92)
        layout_dosis.addWidget(self.inputs['dosis_db_min'])
        layout_dosis.addWidget(QLabel('Dosis max:'))
        layout_dosis.addWidget(self.inputs['dosis_db_max'])
        self.frame_rango_dosis.setLayout(layout_dosis)
        layout.addRow(self.boton_rangos_dosis, self.frame_rango_dosis)

        layout.addRow(self.boton_generar_db)

        self.setTabText(8, 'Base de datos')
        self.frame_rango_energias.hide()
        self.frame_rango_dosis.hide()
        self.inputs['db_energia_dosis_fija'].hide()
        self.tab8.setLayout(layout)
        self.setTabVisible(8, False)

    def db_cambiar_energias(self):
        if self.frame_rango_energias.isHidden():
            self.frame_rango_energias.show()
            self.boton_rangos_energia.setText('Usar intervalo predeterminado')
        else:
            self.frame_rango_energias.hide()
            self.boton_rangos_energia.setText('Cambiar intervalo de energías')
            self.inputs['energy_db_min'].setText('')
            self.inputs['energy_db_max'].setText('')

    def db_cambiar_dosis(self):
        if self.frame_rango_dosis.isHidden():
            self.frame_rango_dosis.show()
            self.boton_rangos_dosis.setText('Usar intervalo predeterminado')
        else:
            self.frame_rango_dosis.hide()
            self.boton_rangos_dosis.setText('Cambiar intervalo de dosis')
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
            self, 'Elegir carpeta')
        self.dose_data.setText('{}'.format(self.inputs['dose_data_path']))

    def open_spectrum_data(self):
        self.inputs['spectrum_data_path'] = QFileDialog.getExistingDirectory(
            self, 'Elegir carpeta')
        self.spectrum_data.setText('{}'.format(
            self.inputs['spectrum_data_path']))

    def open_databasefolder(self):
        self.inputs['databasefolder_path'] = QFileDialog.getExistingDirectory(
            self, 'Elegir carpeta')
        self.database.setText('{}'.format(self.inputs['databasefolder_path']))

    def open_plot_dat(self):
        self.inputs['path_plotdats'] = QFileDialog.getExistingDirectory(
            self, "Elegir carpeta")

    def open_tab_lis(self):
        self.inputs['path_tablis'] = QFileDialog.getExistingDirectory(
            self, "Elegir carpeta")

    def open_carpeta_plots(self):
        self.inputs['path_carpeta_plots'] = QFileDialog.getExistingDirectory(
            self, "Elegir carpeta")

    def open_set_experimental(self):
        self.inputs['set_experimental'] = QFileDialog.getOpenFileName(
            None, 'Abrir archivo', '', '')


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
