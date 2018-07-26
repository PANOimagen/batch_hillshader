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

import numpy as np
from numpy import (gradient, pi, arctan, arctan2, sin, cos, sqrt)

def hillshade(array, no_data_value, azimuth, angle_altitude):
    '''Hillshade the input numpy array and return a uint8 array.

    This function calculates the value of the hillshade array,
    given an altitudes array, an azimuth and an altitude angle
    https://github.com/rveciana/geoexamples/blob/master/python/shaded_relief/shaded_relief.py
    '''

    x, y = gradient(array)
    slope = pi/2. - arctan(sqrt(x * x + y * y))
    aspect = arctan2(-x, y)
    azimuthrad = azimuth * pi / 180.
    altituderad = angle_altitude * pi / 180.


    shaded = (sin(altituderad) * sin(slope)
                    + cos(altituderad) * cos(slope)
                    * cos(azimuthrad - aspect))

    hillshade_array = 255 * (shaded + 1) / 2

    return hillshade_array.astype(dtype=np.uint8)
