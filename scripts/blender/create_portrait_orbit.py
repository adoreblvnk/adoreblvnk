import bpy
import json
import math
import os
from pathlib import Path

from mathutils import Vector

PROJECT = Path(__file__).resolve().parents[2]
WORK = Path(os.environ.get('PORTRAIT_ORBIT_WORKDIR', '/tmp/portrait-fluid-loop'))
WORK.mkdir(parents=True, exist_ok=True)
OUT = PROJECT / 'public/models/portrait-orbit.glb'
OUT.parent.mkdir(parents=True, exist_ok=True)

FPS = 24
END = 240
LOOP_CLIP = 'FLUID_LOOP'
ASSEMBLY_CLIP = 'ASSEMBLY_LOAD_IN'
ASSEMBLY_DURATION = 1.5

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.fps = FPS
scene.frame_start = 0
scene.frame_end = END
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = True
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'SINE'

world = bpy.data.worlds.new('World')
world.color = (0.006, 0.006, 0.006)
scene.world = world

material = bpy.data.materials.new('FLUID_SIGNAL_WHITE')
material.diffuse_color = (0.78, 0.80, 0.80, 1.0)
material.use_nodes = True
bsdf = material.node_tree.nodes.get('Principled BSDF')
bsdf.inputs['Base Color'].default_value = (0.78, 0.80, 0.80, 1.0)
bsdf.inputs['Roughness'].default_value = 0.72
bsdf.inputs['Metallic'].default_value = 0.0


def move_action_to_track(owner, track_name):
    if not owner.animation_data or not owner.animation_data.action:
        return
    action = owner.animation_data.action
    track = owner.animation_data.nla_tracks.new()
    track.name = track_name
    track.strips.new(track_name, int(action.frame_range[0]), action)
    owner.animation_data.action = None


root = bpy.data.objects.new('PORTRAIT_FLUID_ROOT', None)
assembly = bpy.data.objects.new('PORTRAIT_FLUID_ASSEMBLY', None)
bpy.context.collection.objects.link(root)
bpy.context.collection.objects.link(assembly)
assembly.parent = root
root['assembly_clip'] = ASSEMBLY_CLIP
root['assembly_duration'] = ASSEMBLY_DURATION
root['entropy_name'] = 'fluid'
root['entropy_clip'] = LOOP_CLIP
root['entropy_gain'] = 0.78
root['entropy_attack'] = 0.16
root['entropy_release'] = 0.032

# A single implicit body: broad rear basins fuse through a central backing mass,
# while one restrained lower-right swell reaches forward around the portrait edge.
meta_data = bpy.data.metaballs.new('FLUID_BODY_FIELD')
meta_data.resolution = 0.075
meta_data.render_resolution = 0.055
meta_data.threshold = 0.62
meta = bpy.data.objects.new('FLUID_BODY_FIELD', meta_data)
bpy.context.collection.objects.link(meta)

positive_fields = (
    (-1.08, 1.08, 0.92, 0.92),
    (0.16, 1.12, 1.08, 1.03),
    (1.16, 1.06, 0.55, 0.86),
    (1.28, 1.00, -0.34, 0.88),
    (0.55, 1.04, -1.10, 0.96),
    (-0.58, 1.10, -1.12, 0.88),
    (-1.22, 1.10, -0.42, 0.84),
    (-1.27, 1.08, 0.36, 0.82),
    (0.00, 1.18, -0.02, 1.10),
    (0.92, -0.24, -0.82, 0.62),
    (1.22, 0.42, -0.58, 0.58),
)
for x, y, z, radius in positive_fields:
    element = meta_data.elements.new()
    element.co = (x, y, z)
    element.radius = radius
    element.stiffness = 2.15

# Offset pressure bites break the silhouette without producing a clean annulus.
for x, y, z, radius in ((1.30, 1.06, 0.82, 0.46), (-1.12, 1.10, -0.88, 0.42)):
    element = meta_data.elements.new()
    element.co = (x, y, z)
    element.radius = radius
    element.stiffness = 1.7
    element.use_negative = True

bpy.context.view_layer.objects.active = meta
meta.select_set(True)
bpy.ops.object.convert(target='MESH')
fluid = bpy.context.active_object
fluid.name = 'FLUID_BODY'
fluid.data.name = 'FLUID_BODY_MESH'
fluid.parent = assembly
fluid.data.materials.append(material)
fluid['sculpture_role'] = 'fluid_body'
for polygon in fluid.data.polygons:
    polygon.use_smooth = True

# Stabilize the generated field and remove negligible loose islands if any.
bpy.context.view_layer.objects.active = fluid
fluid.select_set(True)
bpy.ops.object.mode_set(mode='EDIT')
bpy.ops.mesh.select_all(action='SELECT')
bpy.ops.mesh.remove_doubles(threshold=0.0005)
bpy.ops.object.mode_set(mode='OBJECT')

basis = fluid.shape_key_add(name='Basis')
base_positions = [vertex.co.copy() for vertex in fluid.data.vertices]
transfer_centers = (
    (Vector((-0.95, 1.05, 0.78)), 0.2),
    (Vector((0.55, 1.06, 0.90)), 1.8),
    (Vector((1.00, -0.04, -0.64)), 3.3),
    (Vector((-0.45, 1.06, -0.92)), 4.9),
)


def deform(position, phase):
    result = position.copy()
    for center, seed in transfer_centers:
        delta = position - center
        distance = delta.length
        weight = math.exp(-(distance * distance) / 1.05)
        pulse = math.sin(phase + seed)
        if distance > 0.0001:
            result += delta.normalized() * (0.070 * pulse * weight)
        result.x += 0.035 * math.cos(phase + seed) * weight
        result.z += 0.045 * math.sin(phase + seed * 0.7) * weight
        result.y += 0.025 * math.cos(phase * 1.2 + seed) * weight
    # A slow pressure crease travels through the outer shell.
    crease = math.sin(position.x * 2.1 + position.z * 1.5 + phase)
    result.y += 0.018 * crease * max(0.0, min(1.0, abs(position.x) + abs(position.z) - 0.6))
    return result


keys = []
for phase_index, phase in enumerate((math.pi * 0.5, math.pi, math.pi * 1.5)):
    key = fluid.shape_key_add(name=f'FLUID_PHASE_{phase_index + 1}')
    for vertex_index, position in enumerate(base_positions):
        key.data[vertex_index].co = deform(position, phase)
    keys.append(key)

for frame, active in ((0, None), (60, 0), (120, 1), (180, 2), (240, None)):
    for key_index, key in enumerate(keys):
        key.value = 1.0 if active == key_index else 0.0
        key.keyframe_insert('value', frame=frame, group=LOOP_CLIP)
move_action_to_track(fluid.data.shape_keys, LOOP_CLIP)

# Bounded sway keeps the sculpture wrapped around protected facial and hand zones.
root.rotation_mode = 'XYZ'
for frame, angle in ((0, 0.0), (60, 0.042), (120, 0.0), (180, -0.042), (240, 0.0)):
    root.rotation_euler = (0.0, angle, 0.0)
    root.keyframe_insert('rotation_euler', frame=frame, group=LOOP_CLIP)
move_action_to_track(root, LOOP_CLIP)

for frame, scale in ((0, 0.04), (8, 0.18), (18, 0.72), (29, 1.04), (36, 1.0)):
    assembly.scale = (scale, scale, scale)
    assembly.keyframe_insert('scale', frame=frame, group=ASSEMBLY_CLIP)
move_action_to_track(assembly, ASSEMBLY_CLIP)

tracker_positions = (
    (-1.26, 0.38, 0.52),
    (0.30, 0.40, 1.34),
    (1.42, 0.04, -0.22),
    (-0.30, 0.36, -1.42),
)
trackers = []
for index, position in enumerate(tracker_positions):
    anchor = bpy.data.objects.new(f'TRACKER_{index:02d}', None)
    bpy.context.collection.objects.link(anchor)
    anchor.parent = assembly
    anchor.location = position
    anchor['tracker_index'] = index
    trackers.append(anchor)

bpy.ops.object.select_all(action='DESELECT')
for obj in (root, assembly, fluid, *trackers):
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
    export_force_sampling=True,
    export_materials='EXPORT',
    export_extras=True,
    export_yup=True,
)

bpy.ops.wm.save_as_mainfile(filepath=str(WORK / 'portrait-fluid-loop-source.blend'))


def point_camera(camera, target=Vector((0, 0, -0.02))):
    camera.rotation_euler = (target - camera.location).to_track_quat('-Z', 'Y').to_euler()


camera_data = bpy.data.cameras.new('DIAGNOSTIC_CAMERA')
camera = bpy.data.objects.new('DIAGNOSTIC_CAMERA', camera_data)
bpy.context.collection.objects.link(camera)
scene.camera = camera
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.8
key_light = bpy.data.objects.new('KEY', bpy.data.lights.new('KEY', 'AREA'))
key_light.data.energy = 900
key_light.data.shape = 'DISK'
key_light.data.size = 5
key_light.location = (-3.5, -4.5, 5.0)
bpy.context.collection.objects.link(key_light)
fill = bpy.data.objects.new('FILL', bpy.data.lights.new('FILL', 'AREA'))
fill.data.energy = 520
fill.data.size = 4
fill.location = (4.0, -1.5, 1.0)
bpy.context.collection.objects.link(fill)

scene.frame_set(60)
camera.location = (0, -8, 0.15)
point_camera(camera)
scene.render.filepath = str(WORK / 'fluid-loop-front.png')
bpy.ops.render.render(write_still=True)
camera.location = (5.3, -6.4, 3.4)
point_camera(camera)
scene.render.filepath = str(WORK / 'fluid-loop-oblique.png')
bpy.ops.render.render(write_still=True)

report = {
    'reference': 'Abstract Geometry Fluid Seamless Loop Animation by Guzdek Adam, CC BY 4.0; original procedural adaptation',
    'source': 'https://sketchfab.com/3d-models/abstract-geometry-fluid-seamless-loop-animation-5eb25e2015e94f9ba17450ac342a8b08',
    'license': 'https://creativecommons.org/licenses/by/4.0/',
    'mesh_objects': 1,
    'vertices': len(fluid.data.vertices),
    'polygons': len(fluid.data.polygons),
    'shape_keys': 3,
    'animation_clips': [LOOP_CLIP, ASSEMBLY_CLIP],
    'duration_seconds': END / FPS,
    'assembly_duration_seconds': ASSEMBLY_DURATION,
    'tracker_anchors': len(trackers),
    'glb': str(OUT),
}
(WORK / 'build-report.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
