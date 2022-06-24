import matplotlib.pyplot as plt
import numpy as np
norm_dose=0.5
##### ESTE CÓDIGO ES PARA COMPARAR OUTPUTS DE VERSIÓN ANTIGUA YA INEXISTENTE CON VERSIÓN NUEVA EN LECTURA DE DATOS


# data_antiguo=open('proc_prueba_tab_deprecated.lis')
data_nuevo=open('proc_wouters1_spectrum_data/proc_wouters1_spectrum_data_{}Gy'.format(norm_dose))
# next(data_antiguo)
next(data_nuevo)

depths_mm=[]
doses=[]
doseerrs=[]
dsbyields=[]
dsbyielderrs=[]
lmbdas=[]
lmbdaerrs=[]
survs=[]
surverrs=[]
# for line in data_antiguo: #line.split = Profund[mm] D[A.U.]   D-Error    DSB-Yield  Yield-Error  Lambda  Lambda-Error    S      S-Error
#     depth_mm=float(line.split(' ')[0])
#     dose=float(line.split(' ')[1])
#     doseerr=float(line.split(' ')[2])
#     dsbyield=float(line.split(' ')[3])
#     dsbyielderr=float(line.split(' ')[4])
#     lmbda=float(line.split(' ')[5])
#     lmbdaerr=float(line.split(' ')[6])
#     surv=float(line.split(' ')[7])
#     surverr=float(line.split(' ')[8])
#
#     depths_mm.append(depth_mm)
#     doses.append(dose)
#     doseerrs.append(doseerr)
#     dsbyields.append(dsbyield)
#     dsbyielderrs.append(dsbyielderr)
#     lmbdas.append(lmbda)
#     lmbdaerrs.append(lmbdaerr)
#     survs.append(surv)
#     surverrs.append(surverr)


depths_mm2=[]
doses2=[]
doseerrs2=[]
dsbyields2=[]
dsbyielderrs2=[]
lmbdas2=[]
lmbdaerrs2=[]
survs2=[]
surverrs2=[]
for line in data_nuevo: #line.split = Profund[mm] D[A.U.]   D-Error    DSB-Yield  Yield-Error  Lambda  Lambda-Error    S      S-Error
    depth_mm=float(line.split(' ')[0])
    dose=float(line.split(' ')[1])
    doseerr=float(line.split(' ')[2])
    dsbyield=float(line.split(' ')[3])
    dsbyielderr=float(line.split(' ')[4])
    lmbda=float(line.split(' ')[5])
    lmbdaerr=float(line.split(' ')[6])
    surv=float(line.split(' ')[7])
    surverr=float(line.split(' ')[8])

    depths_mm2.append(depth_mm)
    doses2.append(dose)
    doseerrs2.append(doseerr)
    dsbyields2.append(dsbyield)
    dsbyielderrs2.append(dsbyielderr)
    lmbdas2.append(lmbda)
    lmbdaerrs2.append(lmbdaerr)
    survs2.append(surv)
    surverrs2.append(surverr)

def fluka_to_data(tablispath,detector_depths):
    #Lee las tablas del archivo tab lis y escribe una nueva tabla más ordenada
    #en formato profundidad - energía - peso - error. También devuelve las mismas
    #tablas directamente en formato numérico si eso es lo que conviene.

    tablis=open(tablispath,'r')#lectura de tabla de fluka de espectros
    ini_pos_tab=[]
    fin_pos_tab=[]
    data=[]
    table_reading=False
    for i,line in enumerate(tablis): #lectura linea por linea de la tabla
        list_line=line.split(' ')
        list_line_stripped=[txt.strip() for txt in list_line]
        list_line_stripped=list(filter(None,list_line_stripped)) #procesamiento de la linea, se deja limpio cada dato
        data.append(list_line_stripped) #aquí está cada linea limpia
        if "Detector" in list_line_stripped: #si la linea corresponde al header de una tabla de fluencia se registra
            ini_pos_tab.append(i + 2)        #donde comienza la tabla
            table_reading=True
        if table_reading==True and len(list_line_stripped)==0: #si la linea está vacía implica que se acabó la lista y
            fin_pos_tab.append(i)                              #se indica donde ocurre
            table_reading=False
    all_tabs=[]
    for n_tab in range(len(ini_pos_tab)): #se busca en el registro de inicios de tabla donde inician y terminan las listas
        ini=ini_pos_tab[n_tab]            #y se extraen de la variable data
        fin=fin_pos_tab[n_tab]
        pre_final_tab=data[ini:fin]
        final_tab=[]

        for line in pre_final_tab: #se escribe el nuevo archivo
            E=(float(line[0])/2+float(line[1])/2)*1000
            W=float(line[2])
            We=float(line[3])
            newline=[detector_depths[n_tab],E,W,We]
            final_tab.append(newline)
        all_tabs.append(final_tab) #se guardan las tablas nuevas en formato numérico también
    return all_tabs #retorna todas las tablas, cada tabla es un conjunto de listas con profundidad, energía, peso, error
from fluka_to_data import lector_spectrum_data_FLUKA

# Ebins,spectrum_avg,spectrum_std=lector_spectrum_data_FLUKA("D:\\Universidad\\"
#                                             "Cellular-Response\\"
#                                             "FLUKA\\"
#                                             "prueba_corrientes_spectrum_data",
#                                             depths_mm)
#
# espectros_antiguos=fluka_to_data("D:\\Universidad\\Cellular-Response\\RESPONSE\\sim1_fluencias\\sim1_99_tab.lis",
#                                  depths_mm)

# Ws=[]
# Wes=[]
# for spec_at_depth in espectros_antiguos:
#     W_at_depth=[]
#     We_at_depth=[]
#     for bin in spec_at_depth:
#         W=bin[2]
#         We=bin[3]
#         W_at_depth.append(W)
#         We_at_depth.append(We)
#     Ws.append(W_at_depth)
#     Wes.append(We_at_depth)
#

# PARA VISUALIZAR ESPECTROS PROMEDIADOS.
# contador=0
# maxspec=200
# n_depths=len(depths_mm)
#
# for i in range(n_depths):
#     plt.errorbar(Ebins,spectrum_avg[i],spectrum_std[i],
#                  color='black',capsize=5,label='Read ASCII')
#     plt.errorbar(Ebins,np.array(Ws[i]),np.array(Wes[i])*np.array(Ws[i])/100,
#                  color='red',capsize=5,linestyle='--',label='Read tab.lis')
#     plt.legend()
#     plt.ylabel("Peso (corriente o fluencia)")
#     plt.xlabel("Energía [MeV]")
#     plt.ylim([0,maxspec])
#     plt.title('Profundidad: {}mm\nruns averaged'.format(contador))
#     plt.draw()
#     plt.pause(0.001)
#     plt.clf()
#     contador+=1
# plt.show()

i=100
# plt.errorbar(depths_mm2,doses2,doseerrs2,
#                  color='black',capsize=5,label='New code dose')
plt.errorbar(depths_mm2,survs2,surverrs2,
                 color='black',capsize=5,label='New code survival')

depths_wouters=[]
survs_wouters=[]
surverrs_wouters=[]
with open('wouters_old_code/{}Gy_plotlog.txt'.format(norm_dose), 'r') as plot:
    for point in plot:
        point_float=[float(i) for i in point.split(' ')]
        depths_wouters.append(point_float[0])
        survs_wouters.append(point_float[1])
        surverrs_wouters.append(point_float[2])
plt.errorbar(depths_wouters,survs_wouters,surverrs_wouters,
                 color='red',capsize=5,label='Old code survival')

doses_depths_wouters=[]
doses_wouters=[]
with open('doses_log_normalized.txt','r') as plot:
    for point in plot:
        point_float=[float(i) for i in point.split(' ')]
        doses_depths_wouters.append(point_float[0]/1.05)
        doses_wouters.append(point_float[1]*norm_dose)
# plt.plot(doses_depths_wouters,doses_wouters,color='red',label='Old code dose')

depths_yield_log_wouters=[]
yield_log_wouters=[]
lambda_log_wouters=[]
with open('wouters_old_yield_log_v79.txt','r') as log:
    next(log)
    for line in log:
        depths_yield_log_wouters.append(float(line.split(' ')[0]))
        yield_log_wouters.append(float(line.split(' ')[1]))
        lambda_log_wouters.append(float(line.split(' ')[3]))

SF_WOUTERS_DATA = open('wouters_exp/SFE1_{}GY_WOUTERS.txt'.format(norm_dose), 'r')
SF_WOUTERS = []
DEPTHS_xGY_WOUTERS = []
for line in SF_WOUTERS_DATA:
    info = line.split(' ')
    d = float(info[0].strip())
    SF = float(info[1].strip())
    DEPTHS_xGY_WOUTERS.append(d)
    SF_WOUTERS.append(SF)

# SF_WOUTERS_DATA = open('wouters_exp/SFE1_1.5GY_WOUTERS.txt', 'r')
# for line in SF_WOUTERS_DATA:
#     info = line.split(' ')
#     d = float(info[0].strip())
#     SF = float(info[1].strip())
#     DEPTHS_xGY_WOUTERS.append(d)
#     SF_WOUTERS.append(SF)

plt.scatter(DEPTHS_xGY_WOUTERS,SF_WOUTERS,label='Wouters exp',color='green')
plt.legend()


fig, ax = plt.subplots()
ax.plot(depths_mm2,dsbyields2,label='New yield',color='red')
ax.plot(depths_mm2,lmbdas2,label='New lambda',color='blue')

ax.plot(depths_yield_log_wouters,yield_log_wouters,label='Old yield',color='red',linestyle='--')
ax.plot(depths_yield_log_wouters,lambda_log_wouters,label='Old lambda',color='blue',linestyle='--')
ax.legend()
plt.show()

############################# PLOTTEAR - PROBAR QUE PROCS SEAN IGUALES O MUUUUY PARECIDOS.