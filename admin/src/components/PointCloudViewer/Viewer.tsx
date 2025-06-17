import React, { useRef, useEffect } from "react";
import * as THREE from "three";

const WS_URL = "ws://localhost:3000/ws/pointcloud";

const Viewer: React.FC = () => {
  const mountRef = useRef<HTMLDivElement>(null);
  const geometryRef = useRef<THREE.BufferGeometry | null>(null);
  
  useEffect(() => {
    let width = mountRef.current?.clientWidth || 0;
    let height = mountRef.current?.clientHeight || 0;
    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.01, 100);
    camera.position.set(0, 0, 2);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    mountRef.current!.appendChild(renderer.domElement);

    // 点云 geometry
    const geometry = new THREE.BufferGeometry();
    geometryRef.current = geometry;
    geometry.setAttribute("position", new THREE.BufferAttribute(new Float32Array([]), 3));
    geometry.setAttribute("color", new THREE.BufferAttribute(new Float32Array([]), 3));

    const material = new THREE.PointsMaterial({
      size: 0.01,
      vertexColors: true, // 必须为true
    });
    const points = new THREE.Points(geometry, material);
    scene.add(points);

    const animate = () => {
      requestAnimationFrame(animate);
      renderer.render(scene, camera);
    };
    animate();

    // WebSocket 数据处理
    const ws = new WebSocket(WS_URL);
    ws.binaryType = "arraybuffer";
    ws.onmessage = event => {
      const buffer = event.data as ArrayBuffer;
      const arr = new Float32Array(buffer); // [x, y, z, ...]
      const n = arr.length / 3;
      // 取所有z
      let minZ = Infinity,
        maxZ = -Infinity;
      for (let i = 0; i < n; i++) {
        const z = arr[i * 3 + 2];
        if (z < minZ) minZ = z;
        if (z > maxZ) maxZ = z;
      }
      // 构造颜色数组，根据z线性插值到灰度
      const colors = new Float32Array(n * 3);
      for (let i = 0; i < n; i++) {
        const z = arr[i * 3 + 2];
        // 避免maxZ==minZ时除0
        let t = (z - minZ) / (maxZ - minZ || 1); // 归一化0~1
        // 你可以选择不同色阶，比如灰度（r=g=b）或者伪彩色（如彩虹映射）
        colors[i * 3] = t; // R
        colors[i * 3 + 1] = t; // G
        colors[i * 3 + 2] = t; // B
      }
      if (geometryRef.current) {
        geometryRef.current.setAttribute("position", new THREE.BufferAttribute(arr, 3));
        geometryRef.current.setAttribute("color", new THREE.BufferAttribute(colors, 3));
        geometryRef.current.computeBoundingSphere();
      }
    };

    return () => {
      ws.close();
      renderer.dispose();
      mountRef.current?.removeChild(renderer.domElement);
    };
  }, []);

  return (
    <div
      ref={mountRef}
      style={{ width: "70vw", height: "70vh", background: "#181818", zIndex: 999999 }}
    />
  );
};

export default Viewer;
