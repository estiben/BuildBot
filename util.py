import math
import constants

#add
def add2((x1,y1), (x2,y2)):
    return (x1 + x2, y1 + y2)
    #return map(lambda (x, y): x + y, zip((x1, y1), (x2, y2)))
    
#subtract
def sub2((x1,y1), (x2,y2)):
    return (x1 - x2, y1 - y2)
    #return map(lambda (x, y): x - y, zip((x1, y1), (x2, y2)))
    
#convert view coordinates to world coordinates
def view_to_world((x,y), view):
    return (x + view.x, y + view.y)

#convert world coordinates to view coordinates
def world_to_view((x,y), view):
    return (x - view.x, y - view.y)
    
#convert world coordinates to grid coordinates
def world_to_grid((x, y)):
    return (x // constants.cellSize, y // constants.cellSize)

#convert grid coordinates to world coordinates
def grid_to_world((x, y)):
    return ((x * constants.cellSize) + (constants.cellSize // 2), (y * constants.cellSize) + (constants.cellSize // 2))
    
#calculate x and y from given speed and direction
def speedDir_xy(s, d):
    return (math.sin(d * math.pi / 8) * s, -math.cos(d * math.pi / 8) * s)
    
#return direction from 1 to 2, returns 0-16
def point_direction((x1, y1), (x2, y2)):
    return (math.atan2(x2 - x1, y1 - y2) / (math.pi / 8)) % 16