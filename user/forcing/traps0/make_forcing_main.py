"""
This is the main program for making the RIVER and TRAPS forcing file, for the
updated ROMS

Test on mac in ipython:
run make_forcing_main.py -g cas6 -r backfill -d 2020.01.01 -f traps0 -test True


"""

from pathlib import Path
import sys, os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from lo_tools import forcing_argfun2 as ffun

Ldir = ffun.intro() # this handles all the argument passing
result_dict = dict()
result_dict['start_dt'] = datetime.now()

# ENABLE OR DISABLE TINY RIVERS AND/OR POINT SOURCES
enable_tinyrivers = True 
enable_pointsources = True

# ****************** CASE-SPECIFIC CODE *****************

date_string = Ldir['date_string']
out_dir = Ldir['LOo'] / 'forcing' / Ldir['gridname'] / ('f' + date_string) / Ldir['frc']

import xarray as xr
from lo_tools import Lfun, zrfun
import numpy as np
import pandas as pd
import rivfun
import trapsfun

if Ldir['testing']:
    from importlib import reload
    reload(zrfun)
    reload(rivfun)

out_fn = out_dir / 'rivers.nc'
out_fn.unlink(missing_ok=True)

# set up the time index for the record
dsf = Ldir['ds_fmt']
dt0 = datetime.strptime(Ldir['date_string'],dsf) - timedelta(days=2.5)
dt1 = datetime.strptime(Ldir['date_string'],dsf) + timedelta(days=4.5)
days = (dt0, dt1)
    
# pandas Index objects
dt_ind = pd.date_range(start=dt0, end=dt1)
yd_ind = pd.Index(dt_ind.dayofyear)

ot_vec = np.array([Lfun.datetime_to_modtime(item) for item in dt_ind])
NT = len(ot_vec)

S_info_dict = Lfun.csv_to_dict(Ldir['grid'] / 'S_COORDINATE_INFO.csv')
S = zrfun.get_S(S_info_dict)
N = S['N']

grid_fn = Ldir['grid'] / 'grid.nc'
G = zrfun.get_basic_info(grid_fn, only_G=True)

###############################################################################################
# LIVEOCEAN PRE-EXISTING RIVERS

# Load a dataframe with info for rivers to get
gridname = 'cas6'
ri_dir = Ldir['LOo'] / 'pre' / 'river' / gridname
ri_fn = ri_dir / 'river_info.csv'
ri_df = pd.read_csv(ri_fn, index_col='rname')

# get historical and climatological data files
year0 = 1980
year1 = 2020
# historical and climatological data
Ldir['Hflow_fn'] = ri_dir / 'Data_historical' / ('ALL_flow_' + str(year0) + '_' + str(year1) + '.p')
Ldir['Cflow_fn'] = ri_dir / 'Data_historical' / ('CLIM_flow_' + str(year0) + '_' + str(year1) + '.p')
Ldir['Ctemp_fn'] = ri_dir / 'Data_historical' / ('CLIM_temp_' + str(year0) + '_' + str(year1) + '.p')

# get the list of rivers and indices for this grid
gri_fn = Ldir['grid'] / 'river_info.csv'
gri_df = pd.read_csv(gri_fn, index_col='rname')
if Ldir['testing']:
    gri_df = gri_df.loc[['columbia', 'skagit'],:]
NRIV = len(gri_df)

# associate rivers with ones that have temperature climatology data
ri_df = rivfun.get_tc_rn(ri_df)

# get the flow and temperature data for these days
qt_df_dict = rivfun.get_qt(gri_df, ri_df, dt_ind, yd_ind, Ldir, dt1, days)

# Start Dataset
LOriv_ds = xr.Dataset()

# Add time coordinate
LOriv_ds['river_time'] = (('river_time',), ot_vec)
LOriv_ds['river_time'].attrs['units'] = Lfun.roms_time_units
LOriv_ds['river_time'].attrs['long_name'] = 'river time'

# Add river coordinate
LOriv_ds['river'] = (('river',), np.arange(1,NRIV+1))
LOriv_ds['river'].attrs['long_name'] = 'river runoff identification number'

# Add river names
LOriv_ds['river_name'] = (('river',), list(gri_df.index))
LOriv_ds['river_name'].attrs['long_name'] = 'river name'

# Add Vshape
vn = 'river_Vshape'
vinfo = zrfun.get_varinfo(vn, vartype='climatology')
dims = ('s_rho', 'river')
# For Vtransform = 2, even spacing is a good approximation, and
# we implement this by using 1/N as the fraction in each vertical cell.
Vshape = (1/N) * np.ones((N, NRIV))
LOriv_ds[vn] = (dims, Vshape)
LOriv_ds[vn].attrs['long_name'] = vinfo['long_name']

# Add position and direction
for vn in ['river_Xposition', 'river_Eposition', 'river_direction']:
    vinfo = zrfun.get_varinfo(vn, vartype='climatology')
    if vn == 'river_direction':
        LOriv_ds[vn] = (('river',), gri_df.idir.to_numpy())
    elif vn == 'river_Xposition':
        X_vec = np.nan * np.ones(NRIV)
        ii = 0
        for rn in gri_df.index:
            if gri_df.loc[rn, 'idir'] == 0:
                X_vec[ii] = gri_df.loc[rn, 'col_py'] + 1
            elif gri_df.loc[rn, 'idir'] == 1:
                X_vec[ii] = gri_df.loc[rn, 'col_py']
            ii += 1
        LOriv_ds[vn] = (('river',), X_vec)
    elif vn == 'river_Eposition':
        E_vec = np.nan * np.ones(NRIV)
        ii = 0
        for rn in gri_df.index:
            if gri_df.loc[rn, 'idir'] == 0:
                E_vec[ii] = gri_df.loc[rn, 'row_py']
            elif gri_df.loc[rn, 'idir'] == 1:
                E_vec[ii] = gri_df.loc[rn, 'row_py'] + 1
            ii += 1
        LOriv_ds[vn] = (('river',), E_vec)
    LOriv_ds[vn].attrs['long_name'] = vinfo['long_name']
        

# Add transport
vn = 'river_transport'
vinfo = zrfun.get_varinfo(vn, vartype='climatology')
dims = (vinfo['time'],) + ('river',)
Q_mat = np.zeros((NT, NRIV))
rr = 0
for rn in gri_df.index:
    qt_df = qt_df_dict[rn]
    flow = qt_df['final'].values
    Q_mat[:,rr] = flow * gri_df.loc[rn, 'isign']
    rr += 1
LOriv_ds[vn] = (dims, Q_mat)
LOriv_ds[vn].attrs['long_name'] = vinfo['long_name']
LOriv_ds[vn].attrs['units'] = vinfo['units']

# Add salinity and temperature
for vn in ['river_salt', 'river_temp']:
    vinfo = zrfun.get_varinfo(vn, vartype='climatology')
    dims = (vinfo['time'],) + ('s_rho', 'river')
    if vn == 'river_salt':
        TS_mat = np.zeros((NT, N, NRIV))
    elif vn == 'river_temp':
        TS_mat = np.nan * np.zeros((NT, N, NRIV))
        rr = 0
        for rn in gri_df.index:
            qt_df = qt_df_dict[rn]
            for nn in range(N):
                TS_mat[:, nn, rr] = qt_df['temperature'].values
            rr += 1
    if np.isnan(TS_mat).any():
        print('Error from riv00: nans in river_temp!')
        sys.exit()
    LOriv_ds[vn] = (dims, TS_mat)
    LOriv_ds[vn].attrs['long_name'] = vinfo['long_name']
    LOriv_ds[vn].attrs['units'] = vinfo['units']
    
# Add biology (see the lineup near the end of fennel_var.h)
bvn_list = ['NO3', 'NH4', 'Phyt', 'Zoop', 'LDeN', 'SDeN', 'Chlo',
        'TIC', 'TAlk', 'LDeC', 'SDeC', 'Oxyg']
for bvn in bvn_list:
    vn = 'river_' + bvn
    vinfo = zrfun.get_varinfo(vn)
    dims = (vinfo['time'],) + ('s_rho', 'river')
    B_mat = np.nan * np.zeros((NT, N, NRIV))
    rr = 0
    for rn in gri_df.index:
        qt_df = qt_df_dict[rn]
        for nn in range(N):
            B_mat[:, nn, rr] = rivfun.get_bio_vec(bvn, rn, yd_ind)
        rr += 1
    if np.isnan(B_mat).any():
        print('Error from riv00: nans in B_mat for ' + vn)
        sys.exit()
    LOriv_ds[vn] = (dims, B_mat)
    LOriv_ds[vn].attrs['long_name'] = vinfo['long_name']
    LOriv_ds[vn].attrs['units'] = vinfo['units']
###########################################################################################
# FORCING FOR TINY RIVERS

# Start Dataset
triv_ds = xr.Dataset()

NTRIV = 0

if enable_tinyrivers == True:

    # Run placement algorithm to put tiny rivers on LiveOcean grid
    trapsfun.traps_placement('riv')

    # define directory for tiny river climatology
    tri_dir = Ldir['LOo'] / 'pre' / 'traps' / 'tiny_rivers'
    traps_type = 'triv'

    # climatological data files
    year0 = 1999
    year1 = 2017
    # climatological data
    Ldir['Cflow_triv_fn'] = tri_dir / 'Data_historical' / ('CLIM_flow_' + str(year0) + '_' + str(year1) + '.p')
    Ldir['Ctemp_triv_fn'] = tri_dir / 'Data_historical' / ('CLIM_temp_' + str(year0) + '_' + str(year1) + '.p')
    Ldir['CDO_triv_fn']   = tri_dir / 'Data_historical' / ('CLIM_DO_' + str(year0) + '_' + str(year1) + '.p')
    Ldir['CNH4_triv_fn']  = tri_dir / 'Data_historical' / ('CLIM_NH4_' + str(year0) + '_' + str(year1) + '.p')
    Ldir['CNO3_triv_fn']  = tri_dir / 'Data_historical' / ('CLIM_NO3_' + str(year0) + '_' + str(year1) + '.p')
    Ldir['CTalk_triv_fn'] = tri_dir / 'Data_historical' / ('CLIM_Talk_' + str(year0) + '_' + str(year1) + '.p')
    Ldir['CTIC_triv_fn']  = tri_dir / 'Data_historical' / ('CLIM_TIC_' + str(year0) + '_' + str(year1) + '.p')

    # get the list of rivers and indices for this grid
    gri_fn = Ldir['grid'] / 'triv_info.csv'
    gri_df = pd.read_csv(gri_fn, index_col='rname')
    if Ldir['testing']:
        gri_df = gri_df.loc[['Kennedy_Schneider', 'North Olympic'],:]
    NTRIV = len(gri_df)

    # get the flow, temperature, and nutrient data for these days
    qtbio_triv_df_dict = trapsfun.get_qtbio(gri_df, dt_ind, yd_ind, Ldir, traps_type)

    # Add time coordinate
    triv_ds['river_time'] = (('river_time',), ot_vec)
    triv_ds['river_time'].attrs['units'] = Lfun.roms_time_units
    triv_ds['river_time'].attrs['long_name'] = 'river time'

    # Add river coordinate
    triv_ds['river'] = (('river',), np.arange(NRIV+1,NRIV+NTRIV+1))
    triv_ds['river'].attrs['long_name'] = 'tiny river runoff identification number'

    # Add river names
    triv_ds['river_name'] = (('river',), list(gri_df.index))
    triv_ds['river_name'].attrs['long_name'] = 'tiny river name'

    # Add Vshape
    vn = 'river_Vshape'
    vinfo = zrfun.get_varinfo(vn, vartype='climatology')
    dims = ('s_rho', 'river')
    # For Vtransform = 2, even spacing is a good approximation, and
    # we implement this by using 1/N as the fraction in each vertical cell.
    Vshape = (1/N) * np.ones((N, NTRIV))
    triv_ds[vn] = (dims, Vshape)
    triv_ds[vn].attrs['long_name'] = vinfo['long_name']

    # Add position and direction
    for vn in ['river_Xposition', 'river_Eposition', 'river_direction']:
        vinfo = zrfun.get_varinfo(vn, vartype='climatology')
        if vn == 'river_direction':
            triv_ds[vn] = (('river',), gri_df.idir.to_numpy())
        elif vn == 'river_Xposition':
            X_vec = np.nan * np.ones(NTRIV)
            ii = 0
            for rn in gri_df.index:
                if gri_df.loc[rn, 'idir'] == 0:
                    X_vec[ii] = gri_df.loc[rn, 'col_py'] + 1
                elif gri_df.loc[rn, 'idir'] == 1:
                    X_vec[ii] = gri_df.loc[rn, 'col_py']
                ii += 1
            triv_ds[vn] = (('river',), X_vec)
        elif vn == 'river_Eposition':
            E_vec = np.nan * np.ones(NTRIV)
            ii = 0
            for rn in gri_df.index:
                if gri_df.loc[rn, 'idir'] == 0:
                    E_vec[ii] = gri_df.loc[rn, 'row_py']
                elif gri_df.loc[rn, 'idir'] == 1:
                    E_vec[ii] = gri_df.loc[rn, 'row_py'] + 1
                ii += 1
            triv_ds[vn] = (('river',), E_vec)
        triv_ds[vn].attrs['long_name'] = vinfo['long_name']

    # Add transport
    vn = 'river_transport'
    vinfo = zrfun.get_varinfo(vn, vartype='climatology')
    dims = (vinfo['time'],) + ('river',)
    Q_mat = np.zeros((NT, NTRIV))
    rr = 0
    for rn in gri_df.index:
        qtbio_triv_df = qtbio_triv_df_dict[rn]
        flow = qtbio_triv_df['flow'].values
        Q_mat[:,rr] = flow * gri_df.loc[rn, 'isign']
        rr += 1
    triv_ds[vn] = (dims, Q_mat)
    triv_ds[vn].attrs['long_name'] = vinfo['long_name']
    triv_ds[vn].attrs['units'] = vinfo['units']

    # Add salinity and temperature
    for vn in ['river_salt', 'river_temp']:
        vinfo = zrfun.get_varinfo(vn, vartype='climatology')
        dims = (vinfo['time'],) + ('s_rho', 'river')
        if vn == 'river_salt':
            TS_mat = np.zeros((NT, N, NTRIV))
        elif vn == 'river_temp':
            TS_mat = np.nan * np.zeros((NT, N, NTRIV))
            rr = 0
            for rn in gri_df.index:
                qtbio_triv_df = qtbio_triv_df_dict[rn]
                for nn in range(N):
                    TS_mat[:, nn, rr] = qtbio_triv_df['temp'].values
                rr += 1
        if np.isnan(TS_mat).any():
            print('Error from traps00: nans in tiny river river_temp!')
            sys.exit()
        triv_ds[vn] = (dims, TS_mat)
        triv_ds[vn].attrs['long_name'] = vinfo['long_name']
        triv_ds[vn].attrs['units'] = vinfo['units']

    # Add biology that have existing climatology
    for var in ['NO3', 'NH4', 'TIC', 'TAlk', 'Oxyg']:
        vn = 'river_' + var
        vinfo = zrfun.get_varinfo(vn, vartype='climatology')
        dims = (vinfo['time'],) + ('s_rho', 'river')
        B_mat = np.nan * np.zeros((NT, N, NTRIV))
        rr = 0
        for rn in gri_df.index:
            qtbio_triv_df = qtbio_triv_df_dict[rn]
            for nn in range(N):
                B_mat[:, nn, rr] = qtbio_triv_df[var].values
            rr += 1
        if np.isnan(TS_mat).any():
            print('Error from traps00: nans in tiny river bio!')
            sys.exit()
        triv_ds[vn] = (dims, B_mat)
        triv_ds[vn].attrs['long_name'] = vinfo['long_name']
        triv_ds[vn].attrs['units'] = vinfo['units']

    # Add remaining biology (see the lineup near the end of fennel_var.h)
    # I'm pretty sure this is simply filling everything with zeros
    bvn_list = ['Phyt', 'Zoop', 'LDeN', 'SDeN', 'Chlo', 'LDeC', 'SDeC']
    for bvn in bvn_list:
        vn = 'river_' + bvn
        vinfo = zrfun.get_varinfo(vn)
        dims = (vinfo['time'],) + ('s_rho', 'river')
        B_mat = np.nan * np.zeros((NT, N, NTRIV))
        rr = 0
        for rn in gri_df.index:
            qtbio_triv_df = qtbio_triv_df_dict[rn]
            for nn in range(N):
                B_mat[:, nn, rr] = rivfun.get_bio_vec(bvn, rn, yd_ind)
            rr += 1
        if np.isnan(B_mat).any():
            print('Error from traps00: nans in B_mat for tiny river ' + vn)
            sys.exit()
        triv_ds[vn] = (dims, B_mat)
        triv_ds[vn].attrs['long_name'] = vinfo['long_name']
        triv_ds[vn].attrs['units'] = vinfo['units']

###########################################################################################
# FORCING FOR MARINE POINT SOURCES

# Start Dataset
wwtp_ds = xr.Dataset()

NWWTP = len(gri_df)

if enable_pointsources == True:

    # Run placement algorithm to put marine point sources on LiveOcean grid
    trapsfun.traps_placement('wwtp')
    traps_type = 'wwtp'

    # define directory for tiny river climatology
    wwtp_dir = Ldir['LOo'] / 'pre' / 'traps' / 'point_sources'

    # climatological data files
    year0 = 1999
    year1 = 2017
    # climatological data
    Ldir['Cflow_wwtp_fn'] = wwtp_dir / 'Data_historical' / ('CLIM_flow_' + str(year0) + '_' + str(year1) + '.p')
    Ldir['Ctemp_wwtp_fn'] = wwtp_dir / 'Data_historical' / ('CLIM_temp_' + str(year0) + '_' + str(year1) + '.p')
    Ldir['CDO_wwtp_fn']   = wwtp_dir / 'Data_historical' / ('CLIM_DO_' + str(year0) + '_' + str(year1) + '.p')
    Ldir['CNH4_wwtp_fn']  = wwtp_dir / 'Data_historical' / ('CLIM_NH4_' + str(year0) + '_' + str(year1) + '.p')
    Ldir['CNO3_wwtp_fn']  = wwtp_dir / 'Data_historical' / ('CLIM_NO3_' + str(year0) + '_' + str(year1) + '.p')
    Ldir['CTalk_wwtp_fn'] = wwtp_dir / 'Data_historical' / ('CLIM_Talk_' + str(year0) + '_' + str(year1) + '.p')
    Ldir['CTIC_wwtp_fn']  = wwtp_dir / 'Data_historical' / ('CLIM_TIC_' + str(year0) + '_' + str(year1) + '.p')

    # get the list of rivers and indices for this grid
    gri_fn = Ldir['grid'] / 'wwtp_info.csv'
    gri_df = pd.read_csv(gri_fn, index_col='rname')
    if Ldir['testing']:
        gri_df = gri_df.loc[['West Point', 'Birch Bay'],:]
    NWWTP = len(gri_df)

    # get the flow, temperature, and nutrient data for these days
    qtbio_wwtp_df_dict = trapsfun.get_qtbio(gri_df, dt_ind, yd_ind, Ldir, traps_type)

    # Add time coordinate
    wwtp_ds['river_time'] = (('river_time',), ot_vec)
    wwtp_ds['river_time'].attrs['units'] = Lfun.roms_time_units
    wwtp_ds['river_time'].attrs['long_name'] = 'river time'

    # Add river coordinate
    wwtp_ds['river'] = (('river',), np.arange(NRIV+NTRIV+1,NRIV+NTRIV+NWWTP+1))
    wwtp_ds['river'].attrs['long_name'] = 'marine point source identification number'

    # Add river names
    wwtp_ds['river_name'] = (('river',), list(gri_df.index))
    wwtp_ds['river_name'].attrs['long_name'] = 'point source name'

    # Add Vshape
    vn = 'river_Vshape'
    vinfo = zrfun.get_varinfo(vn, vartype='climatology')
    dims = ('s_rho', 'river')
    # All discharge coming from the bottom layer
    Vshape = np.zeros((N, NWWTP))
    Vshape[0,:] = 1
    wwtp_ds[vn] = (dims, Vshape)
    wwtp_ds['river_Vshape'].attrs['long_name'] = vinfo['long_name']

    # Add position and direction
    for vn in ['river_Xposition', 'river_Eposition', 'river_direction']:
        vinfo = zrfun.get_varinfo(vn, vartype='climatology')
        if vn == 'river_direction':
            # set point source diretion to enter vertically (2)
            wwtp_direction = 2 * np.ones(NWWTP) 
            wwtp_ds[vn] = (('river',), wwtp_direction)
        elif vn == 'river_Xposition':
            X_vec = np.nan * np.ones(NWWTP)
            for ii,wn in enumerate(gri_df.index):
                X_vec[ii] = gri_df.loc[wn, 'col_py']
            wwtp_ds[vn] = (('river',), X_vec)
        elif vn == 'river_Eposition':
            E_vec = np.nan * np.ones(NWWTP)
            # ii = 0
            for ii,wn in enumerate(gri_df.index):
                E_vec[ii] = gri_df.loc[wn, 'row_py']
                # ii += 1
            wwtp_ds[vn] = (('river',), E_vec)
                # ii += 1
            wwtp_ds[vn] = (('river',), E_vec)
        wwtp_ds[vn].attrs['long_name'] = vinfo['long_name']

    # Add transport
    vn = 'river_transport'
    vinfo = zrfun.get_varinfo(vn, vartype='climatology')
    dims = (vinfo['time'],) + ('river',)
    Q_mat = np.zeros((NT, NWWTP))
    rr = 0
    for rn in gri_df.index:
        qtbio_wwtp_df = qtbio_wwtp_df_dict[rn]
        flow = qtbio_wwtp_df['flow'].values
        Q_mat[:,rr] = flow
        rr += 1
    wwtp_ds[vn] = (dims, Q_mat)
    wwtp_ds[vn].attrs['long_name'] = vinfo['long_name']
    wwtp_ds[vn].attrs['units'] = vinfo['units']

    # Add salinity and temperature
    for vn in ['river_salt', 'river_temp']:
        vinfo = zrfun.get_varinfo(vn, vartype='climatology')
        dims = (vinfo['time'],) + ('s_rho', 'river')
        if vn == 'river_salt':
            TS_mat = np.zeros((NT, N, NWWTP))
        elif vn == 'river_temp':
            TS_mat = np.nan * np.zeros((NT, N, NWWTP))
            rr = 0
            for rn in gri_df.index:
                qtbio_wwtp_df = qtbio_wwtp_df_dict[rn]
                for nn in range(N):
                    TS_mat[:, nn, rr] = qtbio_wwtp_df['temp'].values
                rr += 1
        if np.isnan(TS_mat).any():
            print('Error from traps00: nans in point source river_temp!')
            sys.exit()
        wwtp_ds[vn] = (dims, TS_mat)
        wwtp_ds[vn].attrs['long_name'] = vinfo['long_name']
        wwtp_ds[vn].attrs['units'] = vinfo['units']

    # Add biology that have existing climatology
    for var in ['NO3', 'NH4', 'TIC', 'TAlk', 'Oxyg']:
        vn = 'river_' + var
        vinfo = zrfun.get_varinfo(vn, vartype='climatology')
        dims = (vinfo['time'],) + ('s_rho', 'river')
        B_mat = np.nan * np.zeros((NT, N, NWWTP))
        rr = 0
        for rn in gri_df.index:
            qtbio_wwtp_df = qtbio_wwtp_df_dict[rn]
            for nn in range(N):
                B_mat[:, nn, rr] = qtbio_wwtp_df[var].values
            rr += 1
        if np.isnan(TS_mat).any():
            print('Error from traps00: nans in tiny river bio!')
            sys.exit()
        wwtp_ds[vn] = (dims, B_mat)
        wwtp_ds[vn].attrs['long_name'] = vinfo['long_name']
        wwtp_ds[vn].attrs['units'] = vinfo['units']

    # Add remaining biology (see the lineup near the end of fennel_var.h)
    # I'm pretty sure this is simply filling everything with zeros
    bvn_list = ['Phyt', 'Zoop', 'LDeN', 'SDeN', 'Chlo', 'LDeC', 'SDeC']
    for bvn in bvn_list:
        vn = 'river_' + bvn
        vinfo = zrfun.get_varinfo(vn)
        dims = (vinfo['time'],) + ('s_rho', 'river')
        B_mat = np.nan * np.zeros((NT, N, NWWTP))
        rr = 0
        for rn in gri_df.index:
            qtbio_wwtp_df = qtbio_wwtp_df_dict[rn]
            for nn in range(N):
                B_mat[:, nn, rr] = rivfun.get_bio_vec(bvn, rn, yd_ind)
            rr += 1
        if np.isnan(B_mat).any():
            print('Error from traps00: nans in B_mat for tiny river ' + vn)
            sys.exit()
        wwtp_ds[vn] = (dims, B_mat)
        wwtp_ds[vn].attrs['long_name'] = vinfo['long_name']
        wwtp_ds[vn].attrs['units'] = vinfo['units']

###########################################################################################

# combine all forcing datasets
all_ds = xr.merge([LOriv_ds,triv_ds, wwtp_ds])
# print(all_ds['river_name'])
# print(all_ds['river_Chlo'][0][0])

# Save to NetCDF
all_ds.to_netcdf(out_fn)
all_ds.close()

# -------------------------------------------------------

# test for success
if out_fn.is_file():
    result_dict['result'] = 'success' # success or fail
else:
    result_dict['result'] = 'fail'

# *******************************************************

result_dict['end_dt'] = datetime.now()
ffun.finale(Ldir, result_dict)
