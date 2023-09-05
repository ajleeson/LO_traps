# LO_traps/user/forcing

This folder contains forcing directories used to generate TRAPS forcing. Every forcing directory should contain some verions of the scripts detailed below.

---
## Forcing folders

<details><summary><strong>trapsV00 (2023.09.04)</strong></summary>

This is the first, fully functional, version of TRAPS. The code implements WWTPs as vertical sources (and they no longer blow up!).

The code in trapsV00 has also been cleaned, commented, and restructured as part of a major refactoring effort.

</details>

---
## make_forcing_main.py & make_[source type]_forcing.py

These scripts generate a rivers.nc file for ROMS. The file is saved in LO_output/forcing/[gridname]/[fdate]/trapsV00.

<details><summary><strong>Summary</strong></summary>

The `make_forcing_main.py` script is based off of typical `make_forcing_main.py` scripts used in LiveOcean. They both generate flow, temperature, salt, and biogeochemistry forcing for sources. What makes the new `make_forcing_main.py` different is that the actual forcing generation for pre-existing LO rivers, tiny rivers, and point sources are all handled separately in three different helper scripts:

- make_LOriv_forcing.py
- make_triv_forcing.py
- make_wwtp_forcing.py

The scripts have been separated to improve readability. Now, `make_forcing_main.py` simply calls each of these helper scripts and concatenates their results into one dataset. The final dataset is saved as rivers.nc.

</details>

<details><summary><strong>Important details</strong></summary>

*Notes for make_LOriv_forcing.py*

- The flow and temperature data for all pre-existing LO rivers is unchanged compared to prior versions of LO.
- There are several pre-exsiting LO rivers for which Ecology also has data. The biogeochemistry variables for these duplicate pre-existing rivers are thus filled using the TRAPS climatology based on Ecology's data (LO_user/pre/traps/make_climatology_LOrivbio.py).
- Some duplicate rivers have weird values in Ecology's dataset (i.e. zero DO, negative TIC, etc.). The algorithm opts to **not** use Ecology's data for these weird rivers, and instead leave these pre-existing rivers unchanged.
- Fraser river NH4 is set to a constant 4.43 mmol/m3 concentration, as recommended by Susan Allen.

*Overlapping rivers in make_triv_forcing.py & make_wwtp_forcing.py*

- Sometimes, a pair of tiny rivers or a pair of WWTPs may be mapped to the same cell on the model grid. They are 'overlapping' sources.
- To ensure that ROMS does not get confused, the forcing algorithm consolidates the overlapping sources into a single source.
- The names of the overlapping sources are combine using a '+'. For instance, the tiny rivers 'Perry Cr' and 'McLane Cr' get combined into a single river called 'Perry Cr+McLane Cr'
- The flowrate of the consolidate source is the sum of the two sources
- The other variables are consolidated using a weighted average based on flowrate

*WWTP open and close dates*

- LO_data/traps/wwtp_open_close_dates.xlsx contains a list of WWTPs and their open/close years
- The `make_wwtp_forcing.py` script checks this file. If a WWTP is closed for the year in which forcing is being generated, then the discharge rate is padded with zeros

</details>

<details><summary><strong>Disabling TRAPS</strong></summary>

Users can choose to enable either tiny rivers, point sources, or both by toggling the logical switches on lines 21 and 22 of this file.

![enablingtraps](https://user-images.githubusercontent.com/15829099/209865242-878e6657-cbc6-4bac-b583-19273b5fcf3a.png)

*NOTE:* If you enable point sources, then you must also enable LwSrc in the corresponding BLANK.in file. LuvSrc will already be enabled by default because rivers introduce horizontal (or u- v-) momentum to the system. Point sources discharge vertically (w-momentum), so LwSrc must be set to 'T' true. Example screenshot below.

 ![enable_lwsrc](https://user-images.githubusercontent.com/15829099/209903422-4f3f238b-68f8-44e4-b31d-2448cc5d9053.png)

 </details>

---
## trapsfun.py

This script has similar functionality to rivfun.py. It contains helper functions used to generate forcing for TRAPS.

---
## rivfun.py

This script was borrowed directly from Parker's riv00 forcing. It is included in TRAPS because it contains necessary functions to generate forcing for pre-existing LO rivers.