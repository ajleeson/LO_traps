# LO_traps/user

## LO_traps/user/forcing

Copy LO_traps/user/forcing/traps0 into your instance of LO_user/forcing. This folder contains 3 scripts. The rivfun.py script is borrowed directly from LO/forcing/riv00.

- **trapsfun.py:** This code has similar functionality to rivfun.py. It contains helper functions used to generate forcing for TRAPS. It also contains the most complex algorithms in the TRAPS module which take in TRAPS lat/lon coordinates and place the TRAPS on the nearest coastal grid cell.
- **make_forcing_main.py:** This script should be used generate a rivers.nc forcing file like any other model run. However, it adds TRAPS to the forcing generation process, calling upon trapsfun.py. Users can choose to enable either tiny rivers, point sources, or both by toggling the logical switches on lines 21 and 22 of this file.

![enablingtraps](https://user-images.githubusercontent.com/15829099/209865242-878e6657-cbc6-4bac-b583-19273b5fcf3a.png)

*NOTE:* If you enable point sources, then you must also enable LwSrc in the corresponding BLANK.in file. LuvSrc will already be enabled by default because rivers introduce horizontal (or u- v-) momentum to the system. Point sources discharge vertically (w-momentum), so LwSrc must be set to 'T' true. Example screenshot below.

 ![enable_lwsrc](https://user-images.githubusercontent.com/15829099/209903422-4f3f238b-68f8-44e4-b31d-2448cc5d9053.png)

### traps0 vs traps1

As of 2023.01.06, the user can choose whether to use Ecology's biogeochemistry values for pre-existing LiveOcean rivers.

The **traps0** forcing folder does not use Ecology's data to generate biogeochemistry forcing for pre-existing LiveOcean rivers. Instead, the biology is handled by LiveOcean's default, using functions in rivfun.py.

The **traps1** forcing folder generates biogeochemistry forcing for pre-existing LiveOcean rivers using Ecology's data. Note that not all pre-existing rivers have Ecology data. However, for the rivers that are duplicated, Ecology's data is used. There are 20 such rivers. The forcing is handled using functions in trapsfun.py. Only biogeochemistry parameters (TIC, TAlk, Oxyg, NO3, NH4) use Ecology's data. Temperature and flowrate are still handled using LiveOcean's default functions.

---

## LO_traps/user/pre

*Note, that this is an optional module. Unless you plan on modifying the climatology script and generating new TRAPS climatology, you do not need these files to run the TRAPS module. Instead, you can simply copy the results of climatology generation in LO_traps/output.*

Copy LO_traps/user/pre/traps into your instance of LO_user/pre. This directory contains three files:

- **make_climatology_pointsources.py:** Creates climatology files for all point sources using Ecology's data in LO_traps/data/point_sources.
- **make_climatology_tinyrivers.py**: Creates climatology files for river mouths using Ecology's data in LO_traps/data/nonpoint_sources. This script does not generate climatology for pre-existing rivers in LiveOcean.
- **make_climatology_LOrivbio.py:** Creates biogeochemistry climatology files for all pre-existing LiveOcean rivers for which Ecology has data in LO_traps/data/nonpoint_sources. This script does not generate climatology for tiny rivers, nor does it generate flowrate or temperature climatology.

To run the climatology scripts, go to ipython from LO_user/pre/traps and do

```
run make_climatology_tinyrivers.py
run make_climatology_pointsources.py
run make_climatology_LOrivbio.py
```

To generate forcing, you will need to copy the output into the corresponding directory on Perigee.