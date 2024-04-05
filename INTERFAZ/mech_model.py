import math
import numpy as np
from scipy.integrate import simps
from uncertainties import ufloat, correlated_values
import uncertainties.umath as u
from abc import ABC, abstractmethod

#Funciones del modelo mecanístico

# Datos HSG - V79

# μx 0.9817 ± 0.0056 0.9568 ± 0.0236
# μy 0.0891 ± 0.0068 0.0300 ± 0.0177
# ζ 0.1025 ± 0.0065 0.0412 ± 0.0209
# ξ 0.0572 ± 0.0027 0.0608 ± 0.0381
# ηλp→1 (7.26 ± 0.04)E-4 (9.78 ± 0.10)E-4
# ηλp→∞ 0.0022 ± 0.0001 0.0065 ± 0.0001

# Datos célula humana HSG

# μx 0.9817 ± 0.0056
# μy 0.0891 ± 0.0068
# ζ 0.1025 ± 0.0065
# ξ 0.0572 ± 0.0027
# ηλp→1 (7.26 ± 0.04)E-4
# ηλp→∞ 0.0022 ± 0.0001

# Datos célula hamster V-79

# μx 0.9568 ± 0.0236
# μy 0.0300 ± 0.0177
# ζ 0.0412 ± 0.0209
# ξ 0.0608 ± 0.0381
# ηλp→1 (9.78 ± 0.10)E-4
# ηλp→∞ 0.0065 ± 0.0001


class Modelo(ABC):

    @abstractmethod
    def predict(self):
        pass


class Modelo_Wang(Modelo):

    def __init__(self):
        self.name = 'Wang'
        self.params= dict()
        self.params['V79'] = {'mu_x': ufloat(0.9568,0.0236),
                              'mu_y': ufloat(0.0300,0.0177),
                              'zeta': ufloat(0.0412,0.0209),
                              'xi':  ufloat(0.0608,0.0381),
                              'eta_1': ufloat(9.78e-4,0.10e-4),
                              'eta_infty': ufloat(0.0065,0.0001)}
        
        self.params['HSG'] = {'mu_x': ufloat(0.9817,0.0056),
                            'mu_y': ufloat(0.0891,0.0068),
                            'zeta': ufloat(0.1025,0.0065),
                            'xi': ufloat(0.0572,0.0027),
                            'eta_1': ufloat(7.26e-4,0.04e-4),
                            'eta_infty': ufloat(0.0022,0.0001)}

    def add_params(self, ctype, dose, doseerr, yld, ylderr, lmbda, lmbdaerr, d):
        self.ctype = ctype
        self.dose = dose
        self.doserr = doseerr
        self.Yld = yld
        self.Ylderr = ylderr
        self.lmbda = lmbda
        self.lmbdaerr = lmbdaerr
        self.d = d


    def predict(self):
        self.Yld = self.Yld / self.dose
        if self.dose!=0:
            if self.ctype == 'V79':
                params = self.params['V79']
            elif self.ctype == 'HSG':
                params = self.params['HSG']
            else:
                params = self.params[self.ctype]
            D=ufloat(self.dose,self.doserr)
            Y=ufloat(self.Yld,self.Ylderr)
            lmbda=ufloat(self.lmbda,self.lmbdaerr)*10**2/self.d**2

            N = Y * D  # NÚMERO DE DSBS X CÉLULA
            n_p = Y*D/lmbda * (1 - u.exp(-lmbda))
            lmbda_p = lmbda / (1 - u.exp(-lmbda))
            eta = params['eta_infty'] - (params['eta_infty'] - params['eta_1']) / lmbda_p
            Pint = (1 - u.exp(-eta * n_p)) / (eta * n_p)
            Ptrack = (1 - u.exp(-params['xi'] * lmbda_p)) / (params['xi'] * lmbda_p)
            Pcorrect = params['mu_x'] * Pint * Ptrack
            Pcontrib = (1 - u.exp(-params['zeta'] * lmbda_p)) / (params['zeta'] * lmbda_p)
            N_death = params['mu_y'] * N * Pcontrib * (1 - Pcorrect)
            S = u.exp(-N_death)
            return S.nominal_value, S.std_dev
        else:
            return 1

    def add_cell_params(self, cell_line, params):
        if cell_line in self.params.keys():
            self.params[f'{cell_line}'].update(params)
        else:
            self.params[f'{cell_line}'] = params



class Modelo_Wang_params_sophia(Modelo_Wang):
    
    def __init__(self):
        super().__init__()

        self.name = 'Wang-Sophia'
        self.params = dict()
        self.params['V79'] = {
                            'mu_x': ufloat(0.9454,0.0236),
                            'mu_y': ufloat(0.03,0.0177),
                            'zeta': ufloat(0.0525,0.0209),
                            'xi': ufloat(0.0575,0.0381),
                            'eta_1': ufloat(0.0019,0.10e-4),
                            'eta_infty': ufloat(0.0021,0.0001)}
        self.params['HSG'] = {
                            'mu_x': ufloat(0.9853,0.0056),
                            'mu_y': ufloat(0.0866,0.0068),
                            'zeta': ufloat(0.09832,0.0065),
                            'xi': ufloat(0.0569,0.0027),
                            'eta_1': ufloat(2.9e-10,0.04e-4),
                            'eta_infty': ufloat(0.0024,0.0001)}


class TLK_model(Modelo):
    
    def __init__(self):
        self.name = 'TLK'
        self.params = dict()
        self.params['V79'] = {'lambda_1': ufloat(6.38E-1, 0.45E-1),
                              'lambda_2': ufloat(5.44E-1, 1.21E-1),
                              'phi_1': ufloat(1.52E-4, 1.43E-4),
                              'phi_2': ufloat(8.46E-3, 0.30E-3),
                              'gamma_eta': ufloat(4.89E-6, 0.76E-6)}

    def add_params(self, sigma1, sigma2, dose, doserr, cell, T=28):
        self.sigma1 = sigma1
        self.sigma2 = sigma2
        self.dose = ufloat(dose, doserr)
        self.T = T
        self.get_params_cell(cell)


    def get_params_cell(self, cell):
        self.lambda1 = self.params[f'{cell}']['lambda_1']
        self.lambda2 = self.params[f'{cell}']['lambda_2']
        self.phi1 = self.params[f'{cell}']['phi_1']
        self.phi2 = self.params[f'{cell}']['phi_2']
        self.gamma_eta = self.params[f'{cell}']['gamma_eta']


    def add_cell_params(self, cell_line, params):
        if cell_line in self.params.keys():
            self.params[f'{cell_line}'].update(params)
        else:
            self.params[f'{cell_line}'] = params


    def predict(self):
        survival, survivalerr = self.survival_LQ()
        return survival, survivalerr


    def alpha(self):
        return self.phi1 * self.sigma1 + self.phi2 * self.sigma2

    def beta(self):
        lambda1 = self.lambda1
        lambda2 = self.lambda2
        # gamma_eta = gamma * eta
        gamma_eta = self.gamma_eta

        return gamma_eta * (self.sigma1 ** 2 / (2 * lambda1) + self.sigma2 ** 2 / (2 * lambda2) + self.sigma1 * self.sigma2 / (lambda1 + lambda2))
    
    def survival_LQ(self):
        a = self.alpha()
        b = self.beta()
        S = u.exp(-a * self.dose - b * self.dose ** 2)
        return S.nominal_value, S.std_dev

    def L(self, t, L1t0, L2t0):
        lambda1 = self.lambda1
        lambda2 = self.lambda2
        eta = self.eta
        L1 = L1t0 * u.exp(-lambda1 * t) / (1 + eta * ((1 - u.exp(-lambda1 * t)) * L1t0 / lambda1 + (1 - u.exp(-lambda2 * t)) * L2t0 / lambda2))
        return [L1, L1 * u.exp((lambda1 - lambda2) * t) * L2t0 / L1t0]

    def Lf(self, t, L1, L2):
        dotLf = self.phi1 * self.lambda1 * L1 + self.phi2 * self.lambda2 * L2 + self.gamma * self.eta * (L1 + L2) ** 2
        return simps(dotLf, t)


    def survival_TLK(self):
        L1, L2 = self.L(self.T, self.sigma1 * self.dose, self.sigma2 * self.dose, self.lambda1, self.lambda2, self.eta)
        survival = u.exp(-self.Lf(self.T, L1, L2, self.lambda1, self.lambda2, self.phi1, self.phi2, self.gamma, self.eta))
        return survival



class Modelo_ML:
    pass




def mech_model_simple(D,lmbda):
    #Células V79
    mu_x = 0.9568
    mu_y = 0.0300
    zeta = 0.0412
    xi = 0.0608
    eta_1 = 9.78e-4
    eta_infty = 0.0065
    #### EJEMPLO LET = 7.6315 keV/um -> Protones 5.2MeV -> Y = 5.71947E+01 -> lmbda = 3.56914E+00?
    R = 5 # um
    rho = 1  # Nucleus density g/cm3
    LET = 7.6315  # keV/um
    Y = 5.71947E+01  # Y ES EL YIELD de DSB, DEPENDE DE ENERGÍA Y PARTÍCULA (MCDS)
    N = Y * D  # NÚMERO DE DSBS X CÉLULA
    n = math.pi * R ** 2 * D * rho * 10 ** (-18) / (LET * 1.602 * 10 ** (-19))
    if lmbda==0:
        lmbda = N / n
    n_p = n * (1 - math.exp(-lmbda))
    lmbda_p = lmbda / (1 - math.exp(-lmbda))
    eta = eta_infty - (eta_infty - eta_1) / lmbda_p
    Pint = (1 - math.exp(-eta * n_p)) / (eta * n_p)
    Ptrack = (1 - math.exp(-xi * lmbda_p)) / (xi * lmbda_p)
    Pcorrect = mu_x * Pint * Ptrack
    Pcontrib = (1 - math.exp(-zeta * lmbda_p)) / (zeta * lmbda_p)
    N_death = mu_y * N * Pcontrib * (1 - Pcorrect)
    S = math.exp(-N_death)
    return S

def mech_model(D,ctype,LET,Y, DNA=5.6, NDIA=11):
    #Y = Y * DNA / 6
    #Ylderr = Ylderr * DNA / 6
    #lmbdas = lmbdas * 25 / (NDIA ** 2)
    #lmbdaesrr = lmbdaesrr * 25 / (NDIA ** 2)
    if D!=0:
        if ctype.lower()=="v79":
            mu_x = 0.9568
            mu_y = 0.0300
            zeta = 0.0412
            xi = 0.0608
            eta_1 = 9.78e-4
            eta_infty = 0.0065
        else:
            mu_x = 0.9817
            mu_y = 0.0891
            zeta = 0.1025
            xi = 0.0572
            eta_1 = 7.26e-4
            eta_infty = 0.0022
        R = 5.5  # um
        rho = 1  # Nucleus density g/cm3
        N = Y * D  # NÚMERO DE DSBS X CÉLULA
        lmbda = Y * (LET * 1.602 * 10 ** (-19)) / (math.pi * R ** 2 * rho * 10 ** (-18)) # =N/n

        #lmbda = 3
        n_p = Y*D/lmbda * (1 - math.exp(-lmbda))
        lmbda_p = lmbda / (1 - math.exp(-lmbda))
        eta = eta_infty - (eta_infty - eta_1) / lmbda_p
        Pint = (1 - math.exp(-eta * n_p)) / (eta * n_p)
        Ptrack = (1 - math.exp(-xi * lmbda_p)) / (xi * lmbda_p)
        Pcorrect = mu_x * Pint * Ptrack
        Pcontrib = (1 - math.exp(-zeta * lmbda_p)) / (zeta * lmbda_p)
        N_death = mu_y * N * Pcontrib * (1 - Pcorrect)
        S = math.exp(-N_death)


        return S, lmbda
    else:
        return 1, 0 # 0 lmbda es solo para rellenar y que no se caiga el código mientras testeo esta parte



def mech_model_wlmbda(D,ctype,Y,lmbda):
    if D!=0:
        if ctype.lower()=="v79":
            mu_x = 0.9568
            mu_y = 0.0300
            zeta = 0.0412
            xi = 0.0608
            eta_1 = 9.78e-4
            eta_infty = 0.0065
        else:
            mu_x = 0.9817
            mu_y = 0.0891
            zeta = 0.1025
            xi = 0.0572
            eta_1 = 7.26e-4
            eta_infty = 0.0022

        N = Y * D  # NÚMERO DE DSBS X CÉLULA
        n_p = (Y*D/lmbda) * (1 - math.exp(-lmbda))
        lmbda_p = lmbda / (1 - math.exp(-lmbda))
        eta = eta_infty - ((eta_infty - eta_1) / lmbda_p)
        Pint = (1 - math.exp(-eta * n_p)) / (eta * n_p)
        Ptrack = (1 - math.exp(-xi * lmbda_p)) / (xi * lmbda_p)
        Pcorrect = mu_x * Pint * Ptrack
        Pcontrib = (1 - math.exp(-zeta * lmbda_p)) / (zeta * lmbda_p)
        N_death = mu_y * N * Pcontrib * (1 - Pcorrect)
        S = math.exp(-N_death)


        database_mech_model = open('database_mech_model_lambda.database', 'a')
        database_mech_model.write('LAMBDA n_p LAMBDA_p ETA P_int P_track P_correct P_contrib S\n')
        database_mech_model.write('{} {} {} {} {} {} {} {} {}\n'.format(lmbda, n_p, lmbda_p, eta, Pint,
                                                                         Ptrack, Pcorrect, Pcontrib, S))

        return S
    else:
        return 1


def mech_model_wlmbda_uncert(ctype,dose,doseerr,Yld,Ylderr,lmbdas,lmbdaesrr,modelo, d=10):
    Yld = Yld / dose
    if dose!=0:
        if modelo == 'Wang':
            if ctype.lower()=="v79":
                mu_x = ufloat(0.9568,0.0236)
                mu_y = ufloat(0.0300,0.0177)
                zeta = ufloat(0.0412,0.0209)
                xi = ufloat(0.0608,0.0381)
                eta_1 = ufloat(9.78e-4,0.10e-4)
                eta_infty = ufloat(0.0065,0.0001)

            elif ctype.lower()=="v79s":
                cov_matrix = np.array([[0.02906061, 0, 0, 0, 0, 0],
                                    [0, 0.09059012, 0, 0, 0, 0],
                                    [0, 0, 0.12912589, 0, 0, 0],
                                    [0, 0, 0, 0.03508078, 0, 0],
                                    [0, 0, 0, 0, 5.75863e-6, 0],
                                    [0, 0, 0, 0, 0, 9.50551e-7]])
                # zeta,xi,mux,muy,eta1,etainf
                (zeta, xi, mu_x, mu_y, eta_1, eta_infty) = correlated_values(
                    [0.0320, 0.0456, 0.9409, 0.0298, 0.002295, 0.00276], cov_matrix)

            elif ctype.lower()=="v79scov":
                cov_matrix = np.array([[0.02906061, -0.05128389, 0.06116949, 0.03192539,0,0],
                                    [-0.05128389, 0.09059012, -0.10784773,-0.05636421,0,0],
                                    [0.06116949, -0.10784773, 0.12912589, 0.0671851,0,0],
                                    [0.03192539, -0.05636421, 0.0671851, 0.03508078,0,0],
                                    [0,0,0,0,5.75863e-6,-2.17495e-6],
                                    [0,0,0,0,-2.17495e-6,9.50551e-7]])
                                        #zeta,xi,mux,muy,eta1,etainf
                (zeta, xi, mu_x, mu_y, eta_1, eta_infty) = correlated_values(
                        [0.0320, 0.0456, 0.9409, 0.0298,0.002295,0.00276],cov_matrix)
            elif ctype.lower()=="v79covwangseba":
                cov_matrix = np.array([[0.0412**2, -0.05128389, 0.06116949, 0.03192539,0,0],
                                    [-0.05128389, 0.0608**2, -0.10784773,-0.05636421,0,0],
                                    [0.06116949, -0.10784773, 0.0236**2, 0.0671851,0,0],
                                    [0.03192539, -0.05636421, 0.0671851, 0.0177**2,0,0],
                                    [0,0,0,0,(0.10e-4)**2,-2.17495e-6],
                                    [0,0,0,0,-2.17495e-6,(0.0001)**2]])
                                        #zeta,xi,mux,muy,eta1,etainf
                (zeta, xi, mu_x, mu_y, eta_1, eta_infty) = correlated_values(
                        [0.0412, 0.0608, 0.9568, 0.0300,9.78e-4,0.0065],cov_matrix)
            elif ctype.lower()=="hsg":
                mu_x = ufloat(0.9817,0.0056)
                mu_y = ufloat(0.0891,0.0068)
                zeta = ufloat(0.1025,0.0065)
                xi = ufloat(0.0572,0.0027)
                eta_1 = ufloat(7.26e-4,0.04e-4)
                eta_infty = ufloat(0.0022,0.0001)
            elif ctype.lower()=='hsgs':
                mu_x = ufloat(1, 0)
                mu_y = ufloat(0.1069, 0)
                zeta = ufloat(0.0864, 0)
                xi = ufloat(0.0330, 0)
                eta_1 = ufloat(0.005333, 0)
                eta_infty = ufloat(0.005599, 0)
        elif modelo == 'Wang-Sophia':
            # Por ahora tienen incertidumbre de Wang
            if ctype == 'v79':
                mu_x = ufloat(0.9454,0.0236)
                mu_y = ufloat(0.03,0.0177)
                zeta = ufloat(0.0525,0.0209)
                xi = ufloat(0.0575,0.0381)
                eta_1 = ufloat(0.0019,0.10e-4)
                eta_infty = ufloat(0.0021,0.0001)
            elif ctype == 'hsg':
                mu_x = ufloat(0.9853,0.0056)
                mu_y = ufloat(0.0866,0.0068)
                zeta = ufloat(0.09832,0.0065)
                xi = ufloat(0.0569,0.0027)
                eta_1 = ufloat(2.9e-10,0.04e-4)
                eta_infty = ufloat(0.0024,0.0001)
        D=ufloat(dose,doseerr)
        Y=ufloat(Yld,Ylderr)
        lmbda=ufloat(lmbdas,lmbdaesrr)*10**2/d**2

        N = Y * D  # NÚMERO DE DSBS X CÉLULA
        n_p = Y*D/lmbda * (1 - u.exp(-lmbda))
        lmbda_p = lmbda / (1 - u.exp(-lmbda))
        eta = eta_infty - (eta_infty - eta_1) / lmbda_p
        Pint = (1 - u.exp(-eta * n_p)) / (eta * n_p)
        Ptrack = (1 - u.exp(-xi * lmbda_p)) / (xi * lmbda_p)
        Pcorrect = mu_x * Pint * Ptrack
        Pcontrib = (1 - u.exp(-zeta * lmbda_p)) / (zeta * lmbda_p)
        N_death = mu_y * N * Pcontrib * (1 - Pcorrect)
        S = u.exp(-N_death)
        return S.nominal_value, S.std_dev
    else:
        return 1
