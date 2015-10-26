from rpy2 import robjects
from rpy2.robjects.packages import importr
import numpy as np
import pandas as pd


forecast = importr('forecast')
frequency = robjects.r('frequency')
NULL = robjects.NULL


def ts(data, start=1, frequency=1):
  '''
  Turns the provided data into an R time series. 
  
  Args:
    data - Python sequence representing values of a regular time series.
    start - default 1; a number or 2-tuple to use as start index of sequence.
      If 2-tuple, it is (period, step), e.g. March 2010 is (2010, 3).
    frequency - default 1; number of points in each time period.
        e.g. 12 for monthly data with an annual period

  Returns:
    an object that maps to an R time series (class 'ts')
  '''
  ts = robjects.r('ts')
  rdata = robjects.FloatVector(data)
  if type(start) == tuple:
    start = robjects.r.c(*start)
  time_series = ts(rdata, start=start, frequency=frequency)  
  return time_series


def extract_forecast(fc, horizon, mean_only, as_pandas):
  '''
  Utility function to extract the desired elements from a completed forecast 
  and return them as either Python or Pandas objects.
  
  Args:
    fc - an object with class forecast from R Forecast
    horizon - number of steps ahead in the forecast
    mean_only - if True, return only the mean prediction.
    as_pandas  - if True, return a Pandas DataFrame or Series
    
  Returns:
    A forecast with or without prediction intervals, 
    as either a list/tuple or as a Pandas DataFrame/Series.
  '''
  if mean_only:
    result = list(fc.rx2('mean'))
    if as_pandas:
      return pd.Series(result)
    else: 
      return result
  else:
    lower_95 = list(fc.rx2('lower')[horizon:])
    lower_80 = list(fc.rx2('lower')[:horizon])
    mean_fc  = list(fc.rx2('mean'))
    upper_80 = list(fc.rx2('upper')[:horizon])
    upper_95 = list(fc.rx2('upper')[horizon:])
    results = (lower_95, lower_80, mean_fc, upper_80, upper_95)
    if as_pandas:
      cols = ['lower95','lower80','point_forecast','upper80','upper95']
      df = pd.DataFrame(dict(zip(cols, results)))
      return df[cols]
    else:
      return results
  
  
def meanf(x, h=10, lam=NULL):
  '''
  Perform a mean forecast on the provided data by calling meanf() 
  from R Forecast.
  
  Args:
    x - an R time series, obtained from forecast_wrapper.ts()
    h - default 10; the forecast horizon.
    lam - BoxCox transformation parameter. The default is R's NULL value.
      If NULL, no transformation is applied. Otherwise, a Box-Cox 
      transformation is applied before forecasting and inverted after.

  Returns:
    an object that maps to an R object of class 'forecast'
  '''
  return forecast.meanf(x, h, **{'lambda' : lam})
  
  
def thetaf(x, h=10):
  '''
  Perform a theta forecast on the provided data by calling thetaf() 
  from R Forecast. The theta forecast is equivalent to a random walk 
  forecast (rwf in R Forecast) with drift, with the drift equal to half 
  the slope of a linear regression model fitted to with a trend. The 
  theta forecast did well in the M3 competition.
  
  Args:
    x - an R time series, obtained from forecast_wrapper.ts()
    h - default 10; the forecast horizon.

  Returns:
    an object that maps to an R object of class 'forecast'
  '''
  return forecast.thetaf(x, h)


def naive(x, h=10, lam=NULL):
  '''
  Perform a naive forecast on the provided data by calling naive() 
  from R Forecast. This is also called the 'Last Observed Value' 
  forecast. The point forecast is a constant at the last observed value.
  
  Args:
    x - an R time series, obtained from forecast_wrapper.ts()
    h - default 10; the forecast horizon.
    lam - BoxCox transformation parameter. The default is R's NULL value.
      If NULL, no transformation is applied. Otherwise, a Box-Cox 
      transformation is applied before forecasting and inverted after.

  Returns:
    an object that maps to an R object of class 'forecast'
  '''
  return forecast.naive(x, h, **{'lambda' : lam})


def snaive(x, h=None, lam=NULL):
  '''
  Perform a seasonal naive forecast on the provided data by calling 
  snaive() from R Forecast. This is also called the 'Last Observed 
  Seasonal Value' forecast. The point forecast is the value of the 
  series one full period in the past.
  
  Args:
    x - an R time series, obtained from forecast_wrapper.ts()
      For this forecast method, x should be periodic.
    h - Forecast horizon; default is 2 full periods of a periodic series
    lam - BoxCox transformation parameter. The default is R's NULL value.
      If NULL, no transformation is applied. Otherwise, a Box-Cox 
      transformation is applied before forecasting and inverted after.

  Returns:
    an object that maps to an R object of class 'forecast'
  '''
  if h is None:
    h = 2 * frequency(x)[0]
  return forecast.snaive(x, h, **{'lambda' : lam})


def rwf(x, h=10, drift=False, lam=NULL):
  '''
  Perform a random walk forecast on the provided data by calling 
  rwf() from R Forecast. The forecast can have drift, which allows 
  a trend in the mean prediction, but by default, it does not.
  
  Args:
    x - an R time series, obtained from forecast_wrapper.ts()
    h - default 10; the forecast horizon.
    drift - default False. If True, a random walk with drift model is fitted.
    lam - BoxCox transformation parameter. The default is R's NULL value.
      If NULL, no transformation is applied. Otherwise, a Box-Cox 
      transformation is applied before forecasting and inverted after.

  Returns:
    an object that maps to an R object of class 'forecast'
  '''
  return forecast.rwf(x, h, drift, **{'lambda' : lam})













