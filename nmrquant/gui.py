from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from calculator import Quantifier


class RmnqGui:

    def __init__(self):
        """Main window constructor"""

        self.root = Tk()
        self.root.title = "RMNQ quantification program"
        self.mainframe = ttk.Frame(self.root, padding="3")
        self.mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)

        self.quantifier = Quantifier(None, None)

        # Make the different buttons. They should be responsive to resizing of window. Starting with upload btns
        self.upload_data_button = Button(self.mainframe, text="Select Data File", command=self.upload_datafile)
        self.upload_data_button.grid(row=1, column=0, columnspan=2)

        self.upload_data_button = Button(self.mainframe, text="Select Database", command=self.upload_database)
        self.upload_data_button.grid(row=3, column=0, columnspan=2)

        self.upload_data_button = Button(self.mainframe, text="Select Template", command=self.upload_template)
        self.upload_data_button.grid(row=5, column=0, columnspan=2)

        # Make submit button
        self.submit_button = Button(self.mainframe, text="Submit", command=self.submit)
        self.submit_button.grid(row=5, column=5, columnspan=2)

        # Make entry point for dilution factor
        self.dil_fact = StringVar()
        self.dil_fact_entry = Entry(self.mainframe, width=35, borderwidth=5, textvariable=self.dil_fact)
        self.dil_fact_entry.grid(row=1, column=5, columnspan=3)
        self.dil_fact_entry.insert(0, "Enter dilution factor: ")

        # Make big Label for the logging of what is going on in the app
        self.logger = ttk.Label(self.mainframe)
        self.logger.grid(row=6, column=1, columnspan=5, sticky="s")
        self.logcontents = StringVar()
        self.logger['textvariable'] = self.logcontents

        self.root.mainloop()

    # Make commands for uploading the files
    def upload_datafile(self, event=None):
        filename = filedialog.askopenfilename()
        self.quantifier.get_data(filename)
        print('Selected:', filename)

    def upload_database(self, event=None):
        filename = filedialog.askopenfilename()
        self.quantifier.get_db(filename)
        print('Selected:', filename)

    def upload_template(self, event=None):
        filename = filedialog.askopenfilename()
        self.quantifier.import_md(filename)
        print('Selected:', filename)

    # Make command for submiting the files and dilution factor
    def submit(self, event=None):
        self.logcontents.set("Submit button has been pressed")
        self.quantifier.dilution_factor = self.dil_fact_entry.get()
        self.quantifier.merge_md_data()
        self.quantifier.clean_cols()
        self.quantifier.prep_db()
        self.quantifier.calculate_concentrations()
        self.quantifier.get_mean()




