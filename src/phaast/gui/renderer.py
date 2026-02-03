from math import acos, pi, sqrt

from phaast.vector import Vector
import  OpenGL.GL as gl
import  OpenGL.GLU as glu

QUALITY = 37

def draw_sphere(pos : Vector, radius : float, color : tuple[float, float, float], quality = QUALITY):
    gl.glPushMatrix()

    gl.glTranslated(pos.x, pos.y, pos.z)

    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
    gl.glColor3d(*color)
    sphere = glu.gluNewQuadric()
    glu.gluSphere(sphere, radius, quality, quality)
    glu.gluDeleteQuadric(sphere)

    gl.glPopMatrix()

def draw_sphere_alpha(pos : Vector, radius : float, color : tuple[float, float, float], alpha : float, quality = QUALITY):
    gl.glPushMatrix()

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glDepthMask(gl.GL_FALSE)

    gl.glTranslated(pos.x, pos.y, pos.z)

    #glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
    gl.glColor4d(*color, alpha)
    sphere = glu.gluNewQuadric()
    gl.glFrontFace(gl.GL_CW)
    glu.gluSphere(sphere, radius, quality, quality)
    gl.glFrontFace(gl.GL_CCW)
    glu.gluSphere(sphere, radius, quality, quality)
    glu.gluDeleteQuadric(sphere)

    gl.glDepthMask(gl.GL_TRUE)
    gl.glDisable(gl.GL_BLEND)

    gl.glPopMatrix()

def draw_cylinder(start : Vector, end : Vector, r1 : float, r2 : float, color : tuple[float, float, float], quality = QUALITY):
    gl.glPushMatrix()

    gl.glTranslated(start.x, start.y, start.z)

    z_axis = Vector(0,0,1)

    height = (end-start).mod
    if height > 0:
        dir = (end-start).normalized()

        rot_dir = dir.cross(z_axis)

        if rot_dir.mod_sqr>0.0001:
            rot_dir.normalize()
            gl.glRotated(
                -180 * acos(dir * z_axis) / pi,
                #atan2(start.cross(end).mod, start*end) * 180 / pi,
                *rot_dir,
            )

        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        gl.glColor3d(*color)
        cylinder = glu.gluNewQuadric()
        glu.gluCylinder(cylinder, r1, r2, height, quality, quality)
        glu.gluDeleteQuadric(cylinder)

    gl.glPopMatrix()

def draw_cylinder_alpha(start : Vector, end : Vector, r1 : float, r2 : float, color : tuple[float, float, float], alpha : float, quality = QUALITY):
    gl.glPushMatrix()

    gl.glEnable(gl.GL_BLEND)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glDepthMask(gl.GL_FALSE)

    gl.glTranslated(start.x, start.y, start.z)

    z_axis = Vector(0,0,1)

    height = (end-start).mod
    if height > 0:

        dir = (end-start).normalized()

        rot_dir = dir.cross(z_axis)

        if rot_dir.mod_sqr>0.0001:
            rot_dir.normalize()
            gl.glRotated(
                -180 * acos(dir * z_axis) / pi,
                #atan2(start.cross(end).mod, start*end) * 180 / pi,
                *rot_dir,
            )

        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_FILL)
        gl.glColor4d(*color, alpha)
        cylinder = glu.gluNewQuadric()
        gl.glFrontFace(gl.GL_CW)
        glu.gluCylinder(cylinder, r1, r2, height, quality, quality)
        gl.glFrontFace(gl.GL_CCW)
        glu.gluCylinder(cylinder, r1, r2, height, quality, quality)
        glu.gluDeleteQuadric(cylinder)

    gl.glDepthMask(gl.GL_TRUE)
    gl.glDisable(gl.GL_BLEND)

    gl.glPopMatrix()

def draw_cylinder_hyperbolic(start : Vector, end : Vector, r1 : float, r2 : float, color : tuple[float, float, float], segments : int = 8, quality = QUALITY):
    segment_dir = (end-start)/float(segments)

    def hyperbole(z : float) -> float:
        return sqrt(r2**2 + (r1**2 - r2**2)*(1 - z)**2)
    
    for i in range(segments):
        initial_pos = start + (segment_dir*float(i))
        final_pos = start + (segment_dir*float(i+1))

        draw_cylinder(
            initial_pos,
            final_pos,
            r1 = hyperbole(i/segments),
            r2 = hyperbole((i+1)/segments),
            color = color,
            quality = quality,
        )
