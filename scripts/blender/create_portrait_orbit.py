import bpy, json, math, os, random
from pathlib import Path
from mathutils import Quaternion, Vector

PROJECT = Path(__file__).resolve().parents[2]
WORK = Path(os.environ.get('PORTRAIT_ORBIT_WORKDIR', '/tmp/portrait-orbit-entropy'))
WORK.mkdir(parents=True, exist_ok=True)
OUT = PROJECT / 'public/models/portrait-orbit.glb'
OUT.parent.mkdir(parents=True, exist_ok=True)

FPS = 24
END = 384
TRACK = 'ENTROPY_ORBIT'
ASSEMBLY_CLIP = 'ASSEMBLY_LOAD_IN'
ASSEMBLY_DURATION = 1.45
PROFILE_WIDTH_SCALE = 0.32
PROFILE_DEPTH_SCALE = 0.30
ORBIT_VERTICAL_SCALE = 0.35
PIECE_CURVATURE_SCALE = 0.52
ORBIT_DEPTH_SCALE = 0.82

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.fps = FPS
scene.frame_start = 0
scene.frame_end = END
bpy.context.preferences.edit.keyframe_new_interpolation_type = 'LINEAR'
world = bpy.data.worlds.new('World')
world.color = (0.003, 0.003, 0.003)
scene.world = world


def generated_texture(name, pattern, size=128):
    image = bpy.data.images.new(name, width=size, height=size, alpha=False)
    rng = random.Random(73 if pattern == 'grain' else 29)
    pixels = []
    for y in range(size):
        for x in range(size):
            if pattern == 'ribbed':
                band = ((x + y * 2) // 11) % 3
                value = (0.88, 0.50, 0.72)[band]
                value += 0.05 * math.sin(y * 0.31)
            else:
                cell_x, cell_y = x // 9, y // 9
                seeded = random.Random(cell_x * 92821 + cell_y * 68917 + 41)
                value = 0.44 + seeded.random() * 0.46
                if (cell_x + cell_y) % 5 == 0:
                    value *= 0.68
            value = max(0.0, min(1.0, value))
            pixels.extend((value, value, value, 1.0))
    image.pixels.foreach_set(pixels)
    image.pack()
    return image


def make_material(name, value, roughness, texture=None):
    material = bpy.data.materials.new(name)
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    bsdf = nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (value, value, value, 1)
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Metallic'].default_value = 0.0
    if texture:
        tex = nodes.new('ShaderNodeTexImage')
        tex.image = texture
        tex.interpolation = 'Closest'
        tex.extension = 'REPEAT'
        links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    return material


ribbed_image = generated_texture('ENTROPY_RIBBED_TEXTURE', 'ribbed')
grain_image = generated_texture('ENTROPY_GRAIN_TEXTURE', 'grain')
materials = {
    'solid': make_material('ENTROPY_SOLID', 0.86, 0.54),
    'ribbed': make_material('ENTROPY_RIBBED', 0.78, 0.62, ribbed_image),
    'grain': make_material('ENTROPY_GRAIN', 0.72, 0.74, grain_image),
    'dark': make_material('ENTROPY_DARK', 0.46, 0.68),
}

root = bpy.data.objects.new('PORTRAIT_ORBIT_ROOT', None)
primary_plane = bpy.data.objects.new('PORTRAIT_ORBIT_PLANE', None)
counter_plane = bpy.data.objects.new('ENTROPY_COUNTER_PLANE', None)
drift_plane = bpy.data.objects.new('ENTROPY_DRIFT_PLANE', None)
cross_plane = bpy.data.objects.new('ENTROPY_CROSS_PLANE', None)
echo_plane = bpy.data.objects.new('ENTROPY_ECHO_PLANE', None)
primary = bpy.data.objects.new('PORTRAIT_ORBIT_CONTROLLER', None)
counter = bpy.data.objects.new('ENTROPY_COUNTER_CONTROLLER', None)
drift = bpy.data.objects.new('ENTROPY_DRIFT_CONTROLLER', None)
cross = bpy.data.objects.new('ENTROPY_CROSS_CONTROLLER', None)
echo = bpy.data.objects.new('ENTROPY_ECHO_CONTROLLER', None)
planes = (primary_plane, counter_plane, drift_plane, cross_plane, echo_plane)
controllers = (primary, counter, drift, cross, echo)
for obj in (root, *planes, *controllers):
    bpy.context.collection.objects.link(obj)
for plane, controller in zip(planes, controllers):
    plane.parent = root
    controller.parent = plane

family_configs = {
    'counter': (counter, 'ENTROPY_COUNTER', 1.70, 0.34, 0.045),
    'drift': (drift, 'ENTROPY_DRIFT', 1.00, 0.22, 0.025),
    'cross': (cross, 'ENTROPY_CROSS', 1.45, 0.30, 0.032),
    'echo': (echo, 'ENTROPY_ECHO', 1.15, 0.25, 0.028),
    'orbit': (primary, 'ENTROPY_ORBIT', 1.30, 0.28, 0.035),
}
root['assembly_clip'] = ASSEMBLY_CLIP
root['assembly_duration'] = ASSEMBLY_DURATION
for family, (controller, clip, gain, attack, release) in family_configs.items():
    controller['entropy_name'] = family
    controller['entropy_clip'] = clip
    controller['entropy_gain'] = gain
    controller['entropy_attack'] = attack
    controller['entropy_release'] = release

# Lower the orbital assembly independently of the portrait, then give each family
# a fixed shallow inclination. Controllers rotate locally inside these planes.
root.location.z = -0.34
for plane, degrees in zip(planes, ((6.0, 1.5), (-7.0, -3.0), (4.0, 5.5), (-4.5, 8.0), (8.5, -5.5))):
    plane.rotation_euler = (math.radians(degrees[0]), math.radians(degrees[1]), 0)
parts = []
animated = {}


def make_arc(name, parent, center_angle, span, rx, rz, width, thickness, depth, material_key, subdivisions=14, texture_repeat=3.0):
    width *= PROFILE_WIDTH_SCALE
    thickness *= PROFILE_DEPTH_SCALE
    rz *= ORBIT_VERTICAL_SCALE
    ry = rx * ORBIT_DEPTH_SCALE + depth * 0.08
    path_span = span * PIECE_CURVATURE_SCALE
    path_scale = 1 / PIECE_CURVATURE_SCALE
    base_x = rx * math.cos(center_angle)
    base_y = ry * math.sin(center_angle)
    base_z = rz * math.sin(center_angle)
    centers, tangents = [], []
    for i in range(subdivisions + 1):
        u = i / subdivisions
        angle = center_angle + path_span * (u - 0.5)
        x = base_x + (rx * math.cos(angle) - base_x) * path_scale
        y = base_y + (ry * math.sin(angle) - base_y) * path_scale
        z = base_z + 0.012 * math.sin(u * math.tau + center_angle * 1.7)
        centers.append(Vector((x, y, z)))
        tangents.append(Vector((
            -rx * math.sin(angle) * path_span * path_scale,
            ry * math.cos(angle) * path_span * path_scale,
            0.012 * math.tau * math.cos(u * math.tau),
        )).normalized())

    vertices, faces = [], []
    for i, (center, tangent) in enumerate(zip(centers, tangents)):
        u = i / subdivisions
        angle = center_angle + path_span * (u - 0.5)
        radial = Vector((math.cos(angle), math.sin(angle), 0.05 * math.sin(center_angle + u * math.pi))).normalized()
        normal = tangent.cross(radial).normalized()
        width_here = width * (0.76 + 0.34 * math.sin(math.pi * u) + 0.07 * math.sin(u * math.tau * 3 + center_angle))
        thickness_here = thickness * (0.88 + 0.12 * math.cos(u * math.tau + center_angle))
        vertices.extend([
            tuple(center - radial * width_here / 2 - normal * thickness_here / 2),
            tuple(center + radial * width_here / 2 - normal * thickness_here / 2),
            tuple(center + radial * width_here / 2 + normal * thickness_here / 2),
            tuple(center - radial * width_here / 2 + normal * thickness_here / 2),
        ])

    for i in range(subdivisions):
        a, b = i * 4, (i + 1) * 4
        faces.extend([
            (a, a + 1, b + 1, b),
            (a + 1, a + 2, b + 2, b + 1),
            (a + 2, a + 3, b + 3, b + 2),
            (a + 3, a, b, b + 3),
        ])
    faces.extend([(0, 3, 2, 1), (subdivisions * 4, subdivisions * 4 + 1, subdivisions * 4 + 2, subdivisions * 4 + 3)])

    pivot = centers[len(centers) // 2]
    local_vertices = [tuple(Vector(vertex) - pivot) for vertex in vertices]
    mesh = bpy.data.meshes.new(name + '_MESH')
    mesh.from_pydata(local_vertices, [], faces)
    mesh.materials.append(materials[material_key])
    uv = mesh.uv_layers.new(name='UVMap')
    across = (0.0, 1.0, 1.0, 0.0)
    for loop in mesh.loops:
        vertex = loop.vertex_index
        uv.data[loop.index].uv = ((vertex // 4) / subdivisions * texture_repeat, across[vertex % 4])

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = pivot
    midpoint_tangent = tangents[len(tangents) // 2]
    obj['orbit_tangent'] = [midpoint_tangent.x, midpoint_tangent.z, -midpoint_tangent.y]
    obj.parent = parent
    parts.append(obj)

    bevel = obj.modifiers.new('ENTROPY_EDGE', 'BEVEL')
    bevel.width = min(width, thickness) * 0.16
    bevel.segments = 1
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.modifier_apply(modifier=bevel.name)
    for uv_loop in obj.data.uv_layers['UVMap'].data:
        uv_loop.uv = tuple(round(value, 4) for value in uv_loop.uv)
    obj.select_set(False)
    return obj


def make_tick(name, parent, angle, radius_x, radius_z, depth, dimensions, material_key):
    return make_arc(
        name,
        parent,
        angle,
        dimensions[2] / radius_x,
        radius_x,
        radius_z,
        dimensions[0],
        dimensions[1],
        depth,
        material_key,
        subdivisions=8,
        texture_repeat=1.2,
    )


# Five sparse orbital families reuse the restored geometry at a 4 / 4 / 3 / 3 / 3 split.
primary_specs = [
    ('ORBIT_SEGMENT_00', 0.10, 0.60, 1.48, 1.20, 0.19, 0.13, -0.66, 'solid'),
    ('ORBIT_SEGMENT_03', 1.62, 0.72, 1.44, 1.16, 0.145, 0.11, 0.56, 'grain'),
    ('ORBIT_SEGMENT_06', 3.34, 0.82, 1.50, 1.22, 0.17, 0.10, -0.72, 'ribbed'),
    ('ORBIT_SEGMENT_10', 5.10, 0.64, 1.46, 1.18, 0.13, 0.12, 0.58, 'grain'),
]
primary_parts = [make_arc(name, primary, center, span, rx, rz, width, thick, depth, mat) for name, center, span, rx, rz, width, thick, depth, mat in primary_specs]

counter_specs = [
    ('ENTROPY_SHARD_00', 0.52, 0.22, 1.75, 1.36, 0.08, 0.16, 0.48, 'dark'),
    ('ENTROPY_SHARD_01', 1.96, 0.31, 1.68, 1.42, 0.15, 0.07, -0.62, 'grain'),
    ('ENTROPY_SHARD_02', 3.02, 0.17, 1.78, 1.34, 0.065, 0.20, 0.40, 'ribbed'),
    ('ENTROPY_SHARD_03', 4.52, 0.39, 1.72, 1.40, 0.12, 0.10, -0.68, 'solid'),
]
counter_parts = [make_arc(name, counter, center, span, rx, rz, width, thick, depth, mat, subdivisions=10, texture_repeat=1.8) for name, center, span, rx, rz, width, thick, depth, mat in counter_specs]

drift_parts = [
    make_tick('ENTROPY_TICK_00', drift, 0.34, 1.82, 1.42, -0.58, (0.10, 0.16, 0.38), 'ribbed'),
    make_tick('ENTROPY_TICK_01', drift, 2.26, 1.78, 1.46, 0.54, (0.19, 0.09, 0.24), 'solid'),
    make_tick('ENTROPY_TICK_02', drift, 3.92, 1.84, 1.40, -0.72, (0.08, 0.22, 0.31), 'dark'),
]

cross_specs = [
    ('CROSS_FRAGMENT_00', 0.88, 0.34, 1.56, 0.78, 0.09, 0.08, -0.50, 'ribbed'),
    ('CROSS_FRAGMENT_01', 2.42, 0.38, 1.63, 1.32, 0.105, 0.15, -0.52, 'dark'),
    ('CROSS_FRAGMENT_02', 4.18, 0.27, 1.58, 1.29, 0.075, 0.075, 0.46, 'solid'),
]
cross_parts = [make_arc(name, cross, center, span, rx, rz, width, thick, depth, mat) for name, center, span, rx, rz, width, thick, depth, mat in cross_specs]

echo_parts = [
    make_arc('ECHO_FRAGMENT_00', echo, 5.83, 0.30, 1.67, 1.34, 0.22, 0.09, -0.55, 'dark'),
    make_arc('ECHO_FRAGMENT_01', echo, 5.58, 0.20, 1.76, 1.37, 0.20, 0.07, 0.52, 'grain', subdivisions=10, texture_repeat=1.8),
    make_tick('ECHO_FRAGMENT_02', echo, 5.36, 1.80, 1.44, 0.45, (0.15, 0.11, 0.18), 'grain'),
]

part_families = {
    **{part: 'orbit' for part in primary_parts},
    **{part: 'counter' for part in counter_parts},
    **{part: 'drift' for part in drift_parts},
    **{part: 'cross' for part in cross_parts},
    **{part: 'echo' for part in echo_parts},
}
degrees_per_orbit = (10, 12, 14, 16, 18, 20, 22, 24)
for index, part in enumerate(sorted(parts, key=lambda item: item.name)):
    direction = -1 if index % 2 else 1
    part['entropy_family'] = part_families[part]
    part['rotation_axis'] = part.pop('orbit_tangent')
    part['rotation_rate'] = direction * math.radians(degrees_per_orbit[index % len(degrees_per_orbit)]) / 16

assembly_parts = [*counter_parts, *cross_parts, *drift_parts, *echo_parts, *primary_parts]
assembly_wrappers = []
for index, part in enumerate(assembly_parts):
    delay = (index % 6) * 0.045 + (index // 6) * 0.02
    rotation = (
        ((index % 3) - 1) * 0.32,
        (((index * 2) % 5) - 2) * 0.18,
        (((index * 3) % 7) - 3) * 0.11,
    )
    wrapper = bpy.data.objects.new(f'ASSEMBLY_{index:02d}', None)
    bpy.context.collection.objects.link(wrapper)
    wrapper.parent = part.parent
    part.parent = wrapper
    wrapper['assembly_order'] = index
    wrapper['assembly_delay'] = delay
    wrapper['assembly_rotation'] = rotation
    assembly_wrappers.append(wrapper)

tracker_anchors = []
for index, part in enumerate((primary_parts[0], primary_parts[1], primary_parts[2], primary_parts[3])):
    anchor = bpy.data.objects.new(f'TRACKER_{index:02d}', None)
    bpy.context.collection.objects.link(anchor)
    anchor.parent = part
    anchor.location = sum((Vector(corner) for corner in part.bound_box), Vector()) / 8
    anchor['tracker_index'] = index
    tracker_anchors.append(anchor)

for wrapper in assembly_wrappers:
    delay = wrapper['assembly_delay']
    rotation = Vector(wrapper['assembly_rotation'])
    wrapper.rotation_mode = 'XYZ'
    for frame in range(math.ceil(ASSEMBLY_DURATION * FPS) + 1):
        progress = min(max((frame / FPS - delay) / 0.95, 0), 1)
        ease = 1 - (1 - progress) ** 3
        wrapper.scale = (0.08 + 0.92 * ease,) * 3
        wrapper.rotation_euler = rotation * (1 - ease)
        wrapper.keyframe_insert('scale', frame=frame, group=ASSEMBLY_CLIP)
        wrapper.keyframe_insert('rotation_euler', frame=frame, group=ASSEMBLY_CLIP)
    animated[wrapper] = ASSEMBLY_CLIP


def insert_rotation(obj, frames, turns, axis=(0, 1, 0)):
    obj.rotation_mode = 'QUATERNION'
    axis_vector = Vector(axis).normalized()
    previous = None
    for frame, turn in zip(frames, turns):
        rotation = Quaternion(axis_vector, math.tau * turn)
        if previous is not None:
            rotation.make_compatible(previous)
        obj.rotation_quaternion = rotation
        obj.keyframe_insert('rotation_quaternion', frame=frame, group=TRACK)
        previous = rotation.copy()
    animated[obj] = obj['entropy_clip']


def insert_scale(obj, frames, values, track):
    for frame, value in zip(frames, values):
        obj.scale = (value, value, value)
        obj.keyframe_insert('scale', frame=frame, group=TRACK)
    animated[obj] = track


def move_action_to_track(obj, track_name):
    if not obj.animation_data or not obj.animation_data.action:
        return
    action = obj.animation_data.action
    track = obj.animation_data.nla_tracks.new()
    track.name = track_name
    track.strips.new(track_name, int(action.frame_range[0]), action)
    obj.animation_data.action = None


# Orbit around world vertical (Blender Z): pieces travel horizontally and through
# depth while retaining their authored height instead of climbing the screen.
insert_rotation(primary, [0, 96, 192, 288, 384], [0.0, 0.20, 0.55, 0.72, 1.0], axis=(0, 0, 1))
insert_rotation(counter, [0, 72, 168, 240, 312, 384], [0.0, -0.14, -0.38, -0.58, -0.78, -1.0], axis=(0, 0, 1))
insert_rotation(drift, [0, 96, 192, 288, 384], [0.0, 0.14, 0.36, 0.64, 1.0], axis=(0, 0, 1))
insert_rotation(cross, [0, 72, 168, 264, 336, 384], [0.0, 0.12, 0.34, 0.60, 0.84, 1.0], axis=(0, 0, 1))
insert_rotation(echo, [0, 96, 192, 288, 384], [0.0, -0.24, -0.46, -0.76, -1.0], axis=(0, 0, 1))

# One phase-offset pulse per family; every piece returns exactly to its starting scale.
insert_scale(primary_parts[3], [0, 96, 192, 288, 384], [1.0, 1.14, 0.86, 1.07, 1.0], 'ENTROPY_ORBIT')
insert_scale(counter_parts[1], [0, 96, 192, 288, 384], [1.0, 1.20, 0.88, 1.05, 1.0], 'ENTROPY_COUNTER')
insert_scale(drift_parts[0], [0, 96, 192, 288, 384], [1.0, 0.78, 1.18, 0.90, 1.0], 'ENTROPY_DRIFT')
insert_scale(cross_parts[1], [0, 96, 192, 288, 384], [1.0, 1.16, 0.84, 1.11, 1.0], 'ENTROPY_CROSS')
insert_scale(echo_parts[0], [0, 96, 192, 288, 384], [1.0, 0.82, 1.16, 0.91, 1.0], 'ENTROPY_ECHO')

for obj, track_name in animated.items():
    move_action_to_track(obj, track_name)

bpy.ops.object.select_all(action='DESELECT')
for obj in [root, *planes, *controllers, *assembly_wrappers, *parts, *tracker_anchors]:
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

bpy.ops.wm.save_as_mainfile(filepath=str(WORK / 'portrait-orbit-entropy-source.blend'))
report = {
    'parts': len(parts),
    'primary_parts': len(primary_parts),
    'counter_parts': len(counter_parts),
    'drift_parts': len(drift_parts),
    'cross_parts': len(cross_parts),
    'echo_parts': len(echo_parts),
    'animated_nodes': len(animated),
    'animation_clips': [*[config[1] for config in family_configs.values()], ASSEMBLY_CLIP],
    'assembly_wrappers': len(assembly_wrappers),
    'tracker_anchors': len(tracker_anchors),
    'duration_seconds': END / FPS,
    'materials': list(materials),
    'glb': str(OUT),
}
(WORK / 'build-report.json').write_text(json.dumps(report, indent=2))
print(report)
