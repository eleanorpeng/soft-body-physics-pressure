import math
from OpenGL.raw.GLUT import glutSwapBuffers

from Material import *
from Spring import *
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *

nump = 20
nums = nump + 1
radius = 0.6
screen = (600, 600)
zoom = 7
PI = math.pi
springs = [Spring() for i in range(nums + 2)]
points = [Material() for i in range(nump + 2)]
my_points = points.copy()

mass = 1
restitution = 0.3
pressure = 0.1
final_pressure = 50
KS = 100.0 # elasticity factor (spring)
KD = 10.0  # elasticity factor (damping)
dt = 0.01
gravity = -9.81
keys = None

def main():
    global pressure
    global keys

    pg.init()
    pg.display.set_mode(screen, pg.DOUBLEBUF | pg.OPENGL)

    glViewport(0, 0, screen[0], screen[1])
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(-zoom, zoom, -zoom, zoom)
    glMatrixMode(GL_MODELVIEW)

    create_ball()

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()
            keys = pg.key.get_pressed()

        set_force()
        set_pressure_force()
        integrate_euler()
        draw()
        if pressure < final_pressure:
            pressure += final_pressure / 100.0


def create_ball():
    for i in range(1, nump+1):
        points[i].x = radius * math.sin(i * (2 * PI) / nump)
        points[i].y = radius * math.cos(i * (2 * PI) / nump) + zoom / 2

    for i in range(1, nump+1):
        add_spring(i, i, i+1)
    add_spring(nump, nump, 1)


def add_spring(index, i, j):
    springs[index].i = i
    springs[index].j = j
    springs[index].length = math.sqrt(((points[i].x - points[j].x) ** 2) + ((points[i].y - points[j].y) ** 2))

def set_force():
    check_key()

    for i in range(1, nums+1):
        cur_spring = springs[i]
        point1 = points[cur_spring.i]
        point2 = points[cur_spring.j]

        x_diff = point1.x - point2.x
        y_diff = point1.y - point2.y
        r12d = math.sqrt(x_diff ** 2 + y_diff ** 2)

        # get velocities of start & end points
        if r12d != 0:
            vx12 = points[cur_spring.i].vx - points[cur_spring.j].vx
            vy12 = points[cur_spring.i].vy - points[cur_spring.j].vy

            force = ((r12d - cur_spring.length) * KS + (vx12 * x_diff + vy12 * y_diff)) * KD / r12d

            fx = x_diff / r12d * force
            fy = y_diff / r12d * force

            # Accumulate force for starting point
            points[cur_spring.i].fx -= fx
            points[cur_spring.i].fy -= fy

            # Accumulate force for ending point
            points[cur_spring.j].fx += fx
            points[cur_spring.j].fy += fy

            cur_spring.nx = y_diff / r12d
            cur_spring.ny = -x_diff / r12d

def check_key():
    for i in range(1, nump + 1):
        my_points[i].fx = 0
        my_points[i].fy = gravity * mass if (pressure - final_pressure) >= 0 else 0
        if keys[pg.K_UP]:
            my_points[i].fy = -gravity * mass
        if keys[pg.K_DOWN]:
            my_points[i].fy = gravity * mass
        if keys[pg.K_RIGHT]:
            my_points[i].fx = -gravity * mass
        if keys[pg.K_LEFT]:
            my_points[i].fx = gravity * mass

def get_volume():
    volume = 0
    for i in range(1, nums):
        cur_spring = springs[i]
        point1 = my_points[cur_spring.i]
        point2 = my_points[cur_spring.j]
        x_diff = point1.x - point2.x
        y_diff = point1.y - point2.y

        r12d = math.sqrt(x_diff ** 2 + y_diff ** 2)
        volume += 0.5 * abs(x_diff) * abs(cur_spring.nx) * r12d
    return volume

def get_r12d(cur_spring):
    point1 = points[cur_spring.i]
    point2 = points[cur_spring.j]
    x_diff = point1.x - point2.x
    y_diff = point1.y - point2.y
    r12d = math.sqrt(x_diff ** 2 + y_diff ** 2)
    return r12d

def set_pressure_force():
    volume = get_volume()
    if volume <= 0:
        return

    for i in range(1, nump + 1):
        r12d = get_r12d(springs[i])
        pressurev = r12d * pressure * (1 / volume)
        point1 = my_points[springs[i].i]
        point2 = my_points[springs[i].j]
        point1.fx += springs[i].nx * pressurev
        point1.fy += springs[i].ny * pressurev
        point2.fx += springs[i].nx * pressurev
        point2.fy += springs[i].ny * pressurev

def integrate_euler():
    for i in range(1, nump + 1):
        cur_point = my_points[i]
        cur_point.vx = cur_point.vx + (cur_point.fx / mass) * dt
        cur_point.vy = cur_point.vy + (cur_point.fy / mass) * dt

        drx = cur_point.vx * dt
        dry = cur_point.vy * dt

        if cur_point.y + dry < -zoom:
            dry = -zoom - my_points[i].y
            my_points[i].vx = 0.95 * my_points[i].vx
            my_points[i].vy = -restitution * my_points[i].vy
        if cur_point.y + dry > zoom:
            dry = zoom - my_points[i].y
            my_points[i].vx = 0.95 * my_points[i].vx
            my_points[i].vy = -restitution * my_points[i].vy

        my_points[i].y = my_points[i].y + dry

        if cur_point.x + drx < -zoom:
            drx = -zoom - my_points[i].x
            my_points[i].vx = -restitution * my_points[i].vy
            my_points[i].vy = 0.95 * my_points[i].vy
        if cur_point.x + drx > zoom:
            drx = zoom - my_points[i].x
            my_points[i].vx = -restitution * my_points[i].vx
            my_points[i].vy = 0.95 * my_points[i].vy

        my_points[i].x = my_points[i].x + drx

        if my_points[i].x > zoom:
            my_points[i].x = zoom;
        if my_points[i].x < -zoom:
            my_points[i].x = -zoom;
        if my_points[i].y > zoom:
            my_points[i].y = zoom;
        if my_points[i].y < -zoom:
            my_points[i].y = -zoom;

def draw():
    glClearColor(1, 1, 1, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_QUADS)

    for i in range(1, nums):
        glColor3f(1, 0.4, 0.4)
        glVertex2f(my_points[springs[i].i].x, my_points[springs[i].i].y)
        glVertex2f(my_points[springs[i].j].x, my_points[springs[i].j].y)

        glVertex2f(my_points[nump - springs[i].i + 1].x, my_points[nump - springs[i].i + 1].y)
        glVertex2f(my_points[nump - springs[i].j + 1].x, my_points[nump - springs[i].j + 1].y)

    glEnd()
    pg.display.flip()
    pg.time.wait(10)

if __name__ == "__main__":
    main()