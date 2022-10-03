import bpy
import json
from bpy.types import Operator
import addon_utils

# These classes are used to call some existing operator from the addon panel.
# Some of them are probably stupid and some of them makes sense.

class SwitchMode(Operator):
    """Edit the painting of the last instantiated object"""
    bl_idname = "switch.mode"
    bl_label = "Switch Object Mode"
    def execute(self, context):

        obj = context.object
        val = json.loads(obj.bagapieList[obj.bagapieIndex]['val'])
        modifiers = val['modifiers']
        scatt_vertex_grp = modifiers[2]

        vertex_group = obj.vertex_groups
        vertex_group.active_index = vertex_group[scatt_vertex_grp].index

        bpy.ops.paint.weight_paint_toggle()
        return {'FINISHED'}

class EditMode(Operator):
    """Switch Object Mode"""
    bl_idname = "bool.mode"
    bl_label = "Switch Object Mode"
    def execute(self, context):

        try:
            obj = context.object
            val = json.loads(obj.bagapieList[obj.bagapieIndex]['val'])
            type = val['name']
            modifiers = val['modifiers']

            if type == 'boolean':
                bpy.ops.object.select_all(action='DESELECT')
                bool_obj = bpy.data.objects[modifiers[5]]
                bpy.context.view_layer.objects.active = bool_obj
                if bpy.context.object.mode == 'OBJECT':
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.wm.tool_set_by_id(name="builtin.primitive_cube_add")
                elif bpy.context.object.mode == 'EDIT':
                    bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
                    bpy.ops.object.editmode_toggle()

            else:
                if bpy.context.object.mode == 'OBJECT':
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.wm.tool_set_by_id(name="builtin.primitive_cube_add")
                elif bpy.context.object.mode == 'EDIT':
                    bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
                    bpy.ops.object.editmode_toggle()

        except:
            if bpy.context.object.mode == 'OBJECT':
                    bpy.ops.object.editmode_toggle()
                    bpy.ops.wm.tool_set_by_id(name="builtin.primitive_cube_add")
            elif bpy.context.object.mode == 'EDIT':
                bpy.ops.wm.tool_set_by_id(name="builtin.select_box")
                bpy.ops.object.editmode_toggle()

        return {'FINISHED'}

class UseSolidify(Operator):
    """Enable/Disable Solidify Modifier"""
    bl_idname = "solidify.visibility"
    bl_label = "Switch Object Mode"
    def execute(self, context):

        obj = context.object
        val = json.loads(obj.bagapieList[obj.bagapieIndex]['val'])
        type = val['name']
        modifiers = val['modifiers']        
        
        solidify_modifier = bpy.data.objects[modifiers[5]].modifiers[modifiers[4]]

        if solidify_modifier.show_viewport == False:
            solidify_modifier.show_viewport=True
            solidify_modifier.show_render=True
            solidify_modifier.show_in_editmode=True
        else:
            solidify_modifier.show_viewport=False
            solidify_modifier.show_render=False
            solidify_modifier.show_in_editmode=False

        return {'FINISHED'}

class InvertPaint(Operator):
    """Invert paint brush influence"""
    bl_idname = "invert.paint"
    bl_label = "Invert Weight Paint"
    def execute(self, context):
        weight_value = bpy.context.scene.tool_settings.unified_paint_settings.weight
        bpy.context.scene.tool_settings.unified_paint_settings.weight = weight_value*(-1)+1
        return {'FINISHED'}

class InvertWeight(Operator):
    """Invert paint"""
    bl_idname = "invert.weight"
    bl_label = "Invert Weight Value"
    def execute(self, context):
        bpy.ops.object.vertex_group_invert()
        return {'FINISHED'}

class CleanWPaint(Operator):
    """Lift all the painting"""
    bl_idname = "clean.paint"
    bl_label = "Clean Weight Paint"
    def execute(self, context):
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action='SELECT')
        bpy.ops.object.vertex_group_remove_from(use_all_groups=False)
        bpy.ops.paint.weight_paint_toggle()
        if bpy.context.scene.tool_settings.unified_paint_settings.weight < 1:
            bpy.ops.invert.paint()
        return {'FINISHED'}

class ADD_Assets(Operator):
    """Add asset to the current scatter layer"""
    bl_idname = "add.asset"
    bl_label = "Add Asset"
    def execute(self, context):
        
        target = bpy.context.active_object
        assets = bpy.context.selected_objects
        if len(assets) < 1:
            addon_name = 'DevjBagaPieAssets'
            success = addon_utils.check(addon_name)
            if success[0]:
                bpy.ops.bagapieassets.callpieforimport(import_mode = 'AddAssets')
                return {'FINISHED'}
            else:
                Warning(message = "Select your asset(s) then and the surface with the Scatter Layer to add the asset to.", title = "No asset selected.", icon = 'INFO')
                return {'FINISHED'}
        if target not in assets:
                Warning(message = "Select your surface with the Scatter Layer to add the asset to.", title = "No surface/scatter selected.", icon = 'INFO')
                return {'FINISHED'}
        assets.remove(target)

        nodegroup = target.modifiers.get("BagaPie_Scatter").node_group
        index = target.bagapieIndex
        val = json.loads(target.bagapieList[index]['val'])
        modifiers = val['modifiers']
        scatter_node = nodegroup.nodes.get(modifiers[1])

        if scatter_node.label != "BagaPie_Scatter":
            Warning("You must select a Scatter layer.", "WARNING", 'ERROR') 
            return {'FINISHED'}

        scatter_collection = scatter_node.inputs[1].default_value

        for asset in assets:
            if asset.name not in scatter_collection.objects:
                scatter_collection.objects.link(asset)
        
        return {'FINISHED'}

class REMOVE_Assets(Operator):
    """Remove asset to the current scatter layer"""
    bl_idname = "remove.asset"
    bl_label = "Remove Asset"
    def execute(self, context):
        
        target = bpy.context.active_object
        assets = bpy.context.selected_objects
        if len(assets) < 1:
            Warning(message = "Select your asset(s) then and the surface with the Scatter Layer to remove the asset to.", title = "No asset selected.", icon = 'INFO')
            return {'FINISHED'}
        assets.remove(target)

        nodegroup = target.modifiers.get("BagaPie_Scatter").node_group
        index = target.bagapieIndex
        val = json.loads(target.bagapieList[index]['val'])
        modifiers = val['modifiers']
        scatter_node = nodegroup.nodes.get(modifiers[1])

        if scatter_node.label != "BagaPie_Scatter":
            Warning("You must select a Scatter layer.", "WARNING", 'ERROR') 
            return {'FINISHED'}

        scatter_collection = scatter_node.inputs[1].default_value

        not_in_selected_layer = True
        for asset in assets:
            if asset.name in scatter_collection.objects:
                not_in_selected_layer = False
                scatter_collection.objects.unlink(asset)

        if not_in_selected_layer == True:
            Warning(message = "Asset(s) not in the selected Layer", title = "Wrong layer selected", icon = 'INFO')
            return {'FINISHED'}
        
        return {'FINISHED'}
        
class Rename_Layer(Operator):
    """Rename the current modifier layer"""
    bl_idname = "rename.layer"
    bl_label = "Rename Layer"
    bl_options = {'REGISTER', 'UNDO'}

    layer_name: bpy.props.StringProperty(default="None")

    def invoke(self, context, event):
        wm = context.window_manager
        bpy.context.scene['Layer_Name'] = "None"
        return wm.invoke_props_dialog(self)
    
    def draw(self, context):
        layout = self.layout
        # layout.prop(bpy.context.scene, '["Layer_Name"]', text="New name ")
        layout.prop(self, 'layer_name', text = "New name")

    def execute(self, context):
        
        target = bpy.context.active_object
        index = target.bagapieIndex
        val = json.loads(target.bagapieList[index]['val'])
        modifiers = val['modifiers']
        context.object.bagapieList.remove(index)
        val = {
            'name': 'scatter',
            'modifiers':[
                        modifiers[0],  # MODIFIER NAME
                        modifiers[1],
                        modifiers[2],
                        self.layer_name #bpy.context.scene['Layer_Name'],  # LAYER NAME
                        ]
        }

        # Rename Collection
        nodegroup = target.modifiers.get("BagaPie_Scatter").node_group
        modifiers = val['modifiers']
        scatter_node = nodegroup.nodes.get(modifiers[1])
        scatter_collection = scatter_node.inputs[1].default_value
        scatter_collection.name = self.layer_name

        item = target.bagapieList.add()
        item.val = json.dumps(val)
        # del bpy.context.scene['Layer_Name']
        target.bagapieIndex = len(target.bagapieList)-1
        
        return {'FINISHED'}

###################################################################################
# DISPLAY WARNING MESSAGE
###################################################################################
def Warning(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
