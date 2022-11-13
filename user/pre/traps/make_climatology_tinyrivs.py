"""
Make climatologies for tiny rivers.
Discharge rate, temperature, and biogeochemisty variables.

Based on Ecology's timeseries, stored in LO_data/traps

This code shows how powerful pandas is for this kind of task.
Really just one line to make a climatology (the groupby call)
"""

from lo_tools import Lfun
Ldir = Lfun.Lstart()

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import datetime
import matplotlib.dates as mdates

# define year range to create climatologies
year0 = 1999
year1 = 2017

# define gridname
gridname = 'cas6'

# file with all traps names and ID numbers
traps_info_fn = Ldir['data'] / 'traps' / 'SSM_source_info.xlsx'
# location of historical data to process
riv_dir = Ldir['data'] / 'traps' / 'nonpoint_sources'
all_his_fns = os.listdir(riv_dir)

# Get all river names and river IDs
traps_info_df = pd.read_excel(traps_info_fn,usecols='D,E,F')
# Only interested in rivers
riv_all_df = traps_info_df.loc[traps_info_df['Inflow_Typ'] == 'River']
# remove duplicate river names (some are listed in two rows)
riv_singles_df = riv_all_df.loc[traps_info_df['Name'].str.contains('- 2') == False]
# rename rivers that have a ' - 1' at the end
riv_names_df = riv_singles_df['Name'].str.replace(' - 1', '')
# get river names and river ids
rivnames = riv_names_df.values
rivids = riv_singles_df['ID'].values

# # just Union River for now -------------------------------------------------
# rivnames = rivnames[90:91]
# rivids = rivids[90:91]

# initialize dataframes for all rivers
flow_clim_df = pd.DataFrame()
# salt_clim_df = pd.DataFrame()
temp_clim_df = pd.DataFrame()
NO3_clim_df  = pd.DataFrame()
NH4_clim_df  = pd.DataFrame()
# phyto_clim_df = pd.DataFrame()
# chlo_clim_df = pd.DataFrame()
TIC_clim_df  = pd.DataFrame()
Talk_clim_df = pd.DataFrame()
DO_clim_df   = pd.DataFrame()

# loop through all rivers
for i,rname in enumerate(rivnames):

    print('{}: {}'.format(i,rname))

    # get river index
    rID = rivids[i]
    
    riv_fn = ''

    # find Ecology's timeseries based on river id
    for fn in all_his_fns:
        root, ext = os.path.splitext(fn)
        if root.startswith(str(rID)) and ext == '.xlsx':
            riv_fn = fn
    
    # Let user know if couldn't find timeseries for a given river
    if riv_fn == '0':
        print('No history file found for {}'.format(rname))
        continue
    # Otherwise, read history file as df
    else:
        riv_fp = str(riv_dir)  + '/' + riv_fn
        riv_df = pd.read_excel(riv_fp, skiprows=[0])

    # rename columns so that they are standardized
    # I have previously verified that Ecology's .xlsx files all have the same parameters
    riv_df = riv_df.set_axis(['Date', 'Year', 'Month', 'Day',
                            'Hour', 'Minute', 'Bin1', 'Flow(m3/s)',
                            'Temp(C)','Salt(ppt)','NH4(mg/L)',
                            'NO3+NO2(mg/L)', 'PO4(mg/L)', 'DO(mg/L)',
                            'pH', 'DON(mg/L)', 'PON(mg/L)', 'DOP(mg/L)',
                            'POP(mg/L)', 'POCS(mg/L)', 'POCF(mg/L)',
                            'POCR(mg/L)', 'DOCS(mg/L)', 'DOCF(mg/L)',
                            'Diatoms', 'Dinoflag', 'Chl', 'DIC(mmol/m3)',
                            'Alk(mmol/m3)'], axis=1, inplace=False)

    # replace all zeros with nans, so zeros don't bias data
    riv_df = riv_df.replace(0, np.nan)

    # calculate averages (compress 1999-2017 timeseries to single day, with an average for each day)
    riv_avgs_df = riv_df.groupby(['Month','Day']).mean().reset_index()
    riv_avgs_df.index = riv_avgs_df.index + 1 # start day index from 1 instead of 0

    # Plot averages (this was written to test one river at a time, so only pass one river through for-loop)
    plotting = False
    vn = 'Flow(m3/s)'
    if plotting == True:
        fig, ax = plt.subplots(1,1, figsize=(11, 6))
        yrday = np.linspace(1,367,366)
        # Plot individual years
        for yr in range(1999,2018):
            riv_yr_df = riv_df.loc[riv_df['Year'] == yr]
            # Insert a nan on Feb 29 if not a leap year
            if np.mod(yr,4) != 0:
                # print('{} is not a leap year'.format(yr)) # debugging
                nans = [np.nan]*29
                riv_yr_df = riv_yr_df.reset_index(drop=True) # reset all dataframes to index from 0
                riv_yr_df.loc[58.5] = nans # leap year is 60th Julian day, so add a new 59th index since Python indexes from 0
                riv_yr_df = riv_yr_df.sort_index().reset_index(drop=True) # sort indices and renumber
                # print(riv_yr_df[58:61]) # debugging
            if yr == 2017:
                yrday_17 = np.linspace(1,214,213) # don't have full 2017 dataset
                plt.plot(yrday_17,riv_yr_df[vn],alpha=0.5, label=yr)
            else:
                plt.plot(yrday,riv_yr_df[vn],alpha=0.5, label=yr)
        # Plot average
        plt.plot(yrday,riv_avgs_df[vn].values, label='average', color='black', linewidth=2)
        plt.legend(loc='best', ncol = 4,fontsize=14)
        plt.ylabel(vn,fontsize=16)
        plt.xlabel('Julian Day',fontsize=16)
        ax.tick_params(axis='both', which='major', labelsize=14)
        plt.title(rname,fontsize=18)
        plt.show()

    # Add data to climatology dataframes, and convert to units that LiveOcean expects
    flow_clim_df[rname] = riv_avgs_df['Flow(m3/s)']             # [m3/s]
    # salt_clim_df[rname] = riv_avgs_df['Salt(ppt)']              # [PSS]
    temp_clim_df[rname] = riv_avgs_df['Temp(C)']                # [C]
    NO3_clim_df[rname]  = riv_avgs_df['NO3+NO2(mg/L)'] * 71.4   # [mmol/m3]
    NH4_clim_df[rname]  = riv_avgs_df['NH4(mg/L)'] * 71.4       # [mmol/m3]
    # phyto_clim_df[rname] = riv_avgs_df['Diatoms'] + riv_avgs_df['Dinoflag'] # [mmol/m3]
    # chlo_clim_df[rname] = riv_avgs_df['Chl']                    # [mg/L]
    TIC_clim_df[rname]  = riv_avgs_df['DIC(mmol/m3)']           # [mmol/m3]
    Talk_clim_df[rname] = riv_avgs_df['Alk(mmol/m3)']           # [meq/m3]
    DO_clim_df[rname]   = riv_avgs_df['DO(mg/L)'] * 31.26       # [mmol/m3]

    # Sort in descending order (so it's easier to visualize when graphing)
    flow_clim_df = flow_clim_df.sort_values(by = 1, axis = 1, ascending = False)
    # salt_clim_df = salt_clim_df.sort_values(by = 1, axis = 1, ascending = False)
    temp_clim_df = temp_clim_df.sort_values(by = 1, axis = 1, ascending = False)
    NO3_clim_df = NO3_clim_df.sort_values(by = 1, axis = 1, ascending = False)
    NH4_clim_df = NH4_clim_df.sort_values(by = 1, axis = 1, ascending = False)
    TIC_clim_df = TIC_clim_df.sort_values(by = 1, axis = 1, ascending = False)
    Talk_clim_df = Talk_clim_df.sort_values(by = 1, axis = 1, ascending = False)
    DO_clim_df = DO_clim_df.sort_values(by = 1, axis = 1, ascending = False)

# print('\n--------------------------------FLOW--------------------------------')
# print(flow_clim_df[10:15])
# print('\n--------------------------------SALT--------------------------------')
# print(salt_clim_df[10:15])
# print('\n--------------------------------TEMP--------------------------------')
# print(temp_clim_df[10:15])
# print('\n--------------------------------NO3--------------------------------')
# print(NO3_clim_df[10:15])
# print('\n--------------------------------NH4--------------------------------')
# print(NH4_clim_df[10:15])
# # print('\n--------------------------------PHYTO--------------------------------')
# # print(phyto_clim_df[10:15])
# # print('\n--------------------------------CHLO--------------------------------')
# # print(chlo_clim_df[10:15])
# print('\n--------------------------------TIC--------------------------------')
# print(TIC_clim_df[10:15])
# print('\n--------------------------------TALK--------------------------------')
# print(Talk_clim_df[10:15])
# print('\n--------------------------------DO--------------------------------')
# print(DO_clim_df[10:15])


# check for missing values:
if pd.isnull(flow_clim_df).sum().sum() != 0:
    print('Warning, there are missing flow values!')
# if pd.isnull(salt_clim_df).sum().sum() != 0:
#     print('Warning, there are missing salinity values!')
if pd.isnull(temp_clim_df).sum().sum() != 0:
    print('Warning, there are missing temperature values!')
if pd.isnull(NO3_clim_df).sum().sum() != 0:
    print('Warning, there are missing nitrate values!')
if pd.isnull(NH4_clim_df).sum().sum() != 0:
    print('Warning, there are missing ammonium values!')
if pd.isnull(TIC_clim_df).sum().sum() != 0:
    print('Warning, there are missing TIC values!')
if pd.isnull(Talk_clim_df).sum().sum() != 0:
    print('Warning, there are missing alkalinity values!')
if pd.isnull(DO_clim_df).sum().sum() != 0:
    print('Warning, there are missing oxygen values!')

# save results
clim_dir = Ldir['LOo'] / 'pre' / 'traps' / gridname / 'tiny_rivers' /'Data_historical'
flow_clim_df.to_pickle(clim_dir / ('CLIM_flow_' + str(year0) + '_' + str(year1) + '.p'))
# salt_clim_df.to_pickle(clim_dir / ('CLIM_salt_' + str(year0) + '_' + str(year1) + '.p'))
temp_clim_df.to_pickle(clim_dir / ('CLIM_temp_' + str(year0) + '_' + str(year1) + '.p'))
NO3_clim_df.to_pickle(clim_dir / ('CLIM_NO3_' + str(year0) + '_' + str(year1) + '.p'))
NH4_clim_df.to_pickle(clim_dir / ('CLIM_NH4_' + str(year0) + '_' + str(year1) + '.p'))
TIC_clim_df.to_pickle(clim_dir / ('CLIM_TIC_' + str(year0) + '_' + str(year1) + '.p'))
Talk_clim_df.to_pickle(clim_dir / ('CLIM_Talk_' + str(year0) + '_' + str(year1) + '.p'))
DO_clim_df.to_pickle(clim_dir / ('CLIM_DO_' + str(year0) + '_' + str(year1) + '.p'))

# Plotting
plt.close('all')

fig = plt.figure(figsize=(18,10))
rn_split = np.array_split(flow_clim_df.columns, 24)
for ii in range(1,25):
    ax = fig.add_subplot(6,4,ii)
    flow_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 21:
        ax.set_xlabel('Yearday')
    if ii in [1, 5, 9, 13, 17, 21]:
        ax.set_ylabel(r'Flow [$m^{3}s^{-1}$]', fontsize = 10)
plt.tight_layout()
fig.savefig(clim_dir / ('CLIM_flow_plot.png'))

# fig = plt.figure(figsize=(18,10))
# rn_split = np.array_split(salt_clim_df.columns, 24)
# for ii in range(1,25):
#     ax = fig.add_subplot(6,4,ii)
#     salt_clim_df[rn_split[ii-1]].plot(ax=ax)
#     ax.set_xlim(0,366)
#     ax.set_ylim(0, 25)
#     plt.legend(fontsize=6, ncol=3, loc='best')
#     ax.tick_params(axis='both', labelsize=8)
#     if ii >= 21:
#         ax.set_xlabel('Yearday')
#     if ii in [1, 5, 9, 13, 17, 21]:
#         ax.set_ylabel(r'Salinity [$g kg^{-1}$]', fontsize = 10)
# fig.savefig(clim_dir / ('CLIM_salt_plot.png'))

fig = plt.figure(figsize=(18,10))
rn_split = np.array_split(temp_clim_df.columns, 24)
for ii in range(1,25):
    ax = fig.add_subplot(6,4,ii)
    temp_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 21:
        ax.set_xlabel('Yearday')
    if ii in [1, 5, 9, 13, 17, 21]:
        ax.set_ylabel(r'Temp [$^{\circ}C$]', fontsize = 10)
fig.savefig(clim_dir / ('CLIM_temp_plot.png'))

fig = plt.figure(figsize=(18,10))
rn_split = np.array_split(NO3_clim_df.columns, 24)
for ii in range(1,25):
    ax = fig.add_subplot(6,4,ii)
    NO3_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 21:
        ax.set_xlabel('Yearday')
    if ii in [1, 5, 9, 13, 17, 21]:
        ax.set_ylabel(r'NO3 [$mmol m^3$]', fontsize = 10)
fig.savefig(clim_dir / ('CLIM_NO3_plot.png'))

fig = plt.figure(figsize=(18,10))
rn_split = np.array_split(NH4_clim_df.columns, 24)
for ii in range(1,25):
    ax = fig.add_subplot(6,4,ii)
    NH4_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 21:
        ax.set_xlabel('Yearday')
    if ii in [1, 5, 9, 13, 17, 21]:
        ax.set_ylabel(r'NH4 [$mmol m^3$]', fontsize = 10)
fig.savefig(clim_dir / ('CLIM_NH4_plot.png'))

fig = plt.figure(figsize=(18,10))
rn_split = np.array_split(TIC_clim_df.columns, 24)
for ii in range(1,25):
    ax = fig.add_subplot(6,4,ii)
    TIC_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 21:
        ax.set_xlabel('Yearday')
    if ii in [1, 5, 9, 13, 17, 21]:
        ax.set_ylabel(r'TIC [$mmol m^3$]', fontsize = 10)
fig.savefig(clim_dir / ('CLIM_TIC_plot.png'))

fig = plt.figure(figsize=(18,10))
rn_split = np.array_split(Talk_clim_df.columns, 24)
for ii in range(1,25):
    ax = fig.add_subplot(6,4,ii)
    Talk_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 21:
        ax.set_xlabel('Yearday')
    if ii in [1, 5, 9, 13, 17, 21]:
        ax.set_ylabel(r'Talk [$mEq m^3$]', fontsize = 10)
fig.savefig(clim_dir / ('CLIM_Talk_plot.png'))

fig = plt.figure(figsize=(18,10))
rn_split = np.array_split(DO_clim_df.columns, 24)
for ii in range(1,25):
    ax = fig.add_subplot(6,4,ii)
    DO_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 21:
        ax.set_xlabel('Yearday')
    if ii in [1, 5, 9, 13, 17, 21]:
        ax.set_ylabel(r'DO [$mmol m^3$]')
fig.savefig(clim_dir / ('CLIM_DO_plot.png'))
    
plt.show()