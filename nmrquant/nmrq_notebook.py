import io
import logging
from pathlib import Path
import os

import ipywidgets as widgets
from IPython.display import display
import pandas as pd

from rmnq_calculator import Quantifier
import nmrquant.nmrq_logger

mod_logger = logging.getLogger("RMNQ_logger.notebook")


class Rnb:
    """Class to control RMNQ notebook interface"""

    def __init__(self, verbose=False):

        self.quantifier = Quantifier(None, verbose)

        self.home = Path(os.getcwd())
        self.run_dir = None

        # Initialize child logger for class instances
        self.logger = logging.getLogger("RMNQ_logger.notebook.Rnb")
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

        self.upload_datafile_btn = widgets.FileUpload(
            accept='',  # Accepted file extension e.g. '.txt', '.pdf', 'image/*', 'image/*,.pdf'
            multiple=False,  # True to accept multiple files upload else False
            description="Upload datafile",
            style=widgetstyle)

        self.upload_database_btn = widgets.FileUpload(
            accept='',
            multiple=False,
            description="Upload database",
            style=widgetstyle
        )

        self.upload_template_btn = widgets.FileUpload(
            accept='',
            multiple=False,
            description="Upload template",
            style=widgetstyle
        )
        self.text_box = widgets.Text(value='', description='Run name:')

        self.tsp_btn = widgets.Text(value='', description='TSP concentration:', disabled=True,
                                    style=widgetstyle)

        self.dilution_text = widgets.Text(value='', description='Dilution factor:', style=widgetstyle)

        self.submit_btn = widgets.Button(description='Submit data', disabled=False,
                                         button_style='', tooltip='Click to submit selection',
                                         icon='', style=widgetstyle)

        self.calculate_btn = widgets.Button(description='Calculate',
                                            disabled=False, button_style='',
                                            tooltip='Click to calculate and export',
                                            icon='', style=widgetstyle)

        self.plots_btn = widgets.Button(description='Make plots',
                                        disabled=False, button_style='',
                                        tooltip='Click to generate plots', icon='',
                                        style=widgetstyle)

        self.generate_metadata_btn = widgets.Button(description='Generate Template',
                                                    disabled=False, button_style='',
                                                    tooltip='Click to generate template in parent folder',
                                                    icon='', style=widgetstyle)

        self.export_mean_checkbox = widgets.Checkbox(value=False, description="Mean export",
                                                     disabled=False, style=widgetstyle)

        self.plot_choice_dropdown = widgets.SelectMultiple(options=["individual_histogram",
                                                                    "meaned_histogram",
                                                                    "individual_lineplot",
                                                                    "summary_lineplot"],
                                                           value=("individual_histogram", "individual_histogram"),
                                                           description="Choose plot(s) to create",
                                                           disabled=False, style=widgetstyle)

    def reset(self, verbose):
        """Function to reset the object in notebook
        (only for notebook use because otherwise cell refresh
        doesn't reinitialize the object)"""
        os.chdir(self.home)
        self.__init__(verbose)

    # noinspection PyTypeChecker
    def make_gui(self):

        display(self.upload_datafile_btn,
                self.upload_database_btn,
                self.upload_template_btn,
                self.submit_btn,
                self.export_mean_checkbox,
                self.text_box,
                self.dilution_text,
                self.tsp_btn,
                self.generate_metadata_btn,
                self.calculate_btn,
                self.plot_choice_dropdown,
                self.plots_btn)

    def get_data_from_upload_btn(self, button):
        """
        :return:
        :rtype:
        """

        # Récupération des datas mis en ligne par le bouton upload
        try:
            data = next(iter(button.value))
        except StopIteration:
            return f"No file loaded in {button}"

        data_content = button.value[data]['content']
        with open('myfile', 'wb') as f:
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

    def generate_template(self, event):
        if self.quantifier.data is None:
            self.quantifier.get_data(self.get_data_from_upload_btn(self.upload_datafile_btn))

        self.quantifier.generate_metadata(".")

        self.logger.info(
            "Template has been created. Check parent folder for RMNQ_Template.xlsx")

    def initialize_data_vars(self, event):

        self.logger.debug("Initializing datafile")
        if self.quantifier.data is None:
            self.quantifier.get_data(self.get_data_from_upload_btn(self.upload_datafile_btn))
        if self.quantifier.use_tsp:
            self.logger.info("External calibration detected. Please enter TSP concentration")
            self.tsp_btn.disabled = False
        self.logger.debug("Initializing database")
        self.quantifier.get_db(self.get_data_from_upload_btn(self.upload_database_btn))
        self.logger.debug("Initializing template")
        self.quantifier.import_md(self.get_data_from_upload_btn(self.upload_template_btn))
        self.logger.debug("Merging template and datafile")
        self.quantifier.merge_md_data()

        return self.logger.info('Data variables initialized')

    def process_data(self, event):

        # Make target directory
        self.run_dir = self.home / self.text_box.value
        self.run_dir.mkdir()
        os.chdir(self.run_dir)

        # Get dilution factor and prepare data for calculations
        self.quantifier.dilution_factor = float(self.dilution_text.value)
        self.quantifier.clean_cols()
        self.quantifier.prep_db()

        # Check type of calibration and if TSP concentration should be used
        if self.quantifier.use_tsp:
            try:
                self.quantifier.calculate_concentrations(float(self.tsp_btn.value))
            except ValueError:
                self.logger.error("TSP concentration must be a number")
        else:
            self.quantifier.calculate_concentrations()
        if self.export_mean_checkbox.value:
            self.quantifier.get_mean()

        self.quantifier.export_data(".", self.text_box.value,
                                    export_mean=self.export_mean_checkbox.value)

    def build_plots(self, event):

        self.quantifier.prep_plots()
        cwd = Path(os.getcwd())

        if "individual_histogram" in self.plot_choice_dropdown.value:
            self.logger.info("Building Individual Histograms...")
            indhist = cwd / 'Histograms_Individual'
            indhist.mkdir()
            os.chdir(indhist)

            for metabolite in self.quantifier.metabolites:
                self.quantifier.make_hist(metabolite, mean=False)

            os.chdir(cwd)

        if "meaned_histogram" in self.plot_choice_dropdown.value:
            self.logger.info("Building Meaned Histograms...")
            meanhist = cwd / 'Histograms_Meaned'
            meanhist.mkdir()
            os.chdir(meanhist)

            for metabolite in self.quantifier.metabolites:
                self.quantifier.make_hist(metabolite, mean=True)

            os.chdir(cwd)

        if "individual_lineplot" in self.plot_choice_dropdown.value:
            self.logger.info("Building Individual Lineplots...")
            indline = cwd / "Lineplots_Individual"
            indline.mkdir()
            os.chdir(indline)

            for metabolite in self.quantifier.metabolites:
                self.quantifier.make_lineplot(metabolite, "individual")

            os.chdir(cwd)

        if "summary_lineplot" in self.plot_choice_dropdown.value:
            self.logger.info("Building Summary Lineplots...")
            sumline = cwd / "Lineplots_Summary"
            sumline.mkdir()
            os.chdir(sumline)

            for metabolite in self.quantifier.metabolites:
                self.quantifier.make_lineplot(metabolite, "summary")

            os.chdir(cwd)

    def load_events(self):

        self.generate_metadata_btn.on_click(self.generate_template)
        self.submit_btn.on_click(self.initialize_data_vars)
        self.calculate_btn.on_click(self.process_data)
        self.plots_btn.on_click(self.build_plots)
