import bpy
from mathutils.kdtree import KDTree

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

def get_neighbors_in_radius(kd_tree, radius, vertex_index, target_coordinate, target_vertex_group, mesh_data):
    neighbors = [item[1] for item in kd_tree.find_range(target_coordinate, radius) if item[1] != vertex_index]
    zero_neighbors = []
    avg_weight = 0
    counter = 0
    for idx in neighbors:
        v = mesh_data.vertices[idx] 
        if is_in_vertex_group(mesh_data, v, target_vertex_group):
            weight = target_vertex_group.weight(idx)
        else:
            weight = 0.0
            target_vertex_group.add([idx], weight, 'REPLACE')
        
        if weight == 0.0:
            zero_neighbors.append(idx)
        else:
            avg_weight += target_vertex_group.weight(idx)
            counter += 1
    
    avg_weight += target_vertex_group.weight(vertex_index)
    counter += 1
    avg_weight = avg_weight / counter

    return zero_neighbors, avg_weight


def smoothen_vertex_group(neighbors, avg_weight, target_vertex_group, vertex_index):
    for idx in neighbors:
        target_vertex_group.add([idx], avg_weight, 'REPLACE')


def get_vg_verts(mesh_data, source_vertex_group):
    vg_vertices = []
    for v in mesh_data.vertices:
        if is_in_vertex_group(mesh_data, v, source_vertex_group):
            weight = source_vertex_group.weight(v.index)
            vg_vertices.append({"vertex":v, "weight": weight})

    return vg_vertices

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

def transfer_weights(source_vertex_group_name, target_vertex_group_name, mesh_name, kd_tree):

    # Switch to object mode NOTE: need to figure out why I need to do this
    bpy.ops.object.mode_set(mode='OBJECT')

    source_vertex_group = bpy.data.objects[mesh_name].vertex_groups.get(source_vertex_group_name)
    target_vertex_group = bpy.data.objects[mesh_name].vertex_groups.get(target_vertex_group_name)

    mesh_data = bpy.data.objects[mesh_name].data

    vg_vertices = get_vg_verts(mesh_data, source_vertex_group)
    #subdivided.append({"index":mesh_vertex_len, "vertex_coordinates":new_vertex})
    #target_vertices = []
    #vg_vertices.append({"vertex":v, "weight": weight})
    for v in vg_vertices:
        vertex = v["vertex"]
        weight = v["weight"] 

        opposite_vertex_index = find_opposite_vertex(kd_tree, vertex, vertex_type="MeshVertex")
        opposite_vertex = mesh_data.vertices[opposite_vertex_index]
        if opposite_vertex:
            target_vertex_group.add([opposite_vertex.index], weight, 'REPLACE')
            #target_vertices.append(opposite_vertex)

            #smoothen target vertex group
            neighbors, avg_weight = get_neighbors_in_radius(kd_tree=kd_tree, radius=0.5, vertex_index=opposite_vertex_index, target_coordinate=opposite_vertex.co, target_vertex_group=target_vertex_group, mesh_data=mesh_data)
            
            smoothen_vertex_group(neighbors=neighbors, avg_weight=avg_weight, target_vertex_group=target_vertex_group, vertex_index=opposite_vertex_index)

    print(f"Vertex group weights transferred from {source_vertex_group_name} to {target_vertex_group_name}")




mesh_name = "low_head"
mesh_data = bpy.data.objects[mesh_name].data
kd_tree = create_kdtree(mesh_data)
transfer_weights("L_Ear", "R_Ear", mesh_name, kd_tree)

#if obj and obj.type == 'MESH':
#    vertex_groups = [vg.name for vg in obj.vertex_groups if vg.name.startswith("L_")]
#    for vg in vertex_groups:
#        source = vg
#        target = vg.replace("L_", "R_")
#        # Replace 'Armature', 'SourceBone', and 'TargetBone' with your actual armature name and bone names
#        transfer_weights(source, target, armature_name, mesh_name)
#else:
#    print("No active mesh object selected.")


