# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


import bpy
from mathutils import Vector
import numpy as np
from math import sqrt, radians, pi
import random


class crop_geometry(bpy.types.Operator):
    bl_idname = "object.crop_geometry"
    bl_label = "Crop Geometry"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        ob = context.object
        patientID = ob.waspmed_prop.patientID
        status = ob.waspmed_prop.status
        for o in bpy.data.objects:
            id = o.waspmed_prop.patientID
            s = o.waspmed_prop.status
            if patientID == id and s == status-1:
                ob.data = o.to_mesh(bpy.context.scene, apply_modifiers=True,
                settings='PREVIEW')
        bpy.ops.object.mode_set(mode='EDIT')

        side = False
        bpy.ops.mesh.select_all(action='SELECT')
        locx = bpy.data.objects['Plane X0'].constraints[0].min_x
        bpy.ops.mesh.bisect(plane_co=(locx,0,0), plane_no=(-1,0,0), use_fill=side, clear_outer=True)

        bpy.ops.mesh.select_all(action='SELECT')
        locx = bpy.data.objects['Plane X1'].constraints[0].max_x
        bpy.ops.mesh.bisect(plane_co=(locx,0,0), plane_no=(1,0,0), use_fill=side, clear_outer=True)

        bpy.ops.mesh.select_all(action='SELECT')
        locz = bpy.data.objects['Plane Z0'].constraints[0].min_z
        bpy.ops.mesh.bisect(plane_co=(0,0,locz), plane_no=(0,0,-1), use_fill=False, clear_outer=True)

        bpy.ops.mesh.select_all(action='SELECT')
        locz = bpy.data.objects['Plane Z1'].constraints[0].max_z
        bpy.ops.mesh.bisect(plane_co=(0,0,locz), plane_no=(0,0,1), use_fill=False, clear_outer=True)


        bpy.ops.object.mode_set(mode='OBJECT')
        return {'FINISHED'}


class define_crop_planes(bpy.types.Operator):
    bl_idname = "object.define_crop_planes"
    bl_label = "Define Crop Planes"
    bl_description = ("")
    bl_options = {'REGISTER', 'UNDO'}

    x0 = bpy.props.FloatProperty(
        name="Trim X0", default=0.00, soft_min=0, soft_max=500,
        description="Trim X0")
    x1 = bpy.props.FloatProperty(
        name="Trim X1", default=0.00, soft_min=-500, soft_max=0,
        description="Trim X1")
    y0 = bpy.props.FloatProperty(
        name="Trim Y0", default=0.00, soft_min=0, soft_max=500,
        description="Trim Y0")
    y1 = bpy.props.FloatProperty(
        name="Trim Y1", default=0.00, soft_min=-500, soft_max=0,
        description="Trim Y1")
    z0 = bpy.props.FloatProperty(
        name="Trim Z0", default=0.00, soft_min=0, soft_max=500,
        description="Trim Z0")
    z1 = bpy.props.FloatProperty(
        name="Trim Z1", default=0.00, soft_min=-500, soft_max=0,
        description="Trim Z1")

    @classmethod
    def poll(cls, context):
        if context.mode == 'OBJECT':
            ob = context.object
            if ob.type == 'MESH': return True
            elif ob.type == 'EMPTY' and ob.parent != None: return True
            else: return False
        else: return False

    def draw(self, context):
        layout = self.layout
        #layout.label(text="Examples")
        ob = context.object
        layout.label(text="Crop X")
        row=layout.row(align=True)
        row.prop(self, "x0", text="X0")
        row.prop(self, "x1", text="X1")
        layout.label(text="Crop Y")
        row=layout.row(align=True)
        row.prop(self, "y0", text="Y0")
        row.prop(self, "y1", text="Y1")
        layout.label(text="Crop Z")
        row=layout.row(align=True)
        row.prop(self, "z0", text="Z0")
        row.prop(self, "z1", text="Z1")

    def execute(self, context):
        ob = context.object
        if ob.type == 'EMPTY':
            empty = ob
            ob = empty.parent
            bpy.data.objects.remove(empty)
        for c in ob.children:
            #if c.type == 'EMPTY':
            bpy.data.objects.remove(c)

        patientID = ob.waspmed_prop.patientID
        status = ob.waspmed_prop.status
        for o in bpy.data.objects:
            id = o.waspmed_prop.patientID
            s = o.waspmed_prop.status
            if patientID == id and s == status-1:
                ob.data = o.to_mesh(bpy.context.scene, apply_modifiers=True,
                settings='PREVIEW')
        #bpy.ops.object.empty_add(type='CUBE')
        #empty = context.object

        #context.scene.objects.active = ob
        #ob.select = True
        #bpy.ops.object.parent_set(type='OBJECT', keep_transform=True)

        #empty.parent = ob
        bb0 = Vector(ob.bound_box[0])
        bb1 = Vector(ob.bound_box[6])
        bb0 += Vector((self.x0, self.y0, self.z0))
        bb1 += Vector((self.x1, self.y1, self.z1))
        bb_origin = (bb0+bb1)/2
        #empty.location = bb_origin

        alpha = 0.4

        # Planes X
        bpy.ops.mesh.primitive_plane_add(
            radius=1000,
            location=(bb_origin.x + bb0.x, bb_origin.y, bb_origin.z),
            rotation=(0, -pi/2, 0))
        plane_x0 = context.object
        plane_x0.name = "Plane X0"
        plane_x0.constraints.new(type='LIMIT_LOCATION')
        plane_x0.constraints[0].use_min_x = True
        plane_x0.constraints[0].min_x = bb0.x
        plane_x0.dimensions = ob.dimensions.zyx
        plane_x0.hide_select = True
        plane_x0.parent = ob

        mat = bpy.data.materials.new(name="Material")
        context.object.data.materials.append(mat)
        context.object.active_material.diffuse_color = (1, 1, 1)
        context.object.active_material.use_transparency = True
        context.object.active_material.alpha = alpha
        context.object.active_material.use_object_color = True
        context.object.show_transparent = True
        bpy.context.object.show_wire = True

        bpy.ops.mesh.primitive_plane_add(
            radius=1000,
            location=(bb_origin.x - bb0.x, bb_origin.y, bb_origin.z),
            rotation=(0, pi/2, 0))
        plane_x1 = context.object
        plane_x1.name = "Plane X1"
        plane_x1.constraints.new(type='LIMIT_LOCATION')
        plane_x1.constraints[0].use_max_x = True
        plane_x1.constraints[0].max_x = bb1.x
        plane_x1.dimensions = ob.dimensions.zyx
        plane_x1.hide_select = True
        plane_x1.parent = ob
        context.object.data.materials.append(mat)
        context.object.show_transparent = True
        bpy.context.object.show_wire = True


        '''
        # Planes Y
        bpy.ops.mesh.primitive_plane_add(
            radius=1000,
            location=(bb_origin.x, bb_origin.y + bb0.y, bb_origin.z),
            rotation=(-pi/2, 0, 0))
        plane_y0 = context.object
        plane_y0.name = "Plane Y0"
        plane_y0.constraints.new(type='LIMIT_LOCATION')
        plane_y0.constraints[0].use_min_y = True
        plane_y0.constraints[0].min_y = bb0.y
        plane_y0.dimensions = ob.dimensions.xzy
        plane_y0.hide_select = True
        plane_y0.parent = ob

        bpy.ops.mesh.primitive_plane_add(
            radius=1000,
            location=(bb_origin.x, bb_origin.y - bb0.y, bb_origin.z),
            rotation=(pi/2, 0,  0))
        plane_y1 = context.object
        plane_y1.name = "Plane Y1"
        plane_y1.constraints.new(type='LIMIT_LOCATION')
        plane_y1.constraints[0].use_max_y = True
        plane_y1.constraints[0].max_y = bb1.y
        plane_y1.dimensions = ob.dimensions.xzy
        plane_y1.hide_select = True
        plane_y1.parent = ob
        '''

        # Planes Z
        bpy.ops.mesh.primitive_plane_add(
            radius=1000,
            location=(bb_origin.x, bb_origin.y, bb_origin.z + bb0.z),
            rotation=(0, pi, 0))
        plane_z0 = context.object
        plane_z0.name = "Plane Z0"
        plane_z0.constraints.new(type='LIMIT_LOCATION')
        plane_z0.constraints[0].use_min_z = True
        plane_z0.constraints[0].min_z = bb0.z
        plane_z0.dimensions = ob.dimensions.xyz
        plane_z0.hide_select = True
        plane_z0.parent = ob

        mat = bpy.data.materials.new(name="Material")
        context.object.data.materials.append(mat)
        context.object.active_material.diffuse_color = (0, .1, 1)
        context.object.active_material.use_transparency = True
        context.object.active_material.alpha = alpha
        context.object.active_material.use_object_color = True
        context.object.show_transparent = True
        bpy.context.object.show_wire = True


        bpy.ops.mesh.primitive_plane_add(
            radius=1000,
            location=(bb_origin.x, bb_origin.y, bb_origin.z - bb0.z),
            rotation=(0, 0, 0))
        plane_z1 = context.object
        plane_z1.name = "Plane Z1"
        plane_z1.constraints.new(type='LIMIT_LOCATION')
        plane_z1.constraints[0].use_max_z = True
        plane_z1.constraints[0].max_z = bb1.z
        plane_z1.dimensions = ob.dimensions.xyz
        plane_z1.hide_select = True
        plane_z1.parent = ob
        context.object.data.materials.append(mat)
        context.object.show_transparent = True
        bpy.context.object.show_wire = True

        for c in ob.children:
            #c.draw_type = 'BOUNDS'
            c.select = False
        context.scene.objects.active = ob
        ob.select = True
        return {'FINISHED'}

class waspmed_crop_panel(bpy.types.Panel):
#class waspmed_scan_panel(, bpy.types.View3DPaintPanel):
    bl_label = "Crop"
    bl_category = "Waspmed"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    #bl_options = {}
    #bl_context = "objectmode"

    #@classmethod
    #def poll(cls, context):
    #    return context.mode in {'OBJECT', 'EDIT_MESH'}

    @classmethod
    def poll(cls, context):
        try:
            ob = context.object
            status = ob.waspmed_prop.status
            is_mesh = ob.type == 'MESH'
            return status == 4 and is_mesh and not context.object.hide
        except: return False

    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        col.operator("object.define_crop_planes", text="Setting Crop Planes", icon="SETTINGS")
        col.separator()
        try:
            row = col.row(align=True)
            row.prop(bpy.data.objects['Plane X0'].constraints['Limit Location'], "min_x", text="Left")
            row.prop(bpy.data.objects['Plane X1'].constraints['Limit Location'], "max_x", text="Right")
            col.separator()
            #row = col.row(align=True)
            #row.prop(bpy.data.objects['Plane Y0'].constraints['Limit Location'], "min_y", text="Y0")
            #row.prop(bpy.data.objects['Plane Y1'].constraints['Limit Location'], "max_y", text="Y1")
            row = col.row(align=True)
            row.prop(bpy.data.objects['Plane Z0'].constraints['Limit Location'], "min_z", text="Bottom")
            row.prop(bpy.data.objects['Plane Z1'].constraints['Limit Location'], "max_z", text="Top")
            col.separator()
            col.operator("object.crop_geometry", text="Crop Geometry", icon="MOD_DECIM")
        except:
            pass
        col.separator()
        box = layout.box()
        col = box.column(align=True)
        col.operator("view3d.ruler", text="Ruler", icon="ARROW_LEFTRIGHT")
        col.separator()
        col.operator("screen.region_quadview", text="Toggle Quad View", icon='SPLITSCREEN')
        col.separator()
        row = col.row(align=True)
        row.operator("ed.undo", icon='LOOP_BACK')
        row.operator("ed.redo", icon='LOOP_FORWARDS')


def register():
    bpy.utils.register_class(waspmed_crop_panel)
    bpy.utils.register_class(define_crop_planes)
    bpy.utils.register_class(crop_geometry)


def unregister():
    bpy.utils.unregister_class(waspmed_crop_panel)
    bpy.utils.unregister_class(define_crop_planes)
    bpy.utils.unregister_class(crop_geometry)


if __name__ == "__main__":
    register()