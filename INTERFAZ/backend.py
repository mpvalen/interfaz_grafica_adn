from xmlrpc.server import SimpleXMLRPCDispatcher
import spectrum_processing as spct
from PyQt5.QtCore import QObject, pyqtSignal
import matplotlib.pyplot as plt
import subprocess
import mech_model as mech
import numpy as np
import mcds_fop as fop
import fluka_to_data as ftd
import os
import pandas as pd
import natsort
from uncertainties import ufloat


class Logica(QObject):
    # Clase que contiene gran parte de las funciones del backend de la interfaz. Se guarda información
    # recurrente como directorio escogido, parámetros dados por el user, etc.
    senal_info_plots_backend = pyqtSignal(list)
    senal_PIDE_pubnames = pyqtSignal(list)
    signal_new_cell = pyqtSignal(str)
    signal_PIDE_ML_data = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.contador_inputs_mcds = 0
        self.path_mcds = os.path.join('mcds', 'bin', 'mcds.exe')
        self.g1 = True
        self.modelo = mech.Modelo_Wang()
        # self.database_particles = [''] añadir protones y carbono12

    def recibir_input_mcds(self, e):
        # recibe un diccionario con parámetros y escribe archivo input
        ident = e['ident'][1]
        print(f'NOCS: {e["nocs"].text()}')
        if str(e['oxygen_type'].currentText()) == '%O2':
            inp_text = fop.mcds_inp(e['dna'].text(), e['ndia'].text(), e['cdia'].text(),
                                    e['wem'].text(), e['seed'].text(), e['nocs'].text(), '',  # FN (Fluka)
                str(e['par'].currentText()), e['ke'].text(
            ), e['mev/a'].text(), e['ad'].text(),
                e['oxygen'].text(), '', e['m0'].text(
            ), e['k'].text(), e['q'].text(),
                e['r'].text(), e['fbl'].text(), e['conc'].text(), e['fnsd'].text(), e['chmx'].text())
        else:
            inp_text = fop.mcds_inp(e['dna'].text(), e['ndia'].text(), e['cdia'].text(),
                                    e['wem'].text(), e['seed'].text(
            ), e['nocs'].text(), '',
                str(e['par'].currentText()), e['ke'].text(
            ), e['mev/a'].text(), e['ad'].text(),
                '', e['oxygen'].text(), e['m0'].text(
            ), e['k'].text(), e['q'].text(),
                e['r'].text(), e['fbl'].text(), e['conc'].text(), e['fnsd'].text(), e['chmx'].text())
        dir = os.path.join(os.getcwd(), ident)
        try:
            os.mkdir(dir)
        except:
            # se usa el mismo directorio
            self.contador_inputs_mcds = len(
                [f for f in os.listdir(dir) if f.endswith('.inp')])
        gen_inp = open(os.path.join(
            dir, f'{ident}_{self.contador_inputs_mcds}.inp'), 'w')
        gen_inp.write(inp_text)
        gen_inp.close()

        self.contador_inputs_mcds += 1

    def lanzar_simulaciones(self, event):
        # iniciar simulaciones con los inputs de la carpeta (MCDS)
        if event == '*':
            # error porque la carpeta no existe
            self.senal_error_lanzar.emit(True)
        else:
            ident = event
            dir = ident
            cont_bats = 0
            try:
                for archivo in os.listdir(dir):
                    if archivo.endswith('inp'):
                        ruta = os.path.join(dir, archivo)
                        bat_path = os.path.join(
                            dir, f'{ident}_bat_{cont_bats}.bat')
                        bat = open(bat_path, 'w')
                        bat.write(fop.mcds_bat(ruta, self.path_mcds))
                        bat.close()
                        subprocess.call([r'{}'.format(bat_path)])
                        os.remove(bat_path)
                        cont_bats += 1
            except FileNotFoundError as error:
                print(
                    'Error: Debe seleccionar una carpeta válida para lanzar las simulaciones')

    def recibir_input_fluka_yield(self, event):
        # recibe diccionario con path de plotdats, tablis, separacion detectores
        # y posicion inicial detector
        self.inputs = event

        try:
            self.dose_data_path = event['dose_data_path']
            self.spectrum_data_path = event['spectrum_data_path']
            self.databasefolder_path = event['databasefolder_path']
            self.depth_min = float(event['depth_min'].text())
            self.depth_max = float(event['depth_max'].text())
            self.sep_ptos = float(event['sep_ptos'].text())
            self.ctype = str(event['ctype'].currentText())
            self.dna = float(event['fluka_dna'].text())
            self.ndia = float(event['fluka_ndia'].text())
            self.dose_norm_max = float(event['dose_norm_max'].text())
            self.proc_output_path = event['proc_folder_path']

            Ndet = int((self.depth_max - self.depth_min) / self.sep_ptos)
            detector_depth = [self.depth_min + i *
                              self.sep_ptos for i in range(0, Ndet + 1)]

            # si es windows, arregla el path
            if '\\' in self.dose_data_path:
                self.dose_data_path = self.dose_data_path.replace('\\', '\\\\')
            if '\\' in self.spectrum_data_path:
                self.spectrum_data_path = self.spectrum_data_path.replace(
                    '\\', '\\\\')
            if '\\' in self.databasefolder_path:
                self.databasefolder_path = self.databasefolder_path.replace(
                    '\\', '\\\\')

            data = ftd.fluka_to_data(self.spectrum_data_path, self.dose_data_path, self.databasefolder_path,
                                     detector_depth, self.ctype, self.dna, self.ndia, self.dose_norm_max,
                                     self.proc_output_path)

        except KeyError as error:
            print('Error: debe escoger una carpeta válida')

    def info_plots(self, event):
        # recibe el tipo de plot, envia info necesaria para plotear
        tipo_plot = str(event['plot_options'].currentText())

        plots = event['plots']
        info_dicts = []
        dict_fontsize = {'title_fontsize': int(event['title_fontsize'].text()),
                         'labels_fontsize': int(event['labels_fontsize'].text()),
                         'axisticks_fontsize': int(event['axisticks_fontsize'].text()),
                         'axistext_fontsize': int(event['axistext_fontsize'].text())}
        for i, plot in enumerate(plots):
            directory = plot.path_carpeta_plots
            dict_info = dict()
            dict_info['tipo_plot'] = tipo_plot
            label_curva = plot.label.text()
            label_set_experimental = plot.label_experimental.text()
            num_ptos_plot = plot.num_puntos_plot.text()
            usar_barras_error = plot.barras_error_check.isChecked()
            try:
                set_experimental_path = plot.set_experimental[0]
                set_x, set_y = read_set_experimental(set_experimental_path)
                set_experimental = {'values': True, 'set_x': set_x, 'set_y': set_y,
                                    'label_curva': label_curva, 'label_experimental': label_set_experimental,
                                    'barras_error': usar_barras_error}
            except (KeyError, FileNotFoundError, IndexError) as error:
                if label_curva != '':
                    set_experimental = {'values': False, 'label_curva': label_curva,
                                        'label_experimental': label_set_experimental,
                                        'barras_error': usar_barras_error}
                else:
                    set_experimental = {'values': False, 'label_curva': f'Plot {i}',
                                        'label_experimental': label_set_experimental,
                                        'barras_error': usar_barras_error}
            set_experimental.update(dict_fontsize)
            if directory == '' and set_experimental['values'] == True:
                # plot only the experimental data
                dict_file = {'set_experimental': set_experimental}
                dict_info['tipo_plot'] = 'Experimental data'
                dict_info[f'{0}'] = dict_file
                info_dicts.append(dict_info)
                self.senal_info_plots_backend.emit(info_dicts)
            else:
                if tipo_plot == 'Dose vs depth':
                    # Leer archivos de la carpeta
                    for file in os.listdir(directory):
                        path_read = os.path.join(directory, file)
                        (self.depths_mm, self.doses, self.doseerrs, self.dsbyields, self.dsbyielderrs,
                        self.lmbdas, self.lmbdaerrs, self.survs, self.surverrs) = read_output_file(path_read)
                        dict_file = {'doses': self.doses, 'doseserr': self.doseerrs,
                                    'depth': self.depths_mm, 'set_experimental': set_experimental,
                                    'num_puntos': num_ptos_plot}
                        dosis_key = find_dose_from_filename(file)
                        dict_info[f'{dosis_key}'] = dict_file
                        info_dicts.append(dict_info)
                    self.senal_info_plots_backend.emit(info_dicts)

                elif tipo_plot == 'Survival vs dose':
                    for file in os.listdir(directory):
                        if file.endswith('.db'):
                            survival, surverr, dose = read_surv_dose_file(
                                os.path.join(directory, file))
                            dict_file = {'doses': dose, 'survival': survival, 'surverr': surverr,
                                        'set_experimental': set_experimental, 'num_puntos': num_ptos_plot}
                            dosis_key = 0
                            dict_info[f'{dosis_key}'] = dict_file
                    info_dicts.append(dict_info)
                    self.senal_info_plots_backend.emit(info_dicts)

                elif tipo_plot == 'Survival vs depth':
                    for file in os.listdir(directory):
                        path_read = os.path.join(directory, file)
                        (self.depths_mm, self.doses, self.doseerrs, self.dsbyields, self.dsbyielderrs,
                        self.lmbdas, self.lmbdaerrs, self.survs, self.surverrs) = read_output_file(path_read)
                        dict_file = {'depth': self.depths_mm, 'survival': self.survs, 'survivalerr': self.surverrs,
                                    'set_experimental': set_experimental, 'num_puntos': num_ptos_plot}
                        dosis_key = find_dose_from_filename(file)
                        dict_info[f'{dosis_key}'] = dict_file
                    info_dicts.append(dict_info)
                    self.senal_info_plots_backend.emit(info_dicts)

                elif tipo_plot == 'Yield vs depth':
                    for file in os.listdir(directory):
                        path_read = os.path.join(directory, file)
                        (self.depths_mm, self.doses, self.doseerrs, self.dsbyields, self.dsbyielderrs,
                        self.lmbdas, self.lmbdaerrs, self.survs, self.surverrs) = read_output_file(path_read)
                        dict_file = {'depth': self.depths_mm, 'dsbyields': self.dsbyields,
                                    'dsbyieldserr': self.dsbyielderrs, 'set_experimental': set_experimental,
                                    'num_puntos': num_ptos_plot}
                        dosis_key = find_dose_from_filename(file)
                        dict_info[f'{dosis_key}'] = dict_file
                    info_dicts.append(dict_info)
                    self.senal_info_plots_backend.emit(info_dicts)

                elif tipo_plot == 'Lambda vs depth':
                    for file in os.listdir(directory):
                        path_read = os.path.join(directory, file)
                        (self.depths_mm, self.doses, self.doseerrs, self.dsbyields, self.dsbyielderrs,
                        self.lmbdas, self.lmbdaerrs, self.survs, self.surverrs) = read_output_file(path_read)
                        dict_file = {'depth': self.depths_mm, 'lambda': self.lmbdas, 'lambdaerr': self.lmbdaerrs,
                                    'set_experimental': set_experimental, 'num_puntos': num_ptos_plot}
                        dosis_key = find_dose_from_filename(file)
                        dict_info[f'{dosis_key}'] = dict_file
                    info_dicts.append(dict_info)
                    self.senal_info_plots_backend.emit(info_dicts)

                elif tipo_plot == 'Test plot':
                    for file in os.listdir(directory):
                        path_read = os.path.join(directory, file)
                        (self.depths_mm, self.doses, self.doseerrs, self.dsbyields, self.dsbyielderrs,
                        self.lmbdas, self.lmbdaerrs, self.survs, self.surverrs) = read_output_file(path_read)
                        dict_file = {'depth': self.depths_mm, 'survival': self.survs, 'survivalerr': self.surverrs,
                                    'set_experimental': set_experimental, 'num_puntos': num_ptos_plot}
                        dosis_key = find_dose_from_filename(file)
                        dict_info[f'{dosis_key}'] = dict_file
                    info_dicts.append(dict_info)
                    self.senal_info_plots_backend.emit(info_dicts)

                elif tipo_plot == 'Test plot 2':
                    # Leer archivo survival_dose
                    for file in os.listdir(directory):
                        if file.endswith('.db'):
                            survival, dose = read_surv_dose_file(
                                os.path.join(directory, file))
                            dict_file = {'doses': dose, 'survival': survival,
                                        'set_experimental': set_experimental, 'num_puntos': num_ptos_plot}
                            dosis_key = 0
                            print(file[-6:-3])
                            dict_info[f'{dosis_key}'] = dict_file
                    info_dicts.append(dict_info)
                    self.senal_info_plots_backend.emit(info_dicts)

    def generar_base_datos(self, event):
        # a partir del tipo de particula + seed, genera una base de datos para distintas energías/dosis
        particula = event['par_option_db'].currentText()
        db_type = event['db_type'].currentText()
        try:
            N = int(event['N_sim'].text())
        except ValueError as err:
            N = ''
        dir = event['ident'][1]
        try:
            dato_fijo = float(
                event['db_energia_dosis_fija'].text().replace(',', '.'))
        except ValueError as error:
            dato_fijo = ''

        datos_omitibles = {'nocs': event['nocs_db'].text(), 'seed': event['seed_db'].text(),
                           'ndia': event['ndia_db'].value(), 'dna': event['dna_db'].value(),
                           'cdia': event['cdia_db'].value()}
        for item in datos_omitibles.items():
            if item[1] != '':
                datos_omitibles[item[0]] = float(item[1])
            else:
                pass
        nocs = datos_omitibles['nocs']
        seed = datos_omitibles['seed']
        ndia = datos_omitibles['ndia']
        dna = datos_omitibles['dna']
        cdia = datos_omitibles['cdia']
        # energia min, max, dosis min y max
        energia_dosis = [0.5, 500, 0.1, 10]

        db_energia_dosis = [event['energy_db_min'].text(), event['energy_db_max'].text(),
                            event['dosis_db_min'].text(), event['dosis_db_max'].text()]
        for i, dato in enumerate(db_energia_dosis):
            if dato != '':
                energia_dosis[i] = float(dato)

        ke = energia_dosis[0]
        max_ke = energia_dosis[1]
        d = energia_dosis[2]
        max_d = energia_dosis[3]
        if dato_fijo != '' and db_type == 'Energy bins':
            # Dosis fija
            d = float(dato_fijo)
        elif dato_fijo != '' and db_type == 'Dose bins':
            # Energía fija
            ke = float(dato_fijo)
        E_levels = np.logspace(np.log10(ke), np.log10(max_ke), N)
        D_levels = np.linspace(d, max_d, num=N)
        cont = 0

        try:
            os.mkdir(dir)
        except:
            # se usa el mismo directorio
            cont = len([f for f in os.listdir(dir) if f.endswith('.inp')])
        if db_type == 'Energy bins':
            for E in E_levels:
                path = os.path.join(dir, f'{particula}_{cont}.inp')
                file = open(path, 'w')
                # file.write("\nSIMCON: seed={} nocs={}\nRADX: PAR={} KE={} AD={}\n\n\n".format(seed,
                #          nocs,particula,E, d))
                file.write("CELL: DNA={} NDIA={} CDIA={}\nSIMCON: seed={} nocs={}\nRADX: PAR={} KE={} AD={}\n\n\n".format(dna,
                                                                                                                          ndia, cdia, seed, nocs, particula, E, d))
                file.close()
                cont += 1
        else:
            for D in D_levels:
                path = os.path.join(dir, f'{particula}_{cont}.inp')
                file = open(path, 'w')
                # file.write("\nSIMCON: seed={} nocs={}\nRADX: PAR={} KE={} AD={}\n\n\n".format(seed,
                #           nocs,particula, ke, D))
                file.write("CELL: DNA={} NDIA={} CDIA={}\nSIMCON: seed={} nocs={}\nRADX: PAR={} KE={} AD={}\n\n\n".format(dna,
                                                                                                                          ndia, cdia, seed, nocs, particula, ke, D))
                file.close()
                cont += 1

        # lanzar simulación con los inputs
        cont_bats = 0
        for archivo in os.listdir(dir):
            if archivo.endswith('inp'):
                ruta = os.path.join(dir, archivo)
                bat_path = os.path.join(dir, f'{dir}_bat_{cont_bats}.bat')
                bat = open(bat_path, 'w')
                bat.write(fop.mcds_bat(ruta, self.path_mcds))
                bat.close()
                subprocess.call([r'{}'.format(bat_path)])
                os.remove(bat_path)
                cont_bats += 1

        # leer Yield y LET
        self.write_database(dir)

    def read_Y_LET(self, file_route):
        mcds_output = open(file_route, 'r')
        # DE LA LINEA 0 A LA 21 ESTÁN LAS CARACTERÍSTICAS DE LA CÉLULA
        # EN LOS ARCHIVOS CON .DAT, LA INFORMACIÓN DEL CAMPO DE RADIACIÓN COMIENZA EN LA LÍNEA 23
        # EN LOS ARCHIVOS SIN .DAT, LA INFORMACIÓN DE LA RADIACIÓN COMIENZA EN LA LINEA 24 Y LOS RESULTADOS EN LA 80
        # LOS ARCHIVOS SIEMPRE TIENEN 6 TABLAS
        contador = 0
        donde_tablas = []
        lista_output = []
        for linea in mcds_output:
            if 'Desired dose' in linea:
                dose = float(linea.split('     ')[0])
                if dose == 1.0:
                    file_input = file_route.replace('.out', '.inp')
                    with open(file_input, 'r') as file:
                        for line in file:
                            if 'AD=' in line:
                                dose = float(line.split('AD=')[1].split('\n')[0])
            if 'DSBcb' in linea:
                cDSBpercent = (float(linea.strip().split(" ")[0]) / 100)
            if linea[0:5] == "TABLE":
                donde_tablas.append(contador)
            lista_output.append(linea)
            contador += 1
        t2 = lista_output[donde_tablas[1]:donde_tablas[2]]
        t3 = lista_output[donde_tablas[2]:donde_tablas[3]]
        LET_filtr = lista_output[47][20:].split('  ')

        LET_cell_entry = float(LET_filtr[1])
        LET_nuc_entry = float(LET_filtr[3])
        LET_nuc_exit = float(LET_filtr[4])

        energia_filtr = lista_output[45][20:].split('  ')
        energia = float(energia_filtr[1])
        del t2[-4:]
        del t2[:5]
        del t3[-2:]
        del t3[:5]
        mcds_output.close()
        filtr2 = list(
            filter(None, (t2[-1].strip()).split(" ")))  # deja una lista con los valores aislados de la fila "total"
        filtr3 = list(
            filter(None, (t3[-1].strip()).split(" ")))
        Y = float(filtr2[1])
        Yerr = float(filtr2[2])
        lmbda = float(filtr3[1])
        lmbdaerr = float(filtr3[2])

        # add sigma1 (sDSB) and sigma2 (cDSB) for the TLK model
        sigma1 = (1 - cDSBpercent) * Y
        sigma2 = cDSBpercent * Y
        return energia, Y, Yerr, LET_cell_entry, LET_nuc_entry, LET_nuc_exit, lmbda, lmbdaerr, dose, sigma1, sigma2

    def write_database(self, path_directory):
        # lee todos los outputs en una carpeta, los ordena en un solo archivo (LET's, Y)
        base_name = os.path.basename(path_directory)
        path_database = os.path.join(path_directory, f'{base_name}.database')
        database = open(path_database, 'w')
        database.write(
            f'energia LET_cell_entry LET_nuc_entry LET_nuc_exit Yield Yielde lambda lambdae\n')
        # database.write(f'Y      Yerr    LET cell entry  LET nucleus entry   LET nucleus exit\n')
        directory_sorted = natsort.natsorted(os.listdir(path_directory))
        for filename in directory_sorted:
            if filename.endswith('.out'):
                path_file = os.path.join(path_directory, filename)
                energia, Y, Yerr, LET_cell_entry, LET_nuc_entry, LET_nuc_exit, lmbda, lmbdaerr, d, sigma1, sigma2 = self.read_Y_LET(
                    path_file)
                database.write('{} {} {} {} {} {} {} {}\n'.format(energia, LET_cell_entry, LET_nuc_entry,
                                                                  LET_nuc_exit, Y, Yerr, lmbda, lmbdaerr))
        database.close()

    def calcular_supervivencia(self, info):
        # El usuario debe haber creado previamente suficientes archivos .out
        directory = info['directory']
        ctype = info['ctype']
        directory_sorted = natsort.natsorted(os.listdir(directory))
        doses = []
        yields = []
        yieldserr = []
        lmbdas = []
        lmbdaserr = []
        survivals = []
        surverrs = []
        let = []
        for file in directory_sorted:
            path = os.path.join(directory, file)
            if file.endswith('.out'):
                energia, y, yerr, let_cell_entry, LET_nuc_entry, LET_nuc_exit, l, lerr, dose, sigma1, sigma2 = self.read_Y_LET(
                    path)
                # survival, lmbda = mech.mech_model(dose, ctype, LET_nuc_entry, y)
                if self.modelo.name == 'TLK':
                    self.modelo.add_params(sigma1, sigma2, dose, 0, ctype)
                else:
                    self.modelo.add_params(ctype, dose, 0, y, yerr, l, lerr, d=10)
                survival, survivalerr = self.modelo.predict()
                #survival, survivalerr = mech.mech_model_wlmbda_uncert(
                #    ctype, dose, 0, y, yerr, l, lerr, self.modelo)
                doses.append(dose)
                try:
                    yields.append(y/dose)
                    yieldserr.append(yerr/dose)
                    lmbdas.append(l)
                    lmbdaserr.append(lerr)
                except ZeroDivisionError as error:
                    # dose is zero
                    yields.append(0)
                    yieldserr.append(0)
                    lmbdas.append(0)
                    lmbdaserr.append(0)
                survivals.append(survival)
                surverrs.append(survivalerr)
        with open(os.path.join(directory, f'survival_dose_{ctype}_{self.modelo.name}.db'), 'w') as file:
            file.write(
                'Survival Survivalerr Dose Yield Yielderr Lambda Lambdaerr\n')
            for (s, serr, d, y, yerr, l, lerr) in zip(survivals, surverrs, doses, yields,
                                                      yieldserr, lmbdas, lmbdaserr):
                file.write('{} {} {} {} {} {} {}\n'.format(
                    s, serr, d, y, yerr, l, lerr))

    def info_ciclo_celular(self, event):
        if event:
            self.g1 = True
        else:
            self.g1 = False

    def modelo_escogido(self, event):
        if event == 'Wang':
            self.modelo = mech.Modelo_Wang()
        elif event == 'Wang-Sophia':
            self.modelo = mech.Modelo_Wang_params_sophia()
        elif event == 'TLK':
            self.modelo = mech.TLK_model()
        elif event == 'ML':
            self.modelo = mech.Modelo_ML()
        else:
            # different parameters for Wang's model
            if self.modelo.name != 'Wang':
                self.modelo = mech.Modelo_Wang()

    def new_wang_params(self, event):
        mu_x = event['mu_x'].value()
        mu_x_e = event['mu_x_e'].value()
        mu_y = event['mu_y'].value()
        mu_y_e = event['mu_y_e'].value()
        zeta = event['zeta'].value()
        zeta_e = event['zeta_e'].value()
        xi = event['xi'].value()
        xi_e = event['xi_e'].value()
        eta_1 = event['eta_1'].value()
        eta_1_e = event['eta_1_e'].value()
        eta_infty = event['eta_infty'].value()
        eta_infty_e = event['eta_infty_e'].value()

        params = {'mu_x': ufloat(mu_x, mu_x_e),
                  'mu_y': ufloat(mu_y, mu_y_e),
                  'zeta': ufloat(zeta, zeta_e),
                  'xi': ufloat(xi, xi_e),
                  'eta_1': ufloat(eta_1, eta_1_e),
                  'eta_infty': ufloat(eta_infty, eta_infty_e)}

        cell = event['new_cell'].text()
        if cell == '':
            # change the parameters of an existing cell
            celltype = event['change_cell_params'].currentText()
            self.modelo.add_cell_params(celltype, params)
        else:
            # define a new cell line with the given parameters
            self.modelo.add_cell_params(cell, params)
            self.signal_new_cell.emit(cell)

    def PIDE_give_data(self, event):
        try:
            pide_path = 'PIDE3.2.csv'
            pubnames = read_pubnames_PIDE(pide_path)
            self.senal_PIDE_pubnames.emit(pubnames)
        except FileNotFoundError as error:
            print('Error: You must select a valid PIDE file')

    def PIDE_receive_user_data(self, event):
        option = event['PIDE_option']
        if option == '#ExpID':
            pide_to_set_experimental(0, event)
        elif option == 'Range of #ExpIDs':
            pide_to_set_experimental(1, event)
        elif option == 'Publication name':
            pide_to_set_experimental(2, event)
        elif option == 'Cell line':
            pide_to_set_experimental(3, event)
        elif option == 'All':
            pide_to_set_experimental(4, event)
    
    def generar_base_datos_pide(self, event):
        cell = event['PIDE_Cells_db'].currentText()
        self.pide_cell_to_mcds(cell, event)

    def add_database_from_folder(self, path):
        self.write_database(path)

    def pide_cell_to_mcds(self, cell, info, pide_path='PIDE3.2.csv', ion_data='PIDE3.2_IonRawData.csv'):
        pide_ion = pd.read_csv(ion_data, sep=';', header=None)
        pide = pd.read_csv(pide_path, sep=';')
        pide_header = ['ExpID', 'Publication', 'PublicationName', 'IonExp', 'PhotonExp']
        n_dose_surv = (pide_ion.shape[1] - len(pide_header)) // 2
        for i in range(n_dose_surv):
            pide_header.append(f'D_{i}')
            pide_header.append(f'S_{i}')
        
        pide_ion.columns = pide_header
        pide_cell = pide[pide['Cells'] == cell]
        expids = pide_cell.ExpID.to_numpy().tolist()
        dir = 'PIDE_database_outputs'
        try:
            os.mkdir(dir)
        except FileExistsError as error:
            pass
        for expid in expids:
            doses = []
            survs = []
            row = pide[pide['ExpID'] == expid]
            row_dose_surv = pide_ion[pide_ion['ExpID'] == expid]
            columns = row_dose_surv.columns.to_numpy()
            dose_surv = [columns[x].tolist() for x in row_dose_surv.notna().to_numpy()]
            # Se tienen los nombres de las columnas que tienen valores distintos a NaN
            dose_surv = list(zip(dose_surv[0][5:][::2], dose_surv[0][5:][1::2]))
            for d_s in dose_surv:
                d = pide_ion[pide_ion['ExpID'] == expid].loc[:, d_s[0]].to_numpy()[0]
                s = pide_ion[pide_ion['ExpID'] == expid].loc[:, d_s[1]].to_numpy()[0]
                if d < 0 or s < 0 or s > 1.1:
                    pass
                else:
                    doses.append(d)
                    survs.append(s)
            pubname = row.PublicationName.iloc[0]
            particula = row.Ion.iloc[0]
            # verificar que la particula sea < 56Fe (máximo válido para MCDS)
            num_particula = [int(i) for i in [*particula] if i.isdigit()]
            z_particula = int(''.join(map(str, num_particula)))
            if z_particula <= 56:
                dna = float(row.DNAcontent.iloc[0].replace(',', '.'))
                datos_omitibles = {'nocs': info['nocs_pide_db'].text(), 'seed': info['seed_pide_db'].text(),
                                'ndia': info['ndia_pide_db'].value(),
                                'cdia': info['cdia_pide_db'].value()}
                for item in datos_omitibles.items():
                    if item[1] != '':
                        datos_omitibles[item[0]] = float(item[1])
                    else:
                        pass
                nocs = datos_omitibles['nocs']
                seed = datos_omitibles['seed']
                ndia = datos_omitibles['ndia']
                cdia = datos_omitibles['cdia']
                ke = float(row.Energy.iloc[0].replace(',', '.'))
                D_levels = np.array(doses)
                cont = 0

                for D in D_levels:
                    path = os.path.join(dir, f'{pubname}_{expid}_{cont}.inp')
                    file = open(path, 'w')
                    file.write("CELL: DNA={} NDIA={} CDIA={}\nSIMCON: seed={} nocs={}\nRADX: PAR={} KE={} AD={}\n\n\n".format(dna,
                                                                                                                            ndia, cdia, seed, nocs, particula, ke, D))
                    file.close()
                    cont += 1
        cont_bats = 0
        for archivo in os.listdir(dir):
            if archivo.endswith('inp'):
                ruta = os.path.join(dir, archivo)
                bat_path = os.path.join(dir, f'{dir}_bat_{cont_bats}.bat')
                bat = open(bat_path, 'w')
                bat.write(fop.mcds_bat(ruta, self.path_mcds))
                bat.close()
                subprocess.call([r'{}'.format(bat_path)])
                os.remove(bat_path)
                cont_bats += 1

            # leer Yield y LET
        self.write_database(dir)
        
    
    def PIDE_data_ML(self, event):
        dict_ml = pide_expid_info(event)
        self.signal_PIDE_ML_data.emit(dict_ml)
    
    def calculate_survival_ML(self, event):
        energy = event['energy_ML'].value()
        charge = event['charge_ML'].value()
        dna = event['dna_ML'].value()
        ion = event['ion_ML'].currentText()
        cell = event['cell_ML'].currentText()
        cellclass = event['cell_class_ML'].currentText()
        cellorigin = event['cell_origin_ML'].currentText()
        cellcycle = event['cell_cycle_ML'].currentText()
        irr_cond = event['irr_cond_ML'].currentText()

        try:
            doses_range = event['dose_ML'].text()
            doses_range = doses_range.split('-')
            doses_range = [int(i) for i in doses_range]
            doses = np.arange(doses_range[0], doses_range[1], 0.5)
            #doses = list(range(doses[0], doses[1]+1))
        except IndexError:
            print('Error: You must enter a valid dose range')
            doses = False

        if cellclass == 'Normal':
            cellclass = 'n'
        else:
            cellclass = 't'
        if cellorigin == 'human':
            cellorigin = 'h'
        else:
            cellorigin = 'r'
        if irr_cond == 'Monoenergetic':
            irr_cond = 'm'
        else:
            irr_cond = 's'
        # pasar las dosis a lista (rango de dosis)
        self.modelo.add_params(doses, energy, charge, dna, ion, cell, cellclass, cellorigin, cellcycle, irr_cond)
        predictions = self.modelo.predict()

        directory = os.path.join(os.getcwd(), 'ML_model')
        with open(os.path.join(directory, f'survival_dose_{cell}_{self.modelo.name}.db'), 'w') as file:
            file.write('Survival_ML Dose\n')
            for (s, d) in zip(predictions, doses):
                file.write('{} {}\n'.format(s, d))
        

######### Fin de la clase ############################

def read_D_Y_lmbda(path_file):
    mcds_output = open(path_file, 'r')
    contador = 0
    donde_tablas = []
    lista_output = []
    for linea in mcds_output:
        if 'Desired dose' in linea:
            dose = float(linea.split('     ')[0])
        if linea[0:5] == "TABLE":
            donde_tablas.append(contador)
        lista_output.append(linea)
        contador += 1
    t2 = lista_output[donde_tablas[1]:donde_tablas[2]]
    t3 = lista_output[donde_tablas[2]:donde_tablas[3]]

    del t2[-4:]
    del t2[:5]
    del t3[-2:]
    del t3[:5]
    mcds_output.close()
    filtr2 = list(
        filter(None, (t2[-1].strip()).split(" ")))  # deja una lista con los valores aislados de la fila "total"
    filtr3 = list(
        filter(None, (t3[-1].strip()).split(" ")))
    Y = float(filtr2[1])
    Yerr = float(filtr2[2])
    lmbda = float(filtr3[1])
    lmbdaerr = float(filtr3[2])
    return dose, Y, Yerr, lmbda, lmbdaerr


def read_surv_dose_file(path):
    file = open(path, 'r')
    next(file)
    survivals = []
    surverr = []
    doses = []
    for line in file:
        survivals.append(float(line.split(' ')[0]))
        try:
            doses.append(float(line.split(' ')[2]))
            surverr.append(float(line.split(' ')[1]))
        except IndexError as error:
            doses.append(float(line.split(' ')[1]))
    return np.asarray(survivals), np.asarray(surverr), np.asarray(doses)


def read_output_file(path):
    # Recibe un archivo con datos procesados, guarda los valores (despues usados para graficar)
    data = open(path, 'r')
    next(data)
    depths = []
    doses = []
    doseerrs = []
    dsbyields = []
    dsbyielderrs = []
    lmbdas = []
    lmbdaerrs = []
    survs = []
    surverrs = []
    for line in data:
        depths.append(float(line.split(' ')[0]))
        doses.append(float(line.split(' ')[1]))
        doseerrs.append(float(line.split(' ')[2]))
        dsbyields.append(float(line.split(' ')[3]))
        dsbyielderrs.append(float(line.split(' ')[4]))
        lmbdas.append(float(line.split(' ')[5]))
        lmbdaerrs.append(float(line.split(' ')[6]))
        survs.append(float(line.split(' ')[7]))
        surverrs.append(float(line.split(' ')[8]))

    (depths, doses, doseerrs, dsbyields, dsbyielderrs,
     lmbdas, lmbdaerrs, survs, surverrs) = (np.asarray(depths), np.asarray(doses), np.asarray(doseerrs),
                                            np.asarray(dsbyields), np.asarray(
                                                dsbyielderrs), np.asarray(lmbdas),
                                            np.asarray(lmbdaerrs), np.asarray(survs), np.asarray(surverrs))

    return depths, doses, doseerrs, dsbyields, dsbyielderrs, lmbdas, lmbdaerrs, survs, surverrs


def find_dose_from_filename(filename):
    # identifica dosis de archivo tipo 'proc_prueba_corrientes_spectrum_data_1.5Gy' u otros que terminen en 'Gy'
    file = filename[:-2]
    dose = []
    for s in reversed(file):
        if s != '_':
            dose.append(s)
        else:
            break
    dose.reverse()
    return float(''.join(dose))


def read_set_experimental(file):
    x = []
    y = []
    data = open(file, 'r')
    for line in data:
        line = line.replace(';', '')
        line_list = line.split(' ')
        try:
            x.append(float(line_list[0]))
            y.append(float(line_list[1]))
        except ValueError as error:
            # hay que cambiar las comas (,) por puntos (.) en los datos
            x.append(float(line_list[0].replace(',', '.')))
            y.append(float(line_list[1].replace(',', '.')))
    return x, y


def all_doses_and_surv(directory):
    all_doses = []
    all_surv = []
    all_surverr = []
    for file in os.listdir(directory):
        # asumiendo que el directorio tiene exclusivamente archivos output y nada raro entremedio
        (depths, doses, doseerrs, dsbyields, dsbyielderrs, lmbdas,
         lmbdaerrs, survs, surverrs) = read_output_file(os.path.join(directory, file))
        all_doses.extend(doses)
        all_surv.extend(survs)
        all_surverr.extend(surverrs)
    all_doses, all_surv, all_surverr = np.asarray(
        all_doses), np.asarray(all_surv), np.asarray(all_surverr)
    return all_doses, all_surv, all_surverr


def read_pubnames_PIDE(pide_path):
    pide = pd.read_csv(pide_path, sep=';')
    pubnames = pide.PublicationName.unique().tolist()
    return pubnames


def pide_expid_info(expid):
    pide = pd.read_csv('PIDE3.2.csv', sep=';')
    row = pide[pide['ExpID'] == expid]
    dict_ml = {'Energy': float(row.Energy.iloc[0].replace(',', '.')),
               'Charge': int(row.Charge.iloc[0]),
               'DNAContent': float(row.DNAcontent.iloc[0].replace(',', '.')),
               'Ion': row.Ion.iloc[0],
               'Cell': row.Cells.iloc[0],
               'CellClass': row.CellClass.iloc[0],
               'CellOrigin': row.CellOrigin.iloc[0],
               'CellCycle': row.CellCycle.iloc[0]}
    return dict_ml

def pide_single_expid(expid, pide):
    doses = []
    survs = []
    row = pide[pide['ExpID'] == expid]
    columns = row.columns.to_numpy()
    dose_surv = [columns[x].tolist() for x in row.notna().to_numpy()]
    # Se tienen los nombres de las columnas que tienen valores distintos a NaN
    dose_surv = list(zip(dose_surv[0][5:][::2], dose_surv[0][5:][1::2]))
    for d_s in dose_surv:
        d = pide[pide['ExpID'] == expid].loc[:, d_s[0]].to_numpy()[0]
        s = pide[pide['ExpID'] == expid].loc[:, d_s[1]].to_numpy()[0]
        if d < 0 or s < 0 or s > 1.1:
            pass
        else:
            doses.append(d)
            survs.append(s)
    pubname = str(row.PublicationName.iloc[0])
    output_file = f'{pubname}_{expid}.txt'
    try:
        os.mkdir('PIDE_outputs')
    except FileExistsError as error:
        pass
    with open(os.path.join('PIDE_outputs', output_file), 'w') as file:
        for dose, surv in zip(doses, survs):
            file.write(f'{dose}; {surv}\n')


def pide_expids_from_pubname(pubname, pide):
    expids = pide[pide['PublicationName'] == pubname].ExpID.to_numpy()
    return expids

def pide_expids_from_cell(cell, pide):
    expids = pide[pide['Cells'] == cell].ExpID.to_numpy()
    return expids

def pide_to_set_experimental(option, info, pide_path='PIDE3.2.csv', ion_data='PIDE3.2_IonRawData.csv'):
    # funcion que convierte datos PIDE a formato de set experimental para graficar
    pide = pd.read_csv(ion_data, sep=';', header=None)
    pide_original = pd.read_csv(pide_path, sep=';')
    #if ion_data:
    pide_header = ['ExpID', 'Publication', 'PublicationName', 'IonExp', 'PhotonExp']
    #else:
    #    pide_header = ['ExpID', 'Publication', 'PublicationName', 'PhotonExp']
    
    n_dose_surv = (pide.shape[1] - len(pide_header)) // 2
    for i in range(n_dose_surv):
        pide_header.append(f'D_{i}')
        pide_header.append(f'S_{i}')
    
    pide.columns = pide_header
    if option == 0:
        # single expid
        expid = int(info['PIDE_ID'].text())
        pide_single_expid(expid, pide)
    elif option == 1:
        # range
        range_id = info['PIDE_range'].text()
        range_id = range_id.split('-')
        range_id = [int(i) for i in range_id]
        range_id_list = list(range(range_id[0], range_id[1]+1))
        for id in range_id_list:
            pide_single_expid(id, pide)
    elif option == 2:
        #pubnames
        pubnames = info['PIDE_PubNames'].currentData()
        #pubnames = pubnames.split(', ')
        for pubname in pubnames:
            pide_expids = pide_expids_from_pubname(pubname, pide)
            for expid in pide_expids:
                pide_single_expid(expid, pide)
    elif option == 3:
        # Cell line
        cell = info['PIDE_Cells'].currentText()
        pide_expids = pide_expids_from_cell(cell, pide_original)
        for expid in pide_expids:
            pide_single_expid(expid, pide)
    else:
        # all
        expids = pide.ExpID.to_numpy().tolist()
        for id in expids:
            pide_single_expid(id, pide)
