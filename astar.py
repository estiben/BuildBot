import astar
import math

#FOR CELL MAPS
StraightCost = 10
DiagonalCost = 14

running = False
current = None

def _diagonalTo(a, b):
  return b[0] == a[0] - 1 and (b[1] == a[1] - 1 or b[1] == a[1] + 1) or b[0] == a[0] + 1 and (b[1] == a[1] - 1 or b[1] == a[1] + 1)

def g_cellbased(a, b):
    if _diagonalTo(a,b):
        return DiagonalCost
    else:
        return StraightCost
    
g_function = g_cellbased

def h_diagonal(pos, end):
    h_diagonal = min(abs(pos[0]-end[0]), abs(pos[1]-end[1]))
    h_straight = (abs(pos[0]-end[0]) + abs(pos[1]-end[1]))
    return DiagonalCost * h_diagonal + StraightCost * (h_straight - 2*h_diagonal)
    
def h_manhattan(pos, end):
    return StraightCost * (abs(pos[0] - end[0]) + abs(pos[1] - end[1]))

h_function = h_manhattan

def get_neighbors(pos):
    l = [ (pos[0]-1, pos[1]),
          (pos[0]+1, pos[1]),
          (pos[0], pos[1]-1),
          (pos[0], pos[1]+1),
          (pos[0]+1,pos[1] +1), 
          (pos[0]-1,pos[1] +1),
          (pos[0]-1,pos[1] -1),
          (pos[0]+1,pos[1] -1)]
    
    i=0
    while i < len(l):
        todel = False
        if l[i][0] < 0 or l[i][1] < 0 or l[i] in astar.blocked or l[i][0] > astar.max_x or l[i][1] > astar.max_y:
            del l[i]
            i-= 1
        i+= 1
        
    for i in (+1,-1):
        for j in (-1, +1):
            d = pos[0] + i, pos[1] + j
            if d not in astar.blocked and ((d[0], d[1] - j) in astar.blocked or (d[0] - i, d[1]) in astar.blocked) and d in l:
                l.remove(d)
    return l

def init(start, end, blocked):
    astar.start = start
    astar.end = end
    astar.blocked = blocked
    
    #Algorithm initialization
    astar.open = [start]
    astar.closed = []
    
    astar.g = {start: 0}
    astar.h = {}
    astar.f = {}
    astar.parent = {start: None}
    
    astar.f[start] = astar.h[start] = h_function(start,end)
    
    astar.lowest = start
    astar.cursor = start
    astar.path = None
    
    astar.running = True
    
    astar.maxg = 0
    astar.maxh = 0
    
    astar.current = None
    
    astar.checked_neighbors = []

def nodeCmp(x,y):
    h1, h2 = h[x], h[y]
    return 1 if h2 > h1 else (0 if h1 == h2 else -1)

def next():
    if len(astar.open) > 0:
        current = None
        for node in astar.open:
            if not current or astar.f[node] < astar.f[current]:
                current = node
        
        astar.current = current
        
        if astar.h[current] < astar.h[lowest] and astar.g[current] > astar.g[lowest]:
            astar.lowest = current
        
        if astar.h[current] < astar.h[cursor] or astar.g[current] > astar.g[cursor]:
            astar.cursor = current
        
        #Updates the path
        astar.test_path = []
        node = cursor
        while node:
            astar.test_path.append(node)
            node = astar.parent[node]
        
        if lowest == end:
            _stop()
            return False
        
        astar.open.remove(current)
                
        astar.closed.append(current)
        
        astar.checked_nodes = [current]
        
        for neighbor in astar.get_neighbors(current):
            update = False
            
            if neighbor not in closed:
                
                astar.checked_nodes.append(neighbor)
                
                g = astar.g[current] + g_function(current, neighbor)
                
                if neighbor in open:
                    if g < astar.g[neighbor]:
                        update = True
                else:
                    astar.open.append(neighbor)
                    update = True
            
                if update:                        
                    astar.parent[neighbor] = current
                    
                    astar.g[neighbor] = g
                    h = astar.h[neighbor] = h_function(neighbor, astar.end)
                    astar.f[neighbor] = g + h
                    
                    astar.maxg = max(astar.maxg, float(g))
                    astar.maxh = max(astar.maxh , float(h))

        #astar.open.sort(nodeCmp,reverse = True)
        
        return True
    else:
        _stop()
        return False
    
def _stop():
    astar.running = False
    astar.path = []
    node = lowest
    while node:
        astar.path.append(node)
        node = astar.parent[node]

def Brensenham_line(x,y,x2,y2):
    """Brensenham line algorithm"""
    steep = 0
    coords = []
    dx = abs(x2 - x)
    if (x2 - x) > 0: sx = 1
    else: sx = -1
    dy = abs(y2 - y)
    if (y2 - y) > 0: sy = 1
    else: sy = -1
    if dy > dx:
        steep = 1
        x,y = y,x
        dx,dy = dy,dx
        sx,sy = sy,sx
    d = (2 * dy) - dx
    for i in range(0,dx):
        if steep: coords.append((y,x))
        else: coords.append((x,y))
        while d >= 0:
            y = y + sy
            d = d - (2 * dx)
        x = x + sx
        d = d + (2 * dy)
    coords.append((x2,y2))
    return coords

#returns true if line from a to b is clear
def walkable((x,y),(x2,y2), blocked):
    steep = 0
    coords = []
    dx = abs(x2 - x)
    if (x2 - x) > 0: sx = 1
    else: sx = -1
    dy = abs(y2 - y)
    if (y2 - y) > 0: sy = 1
    else: sy = -1
    if dy > dx:
        steep = 1
        x,y = y,x
        dx,dy = dy,dx
        sx,sy = sy,sx
    d = (2 * dy) - dx
    for i in range(0,dx):
        if steep:
            if (y,x) in blocked: return False
        elif (x,y) in blocked: return False
        while d >= 0:
            y = y + sy
            d = d - (2 * dx)
        x = x + sx
        d = d + (2 * dy)
    return (x2,y2) not in blocked

def findpath(start, end, blocked):
    init(start,end,blocked)
    while next():
        pass
    checkPoint = 0
    currentPoint = 1
    while currentPoint < len(astar.path) - 1:
        if walkable(astar.path[checkPoint], astar.path[currentPoint + 1], blocked):
            del astar.path[currentPoint]
        else:
            checkPoint = currentPoint
            currentPoint += 1
            