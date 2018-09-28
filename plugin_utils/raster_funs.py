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
import scipy
from scipy import ndimage
from osgeo import gdal, osr
import osgeo.gdalnumeric as gnum
from osgeo import gdalconst
from qgis.core import QgsRasterLayer, QgsProject

def raster_2_array(raster_full_path):
    """Read a raster dem as array
    """
    data_set = gdal.Open(raster_full_path)
    data_set_band = data_set.GetRasterBand(1)
    raster_array = gnum.BandReadAsArray(data_set_band)
    no_data_value = data_set_band.GetNoDataValue()
    
    return raster_array, no_data_value

def raster_erosion(raster_array, dem_array, no_data_value):
    """ Function to eroded a raster array
    """
    try:
        eroded_array = raster_array * ndimage.binary_erosion(
                dem_array - no_data_value)
        return eroded_array
    
    except TypeError:
        # no_data_value is None, issue #3
        return raster_array

def array_2_raster(raster_array, input_template_path, output_path, 
                   data_type=gdalconst.GDT_Byte,
                   no_data_value=0):
    """Create a raster file in geotiff format from a numpy array.

    Geotransform information for the output file is taken from the file at
    input_template_path.
    data_type specifies the data type to be used in the output_file (types
    are defined in gdalconst)
    """

    raster = gdal.Open(input_template_path)
#    data_driver = raster.GetDriver() # Sometimes doesn't work
    try:
        data_driver = gdal.GetDriverByName("GTiff") # for QGIS3
    except TypeError:
        data_driver = gdal.GetDriverByName(b"GTiff") # for QGIS2
    data_set_geotransform = raster.GetGeoTransform()
    data_set_origin_x = data_set_geotransform[0]
    data_set_origin_y = data_set_geotransform[3]
    data_set_pixel_width = data_set_geotransform[1]
    data_set_pixel_height = data_set_geotransform[5]

    cols = raster_array.shape[1]
    rows = raster_array.shape[0]

    target_ds = data_driver.Create(
            output_path, cols, rows, 1, data_type)
    target_ds.SetGeoTransform((
            data_set_origin_x, data_set_pixel_width, 0,
            data_set_origin_y, 0, data_set_pixel_height))

    data_set_out_SRS = osr.SpatialReference()
    data_set_out_SRS.ImportFromWkt(raster.GetProjectionRef())
    target_ds.SetProjection(data_set_out_SRS.ExportToWkt())
    data_set_out_band = target_ds.GetRasterBand(1)
    data_set_out_band.SetNoDataValue(no_data_value)
    data_set_out_band.WriteArray(raster_array)

    data_set_out_band.FlushCache()
    target_ds = None

def load_raster_layer(raster_full_path, raster_filename):
        """Add the result combined hillshade to canvas.
        """
        rlayer = QgsRasterLayer(raster_full_path,
                raster_filename)
        try:
            from qgis.core import QgsMapLayerRegistry
            QgsMapLayerRegistry.instance().addMapLayer(rlayer)
        except ImportError:
            QgsProject.instance().addMapLayer(rlayer)      
