import os
import numpy as np
import mcds_fop as fop
import subprocess

def LET_int(rtype):
    protondata=open('ENERGY_LET_1H.txt','r')
    energies=[]
    lets=[]
    for line in protondata:
        e_let=line.split(' ')
        e=float(e_let[0])
        energies.append(e)
        let=float(e_let[1])
        lets.append(let)
    return energies,lets

def yield_int_simulated(ctype, datname,nocs):
    #Generar un input para el .dat
    path_mcds = os.path.join('mcds', 'bin', 'mcds.exe')
    if ctype.lower()=="hsg":
        DNA=6
    else:
        DNA=5.6
    inpt=open("temp.inp",'w')
    inpt.write("CELL: DNA={} NDIA=10 CDIA=10\n"
               "SIMCON: seed={} nocs={}\n"
               "RADX: FN={}".format(DNA,np.random.randint(100000000,999999999),nocs,datname))
    inpt.close()
    #Correr input
    bat=open("temp.bat",'w')
    bat.write(fop.mcds_bat(os.getcwd()+"\\temp.inp", path_mcds))
    bat.close()
    subprocess.call([r"{}".format(os.getcwd()+"\\temp.bat")])
    #Leer Y y lmbda del output
    Y,Yerr,lmbda,lmbdaerr=fop.mcds_of_clusters_lmbda("temp.out")

    return Y,Yerr,lmbda,lmbdaerr


def yield_int_simulated_v2(ctype,ndia,cdia,wem, seed, datname,nocs,par,ke,meva,ad,po2,mmHg,m0,k,q,r,fbl,conc,fnsd,chmx, ident):
    #Generar un input para el .dat
    if seed != '':
        seed = np.random.randint(100000000,999999999)
    path_mcds = os.path.join('mcds', 'bin', 'mcds.exe')
    if ctype.lower()=="hsg":
        DNA=6
    else:
        DNA=5.6
    input_text = fop.mcds_inp(str(DNA), str(ndia), str(cdia), str(wem), str(seed),
                              str(nocs), str(datname), str(par), str(ke), str(meva),
                              str(ad), str(po2), str(mmHg), str(m0), str(k), str(q),
                              str(r), str(fbl), str(conc), str(fnsd), str(chmx))
    
    try:
        os.mkdir(ident)
        dir = ident
    except:
        dir = ident
    inpt=open(os.path.join(dir, "temp.inp"),'w')
    inpt.write(input_text)
    inpt.close()
    #Correr input
    bat = open(os.path.join(dir, "temp.bat"), "w")
    bat.write(fop.mcds_bat(os.path.join(ident, "temp.inp"), path_mcds))
    bat.close()
    subprocess.call([r"{}".format(os.path.join(ident, "temp.bat"))])
    #Leer Y y lmbda del output
    Y,Yerr,lmbda,lmbdaerr=fop.mcds_of_clusters_lmbda(os.path.join(ident, "temp.out"))

    return Y,Yerr,lmbda,lmbdaerr

def yield_int_weighted(ctype, rtype, cwdtodat):
    cwd = os.getcwd()
    data=open(cwd+"\\"+cwdtodat,'r')
    cont=0
    E=[]
    W=[]
    for line in data:
        if cont>=2:
            line_split=line.split(' ')
            line_stripped=[i.strip() for i in line_split]
            e=float(line_stripped[1])
            w=float(line_stripped[2])
            E.append(e)
            W.append(w)
        cont+=1
    if ctype.lower() == "v79":
        if rtype.lower() == "p-20-samples" or rtype.lower() == "1h":
            data=open(cwd+'\\data\\proton_v79_data')
        elif rtype.lower() == "e":
            data = open(cwd + 'data\\electron_v79_data')
        else:
            data = open(cwd + '\\data\\electron_v79_data')
    else:  # ctype="hsg"
        if rtype.lower() == "p-20-samples" or rtype.lower() == "1h":
            data = open(cwd + '\\data\\proton_hsg_data')
        elif rtype.lower() == "e":
            data = open(cwd + '\\data\\electron_hsg_data')
        else:
            data = open(cwd + '\\data\\electron_hsg_data')
    yields=[]
    lets=[]
    for line in data:
        let,yld=line.split(',')
        yields.append(float(yld))
        lets.append(float(let))
    lets.reverse()
    yields.reverse()
    Y=0
    energies,LETS_interp=LET_int('p-20-samples')
    LETs=list(np.interp(E,energies,LETS_interp))
    for i,let in enumerate(LETs):
        Y+=np.interp(let,lets,yields)*W[i]
    return Y

