#!/usr/bin/env python3
"""
Hub DXF Template Generator
Generates 2D DXF files for geodesic dome plywood hub connector plates.
Classifies hubs by valence (number of connecting struts) and generates
one template per valence type with bolt holes at correct angles.

Usage:
  python hub_dxf.py -f 2 -o models/2v/hub
"""

import math, os, argparse
from collections import defaultdict
from dome3d import *
import dome3d

def hub_angles(verts, edges, radius, freq):
    strut_groups = group_struts(verts, edges, radius, freq)
    hub_struts = defaultdict(list)
    for label, dist, struts in strut_groups:
        for a, b in struts:
            hub_struts[a].append(b)
            hub_struts[b].append(a)

    hubs_by_valence = defaultdict(list)
    for vi, connected in hub_struts.items():
        pos = verts[vi]
        normal = vnorm(pos)
        angles = []
        for ci in connected:
            direction = vnorm(vsub(verts[ci], pos))
            tangent = vnorm(vsub(direction, vscale(normal, vdot(direction, normal))))
            if vlen(tangent) < 1e-6:
                continue
            ref_x = vnorm(vcross(normal, (0, 0, 1) if abs(vdot(normal, (0, 0, 1))) < 0.99 else (1, 0, 0)))
            ref_y = vcross(normal, ref_x)
            x = vdot(tangent, ref_x)
            y = vdot(tangent, ref_y)
            angle = math.atan2(y, x)
            angles.append(angle)
        angles.sort()
        valence = len(angles)
        hubs_by_valence[valence].append(angles)

    return dict(hubs_by_valence)

def write_dxf(filepath, hub_type_name, valence, angles, plate_radius=3.0, hole_offset=2.0, hole_radius=0.25, center_hole_radius=0.125):
    os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
    with open(filepath, 'w') as f:
        f.write('0\nSECTION\n2\nENTITIES\n')
        # Outer plate circle
        f.write(f'0\nCIRCLE\n8\n0\n10\n0.0\n20\n0.0\n40\n{plate_radius}\n')
        # Hub label
        # Bolt holes + approach line
        for i, angle in enumerate(angles):
            bx = hole_offset * math.cos(angle)
            by = hole_offset * math.sin(angle)
            f.write(f'0\nCIRCLE\n8\n0\n10\n{bx:.4f}\n20\n{by:.4f}\n40\n{hole_radius}\n')
            # Approach line from center to bolt hole
            f.write(f'0\nLINE\n8\n0\n10\n0.0\n20\n0.0\n11\n{bx:.4f}\n21\n{by:.4f}\n')
        # Center alignment hole
        f.write(f'0\nCIRCLE\n8\n0\n10\n0.0\n20\n0.0\n40\n{center_hole_radius}\n')
        # Label text (using MTEXT or just a note)
        f.write('0\nTEXT\n8\n0\n10\n0.0\n20\n')
        f.write(f'{plate_radius + 0.5}\n40\n0.2\n1\n')
        f.write(f'{valence}-way hub ({hub_type_name})\n')
        f.write('0\nENDSEC\n0\nEOF\n')
    return len(angles)

def main():
    parser = argparse.ArgumentParser(description='Generate hub DXF templates')
    dome3d.main_parser = parser
    parser.add_argument('-f', '--frequency', type=int, required=True)
    parser.add_argument('-r', '--radius', type=float, default=15.0)
    parser.add_argument('-o', '--output', type=str, default='output/hub')
    args = parser.parse_args()

    freq, radius = args.frequency, args.radius
    verts, faces = build_sphere(freq)
    verts, faces = clip_hemisphere(verts, faces)
    verts = scale_verts(verts, radius)
    edges = extract_edges(faces)

    hubs = hub_angles(verts, edges, radius, freq)

    print(f'{freq}V dome hubs:')
    for valence in sorted(hubs.keys()):
        angles_list = hubs[valence]
        path = f'{args.output}_{valence}way.dxf'
        n = len(angles_list)
        avg_angles = [sum(a[i] for a in angles_list) / n for i in range(valence)]
        write_dxf(path, f'{freq}V', valence, avg_angles)
        print(f'  {valence}-way: {n} hubs → {path}')

if __name__ == '__main__':
    main()
