import pandas as pd
from numpy import linspace
import numpy as np
from scipy.interpolate import interp1d
import sys
import os
from scipy.optimize import curve_fit


def loadData():

    data = {
        'maintenance': {},
        'productionEoL': {},
        'usePhase': {},
        'batteries': {}
    }

    # read default production and EoL data
    data['productionEoL'] = {

        'co2/kg': pd.read_excel(resource_path('Data/ProductionEoL/productionEoLData.xlsx'), sheet_name='productionEoLCOkg', index_col=0),
        'defaultMass': pd.read_excel(resource_path('Data/ProductionEoL/productionEoLData.xlsx'), sheet_name='mass', index_col=0)

    }

    # Read batteries data
    data['batteries']['capacity'] = pd.read_excel(resource_path(
        'Data/Maintenance/maintenance.xlsx'), sheet_name='batteryCapacity', index_col=0)
    data['batteries']['kgco2/kWh'] = 130

    # read maintenance data
    data['maintenance'] = pd.read_excel(resource_path(
        'Data/Maintenance/maintenance.xlsx'), sheet_name='maintenance')
    data['maintenance'] = data['maintenance'].groupby('Mileage')['Delta Maintenance (tonCO2)'].max(
    ).reset_index().sort_values("Mileage").reset_index(drop=True)

    # initialize data for user input data
    data['usePhase'] = {
        'consumptionICE': pd.read_excel(resource_path('Data/Use/usePhaseData.xlsx'), sheet_name='consumptionICE', index_col=0),
        'consumptionBEV': pd.read_excel(resource_path('Data/Use/usePhaseData.xlsx'), sheet_name='consumptionBEV', index_col=0),
        'Gasoline': {
            'WTT': 572,
            'TTW': 2360
        },
        'Diesel': {
            'WTT': 697,
            'TTW': 2650,
        },
        'DrivingShare': {
            'Segment B': 0.44,
            'Segment C': 0.44,
            'SUV': 0.43
        },
        'EnergyMix': {
            'Europe': 0.21,
            'Sweden': 0.008,
            'Poland': 0.614,
            'Finland': 0.04,
            'France': 0.05,
            'Luxembourg': 0.056,
            'Latvia': 0.067,
            'Slovakia': 0.084,
            'Austria': 0.085,
            'Denmark': 0.094,
            'Portugal': 0.119,
            'Lithuania': 0.124,
            'Croatia': 0.134,
            'Belgium': 0.145,
            'Hungary': 0.154,
            'Spain': 0.158,
            'Slovenia': 0.176,
            'Italy': 0.225,
            'Romania': 0.234,
            'Greece': 0.258,
            'Ireland': 0.26,
            'Netherlands': 0.263,
            'Bulgaria': 0.281,
            'Germany': 0.329,
            'Malta': 0.342,
            'Czech Republic': 0.44,
            'Cyprus': 0.585,
            'Estonia': 0.69
        }
    }

    return data


def tooltips():
    tooltip_dict = {
        "carSegment": "Select the category/size class of the current vehicle (e.g., small, medium, SUV).",
        "engineType": "Choose the engine technology of the current vehicle (e.g., Diesel, BEV, Hybrid).",
        "mileage": "Enter the total distance the car has already traveled in kilometers.",
        "secondHandCar": "Check if the vehicle was purchased as second-hand and enter the mileage at the time of purchase.",
        "secondHandCarMileage": "Enter the second-hand car mileage at the time of purchase.",
        "secondHandCarAge": "Enter the second-hand car age at the time of purchase.",
        "massValue": "Mass of the vehicle in kilograms. Impacts production and EoL emissions.",
        "carProductionFootprint": "Emission factor (in kg CO₂ per kg) for producing the car, including end-of-life.",
        "meanConsumptionLiter": "Fuel consumption of the car in liters per 100 km (for ICEs and mild/full hybrids).",
        "meanConsumptionWh": "Electricity consumption of the car in kWh per 100 km (for BEVs and plug-in hybrids).",
        "drivingShare": "Percentage of kilometers driven electrically for plug-in hybrids (0 to 1).",
        "country": "Select the country to automatically load the average electricity mix.",
        "energyMix": "Average carbon intensity of the electricity used, in gCO₂/kWh. Editable if 'Custom' is selected.",
        "batteryCapacity": "Battery capacity in kilowatt-hours. Used to estimate battery-related emissions.",
        "batteryProductionFootprint": "Emission factor for producing the battery in kgCO₂ per kWh.",
        "batteryLifeTime": "Estimated lifetime of the battery before it needs to be replaced (in km).",
        "WTT": "Well-to-Tank emissions for producing and distributing the fuel (in gCO₂/liter).",
        "TTW": "Tank-to-Wheel emissions for burning the fuel during driving (in gCO₂/liter).",
        "keepEOL": "Check to define a shorter usage period for this car than its default lifespan.",
        "keepLifeSpan": "Mileage or age after which the car is sold or retired. Overrides standard lifetime if enabled.",
        "keepUnits": "Select whether the specified lifespan is in kilometers or years.",
        "km2yearsConvFactor": "Average mileage in kilometers covered every year.",
        "maintenance": "Select whether regular maintenance is included in the analysis. It affects the car performance degradation.",
        "ICElifeSpan": "Expected lifetime mileage for internal combustion engine (ICE) vehicles.",
        "BEVlifeSpan": "Expected lifetime mileage for battery electric vehicles (BEVs).",

    }

    return tooltip_dict


def years_to_kilometers(carDataDict, conversionFactor):
    '''Function that converts kilometers to years to accomodate the depreciation model wrt years of usage '''

    # conversionFactor = 12000  # 12000 km each year

    # convert keep life span form kilometers to years
    # if not carDataDict['keepEOL']:
    if 'km' in carDataDict['keepUnits']:
        carDataDict['keepLifeSpan'] = round(carDataDict['keepLifeSpan'], -3) / conversionFactor
    else:
        carDataDict['keepLifeSpan'] = round(carDataDict['keepLifeSpan'] * conversionFactor, -3) / conversionFactor

    # # convert second hand car mileage into year of use
    # if carDataDict['secondHandCar']:
    #     carDataDict['secondHandCarMileage'] = round(carDataDict['secondHandCarMileage'], -3) / conversionFactor

    return carDataDict


def depreciation_curve(carAge, annualMileage, engineType):
    '''
    Parameters
    ----------
    inputValue : float
        Age of the car.

    Returns
    -------
    outputValue : float
        Depreciated value as a fraction of the new value (1.0 = 100%).
    '''

    if engineType == 'BEV':
        outputValue = np.exp(-(0.1706 * carAge + 0.00357 * carAge * annualMileage / 1000))
    else:
        outputValue = np.exp(-(0.1025 * carAge + 0.00190 * carAge * annualMileage / 1000))

    return outputValue


# def depreciation_curve(inputValue):
#     '''
#     Parameters
#     ----------
#     inputValue : float
#         Age of the car.

#     Returns
#     -------
#     outputValue : float
#         Depreciated value as a fraction of the new value (1.0 = 100%).
#     '''

#     # Original depreciation data
#     x_values = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])
#     y_values = np.array([100, 85, 75, 65, 58, 52, 48, 45, 42, 40, 38, 36])

#     # Define exponential decay function with zero asymptote
#     def exp_decay(x, b):
#         return 100 * np.exp(-b * x)

#     # Fit the curve once
#     params, _ = curve_fit(exp_decay, x_values, y_values, p0=(0.1))

#     # Evaluate the exponential function at the given inputValue
#     outputValue = exp_decay(inputValue, *params) / 100  # Return as fraction

#     return outputValue


def compute_intersection(x1, y1, x2, y2):
    """
    Finds the x-value in the first dataset (x1, y1) where the two datasets (y1 and y2) have the same y-value.

    Parameters:
    x1, y1 : First series (x-values and corresponding y-values)
    x2, y2 : Second series (x-values and corresponding y-values)

    Returns:
    x_target : The x-value in the first series where y1 equals y2 (interpolated).
    """
    # Create interpolation functions for both series
    # interp_y1 = interp1d(x1, y1, kind='cubic', fill_value="extrapolate")
    # interp_y2 = interp1d(x2, y2, kind='cubic', fill_value="extrapolate")

    interp_y1 = interp1d(x1, y1, fill_value="extrapolate", kind='previous')
    interp_y2 = interp1d(x2, y2, fill_value="extrapolate", kind='previous')

    # Define a fine x-grid for searching
    x_common = linspace(max(min(x1), min(x2)), min(max(x1), max(x2)), 1000)

    # Compute interpolated y-values on the common x-grid
    y1_common = interp_y1(x_common)
    y2_common = interp_y2(x_common)

    # # Find the index where the y-values are closest
    # diff = abs(y1_common - y2_common)
    # if min(diff) < 0.2:
    #     min_index = argmin(diff)

    #     # Get the corresponding x-value
    #     x_target = x_common[min_index]
    #     y_target = y1_common[min_index]
    # else:
    #     x_target = None
    #     y_target = None

    # Find the index where the y-values are closest
    diff = y1_common - y2_common

    sign_changes = np.where(np.diff(np.sign(diff)))[0]

    if sign_changes.size > 0:
        # For simplicity, we assume one intersection; take the first change
        idx = sign_changes[0]
        # Approximate the intersection point as the midpoint of the two x values around the sign change
        x_target = round((x_common[idx] + x_common[idx + 1]) / 2)
        y_target = round((y1_common[idx] + y2_common[idx + 1]) / 2)

    else:
        x_target = None
        y_target = None

    return x_target, y_target


def interp_data(old_x, old_y, new_x, kind='cubic'):

    interp_func = interp1d(old_x, old_y, kind=kind, fill_value="extrapolate")
    new_y = interp_func(new_x)

    return new_y


def resource_path(relative_path):
    """ Get the correct path for bundled files inside the PyInstaller executable. """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


def add_maintenance(data, mileage, emissions, depreciation):
    maintenanceMileages = data['maintenance']["Mileage"].values
    maintenanceCo2 = data['maintenance']["Delta Maintenance (tonCO2)"].values

    # Find for each mileage in valid_plotXaxis the index of the most recent maintenance event.
    indices = np.searchsorted(maintenanceMileages, mileage, side='right') - 1

    # For mileages before any maintenance event, use 0.0.
    maintenance_to_add = np.where(indices >= 0, maintenanceCo2[indices], 0.0)

    if len(maintenance_to_add) > 0:
        scaledStartwithDepretiacion = maintenance_to_add[0] * depreciation
        maintenance_to_add[1:] -= maintenance_to_add[0] - scaledStartwithDepretiacion
        maintenance_to_add[0] = scaledStartwithDepretiacion

    # Add the corresponding maintenance value to the baseline emissions.
    emissions = emissions + maintenance_to_add
    return emissions


def add_degradation(valid_plotXaxis, growth_factor, conversionFactor):
    # Compute lambda for continuous exponential growth
    lambda_ = np.log(growth_factor) / conversionFactor

    # Compute the starting multiplier at the first mileage point
    x_start = valid_plotXaxis[0]
    start_multiplier = np.exp(lambda_ * x_start)

    # Compute the multiplier array
    multipliers = start_multiplier * np.exp(lambda_ * (valid_plotXaxis - x_start))

    return multipliers


def setLayoutVisible(layout, visible):
    for i in range(layout.count()):
        item = layout.itemAt(i)
        widget = item.widget()
        if widget:
            widget.setVisible(visible)
        layout.invalidate()
    parent_widget = layout.parentWidget()
    if parent_widget:
        parent_widget.adjustSize()
