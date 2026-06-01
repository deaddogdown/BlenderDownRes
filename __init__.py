bl_info = {
    "name": "Blender Down-Res",
    "author": "Dead Dog Down Game Studio",
    "version": (1, 0, 1),
    "blender": (4, 5, 0),
    "location": "View3D > N-Panel > Down-Res",
    "description": "Quick texture resolution reduction for all scene textures",
    "category": "Material",
}

if "bpy" in locals():
    import importlib
    if "BlenderDownRes" in locals():
        importlib.reload(BlenderDownRes)
else:
    from . import BlenderDownRes

import bpy

def register():
    BlenderDownRes.register()

def unregister():
    BlenderDownRes.unregister()

if __name__ == "__main__":
    register()
