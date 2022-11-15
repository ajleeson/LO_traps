# LO_traps/user

### LO_traps/user/forcing

Copy LO_traps/user/forcing/traps0 into your instance of LO_user/forcing. This folder contains 3 scripts. The rivfun.py script is borrowed directly from LO/forcing/riv00.

- **trapsfun.py:** This code has similar functionality to rivfun.py. It contains helper functions used to generate forcing for TRAPS. It also contains the most complex algorithms in the TRAPS module which take in TRAPS lat/lon coordinates and place the TRAPS on the nearest coastal grid cell.
- **make_forcing_main.py:** This script should be used generate a rivers.nc forcing file like any other model run. However, it adds TRAPS to the forcing generation process, calling upon trapsfun.py. Users can choose to enable either tiny rivers, point sources, or both by toggling the logical switches on lines 25 and 26 of this file.

![enablingtraps](https://user-images.githubusercontent.com/15829099/201500023-fe168b8a-84fd-485e-a1c8-9431ed8ee74d.png)

---

### LO_traps/user/pre

*Note, that this is an optional module. Unless you plan on modifying the climatology script and generating new TRAPS climatology, you do not need these files to run the TRAPS module. Instead, you can simply copy the results of climatology generation in LO_traps/output.*

Copy LO_traps/user/pre/traps into your instance of LO_user/pre. This directory contains four files:

- **make_climatology_pointsources.py:** Creates climatology files for all point sources using Ecology's data in LO_traps/data/point_sources.
- **make_climatology_tinyrivers.py**: Creates climatology files for all river mouths using Ecology's data in LO_traps/data/nonpoint_sources.

To run the climatology scripts, go to ipython from LO_user/pre/traps and do

```
run make_climatology_tinyrivers.py
run make_climatology_pointsources.py
```
