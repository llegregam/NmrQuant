Inputs
======

The Data File
-------------

File structure
^^^^^^^^^^^^^^

The data accepted by NMRQuant should be passed in as an excel file (.xlsx), a comma-separated text file (.csv) or a
tabulation-separated text file (.tsv). The structure of the file must be as follows:

=========== =========== =========== ===========
# Spectrum# Metabolite1 Metabolite2 Metabolite3
=========== =========== =========== ===========
  1           xxx        xxx         xxx
  2           xxx        xxx         xxx
  3           xxx        xxx         xxx
  4           xxx        xxx         xxx
=========== =========== =========== ===========

The number of metabolites processed at a time has no limit. The important column here is
the first one: "# Spectrum#", as it will be responsible for linking the recorded values per
metabolite with the different times, conditions and replicates that will be given through
the metadata file (ref).

.. note:: The column header is case-sensitive! Since in most cases the spectrum data comes
          from spectra integrated using Bruker's TopSpin software and this is the column header
          used by their software, for practical reasons the same formalism was kept in NMRQuant.

Every other column must have as header the name of a metabolite, and the associated areas should be
given in each row. If a metabolite has more than one integrated area, **it should be given in two or
more columns and a number should be assigned to each of the column headers with an underscore between
the metabolite name and the number**. For example:

=========== =============== =============== ===============
# Spectrum# Phenylalanine_1 Phenylalanine_2 Phenylalanine_3
=========== =============== =============== ===============
  1           xxx             xxx             xxx
  2           xxx             xxx             xxx
  3           xxx             xxx             xxx
  4           xxx             xxx             xxx
=========== =============== =============== ===============

.. note:: The number of protons for each area group should be given in the database file using
          the same nomenclature as in the data file, including the spaces and numbers.

.. warning:: To calculate concentrations for a metabolite using multiple integration areas (as for phenylalanine in
             the example above), make sure that the proton count for each area is referenced in the database.

Calibration molecule input
^^^^^^^^^^^^^^^^^^^^^^^^^^

To calculate concentrations, NMRQ needs to know if the calibration is internal or external. To know this, it searches in
the data file for a column named "Strd" (for *Standard*). This column is added
in manually by the user, and must have at least in it's first row the number 1 (if the calibration is internal) or 9 (if
the calibration is external).
If the value is equal to 1, the Strd's concentration is not needed and the user does not need to input it in the notebook
or the Command-Line Interface (CLI). On the contrary, if the value is equal to 9, the user will have to give the TSP
concentration through the notebook or the CLI.


The Database File
-----------------

To calculate concentrations from 1D H NMR spectra areas, it is necessary to have the number of protons for each
integrated region (corresponding to an equivalent group of protons in a molecule). Consequently, it is necessary to pass
this information to NMRQuant through **an excel or csv file** containing these proton numbers for each metabolite we are
quantifying. The structure of the excel file should at least be as follows:

        ============== =====
          Metabolite    Heq
        ============== =====
        Formate          1
        Phenylalanine    5
        Tyrosine         2
        ============== =====

As always, the headers for each column are case-sensitive, as are the names of each metabolite which have to be exactly
the same as the ones used in the data file. The two columns shown above are the minimal requirements for NMRQ to
function. Good practices dictate that users also add a column with the different ppm positions of each region for
informational purposes. This is not a problem and will not interfere with the software's ability to read the file.

.. note:: For metabolites that are quantified using two or more regions, the formalism is to add a number **separated
          from the metabolite name by an underscore.** The same must be done for the metabolite names in the data file:

          ================== =====
            Metabolite        Heq
          ================== =====
           Formate            1
           Phenylalanine_1    3
           Phenylalanine_2    2
           Tyrosine           2
          ================== =====

.. note:: If there is no corresponding metabolite in the database file for a given metabolite in the datafile, RMNQ will
          notify you by adding *_Area* after the metabolite's name in the output file, and keep the areas in the
          final results. In this case, the software will also use the area values for plotting. This means that if the
          user uses an arbitrary name for an unknown integration area ("*unknown*" for example) it will still be plotted
          and put in the results.


The Template File
-----------------

Once the datafile is uploaded into the notebook or given in the command-line interface (CLI), the user can generate a
structured template file in which the Time Points, Conditions and Replicate numbers must be referenced. To do this, the
program reads the '# Spectrum#' field in the data file and generates the required number of rows for each spectrum with
the correct formalism for the headers.

.. warning:: Do not change the names of the columns in the generated template file as this will stop NMRQ from reading
             the file correctly!

The metadata given through the template file will then be used to separate the datas in groups for plotting.

.. note:: The Replicates column must number each individual sample of similar Times + Conditions from 1 to n (n being
          the last replicate). This will let the software mean the concentrations and also create the summary plots and
          meaned histograms with error bars.

