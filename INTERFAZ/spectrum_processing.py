import os
import yield_database as yld
import mech_model as mdl
import numpy as np
import matplotlib.pyplot as plt


def average(arr, n):
    remainder = len(arr) % n
    if remainder == 0:
        avg = np.mean(arr.reshape(-1, n), axis=1)
        avg = np.repeat(avg, n)
        return avg
    else:
        avg_head = np.mean(arr[:-remainder].reshape(-1, n), axis=1)
        avg_tail = np.mean(arr[-remainder:])
        avg_head = np.repeat(avg_head, n)
        avg_tail = np.repeat(avg_tail, remainder)
        return np.append(avg_head, avg_tail)

def spctrm_to_data(path): #d es la separación entre detectores
    tab=open(path,'r')
    ini_pos_tab=[]
    fin_pos_tab=[]
    data=[]
    table_reading=False
    for i,line in enumerate(tab):
        list_line=line.split(' ')
        list_line_stripped=[txt.strip() for txt in list_line]
        list_line_stripped=list(filter(None,list_line_stripped))
        data.append(list_line_stripped)
        if "Detector" in list_line_stripped:
            ini_pos_tab.append(i+2)
            table_reading=True
        if table_reading==True and len(list_line_stripped)==0:
            fin_pos_tab.append(i)
            table_reading=False

    all_tabs=[]
    for n_tab in range(len(ini_pos_tab)):
        ini=ini_pos_tab[n_tab]
        fin=fin_pos_tab[n_tab]
        all_tabs.append(data[ini:fin])

    return all_tabs

def data_to_simple(tabs,strt_pos_det,d): #Cambia formato y transforma energía de GeV a MeV
    smpl_data=[]
    for i,tab in enumerate(tabs):
        Pos=strt_pos_det+i*d
        for line in tab:
            FLUMULT=1
            Eavg=(float(line[0])+float(line[1]))/2*1000 #ahora en MeV
            # print("\n\n\n\nWARNING: spectrum_processing.py function: data_to_simple\n"
            #       "FLUENCE MULTIPLIER APPLIED: {}\n\n\n\n".format(FLUMULT))
            Fluence=float(line[2])*FLUMULT
            Error=float(line[3])
            smpl_data.append([Pos,Eavg,Fluence,Error])
    depths=[strt_pos_det+d*i for i in range(len(tabs))]
    return depths,smpl_data


def dat_to_dose(path,d):
    dat=open(path,'r')
    depths=[]
    doses=[]
    for line in dat:
        depth_,dose_=line.split(' ')
        depth=float(depth_.strip())
        dose=float(dose_.strip())
        depths.append(depth)
        doses.append(dose)
    D = np.interp(d,depths,doses)
    return D


def fluka_dose_as_is(path):
    dose_data = open(path, 'r')
    doses = []
    doses_err = []
    bin_starts = []
    bin_ends = []
    for i, line in enumerate(dose_data):
        if i != 0:
            l_split = line.split(' ')
            l_split_f = []
            for str in l_split:
                if str != '':
                    l_split_f.append(str)
            l_strip = [l.strip() for l in l_split_f]
            binstart = float(l_strip[0])
            binend = float(l_strip[1])
            dose = float(l_strip[2])
            dose_err = float(l_strip[3])
            doses.append(dose)
            doses_err.append(dose_err)
            bin_starts.append(binstart)
            bin_ends.append(binend)
    depths=(np.array(bin_starts)+np.array(bin_ends))/2
    return depths, doses, doses_err

def fluka_dose_as_is_interp(depths_to_interp,path,rf):
    dose_data = open(path, 'r')
    doses = []
    doses_err = []
    bin_starts = []
    bin_ends = []
    for i, line in enumerate(dose_data):
        if i != 0:
            l_split = line.split(' ')
            l_split_f = []
            for str in l_split:
                if str != '':
                    l_split_f.append(str)
            l_strip = [l.strip() for l in l_split_f]
            binstart = float(l_strip[0])
            binend = float(l_strip[1])
            dose = float(l_strip[2])
            dose_err = float(l_strip[3])
            doses.append(dose)
            doses_err.append(dose_err)
            bin_starts.append(binstart)
            bin_ends.append(binend)
    depths=(np.array(bin_starts)+np.array(bin_ends))/2
    doses2 = average(np.array(doses),rf)
    DOSES_INT=np.interp(depths_to_interp,depths,doses2)
    return DOSES_INT

def dose_to_survival_slow(doses,smpl_data,nocs,ctype,ndia,cdia,wem,
                          par,ke,meva,ad,po2,mmHg, m0,k,q,r,fbl,conc,fnsd,chmx, ident): #doses en cada detector
    depths=[]
    srvvls=[]
    count=0
    progress_count=0
    for i in smpl_data:
        if i[0] not in depths:
            depths.append(i[0])
    for d in depths:
        es=[]
        ws=[]
        for point in smpl_data:
            if point[0]==d:
                es.append(point[1])
                ws.append(point[2])
                if len(ws)==len(smpl_data)/len(depths):
                    Wtotal = sum(ws)
                    print("\n\n\n\nLARGO PESOS: {}".format(len(ws)))
                    print("LARGO DATOS: {}".format(len(smpl_data)))
                    print("LARGO PROFUNDIDADES: {}".format(len(depths)))
                    try:
                        ws = [w / Wtotal for w in ws]
                    except:
                        print("Alerta: Suma de pesos es 0 en esta iteración\n"
                              "CORREGIR EN FLUKA")
                    try:
                        os.mkdir(ident)
                        dir = ident
                    except:
                        dir = ident
                    path_dat = os.path.join(dir, 'temp.dat')
                    dat=open(path_dat,'w')
                    dat.write("temp dat depth = {}mm\n".format(d))
                    dat.write("{}\n".format(int(len(smpl_data)/len(depths))))
                    print("SUMA PESOS: {}\n\n\n\n".format(sum(ws)))
                    for i,w in enumerate(ws):
                        dat.write("p-20-samples {} {}\n".format(es[i],w))
                    dat.close()
                    Y, lmbda = yld.yield_int_simulated_v2(ctype,ndia,cdia,wem, path_dat,
                                                          nocs,par,ke,meva,ad,po2,mmHg,
                                                          m0,k,q,r,fbl,conc,fnsd,chmx, ident)
                    S=mdl.mech_model_wlmbda(doses[count],ctype,Y,lmbda)
                    srvvls.append(S)
                    count+=1
            else:
                continue
        progress_count+=1
        print("\n\n\n\n\n\nProgreso: {}%\n\n\n\n\n\n".format(round(progress_count / len(depths) * 100, 1)))
    return depths,srvvls


def dose_to_survival_quick(doses,smpl_data,ctype): #doses en cada detector
    depths=[]
    srvvls=[]
    count=0
    letfs=[]
    progress_count=0
    E_interp, LET_interp = yld.LET_int('p-20-samples')
    for i in smpl_data:
        if i[0] not in depths:
            depths.append(i[0])
    for d in depths:
        es=[]
        ws=[]
        lets=[]
        for point in smpl_data:
            if point[0]==d:
                es.append(point[1])
                ws.append(point[2])
                lets.append(np.interp(point[1],E_interp,LET_interp))
                Wtotal = sum(ws)

                if len(ws)==len(smpl_data)/len(depths):
                    # print("\n\n\n\nLARGO PESOS: {}".format(len(ws)))
                    # print("LARGO DATOS: {}".format(len(smpl_data)))
                    # print("LARGO PROFUNDIDADES: {}".format(len(depths)))
                    try:
                        ws=[w/Wtotal for w in ws]
                    except:
                        print("Alerta: Suma de pesos es 0 en esta iteración\n"
                              "CORREGIR EN FLUKA")
                    letf = sum([ws[i] * lets[i] for i in range(len(lets))])
                    dat=open("temp.dat",'w')
                    dat.write("temp dat depth = {}mm\n".format(d))
                    dat.write("{}\n".format(int(len(smpl_data)/len(depths))))
                    # print("SUMA PESOS: {}\n\n\n\n".format(sum(ws)))
                    for i,w in enumerate(ws):
                        dat.write("p-20-samples {} {}\n".format(es[i],w))
                    dat.close()
                    letfs.append(letf)
                    if ctype=="v79":
                        print("ALERTA: YIELD CALCULADO CON V79 spectrum_processing.py -> dose_to_survival_quick")
                    Y=yld.yield_int_weighted(ctype,"p-20-samples","temp.dat")
                    S=mdl.mech_model(doses[count],ctype,letf,Y)
                    srvvls.append(S)
                    count+=1
            else:
                continue
        progress_count+=1
        print("Progreso: {}%".format(round(progress_count / len(depths) * 100, 1)))
    return depths,srvvls,letfs


def dose_to_survival_slow_uncert(doses,smpl_data,nocs,ctype,ndia,cdia,wem, seed,
                                 par,ke,meva,ad,po2,mmHg,m0,k,q,r,fbl,conc,fnsd,chmx, ident): #doses en cada detector
    depths=[]
    srvvls=[]
    srverr=[]
    count=0
    progress_count=0
    for i in smpl_data:
        if i[0] not in depths:
            depths.append(i[0])
    for d in depths:
        es=[]
        ws=[]
        for point in smpl_data:
            if point[0]==d:
                es.append(point[1])
                ws.append(point[2])
                if len(ws)==len(smpl_data)/len(depths):
                    Wtotal = sum(ws)
                    print("\n\n\n\nLARGO PESOS: {}".format(len(ws)))
                    print("LARGO DATOS: {}".format(len(smpl_data)))
                    print("LARGO PROFUNDIDADES: {}".format(len(depths)))
                    try:
                        ws = [w / Wtotal for w in ws]
                    except:
                        print("Alerta: Suma de pesos es 0 en esta iteración\n"
                              "CORREGIR EN FLUKA")
                    try:
                        os.mkdir(ident)
                        dir = ident
                    except:
                        dir = ident
                    path_dat = os.path.join(dir, 'temp.dat')
                    dat=open(path_dat,'w')
                    dat.write("temp dat depth = {}mm\n".format(d))
                    dat.write("{}\n".format(int(len(smpl_data)/len(depths))))
                    print("SUMA PESOS: {}\n\n\n\n".format(sum(ws)))
                    for i,w in enumerate(ws):
                        dat.write("p-20-samples {} {}\n".format(es[i],w))
                    dat.close()
                    Y, lmbda = yld.yield_int_simulated_v2(ctype,ndia,cdia,wem, seed, path_dat,
                                                          nocs,par,ke,meva,ad,po2,mmHg,
                                                          m0,k,q,r,fbl,conc,fnsd,chmx, ident)
                    S,Serr=mdl.mech_model_wlmbda_uncert(doses[count],ctype,Y,lmbda)
                    srvvls.append(S)
                    srverr.append(Serr)
                    count+=1
            else:
                continue
        progress_count+=1
        print("\n\n\n\n\n\nProgreso: {}%\n\n\n\n\n\n".format(round(progress_count / len(depths) * 100, 1)))
    return depths,srvvls,srverr

def dose_to_yield_slow_uncert(smpl_data,nocs,ctype,ndia,cdia,wem, seed,
                              par,ke,meva,ad,po2,mmHg, m0,k,q,r,fbl,conc,fnsd,chmx, ident): #doses en cada detector
    depths=[]
    Ylds=[]
    Yldserr=[]
    Lmbds=[]
    Lmbdserr=[]
    count=0
    progress_count=0
    for i in smpl_data:
        if i[0] not in depths:
            depths.append(i[0])
    for d in depths:
        es=[]
        ws=[]
        for point in smpl_data:
            if point[0]==d:
                es.append(point[1])
                ws.append(point[2])
                if len(ws)==len(smpl_data)/len(depths):
                    Wtotal = sum(ws)
                    print("\n\n\n\nLARGO PESOS: {}".format(len(ws)))
                    print("LARGO DATOS: {}".format(len(smpl_data)))
                    print("LARGO PROFUNDIDADES: {}".format(len(depths)))
                    try:
                        ws = [w / Wtotal for w in ws]
                    except:
                        print("Alerta: Suma de pesos es 0 en esta iteración\n"
                              "CORREGIR EN FLUKA")
                    try:
                        os.mkdir(ident)
                        dir = ident
                    except:
                        dir = ident
                    path_dat = os.path.join(dir, 'temp.dat')
                    dat=open(path_dat,'w')
                    dat.write("temp dat depth = {}mm\n".format(d))
                    dat.write("{}\n".format(int(len(smpl_data)/len(depths))))
                    print("SUMA PESOS: {}\n\n\n\n".format(sum(ws)))
                    for i,w in enumerate(ws):
                        dat.write("p-20-samples {} {}\n".format(es[i],w))
                    dat.close()
                    Y, Yerr, lmbda, lmbdaerr = yld.yield_int_simulated_v2(ctype,ndia,cdia,wem, seed, path_dat,
                                                                          nocs,par,ke,meva,ad,po2,mmHg,
                                                                          m0,k,q,r,fbl,conc,fnsd,chmx, ident)
                    Ylds.append(Y)
                    Yldserr.append(Yerr)
                    Lmbds.append(lmbda)
                    Lmbdserr.append(lmbdaerr)
                    count+=1
            else:
                continue
        progress_count+=1
        print("\n\n\n\n\n\nProgreso: {}%\n\n\n\n\n\n".format(round(progress_count / len(depths) * 100, 1)))
    return depths,Ylds,Yldserr,Lmbds,Lmbdserr

def fluka_dose_as_is_interp_uncert(depths_to_interp,path):
    dose_data = open(path, 'r')
    doses = []
    doses_err = []
    bin_starts = []
    bin_ends = []
    for i, line in enumerate(dose_data):
        if i != 0:
            l_split = line.split(' ')
            l_split_f = []
            for str in l_split:
                if str != '':
                    l_split_f.append(str)
            l_strip = [l.strip() for l in l_split_f]
            binstart = float(l_strip[0])
            binend = float(l_strip[1])
            dose = float(l_strip[2])
            dose_err = float(l_strip[3])
            doses.append(dose)
            doses_err.append(dose_err)
            bin_starts.append(binstart)
            bin_ends.append(binend)
    depths=(np.array(bin_starts)+np.array(bin_ends))/2
    DOSES_INT=np.interp(depths_to_interp,depths,doses)
    DOSES_ERR_INT=np.interp(depths_to_interp,depths,doses_err)
    return DOSES_INT,DOSES_ERR_INT