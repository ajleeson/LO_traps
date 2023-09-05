# LO_traps/user/forcing

- **trapsfun.py:** This code has similar functionality to rivfun.py. It contains helper functions used to generate forcing for TRAPS.

- **make_forcing_main.py:** This script should be used generate a rivers.nc forcing file like any other model run. However, it adds TRAPS to the forcing generation process, calling upon trapsfun.py. Users can choose to enable either tiny rivers, point sources, or both by toggling the logical switches on lines 21 and 22 of this file.

![enablingtraps](https://user-images.githubusercontent.com/15829099/209865242-878e6657-cbc6-4bac-b583-19273b5fcf3a.png)

*NOTE:* If you enable point sources, then you must also enable LwSrc in the corresponding BLANK.in file. LuvSrc will already be enabled by default because rivers introduce horizontal (or u- v-) momentum to the system. Point sources discharge vertically (w-momentum), so LwSrc must be set to 'T' true. Example screenshot below.

 ![enable_lwsrc](https://user-images.githubusercontent.com/15829099/209903422-4f3f238b-68f8-44e4-b31d-2448cc5d9053.png)