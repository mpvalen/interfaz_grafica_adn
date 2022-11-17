import numpy as np
import os
from uncertainties import ufloat
from uncertainties import correlated_values
from uncertainties.umath import *


def mech_model_test(ctype,dose,doseerr,Yld,Ylderr,lmbda,lmbdaerr,DNA,NDIA):
    if dose!=0 and lmbda!=0:
        if ctype.lower()=="v79":
            mu_x = ufloat(0.9568,0.0236)
            mu_y = ufloat(0.0300,0.0177)
            zeta = ufloat(0.0412,0.0209)
            xi = ufloat(0.0608,0.0381)
            eta_1 = ufloat(9.78e-4,0.10e-4)
            eta_infty = ufloat(0.0065,0.0001)
        elif ctype.lower()=="hsg":
            mu_x = ufloat(0.9817,0.0056)
            mu_y = ufloat(0.0891,0.0068)
            zeta = ufloat(0.1025,0.0065)
            xi = ufloat(0.0572,0.0027)
            eta_1 = ufloat(7.26e-4,0.04e-4)
            eta_infty = ufloat(0.0022,0.0001)
        D=ufloat(dose,doseerr)
        Y=ufloat(Yld,Ylderr)
        lmbda=ufloat(lmbda,lmbdaerr)
        N = Y * D  # NÚMERO DE DSBS X CÉLULA
        n_p = Y*D/lmbda * (1 - exp(-lmbda))
        lmbda_p = lmbda / (1 - exp(-lmbda))
        eta = eta_infty - (eta_infty - eta_1) / lmbda_p
        Pint = (1 - exp(-eta * n_p)) / (eta * n_p)
        Ptrack = (1 - exp(-xi * lmbda_p)) / (xi * lmbda_p)
        Pcorrect = mu_x * Pint * Ptrack
        Pcontrib = (1 - exp(-zeta * lmbda_p)) / (zeta * lmbda_p)
        N_death = mu_y * N * Pcontrib * (1 - Pcorrect)
        S = exp(-N_death)
        return S.nominal_value, S.std_dev
    else:
        return 1, 0


def mech_model(ctype,dose,doseerr,Yld,Ylderr,lmbda,lmbdaerr,DNA,NDIA):
    if dose!=0 and lmbda!=0:
        if ctype.lower()=="v79":
            mu_x = ufloat(0.9568,0.0236)
            mu_y = ufloat(0.0300,0.0177)
            zeta = ufloat(0.0412,0.0209)
            xi = ufloat(0.0608,0.0381)
            eta_1 = ufloat(9.78e-4,0.10e-4)
            eta_infty = ufloat(0.0065,0.0001)
        elif ctype.lower()=="hsg":
            mu_x = ufloat(0.9817,0.0056)
            mu_y = ufloat(0.0891,0.0068)
            zeta = ufloat(0.1025,0.0065)
            xi = ufloat(0.0572,0.0027)
            eta_1 = ufloat(7.26e-4,0.04e-4)
            eta_infty = ufloat(0.0022,0.0001)
        D=ufloat(dose,doseerr)
        Y=ufloat(Yld,Ylderr)
        lmbda=ufloat(lmbda,lmbdaerr)
        N = Y * D  # NÚMERO DE DSBS X CÉLULA
        n_p = Y*D/lmbda * (1 - exp(-lmbda))
        lmbda_p = lmbda / (1 - exp(-lmbda))
        eta = eta_infty - (eta_infty - eta_1) / lmbda_p
        Pint = (1 - exp(-eta * n_p)) / (eta * n_p)
        Ptrack = (1 - exp(-xi * lmbda_p)) / (xi * lmbda_p)
        Pcorrect = mu_x * Pint * Ptrack
        Pcontrib = (1 - exp(-zeta * lmbda_p)) / (zeta * lmbda_p)
        N_death = mu_y * N * Pcontrib * (1 - Pcorrect)
        S = exp(-N_death)
        return S.nominal_value, S.std_dev
    else:
        return 1, 0
def lector_dose_data_FLUKA(dose_data_path):
    ascii_file = open(dose_data_path, 'r')
    contador = 0
    values = []
    for line in ascii_file:
        processed_line=list(filter(None, line.strip().split(' ')))
        if "Z coordinate" in line:
            starting_point = float(processed_line[3]) * 10  # starting point in mm
            ending_point = float(processed_line[5]) * 10  # ending point in mm
            nbins = int(processed_line[7])
            bin_width = (ending_point - starting_point) / nbins
        elif contador >= 15:
            values += [float(i) for i in list(filter(None, line.strip().split(' ')))]
        contador += 1
    depths = [starting_point + bin_width * i - bin_width / 2 for i in range(1, nbins + 1)]
    return depths,values

def fully_floatable(list):
    for element in list:
        try:
            float(element)
        except:
            return False
    return True

def lector_spectrum_data_FLUKA(spectrum_data_path,detector_depths):
    n_depths=len(detector_depths)
    spectrums=[] #tablas de fluencia o corriente [run001_depth_0,...,run001_depth_n,...,run005_depth_0,...,run005_depth_n,...]
    for file in os.listdir(spectrum_data_path):
        total_spectrum=[]
        with open(os.path.join(spectrum_data_path,file),'r') as database:
            contador=0
            for line in database:
                stripped_split_line=list(filter(None,line.split(' ')))
                try:
                    if stripped_split_line[1]=='energy' and contador==0:
                        Emin=float(stripped_split_line[4])*1000 #MeV
                        Emax=float(stripped_split_line[6])*1000 #MeV
                        nbins=int(stripped_split_line[8])
                        binwidth=(Emax-Emin)/nbins
                        Ebins=[Emin+binwidth*i-binwidth/2 for i in range(1,nbins+1)]
                        contador+=1
                except:
                    continue
                if fully_floatable(stripped_split_line) == True:
                    total_spectrum += [float(i) for i in stripped_split_line]
        spectrum_separated_by_depth=[total_spectrum[i*nbins:(i+1)*nbins] for i in range(n_depths)]
        if n_depths!=len(total_spectrum)/nbins:
            print("Error: Profundidades dadas no coinciden con espectro de Fluka")
        else:
            spectrums+=spectrum_separated_by_depth

    # PARA VISUALIZAR ESPECTROS.
    # contador=0
    # run=1
    # maxspec=35
    # for spectrum in spectrums:
    #     plt.plot(Ebins,spectrum)
    #     plt.ylabel("Peso (corriente o fluencia)")
    #     plt.xlabel("Energía [MeV]")
    #     plt.ylim([0,maxspec])
    #     if contador == 251:
    #         contador=0
    #         run+=1
    #     plt.title('Profundidad: {}mm\nrun: {}'.format(contador,run))
    #     plt.draw()
    #     plt.pause(0.001)
    #     plt.clf()
    #     contador+=1
    # plt.show()

    spectrum_count=len(os.listdir(spectrum_data_path))

    spectrum_arrays=[]
    spectrum_avg=np.zeros((n_depths,nbins))
    spectrum_variance=np.zeros((n_depths,nbins))

    for i in range(spectrum_count):
        spectrum_arrays.append(np.array(spectrums[i*n_depths:(i+1)*n_depths])*6.28318548)
    for i in range(spectrum_count):
        spectrum_avg+=spectrum_arrays[i]/spectrum_count
    for i in range(spectrum_count):
        spectrum_variance+=(spectrum_arrays[i]-spectrum_avg)**2/spectrum_count

    spectrum_std=np.sqrt(spectrum_variance)

    # PARA VISUALIZAR ESPECTROS PROMEDIADOS.
    # contador=0
    # maxspec=35
    # for i in range(n_depths):
    #     plt.errorbar(Ebins,spectrum_avg_arrays[i],spectrum_variance[i],color='black',capsize=5)
    #     plt.ylabel("Peso (corriente o fluencia)")
    #     plt.xlabel("Energía [MeV]")
    #     plt.ylim([0,maxspec])
    #     plt.title('Profundidad: {}mm\nruns averaged'.format(contador))
    #     plt.draw()
    #     plt.pause(0.001)
    #     plt.clf()
    #     contador+=1
    # plt.show()

    # plt.errorbar(Ebins,spectrum_avg_arrays[0],spectrum_variance[0],color='black',capsize=5)
    # plt.show()
    return Ebins, spectrum_avg, spectrum_std

def database_reader(database_path):
    All_Energies=[]
    All_Yields=[]
    All_Yieldes=[]
    All_Lambdas=[]
    All_Lambdaes=[]
    for filename in os.listdir(database_path):
        Energias=[]
        Yields=[]
        Yieldes=[]
        Lambdas=[]
        Lambdaes=[]
        with open(os.path.join(database_path,filename),'r') as database:
            next(database)
            for line in database:
                numbers=[float(i) for i in list(filter(None, line.strip().split(' ')))]
                if len(numbers)>0:
                    E=numbers[0]
                    LETin=numbers[1]
                    LETavg=numbers[2]
                    LETout=numbers[3]
                    Yield=numbers[4]
                    Yielde=numbers[5]
                    Lambda=numbers[6]
                    Lambdae=numbers[7]
                    Energias.append(E)
                    Yields.append(Yield)
                    Yieldes.append(Yielde)
                    Lambdas.append(Lambda)
                    Lambdaes.append(Lambdae)
        All_Energies.append(Energias)
        All_Yields.append(Yields)
        All_Yieldes.append(Yieldes)
        All_Lambdas.append(Lambdas)
        All_Lambdaes.append(Lambdaes)
    TAll_Yields=np.transpose(np.array(All_Yields))
    TAll_Yieldes=np.transpose(np.array(All_Yieldes))
    TAll_Lambdas=np.transpose(np.array(All_Lambdas))
    TAll_Lambdaes=np.transpose(np.array(All_Lambdaes))
    yields=[]
    yielderrs=[]
    lambdas=[]
    lambdaerrs=[]
    for index in range(len(All_Energies[0])):
        y=TAll_Yields[:][index]
        yerr=TAll_Yieldes[:][index]
        l=TAll_Lambdas[:][index]
        lerr=TAll_Lambdaes[:][index]
        Y=np.sum(y/yerr**2)/np.sum(1/yerr**2)
        Ye=np.sqrt(1/np.sum(1/yerr**2))
        L = np.sum(l / lerr ** 2) / np.sum(1 / lerr ** 2)
        Le = np.sqrt(1 / np.sum(1 / lerr ** 2))
        yields.append(Y)
        yielderrs.append(Ye)
        lambdas.append(L)
        lambdaerrs.append(Le)
    energies=All_Energies[0]
    return energies,yields,yielderrs,lambdas,lambdaerrs

def fluka_to_data(spectrum_data_path,dose_data_path,database_path,
                  detector_depths=[i/2 for i in range(0,101)],ctype='v79',DNA=5.6,NDIA=5,dose_norm_max=1.5,
                  output_folder='proc_spectrum_data'):
    #Lee las tablas del archivo tab lis y escribe una nueva tabla más ordenada
    #en formato profundidad - energía - peso - error. También devuelve las mismas
    #tablas directamente en formato numérico si eso es lo que conviene.
    doses=[]  #Creación de listas de dosis
    dosese=[]
    doses_matrix=[]
    dose_data_path_norm=os.path.normpath(dose_data_path)
    for path in os.listdir(dose_data_path_norm):
        depths_doses,doses_run=lector_dose_data_FLUKA(os.path.join(dose_data_path_norm,path)) #Lectura de dosis desde archivo FLUKA
        doses_matrix.append(doses_run)
    doses_matrix=np.transpose(np.array(doses_matrix))
    for i in range(len(depths_doses)):
        doses_at_same_depth=doses_matrix[i][:]
        dose_avg_at_depth=np.average(doses_at_same_depth)
        dose_std_at_depth=np.std(doses_at_same_depth)
        doses.append(dose_avg_at_depth)
        dosese.append(dose_std_at_depth)

    dosemax=max(doses)
    doses=[i*dose_norm_max/dosemax for i in doses]
    dosese=[i*dose_norm_max/dosemax for i in dosese]
    interp_doses = np.interp(detector_depths, depths_doses, doses)  # Dosis interpoloadas a profundidades de detectores
    interp_dosese = np.interp(detector_depths, depths_doses, dosese)  # Error interpolado

    database_norm_path=os.path.normpath(database_path)
    energies,yields,yielderrs,lambdas,lambdaerrs=database_reader(database_norm_path) #lector de base de datos (MCDS) nos dice cuanto yield corresponde a cada energía

    spectrum_norm_path=os.path.normpath(spectrum_data_path)
    Ebins,spectrum_avg,spectrum_std=lector_spectrum_data_FLUKA(spectrum_norm_path,detector_depths) #Lector de espectro nos entrega todos los espectros, leyendo lo de FLUKA
    filename=spectrum_norm_path.split(os.sep)[-1]
    
    if os.path.exists(output_folder):
        # path completo de una carpeta ya existente
        path_file = os.path.join(output_folder, f'proc_{filename}_{dose_norm_max}Gy')
    else:
        # se debe crear una carpeta con nombre output_folder
        folder = os.path.join(os.getcwd(), output_folder)
        try:
            os.mkdir(folder)
            path_file = os.path.join(folder, f'proc_{filename}_{dose_norm_max}Gy')
        except FileExistsError as error:
            path_file = os.path.join(folder, f'proc_{filename}_{dose_norm_max}Gy')
    newtablis = open(path_file, 'w')
    summarized_tab=[]
    newtablis.write("Profund[mm] D[A.U.]   D-Error    DSB-Yield  Yield-Error  Lambda  Lambda-Error    S      S-Error\n")
    y = np.interp(Ebins, energies, yields)
    yerr = np.interp(Ebins, energies, yielderrs)
    l = np.interp(Ebins, energies, lambdas)
    lerr = np.interp(Ebins, energies, lambdaerrs)
    print(f'y: {y}\n l: {l}')
    for index,detector_depth in enumerate(detector_depths):
        spectrum_at_detector_depth=spectrum_avg[index]
        if sum(spectrum_at_detector_depth)!=0:
            yave=np.average(y, weights=spectrum_at_detector_depth)*DNA/6
            yerrave=np.average(yerr, weights=spectrum_at_detector_depth)*DNA/6
            lave=np.average(l, weights=spectrum_at_detector_depth)*5**2/NDIA**2
            lerrave=np.average(lerr, weights=spectrum_at_detector_depth)*5**2/NDIA**2
        else:
            yave = 0
            yerrave = 0
            lave = 0
            lerrave = 0
        S, Serr = mech_model(ctype, interp_doses[index], interp_dosese[index], yave, yerrave, lave, lerrave, DNA, NDIA)
        newtablis.write("{:.4e} {:.4e} {:.4e} {:.4e} {:.4e} {:.4e} {:.4e} {:.4e} {:.4e}\n".
                        format(detector_depth,interp_doses[index],interp_dosese[index],
                    yave,yerrave,lave,lerrave,S,Serr))
        sumtabline=[detector_depth,interp_doses[index],interp_dosese[index],
                    yave,yerrave,lave,lerrave,S,Serr]
        summarized_tab.append(sumtabline) #también se genera una tabla resumida, ponderando yields.
    newtablis.close()
    return summarized_tab #retorna exactamente lo que queremos saber, una tabla con profundidad, dosis, yield, lambda,
                          #supervivencia y el error de cada cosa.