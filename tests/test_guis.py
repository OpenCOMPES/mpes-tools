import os

import nxarray as nxr
import pytest
from PyQt5.QtWidgets import QApplication

from mpes_tools import ARPES_Analyser
from mpes_tools import fit_panel
from mpes_tools import Gui_3d
from mpes_tools import show_4d_window

test_dir = os.path.dirname(__file__)
app = QApplication([])


@pytest.fixture
def data_4d():
    data = nxr.load(f"{test_dir}/data/example.nxs").data
    return data


@pytest.fixture
def data_3d(data_4d):
    data = data_4d.loc[{"kx": slice(0.48, 0.68)}].mean(dim=("kx"))
    return data


@pytest.fixture
def data_2d(data_3d):
    data = data_3d.loc[{"ky": slice(0.86, 1.08)}].mean(dim="ky")
    return data


def test_gui_4d_initialization(data_4d):
    # Initialize the 3D GUI with the processed data
    graph_window = show_4d_window(data_4d)

    # Assert that the GUI object is created successfully
    assert graph_window is not None


def test_gui_3d_initialization(data_3d):
    # Initialize the 3D GUI with the processed data
    graph_window = Gui_3d(data_3d)

    # Assert that the GUI object is created successfully
    assert graph_window is not None


def test_fit_gui_initialization(data_2d):
    # Initialize the 3D GUI with the processed data
    graph_window = fit_panel(data_2d, 0, 0, "")

    # Assert that the GUI object is created successfully
    assert graph_window is not None


def test_main_gui_initialization():
    # Initialize the 3D GUI with the processed data
    graph_window = ARPES_Analyser()

    # Assert that the GUI object is created successfully
    assert graph_window is not None
