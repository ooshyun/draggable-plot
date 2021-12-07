
"""
    Reference. http://stackoverflow.com/questions/21654008/matplotlib-drag-overlapping-points-interactively
    Draggable plotting for the verification results.

    For the verification results, the user can drag the plot to change the compression data for a channel
    It recommends to make the virtual environment in python using requirements.txt.
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.lines import Line2D

import sys
import numpy as np
import matplotlib
matplotlib.use("Qt5Agg")
from PyQt5 import QtWidgets, QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

PATH_INIT_POINT = './data/point_data_init.txt'
PATH_POINT = './data/point_data.txt'

class DraggablePoint:

    lock = None #  only one can be animated at a time

    def __init__(self, parent, id, x=0.1, y=0.1, size=0.1):

        self.parent = parent
        self.point = patches.Ellipse((x, y), size, size * 3, fc='r', alpha=0.5, edgecolor='r')
        self.id = id
        self.x = x
        self.y = y
        parent.fig.axes[0].add_patch(self.point)
        self.press = None
        self.background = None
        self.connect()
        
        # if another point already exist we draw a line
        if self.parent.list_points:
            line_x = [self.parent.list_points[-1].x, self.x]
            line_y = [self.parent.list_points[-1].y, self.y]

            self.line = Line2D(line_x, line_y, color='r', alpha=0.5)
            parent.fig.axes[0].add_line(self.line)


    def connect(self):

        'connect to all the events we need'

        self.cidpress = self.point.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.point.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.point.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)


    def on_press(self, event):

        if event.inaxes != self.point.axes: return
        if DraggablePoint.lock is not None: return
        contains, attrd = self.point.contains(event)
        if not contains: return
        self.press = (self.point.center), event.xdata, event.ydata
        DraggablePoint.lock = self

        # draw everything but the selected rectangle and store the pixel buffer
        canvas = self.point.figure.canvas
        axes = self.point.axes
        self.point.set_animated(True)
        
        # TODO also the line of some other points needs to be released
        point_number =  self.parent.list_points.index(self)
        
        if self == self.parent.list_points[0]:
            self.parent.list_points[1].line.set_animated(True)            
        elif self == self.parent.list_points[-1]:
            self.line.set_animated(True)            
        else:
            self.line.set_animated(True)            
            self.parent.list_points[point_number+1].line.set_animated(True)                
                    
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.point.axes.bbox)

        # now redraw just the rectangle
        axes.draw_artist(self.point)

        # and blit just the redrawn area
        canvas.blit(axes.bbox)


    def on_motion(self, event):

        if DraggablePoint.lock is not self:
            return
        if event.inaxes != self.point.axes: return
        self.point.center, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        self.point.center = (self.point.center[0]+dx, self.point.center[1]+dy)

        canvas = self.point.figure.canvas
        axes = self.point.axes
        # restore the background region
        canvas.restore_region(self.background)

        # redraw just the current rectangle
        axes.draw_artist(self.point)
        
        point_number =  self.parent.list_points.index(self)
        self.x = self.point.center[0]
        self.y = self.point.center[1]
                
        # We check if the point is A or B        
        if self == self.parent.list_points[0]:
            # or we draw the other line of the point
            self.parent.list_points[1].line.set_animated(True)
            axes.draw_artist(self.parent.list_points[1].line)
        
        elif self == self.parent.list_points[-1]:
            # we draw the line of the point            
            axes.draw_artist(self.line)    

        else:
            # we draw the line of the point
            axes.draw_artist(self.line)
            #self.parent.list_points[point_number+1].line.set_animated(True)
            axes.draw_artist(self.parent.list_points[point_number+1].line)                
        
        
        if self == self.parent.list_points[0]:
            # The first point is especial because it has no line
            line_x = [self.x, self.parent.list_points[1].x]
            line_y = [self.y, self.parent.list_points[1].y]      
            # this is were the line is updated
            self.parent.list_points[1].line.set_data(line_x, line_y)
            
        elif self == self.parent.list_points[-1]:
            line_x = [self.parent.list_points[-2].x, self.x]
            line_y = [self.parent.list_points[-2].y, self.y]
            self.line.set_data(line_x, line_y)        
        else:
            # The first point is especial because it has no line
            line_x = [self.x, self.parent.list_points[point_number+1].x]
            line_y = [self.y, self.parent.list_points[point_number+1].y]      
            # this is were the line is updated
            self.parent.list_points[point_number+1].line.set_data(line_x, line_y)
            
            line_x = [self.parent.list_points[point_number-1].x, self.x]
            line_y = [self.parent.list_points[point_number-1].y, self.y]
            self.line.set_data(line_x, line_y)        

        # blit just the redrawn area
        canvas.blit(axes.bbox)


    def on_release(self, event):

        'on release we reset the press data'
        if DraggablePoint.lock is not self:
            return

        self.press = None
        DraggablePoint.lock = None

        # turn off the rect animation property and reset the background
        self.point.set_animated(False)
        
        point_number =  self.parent.list_points.index(self)
        
        if self == self.parent.list_points[0]:
            self.parent.list_points[1].line.set_animated(False)            
        elif self == self.parent.list_points[-1]:
            self.line.set_animated(False)            
        else:
            self.line.set_animated(False)            
            self.parent.list_points[point_number+1].line.set_animated(False)       
            

        self.background = None

        # redraw the full figure
        self.point.figure.canvas.draw()

        self.x = self.point.center[0]
        self.y = self.point.center[1]

        # custom code written by daniel oh
        # print(self.x, self.y)
        with open(PATH_POINT, 'w') as f:
            f.write(f'{self.id} {self.x} {self.y}')

        with open(PATH_POINT, 'r') as f:
            print("-"*5+"Updating point... "+"-"*5)
            print(f.read())

    def disconnect(self):

        'disconnect all the stored connection ids'

        self.point.figure.canvas.mpl_disconnect(self.cidpress)
        self.point.figure.canvas.mpl_disconnect(self.cidrelease)
        self.point.figure.canvas.mpl_disconnect(self.cidmotion)

class MyGraph(FigureCanvas):

    """A canvas that updates itself every second with a new plot."""

    def __init__(self, parent=None, width=5, height=4, dpi=100):

        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)

        self.axes.grid(True)
        xaxis = np.arange(0, 110+1)
        yaxis = np.arange(-40, 80+1)
        # self.axes.set_xticks(xaxis)
        # self.axes.set_yticks(yaxis)
        self.axes.set_xlim(min(xaxis), max(xaxis))
        self.axes.set_ylim(min(yaxis), max(yaxis))

        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                                   QtWidgets.QSizePolicy.Expanding,
                                   QtWidgets.QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

        # To store the 2 draggable points
        self.list_points = []

        self.show()
        self.plotDraggablePoints()


    def plotDraggablePoints(self, size=1):

        """Plot and define the 2 draggable points of the baseline"""
  
        # del(self.list_points[:])

        with open(PATH_INIT_POINT, 'r') as f:
            init_axises = f.readlines()

        print("-"*5+"Inital point"+"-"*5)
        for id, axis in enumerate(init_axises):
            x, y = axis.split(' ')[:-1]
            x, y = float(x), float(y)
            self.list_points.append(DraggablePoint(self, id, x, y, size))
            print(x, y)

        # self.list_points.append(DraggablePoint(self, 30, 30, size))
        # self.list_points.append(DraggablePoint(self, 40, 40, size))
        # self.list_points.append(DraggablePoint(self, 50, 50, size))
        # self.list_points.append(DraggablePoint(self, 60, 60, size))
        # self.list_points.append(DraggablePoint(self, 70, 10, size))

        self.updateFigure()


    def clearFigure(self):

        """Clear the graph"""

        self.axes.clear()
        self.axes.grid(True)
        del(self.list_points[:])
        self.updateFigure()


    def updateFigure(self):

        """Update the graph. Necessary, to call after each plot"""

        self.draw()

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)
    ex = MyGraph()
    sys.exit(app.exec_())