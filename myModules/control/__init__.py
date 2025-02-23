"""
A package to control the setting peripheral components
===============================================================

Author: Kevin Tung (National Cheng Kung University.BME.2022)

"""
from ._extra_component import ExtraPumpA
from ._extra_component import ExtraPumpB
from ._extra_component import ExtraValve

__all__ = ['ExtraPumpA', 'ExtraPumpB', 'ExtraValve']

# Define the version
__version__ = "1.0.0"