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

---
## Adding TRAPS climatology to pre-existing LO rivers (2023.01.05 update)
Upon request, I have created and generated forcing for pre-existing LiveOcean rivers for which Ecology has data. These are all of the rivers in Ecology's dataset that are duplicates of LiveOcean rivers (and are thus not treated as a tiny river). As part of this update, I have created a new climatology script in LO_traps/pre/traps/make_climatology_LOrivbio.py to generate climatology for these duplicate rivers. I have also created a new folder LO_traps/user/forcing/traps1 with updated versions of make_forcing_main.py and trapsfun.py that use the new climatologies.

There are three confusing parts to the new code:
1. Not all pre-existing LiveOcean rivers have a corresponding duplicate in Ecology's dataset. Thus, the file in LO_traps/data/LiveOcean_SSM_rivers.xlsx is frequently used to identify which of the pre-existing rivers do have Ecology data.
2. LiveOcean and Ecology's dataset use different names for the same rivers. Thus, there are several places in the code in which the name must be converted. When reading data and writing forcing for the pre-existing LiveOcean rivers, the LO name must be used. When generating climatology, or using climatology to create forcing, the Ecology/SSM name must be used. The helper function trapsfun.LO2SSM_name helps handle this conversion.
3. Some pre-existing LiveOcean rivers that have a corresponding duplicate in Ecology's dataset have weird values. I call them "weird rivers." Some characteristics include near-zero DO, negative TIC, and zero alkalinity. Rather than using Ecology's data for weird rivers, I have deferred to LiveOcean's default handling of these rivers. Thus, there are places within the code in which I subtract a list of "weird rivers" from the list of pre-existing, duplicate rivers.
