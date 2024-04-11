# Graphical interface
The interface allows for easy simulations with MCDS, it also contains a section to add FLUKA files, databases can be generated, and it contains a built-in plotting interface.

## Execution
Before running the code, the following Python libraries must be installed: PyQt5, matplotlib, numpy, scipy, uncertainties, and natsort.
To use the interface, simply execute `main.py`.

# Usage
Specify the name of the folder where the files will be saved when running simulations with MCDS or creating a database. This can be ignored, in which case the folder will have a default name.
The various options are found in the top menu: MCDS, Fluka, Plot, Database, and Model.

## MCDS
Contains the necessary parameters to create an input file, each set of parameters can be added to the interface as required. After defining the values, select `Generate input` to create a `.inp` file in the chosen folder at the beginning. You can select a different folder under `New folder`.
Once the input generation is complete, you can run the simulation by selecting `Launch simulations`. This opens a folder selection and then runs the simulations for all files within it.
Finally, an option is included to calculate cell survival using the selected model (see **Model**) and choosing the type of cell to use (HSG and V79 currently).

## Fluka
You can add this option by selecting `Add Fluka parameters`. In this window, you must choose 2 folders with files obtained from Fluka: `dose data`, `spectrum data`. Additionally, a folder with at least one database must be added (see **Database**).

You must add values for the minimum and maximum depth of the beam along with the point separation (bins) matching the Fluka files. Additionally, you must specify the type of cell (V79 or HSG), the amount of DNA, the diameter of the cell nucleus, and the maximum dose. Once all parameters are added, you can select `Fluka -> survival` from the top menu to obtain an output file with survival at different depths. The parameters of the output file are:
- Depth
- Dose + error
- DSB's Yield + error
- Lambda + error
- Survival + error.

## Plot
The plotting interface is displayed. Specify the type of plot and the folder containing the files with information to plot. You can specify the plot label and a set of experimental data, but it's optional.
Once the necessary parameters are added, select `Generate plots` and the program plots what is in the provided folder, showing one plot at a time. You can select `Next plot` or `Previous plot` to navigate through the files in the folder in order. You can change the plot type by changing the selection in `Plot type` and regenerating the plots.

To add more than one curve or set of points at once, select `Add another plot`. The different plots are displayed next to it, and by selecting one of these, you can specify the folder, experimental data set, label, and point separation for that curve. Finally, by clicking on `Generate plots`, all curves are plotted together with their respective labels. If a label is not specified, a default one is used.

## Database
A database can be generated that can be used later in the **Fluka** section. You must choose the type of particle, the number of energy or dose points, and you can specify energy/dose ranges different from the defaults. Additionally, values can be specified for the seed, number of simulations (nocs), nuclear diameter, and amount of DNA different from the default values.
Finally, by selecting `Generate database`, inputs and outputs are generated within a folder with the name provided in the initial window, and finally, a `.database` file is created containing:
- Energy
- Entrance LET to the cell
- Entrance LET to the nucleus
- Exit LET from the nucleus
- DSB's Yield + error
- Lambda + error
You can choose a different folder by selecting `New folder` within the top menu `MCDS`.

## Model
You can select the type of model to calculate survival. Currently, only the Wang model (2018) is used.

## Shortcuts
-  `Ctrl+Q` to generate an MCDS input
-  `Ctrl+W` to launch simulations from the selected folder
