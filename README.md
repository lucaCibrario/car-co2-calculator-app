# ECO Car Replacement Advisor

## Overview

ECO Car Replacement Advisor is a tool for assessing the environmental impact of replacing a car with a more sustainable model. It helps users compare carbon emissions from their current vehicle against potential new cars by modeling both production and use-phase emissions. The tool provides intuitive visualizations and tabular output to facilitate analysis and decision-making.

### Key Features

- Supports multiple new car comparisons
- Break-Even Point (BEP) and Specific Mileage/Age analysis modes
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

- **Energy mix (gCO₂/kWh)**  
  The Energy Mix represents the average carbon intensity of electricity generation in a given country, measured in grams of CO₂ emitted per kilowatt-hour (gCO₂/kWh).
  - If a specific country is selected, the energy mix is automatically populated based on average national data.
  - If "Custom" is selected, the field becomes editable to enter a value to reflect a personalized or projected energy scenario (e.g., green electricity contracts, renewable-only sources).

  This value directly affects the use-phase emissions of electric and plug-in hybrid vehicles, as it determines the CO₂ impact of every kWh used during driving.

- **Second-hand Car Mileage (km)**  
  If the car was bought used, this is the mileage on the odometer at the time of purchase.  
  To set this option, just check the box and enter the mileage of the second-hand car at the time of purchase.
  This parameter affects the responsibility of the current user for the production and EoL of the car.

  **Note**
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

- **BEV Battery Settings (BEVs only)**
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

- **Intended end-of-usage (mileage/age)**  
  Defines whether the car will be kept until the end of its life or just for a limited number of kilometers/years. The value represents the car's total lifespan from the moment of production until retirement or resale.
  If the option **Keep until EoL** is checked, the editable field is filled with the default expected life-time of the vehicle.
  Otherwise a shorter lifetime than the default can be defined, either in kilometers or years, allowing for more flexible and realistic modeling of vehicle usage patterns.

  **Note**
  **Intended end-of-usage (mileage/age)** must be greater than **Second-hand Car Mileage (km)**.
  If the age of the vehicle at the EoL is provided instead of the mileage, the total mileage covered by the car is estimated through the **Average Annual Mileage (km)** value.
  This parameter affects the responsibility of the current user for the production and EoL of the car.

- **Second-hand Car Mileage (km)**

- **ICE Consumption (l/100km)**  

- **EM Consumption (kWh/100km)**  

- **Car Mass (kg)**  

- **Car Production-EoL Footprint (kgCO₂/kg)**

- **WTT (Well-to-Tank) Fuel Footprint (gCO₂/l)**

- **TTW (Tank-to-Wheel) Fuel Footprint (gCO₂/l)**

- **BEV Battery Settings (BEVs only)**
  - **Battery Capacity (kWh)**
  - **Battery Production Footprint (kgCO₂/kWh)**
  - **Estimated life time (km)**

- **Reset** button: Restores default values.  

- **Save** button: Saves the current changes. *(If the window is closed without saving, all changes will be lost.)*  


### **Analysis Settings**

These additional settings affect the carbon footprint computation.

- **Average annual mileage (km)**  
  The average distance the user drives each year.

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
The carbon footprint of each car is represented graphically to provide a quick evaluation of the selected cars.  
- The **history of the current car** starts from year/kilometer `0`, if the car is new, or from the **Second-hand Car Mileage** in kilometers or the equivalent in years.  
- The **history of alternative cars** starts from the mileage defined in **Current Mileage (km)** or its equivalent in years(representing the point of replacement).  

Each carbon footprint history starts with a **step**, whose height represents the CO₂ emissions from the **Production and End-of-Life (EoL)** phases, scaled by the responsibility of the current user.  
- **Second-hand cars** and those **not kept until EoL** have a **responsibility factor** lower than 1.  
- During the **Use Phase**, emissions increase exponentially as the car ages due to component degradation.  

### **Tables**
These tables provide **quantitative** data for the carbon footprint history at specific mileage points.
Data can be retrieved at:

- **Break-Even Point (BEP)**  
  If it exists, the **BEP** is the mileage where the new car's emissions cross the old car's emissions, making the new car the better option from that moment on.  
  Fields in BEP Table:
  - `Car`: The vehicle reference. 
  - `Car Details`: Segment and engine type of the car for a quick reference.
  - `Age/Mileage at BE (years/km)`: The age or the mileage on the odometer of the old car at the time of the BEP.
  - `Emissions at BE (t CO₂)`: Emissions in tons from the old car production.  
  - `BEP - change (years/km)`: Distance in age or mileage between the BEP and the time of replacement.
  - `BEP - change (t CO₂)`: Emissions between the BEP and the time of replacement.

  If the BEP does not exist, the fields are empty.

- **Specific Age/Mileage (years/km)** 
  If this option is selected a user-defined age/mileage should be defined for the analysis. The table can be updated by pushing the **Refresh Table** button.
  Data at any given age/mileage:
  - `Car`: The vehicle reference. 
  - `Car Details`: Segment and engine type of the car for a quick reference.
  - `CO₂ savings (t CO₂)`: Difference in the total emissions between the new car and the old one. A positive value means that the new car is saving emissions.  
  - `Distance from BE (years/km)`: Difference in years/kilometers from the given mileage and the BEP (if it exists).  


## **Help Menu**  
Through the **Help Menu** the user can access:
- the **Full Documentation** in PDF format
- a quick intro to get started


---

## **Notes**
- Every time a field in the input section is changed, the **Compute Carbon Footprint** button must be pressed to update results.
- If the plot does not update automatically, it is sufficient to move the mouse on its area.

## Contact

For any questions or further information, please contact:

- **Eng. Luca Cibrario** – PhD Student, DIMEAS, Politecnico di Torino  
  📧 [luca.cibrario@polito.it](mailto:luca.cibrario@polito.it)

- **Prof. Chiara Gastaldi** – Associate Professor, DIMEAS, Politecnico di Torino  
  📧 [chiara.gastaldi@polito.it](mailto:chiara.gastaldi@polito.it)


## **License**
*This software is currently private and distributed only to selected users.*

