# batch_hillshader

QGIS minimum version = 2.8

Author = PANOimagen S.L.

e-mail = info@panoimagen.com

Plugin to generate a three light exposure hillshade (shaded relief by combining three light exposures)

This plugin generates a three light exposure hillshade (shaded relief by combining three light exposures) using as input 
LiDAR classified data (ASPRS classification / *.laz, *.las formats) or a Digital Terrain Model (DTM) in raster format 
(GEOTiff / ASCII). The output file (three light exposure hillshade) is generated in GEOTiff format and users can save the 
intermediate processing results. This plugin allows users to process more than one file in the same process.

If you uses as input LiDAR data, note that plugin uses LASTools library.
        See LASTools License at: https://rapidlasso.com/lastools/

At the process with LiDAR data, user can generates the FUSION LDV Catalog report with the ground points, to check the input 
data quality (returns density, number of returns, return intensity, ...).

The three light exposures combining method is based in Gantenbein (2012).

  Ref.: Gantenbein, C. (2012): "Creating Shaded Relief for Geologic Mapping using Multiple Light Sources". U.S. From 
  "Digital Mapping Techniques'10--Workshop Proceedings". Geological Survey Open-File Report 1171
  
  (https://pubs.usgs.gov/of/2012/1171/pdf/usgs_of2012-1171-Gantenbein_p101-106.pdf) (Consult date-time: 2017/10/24 - 18:25 p.m.)

KeyWords = Shaded Relief, Hillshade, Digital Terrain Model, DTM, LiDAR, Batch Hillshade Processing, Three Exposure Hillshade

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
