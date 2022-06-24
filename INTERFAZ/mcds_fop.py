import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import warnings
import sys
import subprocess
import os
import shutil
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)
from scipy import stats

import random



def mcds_fop(t1, t2, t3, t4, t5, t6):
    # Transformo un archivo de texto de lista sin headers ni notas ni adornos (la funcion mcds_of se encarga de quitar headers notas y adornos)
    # en una lista de tablas; cada tabla es representada como una lista lista_tabla=[[fila 1],[fila 2],...];
    # [fila i]=[elemento(fila i col 1),elemento(fila i,col 2),...]
    # en mcds_of quito los adornos a la lista y llamo a mcds_fop para que convierta esas tablas "desnudas" en listas de listas.

    lista_t1 = []
    lista_t2 = []
    lista_t3 = []
    lista_t4 = []
    lista_t5 = []
    lista_t6 = []
    for i in t1:
        lista_t1.append([float([txt.replace('---', '0') for txt in i.split()][0]),
                         [txt.replace('---', '0') for txt in i.split()][1]])
    for (a, b, c, d, e) in zip(t2, t3, t4, t5, t6):
        lista_a = a.split()
        lista_b = b.split()
        lista_c = c.split()
        lista_d = d.split()
        lista_e = e.split()
        lista_nna = [float(x) for x in [txt.replace('---', '0') for txt in lista_a]]
        lista_nnb = [float(x) for x in [txt.replace('---', '0') for txt in lista_b]]
        lista_nnc = [float(x) for x in [txt.replace('---', '0') for txt in lista_c]]
        lista_nnd = [float(x) for x in [txt.replace('---', '0') for txt in lista_d]]
        lista_nne = [float(x) for x in [txt.replace('---', '0') for txt in lista_e]]

        lista_t2.append(lista_nna)
        lista_t3.append(lista_nnb)
        lista_t4.append(lista_nnc)
        lista_t5.append(lista_nnd)
        lista_t6.append(lista_nne)
    print(lista_t2[-1])
    print(lista_t3[-1])
    return [lista_t1, lista_t2, lista_t3, lista_t4, lista_t5, lista_t6]
    # la función regresa una lista con las tablas (que son listas de listas (matrices))


def mcds_of(file_route):
    mcds_output = open(file_route, 'r')

    # DE LA LINEA 0 A LA 21 ESTÁN LAS CARACTERÍSTICAS DE LA CÉLULA
    # EN LOS ARCHIVOS CON .DAT, LA INFORMACIÓN DEL CAMPO DE RADIACIÓN COMIENZA EN LA LÍNEA 23
    # EN LOS ARCHIVOS SIN .DAT, LA INFORMACIÓN DE LA RADIACIÓN COMIENZA EN LA LINEA 24 Y LOS RESULTADOS EN LA 80
    # LOS ARCHIVOS SIEMPRE TIENEN 6 TABLAS
    contador = 0
    donde_tablas = []
    lista_output = []
    for linea in mcds_output:
        if linea[0:5] == "TABLE":
            donde_tablas.append(contador)
        lista_output.append(linea)
        contador += 1

    t1 = lista_output[donde_tablas[0]:donde_tablas[1]]
    t2 = lista_output[donde_tablas[1]:donde_tablas[2]]
    t3 = lista_output[donde_tablas[2]:donde_tablas[3]]
    t4 = lista_output[donde_tablas[3]:donde_tablas[4]]
    t5 = lista_output[donde_tablas[4]:donde_tablas[5]]
    t6 = lista_output[donde_tablas[5]:]

    # A LA TABLA 1 QUITAR LAS PRIMERAS 3 LINEAS Y LAS ÚLTIMAS 2
    del t1[0:3]
    del t1[-2:]
    # A LA TABLA 2 HAY QUE QUITAR LAS 5 LINEAS FINALES Y 5 INICIALES
    del t2[-5:]
    del t2[:5]
    # A LA TABLA 3 Y 4 TENGO QUE QUITAR LAS 3 LINEAS FINALES Y LAS 5 INICIALES
    del t3[-3:]
    del t3[:5]
    del t4[-3:]
    del t4[:5]
    # A LA TABLA 5 y 6 TENGO QUE QUITAR 4 LINEAS FINALES Y 5 INICIALES
    del t5[-5:]
    del t5[:5]
    del t6[-4:]
    del t6[:5]

    # Estas lineas crean archivos guardando cada tabla por separado, están comentadas para no llenar de archivos la carpeta.

    # nombre_archivo=file_route.split('\\')[-1]
    # output_tabla_1=open("percent_cluster_yield_{}".format(nombre_archivo),'w')
    # output_tabla_1.writelines((t1))
    # output_tabla_2=open("clusters_per_cell_{}".format(nombre_archivo),'w')
    # output_tabla_2.writelines((t2))
    # output_tabla_3=open("clusters_per_cell_per_track_{}".format(nombre_archivo),'w')
    # output_tabla_3.writelines((t3))
    # output_tabla_4=open("cluster_length_{}".format(nombre_archivo),'w')
    # output_tabla_4.writelines((t4))
    # output_tabla_5=open("density_lesions_{}".format(nombre_archivo),'w')
    # output_tabla_5.writelines((t5))
    # output_tabla_6=open("cluster_sb_percentage_{}".format(nombre_archivo),'w')
    # output_tabla_6.writelines((t6))
    mcds_output.close()
    # output_tabla_1.close()
    # output_tabla_2.close()
    # output_tabla_3.close()
    # output_tabla_4.close()
    # output_tabla_5.close()
    # output_tabla_6.close()

    # Hasta aquí t1...t6, son strings que contienen las tablas sin headers ni notas, solo los valores.
    # con mcds_fop transformo esa tabla sin headers ni notas en listas para cada tabla; cada tabla es una lista de listas
    # cada  lista dentro de la lista de tabla es una fila de la tabla y el índice de sus elementos corresponden a su índice de columna
    return mcds_fop(t1, t2, t3, t4, t5, t6)


def table_to_array(table):
    ar = []
    er = []
    for fila in table:
        ar.append([fila[1], fila[3], fila[5], fila[7]])
        er.append([fila[2], fila[4], fila[6], fila[8]])
    return [np.ravel(np.array(ar)), np.ravel(np.array(er))]


def t_eff_len(table):
    list.reverse(table)
    c = 0
    l = len(table)
    for fila in table:
        if sum(fila[1:len(fila)]) == 0:
            c += 1
        else:
            break
    list.reverse(table)
    # cuenta el largo efectivo de los datos distintos de 0 en una tabla.
    return l - c


def plot_table(tabla, titulo):
    # plot de barras 3D de una tabla
    warnings.filterwarnings("ignore")
    table_eff_len = t_eff_len(tabla)
    fig = plt.figure(figsize=(10, 10))
    ax1 = Axes3D(fig)

    top = table_to_array(tabla[0:table_eff_len])[
        0]  # TOP ES UNA ARRAY QUE CADA 4 ESPACIOS (POR EL LARGO DE _x) PASA A LA SIGUIENTE FILA, PUEDO CONSTRUIR UN ARRAY DE ESTA FORMA CON LA TABLA MANUALMENTE con la idea en mente: tabla[y][x]
    _x = np.array([1, 2, 3, 4])
    _y = np.arange(table_eff_len)
    _xx, _yy = np.meshgrid(_x, _y)
    x, y = _xx.ravel(), _yy.ravel()
    bottom = np.zeros_like(top)
    width = depth = 1

    ax1.bar3d(x, y, bottom, width, depth, top, shade=True)
    ax1.set_zlabel(titulo)
    # ax1.xaxis.set_major_locator(mticker.MaxNLocator(4))
    # ticks_loc = ax1.get_xticks().tolist()
    # ax1.xaxis.set_major_locator(mticker.FixedLocator(ticks_loc))
    ax1.set_xticklabels(['', '', 'DSB', '', 'SSB', '', 'Otros', '', 'Todos'])
    # ax1.w_xaxis.set_ticklabels([ 'DSB', 'SSB', 'Otros', 'Todos',''])
    ax1.set_xlabel('Tipo de daño del cluster')
    ax1.set_ylabel('Cantidad de lesiones en el cluster')
    return


def scat2d(var1, var2, tab1, tab2):
    # PLOT de dispersión de dos variables, pueden pertenecer a tablas distintas, el valor que las conecta es la cantidad
    # de lesiones del cluster al que pertenecen, esto podría mejorarse ya que la interpretación del plot no es muy clara
    fig, ax = plt.subplots()
    tablen1 = t_eff_len(tab1)
    tablen2 = t_eff_len(tab2)
    if tablen1 >= tablen2:
        tablen = tablen1
    else:
        tablen = tablen2
    if var1 == "N° de lesiones del cluster" and var2 == "N° de lesiones del cluster":
        for col in ['DSB', 'SSB', 'Otros']:
            if col == 'DSB':
                x, y = [[], []]
                for fila in tab1[0:tablen]:
                    x.append(fila[0])
                for fila in tab2[0:tablen]:
                    y.append(fila[0])
                ax.scatter(x, y, label=col, marker="D")
            elif col == 'SSB':
                x, y = [[], []]
                for fila in tab1[0:tablen]:
                    x.append(fila[0])
                for fila in tab2[0:tablen]:
                    y.append(fila[0])
                ax.scatter(x, y, label=col, marker="d")
            elif col == 'Otros':
                x, y = [[], []]
                for fila in tab1[0:tablen]:
                    x.append(fila[0])
                for fila in tab2[0:tablen]:
                    y.append(fila[0])
                ax.scatter(x, y, label=col, marker="x")

    elif var1 == "N° de lesiones del cluster":
        for col in ['DSB', 'SSB', 'Otros']:
            if col == 'DSB':
                x, y = [[], []]
                for fila in tab1[0:tablen]:
                    x.append(fila[0])
                for fila in tab2[0:tablen]:
                    y.append(fila[1])
                ax.scatter(x, y, label=col, marker="D")
            elif col == 'SSB':
                x, y = [[], []]
                for fila in tab1[0:tablen]:
                    x.append(fila[0])
                for fila in tab2[0:tablen]:
                    y.append(fila[3])
                ax.scatter(x, y, label=col, marker="d")
            elif col == 'Otros':
                x, y = [[], []]
                for fila in tab1[0:tablen]:
                    x.append(fila[0])
                for fila in tab2[0:tablen]:
                    y.append(fila[5])
                ax.scatter(x, y, label=col, marker="x")
    elif var2 == "N° de lesiones del cluster":
        for col in ['DSB', 'SSB', 'Otros']:
            if col == 'DSB':
                x, y = [[], []]
                for fila in tab1[0:tablen]:
                    x.append(fila[1])
                for fila in tab2[0:tablen]:
                    y.append(fila[0])
                ax.scatter(x, y, label=col, marker="D")
            elif col == 'SSB':
                x, y = [[], []]
                for fila in tab1[0:tablen]:
                    x.append(fila[3])
                for fila in tab2[0:tablen]:
                    y.append(fila[0])
                ax.scatter(x, y, label=col, marker="d")
            elif col == 'Otros':
                x, y = [[], []]
                for fila in tab1[0:tablen]:
                    x.append(fila[5])
                for fila in tab2[0:tablen]:
                    y.append(fila[0])
                ax.scatter(x, y, label=col, marker="x")
    else:
        for col in ['DSB', 'SSB', 'Otros']:
            if col == 'DSB':
                x, y = [[], []]
                for fila in tab1[0:tablen]:
                    x.append(fila[1])
                for fila in tab2[0:tablen]:
                    y.append(fila[1])
                ax.scatter(x, y, label=col, marker="D")
            elif col == 'SSB':
                x, y = [[], []]
                for fila in tab1[0:tablen]:
                    x.append(fila[3])
                for fila in tab2[0:tablen]:
                    y.append(fila[3])
                ax.scatter(x, y, label=col, marker="d")
            elif col == 'Otros':
                x, y = [[], []]
                for fila in tab1[0:tablen]:
                    x.append(fila[5])
                for fila in tab2[0:tablen]:
                    y.append(fila[5])
                ax.scatter(x, y, label=col, marker="x")
    ax.legend()
    ax.grid(True)
    ax.set_xlabel(var1)
    ax.set_ylabel(var2)
    return


def mcds_inp(inp_cell_dna="", inp_cell_ndia="", inp_cell_cdia="", inp_cell_wem="", inp_simcon_seed="",
             inp_simcon_nocs="", inp_radx_fn="",
             inp_radx_par="", inp_radx_ke="", inp_radx_meva="", inp_radx_ad="", inp_evo2_po2="", inp_evo2_mmhg="",
             inp_evo2_m0="", inp_evo2_k="",
             inp_evo2_q="", inp_evo2_r="", inp_mcds_fbl="", inp_dmso_conc="", inp_dmso_fnsd="", inp_dmso_chmx=""):
    # función toma las variables de input que quieran especificarse para correr una simulación de MCDS y retorna un string
    # que ha de ser escrito en un archivo .inp

    if inp_cell_dna != "":
        cell_dna = " DNA=" + inp_cell_dna
    else:
        cell_dna = ""
    if inp_cell_ndia != "":
        cell_ndia = " NDIA=" + inp_cell_ndia
    else:
        cell_ndia = ""
    if inp_cell_cdia != "":
        cell_cdia = " CDIA=" + inp_cell_cdia
    else:
        cell_cdia = ""
    if inp_cell_wem != "":
        cell_wem = " WEM=" + inp_cell_wem
    else:
        cell_wem = ""
    if inp_cell_dna != "" or inp_cell_ndia != "" or inp_cell_cdia != "" or inp_cell_wem != "":
        inp_cell = "CELL:" + cell_dna + cell_ndia + cell_cdia + cell_wem
    else:
        inp_cell = ""

    if inp_simcon_seed != "":
        simcon_seed = " seed=" + inp_simcon_seed
    else:
        simcon_seed = ""
    if inp_simcon_nocs != "":
        simcon_nocs = " nocs=" + inp_simcon_nocs
    else:
        simcon_nocs = ""
    if inp_simcon_seed != "" or inp_simcon_nocs != "":
        inp_simcon = "SIMCON:" + simcon_seed + simcon_nocs
    else:
        inp_simcon = ""

    if inp_radx_fn != "":
        radx_fn = " FN=" + inp_radx_fn
    else:
        radx_fn = ""

    if inp_radx_par != "":
        radx_par = " PAR=" + inp_radx_par
    else:
        radx_par = ""

    if inp_radx_ke != "":
        radx_ke = " KE=" + inp_radx_ke
    else:
        radx_ke = ""

    if inp_radx_meva != "":
        radx_meva = " MeV/A=" + inp_radx_meva
    else:
        radx_meva = ""

    if inp_radx_ad != "":
        radx_ad = " AD=" + inp_radx_ad
    else:
        radx_ad = ""

    if inp_radx_fn != "" or inp_radx_par != "" or inp_radx_ke != "" or inp_radx_meva != "" or inp_radx_ad != "":
        inp_radx = "RADX:" + radx_fn + radx_par + radx_ke + radx_meva + radx_ad
    else:
        inp_radx = ""

    if inp_evo2_po2 != "":
        evo2_po2 = " pO2=" + inp_evo2_po2
    else:
        evo2_po2 = ""

    if inp_evo2_mmhg != "":
        evo2_mmhg = " mmHg=" + inp_evo2_mmhg
    else:
        evo2_mmhg = ""

    if inp_evo2_m0 != "":
        evo2_m0 = " m0=" + inp_evo2_m0
    else:
        evo2_m0 = ""

    if inp_evo2_k != "":
        evo2_k = " k=" + inp_evo2_k
    else:
        evo2_k = ""

    if inp_evo2_q != "":
        evo2_q = " q=" + inp_evo2_q
    else:
        evo2_q = ""

    if inp_evo2_r != "":
        evo2_r = " r=" + inp_evo2_r
    else:
        evo2_r = ""

    if inp_evo2_po2 != "" or inp_evo2_mmhg != "" or inp_evo2_m0 != "" or inp_evo2_k != "" or inp_evo2_q != "" or inp_evo2_r:
        inp_evo2 = "EVO2:" + evo2_po2 + evo2_mmhg + evo2_m0 + evo2_k + evo2_q + evo2_r
    else:
        inp_evo2 = ""

    if inp_mcds_fbl != "":
        mcds_fbl = " fbl=" + inp_mcds_fbl
    else:
        mcds_fbl = ""

    if inp_mcds_fbl != "":
        inp_mcds = "MCDS:" + mcds_fbl
    else:
        inp_mcds = ""

    if inp_dmso_conc != "":
        dmso_conc = " CONC=" + inp_dmso_conc
    else:
        dmso_conc = ""

    if inp_dmso_fnsd != "":
        dmso_fnsd = " FNSD=" + inp_dmso_fnsd
    else:
        dmso_fnsd = ""

    if inp_dmso_chmx != "":
        dmso_chmx = " CHMX=" + inp_dmso_chmx
    else:
        dmso_chmx = ""

    if inp_dmso_conc != "" or inp_dmso_fnsd != "" or inp_dmso_chmx != "":
        inp_dmso = "DMSO:" + dmso_conc + dmso_fnsd + dmso_chmx
    else:
        inp_dmso = ""

    return "{}\n{}\n{}\n{}\n{}\n{}".format(inp_cell, inp_simcon, inp_radx, inp_evo2, inp_mcds, inp_dmso)


def mcds_bat(ruta_archivo, ruta_mcds="D:\\Universidad\\MSc_inv\\Russomando\\mcds\\bin\\mcds.exe"):
    # Función recibe el nombre (o ruta, si no está en la misma carpeta (cwd)) de un archivo y retorna un string
    # que ha de ser escrito en un archivo .bat, al correr este archivo se corre la simulación (esto funciona en windows,
    # para linux me imagino que hay que cambiar esta parte por un archivo .sh ejecutable, sin embargo, esta forma de ejecutar
    # tan complicada es necesaria en windows. En linux probablemente se puede ejecutar desde la terminal llamando al archivo y al programa).
    write_this = "@echo off\ncls\n\nECHO MCDS Automated many simulations for "\
                 + ruta_archivo + "\nset MCDS=\"" + ruta_mcds + "\"\nECHO %path%\n\n%MCDS% " + \
                 "\"" + ruta_archivo + "\"" + "\n\nset MCDS="
    return write_this


##INTERFAZ DE PLOTEO

def mcds_plt(file_route):
    # Programa permite elegir de manera interactiva y rápida uno o más plots para visualizar los datos de las tablas
    print("Bienvenido a la cuasi interfaz gráfica para MCDS\n")
    print("Este programa toma como input el output de MCDS y lo procesa para graficar los resultados de la simulación")
    # file_route = input("Ingrese la ruta al archivo de output MCDS (x.out): ")  # ruta mono_e.out => F:\Universidad\2020'2\Fisica Medica\Russomando\mcds\sample\Autoejemplo\mono_e.out
    while True:
        try:
            tablas = mcds_of(file_route)
            break
        except:
            print("Error en la especificación de la ruta, intente nuevamente")
            file_route = input("Ingrese la ruta al archivo de output MCDS (x.out): ")
    while True:
        print(
            "Seleccione que tipo de gráfico desea visualizar o ingrese <q> para terminar:\n 1. Gráfico de barras 3D\n 2. Dispersión 2D \n 3. Dispersión 3D\n 4. Curva")
        error = 1
        while error == 1:
            selec = input("Selección: ")
            if selec == "1" or selec == "2" or selec == "3":
                error = 0
            elif selec == "q":
                sys.exit()
            elif selec == "q":
                sys.exit()
            else:
                print("Error, ingrese su selección como entero o ingrese <q> para salir")
        ####PLOTEO DE HISTOGRAMA
        if selec == "1":
            while True:
                print(
                    "Seleccione la variable a analizar:\n 1. N° de clusters por célula\n 2. N° de clusters por célula por track \n 3. Largo de clusters [bp]\n 4. Densidad de lesiones [lesiones/nucleótido]\n 5. Composición de cluster [%SB por cluster]\n 6. Todos\n 7. Volver")
                selec_hist = input("Selección: ")
                if selec_hist == "1":
                    plot_table(tablas[1], "N° de clusters por célula")
                    plt.show()
                    break
                elif selec_hist == "2":
                    plot_table(tablas[2], "N° de clusters por célula por track")
                    plt.show()
                    break
                elif selec_hist == "3":
                    plot_table(tablas[3], "Largo de clusters [bp]")
                    plt.show()
                    break
                elif selec_hist == "4":
                    plot_table(tablas[4], "Densidad de lesiones [lesiones/nucleótido]")
                    plt.show()
                    break
                elif selec_hist == "5":
                    plot_table(tablas[5], "Composición de cluster [%SB por cluster]")
                    plt.show()
                    break
                elif selec_hist == "6":
                    plot_table(tablas[1], "N° de clusters por célula")
                    plot_table(tablas[2], "N° de clusters por célula por track")
                    plot_table(tablas[3], "Largo de clusters [bp]")
                    plot_table(tablas[4], "Densidad de lesiones [lesiones/nucleótido]")
                    plot_table(tablas[5], "Composición de cluster [%SB por cluster]")
                    plt.show()
                    break
                elif selec_hist == "7":
                    break
                elif selec_hist == "q" or selec_hist == "Q":
                    sys.exit()
                else:
                    print("Error, elija una de las opciones (o ingrese <q> para salir)")
        ####PLOTEO DE DISPERSIÓN 2D
        elif selec == "2":
            print(
                "Seleccione la variable para el eje x:\n 1. N° de lesiones del cluster \n 2. N° de clusters por célula\n 3. N° de clusters por célula por track \n 4. Largo de clusters [bp] \n 5. Densidad de lesiones\n 6. Composición de cluster [%SB por cluster]\n 7. Volver")
            selec_scatx = input("Selección: ")
            print(
                "Seleccione la variable para el eje y:\n 1. N° de lesiones del cluster \n 2. N° de clusters por célula\n 3. N° de clusters por célula por track \n 4. Largo de clusters [bp] \n 5. Densidad de lesiones\n 6. Composición de cluster [%SB por cluster]\n 7. Volver")
            selec_scaty = input("Selección: ")
            while True:
                while True:
                    if selec_scatx == "1":
                        varx = "N° de lesiones del cluster"
                        tabx = "any"
                        break
                    elif selec_scatx == "2":
                        varx = "N° de clusters por célula"
                        tabx = tablas[1]
                        break
                    elif selec_scatx == "3":
                        varx = "N° de clusters por célula por trayectoria"
                        tabx = tablas[2]
                        break
                    elif selec_scatx == "4":
                        varx = "Largo de clusters [bp]"
                        tabx = tablas[3]
                        break
                    elif selec_scatx == "5":
                        varx = "Densidad de lesiones [lesiones por nucleótido]"
                        tabx = tablas[4]
                        break
                    elif selec_scatx == "6":
                        varx = "Composición de cluster [%SB por cluster]"
                        tabx = tablas[5]
                        break
                    elif selec_scatx == "7":
                        selec_scaty = "7"
                        break
                    else:
                        print("Error, elija una de las opciones (o ingrese <q> para salir)")
                while True:
                    if selec_scaty == "1":
                        vary = "N° de lesiones del cluster"
                        taby = "any"
                        break
                    elif selec_scaty == "2":
                        vary = "N° de clusters por célula"
                        taby = tablas[1]
                        break
                    elif selec_scaty == "3":
                        vary = "N° de clusters por célula por trayectoria"
                        taby = tablas[2]
                        break
                    elif selec_scaty == "4":
                        vary = "Largo de clusters [bp]"
                        taby = tablas[3]
                        break
                    elif selec_scaty == "5":
                        vary = "Densidad de lesiones [lesiones por nucleótido]"
                        taby = tablas[4]
                        break
                    elif selec_scaty == "6":
                        vary = "Composición de cluster [%SB por cluster]"
                        taby = tablas[5]
                        break
                    elif selec_scaty == "7":
                        break
                    else:
                        print("Error, elija una de las opciones (o ingrese <q> para salir)")
                if selec_scaty == "7" or selec_scatx == "7":
                    break
                try:
                    if taby == "any" and tabx == "any":
                        tabx = tablas[1]
                        taby = tablas[1]
                        scat2d(varx, vary, tabx, taby)
                        plt.show()
                        break
                    elif taby == "any" and tabx != "any":
                        taby = tabx
                        scat2d(varx, vary, tabx, taby)
                        plt.show()
                        break
                    elif tabx == "any" and taby != "any":
                        tabx = taby
                        scat2d(varx, vary, tabx, taby)
                        plt.show()
                        break
                    else:
                        scat2d(varx, vary, tabx, taby)
                        plt.show()
                        break
                except:
                    print("Ha ocurrido un error")
                    break


def mcds_inp_gen(ident):
    # Esta función permite iterar la generación de archivos .inp n_iter veces para variar algun parámetro y fijar los demás, este programa tiene
    # como finalidad estudiar la sensibilidad de la simulación a cambios en diferentes parámetros. Esta función funciona de manera
    # interactiva, es decir, se requiere de input. Partiendo por el identificador de la prueba (ident) que será el nombre de la carpeta con el output
    while True:
        param = input("Seleccione el tipo de parámetro a testear:\n1.Contenido de ADN [Gbp] 2.Diámetro nuclear [um]\n"
                      "3.Diámetro celular [um]  4.WEM [mg/cm^2]\n5.Campo de radiación [Archivo Dat] 6.Partícula\n"
                      "7.Energía Cinética [MeV] 8.Energía Cinética por nucleón [MeV/A]\n9.Dosis Absorbida [Gy] 10."
                      "Concentración de oxígeno [%O2]\n11.Presión parcial de oxígeno [mmHg] 12.OER máximo\n"
                      "13.k 14.q 15.r 16.fbl 17.Concentración DMSO [mol/dm^3]\n18.Fracción no rescatable 19.CHMX[mol/dm^3]\n20.N° de células simuladas 21.Semilla de n°s aleatorios\nSelección: ")
        if param not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17",
                         "18", "19", "20", "21"]:
            print("Error en la selección, intente nuevamente")
        else:
            break
    en_pred = input("¿Desea usar los valores predeterminados de energía definidos en el codigo fuente? s/n: ").lower()
    [inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
     inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2, inp_evo2_mmhg,
     inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl, inp_dmso_conc, inp_dmso_fnsd,
     inp_dmso_chmx] = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""]
    while True:
        spec = input("¿Desea fijar manualmente alguna variable de la simulación? (y/n): ")
        if spec == "y" or spec == "Y":
            while True:
                var = input(
                    "Seleccione que variable desea fijar o ingrese <t> para concluir la fijación de variables:\n1.Contenido de ADN [Gbp] 2.Diámetro nuclear [um]\n"
                    "3.Diámetro celular [um]  4.WEM [mg/cm^2]\n5.Campo de radiación [Archivo Dat] 6.Partícula\n"
                    "7.Energía Cinética [MeV] 8.Energía Cinética por nucleón [MeV/A]\n9.Dosis Absorbida [Gy] 10."
                    "Concentración de oxígeno [%O2]\n11.Presión parcial de oxígeno [mmHg] 12.OER máximo\n"
                    "13.k 14.q 15.r 16.fbl 17.Concentración DMSO [mol/dm^3]\n18.Fracción no rescatable 19.CHMX[mol/dm^3]\n"
                    "20.N° de células simuladas 21.Semilla de n°s aleatorios\nSelección: ")

                if var == "1":
                    inp_cell_dna = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "2":
                    inp_cell_ndia = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "3":
                    inp_cell_cdia = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "4":
                    inp_cell_wem = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "5":
                    inp_radx_fn = input("Ingrese archivo de radiación, para cancelar solo presione <enter>: ")
                elif var == "6":
                    inp_radx_par = input("Ingrese partícula a fijar, para cancelar solo presione <enter>: ")
                elif var == "7":
                    inp_radx_ke = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "8":
                    inp_radx_meva = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "9":
                    inp_radx_ad = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "10":
                    inp_evo2_po2 = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "11":
                    inp_evo2_mmhg = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "12": \
                        inp_evo2_m0 = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "13":
                    inp_evo2_k = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "14":
                    inp_evo2_q = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "15":
                    inp_evo2_r = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "16":
                    inp_mcds_fbl = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "17":
                    inp_dmso_conc = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "18":
                    inp_dmso_fnsd = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "19":
                    inp_dmso_chmx = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "20":
                    inp_simcon_nocs = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "21":
                    inp_simcon_seed = input("Ingrese nuevo valor, para cancelar solo presione <enter>: ")
                elif var == "t" or var == "T":
                    break

                else:
                    print("Error en la selección, vuelva a intentarlo")

        elif spec == "n" or spec == "N":
            break
        else:
            print("Error en el input, intente nuevamente")
    cwd = os.getcwd()
    if os.path.exists(cwd + "\\" + ident):
        shutil.rmtree(cwd + "\\" + ident)
    os.mkdir(cwd + "\\" + ident)
    contador = 0
    if param == "1":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("Cont. ADN = {} Gbp".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(i, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "2":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("Diámetro nuclear = {} um".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, i, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "3":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("Diámetro Celular = {} um".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, i, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "4":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("WEM = {} mm".format(float(i) * 10 / 1000))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, i, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "5":
        archivos_dat = []
        labels = []
        while True:
            orden = input("Ingrese nombre del archivo .dat a testear o ingrese <t> para terminar la lista: ")
            if orden != "t" and orden != "T":
                archivos_dat.append(orden)
            else:
                break
        for i in archivos_dat:
            labels.append("{}".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         i, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "6":
        particulas = []
        labels = []
        while True:
            orden = input("Ingrese nombre de partícula a testear o ingrese <t> para terminar la lista de particulas: ")
            if orden != "t" and orden != "T":
                particulas.append(orden)
            else:
                break
        for i in particulas:
            labels.append("{}".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, i, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "7":
        valores = []
        labels = []
        if en_pred != "s":
            while True:
                orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
                if orden != "t" and orden != "T":
                    valores.append(orden)
                else:
                    break
        elif en_pred == "s":
            valores = [  0.5,   1. ,   1.5,   2. ,   2.5,   3. ,   3.5,   4. ,   4.5,
                         5. ,   5.5,   6. ,   6.5,   7. ,   7.5,   8. ,   8.5,   9. ,
                         9.5,  10. ,  10.5,  11. ,  11.5,  12. ,  12.5,  13. ,  13.5,
                        14. ,  14.5,  15. ,  15.5,  16. ,  16.5,  17. ,  17.5,  18. ,
                        18.5,  19. ,  19.5,  20. ,  20.5,  21. ,  21.5,  22. ,  22.5,
                        23. ,  23.5,  24. ,  24.5,  25. ,  25.5,  26. ,  26.5,  27. ,
                        27.5,  28. ,  28.5,  29. ,  29.5,  30. ,  30.5,  31. ,  31.5,
                        32. ,  32.5,  33. ,  33.5,  34. ,  34.5,  35. ,  35.5,  36. ,
                        36.5,  37. ,  37.5,  38. ,  38.5,  39. ,  39.5,  40. ,  40.5,
                        41. ,  41.5,  42. ,  42.5,  43. ,  43.5,  44. ,  44.5,  45. ,
                        45.5,  46. ,  46.5,  47. ,  47.5,  48. ,  48.5,  49. ,  49.5,
                        50. ,  50.5,  51. ,  51.5,  52. ,  52.5,  53. ,  53.5,  54. ,
                        54.5,  55. ,  55.5,  56. ,  56.5,  57. ,  57.5,  58. ,  58.5,
                        59. ,  59.5,  60. ,  60.5,  61. ,  61.5,  62. ,  62.5,  63. ,
                        63.5,  64. ,  64.5,  65. ,  65.5,  66. ,  66.5,  67. ,  67.5,
                        68. ,  68.5,  69. ,  69.5,  70. ,  70.5,  71. ,  71.5,  72. ,
                        72.5,  73. ,  73.5,  74. ,  74.5,  75. ,  75.5,  76. ,  76.5,
                        77. ,  77.5,  78. ,  78.5,  79. ,  79.5,  80. ,  80.5,  81. ,
                        81.5,  82. ,  82.5,  83. ,  83.5,  84. ,  84.5,  85. ,  85.5,
                        86. ,  86.5,  87. ,  87.5,  88. ,  88.5,  89. ,  89.5,  90. ,
                        90.5,  91. ,  91.5,  92. ,  92.5,  93. ,  93.5,  94. ,  94.5,
                        95. ,  95.5,  96. ,  96.5,  97. ,  97.5,  98. ,  98.5,  99. ,
                        99.5, 100. , 100.5, 101. , 101.5, 102. , 102.5, 103. , 103.5,
                       104. , 104.5, 105. , 105.5, 106. , 106.5, 107. , 107.5, 108. ,
                       108.5, 109. , 109.5, 110. , 110.5, 111. , 111.5, 112. , 112.5,
                       113. , 113.5, 114. , 114.5, 115. , 115.5, 116. , 116.5, 117. ,
                       117.5, 118. , 118.5, 119. , 119.5, 120. , 120.5, 121. , 121.5,
                       122. , 122.5, 123. , 123.5, 124. , 124.5, 125. , 125.5, 126. ,
                       126.5, 127. , 127.5, 128. , 128.5, 129. , 129.5, 130. , 130.5,
                       131. , 131.5, 132. , 132.5, 133. , 133.5, 134. , 134.5, 135. ,
                       135.5, 136. , 136.5, 137. , 137.5, 138. , 138.5, 139. , 139.5,
                       140. , 140.5, 141. , 141.5, 142. , 142.5, 143. , 143.5, 144. ,
                       144.5, 145. , 145.5, 146. , 146.5, 147. , 147.5, 148. , 148.5,
                       149. , 149.5, 150. , 150.5, 151. , 151.5, 152. , 152.5, 153. ,
                       153.5, 154. , 154.5, 155. , 155.5, 156. , 156.5, 157. , 157.5,
                       158. , 158.5, 159. , 159.5, 160. , 160.5, 161. , 161.5, 162. ,
                       162.5, 163. , 163.5, 164. , 164.5, 165. , 165.5, 166. , 166.5,
                       167. , 167.5, 168. , 168.5, 169. , 169.5, 170. , 170.5, 171. ,
                       171.5, 172. , 172.5, 173. , 173.5, 174. , 174.5, 175. , 175.5,
                       176. , 176.5, 177. , 177.5, 178. , 178.5, 179. , 179.5, 180. ,
                       180.5, 181. , 181.5, 182. , 182.5, 183. , 183.5, 184. , 184.5,
                       185. , 185.5, 186. , 186.5, 187. , 187.5, 188. , 188.5, 189. ,
                       189.5, 190. , 190.5, 191. , 191.5, 192. , 192.5, 193. , 193.5,
                       194. , 194.5, 195. , 195.5, 196. , 196.5, 197. , 197.5, 198. ,
                       198.5, 199. , 199.5, 200. , 200.5, 201. , 201.5, 202. , 202.5,
                       203. , 203.5, 204. , 204.5, 205. , 205.5, 206. , 206.5, 207. ,
                       207.5, 208. , 208.5, 209. , 209.5, 210. , 210.5, 211. , 211.5,
                       212. , 212.5, 213. , 213.5, 214. , 214.5, 215. , 215.5, 216. ,
                       216.5, 217. , 217.5, 218. , 218.5, 219. , 219.5, 220. , 220.5,
                       221. , 221.5, 222. , 222.5, 223. , 223.5, 224. , 224.5, 225. ,
                       225.5, 226. , 226.5, 227. , 227.5, 228. , 228.5, 229. , 229.5,
                       230. , 230.5, 231. , 231.5, 232. , 232.5, 233. , 233.5, 234. ,
                       234.5, 235. , 235.5, 236. , 236.5, 237. , 237.5, 238. , 238.5,
                       239. , 239.5, 240. , 240.5, 241. , 241.5, 242. , 242.5, 243. ,
                       243.5, 244. , 244.5, 245. , 245.5, 246. , 246.5, 247. , 247.5,
                       248. , 248.5, 249. , 249.5, 250. , 250.5, 251. , 251.5, 252. ,
                       252.5, 253. , 253.5, 254. , 254.5, 255. , 255.5, 256. , 256.5,
                       257. , 257.5, 258. , 258.5, 259. , 259.5, 260. , 260.5, 261. ,
                       261.5, 262. , 262.5, 263. , 263.5, 264. , 264.5, 265. , 265.5,
                       266. , 266.5, 267. , 267.5, 268. , 268.5, 269. , 269.5, 270. ,
                       270.5, 271. , 271.5, 272. , 272.5, 273. , 273.5, 274. , 274.5,
                       275. , 275.5, 276. , 276.5, 277. , 277.5, 278. , 278.5, 279. ,
                       279.5, 280. , 280.5, 281. , 281.5, 282. , 282.5, 283. , 283.5,
                       284. , 284.5, 285. , 285.5, 286. , 286.5, 287. , 287.5, 288. ,
                       288.5, 289. , 289.5, 290. , 290.5, 291. , 291.5, 292. , 292.5,
                       293. , 293.5, 294. , 294.5, 295. , 295.5, 296. , 296.5, 297. ,
                       297.5, 298. , 298.5, 299. , 299.5, 300. , 300.5, 301. , 301.5,
                       302. , 302.5, 303. , 303.5, 304. , 304.5, 305. , 305.5, 306. ,
                       306.5, 307. , 307.5, 308. , 308.5, 309. , 309.5, 310. , 310.5,
                       311. , 311.5, 312. , 312.5, 313. , 313.5, 314. , 314.5, 315. ,
                       315.5, 316. , 316.5, 317. , 317.5, 318. , 318.5, 319. , 319.5,
                       320. , 320.5, 321. , 321.5, 322. , 322.5, 323. , 323.5, 324. ,
                       324.5, 325. , 325.5, 326. , 326.5, 327. , 327.5, 328. , 328.5,
                       329. , 329.5, 330. , 330.5, 331. , 331.5, 332. , 332.5, 333. ,
                       333.5, 334. , 334.5, 335. , 335.5, 336. , 336.5, 337. , 337.5,
                       338. , 338.5, 339. , 339.5, 340. , 340.5, 341. , 341.5, 342. ,
                       342.5, 343. , 343.5, 344. , 344.5, 345. , 345.5, 346. , 346.5,
                       347. , 347.5, 348. , 348.5, 349. , 349.5, 350. , 350.5, 351. ,
                       351.5, 352. , 352.5, 353. , 353.5, 354. , 354.5, 355. , 355.5,
                       356. , 356.5, 357. , 357.5, 358. , 358.5, 359. , 359.5, 360. ,
                       360.5, 361. , 361.5, 362. , 362.5, 363. , 363.5, 364. , 364.5,
                       365. , 365.5, 366. , 366.5, 367. , 367.5, 368. , 368.5, 369. ,
                       369.5, 370. , 370.5, 371. , 371.5, 372. , 372.5, 373. , 373.5,
                       374. , 374.5, 375. , 375.5, 376. , 376.5, 377. , 377.5, 378. ,
                       378.5, 379. , 379.5, 380. , 380.5, 381. , 381.5, 382. , 382.5,
                       383. , 383.5, 384. , 384.5, 385. , 385.5, 386. , 386.5, 387. ,
                       387.5, 388. , 388.5, 389. , 389.5, 390. , 390.5, 391. , 391.5,
                       392. , 392.5, 393. , 393.5, 394. , 394.5, 395. , 395.5, 396. ,
                       396.5, 397. , 397.5, 398. , 398.5, 399. , 399.5, 400. , 400.5,
                       401. , 401.5, 402. , 402.5, 403. , 403.5, 404. , 404.5, 405. ,
                       405.5, 406. , 406.5, 407. , 407.5, 408. , 408.5, 409. , 409.5,
                       410. , 410.5, 411. , 411.5, 412. , 412.5, 413. , 413.5, 414. ,
                       414.5, 415. , 415.5, 416. , 416.5, 417. , 417.5, 418. , 418.5,
                       419. , 419.5, 420. , 420.5, 421. , 421.5, 422. , 422.5, 423. ,
                       423.5, 424. , 424.5, 425. , 425.5, 426. , 426.5, 427. , 427.5,
                       428. , 428.5, 429. , 429.5, 430. , 430.5, 431. , 431.5, 432. ,
                       432.5, 433. , 433.5, 434. , 434.5, 435. , 435.5, 436. , 436.5,
                       437. , 437.5, 438. , 438.5, 439. , 439.5, 440. , 440.5, 441. ,
                       441.5, 442. , 442.5, 443. , 443.5, 444. , 444.5, 445. , 445.5,
                       446. , 446.5, 447. , 447.5, 448. , 448.5, 449. , 449.5, 450. ,
                       450.5, 451. , 451.5, 452. , 452.5, 453. , 453.5, 454. , 454.5,
                       455. , 455.5, 456. , 456.5, 457. , 457.5, 458. , 458.5, 459. ,
                       459.5, 460. , 460.5, 461. , 461.5, 462. , 462.5, 463. , 463.5,
                       464. , 464.5, 465. , 465.5, 466. , 466.5, 467. , 467.5, 468. ,
                       468.5, 469. , 469.5, 470. , 470.5, 471. , 471.5, 472. , 472.5,
                       473. , 473.5, 474. , 474.5, 475. , 475.5, 476. , 476.5, 477. ,
                       477.5, 478. , 478.5, 479. , 479.5, 480. , 480.5, 481. , 481.5,
                       482. , 482.5, 483. , 483.5, 484. , 484.5, 485. , 485.5, 486. ,
                       486.5, 487. , 487.5, 488. , 488.5, 489. , 489.5, 490. , 490.5,
                       491. , 491.5, 492. , 492.5, 493. , 493.5, 494. , 494.5, 495. ,
                       495.5, 496. , 496.5, 497. , 497.5, 498. , 498.5, 499. , 499.5,
                       500. ]
            valores = [str(val) for val in valores]
            print("Uso de energías predeterminadas en codigo fuente...")
            print("E={}".format(valores))
        for i in valores:
            labels.append("KE = {} MeV".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, i, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "8":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("KE x nucleón = {} MeV/A".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, i, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "9":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("Dosis Absorbida = {} Gy".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, i, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "10":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("pO2 = {} %".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, i,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "11":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("[O2] = {} mmHg".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         i, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "12":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("max OER = {}".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, i, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "13":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("k = {}".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, i, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "14":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("q = {}".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, i, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "15":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("r = {}".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, i, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "16":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("Fracción de sitios abasicos = {}".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, i,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "17":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("[DMSO] = {} mol/dm^3".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         i,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "18":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("Fracción no reducible: {}".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         i, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "19":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("CHMX: {} mol/dm^3".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, i))
            texto_input.close()
            contador += 1
    elif param == "20":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("N simulaciones: {}".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, inp_simcon_seed, i,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    elif param == "21":
        valores = []
        labels = []
        while True:
            orden = input("Ingrese valores a testear o ingrese <t> para terminar la lista de valores: ")
            if orden != "t" and orden != "T":
                valores.append(orden)
            else:
                break
        for i in valores:
            labels.append("Random seed: {}".format(i))
            texto_input = open(cwd + "\\" + ident + "\\" + ident + "_{}".format(contador) + ".inp", 'w')
            texto_input.write(
                mcds_inp(inp_cell_dna, inp_cell_ndia, inp_cell_cdia, inp_cell_wem, i, inp_simcon_nocs,
                         inp_radx_fn, inp_radx_par, inp_radx_ke, inp_radx_meva, inp_radx_ad, inp_evo2_po2,
                         inp_evo2_mmhg, inp_evo2_m0, inp_evo2_k, inp_evo2_q, inp_evo2_r, inp_mcds_fbl,
                         inp_dmso_conc,
                         inp_dmso_fnsd, inp_dmso_chmx))
            texto_input.close()
            contador += 1
    return labels


def extr_column(table, column_index):
    # column_index es el índice de la columna que quiero extraer (de 0 a 4)
    # table es la tabla (lista de listas) a la que quiero extraerle la columna
    column = []
    for i in table:
        column.append(i[column_index])
    return column


def table_var_name(table_index):
    if table_index == 7:
        var_name = "Producción porcentual de daño en clusters"
    elif table_index == 1:
        var_name = "N° de lesiones del cluster"
    elif table_index == 2:
        var_name = "N° de clusters por célula"
    elif table_index == 3:
        var_name = "N° de clusters por célula por trayectoria"
    elif table_index == 4:
        var_name = "Largo de clusters [bp]"
    elif table_index == 5:
        var_name = "Densidad de lesiones [lesiones por nucleótido]"
    elif table_index == 6:
        var_name = "Composición de cluster [%SB por cluster]"
    else:
        var_name = False
    return var_name


def plot_t1(t1s, labels, dir):
    xlabels = ['BD', 'SSB', 'SSB+', '2SSB', 'DSB', 'DSB+', 'DSB++', 'SSBc', 'SSBcb', 'DSBc', 'DSBcb']
    x = np.arange(len(xlabels))  # the label locations
    cont = 0
    fig, ax = plt.subplots()
    for i in t1s:
        y = []
        for t in i:
            y.append(t[0])
        xd = np.arange(len(t1s))
        width = 0.8 / len(xd)  # the width of the bars
        ax.bar(x + width * cont - width * len(xd) / 2, y, width, label=labels[cont], align='edge')
        cont += 1
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Porcentaje de aparaición del cúmulo [%]')
    ax.set_title('Porcentaje de daño por tipo de cúmulo')
    ax.set_xticks(x)
    ax.set_xticklabels(xlabels)
    ax.legend()
    fig.savefig(dir + "\\Porcentaje de daño por tipo de cúmulo.png")
    fig.tight_layout()


def line_2d(tabla, xlabel, ylabel, titulo, dir):  # GRÁFICO DE ALGO EN FN DEL N° DE LESIONES
    labels = ["DSB", "SSB", "Otros", "Todos"]
    markers = ["D", "d", "x", "o"]
    nlesions = []
    dsb = []
    dsb_er = []
    ssb = []
    ssb_er = []
    others = []
    others_er = []
    all = []
    all_er = []
    eff_len = t_eff_len(tabla)
    for i in tabla[0:eff_len]:
        nlesions.append(i[0])
        dsb.append(i[1])
        dsb_er.append(i[2])
        ssb.append(i[3])
        ssb_er.append(i[4])
        others.append(i[5])
        others_er.append(i[6])
        all.append(i[7])
        all_er.append(i[8])
    xs = [nlesions, nlesions, nlesions, nlesions]
    ys = [dsb, ssb, others, all]
    ers = [dsb_er, ssb_er, others_er, all_er]
    fig, ax = plt.subplots()
    i = 0
    while i < len(xs):
        # ax.plot(xs[i],ys[i],linestyle='--',linewidth=0.2)
        # ax.scatter(xs[i],ys[i],marker=markers[i],label=labels[i])
        ax.errorbar(xs[i], ys[i], ers[i], label=labels[i], capsize=2.5, linestyle='--', linewidth=0.5)
        i += 1
    # ax.set_xticks(np.array(xs[0]))
    ax.set_title(titulo)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.legend()
    ax.xaxis.set_minor_locator(MultipleLocator(1))
    ax.grid()
    ax.xaxis.grid(True, which='minor')
    fig.tight_layout()
    dir_save_0 = dir + "\\{}.png".format(titulo).replace("/", "")
    dir_save = dir_save_0.strip('/')
    fig.savefig(dir_save)


def param_tester(ident):
    path_mcds = os.path.join('mcds', 'bin', 'mcds.exe')
    cwd = os.getcwd()
    if os.path.exists(cwd + "\\" + ident + "_bats"):
        shutil.rmtree(cwd + "\\" + ident + "_bats")
    os.mkdir(
        cwd + "\\" + ident + "_bats")  # Estas 3 lineas checkean si la carpeta "ident_bats" ya existe y la sobreescribe si es asi

    labels = mcds_inp_gen(ident)  # genera inputs y labels
    label_file = open(cwd + "\\" + ident + "\\" + ident + "_labels", 'w')
    for i in labels:
        label_file.write(i + "\n")
    label_file.close()
    contador = 0
    for file in os.listdir(
            cwd + "\\" + ident):  # Para cada input se escribe un .bat en la carpeta ident_bats y se corre; los .out quedan en la carpeta ident
        if file[-3:] == "inp":
            ruta = os.path.join(cwd + "\\" + ident, file)
            bat = open(cwd + "\\" + ident + "_bats\\" + ident + "_bat_{}".format(contador) + ".bat", 'w')
            bat.write(mcds_bat(ruta, path_mcds))
            bat.close()
            subprocess.call(
                [r"{}".format(cwd) + "\\" + ident + "_bats\\" + ident + "_bat_{}".format(contador) + ".bat"])
            contador += 1
    return


def test_info(ident):  # Generar una tupla, un término con todas la tablas y el otro con las labels
    cwd = os.getcwd()
    labels_0 = []
    label_file = open(cwd + "\\" + ident + "\\" + ident + "_labels", 'r')
    for label in label_file:
        if label != "":
            labels_0.append(label)
    file_numbers = []
    alltabs = []  # lista con todas las tablas de los outputs [[[t1],[t2]...,[]]]=[mcds_of(out1),mcds_of(out2),...]
    for file in os.listdir(cwd + "\\" + ident):
        if file.endswith(".out"):
            file_numberdotout = ''.join(file.split("_")[-1:])
            file_number = int(file_numberdotout.replace('.out', ''))
            file_numbers.append(file_number)
            alltabs.append(mcds_of(cwd + "\\" + ident + "\\" + file))
    alltabs_ord = list(range(len(alltabs)))
    cont = 0
    for i in file_numbers:
        alltabs_ord[i] = alltabs[cont]
        cont += 1
    labels = [lbl.strip('\n') for lbl in labels_0]
    return alltabs_ord, labels


def frac_cluster(t2):
    nlesions = []
    dsb = []
    dsb_er = []
    ssb = []
    ssb_er = []
    others = []
    others_er = []
    all = []
    all_er = []
    eff_len = t_eff_len(t2)
    for i in t2[0:eff_len]:
        nlesions.append(i[0])
        dsb.append(i[1])
        dsb_er.append(i[2])
        ssb.append(i[3])
        ssb_er.append(i[4])
        others.append(i[5])
        others_er.append(i[6])
        all.append(i[7])
        all_er.append(i[8])
    tot_dsb_er = sum([i ** 2 for i in dsb_er]) ** 0.5
    tot_dsb = sum(dsb)
    tot_ssb_er = sum([i ** 2 for i in ssb_er]) ** 0.5
    tot_ssb = sum(ssb)
    tot_others_er = sum([i ** 2 for i in others_er]) ** 0.5
    tot_others = sum(others)
    tot_all = sum(all)
    tot_all_er = sum([i ** 2 for i in all_er]) ** 0.5

    try:
        frac_dsb = tot_dsb / tot_all
        frac_dsb_er = frac_dsb * sum([i ** 2 for i in [tot_dsb_er / tot_dsb, tot_all_er / tot_all]]) ** 0.5
        frac_ssb = tot_ssb / tot_all
        frac_ssb_er = frac_ssb * sum([i ** 2 for i in [tot_ssb_er / tot_ssb, tot_all_er / tot_all]]) ** 0.5
        frac_others = tot_others / tot_all
        frac_others_er = frac_others * sum([i ** 2 for i in [tot_others_er / tot_others, tot_all_er / tot_all]]) ** 0.5
    except:
        frac_dsb = 0
        frac_dsb_er = 0
        frac_ssb = 0
        frac_ssb_er = 0
        frac_others = 0
        frac_others_er = 0

    return [(frac_dsb, frac_dsb_er), (frac_ssb, frac_ssb_er), (frac_others, frac_others_er)]


def tot_cluster(t2):
    nlesions = []
    dsb = []
    dsb_er = []
    ssb = []
    ssb_er = []
    others = []
    others_er = []
    all = []
    all_er = []
    eff_len = t_eff_len(t2)
    for i in t2[0:eff_len]:
        nlesions.append(i[0])
        dsb.append(i[1])
        dsb_er.append(i[2])
        ssb.append(i[3])
        ssb_er.append(i[4])
        others.append(i[5])
        others_er.append(i[6])
        all.append(i[7])
        all_er.append(i[8])
    tot_dsb_er = sum([i ** 2 for i in dsb_er]) ** 0.5
    tot_dsb = sum(dsb)
    tot_ssb_er = sum([i ** 2 for i in ssb_er]) ** 0.5
    tot_ssb = sum(ssb)
    tot_others_er = sum([i ** 2 for i in others_er]) ** 0.5
    tot_others = sum(others)
    tot_all = sum(all)
    tot_all_er = sum([i ** 2 for i in all_er]) ** 0.5

    return [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er), (tot_all, tot_all_er)]


def tot_lesions(t2):
    les_on_dsb = []
    les_on_dsb_er = []
    les_on_ssb = []
    les_on_ssb_er = []
    les_on_others = []
    les_on_others_er = []
    les_on_all = []
    les_on_all_er = []
    eff_len = t_eff_len(t2)
    for i in t2[0:eff_len]:
        nlesions = i[0]
        les_on_dsb.append(i[1] * nlesions)
        les_on_dsb_er.append(i[2] * nlesions)
        les_on_ssb.append(i[3] * nlesions)
        les_on_ssb_er.append(i[4] * nlesions)
        les_on_others.append(i[5] * nlesions)
        les_on_others_er.append(i[6] * nlesions)
        les_on_all.append(i[7] * nlesions)
        les_on_all_er.append(i[8] * nlesions)

    tot_les_on_dsb_er = sum([i ** 2 for i in les_on_dsb_er]) ** 0.5
    tot_les_on_dsb = sum(les_on_dsb)
    tot_les_on_ssb_er = sum([i ** 2 for i in les_on_ssb_er]) ** 0.5
    tot_les_on_ssb = sum(les_on_ssb)
    tot_les_on_others_er = sum([i ** 2 for i in les_on_others_er]) ** 0.5
    tot_les_on_others = sum(les_on_others)
    tot_les_on_all_er = sum([i ** 2 for i in les_on_all_er]) ** 0.5
    tot_les_on_all = sum(les_on_all)

    tloa = tot_les_on_dsb + tot_les_on_ssb + tot_les_on_others
    tloa_er = sum([i ** 2 for i in [tot_les_on_dsb_er, tot_les_on_ssb_er, tot_les_on_others_er]]) ** 0.5

    return [(tot_les_on_dsb, tot_les_on_dsb_er), (tot_les_on_ssb, tot_les_on_ssb_er),
            (tot_les_on_others, tot_les_on_others_er), (tot_les_on_all, tot_les_on_all_er)]


# def plot_bars([(frac_dsb,frac_dsb_er),(frac_ssb,frac_ssb_er),(frac_others,frac_others_er)])
def plot_bars(t2s, labels, dir):
    xlabels = ['DSB', 'SSB', 'Otros', 'Todos']
    x2labels = ['DSB', 'SSB', 'Otros']
    x = np.arange(len(xlabels))  # the label locations
    cont = 0
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(12, 5))
    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        y = [tot_dsb, tot_ssb, tot_others, tot_all]
        y_err = [tot_dsb_er, tot_ssb_er, tot_others_er, tot_all_er]
        xd = np.arange(len(t2s))
        width = 0.8 / len(xd)  # the width of the bars
        ax1.bar(x + width * cont - width * len(xd) / 2, y, width, label=labels[cont], align='edge')
        ax1.errorbar(x + width * cont - width * len(xd) / 2 + width / 2, y, yerr=y_err, color='black', linewidth=0,
                     elinewidth=1, markeredgewidth=1, capsize=10 * width)
        cont += 1
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax1.set_ylabel('N° total de clusters por tipo')
    ax1.set_xticks(x)
    ax1.set_xticklabels(xlabels)
    # ax1.legend()
    x2 = np.arange(len(x2labels))
    cont = 0
    for i in t2s:
        [(frac_dsb, frac_dsb_er), (frac_ssb, frac_ssb_er), (frac_others, frac_others_er)] = frac_cluster(i)
        y = [frac_dsb, frac_ssb, frac_others]
        y_err = [frac_dsb_er, frac_ssb_er, frac_others_er]
        xd = np.arange(len(t2s))
        width = 0.8 / len(xd)  # the width of the bars
        ax2.bar(x2 + width * cont - width * len(xd) / 2, y, width, label=labels[cont], align='edge')
        ax2.errorbar(x2 + width * cont - width * len(xd) / 2 + width / 2, y, yerr=y_err, color='black', linewidth=0,
                     elinewidth=1, markeredgewidth=1, capsize=10 * width)
        cont += 1
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax2.set_ylabel('Fracción de aparición de tipo de cluster')
    ax2.set_xticks(x2)
    ax2.yaxis.set_minor_locator(MultipleLocator(2))
    ax2.yaxis.grid(True, which='both')
    ax2.set_xticklabels(x2labels)
    # ax2.legend(framealpha=1)
    # fig.savefig(dir+"\\Porcentaje de daño por tipo de cúmulo.png")
    cont = 0
    for i in t2s:
        [(tot_les_on_dsb, tot_les_on_dsb_er), (tot_les_on_ssb, tot_les_on_ssb_er),
         (tot_les_on_others, tot_les_on_others_er), (tot_les_on_all, tot_les_on_all_er)] = tot_lesions(i)
        y = [tot_les_on_dsb, tot_les_on_ssb, tot_les_on_others, tot_les_on_all]
        y_err = [tot_les_on_dsb_er, tot_les_on_ssb_er, tot_les_on_others_er, tot_les_on_all_er]
        xd = np.arange(len(t2s))
        width = 0.8 / len(xd)  # the width of the bars
        ax3.bar(x + width * cont - width * len(xd) / 2, y, width, label=labels[cont], align='edge')
        ax3.errorbar(x + width * cont - width * len(xd) / 2 + width / 2, y, yerr=y_err, color='black', linewidth=0,
                     elinewidth=1, markeredgewidth=1, capsize=10 * width)
        cont += 1
    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax3.set_ylabel('N° total de lesiones por tipo de cluster')
    ax3.set_xticks(x)
    ax3.set_xticklabels(xlabels)
    ax3.legend(framealpha=1)
    fig.suptitle('Vista general de clusters y lesiones', fontsize=16)
    fig.tight_layout()
    if os.path.exists(dir) == False:
        os.mkdir(dir)
    fig.savefig(dir + "\\Vista general de clusters y lesiones.png")


def dsb_vs_ssb(t2s, labels):
    x = []
    x_er = []
    y = []
    y_er = []

    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        x.append(tot_ssb)
        x_er.append(tot_ssb_er)
        y.append(tot_dsb)
        y_er.append(tot_dsb_er)
    fig, ax = plt.subplots()
    ax.errorbar(x, y, y_er, x_er, linewidth=0, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1)
    for i, txt in enumerate(labels):
        ax.annotate(txt, (x[i], y[i]))


def dsb_ssb_ratio_vs_info(t2s, info, eje_x, labels):
    # info son las labels del eje x, puede ser lo que sea.
    fig, ax = plt.subplots()
    y = []
    y_er = []
    x = np.arange(len(info))
    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        y.append(tot_dsb / tot_ssb)
        y_er.append(tot_dsb_er / tot_ssb_er * ((tot_dsb_er / tot_dsb) ** 2 + (tot_ssb_er / tot_ssb) ** 2) ** 0.5)
    ax.errorbar(x, y, y_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1)
    ax.set_ylabel('DSB/SSB ratio')
    ax.set_xlabel(eje_x)
    ax.set_xticks(x)
    ax.set_xticklabels(info)
    for i, txt in enumerate(labels):
        ax.annotate(txt, (x[i], y[i]))


def track_info(ident="prueba_energia_0mm"):
    cwd = os.getcwd()
    outs = []
    contador = 0
    for file in os.listdir(cwd + "\\" + ident):  # Para cada input se extrae la info de track
        if file[-3:] == "out":
            contador += 1
    for i in range(contador):
        with open(cwd + "\\" + ident + "\\" + ident + "_{}.out".format(i), "r") as output:
            leer = False
            temp_out = []
            for line in output:
                if "PARTICLE TRANSPORT" in line:
                    leer = True
                if "LET=(Stot-Srad)" in line:
                    break
                if leer == True:
                    temp_out.append(line)
        if len(temp_out[7:16]) != 0:
            outs.append(temp_out[7:16])
        output.close()
    transports = []
    for out in outs:
        xd = [i.split("  ") for i in out]
        for lista in xd:
            while "" in lista:
                lista.remove("")
        KE = [xd[0][i] for i in list(range(1, 5))]
        KE.append(xd[0][5][0:-1])
        Zeff_beta_sq = [xd[1][i] for i in list(range(1, 5))]
        Zeff_beta_sq.append(xd[1][5][0:-1])
        LET = [xd[2][i] for i in list(range(1, 5))]
        LET.append(xd[2][5][0:-1])
        Res_range = [xd[3][i] for i in list(range(1, 5))]
        Res_range.append(xd[3][5][0:-1])
        DPUF1 = [xd[4][i] for i in list(range(1, 5))]
        DPUF1.append(xd[4][5][0:-1])
        DPUF2 = [xd[5][i] for i in list(range(1, 5))]
        DPUF2.append(xd[5][5][0:-1])
        Edep = [xd[6][i] for i in list(range(1, 5))]
        Edep.append(xd[6][5][0:-1])
        YF = [xd[7][i] for i in list(range(1, 5))]
        YF.append(xd[7][5][0:-1])
        ZF = [xd[8][i] for i in list(range(1, 5))]
        ZF.append(xd[8][5][0:-1])
        transport = {"incident_KE": KE[0], "cell_entry_KE": KE[1], "cell_exit_KE": KE[2], "nucleus_entry_KE": KE[3],
                     "nucleus_exit_KE": KE[4],
                     "incident_Zeff_beta_sq": Zeff_beta_sq[0], "cell_entry_Zeff_beta_sq": Zeff_beta_sq[1],
                     "cell_exit_Zeff_beta_sq": Zeff_beta_sq[2],
                     "nucleus_entry_Zeff_beta_sq": Zeff_beta_sq[3], "nucleus_exit_Zeff_beta_sq": Zeff_beta_sq[4],
                     "incident_LET": LET[0], "cell_entry_LET": LET[1], "cell_exit_LET": LET[2],
                     "nucleus_entry_LET": LET[3], "nucleus_exit_LET": LET[4],
                     "incident_Res_range": Res_range[0], "cell_entry_Res_range": Res_range[2],
                     "cell_exit_Res_range": Res_range[2], "nucleus_entry_Res_range": Res_range[3],
                     "nucleus_exit_Res_range": Res_range[4],
                     "incident_DPUF1": DPUF1[0], "cell_entry_DPUF1": DPUF1[1], "cell_exit_DPUF1": DPUF1[2],
                     "nucleus_entry_DPUF1": DPUF1[3], "nucleus_exit_DPUF1": DPUF1[4],
                     "incident_DPUF2": DPUF2[0], "cell_entry_DPUF2": DPUF2[1], "cell_exit_DPUF2": DPUF2[2],
                     "nucleus_entry_DPUF2": DPUF2[3], "nucleus_exit_DPUF2": DPUF2[4],
                     "incident_Edep": Edep[0], "cell_entry_Edep": Edep[1], "cell_exit_Edep": Edep[2],
                     "nucleus_entry_Edep": Edep[3], "nucleus_exit_Edep": Edep[4],
                     "incident_YF": YF[0], "cell_entry_YF": YF[1], "cell_exit_YF": YF[2], "nucleus_entry_YF": YF[3],
                     "nucleus_exit_YF": YF[4],
                     "incident_ZF": ZF[0], "cell_entry_ZF": ZF[1], "cell_exit_ZF": ZF[2], "nucleus_entry_ZF": ZF[3],
                     "nucleus_exit_ZF": ZF[4]}
        transports.append(transport)
    return transports


def dsb_vs_info(t2s, eje_x, titulo, figura, color):
    y = []
    y_er = []
    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        y.append(tot_dsb)
        y_er.append(tot_dsb_er)
    plt.errorbar(eje_x, y, y_er, linewidth=0.5, elinewidth=1, markeredgewidth=1
                 , capsize=1, capthick=1, marker=figura, color=color, fillstyle='none')
    plt.ylabel('Yield de DSB [clusters/cell]')
    plt.xlabel('LET [keV/um]')
    plt.title(titulo)
    plt.xscale('log')
    plt.yscale('log')


def ssb_vs_info(t2s, info, eje_x, titulo):
    # info son las labels del eje x, puede ser lo que sea.
    fig, ax = plt.subplots()
    y = []
    y_er = []
    x = np.arange(len(info))
    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        y.append(tot_ssb)
        y_er.append(tot_ssb_er)
    ax.errorbar(x, y, y_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1, color="orange")
    ax.set_ylabel('Producción de SSB [clusters/cell]')
    ax.set_xlabel(eje_x)
    ax.set_xticks(x)
    ax.set_xticklabels(info)
    ax.set_title(titulo)


def dsb_and_ssb_and_others_vs_info(t2s, info, eje_x, titulo):
    # info son las labels del eje x, puede ser lo que sea.
    fig, ax = plt.subplots()
    y1 = []
    y1_er = []
    y2 = []
    y2_er = []
    y3 = []
    y3_er = []
    y4 = []
    y4_er = []
    x = np.arange(len(info))
    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        y1.append(tot_dsb)
        y1_er.append(tot_dsb_er)
        y2.append(tot_ssb)
        y2_er.append(tot_ssb_er)
        y3.append(tot_others)
        y3_er.append(tot_others_er)
        y4.append(tot_all)
        y4_er.append(tot_all_er)
    ax.errorbar(x, y1, y1_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                label="Clusters DSB")
    ax.errorbar(x, y2, y2_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                label="Clusters SSB")
    ax.errorbar(x, y3, y3_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                label="Otros clusters")
    ax.errorbar(x, y4, y4_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                label="Total clusters")
    ax.legend()
    ax.set_title(titulo)
    ax.set_ylabel('Producción de clusters [clusters/cell]')
    ax.set_xlabel(eje_x)
    ax.set_xticks(x)
    ax.set_xticklabels(info)


def process_prof(ident, particula):  # NECESITA INPUT MANUAL
    cwd = os.getcwd()
    cuantosdat = 0
    # for file in os.listdir(cwd):
    #     if (ident in file) and (file[-4:]==".dat"):
    #         cuantosdat+=1
    for i in list(range(1, 4)):  # CAMBIAR ESTO DEPENDIENDO DE CUANTOS DAT HAY
        dat = open(cwd + "\\" + ident + "_" + str(i) + ".dat")
        contador = 0
        energias = []
        pesos = []
        for linea in dat:
            info = linea.split("\t")
            energias.append(info[0])
            pesos.append(info[1][:-1])
            contador += 1
        peso_tot = sum([float(p) for p in pesos])
        peso_norm = [str(float(p) / peso_tot) for p in pesos]
        fmtd_dat = open("fmtd_" + ident + "_" + str(i) + ".dat", 'w')
        fmtd_dat.write(ident + "_" + str(i) + "\n")
        fmtd_dat.write(str(contador) + "\n")
        for [a, b] in zip(energias, peso_norm):
            fmtd_dat.write(particula + " " + a + " " + b + "\n")


def t_incident_p(path_output):
    # Lee los datos de tabla "INCIDENT PARTICLE", la printea y la retorna
    inicio_tabla = 0
    fin_tabla = -1
    list_file = []
    with open(path_output, "r") as file:
        for contador, linea in enumerate(file):
            if "INCIDENT" in linea:
                inicio_tabla = contador + 1
            elif "PARTICLE TRANSPORT" in linea:
                fin_tabla = contador - 1
            list_file.append(linea.strip())
    list_table = list_file[inicio_tabla:fin_tabla]
    print(list_table)
    return list_table


def t_incident_mxrf(path_output):
    # Lee tabla INCIDENT MXRF y convierte cada fila en un diccionario.
    # input: Ruta archivo .out
    # Output: Lista de diccionarios
    inicio_tabla = 0
    fin_tabla = -1
    list_file = []
    with open(path_output, "r") as file:
        for contador, linea in enumerate(file):
            if "INCIDENT MXRF" in linea:
                inicio_tabla = contador + 7
            elif "ZEB" in linea:
                fin_tabla = contador - 2
            list_file.append(linea.strip())
    list_table = list_file[inicio_tabla:fin_tabla]

    dict_keys = ["ion", "ke", "zeb", "csda", "s_rad", "s_total", "fluence", "dose"]
    list_dicts_mxrf = []
    for data in list_table:
        data_clean = list(filter(len, data.split(' ')))
        dict_mxrf = dict(zip(dict_keys, data_clean))
        list_dicts_mxrf.append(dict_mxrf)
    return list_dicts_mxrf


def t_target_dosimetry(path_output):
    # Lee tabla TARGET DOSIMETRY y convierte cada fila en un diccionario.
    # input: Ruta archivo .out
    # Output: Lista de diccionarios
    inicio_tabla = 0
    fin_tabla = -1
    list_file = []
    with open(path_output, "r") as file:
        for contador, linea in enumerate(file):
            if "TARGET DOSIMETRY" in linea:
                inicio_tabla = contador + 6
            elif "YF=frequency-mean" in linea:
                fin_tabla = contador - 2
            list_file.append(linea.strip())
    list_table = list_file[inicio_tabla:fin_tabla]

    dict_keys = ["ion", "ke", "zeb", "csda", "fluence", "dpuf", "dose", "yf", "yd", "zf"]
    list_dicts_dosimetry = []
    for data in list_table:
        data_clean = list(filter(len, data.split(' ')))
        dict_dosimetry = dict(zip(dict_keys, data_clean))
        list_dicts_dosimetry.append(dict_dosimetry)
    return list_dicts_dosimetry


def t_particle_transport(path_output):
    inicio_tabla = 0
    fin_tabla = -1
    list_file = []
    with open(path_output, "r") as file:
        for contador, linea in enumerate(file):
            if "PARTICLE TRANSPORT" in linea:
                inicio_tabla = contador + 7
            elif "LET=(Stot-Srad);" in linea:
                fin_tabla = contador - 1
            list_file.append(linea.strip())
    list_table = list_file[inicio_tabla:fin_tabla]
    # print(list_table)
    return list_table


def t_dat(path_dat):
    # Lee el .dat y convierte cada fila en un diccionario.
    # input: Ruta archivo .dat
    # Output: Lista de diccionarios

    list_table = []
    with open(path_dat, "r") as file:
        for contador, linea in enumerate(file):
            if contador >= 3:
                list_table.append(linea.strip())
    dict_keys = ["ion", "ke", "normed_weight"]
    list_dicts_dat = []
    for data in list_table:
        data_clean = list(filter(len, data.split(' ')))
        dict_dat = dict(zip(dict_keys, data_clean))
        list_dicts_dat.append(dict_dat)
        print(dict_dat)
    return list_dicts_dat


def allclusters_vs_info(t2s, info, eje_x, titulo):
    # info son las labels del eje x, puede ser lo que sea.
    fig, ax = plt.subplots()
    y = []
    y_er = []
    x = np.arange(len(info))
    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        y.append(tot_all)
        y_er.append(tot_all_er)
    ax.errorbar(x, y, y_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1, color="red")
    ax.set_ylabel('Número total de clusters (DSB+SSB+BD) [clusters/cell]')
    ax.set_xlabel(eje_x)
    ax.set_xticks(x)
    ax.set_xticklabels(info)
    ax.set_title(titulo)


def others_vs_info(t2s, info, eje_x, titulo):
    # info son las labels del eje x, puede ser lo que sea.
    fig, ax = plt.subplots()
    y = []
    y_er = []
    x = np.arange(len(info))
    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        y.append(tot_others)
        y_er.append(tot_others_er)
    ax.errorbar(x, y, y_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1, color="green")
    ax.set_ylabel('Producción de clusters sin SB [clusters/cell]')
    ax.set_xlabel(eje_x)
    ax.set_xticks(x)
    ax.set_xticklabels(info)
    ax.set_title(titulo)


def dsb_ssb_and_others_vs_info_separated(t2s, info, eje_x, titulo):
    # info son las labels del eje x, puede ser lo que sea.
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    y1 = []
    y1_er = []
    y2 = []
    y2_er = []
    y3 = []
    y3_er = []
    y4 = []
    y4_er = []
    x = np.arange(len(info))
    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        y1.append(tot_dsb)
        y1_er.append(tot_dsb_er)
        y2.append(tot_ssb)
        y2_er.append(tot_ssb_er)
        y3.append(tot_others)
        y3_er.append(tot_others_er)
        y4.append(tot_all)
        y4_er.append(tot_all_er)
    ax1.errorbar(x, y1, y1_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters DSB")
    ax2.errorbar(x, y2, y2_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters SSB", color="orange")
    ax3.errorbar(x, y3, y3_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Otros clusters", color="green")
    ax4.errorbar(x, y4, y4_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Total clusters", color="red")
    fig.suptitle(titulo)
    ax3.set_ylabel('Producción de clusters [clusters/cell]')
    ax1.set_xlabel(eje_x)
    ax2.set_xlabel(eje_x)
    ax3.set_xlabel(eje_x)
    ax4.set_xlabel(eje_x)
    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax4.legend()
    ax1.set_xticks(x)
    ax1.set_xticklabels(info)
    ax2.set_xticks(x)
    ax2.set_xticklabels(info)
    ax3.set_xticks(x)
    ax3.set_xticklabels(info)
    ax4.set_xticks(x)
    ax4.set_xticklabels(info)


def compare_dsb_ssb_and_others_vs_info_separated(t2s, t2sx, info, eje_x, titulo, label1, label2):
    # info son las labels del eje x, puede ser lo que sea.
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    y1 = []
    y1_er = []
    y2 = []
    y2_er = []
    y3 = []
    y3_er = []
    y4 = []
    y4_er = []
    y1x = []
    y1_erx = []
    y2x = []
    y2_erx = []
    y3x = []
    y3_erx = []
    y4x = []
    y4_erx = []
    x = np.arange(len(info))
    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        y1.append(tot_dsb)
        y1_er.append(tot_dsb_er)
        y2.append(tot_ssb)
        y2_er.append(tot_ssb_er)
        y3.append(tot_others)
        y3_er.append(tot_others_er)
        y4.append(tot_all)
        y4_er.append(tot_all_er)
    for j in t2sx:
        [(tot_dsbx, tot_dsb_erx), (tot_ssbx, tot_ssb_erx), (tot_othersx, tot_others_erx),
         (tot_allx, tot_all_erx)] = tot_cluster(j)
        y1x.append(tot_dsbx)
        y1_erx.append(tot_dsb_erx)
        y2x.append(tot_ssbx)
        y2_erx.append(tot_ssb_erx)
        y3x.append(tot_othersx)
        y3_erx.append(tot_others_erx)  # TERMINAR DE PONER LAS X
        y4x.append(tot_allx)
        y4_erx.append(tot_all_erx)
    ax1.errorbar(x, y1, y1_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters DSB " + label1)
    ax2.errorbar(x, y2, y2_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters SSB " + label1)
    ax3.errorbar(x, y3, y3_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Otros clusters " + label1)
    ax4.errorbar(x, y4, y4_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Total clusters " + label1)
    ax1.errorbar(x, y1x, y1_erx, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters DSB " + label2)
    ax2.errorbar(x, y2x, y2_erx, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters SSB " + label2)
    ax3.errorbar(x, y3x, y3_erx, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Otros clusters " + label2)
    ax4.errorbar(x, y4x, y4_erx, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Total clusters " + label2)
    fig.suptitle(titulo)
    ax3.set_ylabel('Producción de clusters [clusters/cell]')
    ax1.set_xlabel(eje_x)
    ax2.set_xlabel(eje_x)
    ax3.set_xlabel(eje_x)
    ax4.set_xlabel(eje_x)
    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax4.legend()
    ax1.set_xticks(x)
    ax1.set_xticklabels(info)
    ax2.set_xticks(x)
    ax2.set_xticklabels(info)
    ax3.set_xticks(x)
    ax3.set_xticklabels(info)
    ax4.set_xticks(x)
    ax4.set_xticklabels(info)


def csv_to_list(ident):
    cwd = os.getcwd()
    dir = cwd + "\\" + ident
    if os.path.exists(dir):
        x1 = []
        y1 = []
        x2 = []
        y2 = []
        archivo = open(dir, 'r')
        cont = 0
        for linea in archivo:
            sep = linea.split(',')
            if cont >= 2:
                x1.append(sep[0])
                y1.append(sep[1])
                x2.append(sep[2])
                y2.append(sep[3])
            cont += 1
        return [x1, y1, x2, y2]
    else:
        print("El archivo no existe.")
        return None


def compare_dsb_vs_info_separated_wcsv(csv, t2s, t2sx, info, eje_x, titulo, label1, label2):
    # info son las labels del eje x, puede ser lo que sea.
    fig, ax1 = plt.subplots()
    y1 = []
    y1_er = []
    y1x = []
    y1_erx = []
    x = [float(i) for i in info]
    [x1c, y1c, x2c, y2c] = csv_to_list(csv)
    x1c = [i for i in x1c if i != '']
    y1c = [i for i in y1c if i != '']
    x2c = [i for i in x2c if i != '']
    y2c = [i for i in y2c if i != '\n']
    x1c = [float(i) for i in x1c]
    y1c = [float(i) for i in y1c]
    x2c = [float(i) for i in x2c]
    y2c = [float(i.strip("\n")) for i in y2c]
    print(x1c)
    print(y1c)
    print(x2c)
    print(y2c)
    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        y1.append(tot_dsb)
        y1_er.append(tot_dsb_er)
    for j in t2sx:
        [(tot_dsbx, tot_dsb_erx), (tot_ssbx, tot_ssb_erx), (tot_othersx, tot_others_erx),
         (tot_allx, tot_all_erx)] = tot_cluster(j)
        y1x.append(tot_dsbx)
        y1_erx.append(tot_dsb_erx)
    ax1.errorbar(x, y1, y1_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="oxic DSB MCDS")
    ax1.errorbar(x, y1x, y1_erx, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="anoxic DSB MCDS")
    ax1.scatter(x2c, y2c, label="anoxic DSB paper", marker='+', color='red')
    ax1.scatter(x1c, y1c, label="oxic DSB paper", marker='x', color='green')
    x1ca = np.array(x1c)
    y1ca = np.array(y1c)
    x2ca = np.array(x2c)
    y2ca = np.array(y2c)
    mb1 = np.polyfit(x1c, y1c, 1)
    mb2 = np.polyfit(x2c, y2c, 1)
    print("Ecuación de recta óxica paper: y={}x+{}".format(mb1[0], mb1[1]))
    print("Ecuación de recta anóxica paper: y={}x+{}".format(mb2[0], mb2[1]))
    print("Ecuación de recta óxica datos: y={}x+{}".format((y1[-1] - y1[0]) / (x[-1] - x[0]),
                                                           (y1[-1] - y1[0]) / (x[-1] - x[0]) * x[0] - y1[0]))
    print("Ecuación de recta anóxica datos: y={}x+{}".format((y1x[-1] - y1x[0]) / (x[-1] - x[0]),
                                                             (y1x[-1] - y1x[0]) / (x[-1] - x[0]) * x[0] - y1x[0]))
    ax1.plot(x1ca, mb1[0] * x1ca + mb1[1], markersize=0, color='green', linewidth=0.5)
    ax1.plot(x2ca, mb2[0] * x2ca + mb2[1], markersize=0, color='red', linewidth=0.5)
    fig.suptitle(titulo)
    ax1.set_ylabel('Producción de clusters DSB [clusters/cell]')
    ax1.set_xlabel(eje_x)
    ax1.legend()
    # ax1.set_xticks(x)
    # ax1.set_xticklabels(info)


def mcds_inp_gen_and_tester_for_frankenberg(ident):
    # Puntos en el eje x predeterminados ["100","200","300","400","500","600","700","800","900","1000","1100","1200","1300","1400","1500","1600","1700","1800","1900","2000","2100","2200","2300","2400","2500"]
    path_mcds = os.path.join('mcds', 'bin', 'mcds.exe')
    lista_dosis = []
    while True:
        dosis = input(
            "Ingrese dosis para la generación de inputs, ingrese <d> para utilizar los valores por defecto en Frankenberg o <t> para terminar la lista: ")
        dosis_prueba = dosis
        try:
            float(dosis_prueba)
            lista_dosis.append(dosis)
        except:
            if dosis == "d":
                lista_dosis = ["100", "200", "300", "400", "500", "600", "700", "800", "900", "1000", "1100", "1200",
                               "1300", "1400", "1500", "1600", "1700", "1800", "1900", "2000", "2100", "2200", "2300",
                               "2400", "2500"]
                break
            elif dosis == "t":
                break
            else:
                print("Ha tenido un error de digitación, intente nuevamente")
    cwd = os.getcwd()
    dir = cwd + "\\" + ident
    # Input
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.mkdir(dir)
    n = int(input("Indique cuantas pruebas desea realizar: "))
    contador = 0
    while contador < n:
        contador += 1
        print("Ingrese los parámetros deseados para la prueba {}".format(contador))
        m0 = input("Ingrese valor de OER máximo de prueba: ")
        k = input("Ingrese valor de concentración de referencia K de prueba: ")
        q = input("Ingrese valor de parámetro q: ")
        r = input("Ingrese valor de parámetro r: ")
        paramsdeltest = "m0={}_k={}_q={}_r={}".format(m0, k, q, r)
        dirprueba = cwd + "\\" + ident + "\\prueba " + str(contador) + " " + paramsdeltest
        diroxic = dirprueba + "\\" + ident + "_oxic_" + paramsdeltest
        diranoxic = dirprueba + "\\" + ident + "_anoxic_" + paramsdeltest
        os.mkdir(dirprueba)
        os.mkdir(diroxic)
        os.mkdir(diranoxic)
        cont = 0
        for dose in lista_dosis:
            inp_ox = mcds_inp(inp_cell_dna="0.012", inp_cell_ndia="1.5", inp_cell_cdia="5", inp_radx_par="e",
                              inp_radx_ke="30", inp_radx_ad=dose, inp_evo2_po2="21", inp_evo2_m0=m0, inp_evo2_k=k,
                              inp_evo2_q=q, inp_evo2_r=r, inp_simcon_nocs="10000")
            inp_anox = mcds_inp(inp_cell_dna="0.012", inp_cell_ndia="1.5", inp_cell_cdia="5", inp_radx_par="e",
                                inp_radx_ke="30", inp_radx_ad=dose, inp_evo2_po2="0", inp_evo2_m0=m0, inp_evo2_k=k,
                                inp_evo2_q=q, inp_evo2_r=r, inp_simcon_nocs="10000")
            texto_input_ox = open(diroxic + "\\" + ident + "_oxic_" + paramsdeltest + "_{}".format(cont) + ".inp", 'w')
            texto_input_ox.write(inp_ox)
            texto_input_ox.close()
            texto_input_anox = open(diranoxic + "\\" + ident + "_anoxic_" + paramsdeltest + "_{}".format(cont) + ".inp",
                                    'w')
            texto_input_anox.write(inp_anox)
            texto_input_anox.close()
            cont += 1
    contador = 0
    for carpeta_prueba in os.listdir(dir):
        for anoxic_oxic in os.listdir(
                dir + "\\" + carpeta_prueba):  # Para cada input se escribe un .bat en la carpeta ident_bats y se corre; los .out quedan en la carpeta ident
            for test in os.listdir(dir + "\\" + carpeta_prueba + "\\" + anoxic_oxic):
                if test[-3:] == "inp":
                    ruta = os.path.join(dir + "\\" + carpeta_prueba + "\\" + anoxic_oxic, test)
                    bat = open(dir + "\\" + carpeta_prueba + "\\" + anoxic_oxic + "\\" + ident + "_bat_" + str(
                        contador) + ".bat", 'w')
                    bat.write(mcds_bat(ruta, path_mcds))
                    bat.close()
                    subprocess.call(
                        [r'{}'.format(dir + "\\" + carpeta_prueba + "\\" + anoxic_oxic + "\\" + ident + "_bat_" + str(
                            contador) + ".bat")])
                    contador += 1
        contador = 0
    return


def test_info_alt(ident):  # Generar una tupla, un término con todas la tablas y el otro con las labels
    cwd = os.getcwd()
    file_numbers = []
    alltabs = []  # lista con todas las tablas de los outputs [[[t1],[t2]...,[]]]=[mcds_of(out1),mcds_of(out2),...]
    for file in os.listdir(cwd + "\\" + ident):
        if file.endswith(".out"):
            file_numberdotout = ''.join(file.split("_")[-1:])
            file_number = int(file_numberdotout.replace('.out', ''))
            file_numbers.append(file_number)
            alltabs.append(mcds_of(cwd + "\\" + ident + "\\" + file))
    alltabs_ord = list(range(len(alltabs)))
    cont = 0
    for i in file_numbers:
        alltabs_ord[i] = alltabs[cont]
        cont += 1
    return alltabs_ord


def mcds_inp_gen_and_tester_for_frankenberg_alt(ident):
    # Puntos en el eje x predeterminados ["100","200","300","400","500","600","700","800","900","1000","1100","1200","1300","1400","1500","1600","1700","1800","1900","2000","2100","2200","2300","2400","2500"]
    path_mcds = os.path.join('mcds', 'bin', 'mcds.exe')
    lista_dosis = []
    while True:
        dosis = input(
            "Ingrese dosis para la generación de inputs, ingrese <d> para utilizar los valores por defecto en Frankenberg o <t> para terminar la lista: ")
        dosis_prueba = dosis
        try:
            float(dosis_prueba)
            lista_dosis.append(dosis)
        except:
            if dosis == "d":
                lista_dosis = ["100", "200", "300", "400", "500", "600", "700", "800", "900", "1000", "1100", "1200",
                               "1300", "1400", "1500", "1600", "1700", "1800", "1900", "2000", "2100", "2200", "2300",
                               "2400", "2500"]
                break
            elif dosis == "t":
                break
            else:
                print("Ha tenido un error de digitación, intente nuevamente")
    cwd = os.getcwd()
    dir = cwd + "\\" + ident
    # Input
    if os.path.exists(dir):
        shutil.rmtree(dir)
    os.mkdir(dir)
    n = int(input("Indique cuantas pruebas desea realizar: "))
    contador = 0
    while contador < n:
        contador += 1
        print("Ingrese los parámetros deseados para la prueba {}".format(contador))
        po2 = input("Ingrese valor de concentración de oxígeno máxima de prueba: ")
        k = input("Ingrese valor de concentración de referencia K de prueba: ")
        q = input("Ingrese valor de parámetro q: ")
        r = input("Ingrese valor de parámetro r: ")
        paramsdeltest = "po2={}_k={}_q={}_r={}".format(po2, k, q, r)
        dirprueba = cwd + "\\" + ident + "\\prueba " + str(contador) + " " + paramsdeltest
        diroxic = dirprueba + "\\" + ident + "_oxic_" + paramsdeltest
        diranoxic = dirprueba + "\\" + ident + "_anoxic_" + paramsdeltest
        os.mkdir(dirprueba)
        os.mkdir(diroxic)
        os.mkdir(diranoxic)
        cont = 0
        for dose in lista_dosis:
            inp_ox = mcds_inp(inp_cell_dna="0.012", inp_cell_ndia="1.5", inp_cell_cdia="5", inp_radx_par="e",
                              inp_radx_ke="30", inp_radx_ad=dose, inp_evo2_po2=po2, inp_evo2_m0="2.2", inp_evo2_k=k,
                              inp_evo2_q=q, inp_evo2_r=r, inp_simcon_nocs="10000")
            inp_anox = mcds_inp(inp_cell_dna="0.012", inp_cell_ndia="1.5", inp_cell_cdia="5", inp_radx_par="e",
                                inp_radx_ke="30", inp_radx_ad=dose, inp_evo2_po2="0", inp_evo2_m0="2.2", inp_evo2_k=k,
                                inp_evo2_q=q, inp_evo2_r=r, inp_simcon_nocs="10000")
            texto_input_ox = open(diroxic + "\\" + ident + "_oxic_" + paramsdeltest + "_{}".format(cont) + ".inp", 'w')
            texto_input_ox.write(inp_ox)
            texto_input_ox.close()
            texto_input_anox = open(diranoxic + "\\" + ident + "_anoxic_" + paramsdeltest + "_{}".format(cont) + ".inp",
                                    'w')
            texto_input_anox.write(inp_anox)
            texto_input_anox.close()
            cont += 1
    contador = 0
    for carpeta_prueba in os.listdir(dir):
        for anoxic_oxic in os.listdir(
                dir + "\\" + carpeta_prueba):  # Para cada input se escribe un .bat en la carpeta ident_bats y se corre; los .out quedan en la carpeta ident
            for test in os.listdir(dir + "\\" + carpeta_prueba + "\\" + anoxic_oxic):
                if test[-3:] == "inp":
                    ruta = os.path.join(dir + "\\" + carpeta_prueba + "\\" + anoxic_oxic, test)
                    bat = open(dir + "\\" + carpeta_prueba + "\\" + anoxic_oxic + "\\" + ident + "_bat_" + str(
                        contador) + ".bat", 'w')
                    bat.write(mcds_bat(ruta, path_mcds))
                    bat.close()
                    subprocess.call(
                        [r'{}'.format(dir + "\\" + carpeta_prueba + "\\" + anoxic_oxic + "\\" + ident + "_bat_" + str(
                            contador) + ".bat")])
                    contador += 1
        contador = 0
    return


def clusters_vs_energy_and_let(t2s, Es, LETs, titulo):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2)
    y1 = []
    y1_er = []
    y2 = []
    y2_er = []
    Energia = [float(i) for i in Es]
    LET = [float(i) for i in LETs]
    print(Energia)
    print(LET)
    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        y1.append(tot_dsb)
        y1_er.append(tot_dsb_er)
        y2.append(tot_ssb)
        y2_er.append(tot_ssb_er)
    print(y1)
    print(y2)

    ax1.errorbar(Energia, y1, y1_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters DSB vs Energia")
    ax2.errorbar(Energia, y2, y2_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters SSB vs Energia")
    ax3.errorbar(LET, y1, y1_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters DSB vs LET")
    ax4.errorbar(LET, y2, y2_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters SSB vs LET")
    fig.suptitle(titulo)
    ax3.set_ylabel('Producción de clusters [clusters/cell]')
    ax1.set_xlabel("Energía [MeV]")
    ax1.set_xscale('log')
    ax2.set_xlabel("Energía [MeV]")
    ax2.set_xscale('log')
    ax3.set_xlabel("LET[keV/um]")
    ax4.set_xlabel("LET[keV/um]")
    ax1.legend()
    ax2.legend()
    ax3.legend()
    ax4.legend()


def clusters_vs_energy(t2s, Es, titulo):
    fig, ax1 = plt.subplots()
    y1 = []
    y1_er = []
    y2 = []
    y2_er = []
    y3 = []
    y3_er = []
    y4 = []
    y4_er = []
    Energia = [float(i) for i in Es]
    print(Energia)
    for i in t2s:
        [(tot_dsb, tot_dsb_er), (tot_ssb, tot_ssb_er), (tot_others, tot_others_er),
         (tot_all, tot_all_er)] = tot_cluster(i)
        y1.append(tot_dsb)
        y1_er.append(tot_dsb_er)
        y2.append(tot_ssb)
        y2_er.append(tot_ssb_er)
        y3.append(tot_others)
        y3_er.append(tot_others_er)
        y4.append(tot_all)
        y4_er.append(tot_all_er)
    ax1.errorbar(Energia, y1, y1_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters DSB")
    ax1.errorbar(Energia, y2, y2_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters SSB")
    ax1.errorbar(Energia, y3, y3_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Clusters sin SB")
    ax1.errorbar(Energia, y4, y4_er, linewidth=0.5, elinewidth=1, markeredgewidth=1, capsize=1, capthick=1,
                 label="Total de clusters")
    fig.suptitle(titulo)
    ax1.set_ylabel('Producción de clusters [clusters/cell]')
    ax1.set_xlabel("Energía [MeV]")
    ax1.set_xscale('log')
    ax1.legend()


def LET_vs_energy(Es, LETs, titulo):
    fig, ax1 = plt.subplots()
    Energia = [float(i) for i in Es]
    LET = [float(i) for i in LETs]
    ax1.plot(Energia, LET)
    fig.suptitle(titulo)
    ax1.set_xlabel("Energía [MeV]")
    ax1.set_xscale('log')
    ax1.set_ylabel("LET [keV/um]")


def LET_vs_energy_wdb(Es, LETs, titulo, path_to_kassis, path_to_nist):
    fig, ax1 = plt.subplots()
    Energia = [float(i) for i in Es]
    LET = [float(i) for i in LETs]
    E_kassis = []
    LET_kassis = []
    E_nist = []
    LET_nist = []
    with open(path_to_kassis, 'r') as csv_kassis:
        for line in csv_kassis:
            datos = line.split(';')
            E_kassis.append(float(datos[1].replace(',', '.')))
            LET_kassis.append(float(datos[2].replace(',', '.')))
    with open(path_to_nist, 'r') as csv_nist:
        for line in csv_nist:
            datos = line.split(';')
            E_nist.append(float(datos[2].replace(',', '.')))
            LET_nist.append(float(datos[4].replace(',', '.')))
    ax1.errorbar(Energia, LET, label='MCDS', marker='o')
    ax1.errorbar(E_nist, LET_nist, label='NIST database', marker='+')
    ax1.errorbar(E_kassis, LET_kassis, label='Kassis 2011', marker='x')
    fig.suptitle(titulo)
    ax1.set_xlabel("Energía [MeV]")
    ax1.set_xscale('log')
    ax1.set_ylabel("LET [keV/um]")
    ax1.legend()


def read_preparam(path_to_output):
    # Siempre es para condiciones NORMÓXICAS
    # Lee los datos de tabla "DAMAGE FORMATION AND CLUSTERING", la printea y la retorna
    list_file = []
    tabla = False
    with open(path_to_output, "r") as file:
        for contador, linea in enumerate(file):
            if "DAMAGE FORMATION AND CLUSTERING (normoxic conditions)" in linea:
                tabla = True
            if tabla == True:
                p1 = linea.strip()
                p2 = p1.split(" ")[0]
                list_file.append(p2)
            if "chemical repair probability" in linea:
                break
    list_file.pop(0)
    list_file.pop(-2)
    list_file.pop(-2)
    table_dict = {"nseg": list_file[0], "sigSb": list_file[1], "sigBd": list_file[2], "f": list_file[3],
                  "Nmin": list_file[4],
                  "Ndsb": list_file[5], "Bl/Bd": list_file[6], "pcr": list_file[-1]}
    return table_dict


def intersection(lst1, lst2):
    lst3 = [value for value in lst1 if value in lst2]
    return lst3


# def distrib_sb(pos_Sb,sigSb,nseg):
#     for i in range(sigSb):
#          while True:
#             basepair = random.choice(list(range(nseg)))
#             strand = random.choice([0, 1])
#             if [basepair, strand] not in pos_Sb:
#                  pos_Sb.append([basepair,strand])
#                  break
#     return pos_Sb
# def distrib_bd(pos_Bd,sigBd,nseg):
#     for j in range(sigBd):
#         while True:
#             basepair = random.choice(list(range(nseg)))
#             strand = random.choice([0,1])
#             if [basepair,strand] not in pos_Bd:
#                 pos_Bd.append([basepair,strand])
#                 break
#     return pos_Bd

def mcds_of_clusters(file_route):
    mcds_output = open(file_route, 'r')
    # DE LA LINEA 0 A LA 21 ESTÁN LAS CARACTERÍSTICAS DE LA CÉLULA
    # EN LOS ARCHIVOS CON .DAT, LA INFORMACIÓN DEL CAMPO DE RADIACIÓN COMIENZA EN LA LÍNEA 23
    # EN LOS ARCHIVOS SIN .DAT, LA INFORMACIÓN DE LA RADIACIÓN COMIENZA EN LA LINEA 24 Y LOS RESULTADOS EN LA 80
    # LOS ARCHIVOS SIEMPRE TIENEN 6 TABLAS
    contador = 0
    donde_tablas = []
    lista_output = []
    for linea in mcds_output:
        if "number of cells (nocs)" in linea:
            l = linea.strip()
            lst = l.split(' ')
            nocs = lst[0]
        if linea[0:5] == "TABLE":
            donde_tablas.append(contador)
        lista_output.append(linea)
        contador += 1
    t2 = lista_output[donde_tablas[1]:donde_tablas[2]]
    del t2[-4:]
    del t2[:5]
    mcds_output.close()
    filtr = list(
        filter(None, (t2[-1].strip()).split(" ")))  # deja una lista con los valores aislados de la fila "total"
    meandsb = float(filtr[1])
    errdsb = float(filtr[2])
    meanssb = float(filtr[3])
    errssb = float(filtr[4])
    meanbd = float(filtr[5])
    errbd = float(filtr[6])
    meanall = float(filtr[7])
    errall = float(filtr[8])
    return [float(nocs), [meandsb, errdsb, meanssb, errssb, meanbd, errbd, meanall, errall]]


def zscore(mean, mu, sigma, n):
    return (mean - mu) / sigma * n ** 0.5


def z_pvalue(zscore):
    return 2 * (1 - stats.norm.cdf(abs(zscore)))


def total_fluence(list_dicts_dosimetry):
    F=0
    for dosim in list_dicts_dosimetry:
        F+=float(dosim["fluence"])
    return F


def mcds_of_clusters_lmbda(file_route):
    mcds_output = open(file_route, 'r')
    # DE LA LINEA 0 A LA 21 ESTÁN LAS CARACTERÍSTICAS DE LA CÉLULA
    # EN LOS ARCHIVOS CON .DAT, LA INFORMACIÓN DEL CAMPO DE RADIACIÓN COMIENZA EN LA LÍNEA 23
    # EN LOS ARCHIVOS SIN .DAT, LA INFORMACIÓN DE LA RADIACIÓN COMIENZA EN LA LINEA 24 Y LOS RESULTADOS EN LA 80
    # LOS ARCHIVOS SIEMPRE TIENEN 6 TABLAS
    contador = 0
    donde_tablas = []
    lista_output = []
    for linea in mcds_output:
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
    print(t2[-1])
    print(t3[-1])
    filtr2 = list(
        filter(None, (t2[-1].strip()).split(" ")))  # deja una lista con los valores aislados de la fila "total"
    filtr3 =list(
        filter(None, (t3[-1].strip()).split(" ")))
    Y = float(filtr2[1])
    Yerr = float(filtr2[2])
    lmbda = float(filtr3[1])
    lmbdaerr = float(filtr3[2])
    return Y,Yerr,lmbda,lmbdaerr