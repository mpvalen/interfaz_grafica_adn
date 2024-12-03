import sys
from PyQt5.QtWidgets import QApplication
from frontend import VentanaPrincipal, VentanaInicio
from backend import Logica



if __name__ == '__main__':
    app = QApplication([])
    # Elementos gráficos (front-end)
    ventana_principal = VentanaPrincipal()
    popup_inicio = VentanaInicio()

    # Elementos de lógica (back-end)
    logica = Logica()
    # Conexión de señales

    popup_inicio.senal_carpeta_identificadora.connect(ventana_principal.recibir_carpeta_ident)
    ventana_principal.senal_generar_input.connect(logica.recibir_input_mcds)
    ventana_principal.senal_lanzar_simulacion.connect(logica.lanzar_simulaciones)
    ventana_principal.senal_fluka_yield.connect(logica.recibir_input_fluka_yield)
    ventana_principal.senal_fluka_survival.connect(logica.recibir_input_fluka_yield)
    ventana_principal.senal_fluka_nueva_carpeta.connect(popup_inicio.nueva_carpeta_fluka)
    ventana_principal.senal_info_plots.connect(logica.info_plots)
    ventana_principal.senal_generar_db.connect(logica.generar_base_datos)
    ventana_principal.senal_nueva_carpeta.connect(popup_inicio.nueva_carpeta)
    ventana_principal.senal_mcds_supervivencia.connect(logica.calcular_supervivencia)
    ventana_principal.ventana_fontsize.senal_fontsize_plot.connect(ventana_principal.change_fontsize_plot)
    ventana_principal.senal_ciclo_celular.connect(logica.info_ciclo_celular)
    ventana_principal.senal_modelo.connect(logica.modelo_escogido)
    ventana_principal.signal_new_wang_params.connect(logica.new_wang_params)
    ventana_principal.signal_PIDE_get_info.connect(logica.PIDE_give_data)
    ventana_principal.signal_PIDE_send_user_info.connect(logica.PIDE_receive_user_data)
    ventana_principal.signal_PIDE_data_ML.connect(logica.PIDE_data_ML)
    ventana_principal.signal_ML_survival.connect(logica.calculate_survival_ML)
    ventana_principal.senal_generar_db_pide.connect(logica.generar_base_datos_pide)
    ventana_principal.signal_db_from_folder.connect(logica.add_database_from_folder)

    logica.senal_info_plots_backend.connect(ventana_principal.recibir_info_plots)
    logica.senal_PIDE_pubnames.connect(ventana_principal.recibir_PIDE_pubnames)
    logica.signal_new_cell.connect(ventana_principal.add_new_cell_menu)
    logica.signal_PIDE_ML_data.connect(ventana_principal.get_PIDE_values_ML)
    ventana_principal.show()
    popup_inicio.show()
    sys.exit(app.exec_())
