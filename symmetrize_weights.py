import bpy
from mathutils.kdtree import KDTree
import site
import pip
pip.main(['install', 'numpy', '--target', site.USER_SITE])
import numpy as np

def find_opposite_vertex(kd_tree, vertex_coordinate, vertex_type):
    if vertex_type == "Tuple":
        opposite_x = -vertex_coordinate[0]  # negate X-coordinate to find opposite side
        opposite_y = vertex_coordinate[1]
        opposite_z = vertex_coordinate[2]

    elif vertex_type == "MeshVertex":
        opposite_x = -vertex_coordinate.co.x  # negate X-coordinate to find opposite side
        opposite_y = vertex_coordinate.co.y
        opposite_z = vertex_coordinate.co.z

    location = (opposite_x, opposite_y, opposite_z)
    co, index, dist = kd_tree.find(location)
    return index


def get_vg_verts(mesh_data, source_vertex_group):
    vg_vertices = []
    for v in mesh_data.vertices:
        if is_in_vertex_group(mesh_data, v, source_vertex_group):
            weight = source_vertex_group.weight(v.index)
            vg_vertices.append({"vertex":v, "weight": weight})

    return vg_vertices

def subdivide_vertex_group(vertex_coordinate_list, subdivision_level, mesh_vertex_len):
    if subdivision_level < 1:
        return vertex_coordinate_list

    subdivided = []

    for i in range(len(vertex_coordinate_list)):
        ## Current vertex
        #v1 = np.array(vertex_coordinate_list[i]["vertex"].co)
        ## Next vertex (wrap around to the first vertex)
        #v2 = np.array(vertex_coordinate_list[(i + 1) % len(vertex_coordinate_list)]["vertex"].co)

        vertex_one = vertex_coordinate_list[i]
        vertex_two = vertex_coordinate_list[(i + 1) % len(vertex_coordinate_list)]

        v1 = np.array(vertex_one["vertex"].co)
        v2 = np.array(vertex_two["vertex"].co)
       
        weight = (vertex_one["weight"] + vertex_two["weight"]) / 2

        # Add intermediate vertex_coordinate_list based on subdivision level
        for s in range(1, subdivision_level + 1):
            factor = s / (subdivision_level + 1)
            new_vertex = tuple(v1 + factor * (v2 - v1))
            mesh_vertex_len += 1
            subdivided.append({"index":mesh_vertex_len, "vertex_coordinates":new_vertex, "weight": weight})

    return subdivided, mesh_vertex_len

def create_kdtree(mesh):
    kd_tree = KDTree(len(mesh.vertices))
     # Insert all vertices into the KDTree
    for i, vert in enumerate(mesh.vertices):
        kd_tree.insert(vert.co, i)  
    kd_tree.balance()

    return kd_tree

# helper function to find out if a given vertex is in a given vertex group
#misconceptions because all vertices will always be in all of the vertex groups, just need to check for weights
#in short this is somewhat of a useless function
def is_in_vertex_group(mesh_data, v, source_vertex_group):
    for g in mesh_data.vertices[v.index].groups:
        if g.group == source_vertex_group.index:
            return True
    return False

def transfer_weights(source_vertex_group_name, target_vertex_group_name, mesh_name):

    # Switch to object mode NOTE: need to figure out why I need to do this
    bpy.ops.object.mode_set(mode='OBJECT')

    source_vertex_group = bpy.data.objects[mesh_name].vertex_groups.get(source_vertex_group_name)
    target_vertex_group = bpy.data.objects[mesh_name].vertex_groups.get(target_vertex_group_name)

    mesh_data = bpy.data.objects[mesh_name].data

    vg_vertices = get_vg_verts(mesh_data, source_vertex_group)
    #subdivided.append({"index":mesh_vertex_len, "vertex_coordinates":new_vertex})
    kd_tree = create_kdtree(mesh_data)

    #vg_vertices.append({"vertex":v, "weight": weight})
    for v in vg_vertices:
        vertex = v["vertex"]
        weight = v["weight"] 

        opposite_vertex_index = find_opposite_vertex(kd_tree, vertex, vertex_type="MeshVertex")
        opposite_vertex = mesh_data.vertices[opposite_vertex_index]
        if opposite_vertex:
            target_vertex_group.add([opposite_vertex.index], weight, 'REPLACE')

   # subdivided, mesh_vertex_len = subdivide_vertex_group(vg_vertices, 2, len(mesh_data.vertices))
   # #new vertices added!
   # for v in subdivided:
   #     #make sure all subdivided has weights
   #     #subdivided.append({"index":mesh_vertex_len, "vertex_coordinates":new_vertex, "weight": weight})
   #     weight = v["weight"]
   #     vertex_coordinate = v["vertex_coordinates"]
   #     opposite_vertex_index = find_opposite_vertex(kd_tree, vertex_coordinate, vertex_type="Tuple")
   #     opposite_vertex = mesh_data.vertices[opposite_vertex_index]
   #     if opposite_vertex:
   #         target_vertex_group.add([opposite_vertex.index], weight, 'REPLACE')


    print(f"Vertex group weights transferred from {source_vertex_group_name} to {target_vertex_group_name}")




mesh_name = "low_head"
transfer_weights("L_Ear", "R_Ear", mesh_name)

#if obj and obj.type == 'MESH':
#    vertex_groups = [vg.name for vg in obj.vertex_groups if vg.name.startswith("L_")]
#    for vg in vertex_groups:
#        source = vg
#        target = vg.replace("L_", "R_")
#        # Replace 'Armature', 'SourceBone', and 'TargetBone' with your actual armature name and bone names
#        transfer_weights(source, target, armature_name, mesh_name)
#else:
#    print("No active mesh object selected.")


