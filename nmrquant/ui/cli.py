import argparse
import os
from pathlib import Path
import sys

from nmrquant.engine.calculator import Quantifier
from nmrquant.engine.visualizer import *


def parse_args():
    """
    Get user arguments from CLI input

    :return: class: 'Argument Parser'
    """
    parser = argparse.ArgumentParser(
        description="Software for 1D proton NMR quantification")

    parser.add_argument("datafile", type=str,
                        help="Path to data file to process")

    parser.add_argument("-d", "--database", type=str,
                        help="Path to proton database")
    parser.add_argument("-f", "--dilution_factor", type=float,
                        help="Dilution factor used to calculate concentrations")
    parser.add_argument("-t", "--template", type=str,
                        help="Path to template file. ")
    parser.add_argument("-k", "--make_template", type=str,
                        help="Input path to export template to")

    parser.add_argument('-b', '--barplot', choices=["individual", "meaned"], action="append",
                        type=str, help='Choose histogram to build. Enter "individual" or "meaned" ')
    parser.add_argument('-l', '--lineplot', choices=["individual", "summary"],
                        type=str, help='Choose lineplot to build. Enter "individual" or "summary" ')

    parser.add_argument('-m', '--mean', action='store_true',
                        help='Add if means and stds should be calculated on replicates')
    parser.add_argument('-c', '--tsp_concentration', type=float,
                        help='Add tsp concentration if calibration is external')

    parser.add_argument("-e", "--export", type=str, help="Name for exported file")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Add option for debug mode")

    return parser


def process(args):
    """
    Command Line Interface process of nmrquant

    :param args: Arguments passed by the parser
    :return: Excel file export message
    """

    cli_quant = Quantifier(verbose=args.verbose)
    for i, arg in enumerate(sys.argv):
        cli_quant.logger.debug(f"Argument {i} = {arg}")
    if hasattr(args, "k"):
        cli_quant.generate_metadata(args.make_template)
    else:
        destination = Path(args.datafile).parent
        # Get data
        cli_quant.get_data(fr"{args.datafile}")
        cli_quant.get_db((fr"{args.database}")
        cli_quant.import_md(fr'{args.template}')
        # Process data
        cli_quant.merge_md_data()
        cli_quant.clean_cols()
        cli_quant.prep_db()
        if cli_quant.use_strd:
            try:
                cli_quant.calculate_concentrations(args.tsp_concentration)
            except AttributeError:
                raise ("TSP concentration not referenced. Please add '-c' to arguments "
                       "followed by the TSP concentration")
        else:
            cli_quant.calculate_concentrations()
        # If means are needed then calculate
        if args.mean:
            cli_quant.get_mean()
            export_mean = True
        else:
            export_mean = False
        # Get name for exported excel file
        file_name = args.export
        cli_quant.export_data(file_name=file_name,
                              destination=destination,
                              export_mean=export_mean)

        cli_quant.logger.debug(f"Barplot args are: {args.histplot}")
        cli_viz = Vi
        if hasattr(args, "barplot"):

            if "meaned" in args.histplot:
                hist_path = destination / 'Histograms_Meaned'
                hist_path.mkdir()
                os.chdir(hist_path)

                for metabolite in cli_quant.metabolites:
                    cli_quant.make_hist(metabolite, mean=True)

            if "individual" in args.histplot:
                hist_path = destination / 'Histograms_Individual'
                hist_path.mkdir()
                os.chdir(hist_path)

                for metabolite in cli_quant.metabolites:
                    cli_quant.make_hist(metabolite, mean=False)

            os.chdir(destination)

        if hasattr(args, "lineplot"):
            cli_quant.prep_plots()

            if "individual" in args.lineplot:
                lineplot_path = destination / "Lineplots_Individual"
                lineplot_path.mkdir()
                os.chdir(lineplot_path)

                for metabolite in cli_quant.metabolites:
                    cli_quant.make_lineplot(metabolite, "individual")

            if "summary" in args.lineplot:
                lineplot_path = destination / "Lineplots_Summary"
                lineplot_path.mkdir()
                os.chdir(lineplot_path)

                for metabolite in cli_quant.metabolites:
                    cli_quant.make_lineplot(metabolite, "summary")

            os.chdir(destination)

        cli_quant.logger.info(f"Finished. Check {destination} ")


def start_cli():
    parser = parse_args()
    args = parser.parse_args()
    process(args)


start_cli()  # For testing
