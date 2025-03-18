# ECO Car Replacement Advisor

ECO Car Replacement Advisor helps you decide whether to replace your current car with a new one or continue repairing it based on economic and ecological factors.

## Installation

1. Download the latest `.exe` file from this repository.
2. Double-click the file to run the application.

## Usage

Below are the details required to evaluate whether to replace or keep your current car.
When car segment and engine type are selected, default values from the database are used to fill the fields related to consumptions and vehicle mass.

### Current Car Details

Those are the setting for the definition of the current car that has to be replaced.

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

- **Current Mileage (km)** - Compulsory
The total number of kilometers the car has been driven.  

- **ICE Consumption (l/100km)**
The fuel consumption of the **internal combustion engine (ICE)**, measured in liters per 100 km.  

- **EM Consumption (kWh/100km)**
The energy consumption of the **electric motor (EM)**, measured in kilowatt-hours per 100 km.  
*(Only applicable for hybrid and electric vehicles.)*  

- **Car Mass (kg)**
The total weight of the car in kilograms.  

- **Second-hand Car Mileage (km)**
If the car was bought used, this is the mileage recorded at the time of purchase. 
To set this option, just check the box and enter the mileage of the second-hand car at the time of purchase.

- **Country (or Region)**
The location where the car is mainly driven. 

- **Reset** button
To restore the default values.

### New Car(s)

In this form the alternative to the current car, which we want to evaluate, can be defined.
New cars are added by pushing the green **Plus** button, while the red **Minus** is used to cancel them. 
Each new car car be quickly defined through its segment and engine type, but additional parameter can be found in a dialog box triggered by the **Gear** button.

- **Car Segment**

- **Engine Type**
  
- **Second-hand Car Mileage (km)**

- **Keep until EoL (End of Life)**
To define if the car will be kept until the end of life or just for a limited amount of kilometers/years
The default is **True**.

- **Car Mass (kg)**

- **ICE Consumption (l/100km)**

- **EM Consumption (kWh/100km)**

- **Reset** button
To restore the default values.

- **Save** button
To save the current changes (if the window is closed without saving, all the changes are not stored).

### Analysis Settings

Below are listed additional general data used to compute the carbon footprint of cars.

- **Average annual mileage (km)**
It is the average distance that is usually driven by the user each year.

- **Maintenance**
Used to define if the compulsory and extraordinary maintenance is done to the vehicles.
This affects the degradation of the consumptions over time.

### Carbon Footprint Analysis

This is the output section, where the CO_2 hystories are displayed and analysed to make comparisons find the best alternative.
The computation is started by pressing the **Compute Carbon Footprint** button below the input section.

#### Plot

The carbon footprint of each car is represented graphically to provide a quick evaluation of the cars selected for the analysis.
The hystory of the current car starts from kilometer 0, while those of the other cars from the mileage defined under **Current Mileage (km)**, that represents the moment of the change.
The carbon footprint hystory of each car starts with a step, whose high represent the CO_2 emitted in the **production and EoL** phases, scaled by the responsibility of the current user for those emissions. Second-hand cars and those ones, which are not kept until EoL, will have a responsibily factor lower than one.
During the **Use** phase, emissions are proportional to the car fuel/electricity consumptions, that increase with an exponential law as the mileage grows due to the degradation of the components vehicles.

#### Tables

Used to report quantitative data










#### Example Scenario
> Suppose you have a **10-year-old car** with high fuel consumption. The tool will analyze whether a switch to an **electric vehicle** or a **hybrid** is financially and ecologically beneficial.

## License

*This software is currently private and distributed only to selected users.*

---

Would you like additional formatting options, such as **bold text, tables, or lists**?
