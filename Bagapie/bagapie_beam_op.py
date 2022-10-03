import bpy
import json
import os
import addon_utils
from bpy.types import Operator
from . presets import bagapieModifiers

class BAGAPIE_OT_beam_remove(Operator):
    """ Remove Bagapie Beam modifiers """
    bl_idname = "bagapie.beam_remove"
    bl_label = 'Remove Bagapie Beam'

    @classmethod
    def poll(cls, context):
        o = context.object

        return (
            o is not None and 
            o.type == 'MESH'
        )
    
    index: bpy.props.IntProperty(default=0)
    
    def execute(self, context):

        o = context.object
        o.select_set(True)
        bpy.ops.object.delete()

        return {'FINISHED'}


class BAGAPIE_OT_beam(Operator):
    """Create Beam H"""
    bl_idname = 'bagapie.beam'
    bl_label = bagapieModifiers['beam']['label']
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):

        beam = bpy.data.meshes.new('BagaPie_Beam')
        beam = bpy.data.objects.new(beam.name, beam)
        
        new = beam.modifiers.new
        nodegroup = "BagaPie_Beam" # GROUP NAME
        modifier = new(name=nodegroup, type='NODES')
        Add_NodeGroup(self,context,modifier, nodegroup)  

        coll = Collection_Add(self,context)
        coll.objects.link(beam)
        beam.location = bpy.context.scene.cursor.location
        bpy.ops.object.select_all(action='DESELECT')
        beam.select_set(True)
        bpy.context.view_layer.objects.active = beam

        val = {
            'name': 'beam', # MODIFIER TYPE
            'modifiers':[
                nodegroup, #Modifier Name
            ]
        }

        item = beam.bagapieList.add()
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
def Collection_Add(self,context):
    # Create collection and check if the main "Baga Collection" does not already exist
    if bpy.data.collections.get("BagaPie") is None:
        main_coll = bpy.data.collections.new("BagaPie")
        bpy.context.scene.collection.children.link(main_coll)
        array_coll = bpy.data.collections.new("BagaPie_Beam")
        main_coll.children.link(array_coll)
    # If the main collection Bagapie already exist
    elif bpy.data.collections.get("BagaPie_Beam") is None:
        main_coll = bpy.data.collections["BagaPie"]
        array_coll = bpy.data.collections.new("BagaPie_Beam")
        main_coll.children.link(array_coll)
    # If the main collection Bagapie_Scatter already exist
    else:
        array_coll = bpy.data.collections.get("BagaPie_Beam") 

    return array_coll

