# LO_traps/output

You may either run the climatology script yourself (see LO_traps/user/pre). Or, you may copy the generated climatology files from here. If you choose to copy:

Copy LO_traps/output/pre/traps into your instance of LO_output/pre on your local computer and on perigee. This folder contains 3 directories.

- **point_sources:** Climatology files for point sources generated by LO_traps/user/pre/traps/make_climatology_pointsources.py.
- **tiny_rivers:** Climatology files for tiny rivers generated by LO_traps/user/pre/traps/make_climatology_tinyrivs.py.
- **LO_rivbio:** Climatology files for pre-existing rivers generated by LO_traps/user/pre/traps/make_climatology_LOrivbio.py

You will need all of these directories to generate forcing for TRAPS.

These directories also contain a folder called climatology_plots with yearly profiles of the generated climatology for each source. These figures aren't necessary to run code, but they can be nice to look at.