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
import datetime


# helper function 
def monthly2daily(df):
    '''
    turn a monthly dataframe into daily data
    (Note: this works but is very sketchy code!!!!!!!!!!!!!!!!!!!!!!!!!!!!)
    '''
    # duplicate last row
    double_lr_df = pd.concat([df, df.iloc[-1:]], ignore_index=True)
    # picking arbitrary year to fill with daily data (but includes a leap year)
    start_date = datetime.date(2020, 1, 1)
    end_date = datetime.date(2021, 1, 1)
    dates = pd.date_range(start_date, end_date, freq='MS')
    # Replace month column with things that look like dates
    double_lr_df['Month'] = dates
    double_lr_df = double_lr_df.set_index('Month')
    # Change monthly to daily
    double_lr_daily_df = double_lr_df.resample('D').ffill()
    # delete last row (1/1 on the next year)
    daily_df = double_lr_daily_df[:-1]
    # make index start from 1 and go to 366
    daily_i_df = daily_df.reset_index(inplace=True)
    return daily_df
    

# define year range to create climatologies
year0 = 1999
year1 = 2017

# define gridname
gridname = 'cas6'

# file with all traps names and ID numbers
traps_info_fn = Ldir['data'] / 'traps' / 'SSM_source_info.xlsx'
# location of historical data to process
wwtp_dir = Ldir['data'] / 'traps' / 'point_sources'
all_his_fns = os.listdir(wwtp_dir)

# Get all wwtp names and wwtp IDs
traps_info_df = pd.read_excel(traps_info_fn,usecols='D,E,F')
# Only interested in wwtps
wwtp_all_df = traps_info_df.loc[traps_info_df['Inflow_Typ'] == 'Point Source']
#get river names
wwtp_names_df = wwtp_all_df['Name'].str.replace(' - 1', '')
# get river names and river ids
wwtpnames = wwtp_names_df.values
wwtpids = wwtp_all_df['ID'].values

# # just test Brightwater for now -------------------------------------------------
# wwtpnames = wwtpnames[46:47]
# wwtpids = wwtpids[46:47]

# # just test Birch Bay for now -------------------------------------------------
# wwtpnames = wwtpnames[26:27]
# wwtpids = wwtpids[26:27]

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
for i,wname in enumerate(wwtpnames):

    print('{}: {}'.format(i,wname))

    # get river index
    wID = wwtpids[i]
    
    wwtp_fn = ''

    # find Ecology's timeseries based on wwtp id
    for fn in all_his_fns:
        root, ext = os.path.splitext(fn)
        if root.startswith(str(wID)) and ext == '.xlsx':
            wwtp_fn = fn
    
    # Let user know if couldn't find timeseries for a given point source
    if wwtp_fn == '0':
        print('No history file found for {}'.format(wname))
    # Otherwise, read history file as df
    else:
        wwtp_fp = str(wwtp_dir)  + '/' + wwtp_fn
        wwtp_df = pd.read_excel(wwtp_fp, skiprows=[0])

    # rename columns so that they are standardized
    # I have previously verified that Ecology's .xlsx files all have the same parameters
    wwtp_df = wwtp_df.set_axis(['Date', 'Year', 'Month', 'Day',
                            'Hour', 'Minute', 'Bin1', 'Flow(m3/s)',
                            'Temp(C)','Salt(ppt)','NH4(mg/L)',
                            'NO3+NO2(mg/L)', 'PO4(mg/L)', 'DO(mg/L)',
                            'pH', 'DON(mg/L)', 'PON(mg/L)', 'DOP(mg/L)',
                            'POP(mg/L)', 'POCS(mg/L)', 'POCF(mg/L)',
                            'POCR(mg/L)', 'DOCS(mg/L)', 'DOCF(mg/L)',
                            'Diatoms', 'Dinoflag', 'Chl', 'DIC(mmol/m3)',
                            'Alk(mmol/m3)'], axis=1, inplace=False)

    # replace all zeros with nans, so zeros don't bias data
    wwtp_df = wwtp_df.replace(0, np.nan)

    # calculate averages (compress 1999-2017 timeseries to single day, with an average for each day)
    wwtp_avgs_monthly_df = wwtp_df.groupby(['Month','Day']).mean().reset_index()

    # convert monthly data to daily
    wwtp_avgs_df = monthly2daily(wwtp_avgs_monthly_df)
    wwtp_avgs_df.index = wwtp_avgs_df.index + 1 # start day index from 1 instead of 0
    # print(wwtp_avgs_monthly_df)
    # print(wwtp_avgs_df)

    # Plot averages (this was written to test one wwtp at a time, so only pass one wwtp through for-loop)
    plotting = False
    vn = 'Flow(m3/s)'
    if plotting == True:
        fig, ax = plt.subplots(1,1, figsize=(11, 6))
        yrday = np.linspace(1,367,366)
        # Plot individual years
        for yr in range(1999,2017):
            wwtp_yr_monthly_df = wwtp_df.loc[wwtp_df['Year'] == yr]
            # convert monthly to daily
            wwtp_yr_df = monthly2daily(wwtp_yr_monthly_df)
            if yr == 2017:
                yrday_17 = np.linspace(1,214,213) # don't have full 2017 dataset
                plt.plot(yrday_17,wwtp_yr_df[vn],alpha=0.5, label=yr)
            else:
                plt.plot(yrday,wwtp_yr_df[vn],alpha=0.5, label=yr)
        # Plot average
        plt.plot(yrday,wwtp_avgs_df[vn].values, label='average', color='black', linewidth=2)
        plt.legend(loc='best', ncol = 4,fontsize=12)
        plt.ylabel(vn,fontsize=16)
        plt.xlabel('Julian Day',fontsize=16)
        ax.tick_params(axis='both', which='major', labelsize=14)
        plt.title(wname,fontsize=18)
        plt.show()

    # Add data to climatology dataframes, and convert to units that LiveOcean expects
    flow_clim_df[wname] = wwtp_avgs_df['Flow(m3/s)']             # [m3/s]
    # salt_clim_df[rname] = riv_avgs_df['Salt(ppt)']              # [PSS]
    temp_clim_df[wname] = wwtp_avgs_df['Temp(C)']                # [C]
    NO3_clim_df[wname]  = wwtp_avgs_df['NO3+NO2(mg/L)'] * 71.4   # [mmol/m3]
    NH4_clim_df[wname]  = wwtp_avgs_df['NH4(mg/L)'] * 71.4       # [mmol/m3]
    # phyto_clim_df[rname] = riv_avgs_df['Diatoms'] + riv_avgs_df['Dinoflag'] # [mmol/m3]
    # chlo_clim_df[rname] = riv_avgs_df['Chl']                    # [mg/L]
    TIC_clim_df[wname]  = wwtp_avgs_df['DIC(mmol/m3)']           # [mmol/m3]
    Talk_clim_df[wname] = wwtp_avgs_df['Alk(mmol/m3)']           # [meq/m3]
    DO_clim_df[wname]   = wwtp_avgs_df['DO(mg/L)'] * 31.26       # [mmol/m3]

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
# print(flow_clim_df[27:32])
# # print('\n--------------------------------SALT--------------------------------')
# # print(salt_clim_df[27:32])
# print('\n--------------------------------TEMP--------------------------------')
# print(temp_clim_df[27:32])
# print('\n--------------------------------NO3--------------------------------')
# print(NO3_clim_df[27:32])
# print('\n--------------------------------NH4--------------------------------')
# print(NH4_clim_df[27:32])
# # print('\n--------------------------------PHYTO--------------------------------')
# # print(phyto_clim_df[27:32])
# # print('\n--------------------------------CHLO--------------------------------')
# # print(chlo_clim_df[27:32])
# print('\n--------------------------------TIC--------------------------------')
# print(TIC_clim_df[27:32])
# print('\n--------------------------------TALK--------------------------------')
# print(Talk_clim_df[27:32])
# print('\n--------------------------------DO--------------------------------')
# print(DO_clim_df[27:32])


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
clim_dir = Ldir['LOo'] / 'pre' / 'traps' / gridname / 'point_sources' /'Data_historical'
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

fig = plt.figure(figsize=(16,8))
rn_split = np.array_split(flow_clim_df.columns, 12)
for ii in range(1,13):
    ax = fig.add_subplot(4,3,ii)
    flow_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 7:
        ax.set_xlabel('Yearday')
    if ii in [1, 4,7,10]:
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

fig = plt.figure(figsize=(16,8))
rn_split = np.array_split(temp_clim_df.columns, 12)
for ii in range(1,13):
    ax = fig.add_subplot(4,3,ii)
    temp_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 7:
        ax.set_xlabel('Yearday')
    if ii in [1, 4,7,10]:
        ax.set_ylabel(r'Temp [$^{\circ}C$]', fontsize = 10)
fig.savefig(clim_dir / ('CLIM_temp_plot.png'))

fig = plt.figure(figsize=(16,8))
rn_split = np.array_split(NO3_clim_df.columns, 12)
for ii in range(1,13):
    ax = fig.add_subplot(4,3,ii)
    NO3_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 7:
        ax.set_xlabel('Yearday')
    if ii in [1, 4,7,10]:
        ax.set_ylabel(r'NO3 [$mmol m^3$]', fontsize = 10)
fig.savefig(clim_dir / ('CLIM_NO3_plot.png'))

fig = plt.figure(figsize=(16,8))
rn_split = np.array_split(NH4_clim_df.columns, 12)
for ii in range(1,13):
    ax = fig.add_subplot(4,3,ii)
    NH4_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 7:
        ax.set_xlabel('Yearday')
    if ii in [1, 4,7,10]:
        ax.set_ylabel(r'NH4 [$mmol m^3$]', fontsize = 10)
fig.savefig(clim_dir / ('CLIM_NH4_plot.png'))

fig = plt.figure(figsize=(16,8))
rn_split = np.array_split(TIC_clim_df.columns, 12)
for ii in range(1,13):
    ax = fig.add_subplot(4,3,ii)
    TIC_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 7:
        ax.set_xlabel('Yearday')
    if ii in [1, 4,7,10]:
        ax.set_ylabel(r'TIC [$mmol m^3$]', fontsize = 10)
fig.savefig(clim_dir / ('CLIM_TIC_plot.png'))

fig = plt.figure(figsize=(16,8))
rn_split = np.array_split(Talk_clim_df.columns, 12)
for ii in range(1,13):
    ax = fig.add_subplot(4,3,ii)
    Talk_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 7:
        ax.set_xlabel('Yearday')
    if ii in [1, 4,7,10]:
        ax.set_ylabel(r'Talk [$mEq m^3$]', fontsize = 10)
fig.savefig(clim_dir / ('CLIM_Talk_plot.png'))

fig = plt.figure(figsize=(16,8))
rn_split = np.array_split(DO_clim_df.columns, 12)
for ii in range(1,13):
    ax = fig.add_subplot(4,3,ii)
    DO_clim_df[rn_split[ii-1]].plot(ax=ax)
    ax.set_xlim(0,366)
    ax.set_ylim(bottom=0)
    plt.legend(fontsize=6, ncol=3, loc='best')
    ax.tick_params(axis='both', labelsize=8)
    if ii >= 7:
        ax.set_xlabel('Yearday')
    if ii in [1, 4,7,10]:
        ax.set_ylabel(r'DO [$mmol m^3$]')
fig.savefig(clim_dir / ('CLIM_DO_plot.png'))
    
plt.show()