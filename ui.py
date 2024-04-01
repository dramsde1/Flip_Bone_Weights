import bpy


# Define the custom operator
class SymmetrizeWeightsOperator(bpy.types.Operator):
    bl_idname = "object.symmetrize_weights_operator"
    bl_label = "Custom Operator"

    def find_opposite_vertex(self, mesh_data, vertex):

        opposite_x = -vertex.co.x  # negate X-coordinate to find opposite side
        opposite_y = vertex.co.y
        opposite_z = vertex.co.z
        tolerance = 0.1
                        
        # Search for the opposite vertex
        for i, v in enumerate(mesh_data.vertices):
            if abs(v.co.x - opposite_x) < tolerance and abs(v.co.y - opposite_y) < tolerance and abs(v.co.z - opposite_z) < tolerance:  # tolerance for floating point comparison
                return v
                                        
        return None 

    def is_in_vertex_group(self, mesh_data, v, source_vertex_group):
        for g in mesh_data.vertices[v.index].groups:
            if g.group == source_vertex_group.index:
                return True
        return False

    def transfer_weights(self, source_bone_name, target_bone_name, armature_name, mesh_name):

        # Switch to object mode
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

    def execute(self, context):
        # Get the custom properties
        props = context.scene.dynamic_properties

        return {'FINISHED'}


# Define properties to store user input
class DynamicProperties(bpy.types.PropertyGroup):
    source_ref: bpy.props.PointerProperty(name="Source Reference", type=bpy.types.Object)
    target_ref: bpy.props.PointerProperty(name="Target Reference", type=bpy.types.Object)

# Define the operator to add a new property
class AddPropertyOperator(bpy.types.Operator):
    bl_idname = "object.add_property_operator"
    bl_label = "Add Property"

    def execute(self, context):
        # Get the custom properties
        props = context.scene.dynamic_properties

        # Add a new property
        new_property = props.add()
        new_property.name = "Bone"
        new_property.value = 0.0

        return {'FINISHED'}

# Define the panel class
class SymmetrizeWeightsPanel(bpy.types.Panel):
    bl_label = "Symmetrize Weights"
    bl_idname = "PT_Symmetrize"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Symmetrize Weights'

    def draw(self, context):
        layout = self.layout # Access the custom properties

        props = context.scene.dynamic_properties

        # Add a dropdown to select an object
        #layout.prop(props, "object_ref")
        
        # Display existing properties
        for prop in props:
            row = layout.row()
            row.prop(prop, "source_ref")
            row.prop(prop, "target_ref")

        # Add the button that triggers the operator

        #first button to trigger symmetrization
        layout.operator("object.symmetrize_weights_operator", text="Symmetrize")

        #second button to add more source, target bone rows
        layout.operator("object.add_property_operator", text="Add Source + Target")

# Register the operator and panel classes
def register():
    bpy.utils.register_class(SymmetrizeWeightsOperator)
    bpy.utils.register_class(SymmetrizeWeightsPanel)
    bpy.utils.register_class(DynamicProperties)
    bpy.types.Scene.dynamic_properties = bpy.props.CollectionProperty(type=DynamicProperties)
    bpy.utils.register_class(AddPropertyOperator)

# Unregister the operator and panel classes
def unregister():
    bpy.utils.unregister_class(SymmetrizeWeightsOperator)
    bpy.utils.unregister_class(SymmetrizeWeightsPanel)
    bpy.utils.unregister_class(DynamicProperties)
    del bpy.types.Scene.dynamic_properties
    bpy.utils.unregister_class(AddPropertyOperator)

# Test the panel
if __name__ == "__main__":
    register()
