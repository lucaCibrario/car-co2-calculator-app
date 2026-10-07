# ECO Car Replacement Advisor

## Table of Contents

- [Overview](#overview)
  - [Key Features](#key-features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Input Parameters](#input-parameters)
  - [Current Car Details](#current-car-details)
  - [New Car(s)](#new-cars)
  - [Analysis Settings](#analysis-settings)
- [Carbon Footprint Analysis](#carbon-footprint-analysis)
  - [Plot](#plot)
  - [Tables](#tables)
- [Menu](#menu)
  - [File](#file-menu)
  - [Help](#help-menu)
- [Notes](#notes)
- [Contact](#contact)
- [License](#license)


## Overview

ECO Car Replacement Advisor is a tool for assessing the environmental impact of replacing a car with a more sustainable model. It helps users compare carbon emissions from their current vehicle against potential new cars by modeling their entire life-cycles. The tool provides intuitive visualizations and tabular output to facilitate analysis and decision-making.

### Key Features

- Supports multiple new car comparisons  
- Allows analysis over custom time windows to compare different scenarios such as resale, leasing, or long-term ownership  
- Interactive CO₂ history plots  
- Detailed input for:  
  - Current and new vehicle specifications  
  - Fuel/electricity consumption  
  - Driving patterns and battery assumptions  
  - Regional electricity production  
- Optional advanced configuration and tooltips for every setting

## Installation

1. Download the latest `.exe` file.
2. Double-click the file to run the application.

## Quick Start
Follow these simple steps to get started:

- Fill in your current car details – including mileage, segment, fuel type, and energy mix.
- Define the new car(s) – add one or more vehicles to compare, specifying engine type, usage patterns, and optional advanced settings.
- Click "Compute Carbon Footprint" – the app will generate interactive plots and data tables showing CO₂ emission trends, break-even points, and more.

Need more information? Check the full documentation below for detailed guidance.



## Input Parameters

Below are the details required to evaluate whether to replace or keep your current car.
When the car segment and engine type are selected, default values from the database are used to fill the related fields.

### **Current Car Details**

These are the settings for defining the current car that may be replaced.

- **Car Segment**  
  Defines the size and type of the vehicle.  
  - **Segment B**: Small cars, typically hatchbacks (e.g., Ford Fiesta, VW Polo).  
  - **Segment C**: Compact cars, larger than Segment B (e.g., VW Golf, Honda Civic).  
  - **SUV (Sport Utility Vehicle)**: Larger vehicles with higher ground clearance (e.g., Toyota RAV4, BMW X5).  

- **Engine Type**  
  Specifies the fuel type and emission standard of the vehicle. Examples:  
  - **Gasoline (Euro 4, Euro 5, Euro 6)**  
  - **Diesel (Euro 4, Euro 5, Euro 6)**  
  - **Mild/Full Hybrid**: These vehicles combine an internal combustion engine (ICE) with an electric motor to improve fuel efficiency.  
  - **Plug-in Hybrid (PHEV)**: A hybrid vehicle with a larger battery that can be charged from an external power source.  
  - **BEV (Full-electric)**

- **Current Mileage (km) (Compulsory)**  
  The total number of kilometers the car has been driven from its production. It corresponds to the figure that can be read on the odometer.  
  Depending on the type of engine of the current car, the value of **Current Mileage (km)** must be lower than **ICE Car Life Span (km)** or **BEV Car Life Span (km)**, that are defined in the **Advanced Analysis Settings**.

- **Energy mix (gCO₂/kWh)**  
  The Energy Mix represents the average carbon intensity of electricity generation in a given country, measured in grams of CO₂ emitted per kilowatt-hour (gCO₂/kWh).
  - If a specific country is selected, the energy mix is automatically populated based on average national data.
  - If "Custom" is selected, the field becomes editable to enter a value to reflect a personalized or projected energy scenario (e.g., green electricity contracts, renewable-only sources).

  This value directly affects the use-phase emissions of electric and plug-in hybrid vehicles, as it determines the CO₂ impact of every kWh used during driving.

- **Second-hand Car**  
  A checkbox allows you to specify whether the current car was purchased as second-hand.  
  If **checked**, two **compulsory** fields become visible:
  - **Second-hand Car Mileage (km)**: The mileage at the time of second-hand purchase. Must be less than **Current Mileage**.  
  - **Second-hand Car Age (years)**: The car's age at the time of second-hand purchase.

  These fields are used to:
  - Determine the **user's responsibility** for production and end-of-life emissions, based on the remaining share of the vehicle’s life.
  - Recalculate the **effective End-of-Life** based on mileage and age.

  If the checkbox is **not checked**, the car is considered new and full responsibility is assigned to the current user.

  *Note*:   
  The **Second-hand Car Mileage (km)** must be lower than **Current Mileage (km)**.

- **ICE Consumption (l/100km)**  
  The fuel consumption of the **internal combustion engine (ICE)**, measured in liters per 100 km.  

- **EM Consumption (kWh/100km)**  
  The energy consumption of the **electric motor (EM)**, measured in kilowatt-hours per 100 km.  
  *(Only applicable for hybrid and electric vehicles.)*

- **Driving Share (Plug-in Hybrid only)**  
  The Driving Share field represents the proportion of kilometers driven in electric mode for plug-in hybrid vehicles. It is a decimal value between 0 and 1, where:
  - 1.0 means the vehicle is driven entirely in electric mode.
  - 0.0 means it is driven entirely using the internal combustion engine.

- **Car Mass (kg)**   
  The total weight of the car in kilograms. 

- **Car Production-EoL Footprint (kgCO₂/kg)** 
  The Car Production Footprint represents the total carbon emissions associated with the manufacturing and end-of-life treatment of the vehicle.
  This value accounts for the environmental impact of raw material extraction, vehicle assembly, and disposal or recycling processes at the end of the car's lifecycle.

- **WTT (Well-to-Tank) Fuel Footprint (gCO₂/l)**  
  The Well-to-Tank (WTT) Emissions refer to the amount of CO₂ released during the extraction, refining, and distribution of fuel before it reaches the vehicle’s tank.
  WTT emissions are a crucial component of the fuel life cycle and vary based on the type of fuel and energy source.

- **TTW (Tank-to-Wheel) Fuel Footprint (gCO₂/l)**   
  The Tank-to-Wheel (TTW) Emissions capture the CO₂ emissions produced when the fuel is combusted inside the vehicle engine during driving.
  TTW represents the direct operational emissions of the vehicle and depends primarily on fuel type and engine efficiency.

- **Reset** button  
  To restore the default values.

- **BEV Battery Settings (BEVs only):**
  - **Battery Capacity (kWh)**
    Indicates the total energy storage capacity of the vehicle's battery. This value is used to estimate emissions associated with battery production.
  - **Battery Production Footprint (kgCO₂/kWh)**
    Defines the emission factor for battery manufacturing. It represents the environmental impact of producing the battery based on its capacity.
  - **Estimated life time (km)**
    Refers to the estimated distance (in kilometers) a battery can last before requiring replacement. This helps evaluate the long-term impact of battery usage and contributes to end-of-life emission considerations.

  

### **New Car(s)**

This section allows defining the alternative(s) to the current car for evaluation.  
New cars are added by pressing the green **Plus** button, while the red **Minus** button removes them.  
Each new car can be quickly defined through its **segment** and **engine type**, but additional parameters can be set via a dialog box triggered by the **Gear** button.

The available parameters are listed below (the description of each field can be found in the [Current Car Details](#current-car-details) section):

- **Car Segment**  

- **Engine Type**  

- **Second-hand Car**
  - **Second-hand Car Mileage (km)**  
  - **Second-hand Car Age (years)**  

- **ICE Consumption (l/100km)**  

- **EM Consumption (kWh/100km)**  

- **Car Mass (kg)**  

- **Car Production-EoL Footprint (kgCO₂/kg)**

- **WTT (Well-to-Tank) Fuel Footprint (gCO₂/l)**

- **TTW (Tank-to-Wheel) Fuel Footprint (gCO₂/l)**

- **BEV Battery Settings (BEVs only):**
  - **Battery Capacity (kWh)**
  - **Battery Production Footprint (kgCO₂/kWh)**
  - **Estimated life time (km)**

- **Reset** button: Restores default values.  

- **Save** button: Saves the current changes. *(If the window is closed without saving, all changes will be lost.)*  


### **Analysis Settings**

These additional settings affect the carbon footprint computation.

- **Average annual mileage (km)**  
  The average distance the user drives each year.

- **Intended End-of-Usage (Mileage/Age)**  
  This parameter defines how long the user plans to keep the **new car(s)** after replacing the current vehicle. It represents the anticipated usage horizon of the new car(s), either in kilometers or years, starting from the moment it is put into service.

  By default, the **Keep until End of Life (EoL)** option is selected, which sets this value to the expected full lifespan of the vehicle. Alternatively, the user can specify a shorter intended usage duration, offering flexibility to model various ownership scenarios (e.g., resale after a few years or lease return).

  This parameter affects the user’s environmental responsibility over the **production** and **end-of-life** impacts of the new car. It also plays a critical role in identifying the **End-of-Usage (EoU)** point, which is the earliest among the following conditions:

  - The specified intended usage (in kilometers or years) is reached;
  - The **old car** or any of the new ones reaches its own EoL;
  - The **old car** reaches 20 years of age.


- **Maintenance**  
  Defines whether compulsory and extraordinary maintenance is performed.  
  This affects the degradation of fuel/electric consumption over time.

- **Advanced Analysis Settings**  
  Those settings can be accessed by clicking on the **Gear** button in the **Analysis Settings** area.
  - **ICE Car Life Span (km)**: Expected lifespan of an ICE car.  
  - **BEV Car Life Span (km)**: Expected lifespan of a BEV.    
  - **Reset** button: Restores default values.
  - **Save** button: Stores new values. *(If the window is closed without saving, all changes will be lost.)*



## **Carbon Footprint Analysis**

This is the output section, where **CO₂ Footprint History** is displayed and analyzed to make comparisons and find the best alternative.  
The computation starts when the **Compute Carbon Footprint** button is pressed.

The available units of measure for the analysis are:
- **years**
- **kilometers**  
When the units of measure are changed, the plot, tables and **Output data analysis options** are updated accordingly.
Data are transformed from kilometers to years and viceversa through the **Average annual mileage (km)** parameter.


### **Plot**
The carbon footprint of each car is represented graphically to provide a quick evaluation of the old car against the new ones.  
- The **history of the current car** starts from year/kilometer `0`, if the car is new, or from the **Second-hand Car Mileage** in kilometers or the equivalent in years.  
- The **history of new cars** starts from the mileage defined in **Current Mileage (km)** or its equivalent in years (representing the point of replacement).  
- The default analysis time (or distance) window is set to the **End-of-Usage (EoU)** point, which is the earliest among the following conditions:
  - The specified intended usage (in kilometers or years) is reached;
  - The **old car** reaches its own EoL;
  - The **old car** reaches 20 years of age.

Each carbon footprint history starts with a **step**, whose height represents the CO₂ emissions from the **Production and End-of-Life (EoL)** phases, scaled by the responsibility of the current user.  
- **Second-hand cars** and those **not kept until EoL** have a **responsibility factor** lower than 1.  
- During the **Use Phase**, emissions increase exponentially as the car ages due to component degradation.  

### **End-of-Usage (EoU) Table**

This table provides **quantitative data** on carbon footprint metrics at the **End-of-Usage (EoU)** point, enabling side-by-side comparisons of different vehicle options. Each row corresponds to either the current car or a new alternative under evaluation.

The table is automatically updated based on user settings such as intended usage duration, driving profile, and maintenance assumptions.

#### **Columns Description**

- **Car**  
  Identifier of the vehicle. The current vehicle is marked as **Current**, while new options are listed as **Car 1**, **Car 2**, etc.

- **Car Details**  
  A short description of the vehicle, including its segment (e.g., compact, SUV) and engine type (e.g., ICE, HEV, BEV).

- **EoU - change (tCO₂)**  
  The net change in cumulative CO₂ emissions between the EoU and the time of replacement.

- **CO₂ Savings (tCO₂)**  
  Total emissions saved by replacing the current vehicle with the new one at the **EoU**.

- **Yearly Emissions (tCO₂/year)**  
  Average yearly emissions from the replacement moment to the EoU, including all life cycle phases.
  For the **current car** only, yearly emissions are computed from the time the old car was bought to EoU.

- **Production**  
  Percentage contribution of vehicle production to the total yearly emissions.

- **EoL**  
  Percentage contribution of vehicle end-of-life processes to the total yearly emissions.

- **Use**  
  Percentage contribution of the operational (driving) phase to the total yearly emissions.

- **Maintenance**  
  Percentage contribution of maintenance activities (if applicable) to the total yearly emissions.  
  - If maintenance is disabled in settings, this column may show `/`.  
  - For electric vehicles (BEVs), a small non-zero maintenance impact may still appear depending on the data.



## **Menu**

### **File Menu**

The **File Menu** provides options related to data management and export.

- **Export Data**  
  This function allows the user to export the **input** and **output** data of the **most recent simulation** in a structured format (e.g., Excel or CSV), allowing the user to archive, share, or re-load the simulation details in future versions.  

  The exported file includes:

  - **Input Parameters**

    | Field | Description |
    |-------|-------------|
    | `Car ID` | Identifier of the car (e.g., "Current", "Car 1", "Car 2") |
    | `carSegment` | Vehicle class (e.g., Segment B, Segment C, SUV) |
    | `engineType` | Type of powertrain (e.g., Gasoline, Diesel, BEV, PHEV) |
    | `mileageAtChange` | Current mileage (km) at the time of replacement (only for the current car)|
    | `secondHandCar` | Indicates if the car was purchased second-hand (`true` / `false`) |
    | `secondHandCarMileage` | Mileage (km) at the time the car was bought used |
    | `secondHandCarAge` | Age (years) when the car was bought used |
    | `massValue` | Mass of the vehicle in kilograms |
    | `carProductionFootprint` | CO₂ footprint of vehicle production and EoL (kgCO₂/kg) |
    | `meanConsumptionLiter` | Fuel consumption for ICE (liters/10  0 km) |
    | `meanConsumptionWh` | Electricity consumption for EM (Wh/km) |
    | `drivingShare` | Share of driving in electric mode (for PHEVs, 0 to 1) |
    | `country` | Country or region for electricity mix |
    | `energyMix` | Electricity carbon intensity (gCO₂/kWh) |
    | `batteryCapacity` | Battery capacity (kWh) for BEVs and PHEVs |
    | `batteryProductionFootprint` | CO₂ footprint for battery production (kgCO₂/kWh) |
    | `batteryLifeTime` | Estimated battery life span (km) |
    | `WTT` | Well-to-Tank emissions (gCO₂/l) |
    | `TTW` | Tank-to-Wheel emissions (gCO₂/l) |
    | `maintenance` | Indicates if maintenance modeling is enabled |
    | `keepEOL` | Indicates if the car is used until end-of-life |
    | `keepUnits` | Unit of intended usage (`km` or `years`) |
    | `keepLifeSpan` | Planned usage amount in chosen unit |

  - **Simulation Outputs**

    | Field | Description |
    |-------|-------------|
    | `EoUmileage` | Mileage at the End-of-Usage (EoU) point |
    | `EoUage` | Age at the End-of-Usage (EoU) point |
    | `productionEoL` | CO₂ emissions from production and end-of-life (kgCO₂) |
    | `depreciation` | Share of production and EoL attributed to the user |
    | `usePhaseEmissions` | CO₂ emissions during the use phase (kgCO₂) |
    | `carLifeSpan` | Vehicle’s estimated life span (km) |
    | `THco2` | Total historical emissions of the vehicle (kgCO₂) at EoU |
    | `DeltaTHco2` | CO₂ difference vs. current car at between EoU and time of replacement of the current car|
    | `yearlyCo2` | Average yearly emissions (tCO₂/year) |
    | `relativeProductionCo2` | % of yearly emissions from production |
    | `relativeEolCo2` | % of yearly emissions from end-of-life |
    | `relativeUseCo2` | % of yearly emissions from the use phase |
    | `relativeMaintenanceCo2` | % of yearly emissions from maintenance |
    | `co2Savings` | Total CO₂ savings compared to current car (tCO₂) at EoU |
    | `BEkm` | Break-even mileage (km) where emissions are equal |
    | `BEco2` | Emissions at the break-even point (tCO₂) |
    | `DeltaBEkm` | Variation in break-even mileage from baseline |
    | `DeltaBEco2` | Variation in break-even emissions from baseline |


### **Help Menu**

Through the **Help Menu**, the user can access:
- The **Full Documentation** in PDF format.  
- A **Quick Intro** guide to get started.


---

## **Notes**
- Every time a field in the input section is changed, the **Compute Carbon Footprint** button must be pressed to update results.
- **Tip:** Hover over editable fields and column headers in the app for detailed tooltips.


## **Contact**

For any questions or further information, please contact:

- **Eng. Luca Cibrario** – PhD Student, DIMEAS, Politecnico di Torino  
  📧 [luca.cibrario@polito.it](mailto:luca.cibrario@polito.it)

- **Prof. Chiara Gastaldi** – Associate Professor, DIMEAS, Politecnico di Torino  
  📧 [chiara.gastaldi@polito.it](mailto:chiara.gastaldi@polito.it)


## **License**
*This software is currently private and distributed only to selected users.*

