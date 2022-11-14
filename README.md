# LO_traps
 Module to add tiny rivers and wastewater treatment plants to LiveOcean.

 ---
## Description

LO_traps is a module that contains all data and scripts required to add tiny rivers and point sources (TRAPS) to LiveOcean. Tiny rivers are defined as smaller rivers that do not already exist in LiveOcean. Point sources are anthropogenic point sources such as wastewater treatment plants and factories.

The TRAPS integration module is a work in progress. If you encounter any bugs or have general feedback, please email auroral@uw.edu. Thanks!

All data and souce locations have been downloaded from Washington State Department of Ecology's [website](https://fortress.wa.gov/ecy/ezshare/EAP/SalishSea/SalishSeaModelBoundingScenarios.html). These data are also used in the Salish Sea Model.

---
## Where to put which Files

To enable TRAPS, you will need to move the files in LO_traps to the correct directory within the LO system (e.g. LO_data, LO_output, LO_user, etc.).

First, clone the LO_traps repo onto your computer so you can pull updates easily. However, you will still need to manually copy files from your instance of LO_traps into the correct folder within the LO system.

The directories within LO_traps are named after their corresponding directory in the LO system. For example, files and folders within LO_traps/data should be saved in your LO_data.

More details can be found in each subfolder of LO_traps.