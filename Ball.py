import math

from OpenGL.raw.GLUT import glutSwapBuffers

from Material import *
from Spring import *
import pygame as pg
from OpenGL.GL import *
from OpenGL.GLU import *

nump = 5
nums = nump + 1
radius = 10
screen = (500, 500)
PI = math.pi
springs = [Spring() for i in range(nums)]
points = [Material() for i in range(nump)]
my_points = points.copy()

mass = 2
pressure = 2
final_pressure = 700
KS = 0.5 # elasticity factor (spring)
KD = 0.4 # elasticity factor (damping)
dt = 0.25

def main():
    pg.init()
    pg.display.set_mode(screen, GL_DOUBLEBUFFER | pg.OPENGL)
    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                quit()

        create_ball()
        draw()


def create_ball():
    for i in range(1, nump):
        points[i].x = radius * math.sin(i * (2 * PI) / nump)
        points[i].y = radius * math.cos(i * (2 * PI) / nump) + (screen[1] / 2)
        print(points[i].describe())

    for i in range(1, nump-1):
        add_spring(i, i, i+1)
        add_spring(i-1, i-1, 1)
        print(springs[i].describe())

    for i in range(1, nump):
        points[i].fx = 0
        points[i].fy = mass * 9.81
        if pressure - final_pressure < 0:
            points[i].fy = 0

    set_force()
    set_pressure_force()
    integrate_euler()

def add_spring(index, i, j):
    springs[index].i = i
    springs[index].j = j
    springs[index].length = math.sqrt(((points[i].x - points[j].x) ** 2) + ((points[i].y - points[j].y) ** 2))

def set_force():
    for i in range(1, nums-1):
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

def get_volume():
    volume = 0
    for i in range(1, nump-1):
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
    for i in range(1, nump-1):
        r12d = get_r12d(springs[i])
        pressurev = r12d * pressure * (1 / get_volume())
        point1 = my_points[springs[i].i]
        point2 = my_points[springs[i].j]
        point1.fx += springs[i].nx * pressurev
        point2.fy += springs[i].ny * pressurev

def integrate_euler():
    for i in range(1, nump-1):
        cur_point = my_points[i]
        cur_point.vx = cur_point.vx + (cur_point.fx / mass) * dt
        cur_point.x = cur_point.x + cur_point.vx * dt
        cur_point.vy = cur_point.vy + cur_point.fy * dt
        dry = cur_point.vy * dt

        if cur_point.y + dry < -screen[1]:
            dry = -screen[1] - my_points[i].y
            my_points[i].vy = -0.1 * my_points[i].vy
        my_points[i].y = my_points[i].y + dry

def draw():
    glClearColor(1, 1, 1, 0)
    glClear(GL_COLOR_BUFFER_BIT)
    glBegin(GL_QUADS)

    for i in range(1, nums-1):
        glColor3f(1, 0.4, 0.4)
        glVertex2f(my_points[springs[i].i].x, my_points[springs[i].i].y)
        glVertex2f(my_points[springs[i].j].x, my_points[springs[i].j].y)

        glVertex2f(my_points[nump - springs[i].i + 1].x, my_points[nump - springs[i].i + 1].y)
        glVertex2f(my_points[nump - springs[i].j + 1].x, my_points[nump - springs[i].j + 1].y)

    glEnd()
    glutSwapBuffers()


if __name__ == "__main__":
    main()
    # create_ball()