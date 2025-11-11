# -*- coding: utf-8 -*-
"""
Created on Thu Jan 30 21:56:15 2025

@author: brendan

"""
# This is a shim for being able to use pyproject.toml
# to create an editable project. See:
# https://stackoverflow.com/a/62983901

import setuptools

if __name__ == "__main__":
    setuptools.setup()