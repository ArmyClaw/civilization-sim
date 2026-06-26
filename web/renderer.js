// renderer.js — Canvas Renderer for Civilization Sim (Enhanced)
const CivRenderer = (() => {
'use strict';

class Renderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.terrainCanvas = null;
    this.territoryCanvas = null; // offscreen territory overlay
    this.camera = { x: 0, y: 0, zoom: 3 };
    this.selectedId = -1;
    this.tribes = [];
    this.hoveredId = -1;
    this.eraIndex = 0;
    this._dragging = false;
    this._dragStart = { x: 0, y: 0 };
    this._camStart = { x: 0, y: 0 };
    this._pinchDist = 0;
    this.onClick = null;
    this._resize();
    this._bindEvents();
  }

  _resize() {
    const rect = this.canvas.parentElement.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = rect.width * dpr;
    this.canvas.height = rect.height * dpr;
    this.canvas.style.width = rect.width + 'px';
    this.canvas.style.height = rect.height + 'px';
    this.ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    this._displayWidth = rect.width;
    this._displayHeight = rect.height;
  }

  buildTerrain(terrain, size, colors) {
    this.terrainCanvas = document.createElement('canvas');
    this.terrainCanvas.width = size;
    this.terrainCanvas.height = size;
    const ctx = this.terrainCanvas.getContext('2d');
    const imgData = ctx.createImageData(size, size);
    const d = imgData.data;
    const colorMap = colors.map(hex => {
      const r = parseInt(hex.slice(1,3), 16);
      const g = parseInt(hex.slice(3,5), 16);
      const b = parseInt(hex.slice(5,7), 16);
      return [r, g, b];
    });
    for (let i = 0; i < size * size; i++) {
      const c = colorMap[terrain[i]] || colorMap[0];
      const idx = i * 4;
      d[idx]   = c[0];
      d[idx+1] = c[1];
      d[idx+2] = c[2];
      d[idx+3] = 255;
    }
    ctx.putImageData(imgData, 0, 0);
  }

  // Build territory overlay canvas (called whenever territory changes significantly)
  buildTerritoryOverlay(territory, terrain, tribes, size, eraIndex) {
    this.territoryCanvas = document.createElement('canvas');
    this.territoryCanvas.width = size;
    this.territoryCanvas.height = size;
    const ctx = this.territoryCanvas.getContext('2d');
    const imgData = ctx.createImageData(size, size);
    const d = imgData.data;

    // Parse tribe colors
    const tribeColorMap = {};
    for (const t of tribes) {
      if (!t.alive) continue;
      const hex = t.color;
      tribeColorMap[t.id] = [
        parseInt(hex.slice(1,3), 16),
        parseInt(hex.slice(3,5), 16),
        parseInt(hex.slice(5,7), 16),
      ];
    }

    // Era overlay
    const eraOverlay = CivSim.ERA_OVERLAYS[Math.min(eraIndex, CivSim.ERA_OVERLAYS.length - 1)];

    // Territory alpha: stronger in later eras
    const baseAlpha = 0.25 + eraIndex * 0.04;

    for (let i = 0; i < size * size; i++) {
      const ownerId = territory[i];
      const idx = i * 4;
      if (ownerId < 0 || !tribeColorMap[ownerId]) {
        // Era tint on unclaimed land (but not ocean)
        if (terrain[i] > CivSim.TERRAIN.SHALLOW && eraOverlay.a > 0) {
          d[idx]   = 128;
          d[idx+1] = 128;
          d[idx+2] = 128;
          d[idx+3] = Math.floor(eraOverlay.a * 40);
        } else {
          d[idx+3] = 0;
        }
        continue;
      }

      const c = tribeColorMap[ownerId];

      // Era color shift
      let r = c[0], g = c[1], b = c[2];
      if (eraOverlay.r !== 0) r = Math.max(0, Math.min(255, r + eraOverlay.r));
      if (eraOverlay.g !== 0) g = Math.max(0, Math.min(255, g + eraOverlay.g));
      if (eraOverlay.b !== 0) b = Math.max(0, Math.min(255, b + eraOverlay.b));

      // Desaturate in industrial/modern eras (idx 6-7)
      if (eraIndex >= 6) {
        const gray = (r + g + b) / 3;
        const desat = Math.min(0.4, (eraIndex - 5) * 0.15);
        r = Math.floor(r * (1 - desat) + gray * desat);
        g = Math.floor(g * (1 - desat) + gray * desat);
        b = Math.floor(b * (1 - desat) + gray * desat);
      }

      // Brighten in space age
      if (eraIndex >= 8) {
        r = Math.min(255, r + 15);
        g = Math.min(255, g + 15);
        b = Math.min(255, b + 15);
      }

      d[idx]   = r;
      d[idx+1] = g;
      d[idx+2] = b;
      d[idx+3] = Math.floor(baseAlpha * 255);
    }

    ctx.putImageData(imgData, 0, 0);
  }

  centerCamera(size) {
    const zoom = 3;
    this.camera.zoom = zoom;
    this.camera.x = (size - this._displayWidth / zoom) / 2;
    this.camera.y = (size - this._displayHeight / zoom) / 2;
    this._clampCamera(size);
  }

  _clampCamera(size) {
    const maxX = size - this._displayWidth / this.camera.zoom;
    const maxY = size - this._displayHeight / this.camera.zoom;
    this.camera.x = Math.max(-this._displayWidth * 0.3, Math.min(maxX + this._displayWidth * 0.3, this.camera.x));
    this.camera.y = Math.max(-this._displayHeight * 0.3, Math.min(maxY + this._displayHeight * 0.3, this.camera.y));
  }

  updateState(state) {
    this.tribes = state.tribes;
    this.selectedId = state.selectedId;
    this.eraIndex = state.eraIndex || 0;
  }

  render(size) {
    const ctx = this.ctx;
    const w = this._displayWidth;
    const h = this._displayHeight;

    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(0, 0, w, h);

    if (!this.terrainCanvas) return;

    ctx.save();
    ctx.imageSmoothingEnabled = this.camera.zoom < 2;
    ctx.scale(this.camera.zoom, this.camera.zoom);
    ctx.translate(-this.camera.x, -this.camera.y);

    // Draw terrain
    ctx.drawImage(this.terrainCanvas, 0, 0);

    // Draw territory overlay
    if (this.territoryCanvas) {
      ctx.drawImage(this.territoryCanvas, 0, 0);
    }

    // Draw territory borders for selected tribe (if zoomed enough)
    if (this.camera.zoom >= 2) {
      for (const t of this.tribes) {
        if (!t.alive) continue;
        this._drawTerritoryBorder(ctx, t, size);
      }
    }

    // Draw roads/networks in industrial+ era
    if (this.eraIndex >= 6 && this.camera.zoom >= 1.5) {
      this._drawRoads(ctx, size);
    }

    // Draw sea routes in modern+ era
    if (this.eraIndex >= 7 && this.camera.zoom >= 1.5) {
      this._drawSeaRoutes(ctx, size);
    }

    // Draw building icons on territory
    if (this.camera.zoom >= 3) {
      for (const t of this.tribes) {
        if (!t.alive) continue;
        this._drawBuildings(ctx, t);
      }
    }

    ctx.restore();

    // Draw tribe markers in screen space
    for (const t of this.tribes) {
      if (!t.alive) continue;
      const sx = (t.x - this.camera.x) * this.camera.zoom;
      const sy = (t.y - this.camera.y) * this.camera.zoom;
      if (sx < -30 || sy < -30 || sx > w + 30 || sy > h + 30) continue;

      const baseR = Math.max(6, Math.min(20, Math.sqrt(t.population) * 0.28));
      const isSelected = t.id === this.selectedId;
      const isHovered = t.id === this.hoveredId;

      // Glow for selected
      if (isSelected) {
        ctx.beginPath();
        ctx.arc(sx, sy, baseR + 7, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(196,154,60,0.35)';
        ctx.fill();
        ctx.strokeStyle = '#c49a3c';
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      // Settlement level affects marker style
      if (t.settlementLevel >= 3) {
        // City: diamond shape
        ctx.save();
        ctx.translate(sx, sy);
        ctx.rotate(Math.PI / 4);
        ctx.beginPath();
        ctx.rect(-baseR * 0.7, -baseR * 0.7, baseR * 1.4, baseR * 1.4);
        ctx.fillStyle = t.color;
        ctx.fill();
        ctx.strokeStyle = isSelected ? '#c49a3c' : (isHovered ? '#fff' : 'rgba(255,255,255,0.7)');
        ctx.lineWidth = isSelected ? 2.5 : 1.5;
        ctx.stroke();
        ctx.restore();
      } else if (t.settlementLevel >= 2) {
        // Town: square
        ctx.beginPath();
        ctx.rect(sx - baseR * 0.7, sy - baseR * 0.7, baseR * 1.4, baseR * 1.4);
        ctx.fillStyle = t.color;
        ctx.fill();
        ctx.strokeStyle = isSelected ? '#c49a3c' : (isHovered ? '#fff' : 'rgba(255,255,255,0.7)');
        ctx.lineWidth = isSelected ? 2.5 : 1.5;
        ctx.stroke();
      } else {
        // Village/Tribe: circle
        ctx.beginPath();
        ctx.arc(sx, sy, baseR, 0, Math.PI * 2);
        ctx.fillStyle = t.color;
        ctx.fill();
        ctx.strokeStyle = isSelected ? '#c49a3c' : (isHovered ? '#fff' : 'rgba(255,255,255,0.7)');
        ctx.lineWidth = isSelected ? 2.5 : 1.5;
        ctx.stroke();
      }

      // Population text
      if (this.camera.zoom >= 2.5 && baseR > 8) {
        ctx.fillStyle = '#fff';
        ctx.font = `bold ${Math.max(8, baseR * 0.7)|0}px 'DM Mono', monospace`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(this._formatPop(t.population), sx, sy);
      }

      // Name label with settlement level indicator
      if (this.camera.zoom >= 2) {
        ctx.fillStyle = 'rgba(255,255,255,0.85)';
        ctx.font = `${Math.max(8, 10)|0}px 'DM Mono', monospace`;
        ctx.textAlign = 'center';
        const levelIcon = ['🏠','🏘️','🏙️','🏛️','🌟'][t.settlementLevel] || '';
        ctx.fillText(`${levelIcon} ${t.name}`, sx, sy + baseR + 12);
      }
    }

    // Era name overlay on map
    this._drawEraOverlay(ctx, w, h);

    // Minimap
    this._drawMinimap(size);
  }

  _drawTerritoryBorder(ctx, tribe, size) {
    // Only draw for selected or nearby tribes
    const isSelected = tribe.id === this.selectedId;
    if (!isSelected && this.camera.zoom < 4) return; // Only selected at low zoom

    // We need access to simulation territory - we'll skip direct drawing
    // and rely on the overlay canvas instead for performance
  }

  _drawRoads(ctx, size) {
    // Draw lines between nearby tribes that are in industrial+ era
    const alive = this.tribes.filter(t => t.alive && t.settlementLevel >= 2);
    ctx.strokeStyle = 'rgba(180,170,150,0.3)';
    ctx.lineWidth = 0.5;
    for (let i = 0; i < alive.length; i++) {
      for (let j = i + 1; j < alive.length; j++) {
        const a = alive[i], b = alive[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        if (dist > 40) continue;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        // Slight curve for visual interest
        const mx = (a.x + b.x) / 2 + (Math.random() - 0.5) * 3;
        const my = (a.y + b.y) / 2 + (Math.random() - 0.5) * 3;
        ctx.quadraticCurveTo(mx, my, b.x, b.y);
        ctx.stroke();
      }
    }
  }

  _drawSeaRoutes(ctx, size) {
    // Draw dotted lines between coastal tribes in modern+ era
    const coastal = this.tribes.filter(t => t.alive && t.settlementLevel >= 2);
    ctx.strokeStyle = 'rgba(100,180,220,0.25)';
    ctx.lineWidth = 0.5;
    ctx.setLineDash([2, 3]);
    for (let i = 0; i < coastal.length; i++) {
      for (let j = i + 1; j < coastal.length; j++) {
        const a = coastal[i], b = coastal[j];
        const dist = Math.sqrt((a.x-b.x)**2 + (a.y-b.y)**2);
        if (dist < 20 || dist > 60) continue;
        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.stroke();
      }
    }
    ctx.setLineDash([]);
  }

  _drawBuildings(ctx, tribe) {
    if (!tribe.buildings) return;
    // Show building summary near the tribe marker
    const b = tribe.buildings;
    const totalBuildings = Object.values(b).reduce((a, c) => a + c, 0);
    if (totalBuildings === 0) return;

    // Draw small building count badges
    let bx = tribe.x + 3;
    const by = tribe.y - 3;
    const icons = ['🌾','⛏️','⚔️','📚','🏪','🏰'];
    const keys = ['farm','mine','barracks','academy','market','wall'];
    const fs = Math.max(3, 5 / this.camera.zoom);

    ctx.font = `${fs}px sans-serif`;
    ctx.textAlign = 'left';
    ctx.textBaseline = 'bottom';

    for (let i = 0; i < keys.length; i++) {
      if (b[keys[i]] > 0) {
        ctx.fillText(icons[i], bx, by);
        bx += fs + 1;
        if (bx > tribe.x + 20) break;
      }
    }
  }

  _drawEraOverlay(ctx, w, h) {
    const eraName = CivSim.ERAS[this.eraIndex]?.name || '石器时代';
    ctx.fillStyle = 'rgba(44,62,80,0.7)';
    ctx.fillRect(w / 2 - 60, 8, 120, 28);
    ctx.strokeStyle = 'rgba(196,154,60,0.5)';
    ctx.lineWidth = 1;
    ctx.strokeRect(w / 2 - 60, 8, 120, 28);
    ctx.fillStyle = 'rgba(255,255,255,0.9)';
    ctx.font = "11px 'DM Mono', monospace";
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(eraName, w / 2, 22);
  }

  _drawMinimap(size) {
    if (!this.terrainCanvas) return;
    const ctx = this.ctx;
    const mmSize = 120;
    const margin = 12;
    const mx = margin;
    const my = this._displayHeight - mmSize - margin;

    // Background
    ctx.fillStyle = 'rgba(44,62,80,0.85)';
    ctx.fillRect(mx - 2, my - 2, mmSize + 4, mmSize + 4);
    ctx.strokeStyle = 'rgba(160,149,133,0.4)';
    ctx.lineWidth = 1;
    ctx.strokeRect(mx - 2, my - 2, mmSize + 4, mmSize + 4);

    // Terrain
    ctx.imageSmoothingEnabled = true;
    ctx.drawImage(this.terrainCanvas, 0, 0, size, size, mx, my, mmSize, mmSize);

    // Territory overlay on minimap
    if (this.territoryCanvas) {
      ctx.globalAlpha = 0.5;
      ctx.drawImage(this.territoryCanvas, 0, 0, size, size, mx, my, mmSize, mmSize);
      ctx.globalAlpha = 1;
    }

    // Tribe dots (sized by population)
    for (const t of this.tribes) {
      if (!t.alive) continue;
      const r = Math.max(1.5, Math.min(4, Math.sqrt(t.population) * 0.05));
      ctx.beginPath();
      ctx.arc(mx + t.x / size * mmSize, my + t.y / size * mmSize, r, 0, Math.PI * 2);
      ctx.fillStyle = t.color;
      ctx.fill();
    }

    // Viewport rectangle
    const vx = mx + this.camera.x / size * mmSize;
    const vy = my + this.camera.y / size * mmSize;
    const vw = this._displayWidth / this.camera.zoom / size * mmSize;
    const vh = this._displayHeight / this.camera.zoom / size * mmSize;
    ctx.strokeStyle = '#c49a3c';
    ctx.lineWidth = 1.5;
    ctx.strokeRect(vx, vy, vw, vh);
  }

  hitTest(screenX, screenY) {
    const wx = screenX / this.camera.zoom + this.camera.x;
    const wy = screenY / this.camera.zoom + this.camera.y;
    let bestId = -1, bestDist = Infinity;
    for (const t of this.tribes) {
      if (!t.alive) continue;
      const dx = wx - t.x, dy = wy - t.y;
      const d = Math.sqrt(dx*dx + dy*dy);
      const hitR = Math.max(6, Math.min(20, Math.sqrt(t.population) * 0.28)) / this.camera.zoom + 3 / this.camera.zoom;
      if (d < hitR && d < bestDist) {
        bestDist = d;
        bestId = t.id;
      }
    }
    return bestId;
  }

  _formatPop(n) {
    if (n >= 10000) return (n/1000).toFixed(0) + 'k';
    if (n >= 1000) return (n/1000).toFixed(1) + 'k';
    return (n|0) + '';
  }

  _bindEvents() {
    const c = this.canvas;

    c.addEventListener('mousedown', e => {
      this._dragging = true;
      this._dragStart = { x: e.clientX, y: e.clientY };
      this._camStart = { x: this.camera.x, y: this.camera.y };
    });
    window.addEventListener('mousemove', e => {
      if (this._dragging) {
        const dx = e.clientX - this._dragStart.x;
        const dy = e.clientY - this._dragStart.y;
        this.camera.x = this._camStart.x - dx / this.camera.zoom;
        this.camera.y = this._camStart.y - dy / this.camera.zoom;
        this._clampCamera(CivSim.WORLD_SIZE);
      } else {
        const rect = c.getBoundingClientRect();
        const sx = e.clientX - rect.left;
        const sy = e.clientY - rect.top;
        this.hoveredId = this.hitTest(sx, sy);
        c.style.cursor = this.hoveredId >= 0 ? 'pointer' : 'grab';
      }
    });
    window.addEventListener('mouseup', e => {
      if (!this._dragging) return;
      const dx = e.clientX - this._dragStart.x;
      const dy = e.clientY - this._dragStart.y;
      this._dragging = false;
      if (Math.abs(dx) < 5 && Math.abs(dy) < 5) {
        const rect = c.getBoundingClientRect();
        const sx = e.clientX - rect.left;
        const sy = e.clientY - rect.top;
        const id = this.hitTest(sx, sy);
        if (id >= 0 && this.onClick) this.onClick(id);
      }
      c.style.cursor = 'grab';
    });

    c.addEventListener('wheel', e => {
      e.preventDefault();
      const rect = c.getBoundingClientRect();
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const wx = mx / this.camera.zoom + this.camera.x;
      const wy = my / this.camera.zoom + this.camera.y;
      const factor = e.deltaY > 0 ? 0.9 : 1.1;
      this.camera.zoom = Math.max(1, Math.min(12, this.camera.zoom * factor));
      this.camera.x = wx - mx / this.camera.zoom;
      this.camera.y = wy - my / this.camera.zoom;
      this._clampCamera(CivSim.WORLD_SIZE);
    }, { passive: false });

    // Touch
    c.addEventListener('touchstart', e => {
      e.preventDefault();
      if (e.touches.length === 1) {
        this._dragging = true;
        this._dragStart = { x: e.touches[0].clientX, y: e.touches[0].clientY };
        this._camStart = { x: this.camera.x, y: this.camera.y };
      } else if (e.touches.length === 2) {
        this._dragging = false;
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        this._pinchDist = Math.sqrt(dx*dx + dy*dy);
        this._camStart = { x: this.camera.x, y: this.camera.y, zoom: this.camera.zoom };
      }
    }, { passive: false });

    c.addEventListener('touchmove', e => {
      e.preventDefault();
      if (e.touches.length === 1 && this._dragging) {
        const dx = e.touches[0].clientX - this._dragStart.x;
        const dy = e.touches[0].clientY - this._dragStart.y;
        this.camera.x = this._camStart.x - dx / this.camera.zoom;
        this.camera.y = this._camStart.y - dy / this.camera.zoom;
        this._clampCamera(CivSim.WORLD_SIZE);
      } else if (e.touches.length === 2) {
        const dx = e.touches[0].clientX - e.touches[1].clientX;
        const dy = e.touches[0].clientY - e.touches[1].clientY;
        const dist = Math.sqrt(dx*dx + dy*dy);
        const cx = (e.touches[0].clientX + e.touches[1].clientX) / 2;
        const cy = (e.touches[0].clientY + e.touches[1].clientY) / 2;
        const rect = c.getBoundingClientRect();
        const mx = cx - rect.left;
        const my = cy - rect.top;
        const wx = mx / this._camStart.zoom + this._camStart.x;
        const wy = my / this._camStart.zoom + this._camStart.y;
        const scale = dist / Math.max(1, this._pinchDist);
        this.camera.zoom = Math.max(1, Math.min(12, this._camStart.zoom * scale));
        this.camera.x = wx - mx / this.camera.zoom;
        this.camera.y = wy - my / this.camera.zoom;
        this._clampCamera(CivSim.WORLD_SIZE);
      }
    }, { passive: false });

    c.addEventListener('touchend', e => {
      if (e.changedTouches.length === 1 && this._dragging) {
        const t = e.changedTouches[0];
        const dx = t.clientX - this._dragStart.x;
        const dy = t.clientY - this._dragStart.y;
        this._dragging = false;
        if (Math.abs(dx) < 10 && Math.abs(dy) < 10) {
          const rect = c.getBoundingClientRect();
          const sx = t.clientX - rect.left;
          const sy = t.clientY - rect.top;
          const id = this.hitTest(sx, sy);
          if (id >= 0 && this.onClick) this.onClick(id);
        }
      }
      this._dragging = false;
    });

    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => this._resize(), 100);
    });
  }
}

return { Renderer };
})();
