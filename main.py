import pygame, sys, time, threading, random, numpy as np
from math import *


pygame.init()


class Cam:
    def __init__(self, user, x=0, y=0, z=0, rot=[0, 0]):
        self.user = user
        self.pos = [x, y, z]
        self.rot = rot
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.cx = 0; self.cy = 0
        self.mousePos = [self.cx, self.cy]
        self.vel = 0.1; self.zoom = 240


    def rotate(self, mX, mY):
        # print(mX, mY)
        self.rot[0] = self.rot[0] + (mX-self.cx)*pi*0.0008
        self.rot[1] = self.rot[1] + (mY-self.cy)*pi*0.0008


    def move(self, key):
        pos = np.array(self.pos)
        dirPos = np.array([0., 0., 0.])

        if key[pygame.K_w]: dirPos += rotateXZ(rotateYZ([0, 0, self.vel], self.rot[1], -1), self.rot[0], -1)
        if key[pygame.K_a]: dirPos += rotateXZ([-self.vel, 0, 0], self.rot[0], -1)
        if key[pygame.K_s]: dirPos += rotateXZ(rotateYZ([0, 0, -self.vel], self.rot[1], -1), self.rot[0], -1)
        if key[pygame.K_d]: dirPos += rotateXZ([self.vel, 0, 0], self.rot[0], -1)

        self.pos = pos + dirPos

        # if key[pygame.K_e]: self.pos = pos + rotate([0, self.vel, 0], True)
        # if key[pygame.K_q]: self.pos = pos + rotate([0, self.vel, 0], True)

        # if key[pygame.K_w]: self.pos[1] -= self.vel
        # if key[pygame.K_a]: self.pos[0] -= self.vel
        # if key[pygame.K_s]: self.pos[1] += self.vel
        # if key[pygame.K_d]: self.pos[0] += self.vel

        # if key[pygame.K_e]: self.pos[2] += self.vel
        # if key[pygame.K_q]: self.pos[2] -= self.vel


class Object:
    def __init__(self, pos, vectors, polygons, edges, usePolygons=True, useEdges=False, drawPolyMiddle=False, dotColor=(255,255,255)):
        self.pos = np.array(pos)
        self.vectors = [np.array((x+pos[0], y+pos[1], z+pos[2])) for x, y, z in vectors]
        self.polygons = None
        self.edges = None
        self.dotColor = dotColor
        self.drawPolyMiddle = drawPolyMiddle
        if usePolygons: self.polygons = polygons
        if useEdges: self.edges = edges
        # print(self.polygons)
        # print(self.edges)


    def rotate(self, rotX=0, rotY=0, rotZ=0, axis=None):
        if axis == None: axis = self.pos
        else: axis = np.array(axis)
        rotX = rotX/360*2*pi
        rotY = rotY/360*2*pi
        rotZ = rotZ/360*2*pi
        # print("-", rotX, rotY, rotZ)
        for i in range(0, len(self.vectors)):
            # t = time.time()
            # print(f"-{rotY}")
            # print(type(self.pos))
            # print(type(self.vectors[i]))
            self.vectors[i] = rotateXY(rotateYZ(rotateXZ(self.vectors[i]-axis, rotX), rotY), rotZ)+axis
            # print(time.time() - t)


# class Dot:
#     def __init__(self):
#         self.pos = np.array(pos)

 
# Object([0, 0, 0], [(1,1,1), (1,1,1)], [(1), (1, 1), (1, 1, 1)], [(1,1), (1,1)], usePolygons=True, useEdges=False)


def old_render(cam):
    screen.fill((0, 0, 0))

    i = 0; temp = []
    for edge in cube[1]:
        for x, y, z in (cube[0][edge[0]], cube[0][edge[1]]):
            z += 3-cam.pos[2]; f = 500/z
            point = (int((x-cam.pos[0])*f+cam.cx), int((y-cam.pos[1])*f))
            pygame.draw.circle(screen, (255, 255, 255), point, 3)

            if i % 2: pygame.draw.line(screen, (255, 255, 255), temp, point, 1)
            temp = point; i += 1

    pygame.display.update()


def rotateXZ(_vectors, rot, rev=1):
    # print(_vectors)
    x, y, z = _vectors[0], _vectors[1], _vectors[2]
    # x*cos(rot*rev)
    # print(f"XZ {rot}")
    rot = rot*rev
    return (x*cos(rot) - z*sin(rot), y, x*sin(rot) + z*cos(rot))


def rotateYZ(_vectors, rot, rev=1):
    x, y, z = _vectors[0], _vectors[1], _vectors[2]
    # print(f"YZ {rot}")
    rot = -rot*rev
    return (x, z*sin(rot) + y*cos(rot), z*cos(rot) - y*sin(rot))


def rotateXY(_vectors, rot, rev=1):
    x, y, z = _vectors[0], _vectors[1], _vectors[2]
    # print(f"XY {rot}")
    rot = rot*rev
    return (x*cos(rot) - y*sin(rot), x*sin(rot) + y*cos(rot), z)


# def rotate(_vectors, rev=False):
#     x, y, z = _vectors
#     if not rev:
#         rev = 1
        
#     else: rev = -1
#     # print(x, y, z)
#     # print(cam.rot)
#     x, y, z = rotateYZ(rotateXZ([x, y, z], rev), rev)

#     # _z = (x*sin(cam.rot[0]) + z*cos(cam.rot[0])) #*cos(cam.rot[1] - y*sin(cam.rot[1]))
#     return [x, y, z]


def draw_dot(cam, x, y, z, c=(255, 255, 255)):
    x = x-cam.pos[0]
    y = y-cam.pos[1]
    z = z-cam.pos[2]

    x, y, z = rotateYZ(rotateXZ([x, y, z], cam.rot[0]), cam.rot[1])

    if z > 0.001:
        x = int(cam.zoom/z*x)+cam.cx
        y = int(cam.zoom/z*y)+cam.cy

        # print(x, y)

        return (0, c, (x, y))
    else:
        return (0, c, (int(cam.zoom/0.001*x)+cam.cx, int(cam.zoom/0.001*y)+cam.cy))


def render(cam):
    global cams, objs, dots
    draws = []
    for obj in objs:
        v = [] # All the point from 3D to 2D
        if False or (abs(obj.pos[0]-cam.pos[0])+abs(obj.pos[1]-cam.pos[1])+abs(obj.pos[2]-cam.pos[2])) < 20*3:
            for x, y, z in obj.vectors:
                dot = draw_dot(cam, x, y, z, obj.dotColor)
                v.append(dot[2]); draws.append(dot)

            if obj.edges:
                for e1, e2 in obj.edges:
                    draws.append((1, obj.dotColor, v[e1], v[e2]))

        # if obj.polygons: 
        #     # Get all the polygons middle
        #     mids = []
        #     for p1, p2, p3, c in obj.polygons:
        #         middleX = (obj.vectors[p1][0] + obj.vectors[p2][0] + obj.vectors[p3][0]) / 3
        #         middleY = (obj.vectors[p1][1] + obj.vectors[p2][1] + obj.vectors[p3][1]) / 3
        #         middleZ = (obj.vectors[p1][2] + obj.vectors[p2][2] + obj.vectors[p3][2]) / 3
        #         x, y, z = get_dot(middleX, middleY, middleZ)
        #         mids.append((p1, p2, p3, c, abs(pow(middleX-cam.pos[0], 2) + pow(middleY-cam.pos[1], 2) + pow(middleZ-cam.pos[2], 2)), x, y, z))
        #     # Sort middles by distance
        #     for i in range(1, len(mids)):            
        #         for j in range(0, i):
        #             j = i - 1
        #             # print(f"{i}:{j} - {middles[i][3]}:{middles[j][3]}")
        #             if mids[i][4] > mids[j][4]: 
        #                 temp = (mids[j][0], mids[j][1], mids[j][2], mids[j][3], mids[j][4], mids[j][5], mids[j][6], mids[j][7])
        #                 mids[j] = mids[i]
        #                 mids[i] = temp
        #             else: break
        #             i -= 1

        #     #     print(middles)
        #     #     print(middles[i])
        #     # print(middles)
        #     # print()

        #     # Print polygons
        #     for p1, p2, p3, c, _, x, y, z in mids:
        #         if v[p1][2] > 0.1 or v[p2][2] > 0.1 or v[p3][2] > 0.1:
        #             print((v[p1][0], v[p1][1]), (v[p2][0], v[p2][1]), (v[p3][0], v[p3][1]))
        #             pygame.draw.polygon(screen, c, ((v[p1][0], v[p1][1]), (v[p2][0], v[p2][1]), (v[p3][0], v[p3][1])), 0)
        #         if obj.drawPolyMiddle: 
        #             if z > 0.001: pygame.draw.circle(screen, (255, 255, 255), (x+cx, y+cy), 3)

    for x, y, z, c in dots:
        draws.append(draw_dot(cam, x, y, z, c))
    
    for _cam in cams:
        if cam != _cam:
            _, c, pos = draw_dot(cam, _cam.pos[0], _cam.pos[1], _cam.pos[2], _cam.color)
            mag = (pow(abs(_cam.pos[0] - cam.pos[0]), 2) + 
                  pow(abs(_cam.pos[1] - cam.pos[1]), 2) + 
                  pow(abs(_cam.pos[2] - cam.pos[2]), 2)) # 10 - 0.1
            size = 10
            if mag != 0: size = 1/sqrt(mag)*50
            draws.append((2, c, pos, ceil(size)))
    return draws


def physics():
    rots = []
    for obj in objs:
        axis = None; rand = random.randint(0, 2)
        if rand == 1: axis = [0, 0, 0]
        if rand == 2: 
            axis = [obj.pos[0]+random.randint(-5, 5), obj.pos[1]+random.randint(-5, 5), obj.pos[2]+random.randint(-5, 5)]
            dots.append([axis[0], axis[1], axis[2], (0, 255, 0)])
        rots.append((random.randint(0, 360)/fps, random.randint(0, 360)/fps, random.randint(0, 360)/fps, axis))

    i = 0
    while run:
        clock.tick(fps)
        # objs[0].rotate(180/fps, 0, 0)
        for i in range(0, len(objs)-1):
            objs[i].rotate(rots[i][0], rots[i][1], rots[i][2], axis=rots[i][3])
        objs[-1].rotate(180/fps, 0, sin(i)*2)
        i += 1/fps


def start():
    global objs, dots, cams, fps, run, clock

    clock = pygame.time.Clock()
    fps = 120; run = True
    vectors = np.array([[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1], [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]]); # vectors *= 50
    polys = [
        (0, 1, 2, [255, 0, 0]), (0, 2, 3, [200, 0, 0]),
        (1, 2, 5, [0, 0, 255]), (2, 5, 6, [0, 0, 200]), 
        (4, 5, 7, [255, 165, 0]), (6, 5, 7, [200, 110, 0]), 
        (7, 3, 4, [0, 255, 0]), (0, 3, 4, [0, 200, 0]), 
        (2, 3, 6, [255, 255, 255]), (7, 3, 6, [200, 200, 200]),
        (0, 1, 4, [255, 255, 0]), (5, 1, 4, [200, 200, 0])]
    edges = [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4), (0, 4), (1, 5), (2, 6), (3, 7)]

    objs = []; cams = []
    
    dots = [[0, 0, 0, (255, 255, 0)], [0, 0, 0, (255, 255, 0)]]

    cube = Object([0, 0, 0], vectors, polys, edges, useEdges=True)
    cube2 = Object([5, 0, 0], vectors, polys, edges, useEdges=True)
    cube3 = Object([4, 1, -1], vectors, polys, edges, useEdges=True, drawPolyMiddle=True)
    # cube.rotate(1, 2, 3)
    # objs = [Object([5+i, 0, 0], vectors, polys, edges, useEdges=True) for i in range(0, 100)]

    for i in range(0, 10):
        objs.append(
            Object([random.randint(-10, 10), random.randint(-10, 10), random.randint(-10, 10)], vectors, polys, edges, useEdges=True))
    objs.append(cube); objs.append(cube2); objs.append(cube3)

    cube4 = Object([0, 10, 0], vectors, polys, edges, useEdges=True, dotColor=(255, 0, 0))
    dots.append([0, 10, 0, (255, 0, 0)])
    objs.append(cube4)

    threading.Thread(target=physics).start()


def add_cam(user):
    global cams
    cams.append(Cam(user, z=-5))


def remove_cam(user):
    global cams
    for _cam in cams:
        if _cam.user == user: cams.remove(_cam)


def camRotate(user, mX, mY):
    global cams
    for cam in cams:
        if cam.user == user: 
            cam.rotate(mX, mY)


def main(user, cx, cy, key):
    global cams
    cam = None
    for _cam in cams:
        if _cam.user == user: 
            cam = _cam; break
    if not cam: return [(0, (cx, cy), (100, 100, 255))]
    cam.cx = cx; cam.cy = cy
    cam.move(key)
    return render(cam)
