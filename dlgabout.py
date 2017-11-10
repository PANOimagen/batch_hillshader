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
from PyQt4 import uic
from PyQt4.QtGui import QDialog

import platform
import os

try:
    import version
except ImportError:
    class version(object):
        VERSION = "devel"

uiFilePath = os.path.abspath(os.path.join(os.path.dirname(__file__), 'dlgabout.ui'))
FormClass = uic.loadUiType(uiFilePath)[0]

class DlgAbout(QDialog, FormClass):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)
        
        repository_info = (u'Code repository: https://github.com/PANOimagen/batch_hillshader\nBug Tracker: https://github.com/PANOimagen/batch_hillshader/issues')
        
        contact_info = (u'Copyright: (C) 2017 by PANOimagen S.L.\nPANOimagen S.L. La Rioja (Spain)\nwww.panoimagen.com')
        
        plugin_description = (u'This plugin has being developed by PANOimagen S.L. and serves to\ngenerate a three light exposure hillshade (shaded relief by combining\nthree light exposures).\nFor more information, please, read metadata/readme and/or contact the author.')
        
        external_dependencies = (u'This plugin needs the Processing Plugin and uses external libraries for\nLiDAR processing mode, see the corresponding licenses:\n        + LASTools Library\n        + FUSION LDV Software')
        
        license_info = 'This program is free software: you can redistribute it and/or modify it\nunder the terms of the GNU General Public License as published by\nthe Free Software Foundation, either version 3 of the License, or\n(at your option) any later version.'
        
        self.codeRepoLabel.setText(repository_info)
        self.contactLabel.setText(contact_info)
        self.descriptionLabel.setText(plugin_description)
        self.libraryUsedLabel.setText(external_dependencies)
        self.licenseLabel.setText(license_info)
        self.versionLabel.setText('Batch Hillshader version {}'.format(
                version.VERSION))

