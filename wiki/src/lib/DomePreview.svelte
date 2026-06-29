<script>
  import { onMount, onDestroy } from 'svelte';
  import * as THREE from 'three';
  import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

  let { modelUrl } = $props();

  let canvasEl;
  let renderer, scene, camera, controls;
  let animationId;
  let showStruts = $state(true);
  let showHubs = $state(true);
  let showFaces = $state(false);
  let strutGroups = $state([]);
  let hubMeshes = $state([]);
  let faceMesh = null;
  let info = $state({ vertices: 0, struts: 0, types: 0 });

  onMount(async () => {
    const r = await fetch(modelUrl);
    const data = await r.json();
    info = { vertices: data.vertex_count, struts: data.edge_count, types: data.strut_type_count };

    renderer = new THREE.WebGLRenderer({ canvas: canvasEl, antialias: true, alpha: true });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const container = canvasEl.parentElement;
    const cw = container.clientWidth || 800;
    const ch = container.clientHeight || 500;
    renderer.setSize(cw, ch, false);

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f1117);

    camera = new THREE.PerspectiveCamera(55, cw / ch, 0.5, 200);
    camera.position.set(0, 7.5, 28);
    camera.lookAt(0, 7.5, 0);

    controls = new OrbitControls(camera, renderer.domElement);
    controls.target.set(0, 7.5, 0);
    controls.enableDamping = true;
    controls.dampingFactor = 0.1;
    controls.minDistance = 18;
    controls.maxDistance = 60;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 0.4;
    controls.update();

    window.addEventListener('resize', () => {
      const w = container.clientWidth;
      const h = container.clientHeight;
      if (w > 0 && h > 0) {
        renderer.setSize(w, h, false);
        camera.aspect = w / h;
        camera.updateProjectionMatrix();
      }
    });

    // Dome parent group — rotate from Z-up (generated) to Y-up (Three.js)
    const domeGroup = new THREE.Group();
    domeGroup.rotation.x = -Math.PI / 2;
    scene.add(domeGroup);

    // Lighting
    scene.add(new THREE.AmbientLight(0x404060, 2));
    const sun = new THREE.DirectionalLight(0xffffff, 4);
    sun.position.set(20, 30, 15);
    scene.add(sun);
    const fill = new THREE.DirectionalLight(0x4488cc, 1.5);
    fill.position.set(-10, 5, -5);
    scene.add(fill);

    // Ground plane reference
    const grid = new THREE.GridHelper(40, 20, 0x2a2d3a, 0x1a1d27);
    grid.position.y = 0;
    scene.add(grid);

    // Build strut meshes
    const strutParent = new THREE.Group();
    strutParent.name = 'struts';
    domeGroup.add(strutParent);
    strutGroups = [];

    const strutMat = new THREE.MeshStandardMaterial({ roughness: 0.4, metalness: 0.1 });

    for (const group of data.strut_groups) {
      const verts = data.vertices;
      const edges = group.edges;
      const color = new THREE.Color(...group.color);
      const mat = strutMat.clone();
      mat.color = color;

      const groupMesh = new THREE.Group();
      groupMesh.name = group.type;

      for (const [a, b] of edges) {
        const p1 = new THREE.Vector3(...verts[a]);
        const p2 = new THREE.Vector3(...verts[b]);
        const mid = new THREE.Vector3().addVectors(p1, p2).multiplyScalar(0.5);
        const dir = new THREE.Vector3().subVectors(p2, p1);
        const len = dir.length();
        const strutR = 0.18;
        const endR = strutR * 1.5;
        const endH = 0.06;

        // Main strut cylinder
        const cylGeo = new THREE.CylinderGeometry(strutR, strutR, len - endH * 2, 12);
        const cyl = new THREE.Mesh(cylGeo, mat);
        cyl.position.copy(mid);
        const q = new THREE.Quaternion();
        q.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.normalize());
        cyl.setRotationFromQuaternion(q);
        groupMesh.add(cyl);

        // Flattened end caps
        for (const pt of [p1, p2]) {
          const endGeo = new THREE.CylinderGeometry(endR, endR, endH, 8);
          const end = new THREE.Mesh(endGeo, mat);
          end.position.copy(pt);
          end.setRotationFromQuaternion(q);
          groupMesh.add(end);
        }
      }

      strutParent.add(groupMesh);
      strutGroups = [...strutGroups, { mesh: groupMesh, type: group.type, count: group.count }];
    }

    // Hub discs
    const hubParent = new THREE.Group();
    hubParent.name = 'hubs';
    domeGroup.add(hubParent);
    hubMeshes = [];
    const hubGeo = new THREE.CylinderGeometry(0.45, 0.45, 0.08, 12);
    const hubMat = new THREE.MeshStandardMaterial({ color: 0x8890a0, roughness: 0.3, metalness: 0.5 });

    for (const [vi, hub] of Object.entries(data.hubs)) {
      const pos = new THREE.Vector3(...hub.position);
      const n = new THREE.Vector3(...hub.normal);
      const disc = new THREE.Mesh(hubGeo, hubMat);
      disc.position.copy(pos);
      const q = new THREE.Quaternion();
      q.setFromUnitVectors(new THREE.Vector3(0, 1, 0), n);
      disc.setRotationFromQuaternion(q);
      hubParent.add(disc);
      hubMeshes = [...hubMeshes, disc];
    }

    // Face mesh (optional, off by default)
    const faceGeo = new THREE.BufferGeometry();
    const faceVerts = [];
    for (const v of data.vertices) faceVerts.push(...v);
    const faceIdx = [];
    for (const f of data.faces) faceIdx.push(f[0], f[1], f[2]);
    faceGeo.setAttribute('position', new THREE.Float32BufferAttribute(faceVerts, 3));
    faceGeo.setIndex(faceIdx);
    faceGeo.computeVertexNormals();
    faceMesh = new THREE.Mesh(faceGeo, new THREE.MeshPhongMaterial({
      color: 0xffffff, transparent: true, opacity: 0.1, side: THREE.DoubleSide
    }));
    faceMesh.visible = false;
    domeGroup.add(faceMesh);

    function animate() {
      animationId = requestAnimationFrame(animate);
      controls.update();
      renderer.render(scene, camera);
    }
    animate();
  });

  onDestroy(() => {
    if (typeof window !== 'undefined' && animationId != null) {
      cancelAnimationFrame(animationId);
    }
    renderer?.dispose();
  });

  function toggleStruts() {
    showStruts = !showStruts;
    const p = scene.getObjectByName('struts');
    if (p) p.visible = showStruts;
  }
  function toggleHubs() {
    showHubs = !showHubs;
    const p = scene.getObjectByName('hubs');
    if (p) p.visible = showHubs;
  }
  function toggleFaces() {
    showFaces = !showFaces;
    if (faceMesh) faceMesh.visible = showFaces;
  }
</script>

<div class="preview-container">
  <canvas bind:this={canvasEl}></canvas>
  <div class="preview-info">
    {info.vertices} vertices · {info.struts} struts · {info.types} types
  </div>
  <div class="preview-controls">
    <button class:active={showStruts} onclick={toggleStruts}>Struts</button>
    <button class:active={showHubs} onclick={toggleHubs}>Hubs</button>
    <button class:active={showFaces} onclick={toggleFaces}>Faces</button>
    {#each strutGroups as g}
      <span class="badge badge-{g.type}" style="margin-left:4px;">{g.type}</span>
    {/each}
  </div>
</div>
