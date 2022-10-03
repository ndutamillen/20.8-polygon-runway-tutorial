# Blender Adoon BagaPie Modifier
# Created by Antoine Bagattini

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.

#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.


# _______________________________________________ HELLO !

# This addon is free, you can use it for any purpose, modify it and share it.

# Special thanks to Franck Demongin which greatly contributed to this addon.

# Also thanks to all the people who support the development of this addon.
# Thanks to Sybren A. Stüvel (Scripting for artist on Blender Cloud), Drarkfall (Youtube).

# I'm not a programmer, just a newbie to Python. This code is not very good but it works.
# If you have any idea/advice to improve this addon, do not hesitate to contact me !

# _______________________________________________ USER INTERFACE / OP PANEL AND N PANEL

bl_info = {
    "name": "BagaPie Modifier",
    "author": "Antoine Bagattini",
    "version": (0, 6, 2, 2),
    "description": "Use a pie menu to add modifier and Geometry Nodes preset.",
    "blender": (3, 1, 0),
    "cathegory": "3D view",
    "location": "Pie Menue, shortcut : J"
}

from re import T
import bpy
from bpy.types import Menu, Operator, Panel

from . bagapie_ui import (
    BAGAPIE_MT_pie_menu,
    BAGAPIE_PT_modifier_panel, 
    MY_UL_List,
    BAGAPIE_OP_modifierDisplay,
    BAGAPIE_OP_modifierDisplayRender,
    BAGAPIE_OP_modifierApply,
    BAGAPIE_OP_addparttype,
    BAGAPIE_OP_switchinput,
    BAGAPIE_OP_switchboolnode,
    BagaPie_tooltips,
)
from . bagapie_ui_op import ( 
    SwitchMode,
    EditMode,
    UseSolidify,
    InvertPaint,
    CleanWPaint,
    InvertWeight,
    ADD_Assets,
    REMOVE_Assets,
    Rename_Layer,
)
from . bagapie_boolean_op import BAGAPIE_OT_boolean, BAGAPIE_OT_boolean_remove
from . bagapie_wall_op import BAGAPIE_OT_wall_remove, BAGAPIE_OT_wall
from . bagapie_array_op import BAGAPIE_OT_array_remove, BAGAPIE_OT_array, BAGAPIE_OT_drawarray
from . bagapie_scatter_op import BAGAPIE_OT_scatter_remove, BAGAPIE_OT_scatter, UseProperty, Use_Proxy_On_Assets, Use_Camera_Culling_On_Layer
from . bagapie_scatterpaint_op import BAGAPIE_OT_scatterpaint_remove, BAGAPIE_OT_scatterpaint
from . bagapie_displace_op import BAGAPIE_OT_displace_remove, BAGAPIE_OT_displace
from . bagapie_curvearray_op import BAGAPIE_OT_curvearray_remove, BAGAPIE_OT_curvearray
from . bagapie_window_op import BAGAPIE_OT_window_remove, BAGAPIE_OT_window
from . bagapie_group_op import BAGAPIE_OT_ungroup, BAGAPIE_OT_group, BAGAPIE_OT_editgroup, BAGAPIE_OT_lockgroup, BAGAPIE_OT_duplicategroup, BAGAPIE_OT_duplicatelinkedgroup, BAGAPIE_OT_deletegroup
from . bagapie_instance_op import BAGAPIE_OT_makereal, BAGAPIE_OT_instance
from . bagapie_pointeffector_op import BAGAPIE_OT_pointeffector_remove, BAGAPIE_OT_pointeffector
from . bagapie_import_op import BAGAPIE_OT_importnodes
from . bagapie_proxy_op import BAGAPIE_OT_proxy, BAGAPIE_OT_proxy_remove
from . bagapie_wallbrick_op import BAGAPIE_OT_wallbrick, BAGAPIE_OT_wallbrick_remove
from . bagapie_ivy_op import BAGAPIE_OT_ivy, BAGAPIE_OT_ivy_remove, BAGAPIE_OT_AddVertOBJ, BAGAPIE_OT_AddObjectTarget, BAGAPIE_OT_RemoveObjectTarget
from . bagapie_pointsnapinstance import BAGAPIE_OT_pointsnapinstance, BAGAPIE_OT_pointsnapinstance_remove
from . bagapie_instancesdisplace_op import BAGAPIE_OT_instancesdisplace, BAGAPIE_OT_instancesdisplace_remove
from . bagapie_saveasset_op import BAGAPIE_OT_saveasset, BAGAPIE_OT_saveasset_list, BAGAPIE_OT_savematerial, UseLibrary
from . bagapie_pipes_op import BAGAPIE_OT_pipes, BAGAPIE_OT_pipes_remove
from . bagapie_beamwire_op import BAGAPIE_OT_beamwire, BAGAPIE_OT_beamwire_remove
from . bagapie_stairlinear_op import BAGAPIE_OT_stairlinear,BAGAPIE_OT_stairlinear_remove
from . bagapie_stairspiral_op import BAGAPIE_OT_stairspiral, BAGAPIE_OT_stairspiral_remove
from . bagapie_beam_op import BAGAPIE_OT_beam, BAGAPIE_OT_beam_remove
from . bagapie_floor_op import BAGAPIE_OT_floor, BAGAPIE_OT_floor_remove
from . bagapie_handrail_op import BAGAPIE_OT_handrail, BAGAPIE_OT_handrail_remove
from . bagapie_column_op import BAGAPIE_OT_column, BAGAPIE_OT_column_remove
from . bagapie_twist_op import BAGAPIE_OT_deform, BAGAPIE_OT_deform_remove
from . bagapie_camera_op import BAGAPIE_OT_camera, BAGAPIE_OT_camera_remove

# _______________________________________________ REGISTER / UNREGISTER

class BagapieSettings(bpy.types.PropertyGroup):
    val: bpy.props.StringProperty()

class bagapie_Preferences(bpy.types.AddonPreferences):
    bl_idname = __name__

    security_features: bpy.props.BoolProperty(name="Security Features", default=True)
    use_default_proxy: bpy.props.BoolProperty(name="Use Default Proxy", default=True)
    apply_scale_default: bpy.props.BoolProperty(name="Apply Scale Default", default=True)
    use_camera_culling: bpy.props.BoolProperty(name="Apply Scale Default", default=True)
    maximum_polycount: bpy.props.IntProperty(name="Maximum Polycount", default=10000000, min = 0)
    polycount_for_proxy: bpy.props.IntProperty(name="Minimum Polycount", default=100000, min = 0)
    default_percent_display: bpy.props.IntProperty(name="Display percentage", default=100, min = 0, max = 100)

    def draw(self, context):
        layout = self.layout
        wm = context.window_manager

        pref = context.preferences.addons['Bagapie'].preferences
        box = layout.box()
        box.label(text="Scattering Preferences :", icon = "OUTLINER_DATA_HAIR")
        box.label(text="Scatter from previous BagaPie Version aren't compatible with this new version.", icon = "INFO")
        box.prop(pref, 'use_default_proxy', text="Enable proxy by default.")
        if pref.use_default_proxy == True:
            box.prop(pref, 'polycount_for_proxy', text="Minimum polycount for proxy.")
            
        box.prop(pref, 'security_features', text="Use security features for scattering :", icon = "LOCKED")
        if pref.security_features == True:
            row = box.row()
            col = row.column()
            col.separator(factor = 2)

            col = row.column()
            col.prop(pref, 'maximum_polycount', text="Maximum polycount to trigger security features.")
            col.label(text="(Total of average polycount instances * instances count)")
            col.separator(factor = 1)
            col.prop(pref, 'default_percent_display', text="Percentage of instances displayed in the viewport")
            col.prop(pref, 'apply_scale_default', text="Proposes to apply the scale of the target if it is not at 1,1,1.")
            col.prop(pref, 'use_camera_culling', text="Use Camera Culling if it's present.")

        col = layout.column(align=True)
        col.scale_y = 1.5
        col.operator("wm.url_open", text="Get BagaPie Assets !", icon = 'FUND').url = "https://abaga.gumroad.com/l/GcYmPC"
        col.operator("wm.url_open", text="BagaPie Documentation", icon = 'TEXT').url = "https://www.f12studio.fr/bagapiev6"
        col.operator("wm.url_open", text="Help - Support - Bug Report on Discord", icon = 'COMMUNITY').url = "https://discord.gg/YtagqdPW6G"
        col.operator("wm.url_open", text="Help - Support - Bug Report on BlenderArtists", icon = 'COMMUNITY').url = "https://blenderartists.org/t/bagapie-modifier-free-addon/1310959"
        col.operator("wm.url_open", text="Youtube Tutorial", icon = 'PLAY').url = "https://www.youtube.com/playlist?list=PLSVXpfzibQbh_qjzCP2buB2rK1lQtkQvu"

        box = layout.box()
        box = box.column(align=True)
        box.label(text="How to use BagaPie Modifier :")
        box.separator(factor = 2)
        box.scale_y = 0.8
        box.label(text="BagaPie is a collection of Tree Nodes made with Geometry Nodes or modfier presets.")
        box.label(text="Depending on the tool you choose, you must select one or more objects (list below).")
        box.separator(factor = 2)
        box.label(text="After selecting your object(s), press J key.")
        box.label(text="You can then choose a modifier in the pie menu (scatter, boolean, displace, ...).")
        box.label(text="Then access the BagaPie panel (aka N panel [N key]) where all the parameters are organized.")
        box = layout.box()
        box = box.column(align=True)
        box.scale_y = 1.2
        box.label(text="Object selection & type for each modifier:")
        box.separator(factor = 2)
        box.label(text="Deformation :", icon ='MOD_DISPLACE')
        box.label(text="    Displace : One object | type mesh")
        box.label(text="    Instances Displace : One object with instances on it | type mesh or curve")
        box.label(text="    Instances Displace : One object | type mesh or curve")
        box.separator(factor = 1)
        box.label(text="Array :", icon = "MOD_ARRAY")
        box.label(text="    Line : One object | type mesh or curve")
        box.label(text="    Grid : One object | type mesh or curve")
        box.label(text="    Circle : One object | type mesh or curve")
        box.label(text="    Curve : Multiple objects & Curve as active object | type mesh and Curve")
        box.separator(factor = 1)
        box.label(text="Manage :", icon = "PACKAGE")
        box.label(text="    Proxy : One or multiple object(s) | type mesh")
        box.label(text="    Save as Asset : One object | type mesh or curve")
        box.label(text="    Save Material : One object | type mesh or curve")
        box.label(text="    Group : One or multiple object(s) | type mesh or curve")
        box.separator(factor = 1)
        box.label(text="Scattering :", icon = "OUTLINER_DATA_HAIR")
        box.label(text="    Scatter : Multiple object(s) | type mesh")
        box.label(text="    Scatter Paint : Multiple object(s) | type mesh")
        box.label(text="    Point Snap Instance : Multiple object(s) | type mesh")
        box.label(text="    Ivy : One or multiple object(s) | type mesh")
        box.separator(factor = 1)
        box.label(text="Boolean :", icon = "MOD_BOOLEAN")
        box.label(text="    Union : One object | type mesh")
        box.label(text="    Difference : One object | type mesh")
        box.separator(factor = 1)
        box.label(text="Effector :", icon = "PARTICLES")
        box.label(text="    Point Effector : One or multiple object(s) and target | type mesh")
        box.label(text="    CamCulling : Camera and target | type camera or empty")
        box.separator(factor = 1)
        box.label(text="Architecture :", icon = "HOME")
        box.label(text="    Wall : One object | type mesh or curve")
        box.label(text="    Wall Brick : One object | type mesh or curve")
        box.label(text="    Window : One object | type mesh")
        box.label(text="    Pipes : One or multiple object(s) | type mesh")
        box.label(text="    Beam Wire : Nothing | None")
        box.label(text="    Beam : Nothing | None")
        box.label(text="    Stair Linear : Nothing | None")
        box.label(text="    Stair Spiral : Nothing | None")
        box.label(text="    Floor : Nothing | None")
        box.label(text="    Handrail : One object or Nothing | type curve")
        box.label(text="    Column : Nothing | None")
        box.separator(factor = 1)
        box.label(text="Curves :", icon = "MOD_CURVE")
        box.label(text="    Auto Array on Curve : Two object | type mesh and curve")


bpy.utils.register_class(BagapieSettings)
# bpy.utils.register_class(BagapiePreferences)

addon_keymaps = []
addon_keymaps_group = []
addon_keymaps_grouplink = []
classes = [
    bagapie_Preferences,
    BAGAPIE_MT_pie_menu,
    BAGAPIE_PT_modifier_panel,
    MY_UL_List,
    BAGAPIE_OP_switchboolnode,
    SwitchMode,
    EditMode,
    UseSolidify,
    InvertPaint,
    CleanWPaint,
    ADD_Assets,
    UseProperty,
    REMOVE_Assets,
    Rename_Layer,
    Use_Camera_Culling_On_Layer,
    Use_Proxy_On_Assets,
    InvertWeight,
    BAGAPIE_OT_wall_remove,
    BAGAPIE_OT_array_remove,
    BAGAPIE_OT_scatter_remove,
    BAGAPIE_OT_scatterpaint_remove,
    BAGAPIE_OT_displace_remove,
    BAGAPIE_OT_curvearray_remove,
    BAGAPIE_OT_window_remove,
    BAGAPIE_OT_ungroup,
    BAGAPIE_OT_makereal,
    BAGAPIE_OT_pointeffector_remove,
    BAGAPIE_OT_boolean,
    BAGAPIE_OT_boolean_remove,
    BAGAPIE_OT_wall,
    BAGAPIE_OT_array,
    BAGAPIE_OT_drawarray,
    BAGAPIE_OT_scatter,
    BAGAPIE_OT_scatterpaint,
    BAGAPIE_OT_displace,
    BAGAPIE_OT_curvearray,
    BAGAPIE_OT_window,
    BAGAPIE_OP_addparttype,
    BAGAPIE_OT_group,
    BAGAPIE_OT_editgroup,
    BAGAPIE_OT_lockgroup,
    BAGAPIE_OT_duplicategroup,
    BAGAPIE_OT_duplicatelinkedgroup,
    BAGAPIE_OT_deletegroup,
    BAGAPIE_OP_modifierDisplay,
    BAGAPIE_OP_modifierDisplayRender,
    BAGAPIE_OP_modifierApply,
    BAGAPIE_OT_instance,
    BAGAPIE_OT_pointeffector,
    BAGAPIE_OT_importnodes,
    BAGAPIE_OT_proxy_remove,
    BAGAPIE_OT_proxy,
    BAGAPIE_OT_wallbrick,
    BAGAPIE_OT_wallbrick_remove,
    BAGAPIE_OT_ivy,
    BAGAPIE_OT_ivy_remove,
    BAGAPIE_OT_AddObjectTarget,
    BAGAPIE_OT_RemoveObjectTarget,
    BAGAPIE_OT_AddVertOBJ,
    BAGAPIE_OT_pointsnapinstance,
    BAGAPIE_OT_pointsnapinstance_remove,
    BAGAPIE_OT_instancesdisplace,
    BAGAPIE_OT_instancesdisplace_remove,
    BAGAPIE_OT_saveasset,
    BAGAPIE_OT_saveasset_list,
    BAGAPIE_OT_savematerial,
    UseLibrary,
    BAGAPIE_OT_pipes,
    BAGAPIE_OT_pipes_remove,
    BAGAPIE_OP_switchinput,
    BAGAPIE_OT_beamwire,
    BAGAPIE_OT_beamwire_remove,
    BAGAPIE_OT_stairlinear,
    BAGAPIE_OT_stairlinear_remove,
    BAGAPIE_OT_stairspiral,
    BAGAPIE_OT_stairspiral_remove,
    BAGAPIE_OT_beam,
    BAGAPIE_OT_beam_remove,
    BAGAPIE_OT_floor,
    BAGAPIE_OT_floor_remove,
    BAGAPIE_OT_handrail,
    BAGAPIE_OT_handrail_remove,
    BAGAPIE_OT_column,
    BAGAPIE_OT_column_remove,
    BAGAPIE_OT_deform,
    BAGAPIE_OT_deform_remove,
    BAGAPIE_OT_camera,
    BAGAPIE_OT_camera_remove,
    BagaPie_tooltips,
    ]

    
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        kmi = km.keymap_items.new("wm.call_menu_pie", type='J', value='PRESS')
        kmi.properties.name = "BAGAPIE_MT_pie_menu"
        addon_keymaps.append((km,kmi))
        # Group Shortcut
        # Duplicate
        dupli = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        dupli_id = km.keymap_items.new("bagapie.duplicategroup", type='J', alt=True, value='PRESS')
        addon_keymaps_group.append((dupli,dupli_id))
        # Duplicate linked
        dupli_link = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        dupli_id_link = km.keymap_items.new("bagapie.duplicatelinkedgroup", type='N', alt=True, value='PRESS')
        addon_keymaps_grouplink.append((dupli_link,dupli_id_link))

    bpy.types.Scene.bagapieValue = bpy.props.StringProperty(
        name="My List",
        default="none"
    )

    bpy.types.Object.bagapieList = bpy.props.CollectionProperty(type=BagapieSettings)
    bpy.types.Object.bagapieIndex = bpy.props.IntProperty(name="Index", default=0)

    # bpy.types.Scene.bagapiePref = bpy.props.CollectionProperty(type=BagapiePreferences)
    # my_item = bpy.context.scene.bagapiePref.add()
    # my_item.security_features = 1
    # my_item.use_default_proxy = 1
    # my_item.maximum_polycount = 50000000


def unregister():
    for km,kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    for dupli,dupli_id in addon_keymaps_group:
        dupli.keymap_items.remove(dupli_id)
    for dupli_link,dupli_id_link in addon_keymaps_grouplink:
        dupli_link.keymap_items.remove(dupli_id_link)
    addon_keymaps.clear()

    for cls in classes:
        bpy.utils.unregister_class(cls)
        

if __name__ == "__main__":
    register()