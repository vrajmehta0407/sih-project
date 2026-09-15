import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

export const ThreePackageViewer = ({
  className = '',
  scanActive = true,
  mode = 'normal', // 'normal', 'xray', 'slackfill', 'ela'
  fillPercentage = 68,
}) => {
  const containerRef = useRef(null);
  const rendererRef = useRef(null);
  const sceneRef = useRef(null);
  const packageMeshRef = useRef(null);
  const liquidMeshRef = useRef(null);
  const laserPlaneRef = useRef(null);
  const wireframeMeshRef = useRef(null);

  const [interactiveMode, setInteractiveMode] = useState(mode);
  const [fillLevel, setFillLevel] = useState(fillPercentage);
  const [autoRotate, setAutoRotate] = useState(true);

  useEffect(() => {
    setInteractiveMode(mode);
  }, [mode]);

  useEffect(() => {
    setFillLevel(fillPercentage);
  }, [fillPercentage]);

  useEffect(() => {
    if (!containerRef.current) return;

    const width = containerRef.current.clientWidth;
    const height = containerRef.current.clientHeight || 400;

    // Scene
    const scene = new THREE.Scene();
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000);
    camera.position.set(0, 1, 4.5);

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    rendererRef.current = renderer;

    containerRef.current.innerHTML = '';
    containerRef.current.appendChild(renderer.domElement);

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 1.2);
    scene.add(ambientLight);

    const dirLight1 = new THREE.DirectionalLight(0x38bdf8, 2.5);
    dirLight1.position.set(5, 8, 5);
    scene.add(dirLight1);

    const dirLight2 = new THREE.DirectionalLight(0xa855f7, 2.0);
    dirLight2.position.set(-5, -4, -3);
    scene.add(dirLight2);

    const pointLight = new THREE.PointLight(0x00f0ff, 3, 10);
    pointLight.position.set(0, 2, 2);
    scene.add(pointLight);

    // Outer Container Geometry (Product Cereal/Snack Box)
    const boxGeo = new THREE.BoxGeometry(1.6, 2.4, 0.9, 16, 16, 16);

    // Normal Textured Material (Simulated Legal Metrology Label)
    const canvas = document.createElement('canvas');
    canvas.width = 512;
    canvas.height = 768;
    const ctx = canvas.getContext('2d');
    if (ctx) {
      // Background gradient
      const grad = ctx.createLinearGradient(0, 0, 512, 768);
      grad.addColorStop(0, '#1e3a8a');
      grad.addColorStop(0.5, '#3b82f6');
      grad.addColorStop(1, '#6366f1');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 512, 768);

      // Label Header
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 36px sans-serif';
      ctx.fillText('PRISTINE ORGANICS', 40, 80);

      ctx.fillStyle = '#fde047';
      ctx.font = 'bold 24px monospace';
      ctx.fillText('RULE 6(1) VERIFIED', 40, 120);

      // Bounding Box Indicators
      ctx.strokeStyle = '#22c55e';
      ctx.lineWidth = 4;
      ctx.strokeRect(30, 200, 450, 180);

      ctx.fillStyle = '#ffffff';
      ctx.font = '22px sans-serif';
      ctx.fillText('MRP: ₹ 240.00 (Incl. of all taxes)', 50, 245);
      ctx.fillText('Net Qty: 500 g', 50, 290);
      ctx.fillText('Mfg: 08/2026 • Exp: 08/2027', 50, 335);

      // QR Code Box
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(40, 420, 100, 100);
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(50, 430, 80, 80);
      ctx.fillStyle = '#ffffff';
      ctx.font = '16px monospace';
      ctx.fillText('BSA §63', 58, 475);
    }

    const labelTexture = new THREE.CanvasTexture(canvas);

    const normalMat = new THREE.MeshStandardMaterial({
      map: labelTexture,
      roughness: 0.25,
      metalness: 0.1,
      transparent: true,
      opacity: 0.95,
    });

    const boxMesh = new THREE.Mesh(boxGeo, normalMat);
    scene.add(boxMesh);
    packageMeshRef.current = boxMesh;

    // Wireframe Overlay
    const wireGeo = new THREE.WireframeGeometry(boxGeo);
    const wireMat = new THREE.LineBasicMaterial({
      color: 0x00f0ff,
      transparent: true,
      opacity: 0.25,
    });
    const wireMesh = new THREE.LineSegments(wireGeo, wireMat);
    boxMesh.add(wireMesh);
    wireframeMeshRef.current = wireMesh;

    // Inner Liquid/Grain Fill (For Slack-Fill Volumetrics)
    const fillHeight = 2.4 * (fillLevel / 100);
    const fillGeo = new THREE.BoxGeometry(1.5, fillHeight, 0.82);
    const fillMat = new THREE.MeshStandardMaterial({
      color: 0xf59e0b,
      roughness: 0.3,
      metalness: 0.2,
      transparent: true,
      opacity: 0.85,
    });
    const fillMesh = new THREE.Mesh(fillGeo, fillMat);
    fillMesh.position.y = -1.2 + fillHeight / 2;
    boxMesh.add(fillMesh);
    liquidMeshRef.current = fillMesh;

    // Laser Scanning Plane
    const laserGeo = new THREE.PlaneGeometry(2.4, 1.4);
    const laserMat = new THREE.MeshBasicMaterial({
      color: 0x10b981,
      transparent: true,
      opacity: 0.45,
      side: THREE.DoubleSide,
      blending: THREE.AdditiveBlending,
    });
    const laserPlane = new THREE.Mesh(laserGeo, laserMat);
    laserPlane.rotation.x = Math.PI / 2;
    scene.add(laserPlane);
    laserPlaneRef.current = laserPlane;

    // Mouse Interaction / Orbit
    let isDragging = false;
    let previousMousePosition = { x: 0, y: 0 };

    const handleMouseDown = (e) => {
      isDragging = true;
      setAutoRotate(false);
      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const handleMouseMove = (e) => {
      if (!isDragging || !boxMesh) return;
      const deltaX = e.clientX - previousMousePosition.x;
      const deltaY = e.clientY - previousMousePosition.y;

      boxMesh.rotation.y += deltaX * 0.01;
      boxMesh.rotation.x += deltaY * 0.01;

      previousMousePosition = { x: e.clientX, y: e.clientY };
    };

    const handleMouseUp = () => {
      isDragging = false;
    };

    const domElement = renderer.domElement;
    domElement.addEventListener('mousedown', handleMouseDown);
    window.addEventListener('mousemove', handleMouseMove);
    window.addEventListener('mouseup', handleMouseUp);

    // Animation Loop
    let laserDirection = 1;
    let reqId;

    const animate = () => {
      reqId = requestAnimationFrame(animate);

      if (autoRotate && boxMesh) {
        boxMesh.rotation.y += 0.008;
      }

      // Laser Sweep
      if (laserPlane && scanActive) {
        laserPlane.position.y += 0.02 * laserDirection;
        if (laserPlane.position.y > 1.4) laserDirection = -1;
        if (laserPlane.position.y < -1.4) laserDirection = 1;
      }

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!containerRef.current) return;
      const newW = containerRef.current.clientWidth;
      const newH = containerRef.current.clientHeight || 400;
      camera.aspect = newW / newH;
      camera.updateProjectionMatrix();
      renderer.setSize(newW, newH);
    };

    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(reqId);
      domElement.removeEventListener('mousedown', handleMouseDown);
      window.removeEventListener('mousemove', handleMouseMove);
      window.removeEventListener('mouseup', handleMouseUp);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
    };
  }, []);

  // Update mode shaders & visual properties
  useEffect(() => {
    if (!packageMeshRef.current || !liquidMeshRef.current || !wireframeMeshRef.current) return;

    const box = packageMeshRef.current;
    const fill = liquidMeshRef.current;
    const wire = wireframeMeshRef.current;

    if (interactiveMode === 'xray') {
      box.material.opacity = 0.35;
      box.material.color.setHex(0x38bdf8);
      fill.material.opacity = 0.9;
      fill.material.color.setHex(0xec4899);
      wire.material.opacity = 0.8;
      wire.material.color.setHex(0x00f0ff);
    } else if (interactiveMode === 'slackfill') {
      box.material.opacity = 0.25;
      box.material.color.setHex(0x94a3b8);
      fill.material.opacity = 0.85;
      fill.material.color.setHex(0xf59e0b);
      wire.material.opacity = 0.6;
    } else if (interactiveMode === 'ela') {
      box.material.opacity = 0.9;
      box.material.color.setHex(0x7c3aed);
      fill.material.opacity = 0.1;
      wire.material.opacity = 0.9;
      wire.material.color.setHex(0xef4444);
    } else {
      // Normal mode
      box.material.opacity = 0.95;
      box.material.color.setHex(0xffffff);
      fill.material.opacity = 0.6;
      fill.material.color.setHex(0xf59e0b);
      wire.material.opacity = 0.25;
      wire.material.color.setHex(0x00f0ff);
    }
  }, [interactiveMode]);

  return (
    <div className={`relative flex flex-col items-center select-none ${className}`}>
      {/* 3D Canvas Viewport */}
      <div
        ref={containerRef}
        className="w-full h-[420px] cursor-grab active:cursor-grabbing rounded-3xl overflow-hidden"
      />

      {/* 3D HUD Controls Bar */}
      <div className="absolute top-4 left-4 flex flex-wrap gap-2">
        <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-slate-900/80 backdrop-blur-md text-cyan-400 border border-cyan-500/30 flex items-center space-x-1.5 shadow">
          <span className="h-1.5 w-1.5 rounded-full bg-cyan-400 animate-ping" />
          <span>SPATIAL 3D MESH</span>
        </span>
        <span className="px-3 py-1 rounded-full text-[10px] font-mono font-bold bg-slate-900/80 backdrop-blur-md text-emerald-400 border border-emerald-500/30 shadow">
          HEADSPACE: {100 - fillLevel}% VOID
        </span>
      </div>

      {/* Mode Switcher Tabs */}
      <div className="absolute bottom-4 flex items-center gap-1.5 bg-slate-900/85 backdrop-blur-xl border border-white/20 p-1.5 rounded-2xl shadow-xl">
        {[
          { id: 'normal', label: 'Photometric' },
          { id: 'xray', label: 'X-Ray Scan' },
          { id: 'slackfill', label: 'Slack-Fill 3D' },
          { id: 'ela', label: 'Forensic ELA' },
        ].map((item) => (
          <button
            key={item.id}
            type="button"
            onClick={() => setInteractiveMode(item.id)}
            className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
              interactiveMode === item.id
                ? 'bg-gradient-to-r from-cyan-500 to-blue-600 text-white shadow-md font-bold'
                : 'text-slate-300 hover:text-white hover:bg-slate-800/80'
            }`}
          >
            {item.label}
          </button>
        ))}

        <button
          type="button"
          onClick={() => setAutoRotate(!autoRotate)}
          className={`px-2.5 py-1.5 rounded-xl text-xs font-semibold border transition-all ${
            autoRotate
              ? 'bg-purple-600/80 border-purple-400/50 text-white'
              : 'bg-slate-800 border-slate-700 text-slate-400'
          }`}
          title="Toggle 360° Orbit"
        >
          {autoRotate ? '360° ON' : 'PAUSED'}
        </button>
      </div>
    </div>
  );
};
export default ThreePackageViewer;
