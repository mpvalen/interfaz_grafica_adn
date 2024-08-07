# Welcome to the CELL documentation

**CELL (Cellular Effect Lesions Linker)** is a graphical interface for cell survival predictions based on different simulation chains pre-loaded in the system for different cell lines. The program was written in Python using the PyQt5 library.

## Install

The [repository](https://github.com/mpvalen/interfaz_grafica_adn) has to be downloaded. The following libraries are necessary for the execution,  `python`  should be version 3.X minimum.

- Numpy
- Matplotlib
- PyQt5
- scipy
- natsort
- uncertainties

The program allows the use of the [MCDS](https://faculty.washington.edu/trawets/mcds/) (Monte Carlo Damage Simulation) software [[1]](#references)[[2]](#references)[[3]](#references)[[4]](#references) . The latest version of MCDS (3.10A) is required for the correct execution of the program, the folder  `mcds` should be located inside the `INTERFAZ` directory.

## Execution

To use the interface, simply execute `main.py`.

### References

[1] R.D. Stewart, V.K. Yu, A.G. Georgakilas, C. Koumenis, J.H. Park, D.J. Carlson, Monte Carlo Simulation of the Effects of Radiation Quality and Oxygen Concentration on Clustered DNA Lesions. Radiat. Res. 176, 587-602 (2011)

[2] Y Hsiao and  R.D. Stewart, Monte Carlo Simulation of DNA Damage Induction by X-rays and Selected Radioisotopes. Phys. Med. Biol. 53, 233-244 (2008)

[3] V.A. Semenenko and R.D. Stewart. Fast Monte Carlo simulation of DNA damage formed by electrons and light ions. Phys. Med. Biol. 51(7), 1693-1706 (2006)

[4] V.A. Semenenko and R.D. Stewart. A fast Monte Carlo algorithm to simulate the spectrum of DNA damages formed by ionizing radiation. Radiat Res. 161(4), 451-457 (2004).