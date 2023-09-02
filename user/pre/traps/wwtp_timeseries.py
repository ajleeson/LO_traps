"""
Plot timeseries for all WWTPs
So I can identify open and close dates for each of them

To create individual climatology figures, run from ipython with:
run wwtp_flow_timeseries.py
"""

#################################################################################
#                              Import packages                                  #
#################################################################################

from lo_tools import Lfun
Ldir = Lfun.Lstart()

import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import argparse
    

#################################################################################
#                     Get data and set up dataframes                            #
#################################################################################

# read arguments
parser = argparse.ArgumentParser()
# add ctag
parser.add_argument('-ctag', type=str, default='lo_base')
args = parser.parse_args()
ctag = args.ctag

# location to save file
clim_dir = Ldir['LOo'] / 'pre' / 'traps' / 'point_sources' / ctag / 'Data_historical'
Lfun.make_dir(clim_dir)

# get flow and loading data
wwtp_fn = Ldir['data'] / 'traps' / 'all_point_source_data.nc'
ecology_data_ds = xr.open_dataset(wwtp_fn)

# get wwtp names and wwtp ids
wwtpnames = ecology_data_ds['name'].values


#################################################################################
#              Plot all individual point source climatologies                   #
#################################################################################

print('Plotting...')

# generate directory to save files
fig_dir = clim_dir / 'wwtp_timeseries'
Lfun.make_dir(fig_dir)

for i,wname in enumerate(wwtpnames):

    print('{}/{}: {}'.format(i+1,len(wwtpnames),wname))
    dates = ecology_data_ds.date.values
    flows = ecology_data_ds.flow[ecology_data_ds.name == wname].values[0]
    ammonium = ecology_data_ds.NH4[ecology_data_ds.name == wname].values[0]
    nitrate = ecology_data_ds.NO3[ecology_data_ds.name == wname].values[0]

    # Plot timeseries for each source
    fig,ax = plt.subplots(3,1,figsize=(10,7),sharex=True)
    ax[0].plot(dates,flows,color='deeppink')
    ax[1].plot(dates,ammonium,color='olivedrab')
    ax[2].plot(dates,nitrate,color='saddlebrown')
    # scale
    ax[0].set_ylim([0,1.3*max(flows)])
    ax[1].set_ylim([0,1.3*max(ammonium)])
    ax[2].set_ylim([0,1.3*max(nitrate)])
    # labels
    ax[0].set_ylabel('Flow [m3/s]')
    ax[1].set_ylabel('NO4 [mmol/m3]')
    ax[2].set_ylabel('NO3 [mmol/m3]')
    # add grid
    ax[0].grid('True') 
    ax[1].grid('True')
    ax[2].grid('True')
    # format figure
    ax[2].xaxis.set_major_locator(mdates.YearLocator(base=1))
    ax[2].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    plt.xticks(rotation=45)
    ax[2].set_xlim([ecology_data_ds.date.values[0],ecology_data_ds.date.values[-1]])

    # plot title is name of source
    plt.suptitle(wname,fontsize=18)

    # Save figure
    figname = wname + '.png'
    save_path = fig_dir / figname
    fig.savefig(save_path)
    plt.close('all')

print('Done')
