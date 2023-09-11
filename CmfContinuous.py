"""Component for the CMF Continuous module."""
import datetime
import numpy as np
from osgeo import ogr
import os
import shutil
import base
import attrib


class CmfContinuous(base.Component):
    """The Landscape Model component encapsulating the CMF Continuous module."""
    # RELEASES
    VERSION = base.VersionCollection(
        base.VersionInfo("2.0.16", "2023-03-09"),
        base.VersionInfo("2.0.15", "2022-03-03"),
        base.VersionInfo("2.0.14", "2021-12-10"),
        base.VersionInfo("2.0.13", "2021-12-07"),
        base.VersionInfo("2.0.12", "2021-11-18"),
        base.VersionInfo("2.0.11", "2021-10-19"),
        base.VersionInfo("2.0.10", "2021-10-12"),
        base.VersionInfo("2.0.9", "2021-10-11"),
        base.VersionInfo("2.0.8", "2021-09-17"),
        base.VersionInfo("2.0.7", "2021-09-02"),
        base.VersionInfo("2.0.6", "2021-08-18"),
        base.VersionInfo("2.0.5", "2021-08-17"),
        base.VersionInfo("2.0.4", "2021-07-16"),
        base.VersionInfo("2.0.3", "2020-12-28"),
        base.VersionInfo("2.0.2", "2020-12-07"),
        base.VersionInfo("2.0.1", "2020-12-03"),
        base.VersionInfo("2.0.0", "2020-10-22"),
        base.VersionInfo("1.3.35", "2020-08-12"),
        base.VersionInfo("1.3.33", "2020-07-30"),
        base.VersionInfo("1.3.27", "2020-05-20"),
        base.VersionInfo("1.3.24", "2020-04-02"),
        base.VersionInfo("1.3.16", "2020-02-11"),
        base.VersionInfo("1.3.6", "2020-01-09"),
        base.VersionInfo("1.3.3", "2019-12-15"),
        base.VersionInfo("1.2.38", None),
        base.VersionInfo("1.2.37", None)
    )

    # AUTHORS
    VERSION.authors.extend((
        "Sascha Bub (component) - sascha.bub@gmx.de",
        "Thorsten Schad (component) - thorsten.schad@bayer.com",
        "Sebastian Multsch (module) - smultsch@knoell.com"
    ))

    # ACKNOWLEDGEMENTS
    VERSION.acknowledgements.extend((
        "[cmf](https://philippkraft.github.io/cmf/)",
        "[GDAL](https://pypi.org/project/GDAL)",
        "[NumPy](https://numpy.org)"
    ))

    # ROADMAP
    VERSION.roadmap.extend((
        "z-value precision ([#3](https://gitlab.bayer.com/aqrisk-landscape/cmfcontinuous-component/-/issues/1))",
        "Deprecation warning ([#2](https://gitlab.bayer.com/aqrisk-landscape/cmfcontinuous-component/-/issues/2))"
    ))

    # CHANGELOG
    VERSION.added("1.2.37", "`components.CatchmentModel` component")
    # noinspection SpellCheckingInspection
    VERSION.changed("1.2.38", "`components.CatchmentModel` renamed to `components.CmfContinuousEfate` ")
    # noinspection SpellCheckingInspection
    VERSION.fixed("1.3.3", "increased numeric precision in `components.CmfContinuousEfate` (preliminary)")
    # noinspection SpellCheckingInspection
    VERSION.fixed("1.3.6", "Fixes in `components.CmfContinuousEfate` ")
    # noinspection SpellCheckingInspection
    VERSION.changed("1.3.16", "Substance parameterization in `components.CmfContinuousEfate` changed")
    # noinspection SpellCheckingInspection
    VERSION.changed("1.3.24", "`components.CmfContinuousEfate` uses base function to call module")
    # noinspection SpellCheckingInspection
    VERSION.changed("1.3.27", "`components.CmfContinuousEfate` specifies scales")
    # noinspection SpellCheckingInspection
    VERSION.changed("1.3.33", "`components.CmfContinuousEfate` checks input types strictly")
    # noinspection SpellCheckingInspection
    VERSION.changed("1.3.33", "`components.CmfContinuousEfate` checks for physical units")
    # noinspection SpellCheckingInspection
    VERSION.changed("1.3.33", "`components.CmfContinuousEfate` reports physical units to the data store")
    # noinspection SpellCheckingInspection
    VERSION.changed("1.3.33", "`components.CmfContinuousEfate` checks for scales")
    # noinspection SpellCheckingInspection
    VERSION.changed("1.3.35", "`components.CmfContinuousEfate` receives empty path environment variable")
    VERSION.changed("2.0.0", "First independent release")
    VERSION.added("2.0.1", "Changelog and release history")
    VERSION.changed("2.0.2", "Changed specification of `TimeSeries` input and added `InflowReaches` input")
    VERSION.changed("2.0.2", "Inflows from fields into reaches are now processed from the Landscape model data store")
    VERSION.fixed("2.0.3", "Suppressed spelling error check for CSV file header")
    VERSION.changed("2.0.4", "Renamed component")
    VERSION.changed("2.0.4", "Use of markdown in changelog")
    VERSION.changed("2.0.4", "Spelling of input names")
    VERSION.fixed("2.0.4", "Data type access")
    VERSION.added("2.0.5", "README, CHANGELOG, CONTRIBUTING and LICENSE")
    VERSION.added("2.0.6", "Missing reference to module documentation and missing documentation of `PEC_SW` output")
    VERSION.added("2.0.7", "ogr module import")
    VERSION.changed("2.0.8", "Make use of generic types for class attributes")
    VERSION.changed("2.0.9", "Replaced legacy format strings by f-strings")
    VERSION.changed("2.0.10", "Switched to Google docstring style")
    VERSION.changed("2.0.11", "Specified working directory for module")
    VERSION.changed("2.0.12", "Removed `ReachesDrift` input")
    VERSION.changed("2.0.12", "Reports element names of outputs")
    VERSION.changed("2.0.13", "Spell checking")
    VERSION.changed("2.0.14", "Specifies offset of outputs")
    VERSION.changed("2.0.15", "Mitigated weak code warning")
    VERSION.changed(
        "2.0.16", "Updated module to version 8 Aug 2018-1 (removed large files from due to file size limits)")

    def __init__(self, name, observer, store):
        """
        Initializes the CmfContinuous component.

        Args:
            name: The name of the component
            observer: The default observer of the component
            store: The default store of the component.
        """
        super(CmfContinuous, self).__init__(name, observer, store)
        self._module = base.Module(
            "Regulatory Catchment Model",
            "8 Aug 2018-1",
            "module",
            r"\module\documentation",
            base.Module("Python", "3.7.2", "module/bin/python", "module/bin/python/NEWS.txt", None)
        )
        # noinspection SpellCheckingInspection
        self._inputs = base.InputContainer(self, [
            base.Input(
                "ProcessingPath",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="""The working directory for the module. It is used for all files prepared as module inputs
                or generated as (temporary) module outputs."""
            ),
            base.Input(
                "Begin",
                (attrib.Class(datetime.date, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="""The first time step for which input data is provided. This is also the time step of where
                the CmfContinuous simulation starts."""
            ),
            base.Input(
                "End",
                (attrib.Class(datetime.date, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="""The last time step for which input data is provided. This is also the time step of where
                the CmfContinuous simulation ends."""
            ),
            base.Input(
                "Threads",
                (attrib.Class(int, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="The number of simultaneous processes that are spawned by the CmfContinuous module."
            ),
            base.Input(
                "SolverType",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1), attrib.Equals("CVodeKLU")),
                self.default_observer,
                description="The type of solver used by cmf. Currently, only `CVodeKLU` is supported by CmfContinuous."
            ),
            base.Input(
                "Hydrography",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="""The spatial delineation of the hydrographic features in the simulated landscape. This
                input basically represents the flow-lines used during preparation of the hydrology. The hydrography is
                consistently for all components of the Landscape Model subdivided into individual segments (*reaches*).
                """
            ),
            base.Input(
                "MolarMass",
                (attrib.Class(float, 1), attrib.Unit("g/mol", 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="The molar mass of the substance depositing at the water body surface."
            ),
            base.Input(
                "DT50sw",
                (attrib.Class(float, 1), attrib.Unit("d", 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="""The half-life transformation time in water of the substance depositing at the water body 
                surface."""
            ),
            base.Input(
                "DT50sed",
                (attrib.Class(float, 1), attrib.Unit("d", 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="""The half-life transformation time in sediment of the substance depositing at the water 
                body surface."""
            ),
            base.Input(
                "KOC",
                (attrib.Class(float, 1), attrib.Unit("l/kg", 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="""The coefficient for equilibrium adsorption in sediment of the substance depositing at 
                the water body surface."""
            ),
            base.Input(
                "Temp0",
                (attrib.Class(float, 1), attrib.Unit("°C", 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="The reference temperature to which the physical and chemical substance values apply."
            ),
            base.Input(
                "Q10",
                (attrib.Class(float, 1), attrib.Unit("1", 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="The temperature coefficient for chemical reactions of the deposited substance."
            ),
            base.Input(
                "PlantUptake",
                (attrib.Class(float, 1), attrib.Unit("1", 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="The fraction of pesticide that is taken up by plants."
            ),
            base.Input(
                "QFac",
                (attrib.Class(float, 1), attrib.Unit("1", 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="The QFac parameter is not documented in the module documentation."
            ),
            base.Input(
                "Catchment",
                (attrib.Class(str, 1), attrib.Unit(None, 1), attrib.Scales("global", 1)),
                self.default_observer,
                description="""A file path to a CSV file detailing the hydrographic properties of the entire catchment
                depicted by hydrographic the scenario. This file is usually provided by the scenario developer (if
                usage of CmfContinuous is supported by the scenario) and is made available as a project macro."""
            ),
            base.Input(
                "DriftDeposition",
                (
                    attrib.Class(np.ndarray, 1),
                    attrib.Unit("mg/m²", 1),
                    attrib.Scales("time/day, space/reach", 1)
                ),
                self.default_observer,
                description="The average drift deposition onto the surface of a water body."
            ),
            base.Input(
                "TimeSeries",
                (attrib.Class(np.ndarray, 1), attrib.Unit("m³/d", 1), attrib.Scales("time/hour, space/reach2", 1)),
                self.default_observer,
                description="""The inflows to individual reaches. This includes only flows that do not originate from an
                upstream reach (these are modelled by cmf), i.e., lateral inflows. Not every reach has such inflows and
                the list of reaches with inflows therefore is a subset of the list of reaches considered by the 
                hydrographic scenario."""
            ),
            base.Input(
                "InflowReaches",
                (attrib.Class(list[int], 1), attrib.Unit(None, 1), attrib.Scales("space/reach2", 1)),
                self.default_observer,
                description="""The numeric identifiers for individual reaches that show lateral inflows (in the order of
                the `TimeSeries` input)."""
            )
        ])
        self._outputs = base.OutputContainer(self, [
            base.Output(
                "Reaches",
                store,
                self,
                {"scales": "space/reach", "unit": None},
                "The numerical identifiers of the reaches in the order presented by the `PEC_SW` output.",
                {"type": "list[int]"}
            ),
            base.Output(
                "PEC_SW",
                store,
                self,
                {"data_type": np.float, "scales": "time/hour, space/base_geometry", "default": 0, "unit": "mg/m³"},
                "The modelled concentration in the water phase.",
                {
                    "type": np.ndarray,
                    "shape": (
                        "the number of simulated hours as spanned by the [Beginning](#Begin) and [End](#end) input",
                        "the number of reaches included in the [Hydrography](#Hydrography) input"
                    ),
                    "chunks": "for fast retrieval of time series"
                }
            )
        ])

        self._reaches = None

    def run(self):
        """
        Runs the component.

        Returns:
            Nothing.
        """
        self.default_observer.write_message(2, "Component relies on insensible high precision of z-coordinate")
        project_name = "e1"
        processing_path = self.inputs["ProcessingPath"].read().values
        self.prepare_project(processing_path, project_name)
        self.prepare_drift_deposition(os.path.join(processing_path, project_name, "SprayDriftList.csv"))
        self.prepare_time_series(os.path.join(processing_path, project_name, "TimeSeries"))
        self.run_project(processing_path, project_name)
        self.read_outputs(os.path.join(processing_path, project_name, f"{project_name}_reaches.csv"))

    def prepare_catchment_list(self, catchment_file):
        """
        Prepares the catchment list.

        Args:
            catchment_file: The file path for the catchment list.

        Returns:
            Nothing.
        """
        shutil.copyfile(self.inputs["Catchment"].read().values, catchment_file)

    @staticmethod
    def prepare_cell_list(cell_list):
        """
        Prepares the hydrological cell list.

        Args:
            cell_list: The file path for the hydrological cell list.

        Returns:
            Nothing.
        """
        with open(cell_list, "w") as f:
            # noinspection SpellCheckingInspection
            # noinspection GrazieInspection
            f.write(
                "key,reach,reach_connection,adjacent_field,field_connection,x,y,z,latitude,gw_depth,"
                "residencetime_gw_river,residencetime_drainage_river,puddledepth,saturated_depth,evap_depth,area,"
                "deep_gw,deep_gw_rt,drainage_depth,drainage_suction_limit,drainage_t_ret,flowwdith_sw,slope_sw,"
                "nManning,hasDrainage,meteostation,rainstation,soil,plantmodel,unit_traveltime,soilwaterflux"
            )

    @staticmethod
    def prepare_climate(climate_list):
        """
        Prepares the weather input.

        Args:
            climate_list: The file pah for the weather input.

        Returns:
            Nothing.
        """
        with open(climate_list, "w") as f:
            f.write("key,x,y,z,lat,lon")

    @staticmethod
    def prepare_crop_coefficient_list(crop_coefficient_list):
        """
        Prepares the crop coefficient list.

        Args:
            crop_coefficient_list: The file path for the crop coefficient list.

        Returns:
            Nothing.
        """
        with open(crop_coefficient_list, "w") as f:
            # noinspection SpellCheckingInspection
            f.write(
                "key,GLAImin,GLAImax,GLAIharv,rootinit,rootmax,heightinit,heightmax,rpin,Dmin,Dstart,Dmax,Dharv,"
                "cform,dform,feddes1,feddes2,feddes3,feddes4,croptype,wintercrop"
            )

    @staticmethod
    def prepare_crop_management_list(crop_management_list):
        """
        Prepares the crop management list.

        Args:
            crop_management_list: The file path for the crop management list.

        Returns:
            Nothing.
        """
        with open(crop_management_list, "w") as f:
            f.write("key,date,task,description,value")

    def prepare_project(self, processing_path, project_name):
        """
        Prepares the module project.

        Args:
            processing_path: The file path where processing should be conducted.
            project_name: The name of the project.

        Returns:
            Nothing.
        """
        project_path = os.path.join(processing_path, project_name)
        os.makedirs(project_path)
        self.prepare_project_list(os.path.join(processing_path, f"{project_name}.csv"), project_name, processing_path)
        self.prepare_climate(os.path.join(project_path, "ClimateList.csv"))
        self.prepare_cell_list(os.path.join(project_path, "CellList.csv"))
        self.prepare_reach_list(os.path.join(project_path, "ReachList.csv"))
        self.prepare_soil_list(os.path.join(project_path, "SoilList.csv"))
        self.prepare_substance_list(os.path.join(project_path, "SubstanceList.csv"))
        self.prepare_crop_coefficient_list(os.path.join(project_path, "CropCoefficientList.csv"))
        self.prepare_crop_management_list(os.path.join(project_path, "CropManagementList.csv"))
        self.prepare_catchment_list(os.path.join(project_path, "CatchmentList.csv"))

    def prepare_project_list(self, project_list_file, project_name, processing_path):
        """
        Prepares the project list.

        Args:
            project_list_file: The file path for the project list.
            project_name: The name of the project.
            processing_path: The file path where processing should be conducted.

        Returns:
            Nothing.
        """
        with open(project_list_file, "w") as f:
            # noinspection SpellCheckingInspection
            f.write(
                "key,fpath,database,runtype,catchment_separation,begin,end,separate_solver,threads,solvertype,"
                "solutesolvertype,chunksize,substance,efate,drift,timestep,simulation,preprocessing,postprocessing\n"
                f"{project_name},{processing_path},csv,inStream,FALSE,"
                f"{self.inputs['Begin'].read().values.strftime('%Y-%m-%dT%H:%M')},"
                f"{self.inputs['End'].read().values.strftime('%Y-%m-%dT%H:%M')},FALSE,"
                f"{self.inputs['Threads'].read().values},{self.inputs['SolverType'].read().values},None,0,CMP_A,"
                "steps1234,xdrift,hour,TRUE,FALSE,FALSE"
            )

    def prepare_reach_list(self, reach_list_file):
        """
        Prepares the reaches list.

        Args:
            reach_list_file: The file path for the reaches list.

        Returns:
            Nothing.
        """
        hydrography = self.inputs["Hydrography"].read().values
        driver = ogr.GetDriverByName("ESRI Shapefile")
        data_source = driver.Open(hydrography, 0)
        layer = data_source.GetLayer()
        self._reaches = np.zeros((layer.GetFeatureCount(),), np.int)
        with open(reach_list_file, "w") as f:
            # noinspection SpellCheckingInspection
            f.write(
                "key,x,y,z,downstream,initial_depth,manning_n,bankslope,bottomwidth,floodplainslope,shape,dens,"
                "porosity,oc,depth_sed,depth_sed_deep\n"
            )
            for index, feature in enumerate(layer):
                key_r = feature.GetField("key")
                geom = feature.GetGeometryRef()
                coord = geom.GetPoint(0)
                downstream = feature.GetField("downstream")
                f.write(f"r{key_r},")
                f.write(f"{round(coord[0], 2)},")
                f.write(f"{round(coord[1], 2)},")
                f.write(f"{round(coord[2], 8)},")
                f.write(f"{'' if downstream == 'Outlet' else 'r'}{downstream},")
                f.write(f"{feature.GetField('initial_de')},")
                f.write(f"{feature.GetField('manning_n')},")
                # noinspection SpellCheckingInspection
                f.write(f"{feature.GetField('bankslope')},")
                f.write(f"{feature.GetField('width')},")
                f.write("200,")  # floodplain
                f.write(f"{feature.GetField('shape_1')},")
                f.write(f"{feature.GetField('dens')},")
                f.write(f"{feature.GetField('porosity')},")
                f.write(f"{feature.GetField('oc')},")
                f.write(f"{feature.GetField('depth_sed')},")
                f.write(f"{feature.GetField('depth_sed_')}\n")
                self._reaches[index] = key_r
        self.outputs["Reaches"].set_values(self._reaches.tolist(), element_names=(self.outputs["Reaches"],))

    @staticmethod
    def prepare_soil_list(soil_list):
        """
        Prepares the soil list.

        Args:
            soil_list: The file path for the soil list.

        Returns:
            Nothing.
        """
        with open(soil_list, "w") as f:
            # noinspection SpellCheckingInspection
            f.write("key,depth,Ksat,Phi,alpha,n,m,Corg,residual_wetness")

    # noinspection DuplicatedCode
    def prepare_substance_list(self, substance_list_file):
        """
        Prepares the substance list.

        Args:
            substance_list_file: The file path for the substance list.

        Returns: Nothing.
        """
        with open(substance_list_file, "w") as f:
            # noinspection SpellCheckingInspection
            f.write("key,molarmass,DT50sw,DT50sed,KOC,Temp0,Q10,plantuptake,QFAC\n")
            # noinspection SpellCheckingInspection
            f.write(
                f"CMP_A,{self.inputs['MolarMass'].read().values},{self.inputs['DT50sw'].read().values},"
                f"{self.inputs['DT50sed'].read().values},{self.inputs['KOC'].read().values},"
                f"{self.inputs['Temp0'].read().values},{self.inputs['Q10'].read().values},"
                f"{self.inputs['PlantUptake'].read().values},{self.inputs['QFac'].read().values}\n"
            )

    def run_project(self, processing_path, project_name):
        """
        Runs the project.

        Args:
            processing_path: The working directory for the module.
            project_name: The name of the project.

        Returns:
            Nothing.
        """
        module_path = os.path.join(os.path.dirname(__file__), "module", "bin")
        python = os.path.join(module_path, "python", "python.exe")
        script = os.path.join(module_path, "main.py")
        # noinspection SpellCheckingInspection
        base.run_process(
            (python, script, "--folder", processing_path, "--runlist", project_name, "--key", "None"),
            processing_path,
            self.default_observer,
            {"PATH": ""}
        )

    def prepare_drift_deposition(self, spray_drift_list):
        """
        Prepares the drift deposition.

        Args:
            spray_drift_list: The file path for the drift deposition.

        Returns:
            Nothing.
        """
        deposition = self.inputs["DriftDeposition"].read()
        reaches_drift = deposition.element_names[1].get_values()
        begin = datetime.datetime.combine(self.inputs["Begin"].read().values, datetime.time())
        with open(spray_drift_list, "w") as f:
            f.write("key,substance,time,rate\n")
            deposition_events = np.nonzero(deposition.values)
            for i in range(len(deposition_events[0])):
                time_stamp = datetime.datetime.strftime(
                    begin + datetime.timedelta(int(deposition_events[0][i])), '%Y-%m-%dT12:00')
                f.write(
                    f"r{reaches_drift[deposition_events[1][i]]},CMP_A,{time_stamp},"
                    f"{format(deposition.values[(deposition_events[0][i], deposition_events[1][i])], 'f')}\n"
                )

    def prepare_time_series(self, time_series):
        """
        Prepares the hydrological time series.

        Args:
            time_series: The file path for the hydrological time series.

        Returns:
            Nothing.
        """
        os.mkdir(time_series)
        inflow_reaches = self._inputs["InflowReaches"].read().values
        number_hours = self._inputs["TimeSeries"].describe()["shape"][0]
        simulation_start = datetime.datetime.combine(self._inputs["Begin"].read().values, datetime.time())
        for r, reach in enumerate(inflow_reaches):
            inflows = self._inputs["TimeSeries"].read(slices=(slice(number_hours), r)).values
            with open(os.path.join(time_series, f"r{reach}.csv"), "w") as f:
                # noinspection SpellCheckingInspection
                f.write("key,time,flow,conc\n")
                for t, record in enumerate(inflows):
                    f.write(
                        f"r{reach},{(simulation_start + datetime.timedelta(hours=t)).strftime('%Y-%m-%dT%H:%M')},"
                        f"{record},0\n"
                    )

    def read_outputs(self, reaches_file):
        """
        Reads the module outputs into the Landscape Model.

        Args:
            reaches_file: The file path of the module's output file.

        Returns:
            Nothing.
        """
        begin = self.inputs["Begin"].read().values
        begin_date_time = datetime.datetime.combine(begin, datetime.time(1))
        number_time_steps = ((self.inputs["End"].read().values - begin).days + 1) * 24
        self.outputs["PEC_SW"].set_values(
            np.ndarray,
            shape=(number_time_steps, self._reaches.shape[0]),
            chunks=(min(65536, number_time_steps), 1),
            element_names=(None, self.outputs["Reaches"]),
            offset=(begin_date_time, None)
        )
        with open(reaches_file) as f:
            line = f.readline()
            while line:
                line = f.readline()
                cols = line.split(",")
                if len(cols) > 1:
                    pec_sw = np.asarray([float(cols[12])])
                    if pec_sw > 0:
                        key = int(cols[0][1:])
                        time = datetime.datetime.strptime(cols[1], "%Y-%m-%dT%H:%M")
                        x = int(np.where(self._reaches == key)[0])
                        t = int((time - begin_date_time).total_seconds() / 3600)
                        self.outputs["PEC_SW"].set_values(pec_sw, slices=(t, x), create=False)
