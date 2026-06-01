import bpy


class DOWNRES_PT_MainPanel(bpy.types.Panel):
    """Main panel for texture down-res"""
    bl_label = "Texture Down-Res"
    bl_idname = "DOWNRES_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Down-Res'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        props = scene.downres_props
        
        # Resolution selection
        box = layout.box()
        box.label(text="Target Resolution:", icon='IMAGE_DATA')
        
        col = box.column(align=True)
        
        # Resolution buttons with highlighting
        resolutions = [
            ('2048', '2K', 2048),
            ('1024', '1K', 1024),
            ('512', '512', 512),
            ('256', '256', 256),
        ]
        
        for res_id, label, value in resolutions:
            row = col.row(align=True)
            row.scale_y = 1.2
            
            op = row.operator("downres.set_resolution", text=label, depress=(props.target_resolution == res_id))
            op.resolution = res_id
        
        # Down Res button
        row = layout.row()
        row.scale_y = 1.5
        row.operator("downres.process_textures", text="Down-Res", icon='RENDER_RESULT')
        
        # Save button
        row = layout.row()
        row.scale_y = 1.2
        row.operator("downres.save_textures", text="Save DownRes to Blend", icon='FILE_TICK')
        
        # Info display
        layout.separator()
        box = layout.box()
        
        valid_images = [img for img in bpy.data.images if img.type == 'IMAGE' and img.size[0] > 0]
        texture_count = len(valid_images)
        
        if valid_images:
            max_res = max(max(img.size[0], img.size[1]) for img in valid_images)
            box.label(text=f"Textures in scene: {texture_count}", icon='INFO')
            box.label(text=f"Largest: {max_res}px")
        else:
            box.label(text=f"Textures in scene: {texture_count}", icon='INFO')


class DOWNRES_OT_SetResolution(bpy.types.Operator):
    """Set target resolution"""
    bl_idname = "downres.set_resolution"
    bl_label = "Set Resolution"
    bl_options = {'REGISTER', 'UNDO'}
    
    resolution: bpy.props.StringProperty()
    
    def execute(self, context):
        context.scene.downres_props.target_resolution = self.resolution
        return {'FINISHED'}


class DOWNRES_OT_ProcessTextures(bpy.types.Operator):
    """Preview down-res all textures"""
    bl_idname = "downres.process_textures"
    bl_label = "Preview Down-Res"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        props = context.scene.downres_props
        target_res = int(props.target_resolution)
        
        images_to_process = [img for img in bpy.data.images 
                            if img.type == 'IMAGE' 
                            and img.size[0] > 0 
                            and img.size[1] > 0]
        
        if not images_to_process:
            self.report({'WARNING'}, "No valid textures found in scene")
            return {'CANCELLED'}
        
        processed = 0
        skipped = 0
        
        for img in images_to_process:
            current_width = img.size[0]
            current_height = img.size[1]
            
            if current_width <= target_res and current_height <= target_res:
                skipped += 1
                continue
            
            if current_width > current_height:
                new_width = target_res
                new_height = int((target_res / current_width) * current_height)
            else:
                new_height = target_res
                new_width = int((target_res / current_height) * current_width)
            
            new_width = max(1, new_width)
            new_height = max(1, new_height)
            
            try:
                img.scale(new_width, new_height)
                processed += 1
                print(f"Preview: {img.name} from {current_width}x{current_height} to {new_width}x{new_height}")
            except Exception as e:
                print(f"Failed to process {img.name}: {e}")
                continue
        
        if processed > 0:
            self.report({'INFO'}, f"Preview complete: {processed} textures scaled, {skipped} skipped. Click 'Save DownRes to Blend' to make permanent.")
        else:
            self.report({'INFO'}, f"All {skipped} textures already at or below target resolution")
        
        return {'FINISHED'}


class DOWNRES_OT_SaveTextures(bpy.types.Operator):
    """Save down-res textures permanently to blend file"""
    bl_idname = "downres.save_textures"
    bl_label = "Save DownRes to Blend"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        images_to_save = [img for img in bpy.data.images 
                         if img.type == 'IMAGE' 
                         and img.size[0] > 0 
                         and img.size[1] > 0]
        
        if not images_to_save:
            self.report({'WARNING'}, "No valid textures found in scene")
            return {'CANCELLED'}
        
        saved = 0
        
        for img in images_to_save:
            try:
                if img.filepath == "" or img.packed_file is not None:
                    img.pack()
                else:
                    try:
                        img.save()
                    except:
                        img.pack()
                saved += 1
            except Exception as e:
                print(f"Failed to save {img.name}: {e}")
                continue
        
        self.report({'INFO'}, f"Saved {saved} textures to blend file permanently")
        return {'FINISHED'}


class DownResProperties(bpy.types.PropertyGroup):
    target_resolution: bpy.props.StringProperty(
        name="Target Resolution",
        description="Target resolution for texture down-res",
        default="512"
    )


classes = (
    DownResProperties,
    DOWNRES_PT_MainPanel,
    DOWNRES_OT_SetResolution,
    DOWNRES_OT_ProcessTextures,
    DOWNRES_OT_SaveTextures,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.downres_props = bpy.props.PointerProperty(type=DownResProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.downres_props