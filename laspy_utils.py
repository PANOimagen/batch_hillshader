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
import os
from scipy.interpolate import griddata
from osgeo import gdal, osr
from gdal import gdalconst
from .plugin_utils import files_and_dirs_funs
import laspy
from laspy.file import File
from laspy.header import Header

class LiDAR(object):

    def __init__(self, in_las_path, out_path, partials_create, 
                 terrain=False, surfaces=False):
        
        """ Init variables
        """
        self.terrain = terrain
        self.surfaces = surfaces
        if self.terrain:
            self.class_flag = 2
        elif self.surfaces:
            # TODO
            pass

        self.in_las_path = in_las_path
        self.path, full_name = os.path.split(in_las_path)
        self.files_utils = files_and_dirs_funs.DirAndPaths()
        self.name, self.extension = self.files_utils.init(full_name)
        self.partials_create = partials_create
        self.templates_dict = self.files_utils.file_templates(self.name)
        self.out_path = out_path
        self.read_las_file()
        self.get_all_points()
        self.get_scaled_points()
        self.get_file_extent()
        self.get_file_density()
        self.get_points_arrays()

    def process(self):
        
        if self.partials_create and not self.surfaces:
            self.out_dir = os.path.join(self.out_path, 'intermediate_results', 
                                   'las')
            self.files_utils.create_dir(self.out_dir)

            self.write_las_file()

        return [self.lidar_arrays_list, 
                self.las_file_extent, 
                self.density['ground_dens_class']]
        
    def read_las_file(self):
        """ Read the input LiDAR file in las format. Not laz format
        """
        self.in_file = File(self.in_las_path, mode='r')
        self.scale = self.in_file.header.scale
        self.offset = self.in_file.header.offset
        
    def get_all_points(self):
        """ Get points for file (points information and coordinates)
        """
        self.points_array = self.in_file.get_points()
        self.points_number = len(self.in_file)
    
    def get_scaled_points(self):
        """ Get the coordinates scalated
        """
        x = self.in_file.X
        y = self.in_file.Y
        z = self.in_file.Z
        
        self.x_dimension = x * self.scale[0] + self.offset[0]
        self.y_dimension = y * self.scale[1] + self.offset[1]
        self.z_dimension = z * self.scale[-1] + self.offset[-1]
    
    def get_file_extent(self):
        """ Get extent of the lidar file
        """

        self.las_file_extent = [(max(self.x_dimension), max(self.y_dimension)), 
                                (max(self.x_dimension), min(self.y_dimension)), 
                                (min(self.x_dimension), max(self.y_dimension)), 
                                (min(self.x_dimension), min(self.y_dimension))]
    
    # for raster_geotransform= (min(self.x_dimension, max(self.y_dimension)))
    # or the same self.las_file_extent[2]
    
    def get_ground_points(self):
        """ Function to get the number of ground points. 
            Source: laspy documentation
        """
        num_returns = self.in_file.num_returns
        return_num = self.in_file.return_num
        ground_points = self.in_file.points[num_returns == return_num]
        self.ground_points_number = len(ground_points)
        
    def get_file_density(self):
        """ Compute points density only with ground points -class: 2-. 
        """
        self.get_ground_points()
            
        self.density = {}
        self.file_sup_m2 = (max(self.x_dimension) - min(self.x_dimension)) *\
                            (max(self.y_dimension) - min(self.y_dimension))
        # density of all lidar returns
        self.density['all_dens'] = self.points_number / self.file_sup_m2
        
        class_2_points, _ = self.get_points_by_class(2)
        class_0_points, _ = self.get_points_by_class(0)
        class_1_points, _ = self.get_points_by_class(1)
        class_7_points, _ = self.get_points_by_class(7)
        class_8_points, _ = self.get_points_by_class(8)
        # density of only ground points filtered by returns  
        self.density['ground_dens_ret'] = (self.ground_points_number /
                                      self.file_sup_m2)
        # # density of only ground points filtered by class: 2 
        self.density['ground_dens_class'] = (
                            (len(class_2_points)) / self.file_sup_m2)
        # density of lidar file excluding classes 0, 1, 7 and 8. ¿Where is overlap class?
        self.density['util_points'] = ((self.points_number - 
                                len(class_0_points) - len(class_1_points) - 
                                len(class_7_points) - len(class_8_points)) /
                                self.file_sup_m2)
        
        # compare ground points density (filtered points by class vs filtered points by returns)
        if self.density[
                'ground_dens_ret'] == self.density['ground_dens_class']:
            return True
        else:
            return False # pass
        
    def get_points_by_class(self, classif=2):
        """ Get points array with the given classification id (ASPRS classes)
        """
        class_points_bool = self.in_file.Classification == classif
        return self.points_array[class_points_bool], class_points_bool
        
    def get_points_arrays(self):
        """ Creates arrays for a given class (default=2) with the coordinates
            of the points classificated by that class flag
        """
#        class_flags = 2, 3, 4, 5 para suelo, vegetación baja, media y alta respectivamente
        if self.terrain:
            class_2_points, class_2_bool = self.get_points_by_class(
                    self.class_flag)
            size = class_2_points.shape[0]
            x_array = self.x_dimension[class_2_bool].reshape(size, 1)
            y_array = self.y_dimension[class_2_bool].reshape(size, 1)
            z_array = self.z_dimension[class_2_bool]
            
        elif self.surfaces:
            # Guardo el archivo para poder leerlo
            
            self.out_dir = os.path.join(self.out_path, 'intermediate_results', 
                                   'las')
            
            filename = ('Surfaces_' + 
                                self.templates_dict['las'].format(self.name))

            full_path = os.path.join(self.out_dir, filename)
            
            self.files_utils.create_dir(self.out_dir)
            
            out_file = File(full_path, mode='w', header=self.in_file.header)
            out_file.points = self.in_file.points[
                    self.in_file.return_num == 1]
            out_file.close()
            
            #leo el archivo
            in_file = File(full_path, mode='r')
            scale = in_file.header.scale
            offset = in_file.header.offset
                            
            x = in_file.X
            y = in_file.Y
            z = in_file.Z
            
            x_dimension = x * scale[0] + offset[0]
            y_dimension = y * scale[1] + offset[1]
            z_dimension = z * scale[-1] + offset[-1]
            
            size = x_dimension.shape[0]
            
            x_array = x_dimension.reshape(size, 1)
            y_array = y_dimension.reshape(size, 1)
            z_array = z_dimension
            
            # Cerrar archivo para poder eliminarlo
            in_file.close()
            
            if not self.partials_create:     
                self.files_utils.remove_temp_file(full_path)
                try:
                    self.files_utils.remove_temp_dir(self.out_dir)
                except OSError:
                    pass
                
        xy_array = np.concatenate((x_array, y_array), axis=1)
        self.lidar_arrays_list = [xy_array, z_array]
    
    def write_las_file(self):
        """ Create and write a new lidar file with the desirable points
        """ 
        if self.surfaces:
            self.out_full_path = os.path.join(self.out_dir, ('Surfaces_' + 
                                self.templates_dict['las'].format(self.name)))
        
        elif self.terrain:
            self.out_full_path = os.path.join(self.out_dir, ('Terrain_' + 
                                self.templates_dict['las'].format(self.name)))
        
        out_file = File(self.out_full_path, mode='w', 
                            header=self.in_file.header)
        if self.terrain:
            class_2_points, class_2_bool = self.get_points_by_class(
                    self.class_flag)
            out_file.points = self.in_file.points[class_2_bool]
            
        elif self.surfaces:
            out_file.points = self.in_file.points[
                    self.in_file.return_num == 1]
        
        out_file.close()

class RasterizeLiDAR(object):

    def __init__(self, input_file_path, laspy_result, out_path, 
                 terrain=False, surfaces=False,
                 method='nearest', pixel_size=None):

        self.lidar_arrays_list = laspy_result[0]
        self.lidar_extent = laspy_result[1]
        self.density = laspy_result[-1]
        self.files_utils = files_and_dirs_funs.DirAndPaths() 
        _, input_file = os.path.split(input_file_path)
        name, _ = self.files_utils.init(input_file)
        
        self.lidar_xy_array = self.lidar_arrays_list[0]
        self.lidar_altitudes_array = self.lidar_arrays_list[-1]
        self.method = method
        self.pixel_size = pixel_size
        
        templates_dict = self.files_utils.file_templates(name)
        out_name = templates_dict['dem'].format(name)
        self.dirs = self.files_utils.set_output_dir(out_path)[0]
        
        self.files_utils.create_dir(self.dirs['dem'])
        if terrain:
            prefix = 'Terrain_'
        if surfaces:
            prefix = 'Surfaces_'
            
        self.dem_full_path = os.path.join(self.dirs['dem'], (
                        prefix + out_name))

#        lidar_extent = [(max(self.x_dimension), max(self.y_dimension)), 
#                        (max(self.x_dimension), min(self.y_dimension)), 
#                        (min(self.x_dimension), max(self.y_dimension)), 
#                        (min(self.x_dimension), min(self.y_dimension))]
        
#        if not pixel_size:
#            # get the points density and create a pixel size that allows at least three points per pixel
#            self.pixel_size = self.get_recommended_pixel_size(self.density)
#        else:
#            if self.check_pixel_size(pixel_size):
#                self.pixel_size = pixel_size
#            else:
#                self.pixel_size = self.get_recommended_pixel_size(self.density)
           
#    def get_recommended_pixel_size(self, min_returns=3):
#        """ Get the recomended pixel size for output raster file created
#            from lidar data. Pixel size must contains at least 3 lidar
#            returns
#        """
#        return np.round(min_returns / self.density)
#        
#    def check_pixel_size(self, pixel_size):
#        """ Compare pixel size given by the user with the recomended in 
#            accordance with the lidar file density
#        """ 
#        if pixel_size <= self.get_recommended_pixel_size():
#            return False
#    
    def makegrid(self):
        """ This function generates the center grid of the future raster.
            This is needed to interpolate between the LiDAR points
        """
        corner0 = self.lidar_extent[2]
        # px_center0 = (min_x, max_y)
        px_center0 = ((corner0[0] + self.pixel_size / 2),
                      (corner0[1] - self.pixel_size / 2))
        corner1 = self.lidar_extent[1]
        # px_center1 = (max_x, min_y)
        px_center1 = ((corner1[0] - self.pixel_size / 2),
                      (corner1[1] + self.pixel_size / 2))
                
        self.grid_x, self.grid_y = np.mgrid[
                            px_center0[0]: px_center1[0]: self.pixel_size, 
                            px_center0[-1]: px_center1[-1]: -self.pixel_size]

    def interpolate_grid(self):
        """ This function generates an interpolated array from point cloud.
            lidar x-y points, z_values and mesh_grid is needed. 
            Avaible methods are nearest, linear, cubic (1-D) and cubic (2-D) 
        """
        self.makegrid()
        interpolate_grid = griddata(self.lidar_xy_array, 
                                    self.lidar_altitudes_array,
                                    (self.grid_x, self.grid_y), 
                                    method=self.method)
        return interpolate_grid.T

    def array_2_raster(self, raster_array, epsg_code=None,
                   data_type=gdalconst.GDT_Float64, no_data_value=-99999):
        """ Create a raster file in geotiff format from a numpy array.
            Geotransform information for the output file is taken from the 
            input lidar file.
            data_type specifies the data type to be used in the output_file 
            (types are defined in gdalconst)
        """
#        data_driver = raster.GetDriver() # Sometimes doesn't work
        try:
            data_driver = gdal.GetDriverByName("GTiff") # for QGIS3
        except TypeError:
            data_driver = gdal.GetDriverByName(b"GTiff") # for QGIS2
        data_set_geotransform = self.set_raster_geotransform()
    
        rows = raster_array.shape[0]
        cols = raster_array.shape[-1]
        
        target_ds = data_driver.Create(
                self.dem_full_path, cols, rows, 1, data_type)
        target_ds.SetGeoTransform(data_set_geotransform)
        
        if epsg_code:
            data_set_out_SRS = self.set_crs(epsg_code)
            target_ds.SetProjection(data_set_out_SRS.ExportToWkt())
            
        data_set_out_band = target_ds.GetRasterBand(1)
        data_set_out_band.SetNoDataValue(no_data_value)
        data_set_out_band.WriteArray(raster_array)
        
        data_set_out_band.FlushCache()
        target_ds = None
        
        return self.dem_full_path

    def set_raster_geotransform(self):
        """ Set the extent for the output raster
            geotransform = (x_origin, pixel_x, 0, y_origin, 0, pixel_y)
            pixel_y is frecuently defined < 0
        """
        self.raster_origin = self.lidar_extent[2] # this is min_x and max_y
        return (self.raster_origin[0], 
                self.pixel_size, 
                0, 
                self.raster_origin[-1], 
                0,
                -self.pixel_size)
    
    def set_crs(self, epsg_code):
        """ Set the output raster crs by a given EPSG code
        """
        data_set_out_SRS = osr.SpatialReference()
        data_set_out_SRS.ImportFromEPSG(epsg_code)
        
        return data_set_out_SRS