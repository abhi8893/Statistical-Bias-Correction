'''
Recipes using xarray for easier analyses
@author: Abhishek Bhatia
'''

import xarray as xr
import pandas as pd
import numpy as np


def homo_dims(xr_ds):
    pass

'''timmean ,timmin, timmax, timstd'''
#TODO: Implement seltime
def timmean(xr_ds):
    return xr_ds.mean('time')

def timmin(xr_ds):
    return xr_ds.min('time')

def timmax(xr_ds):
    return xr_ds.max('time')

def timstd(xr_ds):
    return xr_ds.std('time')

'''selmon'''
'''ymonmean, ymonmin, ymonmax, ymonstd'''
def selmon(xr_ds, months):
    return xr_ds.sel(time=np.isin(xr_ds['time.month'], months))

def ymonmean(xr_ds):
    return xr_ds.groupby('time.month').mean('time')

def ymonmin(xr_ds):
    return xr_ds.grouby('time.month').min('time')

def ymonmax(xr_ds):
    return xr_ds.groupby('time.month').max('time')

def ymonstd(xr_ds):
    return xr_ds.groupby('time.month').std('time')

'''monmean, monmin, monmax, monstd'''
#TODO: Implement specific month index selector?
def monmean(xr_ds):
    return xr_ds.resample(time='M').mean('time')

def monmin(xr_ds):
    return xr_ds.resample(time='M').min('time')

def monmax(xr_ds):
    return xr_ds.resample(time='M').max('time')

def monstd(xr_ds):
    return xr_ds.resample(time='M').std('time')


'''selyear'''
'''yearmean, yearmin, yearmax, yearstd'''
def selyear(xr_ds, years):
    return xr_ds.sel(time=np.isin(xr_ds['time.year'], years))

def yearmean(xr_ds):
    return xr_ds.groupby('time.year').mean('time')

def yearmin(xr_ds):
    return xr_ds.groupby('time.year').min('time')

def yearmax(xr_ds):
    return xr_ds.groupby('time.year').max('time')

def yearstd(xr_ds):
    return xr_ds.groupby('time.year').std('time')

'''groupbyyday'''
'''ydaymean, ydaymin, ydaymax, ydaystd'''
#TODO: Implement selyday.
def groupbyyday(xr_ds):
    try:
        cft = xr_ds['time'].copy()
        ti = pd.Series(xr_ds.indexes['time'])
        cft.values = ti.apply(lambda x: x.dayofyr)
        return xr_ds.groupby(cft)
    except AttributeError:
        return xr_ds.groupby('time.dayofyear')

def ydaymean(xr_ds):
    return groupbyyday(xr_ds).mean('time')

def ydaymin(xr_ds):
    return groupbyyday(xr_ds).min('time')

def ydaymax(xr_ds):
    return groupbyyday(xr_ds).max('time')

def ydaystd(xr_ds):
    return groupbyyday(xr_ds).std('time')

'''daymean, daymin, daymax, daystd'''
#TODO: Implement specific day index selector?
def daymean(xr_ds):
    return xr_ds.resample('D').mean()

def daymin(xr_ds):
    return xr_ds.resample('D').min()

def daymax(xr_ds):
    return xr_ds.resample('D').max()

def daystd(xr_ds):
    return xr_ds.resample('D').std()

'''selseas'''
'''getseas''' ## Should not be available to user?
'''groupbyseas'''
'''yseasmean, yseasmin, yseasmax, yseasstd'''
def selseas(xr_ds, seas):
    if seas is 'DJF':
        return selmon(xr_ds, [12, 1, 2])
    elif seas is 'MAM':
        return selmon(xr_ds, [3, 4, 5])
    elif seas is 'JJAS':
        return selmon(xr_ds, [6, 7, 8, 9])
    elif seas is 'ON':
        return selmon(xr_ds, [10, 11])


def getseas(month):
    if month in [12, 1, 2]:
        return 'DJF'
    elif month in [3, 4, 5]:
        return 'MAM'
    elif month in [6, 7, 8, 9]:
        return 'JJAS'
    elif month in [10, 11]:
        return 'ON'

def groupbyseas(xr_ds):
    seasgrpr = xr.DataArray(pd.Series(xr_ds['time.month'].values)
                            .apply(getseas), dims={'time':xr_ds['time']},
                            name='seas')

    return xr_ds.groupby(seasgrpr)

def yseasmean(xr_ds):
    return groupbyseas(xr_ds).mean('time')

def yseasmin(xr_ds):
    return groupbyseas(xr_ds).min('time')

def yseasmax(xr_ds):
    return groupbyseas(xr_ds).max('time')

def yseasstd(xr_ds):
    return groupbyseas(xr_ds).std('time')

'''sellonlatbox''' # TODO: Also implement sellon, sellat
'''fldmean''' # TODO: Also implement zonmean, mermean
# TODO: Also implement min, max, std?
def sellonlatbox(xr_ds, llbox):
    lon1, lon2, lat1, lat2 = llbox
    lon, lat = xr_ds.lon, xr_ds.lat
    return xr_ds.sel(lon=(lon>=lon1)&(lon<=lon2),
                     lat=(lat>=lat1)&(lat<=lat2))

def fldmean(xr_ds, llbox=None):
    if llbox is not None:
        return sellonlatbox(xr_ds, llbox).mean(['lat', 'lon'])
    else:
        return xr_ds.mean(['lat', 'lon'])

def anomaly(xr_ds, kind):

    if kind is 'daily':
        return daymean(xr_ds) - ydaymean(xr_ds)

    elif kind is 'monthly':
        return monmean(xr_ds) - ymonmean(xr_ds)

    elif kind is 'seasonal':
        return seasmean(xr_ds) - yseasmean(xr_ds)

    elif kind is 'yearly':
        return yearmean(xr_ds) - ydaymean(xr_ds)


'''Resampling functions for CFTimeIndex'''

def resample_ms_freq(ds, dim='time'):
    """Resample the dataset to 'MS' frequency regardless of the
    calendar used.

    Parameters
    ----------
    ds : Dataset
        Dataset to be resampled
    dim : str
        Dimension name associated with the time index

    Returns
    -------
    Dataset
    """
    index = ds.indexes[dim]
    if isinstance(index, pd.DatetimeIndex):
        return ds.resample(**{dim: 'MS'}).mean(dim)
    elif isinstance(index, xr.CFTimeIndex):
        date_type = index.date_type
        month_start = [date_type(date.year, date.month, 1) for date in ds[dim].values]
        ms = xr.DataArray(month_start, coords=ds[dim].coords)
        ds = ds.assign_coords(MS=ms)
        return ds.groupby('MS').mean(dim).rename({'MS': dim})
    else:
        raise TypeError(
            'Resampling to month start frequency requires using a time index of either '
            'type pd.DatetimeIndex or xr.CFTimeIndex.')
