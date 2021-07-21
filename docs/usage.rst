Usage
=====

Jupyter Notebook interface
--------------------------

The first step is to use the buttons to upload the files into the notebook (or generate the template).

    1.  **Upload datafile**.
        This is always the first thing to do when you first launch the notebook. Use the "*Upload datafile*" button to
        select the data file. This will enable the other upload buttons.

    2. **Uplaod Database**.
       Use this button to upload the database file into the notebook.


    3. **Generate Template**
       Next, if needed, click the "*Generate Template*" button to create the Template in the folder containing the
       notebook file. Fill out the file with the experiment's metadata

    4. **Uplaod Template**
       Use this button to upload the template into the notebook.

Now that the different input files are loaded, you can choose if the means should be calculated for the run by clicking
or not on the *mean export* checkbox. Once this is done, fill out the run name (to name the end folder), the dilution
factor and the concentration in standard molecule (if calibration is external). Once this is done, press the "Calculate"
button to generate the results file. To visualize the data using the plotting module, finish by choosing the plots you
want from the multiple selection list, and click the "Make plots" button.

Command Line Interface
--------------------------

To process your data, type in a terminal:

.. code-block:: bash

    nmrquant [command line options]

Here after the available options with their full names are enumerated and detailed.

.. argparse::
   :module: nmrquant.ui.cli
   :func: parse_args
   :prog: nmrquant
   :nodescription:

NmrQuant proceeds automatically to the data processing and displays progress and important messages in the
standard output.
