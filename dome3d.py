#!/usr/bin/env python3
"""
Geodesic Dome 3D Model Generator
Based on "Geodesic Domes" by Tom Davis, Berkeley Math Circle (2004)

Generates: JSON (Three.js), STL (3D printing/CAD), OBJ (universal)

Usage:
  python dome3d.py -f 2 -r 15 -o models/2v/dome_2v
"""

import math, json, struct, os, sys, argparse, zipfile
from collections import defaultdict

# ============================================================
# Vector math (pure Python, no numpy)
# ============================================================

def v3(x=0.0, y=0.0, z=0.0):
    return (x, y, z)

def vadd(a, b):
    return (a[0]+b[0], a[1]+b[1], a[2]+b[2])

def vsub(a, b):
    return (a[0]-b[0], a[1]-b[1], a[2]-b[2])

def vscale(v, s):
    return (v[0]*s, v[1]*s, v[2]*s)

def vdot(a, b):
    return a[0]*b[0] + a[1]*b[1] + a[2]*b[2]

def vcross(a, b):
    return (a[1]*b[2] - a[2]*b[1],
            a[2]*b[0] - a[0]*b[2],
            a[0]*b[1] - a[1]*b[0])

def vlen(v):
    return math.sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2])

def vnorm(v):
    l = vlen(v)
    if l < 1e-15:
        return (0.0, 0.0, 0.0)
    return (v[0]/l, v[1]/l, v[2]/l)

def vdist(a, b):
    return vlen(vsub(a, b))

def vlerp(a, b, t):
    return (a[0] + (b[0]-a[0])*t, a[1] + (b[1]-a[1])*t, a[2] + (b[2]-a[2])*t)

# ============================================================
# Icosahedron (Berkeley paper: Tom Davis, 2004)
# ============================================================

PHI = (1 + math.sqrt(5)) / 2  # golden ratio ~1.618

ICOSA_RAW = [
    (0, 1, PHI), (0, -1, PHI), (0, -1, -PHI), (0, 1, -PHI),
    (PHI, 0, 1), (-PHI, 0, 1), (-PHI, 0, -1), (PHI, 0, -1),
    (1, PHI, 0), (-1, PHI, 0), (-1, -PHI, 0), (1, -PHI, 0),
]
# Rotate so vertex A (0, 1, φ) maps to north pole (0, 0, 1).
# Rotation around x-axis by angle θ where tan(θ) = 1/φ
_cos = PHI / math.sqrt(1 + PHI * PHI)
_sin = 1.0 / math.sqrt(1 + PHI * PHI)

def _rotate_north(v):
    x, y, z = v
    return (x, y * _cos - z * _sin, y * _sin + z * _cos)

ICOSA_VERTS = [vnorm(_rotate_north(v)) for v in ICOSA_RAW]

# 20 faces from the paper (vertex labels A=0 through L=11)
ICOSA_FACES = [
    [0, 8, 9], [0, 9, 5], [0, 5, 1], [0, 1, 4], [0, 4, 8],
    [1, 5, 10], [1, 10, 11], [1, 11, 4],
    [2, 3, 7], [2, 7, 11],
    [11, 10, 2], [10, 6, 2], [6, 3, 2],
    [3, 6, 9], [3, 9, 8], [3, 8, 7],
    [4, 11, 7], [4, 7, 8],
    [5, 9, 6], [5, 6, 10],
]

# Chord factors from Berkeley paper tables (radius = 1.0)
CHORD_FACTORS = {
    2: {'A': 0.546533057825, 'B': 0.618033988750},
    3: {'A': 0.348615488820, 'B': 0.403548212335, 'C': 0.412411489310},
    4: {'A': 0.253184595784, 'B': 0.294530833739, 'C': 0.295241808844,
         'D': 0.298588133655, 'E': 0.312868930080, 'F': 0.324919696233},
}

STRUT_COLORS = {
    'A': (0xe7, 0x4c, 0x3c),  # red
    'B': (0x34, 0x98, 0xdb),  # blue
    'C': (0x2e, 0xcc, 0x71),  # green
    'D': (0xf3, 0x9c, 0x12),  # orange
    'E': (0x9b, 0x59, 0xb6),  # purple
    'F': (0x1a, 0xbc, 0x9c),  # teal
    'G': (0xe6, 0x7e, 0x22),  # rust
    'H': (0x95, 0xa5, 0xa6),  # grey
}

# ============================================================
# Core geometry: subdivide icosahedron -> geodesic sphere -> dome
# ============================================================

def subdivide_face(v0, v1, v2, freq):
    vertices, point_map, idx = [], {}, 0
    for i in range(freq + 1):
        for j in range(freq + 1 - i):
            k = freq - i - j
            u, v, w = i / freq, j / freq, k / freq
            pt = vnorm((
                u * v0[0] + v * v1[0] + w * v2[0],
                u * v0[1] + v * v1[1] + w * v2[1],
                u * v0[2] + v * v1[2] + w * v2[2],
            ))
            point_map[(i, j)] = (idx, pt)
            vertices.append(pt)
            idx += 1

    faces = []
    for i in range(freq):
        for j in range(freq - i):
            a = point_map[(i, j)][0]
            b = point_map[(i + 1, j)][0]
            c = point_map[(i, j + 1)][0]
            faces.append([a, b, c])
            if i + j < freq - 1:
                d = point_map[(i + 1, j)][0]
                e = point_map[(i + 1, j + 1)][0]
                f_ = point_map[(i, j + 1)][0]
                faces.append([d, e, f_])
    return vertices, faces


def deduplicate_vertices(all_verts, all_faces):
    seen, unique, remap = {}, [], {}
    for i, v in enumerate(all_verts):
        key = (round(v[0], 6), round(v[1], 6), round(v[2], 6))
        if key not in seen:
            seen[key] = len(unique)
            unique.append(v)
        remap[i] = seen[key]
    remapped = [[remap[f] for f in face] for face in all_faces]
    # Remove duplicate faces (triangles along shared icosahedron edges)
    face_set = set()
    deduped = []
    for f in remapped:
        key = tuple(sorted(f))
        if key not in face_set:
            face_set.add(key)
            deduped.append(f)
    return unique, deduped


def build_sphere(freq):
    all_v, all_f = [], []
    for face in ICOSA_FACES:
        v0, v1, v2 = ICOSA_VERTS[face[0]], ICOSA_VERTS[face[1]], ICOSA_VERTS[face[2]]
        sv, sf = subdivide_face(v0, v1, v2, freq)
        offset = len(all_v)
        all_v.extend(sv)
        all_f.extend([[fi + offset for fi in f] for f in sf])
    return deduplicate_vertices(all_v, all_f)


def clip_hemisphere(verts, faces, epsilon=-0.005):
    keep, remap = [], {}
    for i, v in enumerate(verts):
        if v[2] >= epsilon:
            remap[i] = len(keep)
            keep.append(v)
        else:
            remap[i] = None
    new_faces = []
    for f in faces:
        idx = [remap[fi] for fi in f]
        if all(x is not None for x in idx):
            new_faces.append(idx)
    return keep, new_faces


def extract_edges(faces):
    edges = set()
    for f in faces:
        for a, b in [(0, 1), (1, 2), (2, 0)]:
            u, v = f[a], f[b]
            edges.add((min(u, v), max(u, v)))
    return sorted(edges)


def group_struts(verts, edges, radius, freq):
    ref = CHORD_FACTORS.get(freq, {})
    if not ref:
        lengths = sorted(set(vdist(verts[a], verts[b]) for a, b in edges))
        groups, labels = [], list('ABCDEFGH')
        for dist in lengths:
            gdist = round(dist, 4)
            found = False
            for j, g in enumerate(groups):
                if abs(g[0] - gdist) < radius * 0.002:
                    found = True
                    g[1].append(dist)
                    break
            if not found:
                groups.append([gdist, [dist], labels[len(groups)] if len(groups) < len(labels) else '?'])
        ref_factors = {g[2]: g[0] for g in groups}
    else:
        ref_factors = {k: v * radius for k, v in ref.items()}

    type_edges = defaultdict(list)
    edge_list = [(vdist(verts[a], verts[b]), (a, b)) for a, b in edges]
    for dist, edge in edge_list:
        best_label, best_diff = None, float('inf')
        for label, ref_len in ref_factors.items():
            diff = abs(dist - ref_len)
            if diff < best_diff:
                best_diff = diff
                best_label = label
        type_edges[best_label].append(edge)

    labels = sorted(type_edges.keys())
    result = []
    for label in labels:
        struts = type_edges[label]
        avg_len = sum(vdist(verts[a], verts[b]) for a, b in struts) / len(struts)
        result.append((label, avg_len, struts))
    return result


def scale_verts(verts, radius):
    return [vscale(v, radius) for v in verts]


# ============================================================
# JSON export (for Three.js preview)
# ============================================================

def export_json(verts, faces, strut_groups, edges, radius, freq, output_path):
    hub_data = defaultdict(list)
    for label, dist, struts in strut_groups:
        for a, b in struts:
            hub_data[a].append(b)
            hub_data[b].append(a)

    hub_connections = {}
    for vi, connected in hub_data.items():
        pos = verts[vi]
        normal = vnorm(pos)
        hub_connections[vi] = {
            'position': list(pos),
            'normal': list(normal),
            'valence': len(connected),
            'connected': connected,
        }

    data = {
        'radius': radius,
        'frequency': freq,
        'vertex_count': len(verts),
        'edge_count': len(edges),
        'face_count': len(faces),
        'strut_type_count': len(strut_groups),
        'vertices': [[round(v[0], 6), round(v[1], 6), round(v[2], 6)] for v in verts],
        'faces': faces,
        'edges': [list(e) for e in edges],
        'strut_groups': [
            {
                'type': label,
                'length': round(dist, 6),
                'count': len(struts),
                'edges': [list(e) for e in struts],
                'color': [c / 255 for c in STRUT_COLORS.get(label, (0.8, 0.8, 0.8))],
            }
            for label, dist, struts in strut_groups
        ],
        'hubs': hub_connections,
    }
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w') as f:
        json.dump(data, f)
    return data


# ============================================================
# STL export (binary)
# ============================================================

def _stl_triangle(normal, v0, v1, v2):
    return struct.pack('<3f3f3f3fH',
        normal[0], normal[1], normal[2],
        v0[0], v0[1], v0[2],
        v1[0], v1[1], v1[2],
        v2[0], v2[1], v2[2], 0)


def _stl_cylinder(start, end, radius, segments=12):
    direction = vsub(end, start)
    height = vlen(direction)
    if height < 1e-10:
        return b''
    d = vnorm(direction)
    up = (0, 1, 0) if abs(d[1]) < 0.99 else (1, 0, 0)
    right = vnorm(vcross(up, d))
    up = vcross(d, right)

    ring0, ring1 = [], []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        rx = math.cos(angle) * right[0] + math.sin(angle) * up[0]
        ry = math.cos(angle) * right[1] + math.sin(angle) * up[1]
        rz = math.cos(angle) * right[2] + math.sin(angle) * up[2]
        ring0.append((start[0] + rx * radius, start[1] + ry * radius, start[2] + rz * radius))
        ring1.append((end[0] + rx * radius, end[1] + ry * radius, end[2] + rz * radius))

    tris = b''
    for i in range(segments):
        j = (i + 1) % segments
        a0, a1 = ring0[i], ring1[i]
        b0, b1 = ring0[j], ring1[j]
        n0 = vnorm(vsub(a0, start))
        n1 = vnorm(vsub(a1, end))
        tris += _stl_triangle(n0, a0, b0, a1)
        tris += _stl_triangle(n1, a1, b0, b1)
        c = vlerp(start, end, 0)
        nc = vnorm(vsub(c, start))
        tris += _stl_triangle((-nc[0], -nc[1], -nc[2]), ring0[j], ring0[i], start)
        tris += _stl_triangle((d[0], d[1], d[2]), ring1[i], ring1[j], end)
    return tris


def _stl_disc(center, normal, radius, thickness=0.05, segments=16):
    d = vnorm(normal)
    up = (0, 1, 0) if abs(d[1]) < 0.99 else (1, 0, 0)
    right = vnorm(vcross(up, d))
    up = vcross(d, right)
    half_thick = thickness / 2
    offset = vscale(d, -half_thick)

    ring1, ring2 = [], []
    for i in range(segments):
        angle = 2 * math.pi * i / segments
        rx = math.cos(angle) * right[0] + math.sin(angle) * up[0]
        ry = math.cos(angle) * right[1] + math.sin(angle) * up[1]
        rz = math.cos(angle) * right[2] + math.sin(angle) * up[2]
        ring1.append(vadd(center, (rx * radius + offset[0], ry * radius + offset[1], rz * radius + offset[2])))
        ring2.append(vadd(center, (rx * radius - offset[0], ry * radius - offset[1], rz * radius - offset[2])))

    tris = b''
    for i in range(segments):
        j = (i + 1) % segments
        nf = (-d[0], -d[1], -d[2])
        nb = d
        tris += _stl_triangle(nf, ring2[j], ring2[i], center)
        tris += _stl_triangle(nf, ring1[i], ring1[j], center)
        a0, a1 = ring1[i], ring2[i]
        b0, b1 = ring1[j], ring2[j]
        ns = vnorm(vcross(vsub(a1, a0), vsub(b0, a0)))
        tris += _stl_triangle(ns, a0, b0, a1)
        tris += _stl_triangle(ns, a1, b0, b1)
    return tris


def export_stl(verts, strut_groups, radius, output_path, hub_thickness=0.078125, strut_radius=None):
    if strut_radius is None:
        strut_radius = radius * 0.008

    all_tris = b''
    for label, dist, struts in strut_groups:
        for a, b in struts:
            all_tris += _stl_cylinder(verts[a], verts[b], strut_radius, 10)

    hub_data = defaultdict(list)
    for label, dist, struts in strut_groups:
        for a, b in struts:
            hub_data[a].append(b)
            hub_data[b].append(a)

    hub_r = strut_radius * 2.5
    for vi, connected in hub_data.items():
        pos = verts[vi]
        normal = vnorm(pos)
        all_tris += _stl_disc(pos, normal, hub_r, hub_thickness, 12)

    n_tris = len(all_tris) // 50
    header = b'Geodesic Dome STL' + b'\x00' * (80 - 18)
    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'wb') as f:
        f.write(header)
        f.write(struct.pack('<I', n_tris))
        f.write(all_tris)
    return n_tris


# ============================================================
# OBJ export
# ============================================================

def export_obj(verts, strut_groups, radius, output_path, strut_radius=None):
    if strut_radius is None:
        strut_radius = radius * 0.008

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(f'# Geodesic Dome OBJ\n')
        vi = 1
        for label, dist, struts in strut_groups:
            f.write(f'o strut_{label}\n')
            for a, b in struts:
                f.write(f'v {verts[a][0]} {verts[a][1]} {verts[a][2]}\n')
                f.write(f'v {verts[b][0]} {verts[b][1]} {verts[b][2]}\n')
                f.write(f'l {vi} {vi+1}\n')
                vi += 2


# ============================================================
# Main CLI
# ============================================================

def main():
    parser = argparse.ArgumentParser(description='Generate geodesic dome 3D models')
    parser.add_argument('-f', '--frequency', type=int, required=True, help='Dome frequency (2, 3, 4, etc.)')
    parser.add_argument('-r', '--radius', type=float, default=15.0, help='Dome radius in feet (default: 15)')
    parser.add_argument('-o', '--output', type=str, default='output/dome', help='Output path prefix')
    parser.add_argument('--no-stl', action='store_true', help='Skip STL generation')
    parser.add_argument('--no-obj', action='store_true', help='Skip OBJ generation')
    parser.add_argument('--no-json', action='store_true', help='Skip JSON generation')
    args = parser.parse_args()

    freq = args.frequency
    radius = args.radius

    print(f'Building {freq}V geodesic dome (radius={radius} ft)...')

    verts, faces = build_sphere(freq)
    verts, faces = clip_hemisphere(verts, faces)
    verts = scale_verts(verts, radius)

    edges = extract_edges(faces)
    strut_groups = group_struts(verts, edges, radius, freq)

    print(f'  Vertices: {len(verts)}')
    print(f'  Struts:   {len(edges)}')
    print(f'  Faces:    {len(faces)}')
    print(f'  Strut types: {len(strut_groups)}')
    for label, dist, struts in strut_groups:
        print(f'    Type {label}: {len(struts)} struts, {dist:.4f} ft')

    base = args.output
    if not args.no_json:
        export_json(verts, faces, strut_groups, edges, radius, freq, f'{base}.json')
        print(f'  Wrote {base}.json')
    if not args.no_stl:
        n = export_stl(verts, strut_groups, radius, f'{base}_full.stl')
        print(f'  Wrote {base}_full.stl ({n} triangles)')
    if not args.no_obj:
        export_obj(verts, strut_groups, radius, f'{base}_full.obj')
        print(f'  Wrote {base}_full.obj')

    # Individual strut STLs
    if not args.no_stl:
        for label, dist, struts in strut_groups:
            strut_verts = verts
            single_group = [(label, dist, struts)]
            path = f'{base}_strut_{label}.stl'
            n = export_stl(strut_verts, single_group, radius, path)
            print(f'  Wrote {path} ({n} triangles)')

    print('Done.')


if __name__ == '__main__':
    main()
