# LO_traps/data

Copy LO_traps/data/traps into your instance of LO_data on your local computer and on perigee. This directory contains four files/folders.

- **LiveOcean_SSM_rivers.xlsx:** Excel sheet with list of duplicate rivers in LiveOcean and the Salish Sea Model. When you create TRAPS climatology and when you generate forcing, LO_traps/user/pre/make_climatology and the trapsfun.py script in LO_traps/user/forcing will look at this excel sheet to determine which rivers to omit from LiveOcean. This ensures that TRAPS does not add duplicate rivers to LiveOcean.
- **SSM_source_info.xlsx:** Lat/lon coordinates of all river mouths and point sources in SSM. Used by LO_traps/user/forcing/trapsfun.py to determine where in the LiveOcean grid to place a TRAPS. Also contains other metadata about the sources (i.e. Canadian or US source, region, etc.)
- **nonpoint_sources (dir)**: Ecology's timeseries data of state variables for all river mouths. Used in LO_traps/user/pre/traps to generate climatology files. Provides daily values.
- **point_sources (dir):** Ecology's timeseries data of state variables for all point sources. Used in LO_traps/user/pre/traps to generate climatology files. Provides monthly values.