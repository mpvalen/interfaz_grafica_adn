import fluka_to_data as ftd
import numpy as np
dose_data_path= "D:\\Universidad\\Cellular-Response\\FLUKA\\prueba_dose_data"
spectrum_data_path= "D:\\Universidad\\Cellular-Response\\FLUKA\\prueba_corrientes_spectrum_data"
databasefolderpath="D:\\Universidad\\Cellular-Response\\MCDS\\p-50-samples"


data=ftd.fluka_to_data(spectrum_data_path,
                       dose_data_path,
                       databasefolderpath,
                       detector_depths=[i for i in range(0,251)],
                       ctype="hsg",DNA=6,NDIA=5,dose_norm_max=1)
