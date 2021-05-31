import io
import logging
from pathlib import Path
import os

import ipywidgets as widgets
from IPython.display import display
import pandas as pd
import nmrquant.logger

from nmrquant.engine.calculator import Quantifier
from nmrquant.engine.visualizer import *

mod_logger = logging.getLogger("RMNQ_logger.ui.notebook")


class Rnb:
    """Class to control RMNQ notebook interface"""

    def __init__(self, verbose=False):

        self.quantifier = Quantifier(verbose)

        self.home = Path(os.getcwd())
        self.run_dir = None

        # Initialize child logger for class instances
        self.logger = logging.getLogger("RMNQ_logger.ui.notebook.Rnb")
        # fh = logging.FileHandler(f"{self.run_name}.log")
        handler = logging.StreamHandler()
        if verbose:
            handler.setLevel(logging.DEBUG)
        else:
            handler.setLevel(logging.INFO)
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s', "%Y-%m-%d %H:%M:%S")
        handler.setFormatter(formatter)
        if not self.logger.hasHandlers():
            self.logger.addHandler(handler)

        widgetstyle = {'description_width': 'initial'}

        self.display = True

        self.upload_datafile_btn = widgets.FileUpload(
            accept='',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
            multiple=False,  # True to accept multiple files upload else False
            description="Upload datafile",
            style=widgetstyle)

        self.upload_database_btn = widgets.FileUpload(
            accept='',
            multiple=False,
            description="Upload database",
            style=widgetstyle,
            disabled=True
        )

        self.upload_template_btn = widgets.FileUpload(
            accept='',
            multiple=False,
            description="Upload template",
            style=widgetstyle,
            disabled=True
        )
        self.run_text_box = widgets.Text(value='', description='Run name:', disabled=True)

        self.strd_btn = widgets.Text(value='', description='Strd concentration:', disabled=True,
                                     style=widgetstyle)

        self.dilution_text = widgets.Text(value='', description='Dilution factor:', style=widgetstyle, disabled=True)

        self.submit_btn = widgets.Button(description='Submit data', disabled=True,
                                         button_style='', tooltip='Click to submit selection',
                                         icon='', style=widgetstyle)

        self.calculate_btn = widgets.Button(description='Calculate',
                                            disabled=True, button_style='',
                                            tooltip='Click to calculate and export',
                                            icon='', style=widgetstyle)

        self.plots_btn = widgets.Button(description='Make plots',
                                        disabled=True, button_style='',
                                        tooltip='Click to generate plots', icon='',
                                        style=widgetstyle)

        self.generate_metadata_btn = widgets.Button(description='Generate Template',
                                                    disabled=True, button_style='',
                                                    tooltip='Click to generate template in parent folder',
                                                    icon='', style=widgetstyle)

        self.export_mean_checkbox = widgets.Checkbox(value=False, description="Mean export",
                                                     disabled=True, style=widgetstyle)

        self.plot_choice_dropdown = widgets.SelectMultiple(options=["individual_histogram",
                                                                    "meaned_histogram",
                                                                    "individual_lineplot",
                                                                    "summary_lineplot"],
                                                           value=("individual_histogram", "individual_histogram"),
                                                           description="Choose plot(s) to create",
                                                           disabled=True, style=widgetstyle)

    def reset(self, verbose):
        """Function to reset the object in notebook
        (only for notebook use because otherwise cell refresh
        doesn't reinitialize the object)"""
        os.chdir(self.home)
        self.__init__(verbose)

    # noinspection PyTypeChecker
    def make_gui(self):
        """Display the widgets and build the GUI"""
        display(self.upload_datafile_btn,
                self.upload_database_btn,
                self.upload_template_btn,
                self.submit_btn,
                self.export_mean_checkbox,
                self.run_text_box,
                self.dilution_text,
                self.strd_btn,
                self.generate_metadata_btn,
                self.calculate_btn,
                self.plot_choice_dropdown,
                self.plots_btn)

        self.upload_datafile_btn.observe(self._observe_upload_data)

    def get_data_from_upload_btn(self, button):
        """
        Get data stored in upload data button.
        :return: Input data
        :rtype: class: pandas.DataFrame
        """

        # Récupération des datas mis en ligne par le bouton upload
        try:
            data = next(iter(button.value))
        except StopIteration:
            return f"No file loaded in {button}"

        data_content = button.value[data]['content']
        with open('../myfile', 'wb') as f:
            f.write(data_content)
        # Entrons les datas dans un dataframe
        try:
            self.logger.debug(f"Reading file from {button.description} as excel")
            real_data = pd.read_excel(io.BytesIO(data_content))
        except Exception as e:
            self.logger.debug('There was a problem reading file')
            self.logger.debug(e)
            try:
                self.logger.info("Trying to load as csv")
                real_data = pd.read_csv(io.BytesIO(data_content), sep=";")
            except Exception as e:
                self.logger.error("There was a problem reading file")
                self.logger.error(e)
            else:
                return real_data
        else:
            return real_data

    def _observe_upload_data(self, change):
        """Observe the upload data button and enable widgets when data is uploaded"""

        self.generate_metadata_btn.disabled = False
        self.upload_database_btn.disabled = False
        self.upload_template_btn.disabled = False
        self.submit_btn.disabled = False

    def generate_template(self, event):
        """Generate template from input data spectrum count"""

        if self.quantifier.data is None:
            self.quantifier.get_data(self.get_data_from_upload_btn(self.upload_datafile_btn))

        self.quantifier.generate_metadata(".")

        self.logger.info(
            "Template has been created. Check parent folder for RMNQ_Template.xlsx")

    def _submit_button_click(self, event):
        """Submit button function that enables the rest of the widgets and finishes preparation of the different
        input files."""

        # Enable all the other widgets
        self.export_mean_checkbox.disabled = False
        self.run_text_box.disabled = False
        self.dilution_text.disabled = False
        self.calculate_btn.disabled = False
        self.plot_choice_dropdown.disabled = False
        self.plots_btn.disabled = False

        self.logger.debug("Initializing datafile")

        # Check if quantifier contains the data. If not, load it in from upload datafile button
        if self.quantifier.data is None:
            self.quantifier.get_data(self.get_data_from_upload_btn(self.upload_datafile_btn))

        # Check if standard should be used to calculate concentrations (internal or external calibration)
        if self.quantifier.use_strd:
            self.logger.info("External calibration detected. Please enter the concentration of standard")
            self.strd_btn.disabled = False

        # Finish initalizing data variables and data files
        self.logger.debug("Initializing database")
        self.quantifier.get_db(self.get_data_from_upload_btn(self.upload_database_btn))

        self.logger.debug("Initializing template")
        self.quantifier.import_md(self.get_data_from_upload_btn(self.upload_template_btn))

        self.logger.debug("Merging template and datafile")
        self.quantifier.merge_md_data()

        return self.logger.info('Data variables initialized')

    def process_data(self, event):
        """Make destination folder, clean data and calculate results"""

        # Make target directory
        self.run_dir = self.home / self.run_text_box.value
        self.run_dir.mkdir()
        os.chdir(self.run_dir)

        # Get dilution factor and prepare data for calculations
        self.quantifier.dilution_factor = float(self.dilution_text.value)
        self.quantifier.clean_cols()
        self.quantifier.prep_db()

        # Check type of calibration and if Strd concentration should be used
        if self.quantifier.use_strd:
            try:
                self.quantifier.calculate_concentrations(float(self.strd_btn.value))
            except ValueError:
                self.logger.error("Standard concentration must be a number")
        else:
            self.quantifier.calculate_concentrations()
        if self.export_mean_checkbox.value:
            self.quantifier.get_mean()

        self.quantifier.export_data(".", self.run_text_box.value,
                                    export_mean=self.export_mean_checkbox.value)

    def build_plots(self, event):
        """Control plot creation. Make destination folders and generate plots."""

        cwd = Path(os.getcwd())

        times = self.quantifier.conc_data.index.get_level_values("Time_Points").unique()
        replicates = self.quantifier.conc_data.index.get_level_values("Replicates").unique()
        #conditions = self.quantifier.conc_data.index.get_level_values("Conditions").unique()

        if "individual_histogram" in self.plot_choice_dropdown.value:
            if len(times) > 1:
                self.logger.error("Too many time points for individual histograms. Please generate line plots instead")
            else:
                self.logger.info("Building Individual Histograms...")
                indhist = cwd / 'Histograms_Individual'
                indhist.mkdir()
                os.chdir(indhist)

                for metabolite in self.quantifier.metabolites:
                    if len(replicates) > 1:
                        plot = IndHistB(self.quantifier.conc_data, metabolite, self.display)
                    else:
                        plot = IndHistA(self.quantifier.conc_data, metabolite, self.display)
                    fig = plot()
                    fig.savefig(f"{metabolite}.svg", format='svg')
                self.logger.info("Individual histograms have been generated")
            os.chdir(cwd)


        if "meaned_histogram" in self.plot_choice_dropdown.value:
            self.logger.info("Building Meaned Histograms...")
            if len(times) > 1:
                self.logger.error("Too many time points for individual histograms. Please generate line plots instead")
            elif not hasattr(self.quantifier, "mean_data") or not hasattr(self.quantifier, "std_data"):
                self.logger.error("Means and SD data missing. Please select 'export mean' option to generate required"
                                  "data")
            else:
                meanhist = cwd / 'Histograms_Meaned'
                meanhist.mkdir()
                os.chdir(meanhist)

                for metabolite in self.quantifier.metabolites:
                    plot = MultHistB(self.quantifier.mean_data, self.quantifier.std_data, metabolite, self.display)
                    fig = plot()
                    fig.savefig(f"{metabolite}.svg", format="svg")
                self.logger.info("Meaned histograms have been generated")
            os.chdir(cwd)

        if "individual_lineplot" in self.plot_choice_dropdown.value:
            self.logger.info("Building Individual Lineplots...")
            if len(times) == 1:
                self.logger.error("Not enough time points to generate kinetic plots. Please select a histogram "
                                  "representation instead")
            else:
                indline = cwd / "Lineplots_Individual"
                indline.mkdir()
                os.chdir(indline)

                for metabolite in self.quantifier.metabolites:
                    if (len(replicates) == 1) or "Replicates" not in self.quantifier.conc_data.index.names:
                        plot = NoRepIndLine(self.quantifier.conc_data, metabolite, self.display)
                        fig = plot()
                        fig.savefig(f"{metabolite}.svg", format="svg")
                    else:
                        plot = IndLine(self.quantifier.conc_data, metabolite, self.display)
                        figures = plot()
                        for (fname, fig) in figures:
                            fig.savefig(f"{fname}.svg", format="svg")
                self.logger.info("Individual lineplots have been generated")
            os.chdir(cwd)

        if "summary_lineplot" in self.plot_choice_dropdown.value:
            self.logger.info("Building Summary Lineplots...")
            if len(times) == 1:
                self.logger.error("Not enough time points to generate kinetic plots. Please select a histogram "
                                  "representation instead")
            else:

                sumline = cwd / "Lineplots_Summary"
                sumline.mkdir()
                os.chdir(sumline)

                if len(replicates) == 1 or "Replicates" not in self.quantifier.conc_data.index.names:
                    self.logger.warning(
                        "No replicates detected. Plots will still be generated but to remove the useless"
                        "error bars, please select 'individual_lineplot' instead")
                for metabolite in self.quantifier.metabolites:
                    plot = MeanLine(self.quantifier.conc_data, metabolite, self.display)
                    fig = plot()
                    fig.savefig(f"{metabolite}.svg", format="svg")
                self.logger.info("Summary lineplots have been generated")
            os.chdir(cwd)


        os.chdir(self.home)

    def load_events(self):
        """Load events for all the different buttons"""

        self.generate_metadata_btn.on_click(self.generate_template)
        self.submit_btn.on_click(self._submit_button_click)
        self.calculate_btn.on_click(self.process_data)
        self.plots_btn.on_click(self.build_plots)
