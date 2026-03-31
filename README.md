# Satellite Chlorophyll Analysis using Python

This project analyzes satellite-derived chlorophyll concentration data to study coastal environmental conditions around Taiwan using Python.

## Overview
- Process ocean satellite data (.nc format)
- Visualize chlorophyll concentration using geospatial maps
- Extract coastal values near selected cities using a 5×5 spatial averaging method
- Explore the relationship between chlorophyll concentration and GDP growth

## Methods
- Selected coastal cities and identified the nearest valid ocean grid
- Applied a 5×5 window averaging (ignoring NaN values)
- Required at least 50% valid data within the window for reliability
- Performed correlation analysis between chlorophyll concentration and GDP

## Tools & Libraries
- Python
- NumPy
- Pandas
- Matplotlib
- Cartopy
- NetCDF4

## Key Result
- Found a moderate positive correlation between GDP growth and chlorophyll concentration
- Results are exploratory and may be influenced by environmental factors

## Notes
Chlorophyll concentration is used as a proxy for coastal environmental conditions and does not directly represent pollution.

## Author
Yen-Chia Chiu
