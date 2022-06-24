MCDS Homepage: http://faculty.washington.edu/trawets/mcds/
File Last Updated: October 18, 2012 (RD Stewart)


ABOUT MCDS VERSION 3.10A (December 5, 2011)

1. Major update to dosimetry capabilities (includes an analytic but much improved dosimetric/microdosimetric model).
2. New version also uses a simple (analytic) algorithm to better mimic energy losses as a charged particle 
   passes through a cell culture dish/medium and the cytoplasm (optional).
3. Range of allowed particle energies has been expanded (1 eV on up for all particle types; use with of 
   caution since the physics for low energy particles is very uncertain).
4. Format and content of output file updated to include additional information.
5. Executable for linux now available (separate download from MCDS website).


ABOUT MCDS VERSION 3.00B (July 15, 2011)

This readme file provides a description of software to simulate formation of DNA damage in nuclear DNA after exposure to ionizing radiation. The Monte Carlo Damage Simulation (MCDS) generates spatial maps of the damaged nucleotides forming many types of clustered DNA lesion, including single-strand breaks (SSB), double strand breaks (DSB) as well as individual and clustered base damages. For major categories of damage, the MCDS also provides information about cluster complexity (e.g., number of lesions per cluster, cluster length, …).

The software has the capability to simulate damage induction for monoenergetic electrons, protons and other charged particles with atomic number up to and including Z = 26 (i.e., 56Fe).  The minimum allowed kinetic energy depends on the particle type.  For electrons, damage induction can be simulated from about 25 eV up to energies on the order of GeV.  For more massive particles, the allowed minimum kinetic energy increasing with increasing atomic number (e.g., see http://faculty.washington.edu/trawets/mcds/table1.html).

In addition to simulating damage induction for monoenergetic charged particles, the software has the ability to simulate damage induction for arbitrary mixtures of charged particles.  Damage induction for neutral particles (photons and neutrons) can be simulated to tabulating the distribution of secondary charged particles produced through the interactions of neutral particles in a target region of interest (e.g., see Hsaio and Stewart, PMB 53, 233-244, 2008). A major new feature of the 2011 version of the MCDS is the ability to simulate the effects of oxygen on the induction of clustered DNA lesions (see Stewart et al. 2011).  Although not required for the simulation of damage induction, the 2011 version of the MCDS also provides additional particle and dosimetric information, including charged particle stopping power in water, CSDA range, absorbed dose per unit fluence averaged over the cell nucleus, frequency-mean specific energy, energy imparted, and the lineal energy. 

For additional details of the MCDS, see

• R.D. Stewart, V.K. Yu, A.G. Georgakilas, C. Koumenis, J.H. Park, D.J. Carlson, Monte Carlo Simulation of the Effects of 
  Radiation Quality and Oxygen Concentration on Clustered DNA Lesions. Radiat. Res. 176, 587-602 (2011)


• Y Hsiao and  R.D. Stewart, Monte Carlo Simulation of DNA Damage Induction by X-rays and Selected Radioisotopes. 
  Phys. Med. Biol. 53, 233-244 (2008)

• V.A. Semenenko and R.D. Stewart. Fast Monte Carlo simulation of DNA damage formed by electrons and light ions. 
  Phys. Med. Biol. 51(7), 1693-1706 (2006).

• V.A. Semenenko and R.D. Stewart. A fast Monte Carlo algorithm to simulate the spectrum of DNA damages formed by ionizing radiation. 
  Radiat Res. 161(4), 451-457 (2004).

AUTHOR OF MCDS VERSION 3.0 (circa 2011): 
	Robert D. Stewart, Ph.D.
	Associate Professor, Medical Physics
	University of Washington
	Department of Radiation Oncology
	University Cancer Center, UWMC
	1959 NE Pacific Street
	Box 356043
	Seattle, WA 98195-6043
	206-598-7951 office
	trawets@uw.edu
	http://faculty.washington.edu/trawets/

ACKNOWLEDGEMENTS 

Many thanks to Dr. Vladimir A. Semenenko for developing the original (Version 1.0 and 2.0) MCDS software.  Dr. Stewart also thanks Mr. Anshuman Panda for implementing an early version of the model for chemical repair and oxygen fixation. Work supported in part by American Cancer Society grant IRG-58-012-52 (DJC) and in part by a Research Creative Activity Grant from the East Carolina University (ECU) Biology Department (AGG).  Version 1 and 2 of the MCDS were developed with Government support under Grant Numbers DE-FG02-03ER63541 and DE-FG02-03ER63665 (RD Stewart, Principal Investigator) awarded by the United Department of Energy. 

DISCLAIMER

Neither the author nor any government or state agency makes any warranty, express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness of any information, apparatus, product, software or process disclosed, or represents that its use would not infringe privately owned rights.  Reference to any specific commercial product, process, or service by trade name, trademark, manufacturer, or otherwise does not necessarily constitute or imply its endorsement, recommendation, or favoring by the author, the United States Government or any agency thereof, or the University of Washington. The views and opinions of authors expressed herein do not necessarily state or reflect those of the United States Government or any agency thereof.
