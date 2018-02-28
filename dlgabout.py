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


from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog

import platform
import os

try:
    from . import version
except ImportError:
    class version(object):
        VERSION = "devel"

uiFilePath = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'dlgabout.ui'))
FormClass = uic.loadUiType(uiFilePath)[0]

class DlgAbout(QDialog, FormClass):

    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.setupUi(self)

        repo_url = (u'<address><b>https://github.com/PANOimagen/' +
                    u'batch_hillshader</address></b>')

        tracker_url = (u'<address><b>https://github.com/PANOimagen/' +
                       u'batch_hillshader/issues</address></b><br>')

        panoi_url = u'<address><b>www.panoimagen.com</address></b><br>'
        
        repository_info = (u'Code repository: {}<br>Bug Tracker: {}'.format(
                repo_url, tracker_url))
        
        contact_info = (u'<h3>Copyright (C) 2017  by PANOimagen S.L.</h3>' +
                        u'PANOimagen S.L. La Rioja (Spain) -- {}'.format(
                                panoi_url))
                                
        plugin_description = ('This plugin has being developed by PANOimagen' +
                              u' S.L. and serves to generate a three light' +
                              u' exposure<br>hillshade (shaded relief by' +
                              u' combining three light exposures).\nFor more' +
                              u' information, please, read<br>metadata/' +
                              u'readme and/or contact the author.')
        
        external_dependencies = ('This plugin needs the <b>Processing' +
                                 u' Plugin</b> and uses external libraries' +
                                 u' for LiDAR processing mode,<br>see the' 
                                 u' corresponding licenses:<br>        +' +
                                 u' LASTools Library: <b><address>' +
                                 u'https://rapidlasso.com/lastools/' +
                                 u'</address></b> <br>        + FUSION' +
                                 u' LDV Software: <b><address>http://forsys.' +
                                 u'cfr.washington.edu/fusion.html' +
                                 u'</address></b><br>Also you can use <b>LasPy ' +
                                 u' Library</b> (BSD License):<b><address>' +
                                 u'https://github.com/laspy/laspy' +
                                 u'</address></b>')
        
        license_info = (u'<h3>License:' +
                        u'</h3>This program is free software' +
                        u' you can redistribute it and/or modify it under' +
                        u' the terms of the GNU General<br>Public License as' +
                        u' published by the Free Software Foundation, either' +
                        u' version 3 of the License, or (at your<br>option)' +
                        u' any later version.<br><br>This program is' +
                        u' distributed in the hope that it will be useful,' +
                        u' but WITHOUT ANY WARRANTY; without even<br>the' +
                        u' implied warranty of MERCHANTABILITY or FITNESS' +
                        u' FOR A PARTICULAR PURPOSE.  See the GNU General' +
                        u'<br>Public License for more details.<br><br>' +
                        u'You should have received a copy of the GNU' +
                        u' General Public License along with this program.' +
                        u' If not, see:<br><address><b>https://www.gnu.org/' +
                        u'licenses/</address></b>.')        
        self.codeRepoLabel.setText(repository_info)
        self.contactLabel.setText(contact_info)
        self.descriptionLabel.setText(plugin_description)
        self.libraryUsedLabel.setText(external_dependencies)
        self.licenseLabel.setText(license_info)
        self.versionLabel.setText(u'<h2>Batch Hillshader<\h2>' +
                                  u' Version {}'.format(
                                          version.VERSION))