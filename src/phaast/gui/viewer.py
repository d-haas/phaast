from __future__ import annotations
from typing import TYPE_CHECKING, Any, Literal, cast
if TYPE_CHECKING:
    from phaast.gui.gui import GUI

import os
os.environ["PYOPENGL_PLATFORM"] = "glx"

import tkinter as tk
from math import acos, cos, degrees, sin, sqrt
import threading

import OpenGL.GL as gl
import OpenGL.GLU as glu

from pyopengltk.linux import OpenGLFrame
from phaast.vector import Vector
from phaast.structure import Atom, Structure
from phaast.calculators.xtb import XTB
from phaast.calculators.orca import Orca
from phaast.structure.constants import AtomicRadi, AtomicNumber

from phaast.gui import renderer
from phaast.gui.constants import *
from phaast.gui.input import InputHandler

class MolViewer(OpenGLFrame):
    def __init__(self, parent : GUI | tk.Misc, debug : bool = False, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.parent = parent
        self.debug = debug

        self.rotation = Vector()
        self.translation = Vector()

        self.structure : Structure = Structure(
            [Atom(1, Vector(0.0, 0.0, 0.0))],
        )

        self.rotation_quaternion : tuple[float, float, float, float] = (1.0,0.0,0.0,0.0)

        self.distance = -5.0

        self.input = InputHandler(self)

        self.ghost : Atom | None = None
        self.selected : Atom | None = None
        self.last_selected : Atom | None = None

        self.state : Literal[
            "view", "add", "move", "delete", "replace"
        ] = "view"

        self.chosen_z : AtomicNumber = 1

        self.cam_pos : Vector = Vector()
        self.cam_dir : Vector = Vector()
        self.mouse_dir : Vector = Vector(0.0, 0.0, 1.0)

        self.modelview = gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX)
        self.projection = gl.glGetDoublev(gl.GL_PROJECTION_MATRIX)
        self.viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)

        self.render_quality = 8

    def initgl(self):
        # Catppuccin (Mocha) crust color for background
        gl.glClearColor(17/255, 17/255, 27/255, 1)

    def optimize_xtb(self, options : dict[str, Any]) -> None:
        previous_state = self.state
        self.state = "view"
        if not isinstance(self.parent, tk.Misc):
            self.parent.disable_input()

        calc = XTB(**options)

        mol = calc.optimize(self.structure)

        if mol:
            self.structure = mol

        self.state = previous_state
        if not isinstance(self.parent, tk.Misc):
            self.parent.enable_input()

    def optimize_orca(self, options : dict[str, Any]) -> None:
        previous_state = self.state
        self.state = "view"
        if not isinstance(self.parent, tk.Misc):
            self.parent.disable_input()

        calc = Orca(**options)

        def temp_optimize_trj():
            for mol in calc.optimize_trj(self.structure):
                self.structure = mol
            self.state = previous_state
            if not isinstance(self.parent, tk.Misc):
                self.parent.enable_input()

        thread = threading.Thread(target = temp_optimize_trj)
        thread.start()

    def update_quaternion(self):
        ##############################
        # UPDATE ROTATION QUATERNION #
        ##############################
        rotation_axis : Vector = Vector(self.input.mouse_motion[1], self.input.mouse_motion[0], 0)
        rotation_angle : float = rotation_axis.mod * 5.7e-3
        if rotation_angle > 0:
            rotation_axis.normalize()

            w = cos(rotation_angle / 2)
            rotation_axis*= sin(rotation_angle / 2)

            dq : tuple[float, float, float, float] = ( #delta_quaternion
                w, rotation_axis.x, rotation_axis.y, rotation_axis.z,
            )

            rq = self.rotation_quaternion

            self.rotation_quaternion = (
                dq[0]*rq[0] - dq[1]*rq[1] - dq[2]*rq[2], # - dq[3]*rq[3], # dq[3] = 0!
                dq[0]*rq[1] + dq[1]*rq[0] + dq[2]*rq[3], # - dq[3]*rq[2], # dq[3] = 0!
                dq[0]*rq[2] - dq[1]*rq[3] + dq[2]*rq[0], # + dq[3]*rq[1], # dq[3] = 0!
                dq[0]*rq[3] + dq[1]*rq[2] - dq[2]*rq[1], # + dq[3]*rq[0], # dq[3] = 0!
            )

            quarternion_mod : float = sqrt(sum((i**2 for i in self.rotation_quaternion)))

            # Normalizing quaternion
            self.rotation_quaternion = cast(
                tuple[float, float, float, float],
                tuple(
                    (
                        i/quarternion_mod
                        for i
                        in self.rotation_quaternion
                    ),
                ),
            )

    def on_press(self):
        selected, collision_point = self.get_hovered()
        if selected and collision_point:
            self.selected = selected

    def on_release(self):
        self.selected = None

    def on_single_click(self):
        if self.hovered:
            match self.state:
                case "add":
                    if self.ghost:
                        self.structure = Structure(
                            tuple(self.structure) + (self.ghost,)
                        )
                case "delete":
                    self.structure = Structure(
                        tuple((atom for atom in self.structure if atom is not self.selected))
                    )
                case "replace":
                    self.hovered.z = self.chosen_z

            self.structure.center_mass()

    def on_move(self):
        selected, collision_point = self.get_hovered()
        if selected and collision_point:
            other = Atom(self.chosen_z)
            other.pos = selected.pos + (collision_point-selected.pos).normalized()*(selected.radius+other.radius)
            self.ghost = other
            self.hovered = selected
        else:
            self.ghost = None
            self.hovered = None

    def on_drag(self):
        self.get_hovered(change = False)
        if self.state == "move" and self.selected:
            self.move_selected()
        else:
            self.update_quaternion()

    def on_scroll(self, delta):
        self.distance+= float(delta)*5
        self.distance = max(
            -50.0,
            min(
                self.distance,
                -5.0,
            )
        )

    def move_selected(self):
        if TYPE_CHECKING:
            assert self.selected

        selected_plane_dist = (self.selected.pos - self.cam_pos) * self.cam_dir

        dir_scaling = selected_plane_dist / (self.mouse_dir * self.cam_dir)

        mouse_plane_location = self.cam_pos + dir_scaling*self.mouse_dir

        self.selected.pos = mouse_plane_location


    def get_hovered(self, change : bool = True) -> tuple[Atom | None, Vector | None]:

        real_x = self.input.mouse_pos[0] #self.viewport[2] - self.input.mouse_pos[0]
        real_y = self.viewport[3] - self.input.mouse_pos[1]

        self.cam_pos = Vector(
            *glu.gluUnProject(
                real_x,
                real_y,
                0.0,
                self.modelview,
                self.projection,
                self.viewport,
            ),
        )

        far_pos = Vector(
            *glu.gluUnProject(
                real_x,
                real_y,
                1.0,
                self.modelview,
                self.projection,
                self.viewport,
            )
        )


        far_center = Vector(
            *glu.gluUnProject(
                self.width/2,
                self.height/2,
                1.0,
                self.modelview,
                self.projection,
                self.viewport,
            )
        )
        
        self.mouse_dir = (far_pos - self.cam_pos).normalized()

        self.cam_dir = (far_center - self.cam_pos).normalized()
        
        selected : Atom | None = None
        collision_point : Vector | None = None

        if change:
            nearest_dist = float("inf")
            for atom in self.structure:
                # Check line-sphere collision
                distance_vector = atom.pos - self.cam_pos
                nearest_length = distance_vector*self.mouse_dir
                nearest_point = self.cam_pos + nearest_length*far_pos.normalized()
                nearest_point_to_atom_dist = (nearest_point-atom.pos).mod

                if nearest_point_to_atom_dist <= atom.radius/2 and nearest_length < nearest_dist:
                    nearest_dist = nearest_length
                    selected = atom
                    collision_point = nearest_point - sqrt((atom.radius/2)**2 - nearest_point_to_atom_dist**2)*self.mouse_dir

        return selected, collision_point



    def draw_mol(self):
        post_render : Atom | None = None
        for atom in self.structure:

            atom_color = ATOM_COLORS_RGB[atom.z]

            if self.debug:
                bond_color = cast(
                    tuple[float, float, float],
                    tuple(
                        ( i/3 for i in ATOM_COLORS_RGB[atom.z] ),
                    ),
                )
            else:
                bond_color = atom_color

            for other in self.structure:
                if atom is not other and atom.is_touching(other, 0.5):
                    

                    if self.render_quality <= 8:
                        renderer.draw_cylinder(
                            atom.pos,# + sqrt(15*(atom.radius**2)/64)*(other.pos-atom.pos).normalized(),
                            atom.pos + (other.pos - atom.pos) * (atom.radius/(atom.radius+other.radius)+0.001),
                            r1 = 0.051,#(atom.radius+other.radius)/16,
                            r2 = 0.051,#(atom.radius+other.radius)/16,
                            color = bond_color,
                            quality = self.render_quality*4,
                        )
                    else:
                        renderer.draw_cylinder_hyperbolic(
                            #atom.pos + sqrt(3*(atom.radius**2)/16)*(other.pos-atom.pos).normalized(), #For r1 = atom.radius/4
                            atom.pos + sqrt(15*(atom.radius**2)/64)*(other.pos-atom.pos).normalized(),
                            atom.pos + (other.pos - atom.pos) * atom.radius/(atom.radius+other.radius),
                            r1 = atom.radius/8, r2 = (atom.radius+other.radius)/32,
                            color = bond_color,
                            segments = self.render_quality*4,
                            quality = self.render_quality*4,
                        )

            if self.state == "replace" and atom is self.hovered:
                post_render = atom
            else:
                renderer.draw_sphere(
                    atom.pos,
                    atom.radius/2,
                    atom_color,
                    quality = self.render_quality*4,
                )

        if post_render:
            renderer.draw_sphere_alpha(post_render.pos, post_render.radius/2, ATOM_COLORS_RGB[post_render.z], alpha=0.5, quality = self.render_quality*4)
            renderer.draw_sphere_alpha(post_render.pos, AtomicRadi[self.chosen_z]/2, ATOM_COLORS_RGB[self.chosen_z], alpha=0.5, quality = self.render_quality*4)


    def draw_new_ghost(self):
        if self.ghost:
            for other in self.structure:
                if self.ghost.is_touching(other, 0.5):
                    renderer.draw_cylinder_alpha(
                        self.ghost.pos,
                        self.ghost.pos + (other.pos - self.ghost.pos) * self.ghost.radius/(self.ghost.radius+other.radius),
                        r1 = 0.1, r2 = 0.1,
                        color = ATOM_COLORS_RGB[self.ghost.z],
                        alpha = 0.51,
                        quality = self.render_quality*4,
                    )
                    renderer.draw_cylinder_alpha(
                        other.pos,
                        other.pos + (self.ghost.pos - other.pos) * other.radius/(other.radius+self.ghost.radius),
                        r1 = 0.1, r2 = 0.1,
                        color = ATOM_COLORS_RGB[other.z],
                        alpha = 0.51,
                        quality = self.render_quality*4,
                    )

            renderer.draw_sphere_alpha(self.ghost.pos, self.ghost.radius/2, ATOM_COLORS_RGB[self.ghost.z], alpha=0.51, quality=self.render_quality*4)

    def draw_deletion(self):
        if self.hovered:
            renderer.draw_sphere_alpha(
                self.hovered.pos,
                (self.hovered.radius + 0.1)/2,
                (1.0, 0.7, 0.7),
                alpha = 0.1,
                quality = self.render_quality*4,
            )


    def redraw(self):
        gl.glPushMatrix()

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glDepthFunc(gl.GL_LESS)  # Default
        gl.glEnable(gl.GL_LIGHTING)
        gl.glEnable(gl.GL_LIGHT0)
        gl.glEnable(gl.GL_COLOR_MATERIAL)
        gl.glColorMaterial(gl.GL_FRONT, gl.GL_AMBIENT_AND_DIFFUSE)
        gl.glShadeModel(gl.GL_SMOOTH)

        if not self.debug:
            gl.glLightfv(gl.GL_LIGHT0, gl.GL_POSITION, [0.0,300.0,0.0,0.0])
            gl.glLightfv(gl.GL_LIGHT0, gl.GL_DIFFUSE, [3.0,3.0,3.0,1.0])

        gl.glViewport(
            0,
            0,
            self.width,
            self.height,
        )

        glu.gluPerspective(45, self.width/self.height, 1, 1000.0)

        gl.glTranslated(0.0, 0.0, self.distance)

        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT) # type: ignore

        w = min(max(self.rotation_quaternion[0], -1), 1)
        rot_angle = 2 * acos(w)
        if rot_angle != 0:
            quat_sin = sin(rot_angle/2)
            axis = (Vector(*self.rotation_quaternion[1:4])/quat_sin).normalized()
            gl.glRotated(
                degrees(rot_angle),
                *axis,
            )

        self.modelview = gl.glGetDoublev(gl.GL_MODELVIEW_MATRIX)
        self.projection = gl.glGetDoublev(gl.GL_PROJECTION_MATRIX)
        self.viewport = gl.glGetIntegerv(gl.GL_VIEWPORT)

        self.draw_mol()

        match self.state:
            case "add":
                self.draw_new_ghost()
            case "delete":
                self.draw_deletion()

        gl.glPopMatrix()


    """
    def rotate_by_quat(self, pos : Vector) -> Vector:
        rot_axis = Vector(*self.rotation_quaternion[1:4])
        rot_w = self.rotation_quaternion[0]

        #return pos + rot_w*rot_axis.cross(pos) + 2.0*rot_axis.cross(rot_axis.cross(pos))
        t = 2.0 * rot_axis.cross(pos)
        return pos + (rot_w * t) + rot_axis.cross(t)
    """
