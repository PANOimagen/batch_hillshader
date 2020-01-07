# -*- coding: utf-8 -*-
"""
/***************************************************************************
 Batch_Hillshader
                                 A QGIS plugin  to generate a three light
                                 exposure hillshade (shaded relief by
                                 combining three light exposures)

    For more information, see the program documentation.

    Plugin uses LASzip, see <https://laszip.org/>
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

import os
import subprocess

def run_LASzip(laz_path, out_path):
    """ This function call executable laszip file and unzip lidar file (*.laz)
        to *.las. LASzip is an external software with LGPL License. For more
        information visit https://rapidlasso.com/laszip/
    """
    
    path = os.path.split(os.path.abspath(__file__))[0]
    LASzip_path = os.path.join(path, 'LASzip', 'laszip64.exe')

    laz_dir, laz_file = os.path.split(laz_path)
    laz_filename, laz_ext = os.path.splitext(laz_file)
    
    las_ext = '.las'
    idx = 0

    print(out_path, os.path.exists(out_path))
    las_path = os.path.join(out_path, (laz_filename + '_{}'.format(idx) + 
                                          las_ext))
# -----------------------------------------------------------------------------

    in_args = ' -i "{}"'.format(laz_path)
    out_args = ' -o "{}"'.format(las_path)

    call = LASzip_path + in_args + out_args

    shell  = False
    print(call)
    ret = subprocess.call(call, shell)

    if ret !=0:
        if ret < 0:
            raise ValueError(u'LASzip process killed by signal.' + 
                            u' Return code: {}'.format(-ret))
        else:
            raise ValueError(u'LASzip process failed. Return code: {}'.format(
                    ret))
    else:
        return True, las_path