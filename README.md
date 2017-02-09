# baseball_forecaster
Forecasts baseball player stats to predict future performance


##Description
The forecasting is performed by using all the season stats for players within the specified range. Then it will take the previous season's player stats and forecast them to the forecast year. The model used is a Support Vector Regression, and each forecasted category has specific parameter values to get the best fit.

##Results
Results are put into the results.csv and the forecast database's 'batting' table in the results folder

Current Results with standard forecaster (predicting 2015, using train data from 1955 - 2014)

Category(test score, train score): h(0.33, 0.44), hr(0.43, 0.51), r(0.33, 0.47), rbi(0.40, 0.49), sb(0.53, 0.58)

The standard run takes about an hour to complete

##Limitations
Currently it only forecasts counting stats for batting (g, pa, ab, h, double, triple, hr, r, rbi sb, cs, bb, so, ibb, hbp, sh, sf, g_idp)

There are difficulties predicting outliers, since the model does not want to overfit to incorporate them

Does not account for players career stats, only accounts for their previous season's stats


##Requirements
###Data

The data can be obtained at https://www.kaggle.com/seanlahman/the-history-of-baseball

The data is from [Sean Lahman's Baseball Database](http://www.seanlahman.com/baseball-archive/statistics/) and is licensed under
[CC BY-SA 3.0 License](http://creativecommons.org/licenses/by-sa/3.0/)

Only the database.sqlite is necessary

###Python
Python 3.4+, sklearn 0.18+, numpy, pandas, matplotlib

##Configuration
Configuration is in the settings.cfg

The SVR parameters can be modified in forecaster/batting_model_setting.cfg (there are existing default values)

###Required
database_directory: (Enter the path to where the database is located)

database_name: (Enter the database name including .sqlite, only necessary if it was changed from database.sqlite)

###Other Settings
forecasted_batting_categories: (Stats to be predicted, the full list of catagories can be seen in the settings file)

forecaster: (standard will run all the stats using previously tuned C, epsilon and gamma values. complete will tune the parameters during the next run, which will cause the run to take much longer)

forecast_year: (The year that you want forecasted, it cannot be beyond 2016)

furthest_back_year: (The furthest year back you want player data from, it cannot be before 1955)

minimum_plate_appearances: (The minimum plate appearances a player must have to be added to the model)
