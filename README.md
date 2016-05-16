# baseball_forecaster
Forecasts baseball player stats to predict future performance

##Forecasting Methods
###Curve Fitting
Picks a specific player in the previous year to the one forecasted

For each stat it find similar performing players (at each age) and groups them

Plots the mean of those players stat results as they age (Example: x value = age and y value = hr)

Creates a polynomial fit of the plot and then forecasted the next year's stat from that fit

This process happens for all the players in the previous year (that meet minimum_plate_appearances)

####Limitations
Only does hitter counting stats currently (ab, r, h, double, triple, hr, rbi, sb, bb)

Has problems with players that have only played a few seasons (not enough data to fit a good curve)

Cannot effectively use all of the baseball data since stat values can vary from era to era

There are currently performance issues due to all of the inner loops

##Requirements
###Data

The data can be obtained at https://www.kaggle.com/kaggle/the-history-of-baseball

The data is from [Sean Lahman's Baseball Database](http://www.seanlahman.com/baseball-archive/statistics/) and is licensed under
[CC BY-SA 3.0 License](http://creativecommons.org/licenses/by-sa/3.0/)

Only the database.sqlite is necessary

###Python
Python 3.4, numpy

##Configuration
###Required
database_directory: (Enter the path to where the database is located)

database_name: (Enter the database name, including .sqlite)

###Other Settings
forecast_year: (Enter the year that you want forecasted, it cannot be beyond 2016)

furthest_back_year: (Enter the furthest year back you want compared players stats to be from)

minimum_plate_appearances: (Enter the minimum plate appearances a player must have in that year to be eligible for comparison)

number_of_closest_players: (Enter how many players you want to be used in plotting for the stat trend)

polynomial_order: (Enter the order of the polynomial you want to use for the fit)
