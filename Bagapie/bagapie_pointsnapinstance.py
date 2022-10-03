import bpy
import bgl
import blf
import bmesh
import json
import addon_utils
import os
from bpy_extras import view3d_utils
from bpy.types import Operator
from . presets import bagapieModifiers

###################################################################################
# REMODE POINT SNAP INSTANCE
###################################################################################
class BAGAPIE_OT_pointsnapinstance_remove(Operator):
    """ Remove Bagapie Point Snap Instance """
    bl_idname = "bagapie.pointsnapinstance_remove"
    bl_label = 'Remove Bagapie Point Snap Instance'

    @classmethod
    def poll(cls, context):
        o = context.object

        return (
            o is not None and 
            o.type == 'MESH'
        )
    
    index: bpy.props.IntProperty(default=0)
    
    def execute(self, context):
        
        obj = context.object
        val = json.loads(obj.bagapieList[self.index]['val'])
        modifiers = val['modifiers']
        # obj.modifiers.remove(obj.modifiers[modifiers[0]])
        mo = obj.modifiers[modifiers[0]]
        coll_assets = mo["Input_4"]

        coll_instancer=bpy.data.collections['BagaPie_Point_Snap_Instancer']

        # si coll instancer est vide, la delete sinon simple removal

        # remove assets from asset collection and asset collection
        for ass in coll_assets.objects:
            coll_assets.objects.unlink(ass)
        bpy.data.collections.remove(coll_assets)
        
        if len(coll_instancer.objects) <= 1:
            bpy.ops.object.select_all(action='DESELECT')
            for ob in coll_instancer.objects:
                ob.select_set(True)
            bpy.ops.object.delete()
            bpy.data.collections.remove(coll_instancer)
            coll_main=bpy.data.collections['BagaPie_Point_Snap_Instance']
            bpy.data.collections.remove(coll_main)
        else:
            bpy.ops.object.select_all(action='DESELECT')
            obj.select_set(True)
            bpy.ops.object.delete()
            
        return {'FINISHED'}

###################################################################################
# RUN POINT SNAP INSTANCE
###################################################################################
class BAGAPIE_OT_pointsnapinstance(Operator):
    """Att treen at each clic on the selected mesh surface"""
    bl_idname = "bagapie.pointsnapinstance"
    bl_label = bagapieModifiers['pointsnapinstance']['label']
    bl_options = {'REGISTER', 'UNDO'}

    new_mesh = bpy.props.PointerProperty(type=object)
    target_clic = bpy.props.PointerProperty(type=object)
    
    @classmethod
    def poll(cls, context):
        o = context.object

        return (
            o is not None and 
            o.type == 'MESH'
        )

    # THANKS lemon on Stackexchange ! => how-to-move-object-while-tracking-to-mouse-cursor-with-a-modal-operator
    def modal(self, context, event):
        context.area.tag_redraw()

        try:
            mode = bpy.context.object.mode
        except:
            mode = "NONE"

        if event.type == 'LEFTMOUSE' and event.value == 'PRESS' and bpy.context.object.mode == 'OBJECT':
            self.object = bpy.context.object
            # plane = bpy.data.objects['Plane']
            plane = bpy.context.active_object
            plane = self.target_clic

            #Get the mouse position thanks to the event
            self.mouse_pos = event.mouse_region_x, event.mouse_region_y

            #Contextual active object, 2D and 3D regions
            region = bpy.context.region
            region3D = bpy.context.space_data.region_3d

            #The direction indicated by the mouse position from the current view
            self.view_vector = view3d_utils.region_2d_to_vector_3d(region, region3D, self.mouse_pos)
            #The view point of the user
            self.view_point = view3d_utils.region_2d_to_origin_3d(region, region3D, self.mouse_pos)
            #The 3D location in this direction
            self.world_loc = view3d_utils.region_2d_to_location_3d(region, region3D, self.mouse_pos, self.view_vector)

            self.loc_on_plane = None
            if plane:
                world_mat_inv = plane.matrix_world.inverted()
                # Calculates the ray direction in the target space
                rc_origin = world_mat_inv @ self.view_point
                rc_destination = world_mat_inv @ self.world_loc
                rc_direction = (rc_destination - rc_origin).normalized()
                hit, loc, norm, index = plane.ray_cast( origin = rc_origin, direction = rc_direction )
                self.loc_on_plane = loc
                if hit:
                    self.world_loc = plane.matrix_world @ loc

            if self.new_mesh:
                verts =[self.world_loc]
                faces = []
                edit_mesh(self.new_mesh.data, verts, faces, edges=None)

        elif event.type == 'LEFTMOUSE' and event.value == 'PRESS':
            # bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}
        
        elif event.value == 'RELEASE':
            try:
                self.target_clic.select_set(False)
            except:
                pass
            bpy.context.view_layer.objects.active = self.new_mesh
            self.new_mesh.select_set(True)

        elif event.type in {'ESC'} or mode != 'OBJECT':
            # bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            return {'CANCELLED'}

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        if context.area.type == 'VIEW_3D':
            assets = bpy.context.selected_objects
            target = bpy.context.active_object # AKA "Plane"

            # IF INSTANCE ALREADY EXIST
            if target.name.startswith("Point_Instancer"):
                # self.target_clic = target
                # assets.remove(target)
                # coll_assets = Collection_Setup(self,context,target)
                # for ob in assets:
                #     coll_assets.objects.link(ob)

                # CREATE MESH
                args = (self, context)
                # mesh = bpy.data.meshes.new("Point_Instancer")
                self.new_mesh = target

                # coll_instancer = Collection_Instancer(self,context,target)
                # coll_instancer.objects.link(self.new_mesh)

                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = self.new_mesh

                # ADD MODIFIER
                nodegroup = "BagaPie_PointSnapInstances" # GROUP NAME

                # new = self.new_mesh.modifiers.new
                # modifier = new(name=nodegroup, type='NODES')
                # Add_NodeGroup(self,context,modifier, nodegroup)
                # modifier.name = nodegroup
                for mod in target.modifiers:
                    if mod.name.startswith("BagaPie_PointSnapInstances"):
                        psi_modifier = mod

                target = psi_modifier["Input_3"]
                self.target_clic = target
                # psi_modifier["Input_4"] = coll_assets

                # # CUSTOM PROPERTY
                # val = {
                #     'name': 'pointsnapinstance', # MODIFIER TYPE
                #     'modifiers':[
                #         nodegroup, #Modifier Name
                #     ]
                # }

                # item = self.new_mesh.bagapieList.add()
                # item.val = json.dumps(val)

                #Keeps mouse position current 3D location and current object for the draw callback
                #(not needed to make it self attribute if you don't want to use the callback)
                self.mouse_pos = [0,0]
                self.loc = [0,0,0]
                self.object = None
                self.view_point = None
                self.view_vector = None
                self.world_loc = None
                self.loc_on_plane = None

                Warning(message = "PRESS ESCAPE TO FINISH !", title = "IMPORTANT", icon = 'INFO')
            
            # IF IT IS A NEW INSTANCE
            else:
                self.target_clic = target
                assets.remove(target)
                coll_assets = Collection_Setup(self,context,target)
                for ob in assets:
                    coll_assets.objects.link(ob)

                # CREATE MESH
                args = (self, context)
                mesh = bpy.data.meshes.new("Point_Instancer")
                self.new_mesh = bpy.data.objects.new(mesh.name, mesh)

                coll_instancer = Collection_Instancer(self,context,target)
                coll_instancer.objects.link(self.new_mesh)

                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = self.new_mesh

                # ADD MODIFIER
                nodegroup = "BagaPie_PointSnapInstances" # GROUP NAME

                new = self.new_mesh.modifiers.new
                modifier = new(name=nodegroup, type='NODES')
                Add_NodeGroup(self,context,modifier, nodegroup)
                modifier.name = nodegroup

                modifier["Input_3"] = target
                modifier["Input_4"] = coll_assets

                # CUSTOM PROPERTY
                val = {
                    'name': 'pointsnapinstance', # MODIFIER TYPE
                    'modifiers':[
                        nodegroup, #Modifier Name
                    ]
                }

                item = self.new_mesh.bagapieList.add()
                item.val = json.dumps(val)

                #Keeps mouse position current 3D location and current object for the draw callback
                #(not needed to make it self attribute if you don't want to use the callback)
                self.mouse_pos = [0,0]
                self.loc = [0,0,0]
                self.object = None
                self.view_point = None
                self.view_vector = None
                self.world_loc = None
                self.loc_on_plane = None

                Warning(message = "PRESS ESCAPE TO FINISH !", title = "IMPORTANT", icon = 'INFO')

                if len(assets) == 0:
                    Warning(message = "You must select a source object.", title = "Warning", icon = 'ERROR')
                    return {'CANCELLED'}

            args = (self, context)
            # self._handle = bpy.types.SpaceView3D.draw_handler_add(draw_tips, args, 'WINDOW', 'POST_PIXEL')
    
            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, "View3D not found, cannot run operator")
            return {'CANCELLED'}


# def draw_tips(self, context):
#     font_id = 0
#     blf.position(font_id, 20, 100, 0)
#     blf.size(font_id, 15, 100)
#     blf.draw(font_id, "BagaTips: Press Escape to stop.")


###################################################################################
# ADD ON VERTS TO THE CLICK POSITION
###################################################################################
def edit_mesh(obj, verts, faces, edges=None):
    if edges is None:
        edges = []

    # Get a BMesh representation
    bm = bmesh.new()   # create an empty BMesh
    bm.from_mesh(obj)   # fill it in from a Mesh

    bm.verts.new(verts[0])

    # Finish up, write the bmesh back to the mesh
    bm.to_mesh(obj)
    bm.free()

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
    # file_path = r"C:\Users\antoi\Desktop\BagaPie Archive\Dev\Bagapie\BagaPie_Nodes.blend"

    bpy.ops.wm.append(
        filepath=os.path.join(file_path, inner_path, nodes_name),
        directory=os.path.join(file_path, inner_path),
        filename=nodes_name
        )

    return {'FINISHED'}

###################################################################################
# GET OBJECTS SCALE
###################################################################################
def OBJ_Scale(self,context,obj,target):
    instances_max_dimensions = 0
    for ob in obj:  # Get instance max dimensions
        if ob.dimensions.x > instances_max_dimensions:
            instances_max_dimensions = ob.dimensions.x
            if ob.dimensions.x < ob.dimensions.y:
                instances_max_dimensions = ob.dimensions.y

    instances_visual_scale = 0
    for ob in obj:
        instances_visual_scale += ob.scale[0]
        instances_visual_scale += ob.scale[1]
        instances_visual_scale += ob.scale[2]

    target_scale = (target.scale[0] + target.scale[0] + target.scale[0])/3
    
    moy_scale = ((instances_visual_scale/target_scale)/(len(obj)*3))
    instances_max_dimensions = instances_max_dimensions*target_scale
    
    return moy_scale, instances_max_dimensions, target_scale
    return {'FINISHED'}

###################################################################################
# MANAGE COLLECTION
###################################################################################
def Collection_Setup(self,context,target):
    # Create collection and check if the main "Baga Collection" does not already exist
    if bpy.data.collections.get("BagaPie") is None:
        main_coll = bpy.data.collections.new("BagaPie")
        bpy.context.scene.collection.children.link(main_coll)
        scatter_master_coll = bpy.data.collections.new("BagaPie_Point_Snap_Instance")
        main_coll.children.link(scatter_master_coll)
        scatt_coll = bpy.data.collections.new("BagaPie_Point_Snap_Instance_" + target.name)
        scatter_master_coll.children.link(scatt_coll)
    # If the main collection Bagapie already exist
    elif bpy.data.collections.get("BagaPie_Point_Snap_Instance") is None:
        main_coll = bpy.data.collections["BagaPie"]
        scatter_master_coll = bpy.data.collections.new("BagaPie_Point_Snap_Instance")
        main_coll.children.link(scatter_master_coll)
        scatt_coll = bpy.data.collections.new("BagaPie_Point_Snap_Instance_" + target.name)
        scatter_master_coll.children.link(scatt_coll)
    # If the main collection Bagapie_Scatter already exist
    else:
        scatt_coll = bpy.data.collections.new("BagaPie_Point_Snap_Instance_" + target.name)
        scatter_master_coll = bpy.data.collections["BagaPie_Point_Snap_Instance"]
        scatter_master_coll.children.link(scatt_coll)

    return scatt_coll

###################################################################################
# MANAGE COLLECTION
###################################################################################
def Collection_Instancer(self,context,target):
    # Create collection and check if the main "Baga Collection" does not already exist
    if bpy.data.collections.get("BagaPie") is None:
        main_coll = bpy.data.collections.new("BagaPie")
        bpy.context.scene.collection.children.link(main_coll)
        scatter_master_coll = bpy.data.collections.new("BagaPie_Point_Snap_Instance")
        main_coll.children.link(scatter_master_coll)
        scatt_coll = bpy.data.collections.new("BagaPie_Point_Snap_Instancer")
        scatter_master_coll.children.link(scatt_coll)
    # If the main collection Bagapie already exist
    elif bpy.data.collections.get("BagaPie_Point_Snap_Instance") is None:
        main_coll = bpy.data.collections["BagaPie"]
        scatter_master_coll = bpy.data.collections.new("BagaPie_Point_Snap_Instance")
        main_coll.children.link(scatter_master_coll)
        scatt_coll = bpy.data.collections.new("BagaPie_Point_Snap_Instancer")
        scatter_master_coll.children.link(scatt_coll)
    # If the main collection Bagapie_Scatter already exist
    elif bpy.data.collections.get("BagaPie_Point_Snap_Instancer") is None:
        scatt_coll = bpy.data.collections.new("BagaPie_Point_Snap_Instancer")
        scatter_master_coll = bpy.data.collections["BagaPie_Point_Snap_Instance"]
        scatter_master_coll.children.link(scatt_coll)
    else:
        scatt_coll = bpy.data.collections.get("BagaPie_Point_Snap_Instancer") 

    return scatt_coll
  
###################################################################################
# DISPLAY WARNING MESSAGE
###################################################################################
def Warning(message = "", title = "Message Box", icon = 'INFO'):

    def draw(self, context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title = title, icon = icon)
