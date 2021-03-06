#! /usr/bin/env python
# -*- coding: utf-8 -*-

###############################################################################
##                                                                           ##
##  Copyright 2010-2012, Neil Wallace <neil@openmolar.com>                   ##
##                                                                           ##
##  This program is free software: you can redistribute it and/or modify     ##
##  it under the terms of the GNU General Public License as published by     ##
##  the Free Software Foundation, either version 3 of the License, or        ##
##  (at your option) any later version.                                      ##
##                                                                           ##
##  This program is distributed in the hope that it will be useful,          ##
##  but WITHOUT ANY WARRANTY; without even the implied warranty of           ##
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            ##
##  GNU General Public License for more details.                             ##
##                                                                           ##
##  You should have received a copy of the GNU General Public License        ##
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.    ##
##                                                                           ##
###############################################################################

from __future__ import division

from PyQt4 import QtGui, QtCore, QtSvg


import teeth

class ChartRoot(teeth.ChartTooth):
    '''
    custom class which holds data about a root
    '''
    def __init__(self, tooth_id, model):
        teeth.ChartTooth.__init__(self, tooth_id, model)

        #: a boolean so that it's clear this is a ChartRoot,
        #: not the parent class ChartTooth
        self.is_root = True

        #: this variable determines the opacity of any painting
        self.opacity = 0.2

        shortname = self.short_name
        if not self.is_rightside:
            shortname = "%s%s%s"% (shortname[0], "r", shortname[2:])

        #: a reference to a QtSvg.QSvgRenderer with the correct svg
        self.svg_renderer = QtSvg.QSvgRenderer(":teeth/%s.svg"% shortname)

    def draw_structure(self, painter):
        if not self.is_present:
            return

        painter.save()

        drawn = False
        for property in self.properties:
            if property.root_type.startswith("IM"):
                pass
            else:
                option = QtGui.QTextOption(QtCore.Qt.AlignCenter)
                painter.setPen(QtGui.QPen(QtCore.Qt.black))
                painter.drawEllipse(self.rect)
                painter.drawText(self.rect, property.text, option)
                drawn = True

        if not drawn:
            self.draw_svg(painter)

        painter.restore()

    @property
    def has_rct(self):
        for property in self.properties:
            if property.root_type == "RT":
                return True
        return False

    @property
    def is_implant(self):
        for property in self.properties:
            if property.root_type.startswith("IM"):
                return True
        return False

    def draw_svg(self,  painter):
        if not self.is_rightside:
            painter.scale(-1, 1)
            offset = 2 * self.rect.topLeft().x() + self.rect.width()
            painter.translate(-offset, 0)

        if self.svg:
            QtSvg.QSvgRenderer(self.svg).render(painter, self.rect_f)
        else:
            painter.setOpacity(self.opacity)
            self.svg_renderer.render(painter, self.rect_f)

    @property
    def properties(self):
        return self.data_model.get_root_info(self.tooth_id)

    @property
    def perio_properties(self):
        return self.data_model.get_perio_data(self.tooth_id)

    @property
    def svg(self):
        '''
        returns an appropriate svg or None
        (in which case self.svg_renderer is used)

        presently, I only have an SVG for an implant.
        '''
        if self.is_implant:
            if self.is_upper:
                return ":implants/upper_implant.svg"
            else:
                return ":implants/lower_implant.svg"
        if self.has_rct:
            pass

        return None

    def draw_restorations(self, painter):
        '''
        overwrite this function, which is base class specific
        '''
        pass

    def set_rect(self, rect):
        '''
        update the rectangle of the root
        '''
        self.rect = rect
        self.rect_f = QtCore.QRectF(self.rect)

if __name__ == "__main__":
    def paintEvent(event):
        painter = QtGui.QPainter(widg)
        painter.setRenderHint(QtGui.QPainter.Antialiasing, True)
        for root in roots:
            root.draw_structure(painter)

    import chart_data_model
    model = chart_data_model.ChartDataModel()

    app = QtGui.QApplication([])
    widg = QtGui.QWidget()
    widg.setFixedSize(600,600)

    roots = []

    rects = [
        widg.rect().adjusted(0,0,-widg.width()/2, -widg.height()/2),
        widg.rect().adjusted(widg.width()/2, 0, 0, -widg.height()/2),
        widg.rect().adjusted(0,widg.height()/2, -widg.width()/2, 0),
        widg.rect().adjusted(widg.width()/2, widg.height()/2, 0, 0)
        ]

    ids = [1,16,17,32]
    for rect in rects:
        id = ids[rects.index(rect)]
        root = ChartRoot(id, model)
        root.set_rect(rect)
        roots.append(root)

    widg.paintEvent = paintEvent
    widg.show()
    app.exec_()