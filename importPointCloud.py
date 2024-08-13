import os, bpy, bmesh, math, time
from os.path import dirname
from . import installModule

ADDON_DIR = dirname(dirname(dirname(os.path.realpath(__file__)))) + "\\addons\\BlenderPCModelImporter"
print(ADDON_DIR)
ADDON_NAME = os.path.basename(ADDON_DIR)
FILEPATH = ""


class UserException(Exception):

    message: str

    def __init__(self, message: str, *args: object):
        self.message = message
        super().__init__(message, *args)

def get_path():
    return ADDON_DIR


try:
    import pythonnet
except ModuleNotFoundError as exc:
    installModule.installModule("pythonnet")
    try:
        import pythonnet
    except ModuleNotFoundError as exc:
        raise UserException(("Could not download python.net, please try running blender with"
            " admin rights")) from exc

path = os.path.join(get_path(), "libs")
dll_names = [
    "PointCloudBlender.dll",
    "HedgeLib.dll"
]

pythonnet.load("coreclr")

import clr
for dll_name in dll_names:
    dll_path = os.path.join(path, dll_name)
    clr.AddReference(dll_path)

from PointCloudBlender import PointCloudReader
from PointCloudBlender import ModelReader

def importModel(i, importer, parent):
    if os.path.exists(dirname(importer.filepath) + "\\" + i.ModelName + ".terrain-model"):
        model = ModelReader.Model(dirname(importer.filepath) + "\\" + i.ModelName + ".terrain-model", bpy.context.scene.HedgeNeedle)
        for Mesh in model.meshes:
            mesh1 = bpy.data.meshes.new(i.ModelName + " Mesh")
            mesh1.use_auto_smooth = True
            ob = bpy.data.objects.new(i.InstanceName, mesh1)
            ob.location = (i.Position.X, i.Position.Y, i.Position.Z)
            ob.rotation_euler = (i.Rotation.X, i.Rotation.Y, i.Rotation.Z)
            ob.parent = parent
            bpy.context.collection.objects.link(ob)
            bpy.context.view_layer.objects.active = ob
            ob.select_set(True)
            mesh = bpy.context.object.data
            bm = bmesh.new()
            for v in Mesh.verts:
                bm.verts.new((v.X, v.Y, v.Z))
            list = [v for v in bm.verts]
            for f in Mesh.faces:
                try:
                    bm.faces.new((list[f.x], list[f.y], list[f.z]))
                except:
                    continue
            bm.to_mesh(mesh)

            # Normals = []
            # for f in bm.faces:
            #     f.smooth=True
            #     f.normal_flip()
            #     for l in f.loops:
            #         if Mesh.normals != []:
            #             Normals.append((Mesh.normals[l.vert.index].X, Mesh.normals[l.vert.index].Y, Mesh.normals[l.vert.index].Z))
            # bm.to_mesh(mesh)

            if importer.ImportUvs:
                if Mesh.uvs != []:
                    uv_layer = bm.loops.layers.uv.verify()
                if Mesh.uvs1 != []:
                    uv2_layer = bm.loops.layers.uv.new('UVMap2')
                if Mesh.uvs2 != []:
                    uv3_layer = bm.loops.layers.uv.new('UVMap3')
                if Mesh.uvs3 != []:
                    uv4_layer = bm.loops.layers.uv.new('UVMap4')

                for f in bm.faces:
                    for l in f.loops:
                        if Mesh.uvs != []:
                            l[uv_layer].uv[0]  = Mesh.uvs[l.vert.index].X
                            l[uv_layer].uv[1]  = Mesh.uvs[l.vert.index].Y
                        if Mesh.uvs1 != []:
                            l[uv2_layer].uv[0] = Mesh.uvs1[l.vert.index].X
                            l[uv2_layer].uv[1] = Mesh.uvs1[l.vert.index].Y
                        if Mesh.uvs2 != []:
                            l[uv3_layer].uv[0] = Mesh.uvs2[l.vert.index].X
                            l[uv3_layer].uv[1] = Mesh.uvs2[l.vert.index].Y
                        if Mesh.uvs3 != []:
                            l[uv4_layer].uv[0] = Mesh.uvs3[l.vert.index].X
                            l[uv4_layer].uv[1] = Mesh.uvs3[l.vert.index].Y
                bm.to_mesh(mesh)
            bm.free()


            MeshMat = bpy.data.materials.get(Mesh.matName)
            if not MeshMat:
                MeshMat = bpy.data.materials.new(Mesh.matName)

            if len(ob.data.materials)>0:
                ob.data.materials[0]=MeshMat
            else:
                ob.data.materials.append(MeshMat)

            # if Mesh.normals != []:
            #     mesh1.normals_split_custom_set(Normals)
            
def importPointCloud(importer, filepath):
    pc = PointCloudReader.LoadPointCloud(filepath)
    o = bpy.data.objects.new(os.path.basename(filepath), None)
    bpy.context.collection.objects.link(o)
    for i in pc:
        if "shd" in i.InstanceName and importer.ImportShadowModels:
            pass
        elif "shdw" in i.InstanceName and importer.ImportShadowModels:
            pass
        else:
            importModel(i, importer, o)
    
    o.rotation_euler = (math.radians(90), 0, 0)