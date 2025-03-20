# ECO Car Replacement Advisor

ECO Car Replacement Advisor helps you decide whether to replace your current car with a new one or continue repairing it based on the analysis of carbon footprint.

## Installation

1. Download the latest `.exe` file from this repository.
2. Double-click the file to run the application.


## Usage

Below are the details required to evaluate whether to replace or keep your current car.
When the car segment and engine type are selected, default values from the database are used to fill the fields related to consumptions and vehicle mass.

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
  

### **New Car(s)**

This section allows defining the alternative(s) to the current car for evaluation.  
New cars are added by pressing the green **Plus** button, while the red **Minus** button removes them.  
Each new car can be quickly defined through its **segment** and **engine type**, but additional parameters can be set via a dialog box triggered by the **Gear** button.

The available parameters are listed below:

- **Car Segment**  
- **Engine Type**  
- **Second-hand Car Mileage (km)**  
- **Keep until EoL (End of Life)**  
  Defines whether the car will be kept until the end of its life or just for a limited number of kilometers/years.  
  *(Default: `True`.)*  
- **Car Mass (kg)**  
- **ICE Consumption (l/100km)**  
- **EM Consumption (kWh/100km)**  
- **Reset** button: Restores default values.  
- **Save** button: Saves the current changes. *(If the window is closed without saving, all changes will be lost.)*  


### **Analysis Settings**

These additional settings affect the carbon footprint computation.

- **Average annual mileage (km)**  
  The average distance the user drives each year.  
- **Maintenance**  
  Defines whether compulsory and extraordinary maintenance is performed.  
  This affects the degradation of fuel/electric consumption over time.  

### **Carbon Footprint Analysis**

This is the output section, where **CO₂ history** is displayed and analyzed to make comparisons and find the best alternative.  
The computation starts when the **Compute Carbon Footprint** button is pressed.


#### **Plot**
The carbon footprint of each car is represented graphically to provide a quick evaluation of the selected cars.  
- The **history of the current car** starts from kilometer `0`.  
- The **history of alternative cars** starts from the mileage defined in **Current Mileage (km)** (representing the point of replacement).  

Each carbon footprint history starts with a **step**, whose height represents the CO₂ emissions from the **Production and End-of-Life (EoL)** phases, scaled by the responsibility of the current user.  
- **Second-hand cars** and those **not kept until EoL** have a **responsibility factor** lower than 1.  
- During the **Use Phase**, emissions increase exponentially as the car ages due to component degradation.  

#### **Tables**
These tables provide **quantitative** data for the carbon footprint history at specific mileage points.

- **Break-Even Point (BEP)**  
  If it exists, the **BEP** is the mileage where the new car's emissions cross the old car's emissions, making the new car the better option.  
  Fields in BEP Table:
  - `Car`: The vehicle reference.  
  - `BE (km)`: Distance to the BEP from when the old car was bought.  
  - `BE (t CO₂)`: Emissions in tons from the old car purchase.  
  - `ΔBE (km)`: Distance between the BEP and the moment the old car is changed.  
  - `ΔBE (t CO₂)`: Emissions in tons from the replacement point.  

- **Specific Mileage (km)**  
  Data at any given mileage:  
  - `CO₂ Footprint (t CO₂)`: Total emissions in tons at the given mileage.  
  - `Distance from BE (km)`: Difference in kilometers from the given mileage and the BEP (if it exists).  


#### **Help Button**  
Links to this README file.  


#### **Options**  
Additional settings for analysis:  
- **ICE Car Life Span (km)**: Expected lifespan of an ICE car.  
- **BEV Car Life Span (km)**: Expected lifespan of a BEV.  
- **Save** button: Stores new values.  
- **Reset** button: Restores default values.  


---

## **Notes**
Every time a field is changed, the **Compute Carbon Footprint** button must be pressed to update results.

## Contact

For any questions or further information, please contact:

- **Eng. Luca Cibrario** – PhD Student, DIMEAS, Politecnico di Torino  
  📧 [luca.cibrario@polito.it](mailto:luca.cibrario@polito.it)

- **Prof. Chiara Gastaldi** – Associate Professor, DIMEAS, Politecnico di Torino  
  📧 [chiara.gastaldi@polito.it](mailto:chiara.gastaldi@polito.it)


## **License**
*This software is currently private and distributed only to selected users.*

