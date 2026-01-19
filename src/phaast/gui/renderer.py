from math import acos, pi, sqrt

from phaast.vec import Vector
from OpenGL.GL import *
from OpenGL.GLU import *

QUALITY = 37

def draw_sphere(pos : Vector, radius : float, color : tuple[float, float, float]):
    glPushMatrix()

    glTranslated(pos.x, pos.y, pos.z)

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glColor3d(*color)
    sphere = gluNewQuadric()
    gluSphere(sphere, radius, QUALITY, QUALITY)
    gluDeleteQuadric(sphere)

    glPopMatrix()

def draw_sphere_alpha(pos : Vector, radius : float, color : tuple[float, float, float], alpha : float):
    glPushMatrix()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)

    glTranslated(pos.x, pos.y, pos.z)

    #glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    glColor4d(*color, alpha)
    sphere = gluNewQuadric()
    glFrontFace(GL_CW)
    gluSphere(sphere, radius, QUALITY, QUALITY)
    glFrontFace(GL_CCW)
    gluSphere(sphere, radius, QUALITY, QUALITY)
    gluDeleteQuadric(sphere)

    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)

    glPopMatrix()

def draw_cylinder(start : Vector, end : Vector, r1 : float, r2 : float, color : tuple[float, float, float]):
    glPushMatrix()

    glTranslated(start.x, start.y, start.z)

    z_axis = Vector(0,0,1)

    height = (end-start).mod
    if height > 0:
        dir = (end-start).normalized()

        rot_dir = dir.cross(z_axis)

        if rot_dir.mod_sqr>0.0001:
            rot_dir.normalize()
            glRotated(
                -180 * acos(dir * z_axis) / pi,
                #atan2(start.cross(end).mod, start*end) * 180 / pi,
                *rot_dir,
            )

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glColor3d(*color)
        cylinder = gluNewQuadric()
        gluCylinder(cylinder, r1, r2, height, QUALITY, QUALITY)
        gluDeleteQuadric(cylinder)

    glPopMatrix()

def draw_cylinder_alpha(start : Vector, end : Vector, r1 : float, r2 : float, color : tuple[float, float, float], alpha : float):
    glPushMatrix()

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glDepthMask(GL_FALSE)

    glTranslated(start.x, start.y, start.z)

    z_axis = Vector(0,0,1)

    height = (end-start).mod
    if height > 0:

        dir = (end-start).normalized()

        rot_dir = dir.cross(z_axis)

        if rot_dir.mod_sqr>0.0001:
            rot_dir.normalize()
            glRotated(
                -180 * acos(dir * z_axis) / pi,
                #atan2(start.cross(end).mod, start*end) * 180 / pi,
                *rot_dir,
            )

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glColor4d(*color, alpha)
        cylinder = gluNewQuadric()
        glFrontFace(GL_CW)
        gluCylinder(cylinder, r1, r2, height, QUALITY, QUALITY)
        glFrontFace(GL_CCW)
        gluCylinder(cylinder, r1, r2, height, QUALITY, QUALITY)
        gluDeleteQuadric(cylinder)

    glDepthMask(GL_TRUE)
    glDisable(GL_BLEND)

    glPopMatrix()

def draw_cylinder_hyperbolic(start : Vector, end : Vector, r1 : float, r2 : float, color : tuple[float, float, float], segments : int = 8):
    segment_dir = (end-start)/float(segments)

    def hyperbole(z : float) -> float:
        return sqrt(r2**2 + (r1**2 - r2**2)*(1 - z)**2)
        #return r1 + (r2-r1)*sqrt(z)
    
    for i in range(segments):
        initial_pos = start + (segment_dir*float(i))
        final_pos = start + (segment_dir*float(i+1))

        draw_cylinder(
            initial_pos,
            final_pos,
            r1 = hyperbole(i/segments),
            r2 = hyperbole((i+1)/segments),
            color = color,
        )
