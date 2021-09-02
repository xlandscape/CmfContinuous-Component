"""
Component for the CMF Continuous module.
"""
import datetime
import numpy as np
from osgeo import ogr
import os
import shutil
import base
import attrib


class CmfContinuous(base.Component):
    """
    The Landscape Model component encapsulating the CMF Continuous module.
    """
    # RELEASES
    VERSION = base.VersionCollection(
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

    def __init__(self, name, observer, store):
        super(CmfContinuous, self).__init__(name, observer, store)
        self._module = base.Module("Regulatory Catchment Model", "8 Aug 2018", r"\module\documentation")
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
                "ReachesDrift",
                (attrib.Class(np.ndarray, 1), attrib.Unit(None, 1), attrib.Scales("space/reach", 1)),
                self.default_observer,
                description="""The numeric identifiers for individual reaches (in the order of the `DriftDeposition` 
                input) that apply scenario-wide."""
            ),
            base.Input(
                "InflowReaches",
                (attrib.Class("list[int]", 1), attrib.Unit(None, 1), attrib.Scales("space/reach2", 1)),
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
                        "the number of simulated hours as spanned by the [Begin](#Begin) and [End](#end) input",
                        "the number of reaches included in the [Hydrography](#Hydrography) input"
                    ),
                    "chunks": "for fast retrieval of time series"
                }
            )
        ])

        self._reaches = None
        return

    def run(self):
        """
        Runs the component.
        :return: Nothing.
        """
        self.default_observer.write_message(2, "Component relies on insensible high precision of z-coordinate")
        project_name = "e1"
        processing_path = self.inputs["ProcessingPath"].read().values
        self.prepare_project(processing_path, project_name)
        self.prepare_drift_deposition(os.path.join(processing_path, project_name, "SprayDriftList.csv"))
        self.prepare_time_series(os.path.join(processing_path, project_name, "TimeSeries"))
        self.run_project(processing_path, project_name)
        self.read_outputs(os.path.join(processing_path, project_name, project_name + "_reaches.csv"))
        return

    def prepare_catchment_list(self, catchment_file):
        """
        Prepares the catchment list.
        :param catchment_file: The file path for the catchment list.
        :return: Nothing.
        """
        shutil.copyfile(self.inputs["Catchment"].read().values, catchment_file)
        return

    @staticmethod
    def prepare_cell_list(cell_list):
        """
        Prepares the hydrological cell list.
        :param cell_list: The file path for the hydrological cell list.
        :return: Nothing.
        """
        with open(cell_list, "w") as f:
            # noinspection SpellCheckingInspection
            f.write(
                "key,reach,reach_connection,adjacent_field,field_connection,x,y,z,latitude,gw_depth," +
                "residencetime_gw_river,residencetime_drainage_river,puddledepth,saturated_depth,evap_depth,area," +
                "deep_gw,deep_gw_rt,drainage_depth,drainage_suction_limit,drainage_t_ret,flowwdith_sw,slope_sw," +
                "nManning,hasDrainage,meteostation,rainstation,soil,plantmodel,unit_traveltime,soilwaterflux")
        return

    @staticmethod
    def prepare_climate(climate_list):
        """
        Prepares the weather input.
        :param climate_list: The file pah for the weather input
        :return: Nothing.
        """
        with open(climate_list, "w") as f:
            f.write("key,x,y,z,lat,lon")
        return

    @staticmethod
    def prepare_crop_coefficient_list(crop_coefficient_list):
        """
        Prepares the crop coefficient list.
        :param crop_coefficient_list: The file path for the crop coefficient list.
        :return: Nothing.
        """
        with open(crop_coefficient_list, "w") as f:
            # noinspection SpellCheckingInspection
            f.write(
                "key,GLAImin,GLAImax,GLAIharv,rootinit,rootmax,heightinit,heightmax,rpin,Dmin,Dstart,Dmax,Dharv," +
                "cform,dform,feddes1,feddes2,feddes3,feddes4,croptype,wintercrop")
        return

    @staticmethod
    def prepare_crop_management_list(crop_management_list):
        """
        Prepares the crop management list.
        :param crop_management_list: The file path for the crop management list.
        :return: Nothing.
        """
        with open(crop_management_list, "w") as f:
            f.write("key,date,task,description,value")
        return

    def prepare_project(self, processing_path, project_name):
        """
        Prepares the module project.
        :param processing_path: The file path where processing should be conducted.
        :param project_name: The name of the project
        :return: Nothing.
        """
        project_path = os.path.join(processing_path, project_name)
        os.makedirs(project_path)
        self.prepare_project_list(os.path.join(processing_path, project_name + ".csv"), project_name, processing_path)
        self.prepare_climate(os.path.join(project_path, "ClimateList.csv"))
        self.prepare_cell_list(os.path.join(project_path, "CellList.csv"))
        self.prepare_reach_list(os.path.join(project_path, "ReachList.csv"))
        self.prepare_soil_list(os.path.join(project_path, "SoilList.csv"))
        self.prepare_substance_list(os.path.join(project_path, "SubstanceList.csv"))
        self.prepare_crop_coefficient_list(os.path.join(project_path, "CropCoefficientList.csv"))
        self.prepare_crop_management_list(os.path.join(project_path, "CropManagementList.csv"))
        self.prepare_catchment_list(os.path.join(project_path, "CatchmentList.csv"))
        return

    def prepare_project_list(self, project_list_file, project_name, processing_path):
        """
        Prepares the project list.
        :param project_list_file: The file path for the project list.
        :param project_name: The name of the project.
        :param processing_path: The file path where processing should be conducted.
        :return: Nothing.
        """
        with open(project_list_file, "w") as f:
            # noinspection SpellCheckingInspection
            f.write(
                "key,fpath,database,runtype,catchment_separation,begin,end,separate_solver,threads,solvertype," +
                "solutesolvertype,chunksize,substance,efate,drift,timestep,simulation,preprocessing,postprocessing\n" +
                "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}".format(
                    project_name,  # key
                    processing_path,  # fpath
                    "csv",  # database
                    "inStream",  # runtype
                    "FALSE",  # catchment_separation
                    self.inputs["Begin"].read().values.strftime("%Y-%m-%dT%H:%M"),  # begin
                    self.inputs["End"].read().values.strftime("%Y-%m-%dT%H:%M"),  # end
                    "FALSE",  # separate_solver
                    self.inputs["Threads"].read().values,  # threads
                    self.inputs["SolverType"].read().values,  # solvertype
                    "None",  # solutesolvertype
                    "0",  # chunksize
                    "CMP_A",  # substance
                    "steps1234",  # efate
                    "xdrift",  # drift
                    "hour",  # timestep
                    "TRUE",  # simulation
                    "FALSE",  # preprocessing
                    "FALSE"  # prostprocessing
                ))
        return

    def prepare_reach_list(self, reach_list_file):
        """
        Prepares the reaches list.
        :param reach_list_file: The file path for the reaches list.
        :return: Nothing.
        """
        hydrography = self.inputs["Hydrography"].read().values
        driver = ogr.GetDriverByName("ESRI Shapefile")
        data_source = driver.Open(hydrography, 0)
        layer = data_source.GetLayer()
        self._reaches = np.zeros((layer.GetFeatureCount(),), np.int)
        with open(reach_list_file, "w") as f:
            # noinspection SpellCheckingInspection
            f.write(
                "key,x,y,z,downstream,initial_depth,manning_n,bankslope,bottomwidth,floodplainslope,shape,dens," +
                "porosity,oc,depth_sed,depth_sed_deep\n")
            for index, feature in enumerate(layer):
                key_r = feature.GetField("key")
                geom = feature.GetGeometryRef()
                coord = geom.GetPoint(0)
                downstream = feature.GetField("downstream")
                f.write("r" + str(key_r) + ",")
                f.write(str(round(coord[0], 2)) + ",")  # x
                f.write(str(round(coord[1], 2)) + ",")  # y
                f.write(str(round(coord[2], 8)) + ",")  # z
                f.write(("" if downstream == "Outlet" else "r") + downstream + ',')
                f.write(str(feature.GetField("initial_de")) + ",")
                f.write(str(feature.GetField("manning_n")) + ",")
                # noinspection SpellCheckingInspection
                f.write(str(feature.GetField("bankslope")) + ",")
                f.write(str(feature.GetField("width")) + ",")
                f.write("200,")  # floodplain
                f.write(feature.GetField("shape_1") + ",")
                f.write(str(feature.GetField("dens")) + ",")
                f.write(str(feature.GetField("porosity")) + ",")
                f.write(str(feature.GetField("oc")) + ",")
                f.write(str(feature.GetField("depth_sed")) + ",")
                f.write(str(feature.GetField("depth_sed_")) + "\n")
                self._reaches[index] = key_r
        self.outputs["Reaches"].set_values(self._reaches.tolist())
        return

    @staticmethod
    def prepare_soil_list(soil_list):
        """
        Prepares the soil list.
        :param soil_list: The file path for the soil list.
        :return: Nothing.
        """
        with open(soil_list, "w") as f:
            # noinspection SpellCheckingInspection
            f.write("key,depth,Ksat,Phi,alpha,n,m,Corg,residual_wetness")
        return

    def prepare_substance_list(self, substance_list_file):
        """
        Prepares the substance list.
        :param substance_list_file: The file path for the substance list.
        :return: Nothing.
        """
        with open(substance_list_file, "w") as f:
            # noinspection SpellCheckingInspection
            f.write("key,molarmass,DT50sw,DT50sed,KOC,Temp0,Q10,plantuptake,QFAC\n")
            # noinspection SpellCheckingInspection
            f.write("CMP_A,{},{},{},{},{},{},{},{}\n".format(
                self.inputs["MolarMass"].read().values,
                self.inputs["DT50sw"].read().values,
                self.inputs["DT50sed"].read().values,
                self.inputs["KOC"].read().values,
                self.inputs["Temp0"].read().values,
                self.inputs["Q10"].read().values,
                self.inputs["PlantUptake"].read().values,
                self.inputs["QFac"].read().values
            ))
        return

    def run_project(self, processing_path, project_name):
        """
        Runs the project
        :param processing_path: The working directory for the module.
        :param project_name: The name of the project.
        :return: Nothing.
        """
        module_path = os.path.join(os.path.dirname(__file__), "module", "bin")
        python = os.path.join(module_path, "python", "python.exe")
        script = os.path.join(module_path, "main.py")
        # noinspection SpellCheckingInspection
        base.run_process(
            (python, script, "--folder", processing_path, "--runlist", project_name, "--key", "None"),
            None,
            self.default_observer,
            {"PATH": ""}
        )
        return

    def prepare_drift_deposition(self, spray_drift_list):
        """
        Prepares the drift deposition.
        :param spray_drift_list: The file path for the drift deposition.
        :return: Nothing.
        """
        deposition = self.inputs["DriftDeposition"].read().values
        begin = datetime.datetime.combine(self.inputs["Begin"].read().values, datetime.time())
        reaches_drift = self.inputs["ReachesDrift"].read().values
        with open(spray_drift_list, "w") as f:
            f.write("key,substance,time,rate\n")
            deposition_events = np.nonzero(deposition)
            for i in range(len(deposition_events[0])):
                f.write(
                    "r{},{},{},{:f}\n".format(
                        reaches_drift[deposition_events[1][i]],
                        "CMP_A",
                        datetime.datetime.strftime(
                            begin + datetime.timedelta(int(deposition_events[0][i])), "%Y-%m-%dT12:00"),
                        deposition[(deposition_events[0][i], deposition_events[1][i])]
                    )
                )
        return

    def prepare_time_series(self, time_series):
        """
        Prepares the hydrological time series.
        :param time_series: The file path for the hydrological time series.
        :return: Nothing.
        """
        os.mkdir(time_series)
        inflow_reaches = self._inputs["InflowReaches"].read().values
        number_hours = self._inputs["TimeSeries"].describe()["shape"][0]
        simulation_start = datetime.datetime.combine(self._inputs["Begin"].read().values, datetime.time(0))
        for r, reach in enumerate(inflow_reaches):
            inflows = self._inputs["TimeSeries"].read(slices=(slice(number_hours), r)).values
            with open(os.path.join(time_series, "r" + str(reach) + ".csv"), "w") as f:
                # noinspection SpellCheckingInspection
                f.write("key,time,flow,conc\n")
                for t, record in enumerate(inflows):
                    f.write("r{},{},{},0\n".format(
                        reach, (simulation_start + datetime.timedelta(hours=t)).strftime("%Y-%m-%dT%H:%M"), record))
        return

    def read_outputs(self, reaches_file):
        """
        Reads the module outputs into the Landscape Model.
        :param reaches_file: The file path of the module's output file.
        :return: Nothing.
        """
        begin = self.inputs["Begin"].read().values
        begin_date_time = datetime.datetime.combine(begin, datetime.time(1))
        number_time_steps = ((self.inputs["End"].read().values - begin).days + 1) * 24
        self.outputs["PEC_SW"].set_values(
            np.ndarray, shape=(number_time_steps, self._reaches.shape[0]), chunks=(min(65536, number_time_steps), 1))
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
        return
