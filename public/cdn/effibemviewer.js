/**
 * EffiBEM Viewer v0.3.0 - A Three.js-based viewer for OpenStudio GLTF models
 * https://github.com/jmarrec/effibemviewer
 * https://effibem.com
 */
import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";

/**
 * EffiBEMViewer - A viewer for OpenStudio GLTF models
 */
class EffiBEMViewer {
  constructor(container, options = {}) {
    this.container = typeof container === 'string' ? document.getElementById(container) : container;
    this.options = {
      includeGeometryDiagnostics: options.includeGeometryDiagnostics || false,
    };

    // Toggle diagnostics visibility via CSS class
    if (this.options.includeGeometryDiagnostics) {
      this.container.classList.add('include-diagnostics');
    }

    // Internal state
    this.sceneObjects = [];
    this.objectEdges = new Map();
    this.backObjects = new Map();
    this.backToFront = new Map();
    this.selectedObject = null;
    this.originalMaterial = null;
    this.selectedBackWasVisible = false;
    this.renderRequested = false;
    this.mouseDownPos = { x: 0, y: 0 };

    // Get DOM elements
    this.infoPanel = this.container.querySelector('.info-panel');

    this._initScene();
    this._initControls();
    this._initEventListeners();
  }

  _initScene() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xf5f5f5);

    this.camera = new THREE.PerspectiveCamera(45, this.container.clientWidth / this.container.clientHeight, 0.1, 5000);

    this.renderer = new THREE.WebGLRenderer({ antialias: true });
    this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    this.renderer.outputColorSpace = THREE.SRGBColorSpace;
    this.container.appendChild(this.renderer.domElement);

    this.orbitControls = new OrbitControls(this.camera, this.renderer.domElement);

    // Lighting
    this.scene.add(new THREE.AmbientLight(0x888888));
    this.scene.add(new THREE.HemisphereLight(0xffffff, 0x444444, 0.6));
    const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
    dirLight.position.set(1, 2, 1);
    this.scene.add(dirLight);

    // Selection material
    this.selectedMaterial = new THREE.MeshStandardMaterial({
      color: 0xffff00,
      emissive: 0x444400,
      side: THREE.DoubleSide
    });
  }

  _initControls() {
    const $ = (sel) => this.container.querySelector(sel);

    // Surface filter checkboxes
    ['showFloors', 'showWalls', 'showRoofs', 'showWindows', 'showDoors', 'showShading', 'showPartitions', 'showEdges'].forEach(cls => {
      $(`.${cls}`)?.addEventListener('change', () => this._updateVisibility());
    });

    // Story dropdown
    $('.showStory')?.addEventListener('change', () => this._updateVisibility());

    // Render mode dropdown
    $('.renderBy')?.addEventListener('change', () => this._updateRenderMode());

    // Diagnostic filters
    if (this.options.includeGeometryDiagnostics) {
      ['showOnlyNonConvexSurfaces', 'showOnlyIncorrectlyOriented', 'showOnlyNonConvexSpaces', 'showOnlyNonEnclosedSpaces'].forEach(cls => {
        $(`.${cls}`)?.addEventListener('change', () => this._updateVisibility());
      });
    }
  }

  _initEventListeners() {
    // Window resize
    window.addEventListener('resize', () => {
      this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
      this.camera.updateProjectionMatrix();
      this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
      this._requestRender();
    });

    // Orbit controls change
    this.orbitControls.addEventListener('change', () => this._requestRender());

    // Mouse events for selection
    this.renderer.domElement.addEventListener('mousedown', (e) => {
      this.mouseDownPos.x = e.clientX;
      this.mouseDownPos.y = e.clientY;
    });

    this.renderer.domElement.addEventListener('click', (e) => this._onClick(e));
  }

  _onClick(event) {
    // Ignore if this was a drag (camera orbit)
    const dx = event.clientX - this.mouseDownPos.x;
    const dy = event.clientY - this.mouseDownPos.y;
    if (Math.abs(dx) > 5 || Math.abs(dy) > 5) return;

    const rect = this.renderer.domElement.getBoundingClientRect();
    const mouse = new THREE.Vector2(
      ((event.clientX - rect.left) / rect.width) * 2 - 1,
      -((event.clientY - rect.top) / rect.height) * 2 + 1
    );

    const raycaster = new THREE.Raycaster();
    raycaster.setFromCamera(mouse, this.camera);

    // Include both front and back objects for picking
    const visibleObjects = this.sceneObjects.filter(obj => obj.visible);
    const visibleBackObjects = [...this.backObjects.values()].filter(obj => obj.visible);
    const allPickable = [...visibleObjects, ...visibleBackObjects];

    const intersects = raycaster.intersectObjects(allPickable);

    if (intersects.length > 0) {
      let hitObj = intersects[0].object;
      // If we hit a back object, resolve to its front object
      if (this.backToFront.has(hitObj)) {
        hitObj = this.backToFront.get(hitObj);
      }
      this._selectObject(hitObj, event.clientX, event.clientY);
    } else {
      this._selectObject(null);
    }

    this._requestRender();
  }

  _selectObject(obj, clickX, clickY) {
    // Restore previous selection
    if (this.selectedObject && this.originalMaterial) {
      this.selectedObject.material = this.originalMaterial;
      const prevBackObj = this.backObjects.get(this.selectedObject);
      if (prevBackObj) {
        prevBackObj.visible = this.selectedBackWasVisible;
      }
    }

    if (obj) {
      this.selectedObject = obj;
      this.originalMaterial = obj.material;
      obj.material = this.selectedMaterial;

      const backObj = this.backObjects.get(obj);
      if (backObj) {
        this.selectedBackWasVisible = backObj.visible;
        backObj.visible = false;
      }

      this._updateInfoPanel(obj, clickX, clickY);
    } else {
      this.selectedObject = null;
      this.originalMaterial = null;
      this.infoPanel.style.display = 'none';
    }
  }

  _updateInfoPanel(obj, clickX, clickY) {
    const $ = (sel) => this.container.querySelector(sel);
    const data = obj.userData;
    const renderMode = $('.renderBy').value;

    $('.info-name').textContent = data.name || 'Unknown';

    const renderByToRowId = {
      'surfaceType': 'type',
      'boundary': 'boundary',
      'construction': 'construction',
      'thermalZone': 'thermalZone',
      'spaceType': 'spaceType',
      'buildingStory': 'buildingStory',
    };
    const emphasizedRowId = renderByToRowId[renderMode];

    const setRow = (id, value) => {
      const row = $(`.info-${id}-row`);
      const span = $(`.info-${id}`);
      if (value) {
        span.textContent = value;
        row.style.display = 'block';
        row.classList.toggle('emphasized', id === emphasizedRowId);
      } else {
        row.style.display = 'none';
        row.classList.remove('emphasized');
      }
    };

    setRow('type', data.surfaceType);
    setRow('space', data.spaceName);
    setRow('spaceType', data.spaceTypeName);
    setRow('thermalZone', data.thermalZoneName);
    setRow('buildingStory', data.buildingStoryName);
    setRow('construction', data.constructionName);
    setRow('boundary', data.outsideBoundaryCondition);
    setRow('boundaryObject', data.outsideBoundaryConditionObjectName);
    setRow('sunExposure', data.sunExposure);
    setRow('windExposure', data.windExposure);

    if (this.options.includeGeometryDiagnostics) {
      const setDiagRow = (id, value) => {
        const row = $(`.info-${id}-row`);
        const span = $(`.info-${id}`);
        if (row && value !== undefined) {
          span.innerHTML = `<span class="badge ${value ? 'badge-success' : 'badge-danger'}">${value}</span>`;
          row.style.display = 'block';
        } else if (row) {
          row.style.display = 'none';
        }
      };

      setDiagRow('convex', data.convex);
      setDiagRow('correctlyOriented', data.correctlyOriented);
      setDiagRow('spaceConvex', data.spaceConvex);
      setDiagRow('spaceEnclosed', data.spaceEnclosed);
    }

    // Position panel
    const rect = this.container.getBoundingClientRect();
    let left = clickX - rect.left + 15;
    let top = clickY - rect.top - 10;

    this.infoPanel.style.display = 'block';
    const panelRect = this.infoPanel.getBoundingClientRect();
    if (left + panelRect.width > this.container.clientWidth) {
      left = clickX - rect.left - panelRect.width - 15;
    }
    if (top + panelRect.height > this.container.clientHeight) {
      top = this.container.clientHeight - panelRect.height - 10;
    }
    if (top < 10) top = 10;

    this.infoPanel.style.left = left + 'px';
    this.infoPanel.style.top = top + 'px';
  }

  _updateVisibility() {
    const $ = (sel) => this.container.querySelector(sel);
    const showFloors = $('.showFloors')?.checked ?? true;
    const showWalls = $('.showWalls')?.checked ?? true;
    const showRoofs = $('.showRoofs')?.checked ?? true;
    const showWindows = $('.showWindows')?.checked ?? true;
    const showDoors = $('.showDoors')?.checked ?? true;
    const showShading = $('.showShading')?.checked ?? true;
    const showPartitions = $('.showPartitions')?.checked ?? true;
    const showEdges = $('.showEdges')?.checked ?? true;
    const showStory = $('.showStory')?.value || '';

    const showOnlyNonConvexSurfaces = this.options.includeGeometryDiagnostics && $('.showOnlyNonConvexSurfaces')?.checked;
    const showOnlyIncorrectlyOriented = this.options.includeGeometryDiagnostics && $('.showOnlyIncorrectlyOriented')?.checked;
    const showOnlyNonConvexSpaces = this.options.includeGeometryDiagnostics && $('.showOnlyNonConvexSpaces')?.checked;
    const showOnlyNonEnclosedSpaces = this.options.includeGeometryDiagnostics && $('.showOnlyNonEnclosedSpaces')?.checked;

    this.sceneObjects.forEach(obj => {
      const surfaceType = obj.userData?.surfaceType || '';
      const storyName = obj.userData?.buildingStoryName || '';
      let visible = true;

      // Filter by surface type
      if (surfaceType === 'Floor') visible = showFloors;
      else if (surfaceType === 'Wall') visible = showWalls;
      else if (surfaceType === 'RoofCeiling') visible = showRoofs;
      else if (surfaceType.includes('Window') || surfaceType.includes('Skylight') || surfaceType.includes('TubularDaylight') || surfaceType === 'GlassDoor') visible = showWindows;
      else if (surfaceType.includes('Door')) visible = showDoors;
      else if (surfaceType.includes('Shading')) visible = showShading;
      else if (surfaceType === 'InteriorPartitionSurface') visible = showPartitions;

      // Filter by story
      if (visible && showStory && storyName !== showStory) {
        visible = false;
      }

      // Geometry diagnostic filters
      if (visible && showOnlyNonConvexSurfaces && obj.userData.convex !== false) {
        visible = false;
      }
      if (visible && showOnlyIncorrectlyOriented && obj.userData.correctlyOriented !== false) {
        visible = false;
      }
      if (visible && showOnlyNonConvexSpaces && obj.userData.spaceConvex !== false) {
        visible = false;
      }
      if (visible && showOnlyNonEnclosedSpaces && obj.userData.spaceEnclosed !== false) {
        visible = false;
      }

      obj.visible = visible;

      const edges = this.objectEdges.get(obj);
      if (edges) {
        edges.visible = visible && showEdges;
      }

      const backObj = this.backObjects.get(obj);
      if (backObj) {
        backObj.visible = visible;
      }
    });

    this._requestRender();
  }

  _updateRenderMode() {
    const renderMode = this.container.querySelector('.renderBy').value;
    this.sceneObjects.forEach(obj => {
      const { colorExt, colorInt } = this._getColorsForObject(obj, renderMode);
      obj.material.color.setHex(colorExt);
      const backObj = this.backObjects.get(obj);
      if (backObj) {
        backObj.material.color.setHex(colorInt);
      }
    });
    this._requestRender();
  }

  _getColorsForObject(obj, renderMode) {
    const data = obj.userData;
    let colorExt, colorInt;

    switch (renderMode) {
      case 'surfaceType':
        colorExt = EffiBEMViewer.SURFACE_TYPE_COLORS[data.surfaceType] ?? 0xcccccc;
        colorInt = EffiBEMViewer.SURFACE_TYPE_COLORS_INT[data.surfaceType] ?? 0xeeeeee;
        break;
      case 'boundary':
        const bc = data.outsideBoundaryCondition || 'Outdoors';
        let boundaryKey = bc;
        if (bc === 'Outdoors') {
          const sun = data.sunExposure === 'SunExposed';
          const wind = data.windExposure === 'WindExposed';
          if (sun && wind) boundaryKey = 'Outdoors_SunWind';
          else if (sun) boundaryKey = 'Outdoors_Sun';
          else if (wind) boundaryKey = 'Outdoors_Wind';
        }
        colorExt = EffiBEMViewer.BOUNDARY_COLORS[boundaryKey] ?? EffiBEMViewer.BOUNDARY_COLORS[bc] ?? 0xcccccc;
        colorInt = colorExt;
        break;
      case 'construction':
        colorExt = this._getDynamicColor('construction', data.constructionName);
        colorInt = colorExt;
        break;
      case 'thermalZone':
        colorExt = this._getDynamicColor('thermalZone', data.thermalZoneName);
        colorInt = colorExt;
        break;
      case 'spaceType':
        colorExt = this._getDynamicColor('spaceType', data.spaceTypeName);
        colorInt = colorExt;
        break;
      case 'buildingStory':
        colorExt = this._getDynamicColor('buildingStory', data.buildingStoryName);
        colorInt = colorExt;
        break;
      default:
        colorExt = 0xcccccc;
        colorInt = 0xeeeeee;
    }
    return { colorExt, colorInt };
  }

  _getDynamicColor(category, name) {
    if (!this._dynamicColors) this._dynamicColors = {};
    const key = `${category}_${name}`;
    if (!this._dynamicColors[key]) {
      this._dynamicColors[key] = EffiBEMViewer._stringToColor(name);
    }
    return this._dynamicColors[key];
  }

  static _stringToColor(str) {
    if (!str) return 0xcccccc;
    let hash = 0;
    for (let i = 0; i < str.length; i++) {
      hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }
    const h = Math.abs(hash) % 360;
    return new THREE.Color(`hsl(${h}, 65%, 55%)`).getHex();
  }

  _requestRender() {
    if (!this.renderRequested) {
      this.renderRequested = true;
      requestAnimationFrame(() => this._render());
    }
  }

  _render() {
    this.renderRequested = false;
    this.orbitControls.update();
    this.renderer.render(this.scene, this.camera);
  }

  _loadGLTF(gltfData) {
    const loader = new GLTFLoader();
    loader.parse(
      JSON.stringify(gltfData),
      "",
      (gltf) => {
        this.scene.add(gltf.scene);
        this._processLoadedScene(gltf, gltfData);
        this._requestRender();
      },
      (e) => console.error('GLTF load error:', e)
    );
  }

  _processLoadedScene(gltf, gltfData) {
    const renderMode = this.container.querySelector('.renderBy').value;
    const edgeMaterial = new THREE.LineBasicMaterial({ color: 0x000000 });

    gltf.scene.traverse(obj => {
      if (obj.isMesh && obj.userData?.surfaceType) {
        this.sceneObjects.push(obj);

        const { colorExt, colorInt } = this._getColorsForObject(obj, renderMode);

        obj.material = new THREE.MeshPhongMaterial({
          color: colorExt,
          specular: 0x222222,
          shininess: 30,
          side: THREE.FrontSide
        });

        const backObj = obj.clone();
        backObj.material = new THREE.MeshPhongMaterial({
          color: colorInt,
          specular: 0x222222,
          shininess: 30,
          side: THREE.BackSide
        });
        obj.parent.add(backObj);
        this.backObjects.set(obj, backObj);
        this.backToFront.set(backObj, obj);

        const edgesGeometry = new THREE.EdgesGeometry(obj.geometry);
        const edges = new THREE.LineSegments(edgesGeometry, edgeMaterial);
        edges.position.copy(obj.position);
        edges.rotation.copy(obj.rotation);
        edges.scale.copy(obj.scale);
        obj.parent.add(edges);
        this.objectEdges.set(obj, edges);
      }
    });

    // Populate story dropdown
    const storySelect = this.container.querySelector('.showStory');
    const storyNames = [...new Set(this.sceneObjects.map(o => o.userData?.buildingStoryName).filter(Boolean))].sort();
    storyNames.forEach(name => {
      const option = document.createElement('option');
      option.value = name;
      option.textContent = name;
      storySelect.appendChild(option);
    });

    // Add axes and position camera
    this._addAxes(gltfData);
    this._positionCamera(gltfData);
  }

  _addAxes(gltfData) {
    const bbox = gltfData.scenes?.[0]?.extras?.boundingbox;
    const axisSize = bbox ? bbox.lookAtR * 4 : 10;

    // X axis (red)
    const xAxisGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0), new THREE.Vector3(axisSize, 0, 0)
    ]);
    this.scene.add(new THREE.Line(xAxisGeometry, new THREE.LineBasicMaterial({ color: 0xff0000 })));

    // Y axis (green) - OpenStudio Y -> Three.js -Z
    const yAxisGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, 0, -axisSize)
    ]);
    this.scene.add(new THREE.Line(yAxisGeometry, new THREE.LineBasicMaterial({ color: 0x00ff00 })));

    // Z axis (blue) - OpenStudio Z -> Three.js Y
    const zAxisGeometry = new THREE.BufferGeometry().setFromPoints([
      new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, axisSize, 0)
    ]);
    this.scene.add(new THREE.Line(zAxisGeometry, new THREE.LineBasicMaterial({ color: 0x0000ff })));

    // North axis (orange) if set
    const northAxis = gltfData.scenes?.[0]?.extras?.northAxis;
    if (northAxis && northAxis !== 0) {
      const northAxisRad = -northAxis * Math.PI / 180.0;
      const northAxisGeometry = new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(-Math.sin(northAxisRad) * axisSize, 0, -Math.cos(northAxisRad) * axisSize)
      ]);
      this.scene.add(new THREE.Line(northAxisGeometry, new THREE.LineBasicMaterial({ color: 0xff9933 })));
    }
  }

  _positionCamera(gltfData) {
    const bbox = gltfData.scenes?.[0]?.extras?.boundingbox;
    if (bbox) {
      const lookAt = new THREE.Vector3(bbox.lookAtX, bbox.lookAtZ, -bbox.lookAtY);
      const radius = 2.5 * bbox.lookAtR;

      const theta = -30 * Math.PI / 180;
      const phi = 30 * Math.PI / 180;
      this.camera.position.set(
        radius * Math.cos(theta) * Math.cos(phi) + lookAt.x,
        radius * Math.sin(phi) + lookAt.y,
        -radius * Math.sin(theta) * Math.cos(phi) + lookAt.z
      );

      this.orbitControls.target.copy(lookAt);
      this.orbitControls.update();
    }
  }

  /**
   * Load and render a GLTF model from a JSON object
   * @param {Object} gltfData - The GLTF JSON data
   */
  loadFromJSON(gltfData) {
    this._loadGLTF(gltfData);
  }

  /**
   * Load and render a GLTF model from a URL
   * @param {string} url - URL to the GLTF JSON file
   * @returns {Promise} Resolves when loading starts
   */
  loadFromFile(url) {
    return fetch(url)
      .then(response => {
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        return response.json();
      })
      .then(data => this.loadFromJSON(data));
  }

  /**
   * Load and render a GLTF model from a File object (e.g., from <input type="file">)
   * @param {File} file - The File object to load
   * @returns {Promise} Resolves when loading completes
   */
  loadFromFileObject(file) {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = JSON.parse(e.target.result);
          this.loadFromJSON(data);
          resolve(data);
        } catch (err) {
          reject(new Error(`Failed to parse GLTF JSON: ${err.message}`));
        }
      };
      reader.onerror = () => reject(new Error('Failed to read file'));
      reader.readAsText(file);
    });
  }
}

// Static color definitions
EffiBEMViewer.SURFACE_TYPE_COLORS = {
  'Floor': 0x808080, 'Wall': 0xccb266, 'RoofCeiling': 0x994c4c,
  'Window': 0x66b2cc, 'GlassDoor': 0x66b2cc, 'Skylight': 0x66b2cc,
  'TubularDaylightDome': 0x66b2cc, 'TubularDaylightDiffuser': 0x66b2cc,
  'Door': 0x99854c, 'OverheadDoor': 0x99854c,
  'SiteShading': 0x4b7c95, 'BuildingShading': 0x714c99, 'SpaceShading': 0x4c6eb2,
  'InteriorPartitionSurface': 0x9ebc8f, 'AirWall': 0x66b2cc,
};

EffiBEMViewer.SURFACE_TYPE_COLORS_INT = {
  'Floor': 0xbfbfbf, 'Wall': 0xebe2c5, 'RoofCeiling': 0xca9595,
  'Window': 0xc0e2eb, 'GlassDoor': 0xc0e2eb, 'Skylight': 0xc0e2eb,
  'TubularDaylightDome': 0xc0e2eb, 'TubularDaylightDiffuser': 0xc0e2eb,
  'Door': 0xcabc95, 'OverheadDoor': 0xcabc95,
  'SiteShading': 0xbbd1dc, 'BuildingShading': 0xd8cbe5, 'SpaceShading': 0xb7c5e0,
  'InteriorPartitionSurface': 0xd5e2cf, 'AirWall': 0xc0e2eb,
};

EffiBEMViewer.BOUNDARY_COLORS = {
  'Surface': 0x009900, 'Adiabatic': 0xff0000, 'Space': 0xff0000,
  'Outdoors': 0xa3cccc, 'Outdoors_Sun': 0x28cccc, 'Outdoors_Wind': 0x099fa2, 'Outdoors_SunWind': 0x4477a1,
  'Ground': 0xccb77a, 'Foundation': 0x751e7a,
  'OtherSideCoefficients': 0x3f3f3f, 'OtherSideConditionsModel': 0x99004c,
};

// Expose to global scope for non-module usage
window.EffiBEMViewer = EffiBEMViewer;

// Convenience functions that match geometry_preview.html API
window.runFromJSON = function(gltfData, options = {}) {
  const containerId = options.containerId || 'viewer';
  const viewer = new EffiBEMViewer(containerId, options);
  viewer.loadFromJSON(gltfData);
  return viewer;
};

window.runFromFile = function(url, options = {}) {
  const containerId = options.containerId || 'viewer';
  const viewer = new EffiBEMViewer(containerId, options);
  viewer.loadFromFile(url);
  return viewer;
};

window.runFromFileObject = function(file, options = {}) {
  const containerId = options.containerId || 'viewer';
  const viewer = new EffiBEMViewer(containerId, options);
  viewer.loadFromFileObject(file);
  return viewer;
};

// Export for ES module usage
export { EffiBEMViewer };
