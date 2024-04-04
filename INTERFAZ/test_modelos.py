import math
import numpy as np
from uncertainties import ufloat, correlated_values
import uncertainties.umath as u
from abc import ABC, abstractmethod




class Modelo(ABC):

    @abstractmethod
    def predict(self):
        pass


class Modelo_Wang(Modelo):

    def __init__(self):
        self.params= dict()
        self.params['v79'] = {'mu_x': ufloat(0.9568,0.0236),
                              'mu_y': ufloat(0.0300,0.0177),
                              'zeta': ufloat(0.0412,0.0209),
                              'xi':  ufloat(0.0608,0.0381),
                              'eta_1': ufloat(9.78e-4,0.10e-4),
                              'eta_infty': ufloat(0.0065,0.0001)}
        
        self.params['hsg'] = {'mu_x': ufloat(0.9817,0.0056),
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
            if self.ctype == 'v79':
                params = self.params['v79']
            elif self.ctype == 'hsg':
                params = self.params['hsg']
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
        self.params[f'{cell_line}'] = params




class Modelo_Wang_params_sophia(Modelo_Wang):
    
    def __init__(self):
        super().__init__()

        self.params = dict()
        self.params['v79'] = {
                            'mu_x': ufloat(0.9454,0.0236),
                            'mu_y': ufloat(0.03,0.0177),
                            'zeta': ufloat(0.0525,0.0209),
                            'xi': ufloat(0.0575,0.0381),
                            'eta_1': ufloat(0.0019,0.10e-4),
                            'eta_infty': ufloat(0.0021,0.0001)}
        self.params['hsg'] = {
                            'mu_x': ufloat(0.9853,0.0056),
                            'mu_y': ufloat(0.0866,0.0068),
                            'zeta': ufloat(0.09832,0.0065),
                            'xi': ufloat(0.0569,0.0027),
                            'eta_1': ufloat(2.9e-10,0.04e-4),
                            'eta_infty': ufloat(0.0024,0.0001)}



class Modelo_ML:
    pass


