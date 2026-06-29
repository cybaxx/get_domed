#!/usr/bin/env python3
"""Generate all dome models for 2V, 3V, 4V and organize into output directory."""
import os, sys, zipfile
import dome3d
import hub_dxf

FREQUENCIES = [2, 3, 4]
RADIUS = 15.0

OUT_DIR = os.path.join(os.path.dirname(__file__), 'wiki', 'static', 'models')

for freq in FREQUENCIES:
    dome_dir = os.path.join(OUT_DIR, f'{freq}v')
    os.makedirs(dome_dir, exist_ok=True)

    print(f'\n{"="*50}')
    print(f'  Generating {freq}V dome models')
    print(f'{"="*50}')

    verts, faces = dome3d.build_sphere(freq)
    verts, faces = dome3d.clip_hemisphere(verts, faces)
    verts = dome3d.scale_verts(verts, RADIUS)
    edges = dome3d.extract_edges(faces)
    strut_groups = dome3d.group_struts(verts, edges, RADIUS, freq)

    total_struts = sum(len(s[2]) for s in strut_groups)
    print(f'  Vertices: {len(verts)}, Struts: {total_struts}, Types: {len(strut_groups)}')

    # JSON for Three.js
    base = os.path.join(dome_dir, f'dome_{freq}v')
    dome3d.export_json(verts, faces, strut_groups, edges, RADIUS, freq, f'{base}.json')
    print(f'    [JSON] {base}.json')

    # Full dome STL + OBJ
    n_stl = dome3d.export_stl(verts, strut_groups, RADIUS, f'{base}_full.stl')
    print(f'    [STL]  {base}_full.stl ({n_stl} triangles)')
    dome3d.export_obj(verts, strut_groups, RADIUS, f'{base}_full.obj')
    print(f'    [OBJ]  {base}_full.obj')

    # Individual strut STLs
    for label, dist, struts in strut_groups:
        single = [(label, dist, struts)]
        n = dome3d.export_stl(verts, single, RADIUS, f'{base}_strut_{label}.stl')
        print(f'    [STL]  {base}_strut_{label}.stl ({n} triangles)')

    # Hub DXFs
    hubs = hub_dxf.hub_angles(verts, edges, RADIUS, freq)
    for valence in sorted(hubs.keys()):
        angles_list = hubs[valence]
        n = len(angles_list)
        path = os.path.join(dome_dir, f'hub_{valence}way.dxf')
        avg_angles = [sum(a[i] for a in angles_list) / n for i in range(valence)]
        hub_dxf.write_dxf(path, f'{freq}V', valence, avg_angles)
        print(f'    [DXF]  hub_{valence}way.dxf ({n} hubs)')

    # ZIP bundle (includes BOM CSVs)
    zip_path = os.path.join(dome_dir, f'dome_{freq}v_all.zip')
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for fname in sorted(os.listdir(dome_dir)):
            if fname != f'dome_{freq}v_all.zip':
                zf.write(os.path.join(dome_dir, fname), fname)
    size_kb = os.path.getsize(zip_path) / 1024
    print(f'    [ZIP]  dome_{freq}v_all.zip ({size_kb:.0f} KB)')

print(f'\nDone! All models in: {OUT_DIR}')
