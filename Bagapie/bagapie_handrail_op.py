import bpy
import json
import os
import addon_utils
from bpy.types import Operator
from . presets import bagapieModifiers
from random import random

class BAGAPIE_OT_handrail_remove(Operator):
    """ Remove Bagapie Handrail modifiers """
    bl_idname = "bagapie.handrail_remove"
    bl_label = 'Remove Bagapie Handrail'

    @classmethod
    def poll(cls, context):
        o = context.object

        return (
            o is not None and 
            o.type == 'CURVE'
        )
    
    index: bpy.props.IntProperty(default=0)
    
    def execute(self, context):
        
        obj = context.object
        val = json.loads(obj.bagapieList[self.index]['val'])
        modifiers = val['modifiers']
        # modifier = obj.modifiers[modifiers[0]]

        for mod in modifiers:
            obj.modifiers.remove(obj.modifiers[mod])
        
        context.object.bagapieList.remove(self.index)


        return {'FINISHED'}


class BAGAPIE_OT_handrail(Operator):
    """Add Handrail"""
    bl_idname = 'bagapie.handrail'
    bl_label = bagapieModifiers['handrail']['label']
    bl_options = {'REGISTER', 'UNDO'}

    # @classmethod
    # def poll(cls, context):
    #     o = context.object

    #     return (
    #         o is not None and 
    #         o.type == 'MESH'
    #     )

    def execute(self, context):

        # FIRST STEP

        curve_obj = bpy.context.active_object
        selected = bpy.context.selected_objects
            
        if curve_obj is not None and curve_obj.type == 'CURVE' and curve_obj in selected:
            new = bpy.data.objects[curve_obj.name].modifiers.new
        else:
            curve = bpy.data.curves.new('BagaPie_Handrail', 'CURVE')
            curve_obj = bpy.data.objects.new(curve.name, curve)
            curve_obj.data.dimensions = '2D'
            curve_obj.data.resolution_u = 64
            curve_obj.data.render_resolution_u = 64
            curve_obj.location = bpy.context.scene.cursor.location

            new = bpy.data.objects[curve.name].modifiers.new

        nodegroup = "BagaPie_Handrail" # GROUP NAME

        modifier = new(name=nodegroup, type='NODES')
        Add_NodeGroup(self,context,modifier, nodegroup)

        coll_target = Collection_Add(self,context,"BagaPie_Handrail")
        coll_target.objects.link(curve_obj)
        
        

        bpy.context.view_layer.objects.active = curve_obj
        bpy.ops.object.editmode_toggle()
        bpy.context.scene.tool_settings.curve_paint_settings.depth_mode = 'SURFACE'
        bpy.ops.wm.tool_set_by_id(name="builtin.draw")
        
        val = {
            'name': 'handrail', # MODIFIER TYPE
            'modifiers':[
                nodegroup, #Modifier Name
            ]
        }

        item = curve_obj.bagapieList.add()
        item.val = json.dumps(val)
        
        return {'FINISHED'}


###################################################################################
# ADD NODEGROUP TO THE MODIFIER
###################################################################################
def Add_NodeGroup(self,context,modifier, nodegroup_name):
    try:
        modifier.node_group = bpy.data.node_groups[nodegroup_name]
    except:
        Import_Nodes(self,context,nodegroup_name)
        modifier.node_group = bpy.data.node_groups[nodegroup_name]


###################################################################################
# IMPORT NODE GROUP
###################################################################################
def Import_Nodes(self,context,nodes_name):

    for mod in addon_utils.modules():
        if mod.bl_info['name'] == "BagaPie Modifier":
            filepath = mod.__file__
            file_path = filepath.replace("__init__.py","BagaPie_Nodes.blend")
        else:
            pass
    inner_path = "NodeTree"

    bpy.ops.wm.append(
        filepath=os.path.join(file_path, inner_path, nodes_name),
        directory=os.path.join(file_path, inner_path),
        filename=nodes_name
        )
    
    return {'FINISHED'}


###################################################################################
# MANAGE COLLECTION
###################################################################################
def Collection_Add(self,context,coll_name):
    # Create collection and check if the main "Baga Collection" does not already exist
    if bpy.data.collections.get("BagaPie") is None:
        main_coll = bpy.data.collections.new("BagaPie")
        bpy.context.scene.collection.children.link(main_coll)
        sub_coll = bpy.data.collections.new(coll_name)
        main_coll.children.link(sub_coll)
    # If the main collection Bagapie already exist
    elif bpy.data.collections.get(coll_name) is None:
        main_coll = bpy.data.collections["BagaPie"]
        sub_coll = bpy.data.collections.new(coll_name)
        main_coll.children.link(sub_coll)
    # If the main collection Bagapie_Scatter already exist
    else:
        sub_coll = bpy.data.collections.get(coll_name) 

    return sub_coll