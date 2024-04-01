import bpy

# a helper function, given a vertex and a mesh's vertices, it will find the symmetrical vertex across the x axis
def find_opposite_vertex(mesh_data, vertex):

    opposite_x = -vertex.co.x  # negate X-coordinate to find opposite side
    opposite_y = vertex.co.y
    opposite_z = vertex.co.z
    tolerance = 0.1
                    
    # Search for the opposite vertex
    for i, v in enumerate(mesh_data.vertices):
        if abs(v.co.x - opposite_x) < tolerance and abs(v.co.y - opposite_y) < tolerance and abs(v.co.z - opposite_z) < tolerance:  # tolerance for floating point comparison
            return v
                                    
    return None 

# helper function to find out if a given vertex is in a given vertex group
def is_in_vertex_group(mesh_data, v, source_vertex_group):
    for g in mesh_data.vertices[v.index].groups:
        if g.group == source_vertex_group.index:
            return True
    return False

def transfer_weights(source_bone_name, target_bone_name, armature_name, mesh_name):

    # Switch to object mode NOTE: need to figure out why I need to do this
    bpy.ops.object.mode_set(mode='OBJECT')

    # Get the source and target armatures
    source_bone = bpy.data.objects[armature_name].pose.bones.get(source_bone_name)
    target_bone = bpy.data.objects[armature_name].pose.bones.get(target_bone_name)
    

    # Ensure both bones exist
    if source_bone and target_bone:
        
        # make sure vertex group name is in mesh list of vertex groups
        if source_bone_name in bpy.data.objects[mesh_name].vertex_groups:
            source_vertex_group = bpy.data.objects[mesh_name].vertex_groups.get(source_bone_name)

            #first check if target_vertex_group already exists
            target_vertex_group = bpy.data.objects[mesh_name].vertex_groups.get(target_bone_name)

            if not target_vertex_group:
                target_vertex_group = bpy.data.objects[mesh_name].vertex_groups.new(name=target_bone_name)

            mesh_data = bpy.data.objects[mesh_name].data

            # Loop through all vertices
            for v in mesh_data.vertices:
                # Get the weight of the vertex in the source group
                try:
                    #check if the vertex is in the source vertex group
                    # a single vertex can belong to multiple vertex groups
                    if is_in_vertex_group(mesh_data, v, source_vertex_group):
                        # Assign the weight to the target group
                        weight = source_vertex_group.weight(v.index)
                        # need to assign the weight to the opposite side of the mesh with x axis symmetry
                        opposite_vertex = find_opposite_vertex(mesh_data, v)
                        if opposite_vertex:
                            target_vertex_group.add([opposite_vertex.index], weight, 'REPLACE')
                except RuntimeError as e:
                    print(e)

            print(f"Vertex group weights transferred from {source_bone_name} to {target_bone_name}")
        else:
            print(f"Vertex group '{source_bone_name}' not found.")
    else:
        print("Source or target bone not found.")

# Replace 'Armature', 'SourceBone', and 'TargetBone' with your actual armature name and bone names
transfer_weights('R_Thumb2', 'L_Thumb2', 'Root.001', "LOD_1_Group_0_Sub_6__esf007_Body.033")
