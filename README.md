# Batch Hillshader

QGIS minimum version = 2.8

QGIS maximum version = 3.99

Author = **PANOimagen S.L.**

e-mail = *info@panoimagen.com*

Plugin to generate a three light exposure hillshade (shaded relief by combining three light exposures)

This plugin generates a three light exposure hillshade (shaded relief by combining three light exposures) using as input 
LiDAR classified data (ASPRS classification / *.laz, *.las formats) or a Digital Terrain Model (DTM) in raster format 
(GEOTiff / ASCII). The output file (three light exposure hillshade) is generated in GEOTiff format and users can save the 
intermediate processing results. This plugin allows users to process more than one file in the same process.

From version 2.3.0 user can generates a terrain hillshade and a surfaces hillshade (only with LasPy processing mode). The surfaces hillshade is generated using only the first LiDAR returns.

The three light exposures combining method is based in Gantenbein (2012).

  Ref.: Gantenbein, C. (2012): "Creating Shaded Relief for Geologic Mapping using Multiple Light Sources". U.S. From 
  "Digital Mapping Techniques'10--Workshop Proceedings". Geological Survey Open-File Report 1171
  
  (https://pubs.usgs.gov/of/2012/1171/pdf/usgs_of2012-1171-Gantenbein_p101-106.pdf) (Consult date-time: 2017/10/24 - 18:25 p.m.)
  
The following image shows the results of a terrain hillshade (left) and a surfaces hillshade (right). Results generated with LasPy Library
![image](https://github.com/PANOimagen/batch_hillshader/blob/master/icons/terrain&surfaces.png?raw=true)

For processing LiDAR data (allways in ASPRS format *.laz, and *.las) you must to install some external dependecies:

You can use LasPy Library (BSD License) to generate a three exposure hillshade from *.las ASPRS format:

    By default OSGeo console runs with Python 2, you need to configure the console to run with Python 3, so launch, from QGIS installation folder (Windows):

    bin\py3_env.bat

    bin\qt5_env.bat

    python -m pip install numpy

    python -m pip install scipy

    python -m pip install laspy
    
  LasPy documentation is avaible at: *https://github.com/laspy/laspy*
  
  If the process option with the LasPy library is not activated once it has been installed, you must restart QGIS.

  Plugin uses LASzip to unzip LiDAR data (*.laz format to *.las format). LasZip is LGPL License and you can found it at: *https://www.laszip.org/*

KeyWords = Shaded Relief, Hillshade, Digital Terrain Model, DTM, LiDAR, Batch Hillshade Processing, Three Exposure Hillshade, Digital Surfaces Model, MDS, Digital Elevation Model, MDE

Batch Hillshader license:

    Copyright (C) 2017  by PANOimagen S.L.

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.

![image](https://github.com/PANOimagen/batch_hillshader/blob/master/icons/PANOiFullHD.png?raw=true)
