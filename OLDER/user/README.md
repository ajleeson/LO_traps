# LO_traps/user

### traps0 vs traps1

As of 2023.01.06, the user can choose whether to use Ecology's biogeochemistry values for pre-existing LiveOcean rivers.

The **traps0** forcing folder does not use Ecology's data to generate biogeochemistry forcing for pre-existing LiveOcean rivers. Instead, the biology is handled by LiveOcean's default, using functions in rivfun.py.

The **traps1** forcing folder generates biogeochemistry forcing for pre-existing LiveOcean rivers using Ecology's data. Note that not all pre-existing rivers have Ecology data. However, for the rivers that are duplicated, Ecology's data is used. There are 20 such rivers. The forcing is handled using functions in trapsfun.py. Only biogeochemistry parameters (TIC, TAlk, Oxyg, NO3, NH4) use Ecology's data. Temperature and flowrate are still handled using LiveOcean's default functions.

*2023.03.20 Update*

Given the issues with vertical sources, the **traps2** forcing folder can be used to add point sources as horizontal sources. Note that this forcing folder also uses Ecology's biogeochemistry for pre-existing LiveOcean rivers.

*2023.05.10 Update*

I have added **traps3** which, similar to traps2, treats vertical sources like horizontal sources. The only difference is that nitrate/nitrite and ammonium is set to zero for WWTPs.