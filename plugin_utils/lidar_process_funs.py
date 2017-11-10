# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Batch_Hillshader
                                 A QGIS plugin  to generate a three light
                                 exposure hillshade (shaded relief by
                                 combining three light exposures)

    For more information, see the program documentation.

    If you uses as input LiDAR data, note that plugin uses LASTools library.
        See LASTools License at  <https://rapidlasso.com/lastools/>

    Plugin also use in LiDAR data mode FUSION LDV.
        See FUSION LDV License at <http://forsys.cfr.washington.edu/fusion.html>
                              -------------------
        begin                : 2016-07-13
        git sha              : $Format:%H$
        copyright            : (C) 2017 by PANOimagen S.L.
        email                : info@panoimagen.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software: you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation, either version 3 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 *   This program is distributed in the hope that it will be useful,       *
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
 *   GNU General Public License for more details.                          *
 *                                                                         *
 *   You should have received a copy of the GNU General Public License     *
 *   along with this program.  If not, see <https://www.gnu.org/licenses/> *
 ***************************************************************************/
"""
from __future__ import unicode_literals
import processing

def search_lastools_path():
    """This function returns the installation path of LasTools Library
    """
    try:
        return processing.algs.lidar.lastools.LAStoolsUtils.\
                    LAStoolsUtils.LAStoolsPath()
    except AttributeError:
        return ''

def search_fusion_path():
    """This function returns the installation path of FUSION LDV
    """
    try:
        return processing.algs.lidar.fusion.FusionUtils.\
                    FusionUtils.FusionPath()
    except AttributeError:
        return ''


def laz2las(input_file_full_path, las_full_path):
    """Convert compresed lidar file (*.laz) to a lidar file (*.las)
    """
    process = processing.runalg('lidartools:laszip', 'verbose', 'False',
                      input_file_full_path, 'False', 'False', 'False', '',
                      las_full_path)

    return process

def filter_las_ground_points(las_full_path, las_ground_full_path):
    """Filter the lidar points with ground class(class = 8)
    """

    process = processing.runalg('lidartools:las2lasfilter', True, False,
                                las_full_path, 8, 8, 0, "-", 0, "-",  "",
                                las_ground_full_path)

    return process

def create_catalog(ground_points, catalog_params, catalog_full_path):
    """Create Fusion/LDV catalog report.

    Output is written in file catalog_full_path.
    """
    sep = ','
    dens = (str(catalog_params['size_density']),
            str(catalog_params['min_density']),
            str(catalog_params['max_density']))
    density = sep.join(dens)

    firstdens = (str(catalog_params['size1_density']),
                 str(catalog_params['min1_density']),
                 str(catalog_params['max1_density']))
    firstdensity = sep.join(firstdens)

    intens = (str(catalog_params['size_intensity']),
              str(catalog_params['min_intensity']),
              str(catalog_params['max_intensity']))
    intensity = sep.join(intens)

    process = processing.runalg(
                'lidartools:catalog', ground_points, density, firstdensity,
                intensity, '', catalog_full_path)

    return process

def create_dtm(las_full_path, dtm_full_path, size_dtm):
    """Create dtm raster file from lidar ground points in las file
    """

    process = processing.runalg('lidartools:blast2dem', 'verbose', 'False',
        las_full_path, 8, size_dtm, 0, 0, 'False', '', dtm_full_path)

    return process
