.. NmrQuant documentation master file, created by
   sphinx-quickstart on Mon Mar 22 10:25:56 2021.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to NmrQuant's documentation!
====================================

**NMRQuant is a software for the quantification of metabolites from 1D Proton NMR experiments**.
It takes as input integrated areas from spectra and proton counts from a database from excel and
csv files. It can be used with either internal or external calibration, using a standard molecule (usually d4-TSP).
It outputs an excel file containing the calculated concentrations, and svg files containing plots that help
with the visualisation and interpretation of the data.

It is one of the routine tools used on the `MetaToul platform <https://www6.toulouse.inrae.fr/metatoul>`_.

The code is open-source, and available on Github under a GPLv3 license.

The documentation relative to NMRQuant's usage can be found on `ReadTheDocs <https://nmrquant.readthedocs.io/>`_.

It can be used from a command line interface or through an interactive jupyter notebook GUI. The notebook can be
downloaded from the `GitHub page <https://github.com/llegregam/NmrQuant>`_.

.. rubric:: Key Features

* **Calculation of metabolite concentrations from 1D H+ NMR integrated data**
* **Creation of figures (lineplots and barplots) that help with interpretation**


.. toctree::
   :maxdepth: 2
   :caption: Usage:

   quickstart.rst
   inputs.rst
   usage.rst

.. toctree::
   :maxdepth: 2
   :caption: References:

   library_doc.rst
   faq.rst


* :ref:`search`
