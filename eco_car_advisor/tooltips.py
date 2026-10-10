"""Field help text for vehicle and analysis forms."""


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
