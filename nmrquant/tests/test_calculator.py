"""Test module for the NMRQuant calculator"""

import pytest
from pathlib import Path

from nmrquant.engine.calculator import Quantifier

@pytest.fixture(scope="class")
def initial_quantifier():
    return Quantifier()

@pytest.fixture(scope="class")
def quantifier(initial_quantifier):
    initial_quantifier.get_data(str(Path("./nmrquant/tests/test_data/data.xlsx").resolve()))
    initial_quantifier.get_db(str(Path("./nmrquant/tests/test_data/proton_db.csv").resolve()))
    initial_quantifier.import_md(str(Path("./nmrquant/tests/test_data/template.xlsx").resolve()))
    return initial_quantifier


class TestCalculator:

    def test_imports(self, quantifier):
        assert quantifier.data
        assert quantifier.database
        assert quantifier.mdata
        data_cols = [
            "Phenylalanine_2", "Phenylalanine_1", "Tyrosine", "Sucrose_2",
            "Glucose_2", "Glucose_1", "Sucrose_1", "Histine", "Cysteine",
            "Asparagine", "Aspartate", "Methionine", "Pyruvate", "Glutamate+Glutamine",
            "Acetate", "Alanine", "Lactate", "Threonine", "Ethanol", "INC_2", "INC_1",
            "Valine", "Isoleucine", "Isoleucine+Leucine", "Strd"
        ]
        database_cols = [
            'Acetate', 'Alanine', 'Arginine', 'Asparagine', 'Aspartate',
            'Cysteine', 'Ethanol', 'Formate', 'Fumarate', 'GABA', 'Glucose_1',
            'Glucose_2', 'Glutamate', 'Glutamate+Glutamine', 'Glutamine',
            'Glyoxylate', 'Histidine', 'Isoleucine', 'Isoleucine+Leucine',
            'Lactate', 'Leucine', 'Methionine', 'Orotate', 'Phenylalanine',
            'Phenylalanine_1', 'Phenylalanine_2', 'Pyruvate', 'Serine',
            'Succinate', 'Sucrose_1', 'Sucrose_2', 'TSP', 'Threonine',
            'Tyrosine', 'Valine'
        ]
        for col in quantifier.data.columns:
            assert col in data_cols
        for col in quantifier.database.columns:
            assert col in database_cols
        assert quantifier.data["# Spectrum#"].values.all() == quantifier.metadata["# Spectrum"].values.all()
