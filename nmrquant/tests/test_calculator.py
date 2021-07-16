"""Test suite for our calculator"""

# Start by testing imports

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import colorcet as cc
from natsort import natsort_keygen

from nmrquant.engine.calculator import *

# DATAFRAME COMPARISON FUNCTIONS

def compare_columns(df1, df2):
    assert list(df1.columns) == list(df2.columns)

def compare_values(df1, df2):
    for col in df1.columns:
        assert list(df1[col].values) == list(df2[col].values)

def compare_all(df1, df2):
    assert list(df1.all()) == list(df2.all())

def compare_type(df1, df2):
    assert type(df1) == type(df2)


def test_invoque_calculator(self):

    calculator = Quantifier()
    assert calculator.use_strd is False
    assert calculator.data == None
    assert calculator.mdata == None
    assert calculator.database == None
    assert calculator.metadata == None
    assert calculator.cor_data == None
    assert calculator.calc_data == None
    assert calculator.conc_data == None
    assert calculator.mean_data == None
    assert calculator.std_data == None
    assert calculator.plot_data == None
    assert calculator.ind_plot_data == None
    assert calculator.mean_plot_data == None
    assert calculator.metabolites == []
    assert calculator.conditions == []
    assert calculator.time_points == []
    assert calculator.proton_dict == {}
    assert calculator.missing_metabolites == []
    assert calculator.spectrum_count == 0
    assert calculator.dilution_factor == None


class TestGetDataMethod:

    def test_ensure_both_input_types_give_same_result(self):
        calculator1, calculator2 = Quantifier(), Quantifier()
        calculator1.get_data(data)
        calculator2.get_data(r"test_data/data.xlsx")
        compare_all(calculator1.data, calculator2.data)
        compare_type(calculator1.data, calculator2.data)
        compare_columns(calculator1.data, calculator2.data)
        compare_values(calculator1.data, calculator2.data)

    def test_ensure_get_data_checks_for_strd_use(self)


    def test_get_data(self):

        data = pd.read_excel(r"test_data/data.xlsx")

        assert calculator.use_strd is False

    def test_get_db(self):
        calculator1, calculator2 = Quantifier(), Quantifier()
        db = pd.read_csv(r"test_data/proton_db.csv", sep=";")
        calculator1.get_db(db)
        calculator2.get_db(r"test_data/proton_db.csv")
        check_dfs(calculator1.database, calculator2.database)
