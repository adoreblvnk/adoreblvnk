import bpy
import json
import math
import os
import struct
from pathlib import Path

from mathutils import Vector

PROJECT = Path(__file__).resolve().parents[2]
WORK = Path(os.environ.get('PORTRAIT_ORBIT_WORKDIR', '/tmp/scheduler-manifold'))
WORK.mkdir(parents=True, exist_ok=True)
OUT = PROJECT / 'public/models/portrait-orbit.glb'
OUT.parent.mkdir(parents=True, exist_ok=True)

FPS = 24
DURATION = 16.0
END = int(FPS * DURATION)
ORBIT_CLIP = 'SCHEDULER_ORBIT'
ASSEMBLY_CLIP = 'ASSEMBLY_LOAD_IN'
ASSEMBLY_DURATION = 1.45
SEGMENTS = 220
START_ANGLE = 0.70
# Continuous annular lanes preserve the Saturn silhouette at every vertical-axis
# phase. Scheduler character comes from forks, width steps, ribs and apertures,
# not from a gap that can disappear behind the portrait.
END_ANGLE = START_ANGLE + math.tau

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.fps = FPS
scene.frame_start = 0
scene.frame_end = END
scene.world = bpy.data.worlds.new('World')
scene.world.color = (0.008, 0.008, 0.008)


def material(name, value, roughness=0.7):
    mat = bpy.data.materials.new(name)
    mat.diffuse_color = (value, value, value, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (value, value, value, 1.0)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = 0.0
    return mat


materials = [
    material('MANIFOLD_PAPER', 0.84, 0.74),
    material('MANIFOLD_MID', 0.58, 0.80),
    material('MANIFOLD_DARK', 0.27, 0.86),
]

root = bpy.data.objects.new('PORTRAIT_ORBIT_ROOT', None)
controller = bpy.data.objects.new('SCHEDULER_CONTROLLER', None)
alignment = bpy.data.objects.new('HORIZONTAL_RING_ALIGNMENT', None)
bpy.context.collection.objects.link(root)
bpy.context.collection.objects.link(controller)
bpy.context.collection.objects.link(alignment)
alignment.parent = root
controller.parent = alignment
# Geometry is authored in X-Z for straightforward path construction, then laid
# into Blender X-Y. GLTF exports Blender Z as Three Y, yielding Saturn-like
# horizontal rings around the portrait's vertical axis.
alignment.rotation_euler.x = math.radians(30.0)
root['assembly_clip'] = ASSEMBLY_CLIP
root['assembly_duration'] = ASSEMBLY_DURATION
controller['entropy_name'] = 'scheduler'
controller['entropy_clip'] = ORBIT_CLIP
controller['entropy_gain'] = 0.72
controller['entropy_attack'] = 0.18
controller['entropy_release'] = 0.045
root['asset_family'] = 'forked_scheduler_manifold'
root['duration_seconds'] = DURATION
root['lane_count'] = 3
root['detail_language'] = 'forks, stepped widths, ribs, apertures, notches'
root.location.z = -0.12

vertices = []
faces = []
material_indices = []
lane_vertex_ranges = [[], [], []]


def smoothstep(value):
    return value * value * (3.0 - 2.0 * value)


def branch_envelope(u):
    return math.sin(math.pi * u) ** 0.78


def frame_for(lane, u):
    angle = START_ANGLE + (END_ANGLE - START_ANGLE) * u
    spread = branch_envelope(u)
    lane_sign = (-1.0, 0.0, 1.0)[lane]
    radius = 1.88 + lane_sign * 0.25 * spread
    depth_radius = 1.12 + lane_sign * 0.09 * spread
    phase = (0.0, 0.42, -0.33)[lane]
    depth_phase = 0.0

    # Native horizontal annulus in Blender X-Y. Blender Z exports as Three Y,
    # so Z is only a restrained vertical lane deviation around the torso.
    x = radius * math.cos(angle)
    y = depth_radius * math.sin(angle + depth_phase)
    z = lane_sign * 0.10 * spread + 0.045 * math.sin(angle * 2.0 + phase)

    # Lane-specific asynchronous deviations disappear at fork and reconnect.
    x += spread * (0.07 * lane_sign + 0.035 * math.sin(angle * 3.0 + phase))
    z += spread * (0.025 * math.sin(angle * 3.0 - phase))
    y += spread * (lane_sign * 0.08 + 0.035 * math.cos(angle * 2.0 - phase))

    # Numerical tangent.
    eps = 1.0 / (SEGMENTS * 3.0)
    u2 = min(1.0, u + eps)
    a2 = START_ANGLE + (END_ANGLE - START_ANGLE) * u2
    s2 = branch_envelope(u2)
    r2 = 1.88 + lane_sign * 0.25 * s2
    dr2 = 1.12 + lane_sign * 0.09 * s2
    p2 = Vector((
        r2 * math.cos(a2) + s2 * (0.07 * lane_sign + 0.035 * math.sin(a2 * 3.0 + phase)),
        dr2 * math.sin(a2 + depth_phase) + s2 * (lane_sign * 0.08 + 0.035 * math.cos(a2 * 2.0 - phase)),
        lane_sign * 0.10 * s2 + 0.045 * math.sin(a2 * 2.0 + phase) + s2 * (0.025 * math.sin(a2 * 3.0 - phase)),
    ))
    center = Vector((x, y, z))
    tangent = (p2 - center).normalized()
    radial = Vector((math.cos(angle), math.sin(angle + depth_phase), 0.0)).normalized()
    width_axis = (radial - tangent * radial.dot(tangent)).normalized()
    thickness_axis = tangent.cross(width_axis).normalized()
    return center, tangent, width_axis, thickness_axis, angle, spread


def lane_width(lane, u, angle, spread):
    base = (0.090, 0.072, 0.082)[lane]
    stepped = (1.0, 0.72, 1.18, 0.84, 1.08)[min(4, int(u * 5.0))]
    junction = 1.0 + 0.55 * (1.0 - spread)
    pulse = 1.0 + 0.13 * math.sin(angle * (2.0 + lane * 0.5) + lane)
    return base * stepped * junction * pulse


def add_prism_strip(lane):
    start_vertex = len(vertices)
    for i in range(SEGMENTS + 1):
        u = i / SEGMENTS
        center, tangent, width_axis, thickness_axis, angle, spread = frame_for(lane, u)
        width = lane_width(lane, u, angle, spread)
        thickness = 0.038 * (1.0 + 0.18 * math.cos(angle * 2.0 + lane))
        # Four-sided extremely thin folded lane.
        corners = (
            center - width_axis * width - thickness_axis * thickness,
            center + width_axis * width - thickness_axis * thickness,
            center + width_axis * width + thickness_axis * thickness,
            center - width_axis * width + thickness_axis * thickness,
        )
        indices = []
        for corner in corners:
            indices.append(len(vertices))
            vertices.append(tuple(corner))
        lane_vertex_ranges[lane].extend(indices)

    for i in range(SEGMENTS):
        a = start_vertex + i * 4
        b = a + 4
        quads = (
            (a, a + 1, b + 1, b),
            (a + 1, a + 2, b + 2, b + 1),
            (a + 2, a + 3, b + 3, b + 2),
            (a + 3, a, b, b + 3),
        )
        faces.extend(quads)
        material_indices.extend((lane % 2, 0, (lane + 1) % 3, 0))
    faces.extend(((start_vertex, start_vertex + 3, start_vertex + 2, start_vertex + 1),
                  (start_vertex + SEGMENTS * 4, start_vertex + SEGMENTS * 4 + 1,
                   start_vertex + SEGMENTS * 4 + 2, start_vertex + SEGMENTS * 4 + 3)))
    material_indices.extend((2, 2))


for lane_index in range(3):
    add_prism_strip(lane_index)


def add_box(center, axes, half_sizes, mat_index=1, lane_tag=None):
    base = len(vertices)
    ax, ay, az = axes
    sx, sy, sz = half_sizes
    local = [
        (-sx, -sy, -sz), (sx, -sy, -sz), (sx, sy, -sz), (-sx, sy, -sz),
        (-sx, -sy, sz), (sx, -sy, sz), (sx, sy, sz), (-sx, sy, sz),
    ]
    for px, py, pz in local:
        vertices.append(tuple(center + ax * px + ay * py + az * pz))
        if lane_tag is not None:
            lane_vertex_ranges[lane_tag].append(len(vertices) - 1)
    box_faces = (
        (0, 1, 2, 3), (4, 7, 6, 5), (0, 4, 5, 1),
        (1, 5, 6, 2), (2, 6, 7, 3), (4, 0, 3, 7),
    )
    faces.extend(tuple(base + value for value in face) for face in box_faces)
    material_indices.extend((mat_index,) * 6)


# Broad fork and reconnection junctions make the system visually one authored manifold.
for u in (0.012, 0.988):
    center, tangent, width_axis, thickness_axis, _, _ = frame_for(1, u)
    add_box(center, (width_axis, tangent, thickness_axis), (0.24, 0.12, 0.050), 0, 1)

# Meso-scale ribs and dark inset aperture proxies. They are physical geometry large enough
# to survive the production Bayer pass, not micro-greebles.
rib_positions = (
    (0, 0.13), (0, 0.27), (0, 0.47), (0, 0.71), (0, 0.86),
    (1, 0.18), (1, 0.35), (1, 0.58), (1, 0.79),
    (2, 0.10), (2, 0.31), (2, 0.51), (2, 0.68), (2, 0.90),
)
for index, (lane, u) in enumerate(rib_positions):
    center, tangent, width_axis, thickness_axis, angle, spread = frame_for(lane, u)
    width = lane_width(lane, u, angle, spread)
    add_box(
        center + thickness_axis * 0.050,
        (width_axis, tangent, thickness_axis),
        (width * 1.10, 0.018 if index % 3 else 0.030, 0.018),
        2 if index % 4 == 0 else 1,
        lane,
    )

# Sparse rectangular aperture frames: four narrow bars around each dark opening.
apertures = ((0, 0.20), (0, 0.62), (1, 0.42), (1, 0.73), (2, 0.23), (2, 0.57), (2, 0.82))
for lane, u in apertures:
    center, tangent, width_axis, thickness_axis, angle, spread = frame_for(lane, u)
    width = lane_width(lane, u, angle, spread)
    surface = center + thickness_axis * 0.052
    aw = min(width * 0.48, 0.070)
    ah = 0.085
    bar = 0.012
    add_box(surface + width_axis * aw, (width_axis, tangent, thickness_axis), (bar, ah, 0.012), 2, lane)
    add_box(surface - width_axis * aw, (width_axis, tangent, thickness_axis), (bar, ah, 0.012), 2, lane)
    add_box(surface + tangent * ah, (width_axis, tangent, thickness_axis), (aw, bar, 0.012), 2, lane)
    add_box(surface - tangent * ah, (width_axis, tangent, thickness_axis), (aw, bar, 0.012), 2, lane)

mesh = bpy.data.meshes.new('SCHEDULER_MANIFOLD_MESH')
mesh.from_pydata(vertices, [], faces)
mesh.update()
for mat in materials:
    mesh.materials.append(mat)
for polygon, mat_index in zip(mesh.polygons, material_indices):
    polygon.material_index = mat_index

manifold = bpy.data.objects.new('SCHEDULER_MANIFOLD', mesh)
bpy.context.collection.objects.link(manifold)
manifold.parent = controller
manifold['entropy_family'] = 'scheduler'

# Intentional hard/soft balance: one-segment edge bevel preserves facets while taking the
# knife edge off the silhouette. The modifier is applied before shape keys are authored.
bevel = manifold.modifiers.new('MANIFOLD_EDGE_RELIEF', 'BEVEL')
bevel.width = 0.010
bevel.segments = 1
bevel.limit_method = 'ANGLE'
bpy.context.view_layer.objects.active = manifold
manifold.select_set(True)
bpy.ops.object.modifier_apply(modifier=bevel.name)

# Shape keys create independent lane flex without detaching the branching structure.
basis = manifold.shape_key_add(name='Basis')
for lane in range(3):
    key = manifold.shape_key_add(name=f'LANE_{lane}_PHASE')
    # Bevel adds vertices, so drive the original indexed vertices and leave generated edge
    # vertices stable; the deformation stays restrained and junction-safe.
    for index in lane_vertex_ranges[lane]:
        if index >= len(key.data):
            continue
        co = key.data[index].co
        radial = Vector((co.x, co.y, 0.0))
        if radial.length == 0:
            continue
        envelope = min(1.0, max(0.0, (abs(co.x) + abs(co.y) - 0.45) / 1.3))
        phase = math.atan2(co.y, co.x)
        offset = 0.032 * math.sin(phase * 3.0 + lane * 1.7) * envelope
        co += radial.normalized() * offset
        co.z += 0.012 * math.cos(phase * 2.0 - lane) * envelope

# Seamless orbit plus phase-offset local flex.
controller.rotation_mode = 'QUATERNION'
for frame, turn in ((0, 0.0), (96, 0.25), (192, 0.50), (288, 0.75), (END, 1.0)):
    # Blender Z exports to Three Y: spin the horizontal ring around the
    # portrait's vertical axis while its near/far arcs cross the portrait plane.
    controller.rotation_quaternion = (math.cos(math.pi * turn), 0.0, 0.0, math.sin(math.pi * turn))
    controller.keyframe_insert('rotation_quaternion', frame=frame, group=ORBIT_CLIP)

for lane, key in enumerate(manifold.data.shape_keys.key_blocks[1:]):
    phases = (0.0, 0.33, 0.67, 1.0)
    frames = (0, 128, 256, END)
    values = [0.5 + 0.5 * math.sin(math.tau * phase + lane * math.tau / 3.0) for phase in phases]
    values[-1] = values[0]
    for frame, value in zip(frames, values):
        key.value = value
        key.keyframe_insert('value', frame=frame, group=ORBIT_CLIP)

# Assembly load-in remains a separate clip.
root.scale = (0.08, 0.08, 0.08)
root.keyframe_insert('scale', frame=0, group=ASSEMBLY_CLIP)
root.scale = (1.0, 1.0, 1.0)
root.keyframe_insert('scale', frame=int(ASSEMBLY_DURATION * FPS), group=ASSEMBLY_CLIP)


def move_action_to_nla(obj, name):
    if not obj.animation_data or not obj.animation_data.action:
        return
    action = obj.animation_data.action
    track = obj.animation_data.nla_tracks.new()
    track.name = name
    track.strips.new(name, int(action.frame_range[0]), action)
    obj.animation_data.action = None


move_action_to_nla(controller, ORBIT_CLIP)
move_action_to_nla(manifold.data.shape_keys, ORBIT_CLIP)
move_action_to_nla(root, ASSEMBLY_CLIP)

# Tracker anchors follow stable structural junctions.
trackers = []
for index, u in enumerate((0.02, 0.28, 0.54, 0.80)):
    lane = (1, 0, 2, 1)[index]
    center, _, _, _, _, _ = frame_for(lane, u)
    anchor = bpy.data.objects.new(f'TRACKER_{index:02d}', None)
    bpy.context.collection.objects.link(anchor)
    anchor.parent = controller
    anchor.location = center
    anchor['tracker_index'] = index
    trackers.append(anchor)

# Export the production asset.
bpy.ops.object.select_all(action='DESELECT')
for obj in (root, controller, alignment, manifold, *trackers):
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
    export_morph=True,
    export_morph_normal=True,
)

# Standalone evidence render with a neutral portrait-safe proxy.
scene.render.resolution_x = 1280
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.film_transparent = False
scene.view_settings.look = 'AgX - Medium High Contrast'

camera_data = bpy.data.cameras.new('PreviewCamera')
camera = bpy.data.objects.new('PreviewCamera', camera_data)
bpy.context.collection.objects.link(camera)
scene.camera = camera
camera.location = (4.35, -7.2, 3.1)
camera.data.type = 'ORTHO'
camera.data.ortho_scale = 4.75
camera.rotation_euler = (math.radians(75), 0.0, math.radians(31))
constraint = camera.constraints.new(type='TRACK_TO')
constraint.target = root
constraint.track_axis = 'TRACK_NEGATIVE_Z'
constraint.up_axis = 'UP_Y'

key = bpy.data.lights.new('Key', 'AREA')
key.energy = 1050
key.size = 5.0
key_obj = bpy.data.objects.new('Key', key)
bpy.context.collection.objects.link(key_obj)
key_obj.location = (-3.5, -4.0, 5.0)
fill = bpy.data.lights.new('Fill', 'AREA')
fill.energy = 500
fill.size = 4.0
fill_obj = bpy.data.objects.new('Fill', fill)
bpy.context.collection.objects.link(fill_obj)
fill_obj.location = (4.0, 1.0, 1.5)

# Avoid the assembly clip's intentionally tiny first frame in standalone evidence.
for frame, filename in ((72, 'scheduler-front.png'), (168, 'scheduler-quarter.png'), (264, 'scheduler-rear.png')):
    scene.frame_set(frame)
    scene.render.filepath = str(WORK / filename)
    bpy.ops.render.render(write_still=True)

bpy.ops.wm.save_as_mainfile(filepath=str(WORK / 'scheduler-manifold-source.blend'))

triangles = sum(len(poly.vertices) - 2 for poly in manifold.data.polygons)
report = {
    'asset_family': 'forked_scheduler_manifold',
    'mesh_objects': 1,
    'lanes': 3,
    'triangles': triangles,
    'vertices': len(manifold.data.vertices),
    'materials': len(manifold.data.materials),
    'morph_targets': len(manifold.data.shape_keys.key_blocks) - 1,
    'clips': [ORBIT_CLIP, ASSEMBLY_CLIP],
    'duration_seconds': DURATION,
    'apertures': len(apertures),
    'ribs': len(rib_positions),
    'glb_bytes': OUT.stat().st_size,
    'glb': str(OUT),
}
(WORK / 'build-report.json').write_text(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))
