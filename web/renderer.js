// renderer.js — Canvas Renderer for Civilization Sim
const CivRenderer = (() => {
'use strict';

class Renderer {
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx = canvas.getContext('2d');
    this.terrainCanvas = null; // offscreen
    this.camera = { x: 0, y: 0, zoom: 3 };
    this.selectedId = -1;
    this.tribes = [];
    this.hoveredId = -1;
    this._dragging = false;
    this._dragStart = { x: 0, y: 0 };
    this._camStart = { x: 0, y: 0 };
    this._pinchDist = 0;
    this.onClick = null; // callback(id)
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

  centerCamera(size) {
    const zoom = 3;
    this.camera.zoom = zoom;
    this.camera.x = (size - this._displayWidth / zoom) / 2;
    this.camera.y = (size - this._displayHeight / zoom) / 2;
    // Clamp
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
  }

  render(size) {
    const ctx = this.ctx;
    const w = this._displayWidth;
    const h = this._displayHeight;

    // Background
    ctx.fillStyle = '#2c3e50';
    ctx.fillRect(0, 0, w, h);

    if (!this.terrainCanvas) return;

    ctx.save();
    ctx.imageSmoothingEnabled = this.camera.zoom < 2;
    ctx.scale(this.camera.zoom, this.camera.zoom);
    ctx.translate(-this.camera.x, -this.camera.y);

    // Draw terrain
    ctx.drawImage(this.terrainCanvas, 0, 0);

    // Draw tribe influence circles
    for (const t of this.tribes) {
      if (!t.alive) continue;
      const r = Math.min(Math.ceil(Math.sqrt(t.population) * 0.5), 20);
      ctx.beginPath();
      ctx.arc(t.x, t.y, r, 0, Math.PI * 2);
      ctx.fillStyle = t.color + '15';
      ctx.fill();
      ctx.strokeStyle = t.color + '40';
      ctx.lineWidth = 0.5 / this.camera.zoom;
      ctx.stroke();
    }

    ctx.restore();

    // Draw tribe markers in screen space
    for (const t of this.tribes) {
      if (!t.alive) continue;
      const sx = (t.x - this.camera.x) * this.camera.zoom;
      const sy = (t.y - this.camera.y) * this.camera.zoom;
      if (sx < -20 || sy < -20 || sx > w + 20 || sy > h + 20) continue;

      const baseR = Math.max(5, Math.min(16, Math.sqrt(t.population) * 0.25));
      const isSelected = t.id === this.selectedId;
      const isHovered = t.id === this.hoveredId;

      // Glow for selected
      if (isSelected) {
        ctx.beginPath();
        ctx.arc(sx, sy, baseR + 6, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(196,154,60,0.3)';
        ctx.fill();
        ctx.strokeStyle = '#c49a3c';
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      // Marker
      ctx.beginPath();
      ctx.arc(sx, sy, baseR, 0, Math.PI * 2);
      ctx.fillStyle = t.color;
      ctx.fill();
      ctx.strokeStyle = isSelected ? '#c49a3c' : (isHovered ? '#fff' : 'rgba(255,255,255,0.7)');
      ctx.lineWidth = isSelected ? 2.5 : 1.5;
      ctx.stroke();

      // Population text
      if (this.camera.zoom >= 2.5 && baseR > 7) {
        ctx.fillStyle = '#fff';
        ctx.font = `bold ${Math.max(8, baseR * 0.8)|0}px 'DM Mono', monospace`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(t.population < 1000 ? (t.population|0) + '' : (t.population/1000).toFixed(1) + 'k', sx, sy);
      }

      // Name label
      if (this.camera.zoom >= 2) {
        ctx.fillStyle = 'rgba(255,255,255,0.85)';
        ctx.font = `${Math.max(8, 10)|0}px 'DM Mono', monospace`;
        ctx.textAlign = 'center';
        ctx.fillText(t.name, sx, sy + baseR + 10);
      }
    }

    // Minimap
    this._drawMinimap(size);
  }

  _drawMinimap(size) {
    if (!this.terrainCanvas) return;
    const ctx = this.ctx;
    const mmSize = 110;
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

    // Tribe dots
    for (const t of this.tribes) {
      if (!t.alive) continue;
      ctx.beginPath();
      ctx.arc(mx + t.x / size * mmSize, my + t.y / size * mmSize, 2.5, 0, Math.PI * 2);
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
      const hitR = Math.max(5, Math.min(16, Math.sqrt(t.population) * 0.25)) / this.camera.zoom + 3 / this.camera.zoom;
      if (d < hitR && d < bestDist) {
        bestDist = d;
        bestId = t.id;
      }
    }
    return bestId;
  }

  _bindEvents() {
    const c = this.canvas;

    // Mouse
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

    // Wheel zoom
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
    let touches0 = null;
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
      if (e.changedTouches.length === 1 && this._dragging && touches0 === null) {
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

    // Resize
    let resizeTimer;
    window.addEventListener('resize', () => {
      clearTimeout(resizeTimer);
      resizeTimer = setTimeout(() => this._resize(), 100);
    });
  }
}

return { Renderer };
})();
