import argparse

from rmnq_calculator import Quantifier


def parse_args():
    """
    Get user arguments from CLI input

    :return: class: 'Argument Parser'
    """
    parser = argparse.ArgumentParser(
        description="Software for 1D proton NMR quantification")

    parser.add_argument("destination", type=str,
                        help="Path where exports should happen")
    parser.add_argument("datafile", type=str,
                        help="Path to data file to process")
    parser.add_argument("database", type=str,
                        help="Path to proton database")
    parser.add_argument("dilution_factor", type=float,
                        help="Dilution factor used to calculate concentrations")
    parser.add_argument("-t", "--template", type=str, dest='',
                        help="Path to template file. ")
    parser.add_argument("-k", "--make_template", type=str, dest='',
                        help="Input path to export template to")
    parser.add_argument('-m', '--mean', action='store_true',
                        help='Add if means and stds should be calculated on replicates')
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Add option for debug mode")

    return parser


def process(args):
    """
    Command Line Interface process of RMNQuant

    :param args: Arguments passed by the parser
    :return: Excel file export message
    """

    CLI_quant = Quantifier(args.dilution_factor, verbose=args.verbose)

    if hasattr(args, "k"):
        CLI_quant.generate_metadata(args.make_template)

    else:

        export_mean = False

        # Get data
        CLI_quant.get_data(r"{}".format(args.datafile))
        CLI_quant.get_db((r"{}".format(args.database)))
        CLI_quant.import_md(r'{}'.format(args.template))

        # Process data
        CLI_quant.merge_md_data()
        CLI_quant.clean_cols()
        CLI_quant.prep_db()
        CLI_quant.calculate_concentrations()

        #If means are needed then calculate
        if hasattr(args, 'm'):
            CLI_quant.get_mean()
            export_mean = True

        CLI_quant.export_data(destination=args.destination,
                          export_mean=export_mean)

        return CLI_quant.logger.info(f"Finished. Check {args.destination} "
                          "for final data file")


def start_cli():
    parser = parse_args()
    args = parser.parse_args()
    process(args)


start_cli()  # For testing
