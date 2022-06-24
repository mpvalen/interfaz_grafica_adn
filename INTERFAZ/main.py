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

    logica.senal_info_plots_backend.connect(ventana_principal.recibir_info_plots)
    ventana_principal.show()
    popup_inicio.show()
    sys.exit(app.exec_())
