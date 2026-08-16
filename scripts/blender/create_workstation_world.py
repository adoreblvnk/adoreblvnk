import math
import os
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
WORKDIR = Path(os.environ.get('WORKSTATION_WORKDIR', '/tmp/workstation-world'))
OUT = Path(os.environ.get('WORKSTATION_OUT', WORKDIR / 'workstation-world.raw.glb'))
FPS = 24
END = 288

WORKDIR.mkdir(parents=True, exist_ok=True)
OUT.parent.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.engine = 'BLENDER_EEVEE'
scene.render.fps = FPS
scene.frame_start = 1
scene.frame_end = END
scene.render.resolution_x = 1280
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.view_settings.look = 'AgX - Medium High Contrast'
scene.world = bpy.data.worlds.new('World')
scene.world.color = (0.004, 0.004, 0.004)

export_objects = []


def material(name, value, roughness=0.55, metallic=0.0, emission_strength=0.0):
    result = bpy.data.materials.new(name)
    result.diffuse_color = (value, value, value, 1.0)
    result.use_nodes = True
    principled = result.node_tree.nodes.get('Principled BSDF')
    principled.inputs['Base Color'].default_value = (value, value, value, 1.0)
    principled.inputs['Roughness'].default_value = roughness
    principled.inputs['Metallic'].default_value = metallic
    if emission_strength:
        emission = principled.inputs.get('Emission Color') or principled.inputs.get('Emission')
        if emission:
            emission.default_value = (value, value, value, 1.0)
        strength = principled.inputs.get('Emission Strength')
        if strength:
            strength.default_value = emission_strength
    return result


materials = {
    'ink': material('MAT_INK', 0.018, 0.74),
    'rubber': material('MAT_RUBBER', 0.028, 0.88),
    'glass': material('MAT_DARK_GLASS', 0.042, 0.20, 0.10),
    'graphite': material('MAT_GRAPHITE', 0.085, 0.58, 0.18),
    'pcb': material('MAT_PCB_GRAPHITE', 0.15, 0.48, 0.12),
    'mid': material('MAT_MID', 0.31, 0.48, 0.30),
    'copper': material('MAT_COPPER_TONE', 0.43, 0.34, 0.78),
    'silver': material('MAT_OXIDISED_SILVER', 0.60, 0.34, 0.78),
    'paper': material('MAT_OFF_WHITE', 0.84, 0.44),
    'terminal': material('MAT_TERMINAL_EMISSION', 0.94, 0.25, 0.0, 1.8),
    'signal': material('MAT_SIGNAL_EMISSION', 1.0, 0.18, 0.0, 2.8),
}


def register(obj, parent=None, semantic=None, tracker_label=None):
    if parent is not None:
        obj.parent = parent
    if semantic:
        obj['semantic'] = semantic
    if tracker_label:
        obj['tracker_label'] = tracker_label
    export_objects.append(obj)
    return obj


def add_empty(name, location, parent=None, semantic=None, tracker_label=None):
    obj = bpy.data.objects.new(name, None)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    return register(obj, parent, semantic, tracker_label)


def add_box(name, location, dimensions, mat, parent=None, bevel=0.04, rotation=(0, 0, 0), semantic=None):
    bpy.ops.mesh.primitive_cube_add(location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.dimensions = dimensions
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        modifier = obj.modifiers.new('EDGE_SOFTEN', 'BEVEL')
        modifier.width = min(bevel, min(dimensions) * 0.42)
        modifier.segments = 3
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.modifier_apply(modifier=modifier.name)
    obj.data.materials.append(materials[mat])
    return register(obj, parent, semantic)


def add_cylinder(name, location, radius, depth, mat, parent=None, rotation=(math.pi / 2, 0, 0), vertices=32, semantic=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices, radius=radius, depth=depth, location=location, rotation=rotation)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(materials[mat])
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return register(obj, parent, semantic)


def add_sphere(name, location, radius, mat, parent=None, segments=24, rings=12, semantic=None):
    del segments, rings
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=radius, location=location)
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(materials[mat])
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return register(obj, parent, semantic)


def add_torus(name, location, major_radius, minor_radius, mat, parent=None, rotation=(math.pi / 2, 0, 0), semantic=None, major_segments=48, minor_segments=12):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=major_radius,
        minor_radius=minor_radius,
        major_segments=major_segments,
        minor_segments=minor_segments,
        location=location,
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(materials[mat])
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return register(obj, parent, semantic)


def add_cable(name, points, radius, mat, parent=None, semantic=None, resolution=8):
    curve = bpy.data.curves.new(name, 'CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = resolution
    curve.bevel_depth = radius
    curve.bevel_resolution = 4
    spline = curve.splines.new('BEZIER')
    spline.bezier_points.add(len(points) - 1)
    for point, coordinate in zip(spline.bezier_points, points):
        point.co = coordinate
        point.handle_left_type = 'AUTO'
        point.handle_right_type = 'AUTO'
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.data.materials.append(materials[mat])
    obj['route_points'] = [axis for point in points for axis in point]
    return register(obj, parent, semantic)


def add_text(name, text, location, size, mat, parent=None, extrude=0.005, semantic=None):
    curve = bpy.data.curves.new(name, 'FONT')
    curve.body = text
    curve.align_x = 'LEFT'
    curve.align_y = 'CENTER'
    curve.size = size
    curve.extrude = extrude
    curve.bevel_depth = min(extrude * 0.28, 0.0015)
    curve.space_character = 1.0
    font_path = Path('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf')
    if font_path.exists():
        curve.font = bpy.data.fonts.load(str(font_path), check_existing=True)
    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)
    obj.location = location
    obj.rotation_euler = (math.pi / 2, 0, 0)
    obj.data.materials.append(materials[mat])
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.convert(target='MESH')
    obj = bpy.context.object
    obj.name = name
    return register(obj, parent, semantic)


def move_action_to_track(obj, track_name):
    if not obj.animation_data or not obj.animation_data.action:
        return
    action = obj.animation_data.action
    action.name = f'{track_name}__{obj.name}'
    track = obj.animation_data.nla_tracks.new()
    track.name = track_name
    strip = track.strips.new(track_name, int(action.frame_range[0]), action)
    strip.action_frame_start = action.frame_range[0]
    strip.action_frame_end = action.frame_range[1]
    obj.animation_data.action = None


def animate_rotation(obj, axis, rotations, track_name):
    obj.rotation_mode = 'XYZ'
    obj.rotation_euler[axis] = 0
    obj.keyframe_insert('rotation_euler', frame=1, index=axis, group=track_name)
    obj.rotation_euler[axis] = math.tau * rotations
    obj.keyframe_insert('rotation_euler', frame=END, index=axis, group=track_name)
    move_action_to_track(obj, track_name)


def animate_pulse(obj, frames, track_name, low=0.28, high=1.25):
    for frame, value in frames:
        obj.scale = (value, value, value)
        obj.keyframe_insert('scale', frame=frame, group=track_name)
    move_action_to_track(obj, track_name)


def animate_reveal(obj, frame, track_name='RUST_COMPILE'):
    obj.scale = (0.001, 1, 1)
    obj.keyframe_insert('scale', frame=1, group=track_name)
    obj.keyframe_insert('scale', frame=max(1, frame - 2), group=track_name)
    obj.scale = (1, 1, 1)
    obj.keyframe_insert('scale', frame=frame + 3, group=track_name)
    obj.keyframe_insert('scale', frame=END - 7, group=track_name)
    obj.scale = (0.001, 1, 1)
    obj.keyframe_insert('scale', frame=END, group=track_name)
    move_action_to_track(obj, track_name)


def text_width(text, size):
    return max(size / 7.0 * 6.0 * len(text), size)


def reveal_steps(text, duration, stepped):
    count = len(text) if stepped else max(4, duration // 2)
    for step in range(count + 1):
        yield step / count, round(duration * step / count)


def set_mask_reveal(mask, x_start, width, progress, frame, track_name='RUST_COMPILE'):
    remaining = max(0.001, 1.0 - progress)
    mask.location.x = x_start + width * (0.5 + progress * 0.5)
    mask.scale.x = remaining
    mask.keyframe_insert('location', frame=frame, index=0, group=track_name)
    mask.keyframe_insert('scale', frame=frame, index=0, group=track_name)


def animate_typewriter_mask(mask, text, size, x_start, start, duration, stepped):
    width = text_width(text, size)
    set_mask_reveal(mask, x_start, width, 0, 1)
    set_mask_reveal(mask, x_start, width, 0, max(1, start - 1))
    previous = 0
    for progress, offset in reveal_steps(text, duration, stepped):
        frame = start + offset
        if frame > start:
            set_mask_reveal(mask, x_start, width, previous, frame - 1)
        set_mask_reveal(mask, x_start, width, progress, frame)
        previous = progress
    set_mask_reveal(mask, x_start, width, 1, END - 7)
    set_mask_reveal(mask, x_start, width, 0, END)
    move_action_to_track(mask, 'RUST_COMPILE')


def animate_terminal_cursor(cursor, lines, x_start):
    first_text, first_size, first_z, first_start, first_duration, first_stepped = lines[0]
    del first_text, first_size, first_start, first_duration, first_stepped
    cursor_y = cursor.location.y
    cursor.location = (x_start, cursor_y, first_z)
    cursor.keyframe_insert('location', frame=1, group='RUST_COMPILE')
    for text, size, z, start, duration, stepped in lines:
        width = text_width(text, size)
        cursor.location = (x_start, cursor_y, z)
        cursor.keyframe_insert('location', frame=max(1, start - 1), group='RUST_COMPILE')
        previous = 0
        for progress, offset in reveal_steps(text, duration, stepped):
            frame = start + offset
            if frame > start:
                cursor.location = (x_start + width * previous, cursor_y, z)
                cursor.keyframe_insert('location', frame=frame - 1, group='RUST_COMPILE')
            cursor.location = (x_start + width * progress, cursor_y, z)
            cursor.keyframe_insert('location', frame=frame, group='RUST_COMPILE')
            previous = progress
    cursor.keyframe_insert('location', frame=END - 7, group='RUST_COMPILE')
    cursor.location = (x_start, cursor_y, first_z)
    cursor.keyframe_insert('location', frame=END, group='RUST_COMPILE')
    move_action_to_track(cursor, 'RUST_COMPILE')


def point_on_polyline(points, progress):
    vectors = [Vector(point) for point in points]
    lengths = [(vectors[index + 1] - vectors[index]).length for index in range(len(vectors) - 1)]
    total = sum(lengths)
    distance = max(0.0, min(1.0, progress)) * total
    for index, length in enumerate(lengths):
        if distance <= length or index == len(lengths) - 1:
            ratio = 0 if length == 0 else distance / length
            return vectors[index].lerp(vectors[index + 1], ratio)
        distance -= length
    return vectors[-1]


def animate_signal(obj, points, start_frame, duration, track_name='NETWORK_TRAFFIC'):
    obj.scale = (0.001, 0.001, 0.001)
    obj.keyframe_insert('scale', frame=1, group=track_name)
    obj.keyframe_insert('scale', frame=max(1, start_frame - 2), group=track_name)
    obj.scale = (1, 1, 1)
    obj.keyframe_insert('scale', frame=start_frame, group=track_name)
    for step in range(9):
        frame = start_frame + int(duration * step / 8)
        obj.location = point_on_polyline(points, step / 8)
        obj.keyframe_insert('location', frame=frame, group=track_name)
    obj.keyframe_insert('scale', frame=start_frame + duration - 2, group=track_name)
    obj.scale = (0.001, 0.001, 0.001)
    obj.keyframe_insert('scale', frame=start_frame + duration, group=track_name)
    obj.keyframe_insert('scale', frame=END, group=track_name)
    move_action_to_track(obj, track_name)


def add_fan(name, location, radius, parent, track='WORKSTATION_AMBIENT', rotations=10, depth=0.10):
    fan = add_empty(name, location, parent, 'cooling_fan')
    add_torus(f'{name}_RING', (0, 0, 0), radius, radius * 0.10, 'silver', fan, rotation=(math.pi / 2, 0, 0), major_segments=56)
    add_cylinder(f'{name}_HUB', (0, 0, 0), radius * 0.24, depth, 'mid', fan, vertices=40)
    for index in range(9):
        angle = math.tau * index / 9
        blade = add_box(
            f'{name}_BLADE_{index:02d}',
            (math.cos(angle) * radius * 0.54, 0, math.sin(angle) * radius * 0.54),
            (radius * 0.25, depth * 0.52, radius * 0.64),
            'graphite',
            fan,
            radius * 0.06,
            rotation=(0, angle + 0.28, 0),
        )
        blade['fan_blade_index'] = index
    animate_rotation(fan, 1, rotations, track)
    return fan


world_root = add_empty('WORKSTATION_WORLD', (0, 0, 0), semantic='world_root')
world_root['world_version'] = 2
world_root['detail_level'] = 'showcase'
world_root['animation_clips'] = ['WORKSTATION_AMBIENT', 'RUST_COMPILE', 'KEYBOARD_ACTIVITY', 'STORAGE_ACTIVITY', 'NETWORK_TRAFFIC']
world_root['terminal_story'] = 'cargo build --release; cargo test --release'

# Industrial monitor: front shell, rear engineering detail, controls, stand, and live terminal.
monitor = add_empty('DISPLAY_GROUP', (0, 0, 0), world_root, 'display', 'DISPLAY 01')
add_box('DISPLAY_REAR_SHELL', (0.35, 0.16, 0.72), (3.82, 0.34, 2.40), 'graphite', monitor, 0.12)
add_box('DISPLAY_FRAME', (0.35, -0.035, 0.72), (3.75, 0.17, 2.35), 'silver', monitor, 0.10)
add_box('DISPLAY_INNER_BEZEL', (0.35, -0.115, 0.72), (3.52, 0.055, 2.10), 'ink', monitor, 0.035)
add_box('DISPLAY_SCREEN', (0.35, -0.148, 0.75), (3.34, 0.018, 1.91), 'glass', monitor, 0.010, semantic='terminal_screen')
for index in range(22):
    x = -1.40 + index * 0.165
    add_box(f'DISPLAY_TOP_VENT_{index:02d}', (x, 0.343, 1.73), (0.10, 0.025, 0.025), 'ink', monitor, 0.008)
for index in range(8):
    x = -1.12 + index * 0.42
    add_cylinder(f'DISPLAY_BEZEL_SCREW_{index:02d}', (x, -0.153, 1.70 if index % 2 == 0 else -0.27), 0.027, 0.016, 'mid', monitor, vertices=20)
for index in range(4):
    add_box(f'DISPLAY_BUTTON_{index:02d}', (1.50 + index * 0.12, -0.154, -0.30), (0.065, 0.018, 0.035), 'mid', monitor, 0.008)
add_text('DISPLAY_LABEL', 'TTY-01 // RUST', (-1.25, -0.158, -0.27), 0.075, 'mid', monitor, 0.002, 'display_label')
add_box('DISPLAY_VESA_PLATE', (0.35, 0.38, 0.50), (0.72, 0.12, 0.72), 'silver', monitor, 0.06)
for x in (0.08, 0.62):
    for z in (0.24, 0.76):
        add_cylinder(f'VESA_FASTENER_{x:.2f}_{z:.2f}', (x, 0.455, z), 0.045, 0.03, 'ink', monitor, vertices=24)
add_box('DISPLAY_STAND_UPPER', (0.35, 0.34, -0.52), (0.26, 0.34, 1.28), 'silver', monitor, 0.06)
add_cylinder('DISPLAY_HINGE', (0.35, 0.24, -0.02), 0.18, 0.42, 'graphite', monitor, rotation=(0, math.pi / 2, 0), vertices=40)
add_box('DISPLAY_STAND_LOWER', (0.35, 0.20, -1.00), (0.34, 0.38, 0.50), 'graphite', monitor, 0.06)
add_box('DISPLAY_BASE', (0.35, 0.02, -1.30), (1.70, 0.86, 0.12), 'silver', monitor, 0.055)
add_torus('DISPLAY_BASE_CABLE_GROMMET', (0.35, -0.12, -1.23), 0.13, 0.025, 'ink', monitor, rotation=(0, 0, 0), major_segments=40)

# Screen scan structure and actual Rust compilation geometry.
for index in range(18):
    z = 1.55 - index * 0.096
    add_box(f'SCREEN_SCANLINE_{index:02d}', (0.35, -0.161, z), (3.12, 0.006, 0.009), 'graphite', monitor, 0)
add_box('TERMINAL_GUTTER', (-1.17, -0.167, 0.75), (0.018, 0.006, 1.70), 'mid', monitor, 0)
terminal_specs = [
    ('adore@debian:~/src/workstation', 0.092, 6, 38, True),
    ('$ cargo build --release', 0.105, 48, 42, True),
    ('Compiling proc-macro2 v1.0.95', 0.082, 96, 14, False),
    ('Compiling serde v1.0.219', 0.086, 114, 14, False),
    ('Compiling tokio v1.47.1', 0.088, 132, 14, False),
    ('Compiling workstation v0.1.0', 0.082, 150, 14, False),
    ('Finished release [optimized] in 3.81s', 0.073, 168, 18, False),
    ('$ cargo test --release', 0.102, 190, 42, True),
    ('running 12 tests ............', 0.084, 236, 14, False),
    ('test result: ok. 12 passed', 0.088, 254, 20, False),
]
terminal_cursor_lines = []
terminal_x = -1.08
for index, (line, size, start, duration, stepped) in enumerate(terminal_specs):
    z = 1.48 - index * 0.165
    row = add_text(
        f'RUST_LINE_{index:02d}',
        line,
        (terminal_x, -0.177, z),
        size,
        'terminal' if index in {0, 1, 6, 7, 9} else 'mid',
        monitor,
        0.004,
        'rust_terminal_line',
    )
    row['terminal_order'] = index
    width = text_width(line, size)
    mask = add_box(
        f'RUST_MASK_{index:02d}',
        (terminal_x + width * 0.5, -0.184, z),
        (width, 0.008, size * 1.12),
        'glass',
        monitor,
        0,
        semantic='terminal_reveal_mask',
    )
    mask['terminal_order'] = index
    animate_typewriter_mask(mask, line, size, terminal_x, start, duration, stepped)
    terminal_cursor_lines.append((line, size, z, start, duration, stepped))

cursor = add_box('TERMINAL_CURSOR', (terminal_x, -0.190, 1.48), (0.055, 0.008, 0.12), 'signal', monitor, 0.004, semantic='cursor')
animate_terminal_cursor(cursor, terminal_cursor_lines, terminal_x)
for index in range(12):
    segment = add_box(f'COMPILE_PROGRESS_{index:02d}', (-1.02 + index * 0.22, -0.181, -0.14), (0.16, 0.008, 0.035), 'signal' if index in {0, 5, 11} else 'mid', monitor, 0.004, semantic='compile_progress')
    animate_reveal(segment, 96 + index * 11)

# Open-frame host with modeled motherboard, cooling, GPU, power, ports, and fasteners.
host = add_empty('HOST_GROUP', (0, 0, 0), world_root, 'host', 'HOST 01')
for x in (2.18, 4.18):
    add_box(f'HOST_RAIL_V_{x:.2f}', (x, 0.34, 0.12), (0.12, 0.14, 2.95), 'silver', host, 0.035)
for z in (-1.32, 1.56):
    add_box(f'HOST_RAIL_H_{z:.2f}', (3.18, 0.34, z), (2.12, 0.14, 0.12), 'silver', host, 0.035)
for x in (2.22, 4.14):
    for z in (-1.28, 1.52):
        add_box(f'HOST_DEPTH_{x:.2f}_{z:.2f}', (x, 0.72, z), (0.10, 0.78, 0.10), 'graphite', host, 0.025)
for x in (2.18, 4.18):
    for z in (-1.32, 1.56):
        add_cylinder(f'HOST_CORNER_FASTENER_{x:.2f}_{z:.2f}', (x, -0.01, z), 0.055, 0.04, 'ink', host, vertices=24)
add_box('MOTHERBOARD_TRAY', (3.18, 0.22, 0.10), (1.78, 0.12, 2.50), 'ink', host, 0.05)
add_box('MOTHERBOARD', (3.18, 0.11, 0.10), (1.62, 0.08, 2.34), 'pcb', host, 0.035, semantic='motherboard')
for index in range(14):
    x = 2.50 + (index % 5) * 0.30
    z = -0.84 + (index // 5) * 0.57 + (index % 2) * 0.08
    width = 0.18 + (index % 3) * 0.10
    add_box(f'PCB_TRACE_{index:02d}', (x, 0.055, z), (width, 0.018, 0.022), 'copper', host, 0.004, rotation=(0, 0, math.radians((index % 3 - 1) * 16)))
add_box('CPU_SOCKET', (3.28, -0.015, 0.42), (0.88, 0.11, 0.88), 'silver', host, 0.035, semantic='cpu_socket')
for index in range(12):
    add_box(f'CPU_HEATSINK_FIN_{index:02d}', (2.94 + index * 0.058, -0.125, 0.42), (0.035, 0.20, 0.72), 'mid' if index % 2 else 'silver', host, 0.006)
cpu_fan = add_fan('CPU_FAN', (3.30, -0.30, 0.42), 0.46, host, rotations=15, depth=0.11)
for bank in range(4):
    x = 2.48 + bank * 0.19
    add_box(f'RAM_STICK_{bank:02d}', (x, -0.04, 0.92), (0.105, 0.20, 0.94), 'silver' if bank % 2 == 0 else 'mid', host, 0.018, semantic='memory')
    for chip in range(4):
        add_box(f'RAM_{bank:02d}_CHIP_{chip:02d}', (x, -0.155, 0.62 + chip * 0.19), (0.07, 0.028, 0.12), 'ink', host, 0.005)
    add_box(f'RAM_LATCH_{bank:02d}_TOP', (x, -0.045, 1.43), (0.13, 0.20, 0.07), 'paper', host, 0.012)
    add_box(f'RAM_LATCH_{bank:02d}_BOTTOM', (x, -0.045, 0.42), (0.13, 0.20, 0.07), 'paper', host, 0.012)
for index in range(18):
    x = 2.46 + (index % 6) * 0.23
    z = -0.28 + (index // 6) * 0.22
    add_cylinder(f'VRM_CAP_{index:02d}', (x, -0.075, z), 0.045, 0.12 + (index % 2) * 0.03, 'silver' if index % 3 else 'copper', host, vertices=20)
add_box('CHIPSET_HEATSINK', (3.77, -0.03, -0.32), (0.52, 0.16, 0.52), 'graphite', host, 0.08, rotation=(0, 0, math.radians(8)))
for index in range(7):
    add_box(f'CHIPSET_FIN_{index:02d}', (3.58 + index * 0.065, -0.13, -0.32), (0.025, 0.10, 0.38), 'silver', host, 0.004, rotation=(0, 0, math.radians(8)))

# GPU with dual animated fans, fins, backplate, and power connector.
add_box('GPU_BODY', (3.22, -0.08, -0.72), (1.72, 0.38, 0.48), 'graphite', host, 0.07, semantic='gpu')
add_box('GPU_BACKPLATE', (3.22, 0.14, -0.72), (1.60, 0.055, 0.39), 'silver', host, 0.025)
add_box('GPU_PCIE_EDGE', (3.20, -0.29, -0.95), (1.28, 0.035, 0.075), 'copper', host, 0.008)
for index in range(13):
    add_box(f'GPU_FIN_{index:02d}', (2.63 + index * 0.098, -0.28, -0.72), (0.042, 0.20, 0.34), 'silver' if index % 2 else 'mid', host, 0.005)
for index, x in enumerate((2.82, 3.62)):
    add_fan(f'GPU_FAN_{index:02d}', (x, -0.34, -0.72), 0.28, host, rotations=18 + index * 2, depth=0.07)
add_box('GPU_POWER_SOCKET', (4.02, -0.09, -0.47), (0.22, 0.22, 0.13), 'ink', host, 0.025)
for pin in range(8):
    add_box(f'GPU_POWER_PIN_{pin:02d}', (3.95 + (pin % 4) * 0.045, -0.215, -0.49 + (pin // 4) * 0.055), (0.024, 0.018, 0.024), 'copper', host, 0.003)

# PSU and rear I/O details.
add_box('POWER_SUPPLY', (3.58, 0.28, 1.08), (0.96, 0.64, 0.58), 'graphite', host, 0.065, semantic='power')
add_torus('PSU_GRILLE_OUTER', (3.58, -0.055, 1.08), 0.225, 0.018, 'silver', host, major_segments=44)
add_torus('PSU_GRILLE_INNER', (3.58, -0.060, 1.08), 0.145, 0.014, 'mid', host, major_segments=36)
psu_fan = add_fan('PSU_FAN', (3.58, -0.035, 1.08), 0.20, host, rotations=11, depth=0.045)
for index in range(6):
    angle = math.tau * index / 6
    add_box(f'PSU_GRILLE_SPOKE_{index:02d}', (3.58, -0.075, 1.08), (0.43, 0.018, 0.018), 'mid', host, 0.004, rotation=(0, angle, 0))
add_text('PSU_LABEL', '750W // 80+', (3.20, -0.075, 0.79), 0.07, 'paper', host, 0.002, 'power_label')
for row in range(2):
    for column in range(3):
        add_box(f'PSU_MODULAR_PORT_{row}_{column}', (3.28 + column * 0.22, 0.625, 0.98 + row * 0.19), (0.14, 0.025, 0.11), 'ink', host, 0.015)
add_box('REAR_IO_SHIELD', (2.31, 0.02, 0.88), (0.18, 0.18, 0.92), 'silver', host, 0.025)
for index in range(6):
    z = 0.55 + index * 0.14
    add_box(f'REAR_IO_PORT_{index:02d}', (2.30, -0.09, z), (0.11, 0.028, 0.075), 'ink' if index % 2 else 'graphite', host, 0.008)

# Internal power/data routing with connector housings and cable combs.
internal_routes = [
    ('ATX_POWER_CABLE', [(3.66, 0.60, 1.02), (4.02, 0.44, 0.80), (4.02, 0.10, 0.38), (3.92, -0.02, 0.16)], 0.034, 'copper'),
    ('GPU_POWER_CABLE', [(3.48, 0.58, 1.00), (4.18, 0.36, 0.58), (4.18, 0.08, -0.20), (4.02, -0.08, -0.47)], 0.032, 'silver'),
    ('SATA_POWER_CABLE', [(3.42, 0.58, 0.96), (3.98, 0.48, 0.52), (3.82, 0.22, -0.86)], 0.026, 'graphite'),
]
for name, points, radius, mat in internal_routes:
    add_cable(name, points, radius, mat, host, 'internal_cable')
for index, z in enumerate((0.52, 0.15, -0.20)):
    add_box(f'CABLE_COMB_{index:02d}', (4.08, 0.18, z), (0.28, 0.10, 0.075), 'mid', host, 0.018)

# Keyboard with differentiated keycaps, encoder, underside feet, and animated typing cluster.
keyboard = add_empty('INPUT_GROUP', (0, 0, 0), world_root, 'input', 'INPUT 01')
add_box('KEYBOARD_UNDERSIDE', (0.10, -1.40, -1.25), (3.66, 1.12, 0.18), 'rubber', keyboard, 0.09, rotation=(math.radians(-3), 0, 0))
add_box('KEYBOARD_TOP_PLATE', (0.10, -1.43, -1.17), (3.52, 1.02, 0.08), 'silver', keyboard, 0.055, rotation=(math.radians(-3), 0, 0), semantic='keyboard')
animated_keys = []
for row in range(4):
    count = (14, 14, 13, 10)[row]
    x_start = (-1.42, -1.38, -1.28, -0.88)[row]
    for column in range(count):
        x = x_start + column * 0.225
        y = -1.72 + row * 0.215
        z = -1.095 + row * 0.010
        width = 0.185
        if row == 3 and column == 4:
            width = 0.72
            x += 0.23
        key = add_box(f'KEY_{row:02d}_{column:02d}', (x, y, z), (width, 0.165, 0.062), 'ink' if (row + column) % 7 else 'mid', keyboard, 0.022)
        if (row, column) in {(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (2, 5), (3, 4)}:
            animated_keys.append(key)
for index, key in enumerate(animated_keys):
    base_z = key.location.z
    for frame, offset in [(1, 0), (44 + index * 17, 0), (47 + index * 17, -0.035), (52 + index * 17, 0), (END, 0)]:
        key.location.z = base_z + offset
        key.keyframe_insert('location', frame=min(frame, END), group='KEYBOARD_ACTIVITY')
    move_action_to_track(key, 'KEYBOARD_ACTIVITY')
add_cylinder('KEYBOARD_ENCODER', (1.58, -1.66, -1.04), 0.11, 0.11, 'silver', keyboard, rotation=(0, 0, 0), vertices=40)
for index in range(20):
    angle = math.tau * index / 20
    add_box(f'ENCODER_KNURL_{index:02d}', (1.58 + math.cos(angle) * 0.105, -1.66 + math.sin(angle) * 0.105, -0.99), (0.012, 0.025, 0.08), 'ink', keyboard, 0.003, rotation=(0, 0, angle))
add_box('KEYBOARD_USB_PORT', (-1.66, -1.42, -1.16), (0.10, 0.045, 0.055), 'ink', keyboard, 0.010)

# External SSD with machined ribs, connector, cable, and authored activity.
storage = add_empty('STORAGE_GROUP', (0, 0, 0), world_root, 'storage', 'STORAGE 01')
add_box('EXTERNAL_SSD', (-1.62, -1.10, -1.03), (0.82, 0.55, 0.15), 'silver', storage, 0.075, rotation=(0, 0, math.radians(-8)), semantic='storage')
for index in range(9):
    x = -1.94 + index * 0.08
    add_box(f'SSD_RIB_{index:02d}', (x, -1.39, -1.03), (0.035, 0.022, 0.09), 'graphite' if index % 2 else 'mid', storage, 0.006, rotation=(0, 0, math.radians(-8)))
add_box('SSD_USB_C_PORT', (-1.20, -1.13, -1.03), (0.055, 0.16, 0.065), 'ink', storage, 0.016, rotation=(0, 0, math.radians(-8)))
add_text('SSD_LABEL', 'NVME // 2TB', (-1.94, -1.405, -0.97), 0.055, 'ink', storage, 0.002, 'storage_label')
ssd_led = add_box('SSD_ACTIVITY_LED', (-1.28, -1.405, -0.96), (0.055, 0.014, 0.035), 'signal', storage, 0.005, semantic='activity_led')
animate_pulse(ssd_led, [(1, 0.25), (62, 0.25), (66, 1.4), (70, 0.25), (116, 0.25), (120, 1.4), (126, 0.25), (188, 0.25), (192, 1.4), (198, 0.25), (END, 0.25)], 'STORAGE_ACTIVITY')
ssd_route = [(-1.20, -1.13, -1.03), (-0.95, -1.35, -1.18), (-0.55, -1.52, -1.28), (-0.20, -1.58, -1.25)]
add_cable('SSD_USB_CABLE', ssd_route, 0.028, 'graphite', world_root, 'storage_link')

# Managed network switch with recessed ports, visible contacts, labels, LEDs, and traffic pulses.
network = add_empty('NETWORK_GROUP', (0, 0, 0), world_root, 'network', 'ETH 01')
add_box('NETWORK_SWITCH', (3.15, -1.22, -1.12), (2.42, 0.72, 0.38), 'graphite', network, 0.075, semantic='network_switch')
add_box('SWITCH_FACEPLATE', (3.15, -1.59, -1.12), (2.28, 0.035, 0.28), 'silver', network, 0.018)
network_leds = []
for index in range(8):
    x = 2.35 + index * 0.23
    add_box(f'ETH_PORT_FRAME_{index:02d}', (x, -1.615, -1.12), (0.18, 0.035, 0.15), 'ink', network, 0.014, semantic='ethernet_port')
    add_box(f'ETH_PORT_CAVITY_{index:02d}', (x, -1.637, -1.12), (0.13, 0.018, 0.095), 'graphite', network, 0.007)
    for pin in range(4):
        add_box(f'ETH_{index:02d}_PIN_{pin:02d}', (x - 0.045 + pin * 0.03, -1.65, -1.145), (0.014, 0.008, 0.045), 'copper', network, 0.002)
    led = add_box(f'ETH_LED_{index:02d}', (x, -1.653, -1.015), (0.035, 0.008, 0.028), 'signal', network, 0.004, semantic='network_led')
    network_leds.append(led)
    add_text(f'ETH_LABEL_{index:02d}', f'{index + 1}', (x - 0.025, -1.66, -0.965), 0.038, 'ink', network, 0.001)
for index, led in enumerate(network_leds):
    start = 22 + index * 11
    animate_pulse(led, [(1, 0.2), (start, 0.2), (start + 2, 1.25), (start + 6, 0.2), (start + 68, 0.2), (start + 71, 1.25), (start + 76, 0.2), (END, 0.2)], 'NETWORK_TRAFFIC')
add_text('SWITCH_LABEL', '8P MANAGED // 2.5G', (2.18, -1.662, -1.28), 0.055, 'paper', network, 0.002, 'network_label')
add_box('SWITCH_POWER', (4.08, -1.65, -1.22), (0.06, 0.012, 0.06), 'signal', network, 0.008)
for x in (2.03, 4.27):
    add_cylinder(f'SWITCH_RACK_EAR_{x:.2f}', (x, -1.60, -1.12), 0.06, 0.04, 'ink', network, vertices=24)

# Routed physical connections with modeled connector housings and animated signal carriers.
display_route = [(1.45, 0.22, -0.92), (1.72, -0.10, -1.12), (2.18, -0.40, -0.88), (2.58, -0.62, -0.60)]
host_switch_route = [(3.85, 0.05, -0.56), (4.32, -0.45, -0.78), (4.15, -0.95, -1.04), (3.98, -1.42, -1.10)]
foreground_route = [(4.02, -1.56, -1.08), (3.38, -1.72, -0.88), (2.52, -1.62, -0.86), (1.48, -1.48, -0.98), (0.72, -1.60, -1.36)]
link_out_route = [(2.45, -1.60, -1.10), (3.38, -1.82, -1.32), (4.42, -1.92, -1.62), (5.62, -2.05, -2.12)]
add_cable('DISPLAY_LINK', display_route, 0.038, 'silver', world_root, 'display_link')
add_cable('HOST_TO_SWITCH', host_switch_route, 0.045, 'copper', world_root, 'network_link')
add_cable('FOREGROUND_CABLE', foreground_route, 0.053, 'paper', world_root, 'foreground_crossing')
add_cable('LINK_OUT', link_out_route, 0.048, 'silver', world_root, 'link_out')
add_box('DISPLAY_CONNECTOR', (2.58, -0.62, -0.60), (0.22, 0.15, 0.12), 'graphite', world_root, 0.025, rotation=(0, 0, math.radians(-18)), semantic='connector')
add_box('RJ45_CONNECTOR', (3.98, -1.46, -1.10), (0.18, 0.18, 0.13), 'paper', world_root, 0.025, semantic='connector')
for index, (route, start, duration) in enumerate([
    (host_switch_route, 18, 58),
    (host_switch_route, 96, 58),
    (foreground_route, 152, 72),
    (link_out_route, 206, 70),
]):
    pulse = add_sphere(f'NETWORK_SIGNAL_{index:02d}', route[0], 0.070 if index < 2 else 0.060, 'signal', world_root, 20, 10, 'signal_packet')
    animate_signal(pulse, route, start, min(duration, END - start - 1))

# Sparse work-surface engineering details that anchor the equipment without creating a solid slab.
for x in (-1.80, -0.65, 0.50, 1.65, 2.80, 3.95):
    add_box(f'DESK_RAIL_{x:.2f}', (x, -0.25, -1.49), (0.055, 3.05, 0.055), 'graphite', world_root, 0.012, semantic='work_surface_rail')
for index in range(16):
    add_cylinder(f'DESK_FASTENER_{index:02d}', (-1.68 + (index % 8) * 0.78, -1.98 + (index // 8) * 2.55, -1.46), 0.030, 0.024, 'mid', world_root, rotation=(0, 0, 0), vertices=20)

# Runtime camera, target, portrait, text-safe, and instrumentation anchors.
anchors = {
    'IDENTITY': {
        'camera': (0.0, -10.8, 1.45), 'target': (0.78, 0.0, 0.05), 'portrait': (0.50, -1.15, -0.05),
    },
    'POSITION': {
        'camera': (3.25, -9.55, 1.05), 'target': (2.00, 0.0, -0.08), 'portrait': (2.55, -1.15, -0.18),
    },
    'CONTACT': {
        'camera': (4.10, -8.75, -0.45), 'target': (2.65, -0.50, -0.95), 'portrait': (3.45, -1.15, -0.52),
    },
}
for state, values in anchors.items():
    add_empty(f'CAM_{state}', values['camera'], world_root, 'camera_anchor')
    add_empty(f'TARGET_{state}', values['target'], world_root, 'target_anchor')
    add_empty(f'PORTRAIT_{state}', values['portrait'], world_root, 'portrait_anchor')

for index, (name, location, label) in enumerate([
    ('TRACK_DISPLAY', (1.82, -0.22, 1.70), 'DISPLAY 01'),
    ('TRACK_HOST', (4.18, -0.18, 1.48), 'HOST 01'),
    ('TRACK_INPUT', (1.48, -1.72, -1.03), 'INPUT 01'),
    ('TRACK_ETH', (4.02, -1.60, -1.10), 'ETH 01'),
]):
    anchor = add_empty(name, location, world_root, 'tracker', label)
    anchor['tracker_index'] = index

for state, location in {
    'IDENTITY': (-1.60, -0.30, 1.35),
    'POSITION': (-0.30, -0.20, 0.55),
    'CONTACT': (-1.30, -1.20, -0.75),
}.items():
    add_empty(f'TEXT_SAFE_{state}', location, world_root, 'text_safe_anchor')


def has_animated_ancestor(obj):
    current = obj
    while current:
        animation = current.animation_data
        if animation and (animation.action or len(animation.nla_tracks)):
            return True
        current = current.parent
    return False


def batch_static_meshes():
    groups = {}
    for obj in export_objects:
        if obj.type != 'MESH' or obj.keys() or has_animated_ancestor(obj):
            continue
        if len(obj.data.materials) != 1 or not obj.data.materials[0]:
            continue
        material_name = obj.data.materials[0].name
        groups.setdefault(material_name, []).append(obj)

    bpy.context.view_layer.update()
    depsgraph = bpy.context.evaluated_depsgraph_get()
    batch_count = 0
    source_count = 0
    for material_name in sorted(groups):
        sources = sorted(groups[material_name], key=lambda item: item.name)
        if len(sources) < 2:
            continue
        merged = bmesh.new()
        for source in sources:
            evaluated = source.evaluated_get(depsgraph)
            temporary = evaluated.to_mesh()
            temporary.transform(source.matrix_world)
            merged.from_mesh(temporary)
            evaluated.to_mesh_clear()

        mesh = bpy.data.meshes.new(f'STATIC_BATCH_{material_name}')
        merged.to_mesh(mesh)
        merged.free()
        mesh.materials.append(bpy.data.materials[material_name])
        batch = bpy.data.objects.new(f'STATIC_BATCH_{material_name}', mesh)
        bpy.context.collection.objects.link(batch)
        register(batch, world_root, 'static_batch')
        batch['source_count'] = len(sources)
        batch_count += 1
        source_count += len(sources)

        for source in sources:
            export_objects.remove(source)
            bpy.data.objects.remove(source, do_unlink=True)

    world_root['static_batches'] = batch_count
    world_root['batched_sources'] = source_count


batch_static_meshes()

# Export only authored world objects and metadata. Diagnostic camera and lights stay local.
bpy.ops.object.select_all(action='DESELECT')
for obj in export_objects:
    obj.select_set(True)
scene.frame_set(1)
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


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


camera_data = bpy.data.cameras.new('DiagnosticCamera')
camera = bpy.data.objects.new('DiagnosticCamera', camera_data)
bpy.context.collection.objects.link(camera)
scene.camera = camera
camera.data.lens = 52

key_data = bpy.data.lights.new('DiagnosticKey', 'AREA')
key_data.energy = 1100
key_data.shape = 'DISK'
key_data.size = 5.0
key = bpy.data.objects.new('DiagnosticKey', key_data)
bpy.context.collection.objects.link(key)
key.location = (-2.5, -5.5, 6.0)
look_at(key, (1.0, 0.0, 0.0))

fill_data = bpy.data.lights.new('DiagnosticFill', 'AREA')
fill_data.energy = 720
fill_data.size = 4.0
fill = bpy.data.objects.new('DiagnosticFill', fill_data)
bpy.context.collection.objects.link(fill)
fill.location = (5.5, -2.5, 2.5)
look_at(fill, (2.5, 0.0, 0.0))

rim_data = bpy.data.lights.new('DiagnosticRim', 'AREA')
rim_data.energy = 860
rim_data.size = 3.0
rim = bpy.data.objects.new('DiagnosticRim', rim_data)
bpy.context.collection.objects.link(rim)
rim.location = (1.0, 3.5, 4.5)
look_at(rim, (1.8, 0.2, 0.0))

bpy.ops.wm.save_as_mainfile(filepath=str(WORKDIR / 'workstation-world.blend'))
if os.environ.get('WORKSTATION_SKIP_DIAGNOSTICS') != '1':
    diagnostic_views = dict(anchors)
    diagnostic_views['OBLIQUE'] = {
        'camera': (7.2, -8.4, 3.8),
        'target': (1.45, 0.0, 0.0),
        'portrait': (0, 0, 0),
    }
    for state, values in diagnostic_views.items():
        camera.location = values['camera']
        look_at(camera, values['target'])
        scene.frame_set(154 if state == 'OBLIQUE' else 208)
        scene.render.filepath = str(WORKDIR / f'workstation-{state.lower()}.png')
        scene.render.film_transparent = False
        bpy.ops.render.render(write_still=True)

print(f'Exported {OUT}')
print(f'Diagnostics {WORKDIR}')
print(f'Export objects {len(export_objects)}')
