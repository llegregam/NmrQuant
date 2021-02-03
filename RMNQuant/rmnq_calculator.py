"""Module containing the main Data Analyzer"""
import logging
from datetime import datetime

import numpy as np
import pandas as pd
import seaborn as sns

from utilities import read_data, is_empty, append_value

mod_logger = logging.getLogger("RMNQ_logger.calculator")


class Quantifier:
    """
    RMNQ main class to quantify and visualize data
    """

    def __init__(self, dilution_factor, verbose=False):

        self.verbose = verbose

        # Initialize child logger for class instances
        self.logger = logging.getLogger(f"RMNQ_logger.calculator.{self}")
        # fh = logging.FileHandler(f"{self.run_name}.log")
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)

        if verbose:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.INFO)

        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

        self.data = None
        self.mdata = None
        self.database = None
        self.metadata = None
        self.cor_data = None
        self.calc_data = None
        self.conc_data = None
        self.mean_data = None
        self.std_data = None
        self.ind_hist_data = None
        self.mean_hist_data = None

        self.metabolites = []
        self.conditions = []
        self.time_points = []

        self.proton_dict = {}

        self.spectrum_count = 0
        self.dilution_factor = dilution_factor

    def display(self, *args):
        """
        Display different attribute values (for debugging purposes)

        :param args: list of attribute values to return
        :return: attribute value
        """

        if "database" in args:
            try:
                return self.database
            except AttributeError:
                self.logger.error("The database is not loaded."
                                  " Please load and try again")

        if "proton_dict" in args:
            try:
                return self.proton_dict
            except AttributeError:
                self.logger.error("The proton dictionary is not loaded. "
                                  "Please load and try again")

        if "data" in args:
            try:
                return f"Data: {print(self.data)}"
            except AttributeError:
                self.logger.error("Data not loaded. Please load and try again")

        if "merge_data" in args:
            try:
                return f"Merged Data: {print(self.mdata)}"
            except AttributeError:
                self.logger.error("Data not merged. Please merge and try again")

        if "dilution_factor" in args:
            try:
                return f"Dilution factor: {self.dilution_factor}"
            except AttributeError:
                self.logger.error("No dilution factor registered")

        elif is_empty(args):
            self.logger.error("No attribute to check. Please enter"
                              "the attribute")

        else:
            self.logger.error(f"The attributes: {args} do not exist")

    def get_data(self, data_path, excel_sheet=0):
        """Get data from text or excel file"""

        try:
            self.data = read_data(data_path, excel_sheet)

        except TypeError as tperr:
            self.logger.error(f"Error while reading data:{tperr}")

        self.data.drop("TSP", axis=1, inplace=True)

        self.spectrum_count = self.data["# Spectrum#"].max()

        self.logger.info("Data has been loaded")

    def get_db(self, database_path):
        """Get database from csv file"""

        try:
            self.database = read_data(database_path)

        except TypeError as tperr:
            self.logger.error(f"Error while reading data:{tperr}")

        try:
            self.database.sort_values(by="Metabolite", inplace=True)

            self.database["Heq"] = self.database["Heq"].apply(
                lambda x: x.replace(',', '.'))

            self.database["Heq"] = pd.to_numeric(self.database["Heq"])

            for _, met, H in self.database[["Metabolite", "Heq"]].itertuples():
                self.proton_dict.update({met: H})

        except KeyError as key:
            self.logger.error('DataFrame error, are you sure you imported the right file? '
                              f'Error: {key}')

        except Exception as e:
            self.logger.error(f'Unexpected error: {e}')

        else:
            self.logger.info("Database has been loaded")

    def generate_metadata(self, path):
        """Generate template in excel format"""

        self.logger.info("Generating Template...")

        md = pd.DataFrame(columns=["Conditions", "Time_Points", "Replicates"])
        md["# Spectrum#"] = range(1, self.spectrum_count)
        md.Conditions = ""
        md.Time_Points = ""
        md.Replicates = ""

        md.to_excel(r'{}/RMNQ_Template.xlsx'.format(path), index=False)

        self.logger.info("Template generated")

    def import_md(self, path):
        """Import metadata file after modification"""

        self.logger.info("Reading metadata...")

        self.metadata = read_data(path)

        self.conditions = self.metadata["Conditions"].unique()
        self.time_points = self.metadata["Time_Points"].unique()

        self.logger.info("Metadata has been loaded")

    def merge_md_data(self):
        """Merge user-defined metadata with dataset"""

        self.logger.info("Merging...")

        self.mdata = self.metadata.merge(self.data, on="# Spectrum#")
        self.mdata.set_index(["Conditions", "Time_Points",
                              "Replicates", "# Spectrum#"], inplace=True)
        self.mdata.replace(0, np.nan, inplace=True)

        self.logger.info("Merge done!")

    def clean_cols(self):
        """Sum up double metabolite columns"""

        self.logger.info("Cleaning up columns...")

        # Get rid of columns containing + sign because only
        # useful to calculate other cols (ex: LEU+ILE)
        cols = [c for c in self.mdata.columns if "+" not in c]
        self.mdata = self.mdata[cols]
        del cols  # cleanup

        # Sort index so that numbered metabolites are together
        # which helps with the n_counting
        self.cor_data = self.mdata
        self.cor_data.sort_index(axis=1, inplace=True)

        self.logger.debug(f"Beginning cor_data = {self.cor_data}")

        tmp_dict = {}
        # Get indices where metabolites are double
        for ind, col in enumerate(self.cor_data.columns):

            split = col.split(" ")

            if len(split) > 1:  # Else there is no double met

                append_value(tmp_dict, split[0], ind)

        self.logger.debug(f"Temp dict = {tmp_dict}")

        ncount = 0  # Counter for substracting from indices
        if is_empty(tmp_dict):
            return self.logger.info("No double metabolites in data set. Columns are clean")

        else:
            for key, val in tmp_dict.items():
                dropval = [x - ncount for x in val]  # Real indices after drops
                self.logger.debug(f"Dropvals = {dropval}")

                self.cor_data[key] = self.cor_data.iloc[:, dropval[0]] \
                                     + self.cor_data.iloc[:, dropval[1]]

                self.cor_data.drop(self.cor_data.columns[dropval],
                                   axis=1, inplace=True)

                ncount += 2  # Not 1 because the new cols are added at the end of df

            self.logger.debug(f"End cor_data = {self.cor_data}")

        self.metabolites = list(self.cor_data.columns[1:])

        return self.logger.info("Data columns have been cleaned")

    def prep_db(self):
        """Prepare database for concentration calculations"""

        tmp_dict = {}
        removed_values = []

        for key, val in self.proton_dict.items():

            split = key.split(" ")

            if len(split) > 1:
                append_value(tmp_dict, split[0], val)
                removed_values.append(key)

        self.logger.debug(f"Temp dict = {tmp_dict}")
        self.logger.debug(f"Removed values = {removed_values}")

        if is_empty(tmp_dict):
            return self.logger.info(
                "No double metabolites in data set. Database entries are clean")

        else:
            self.logger.debug(tmp_dict)
            tmp_dict = {key: sum(vals) for key, vals in tmp_dict.items()}

            self.logger.debug(f"Summed temp dict = {tmp_dict}")
            self.logger.debug(f"Proton dict before del = {self.proton_dict}")

            for key in removed_values:
                del self.proton_dict[key]

            self.proton_dict = self.proton_dict | tmp_dict

            self.logger.debug(f"Proton dict after del = {self.proton_dict}")

        return self.logger.info("Database ready!")

    def calculate_concentrations(self):
        """Calculate concentrations using number of
        protons and dilution factor"""

        self.logger.info("Calculating concentrations...")

        self.cor_data.fillna(0, inplace=True)
        self.conc_data = pd.DataFrame(columns=self.cor_data.columns)
        self.conc_data = self.cor_data.apply(lambda x: (x * self.dilution_factor))

        self.logger.debug(f"Proton dict before del = {self.proton_dict}")

        for col in self.conc_data.columns:

            for key, val in self.proton_dict.items():
                if key == col:
                    proton_val = val
                    break

            self.conc_data[col] = self.conc_data[col].apply(lambda x: x / proton_val)

        return self.logger.info("Concentrations have been calculated")

    def get_mean(self):
        """Make dataframe meaned on replicates"""

        self.mean_data = self.conc_data.droplevel("# Spectrum#")

        self.mean_data = self.conc_data.groupby(
            ["Conditions", "Time_Points"]).mean()
        self.std_data = self.conc_data.groupby(
            ["Conditions", "Time_Points"]).std()

        return self.logger.info("Means and standard deviations have been calculated")

    def export_data(self, destination, file_name='', fmt="excel", export_mean=False):
        """Export final data in desired format"""

        # Get current date & time
        date_time = datetime.now().strftime("%d%m%Y %Hh%Mmn")

        # Output to multi-page excel file
        if fmt == "excel":
            with pd.ExcelWriter(f"{destination}\{file_name + '_' + date_time}.xlsx") as writer:
                self.mdata.to_excel(writer, sheet_name='Raw Data')
                self.cor_data.to_excel(writer, sheet_name='Corrected Data')
                self.conc_data.to_excel(writer, sheet_name='Concentrations Data')

                if export_mean:
                    self.mean_data.to_excel(writer, sheet_name='Meaned Data')
                    self.std_data.to_excel(writer, sheet_name='Stds')

        return self.logger.info("Data Exported")

    ##Visualization part of the quantifier starts here

    def prep_plots(self):
        """Prepare data for plotting"""

        self.hist_data = self.conc_data.reset_index()
        self.ind_hist_data = self.hist_data
        self.mean_hist_data = self.hist_data

        self.ind_hist_data["ID"] = self.hist_data["Conditions"] + "_" + \
                                   self.hist_data["Time_Points"] + "_" + \
                                   self.hist_data["Replicates"].astype(str)

        self.mean_hist_data["ID"] = self.hist_data["Conditions"] + "_" + \
                                    self.hist_data["Time_Points"]

    def make_hist(self, metabolites, mean=False):
        """
        Make histograms with quantification data

        :param metabolites: Metabolites to plot
        :param mean: Should means with Stds be plotted or only individual data
        :return: Histogram
        """

        if mean is False:
            for metabolite in metabolites:
                sns.barplot(data=self.mean_hist_data, x="ID", y=metabolite)


        else:
            for metabolite in metabolites:
                sns.barplot(data=self.ind_hist_data, x="ID", y=metabolite)
