import bpy
import json
import math
import os
from pathlib import Path
from mathutils import Quaternion, Vector

PROJECT = Path(__file__).resolve().parents[2]
WORK = Path(os.environ.get('PORTRAIT_VEIL_WORKDIR', '/tmp/portrait-veil'))
OUT = PROJECT / 'public/models/portrait-veil.glb'
WORK.mkdir(parents=True, exist_ok=True)
OUT.parent.mkdir(parents=True, exist_ok=True)

FPS = 24
DURATION = 12
END = FPS * DURATION
LAMELLA_COUNT = 13
LENGTH_SEGMENTS = 32
WIDTH_SEGMENTS = 16
MASTER_CLIP = 'VEIL_MASTER_CYCLE'

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
for datablocks in (bpy.data.meshes, bpy.data.curves, bpy.data.materials, bpy.data.cameras, bpy.data.lights, bpy.data.actions):
    for datablock in list(datablocks):
        datablocks.remove(datablock)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.fps = FPS
scene.frame_start = 0
scene.frame_end = END
scene.render.resolution_x = 960
scene.render.resolution_y = 960
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.render.image_settings.color_mode = 'RGBA'
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'BEZIER'

world = bpy.data.worlds.new('VEIL_WORLD')
world.use_nodes = True
world.node_tree.nodes['Background'].inputs['Color'].default_value = (0.006, 0.006, 0.007, 1)
world.node_tree.nodes['Background'].inputs['Strength'].default_value = 0.12
scene.world = world

material = bpy.data.materials.new('VEIL_ROUGH_ACHROMATIC')
material.use_nodes = True
bsdf = material.node_tree.nodes['Principled BSDF']
bsdf.inputs['Base Color'].default_value = (0.62, 0.64, 0.65, 1)
bsdf.inputs['Roughness'].default_value = 0.78
bsdf.inputs['Metallic'].default_value = 0.0
material.use_backface_culling = False
material.blend_method = 'OPAQUE'

root = bpy.data.objects.new('PORTRAIT_VEIL_ROOT', None)
bpy.context.collection.objects.link(root)
root['veil_clip'] = MASTER_CLIP
root['veil_duration'] = END / FPS
root['lamella_count'] = LAMELLA_COUNT
root['topology'] = f'{LENGTH_SEGMENTS + 1}x{WIDTH_SEGMENTS + 1}_open_sheet'

def get_base_module_shape(u, v):
    end_profile = 0.72 + 0.28 * math.sin(u * math.pi) ** 0.38
    side_notch = 1.0 - 0.14 * math.exp(-((u - 0.20) / 0.075) ** 2)
    side_notch += 0.08 * math.exp(-((u - 0.72) / 0.11) ** 2)
    width = 0.52 * end_profile * side_notch

    x = (u - 0.5) * 2.65 + 0.10 * v * math.sin(u * math.pi)
    y = (
        v * width * (1.0 + 0.12 * v * math.sin(u * math.pi * 2.0 + 0.4))
        + 0.055 * math.sin(u * math.pi * 2.0)
        + 0.035 * (u - 0.5)
    )
    crease_a = math.tanh((v - 0.18 * math.sin(u * math.pi * 2.0) + 0.10) * 9.0)
    crease_b = math.tanh((v + 0.26 - 0.10 * math.cos(u * math.pi * 2.0)) * 10.0)
    crease_c = math.tanh((v - 0.56 + 0.08 * math.sin(u * math.pi * 3.0)) * 8.0)
    pleat = 0.012 * math.sin(u * math.pi * 10.0 + v * 1.7) * math.cos(v * math.pi * 4.0)
    edge_curl = 0.032 * abs(v) ** 3 * math.sin(u * math.pi * 2.5 + 0.4)
    z = 0.058 * crease_a - 0.044 * crease_b + 0.026 * crease_c + pleat + edge_curl
    return Vector((x, y, z))

def create_lamella(layer):
    vertices = []
    faces = []
    for i in range(LENGTH_SEGMENTS + 1):
        u = i / LENGTH_SEGMENTS
        for j in range(WIDTH_SEGMENTS + 1):
            v = j / WIDTH_SEGMENTS * 2 - 1
            vertices.append(get_base_module_shape(u, v))

    row = WIDTH_SEGMENTS + 1
    for i in range(LENGTH_SEGMENTS):
        for j in range(WIDTH_SEGMENTS):
            a = i * row + j
            faces.append((a, a + row, a + row + 1, a + 1))

    mesh = bpy.data.meshes.new(f'VEIL_LAMELLA_{layer:02d}_MESH')
    mesh.from_pydata(vertices, [], faces)
    mesh.materials.append(material)
    uv = mesh.uv_layers.new(name='UVMap')
    for loop in mesh.loops:
        vertex_index = loop.vertex_index
        i, j = divmod(vertex_index, row)
        uv.data[loop.index].uv = (i / LENGTH_SEGMENTS, j / WIDTH_SEGMENTS)
    for polygon in mesh.polygons:
        polygon.use_smooth = False

    obj = bpy.data.objects.new(f'VEIL_LAMELLA_{layer:02d}', mesh)
    bpy.context.collection.objects.link(obj)
    obj.parent = root
    obj['lamella_index'] = layer

    t = layer / max(1, (LAMELLA_COUNT - 1))

    theta = math.radians(-145.0 + 265.0 * t)
    spine_x = 0.68 * math.cos(theta) + 0.14 * math.sin(theta * 2.0)
    spine_y = 0.52 * math.sin(theta) + 0.09 * math.sin(theta * 3.0)
    spine_z = 0.16 * math.sin(theta * 2.0) - 0.06 * math.cos(theta)

    offset_x = 0.035 * math.sin(layer * 1.7)
    offset_y = 0.035 * math.cos(layer * 1.3)
    offset_z = 0.035 * math.sin(layer * 1.9)
    obj.location = Vector((spine_x + offset_x, spine_y + offset_y, spine_z + offset_z))

    rot_x = 0.14 * math.sin(theta) + 0.04 * math.cos(layer * 1.2)
    rot_y = 0.12 * math.cos(theta * 1.5) + 0.035 * math.sin(layer * 0.9)
    rot_z = theta + math.pi / 2.0 + 0.08 * math.sin(theta * 2.0)
    obj.rotation_euler = (rot_x, rot_y, rot_z)

    base_scale = 0.72 + 0.17 * math.sin(t * math.pi) + 0.035 * math.sin(layer * 1.91)
    scale_x = base_scale * (1.0 + 0.035 * math.sin(layer * 1.5))
    scale_y = base_scale * (1.0 + 0.045 * math.cos(layer * 1.2))
    scale_z = base_scale * (0.92 + 0.04 * math.cos(layer))
    obj.scale = (scale_x, scale_y, scale_z)

    obj.shape_key_add(name='Basis')
    fold_a = obj.shape_key_add(name='Fold_A')
    fold_b = obj.shape_key_add(name='Fold_B')

    for i in range(LENGTH_SEGMENTS + 1):
        u = i / LENGTH_SEGMENTS
        for j in range(WIDTH_SEGMENTS + 1):
            v = j / WIDTH_SEGMENTS * 2 - 1
            index = i * row + j

            base_v = get_base_module_shape(u, v)
            breathe_a = Vector((base_v.x, base_v.y * 1.10, base_v.z + 0.070 * math.sin(u * math.pi + v)))
            fold_a.data[index].co = breathe_a
            breathe_b = Vector((base_v.x, base_v.y * 0.90, base_v.z - 0.070 * math.sin(u * math.pi - v)))
            fold_b.data[index].co = breathe_b

    samples = [int(END * i / 6.0) for i in range(7)]

    for frame in samples:
        cycle = frame / END * math.tau
        phase = layer * 0.24

        val_a = max(0.0, math.sin(cycle + phase)) * 0.92
        val_b = max(0.0, -math.sin(cycle + phase)) * 0.92

        fold_a.value = val_a
        fold_b.value = val_b
        fold_a.keyframe_insert('value', frame=frame, group=MASTER_CLIP)
        fold_b.keyframe_insert('value', frame=frame, group=MASTER_CLIP)

    action = obj.data.shape_keys.animation_data.action

    track = obj.data.shape_keys.animation_data.nla_tracks.new()
    track.name = MASTER_CLIP
    track.strips.new(MASTER_CLIP, 0, action)
    obj.data.shape_keys.animation_data.action = None

    return obj

lamellae = [create_lamella(layer) for layer in range(LAMELLA_COUNT)]

def add_light(name, light_type, energy, location, size=4.0):
    data = bpy.data.lights.new(name, light_type)
    data.energy = energy
    data.color = (0.92, 0.95, 0.96)
    if light_type == 'AREA':
        data.shape = 'DISK'
        data.size = size
    obj = bpy.data.objects.new(name, data)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    return obj

add_light('VEIL_KEY', 'AREA', 920, (4.5, 5.5, 6.5), 5.0)
add_light('VEIL_RIM', 'AREA', 760, (-5.0, -1.5, 3.0), 4.0)

camera_data = bpy.data.cameras.new('DIAGNOSTIC_CAMERA')
camera = bpy.data.objects.new('DIAGNOSTIC_CAMERA', camera_data)
bpy.context.collection.objects.link(camera)
camera_data.lens = 56
scene.camera = camera

def point_camera(location, target=(0, 0, -0.35)):
    camera.location = location
    camera.rotation_euler = (Vector(target) - camera.location).to_track_quat('-Z', 'Y').to_euler()

scene.frame_set(72)
point_camera((0, 0, 9.4))
scene.render.filepath = str(WORK / 'diagnostic-front.png')
bpy.ops.render.render(write_still=True)

point_camera((5.8, 3.6, 7.2))
scene.render.filepath = str(WORK / 'diagnostic-oblique.png')
bpy.ops.render.render(write_still=True)

isolation_materials = []
for index, obj in enumerate(lamellae):
    value = 0.16 + 0.72 * index / (LAMELLA_COUNT - 1)
    isolated = bpy.data.materials.new(f'ISOLATION_{index:02d}')
    isolated.diffuse_color = (value, 0.08, 1.0 - value, 1)
    isolated.use_nodes = True
    isolated_bsdf = isolated.node_tree.nodes['Principled BSDF']
    isolated_bsdf.inputs['Base Color'].default_value = (value, 0.08, 1.0 - value, 1)
    isolated_bsdf.inputs['Roughness'].default_value = 0.9
    obj.data.materials[0] = isolated
    isolation_materials.append(isolated)
point_camera((0, 0, 9.4))
scene.render.filepath = str(WORK / 'diagnostic-layer-isolation.png')
bpy.ops.render.render(write_still=True)
for obj in lamellae:
    obj.data.materials[0] = material

bpy.ops.object.select_all(action='DESELECT')
for obj in [root, *lamellae]:
    obj.select_set(True)
scene.frame_set(0)

bpy.ops.export_scene.gltf(
    filepath=str(OUT),
    export_format='GLB',
    use_selection=True,
    export_animations=True,
    export_animation_mode='NLA_TRACKS',
    export_merge_animation='NLA_TRACK',
    export_frame_range=True,
    export_force_sampling=False,
    export_materials='EXPORT',
    export_extras=True,
    export_yup=True,
)

bpy.ops.wm.save_as_mainfile(filepath=str(WORK / 'portrait-veil-source.blend'))

total_verts = sum(len(obj.data.vertices) for obj in lamellae)
total_faces = sum(len(obj.data.polygons) for obj in lamellae)

report = {
    'asset': str(OUT),
    'lamellae': LAMELLA_COUNT,
    'shared_topology': {
        'length_segments': LENGTH_SEGMENTS,
        'width_segments': WIDTH_SEGMENTS,
        'vertices_per_lamella': (LENGTH_SEGMENTS + 1) * (WIDTH_SEGMENTS + 1),
        'faces_per_lamella': len(lamellae[0].data.polygons),
        'expected_faces_per_lamella': LENGTH_SEGMENTS * WIDTH_SEGMENTS,
        'open_boundary': True,
        'interior_faces_deleted': False,
    },
    'totals': {
        'vertices': total_verts,
        'faces': total_faces,
        'meshes': LAMELLA_COUNT
    },
    'material_count': 1,
    'material': material.name,
    'animation_clips': [MASTER_CLIP],
    'duration_seconds': END / FPS,

    'diagnostic_renders': [
        str(WORK / 'diagnostic-front.png'),
        str(WORK / 'diagnostic-oblique.png'),
        str(WORK / 'diagnostic-layer-isolation.png'),
    ],
}
(WORK / 'build-report.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
