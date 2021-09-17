## Table of Contents
* [About the project](#about-the-project)
  * [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Usage](#usage)
  * [Inputs](#inputs)
  * [Outputs](#outputs)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [Contact](#contact)
* [Acknowledgements](#acknowledgements)


## About the project
The Landscape Model component encapsulating the CMF Continuous module.  
This is an automatically generated documentation based on the available code and in-line documentation. The current
version of this document is from 2021-09-17.  

### Built with
* Landscape Model core version 1.7
* Regulatory Catchment Model version 8 Aug 2018 (see `\module\documentation` for details)


## Getting Started
The component can be used in any Landscape Model based on core version 1.7 or newer. See the Landscape Model
core's `README` for general tips on how to add a component to a Landscape Model.

### Prerequisites
A model developer that wants to add the `CascadeToxswa` component to a Landscape Model needs to set up the general 
structure for a Landscape Model first. See the Landscape Model core's `README` for details on how to do so.

### Installation
1. Copy the `CascadeToxswa` component into the `model\variant` sub-folder.
2. Make use of the component by including it into the model composition using `module=CmfContinuous` and 
   `class=CmfContinuous`. 


## Usage
The following gives a sample configuration of the `CascadeToxswa` component. See [inputs](#inputs) and 
[outputs](#outputs) for further details on the component's interface.
```xml
<CascadeToxswa module="CascadeToxswa" class="CascadeToxswa" enabled="$(RunCascadeToxswa)">
<ProcessingPath>$(_MCS_BASE_DIR_)\$(_MC_NAME_)\processing\fate\cascade</ProcessingPath>
    <SuspendedSolids
type="float" unit="g/m&#179;">15</SuspendedSolids>
    <HydrographyReachIds>
        <FromOutput
component="DepositionToReach" output="Reaches" />
    </HydrographyReachIds>
    <TimeSeriesStart>
        <FromOutput
component="Hydrology" output="TimeSeriesStart" />
    </TimeSeriesStart>
    <WaterDischarge>
        <FromOutput
component="Hydrology" output="Flow" />
    </WaterDischarge>
    <WaterDepth>
        <FromOutput component="Hydrology"
output="Depth" />
    </WaterDepth>
    <Temperature>
        <FromOutput component="Weather" output="TEMPERATURE_AVG"
/>
    </Temperature>
    <MassLoadingSprayDrift>
        <FromOutput component="DepositionToReach" output="Deposition"
/>
    </MassLoadingSprayDrift>
    <MolarMass type="float" unit="g/mol">$(MolarMass)</MolarMass>
<SaturatedVapourPressure type="float" unit="Pa">$(SaturatedVapourPressure)</SaturatedVapourPressure>
<ReferenceTemperatureForSaturatedVapourPressure type="float" unit="&#176;C">
        $(Temp0)
</ReferenceTemperatureForSaturatedVapourPressure>
    <MolarEnthalpyOfVaporization type="float" unit="kJ/mol">
$(MolarEnthalpyOfVaporization)
    </MolarEnthalpyOfVaporization>
    <SolubilityInWater type="float"
unit="mg/l">$(SolubilityInWater)</SolubilityInWater>
    <ReferenceTemperatureForWaterSolubility type="float"
unit="&#176;C">
        $(Temp0)
    </ReferenceTemperatureForWaterSolubility>
    <MolarEnthalpyOfDissolution
type="float" unit="kJ/mol">
        $(MolarEnthalpyOfDissolution)
    </MolarEnthalpyOfDissolution>
<DiffusionCoefficient type="float" unit="m&#178;/d">$(DiffusionCoefficient)</DiffusionCoefficient>
<ReferenceTemperatureForDiffusion type="float" unit="&#176;C">$(Temp0)</ReferenceTemperatureForDiffusion>
<HalfLifeTransformationInWater type="float" unit="d">$(DT50sw)</HalfLifeTransformationInWater>
<TemperatureAtWhichHalfLifeInWaterWasMeasured type="float" unit="&#176;C">
        $(Temp0)
</TemperatureAtWhichHalfLifeInWaterWasMeasured>
    <MolarActivationEnthalpyOfTransformationInWater type="float"
unit="kJ/mol">
        $(MolarActivationEnthalpyOfTransformationInWater)
</MolarActivationEnthalpyOfTransformationInWater>
    <HalfLifeTransformationInSediment type="float"
unit="d">$(DT50sed)</HalfLifeTransformationInSediment>
    <TemperatureAtWhichHalfLifeInSedimentWasMeasured type="float"
unit="&#176;C">
        $(Temp0)
    </TemperatureAtWhichHalfLifeInSedimentWasMeasured>
<MolarActivationEnthalpyOfTransformationInSediment type="float" unit="kJ/mol">
$(MolarActivationEnthalpyOfTransformationInSediment)
    </MolarActivationEnthalpyOfTransformationInSediment>
<CoefficientForEquilibriumAdsorptionInSediment type="float" unit="l/kg" eval="true">
        $(KOC) / 1.742
</CoefficientForEquilibriumAdsorptionInSediment>
    <ReferenceConcentrationInLiquidPhaseInSediment type="float"
unit="mg/l">
        $(ReferenceConcentrationForKOC)
    </ReferenceConcentrationInLiquidPhaseInSediment>
<FreundlichExponentInSediment type="float" unit="1">
        $(FreundlichExponentInSedimentAndSuspendedParticles)
</FreundlichExponentInSediment>
    <CoefficientForEquilibriumAdsorptionOfSuspendedSoils type="float" unit="l/kg"
eval="true">
        $(KOC) / 1.742
    </CoefficientForEquilibriumAdsorptionOfSuspendedSoils>
<ReferenceConcentrationForSuspendedSoils type="float" unit="mg/l">
        $(ReferenceConcentrationForKOC)
</ReferenceConcentrationForSuspendedSoils>
    <FreundlichExponentForSuspendedSoils type="float" unit="1">
$(FreundlichExponentInSedimentAndSuspendedParticles)
    </FreundlichExponentForSuspendedSoils>
<CoefficientForLinearAdsorptionOnMacrophytes type="float" unit="l/kg">
        0
</CoefficientForLinearAdsorptionOnMacrophytes>
    <NumberWorkers type="int">$(CascadeToxswaWorkers)</NumberWorkers>
<HydrographyReaches>
        <FromOutput component="LandscapeScenario" output="hydrography_id" />
</HydrographyReaches>
    <HydrographyGeometries>
        <FromOutput component="LandscapeScenario"
output="hydrography_geom" />
    </HydrographyGeometries>
    <DownstreamReach>
        <FromOutput
component="LandscapeScenario" output="hydrography_downstream" />
    </DownstreamReach>
    <BottomWidth>
<FromOutput component="LandscapeScenario" output="hydrography_bottom_width" />
    </BottomWidth>
    <BankSlope>
<FromOutput component="LandscapeScenario" output="hydrography_bank_slope" />
    </BankSlope>
    <OrganicContent>
<FromOutput component="LandscapeScenario" output="hydrography_organic_content" />
    </OrganicContent>
<BulkDensity>
        <FromOutput component="LandscapeScenario" output="hydrography_bulk_density" />
    </BulkDensity>
<Porosity>
        <FromOutput component="LandscapeScenario" output="hydrography_porosity" />
    </Porosity>
</CascadeToxswa>
```

### Inputs
#### ProcessingPath
The working directory for the module. It is used for all files prepared as module inputs
or generated as (temporary) module outputs.  
`ProcessingPath` expects its values to be of type `str`.
Values of the `ProcessingPath` input may not have a physical unit.
Values have to refer to the `global` scale.

#### Begin
The first time step for which input data is provided. This is also the time step of where
the CmfContinuous simulation starts.  
`Begin` expects its values to be of type `date`.
Values of the `Begin` input may not have a physical unit.
Values have to refer to the `global` scale.

#### End
The last time step for which input data is provided. This is also the time step of where
the CmfContinuous simulation ends.  
`End` expects its values to be of type `date`.
Values of the `End` input may not have a physical unit.
Values have to refer to the `global` scale.

#### Threads
The number of simultaneous processes that are spawned by the CmfContinuous module.  
`Threads` expects its values to be of type `int`.
Values of the `Threads` input may not have a physical unit.
Values have to refer to the `global` scale.

#### SolverType
The type of solver used by cmf. Currently, only `CVodeKLU` is supported by CmfContinuous.  
`SolverType` expects its values to be of type `str`.
Values of the `SolverType` input may not have a physical unit.
Values have to refer to the `global` scale.
The currently only allowed value is CVodeKLU.

#### Hydrography
The spatial delineation of the hydrographic features in the simulated landscape. This
input basically represents the flow-lines used during preparation of the hydrology. The hydrography is
consistently for all components of the Landscape Model subdivided into individual segments (*reaches*).  
`Hydrography` expects its values to be of type `str`.
Values of the `Hydrography` input may not have a physical unit.
Values have to refer to the `global` scale.

#### MolarMass
The molar mass of the substance depositing at the water body surface.  
`MolarMass` expects its values to be of type `float`.
The physical unit of the `MolarMass` input values is `g/mol`.
Values have to refer to the `global` scale.

#### DT50sw
The half-life transformation time in water of the substance depositing at the water body 
surface.  
`DT50sw` expects its values to be of type `float`.
The physical unit of the `DT50sw` input values is `d`.
Values have to refer to the `global` scale.

#### DT50sed
The half-life transformation time in sediment of the substance depositing at the water 
body surface.  
`DT50sed` expects its values to be of type `float`.
The physical unit of the `DT50sed` input values is `d`.
Values have to refer to the `global` scale.

#### KOC
The coefficient for equilibrium adsorption in sediment of the substance depositing at 
the water body surface.  
`KOC` expects its values to be of type `float`.
The physical unit of the `KOC` input values is `l/kg`.
Values have to refer to the `global` scale.

#### Temp0
The reference temperature to which the physical and chemical substance values apply.  
`Temp0` expects its values to be of type `float`.
The physical unit of the `Temp0` input values is `°C`.
Values have to refer to the `global` scale.

#### Q10
The temperature coefficient for chemical reactions of the deposited substance.  
`Q10` expects its values to be of type `float`.
The physical unit of the `Q10` input values is `1`.
Values have to refer to the `global` scale.

#### PlantUptake
The fraction of pesticide that is taken up by plants.  
`PlantUptake` expects its values to be of type `float`.
The physical unit of the `PlantUptake` input values is `1`.
Values have to refer to the `global` scale.

#### QFac
The QFac parameter is not documented in the module documentation.  
`QFac` expects its values to be of type `float`.
The physical unit of the `QFac` input values is `1`.
Values have to refer to the `global` scale.

#### Catchment
A file path to a CSV file detailing the hydrographic properties of the entire catchment
depicted by hydrographic the scenario. This file is usually provided by the scenario developer (if
usage of CmfContinuous is supported by the scenario) and is made available as a project macro.  
`Catchment` expects its values to be of type `str`.
Values of the `Catchment` input may not have a physical unit.
Values have to refer to the `global` scale.

#### DriftDeposition
The average drift deposition onto the surface of a water body.  
`DriftDeposition` expects its values to be of type `ndarray`.
The physical unit of the `DriftDeposition` input values is `mg/m²`.
Values have to refer to the `time/day, space/reach` scale.

#### TimeSeries
The inflows to individual reaches. This includes only flows that do not originate from an
upstream reach (these are modelled by cmf), i.e., lateral inflows. Not every reach has such inflows and
the list of reaches with inflows therefore is a subset of the list of reaches considered by the 
hydrographic scenario.  
`TimeSeries` expects its values to be of type `ndarray`.
The physical unit of the `TimeSeries` input values is `m³/d`.
Values have to refer to the `time/hour, space/reach2` scale.

#### ReachesDrift
The numeric identifiers for individual reaches (in the order of the `DriftDeposition` 
input) that apply scenario-wide.  
`ReachesDrift` expects its values to be of type `ndarray`.
Values of the `ReachesDrift` input may not have a physical unit.
Values have to refer to the `space/reach` scale.

#### InflowReaches
The numeric identifiers for individual reaches that show lateral inflows (in the order of
the `TimeSeries` input).  
`InflowReaches` expects its values to be of type `list`.
Values of the `InflowReaches` input may not have a physical unit.
Values have to refer to the `space/reach2` scale.

### Outputs
#### Reaches
The numerical identifiers of the reaches in the order presented by the `PEC_SW` output.  
Values are expectedly of type `list[int]`.
The values apply to the following scale: `space/reach`.
Values have no physical unit.
#### PEC_SW
The modelled concentration in the water phase.  
Values are expectedly of type `ndarray`.
Value representation is in a 2-dimensional array.
Dimension 1 spans the number of simulated hours as spanned by the [Begin](#Begin) and [End](#end) input.
Dimension 2 spans the number of reaches included in the [Hydrography](#Hydrography) input.
Chunking of the array is for fast retrieval of time series.
Individual array elements have a type of `float`.
The values apply to the following scale: `time/hour, space/base_geometry`.
The default value of the output is `0`.
The physical unit of the values is `mg/m³`.


## Roadmap
The following changes will be part of future `CascadeToxswa` versions:
* z-value precision ([#3](https://gitlab.bayer.com/aqrisk-landscape/cmfcontinuous-component/-/issues/1))
* Deprecation warning ([#2](https://gitlab.bayer.com/aqrisk-landscape/cmfcontinuous-component/-/issues/2))


## Contributing
Contributions are welcome. Please contact the authors (see [Contact](#contact)). Also consult the `CONTRIBUTING` 
document for more information.


## License
Distributed under the CC0 License. See `LICENSE` for more information.


## Contact
Sascha Bub (component) - sascha.bub@gmx.de  
Thorsten Schad (component) - thorsten.schad@bayer.com  
Sebastian Multsch (module) - smultsch@knoell.com  


## Acknowledgements
* [cmf](https://philippkraft.github.io/cmf/)  
* [GDAL](https://pypi.org/project/GDAL)  
* [NumPy](https://numpy.org)  
