// engine.js — Civilization Simulation Engine
const CivSim = (() => {
'use strict';

// ════════════════════ SIMPLEX 2D NOISE ════════════════════
class SimplexNoise {
  constructor(seed) {
    this.perm = new Uint8Array(512);
    const p = new Uint8Array(256);
    for (let i = 0; i < 256; i++) p[i] = i;
    let s = seed | 0 || 1;
    for (let i = 255; i > 0; i--) {
      s = (s * 16807 + 1) & 0x7fffffff;
      const j = s % (i + 1);
      const tmp = p[i]; p[i] = p[j]; p[j] = tmp;
    }
    for (let i = 0; i < 512; i++) this.perm[i] = p[i & 255];
  }
  noise2D(x, y) {
    const F2 = 0.5 * (Math.sqrt(3) - 1);
    const G2 = (3 - Math.sqrt(3)) / 6;
    const s = (x + y) * F2;
    const i = Math.floor(x + s), j = Math.floor(y + s);
    const t = (i + j) * G2;
    const x0 = x - (i - t), y0 = y - (j - t);
    const i1 = x0 > y0 ? 1 : 0, j1 = x0 > y0 ? 0 : 1;
    const x1 = x0 - i1 + G2, y1 = y0 - j1 + G2;
    const x2 = x0 - 1 + 2 * G2, y2 = y0 - 1 + 2 * G2;
    const ii = i & 255, jj = j & 255;
    const grad3 = [[1,1],[-1,1],[1,-1],[-1,-1],[1,0],[-1,0],[0,1],[0,-1]];
    let n0 = 0, n1 = 0, n2 = 0;
    let t0 = 0.5 - x0*x0 - y0*y0;
    if (t0 > 0) { const gi = this.perm[ii + this.perm[jj]] % 8; t0 *= t0; n0 = t0 * t0 * (grad3[gi][0]*x0 + grad3[gi][1]*y0); }
    let t1 = 0.5 - x1*x1 - y1*y1;
    if (t1 > 0) { const gi = this.perm[ii + i1 + this.perm[jj + j1]] % 8; t1 *= t1; n1 = t1 * t1 * (grad3[gi][0]*x1 + grad3[gi][1]*y1); }
    let t2 = 0.5 - x2*x2 - y2*y2;
    if (t2 > 0) { const gi = this.perm[ii + 1 + this.perm[jj + 1]] % 8; t2 *= t2; n2 = t2 * t2 * (grad3[gi][0]*x2 + grad3[gi][1]*y2); }
    return 70 * (n0 + n1 + n2);
  }
}

// ════════════════════ CONSTANTS ════════════════════
const WORLD_SIZE = 200;
const TERRAIN = { OCEAN: 0, SHALLOW: 1, BEACH: 2, PLAINS: 3, FOREST: 4, HILLS: 5, MOUNTAIN: 6, SNOW: 7 };

const TERRAIN_RESOURCES = [
  { food: 0,    wood: 0,    stone: 0,   iron: 0   }, // OCEAN
  { food: 0.8,  wood: 0,    stone: 0,   iron: 0   }, // SHALLOW
  { food: 0.3,  wood: 0.1,  stone: 0,   iron: 0   }, // BEACH
  { food: 1.0,  wood: 0.2,  stone: 0.1, iron: 0   }, // PLAINS
  { food: 0.4,  wood: 0.8,  stone: 0.05,iron: 0   }, // FOREST
  { food: 0.3,  wood: 0.3,  stone: 0.6, iron: 0.1  }, // HILLS
  { food: 0.1,  wood: 0.1,  stone: 0.5, iron: 0.4  }, // MOUNTAIN
  { food: 0.05, wood: 0,    stone: 0.2, iron: 0.1  }, // SNOW
];

const TERRAIN_COLORS = [
  '#3d7ea6', // OCEAN
  '#6aafc7', // SHALLOW
  '#c9b97a', // BEACH
  '#7a9e57', // PLAINS
  '#4a7345', // FOREST
  '#8b7d6b', // HILLS
  '#6b6156', // MOUNTAIN
  '#d4cfc5', // SNOW
];

const TECH_TREE = [
  { id: 'toolmaking', name: '工具制造',   prereqs: [],                     scholars: 2,  ticks: 80  },
  { id: 'archery',    name: '弓箭',       prereqs: ['toolmaking'],        scholars: 3,  ticks: 70  },
  { id: 'agriculture',name: '农业',       prereqs: ['toolmaking'],        scholars: 5,  ticks: 150 },
  { id: 'pottery',    name: '陶器',       prereqs: ['agriculture'],       scholars: 5,  ticks: 120 },
  { id: 'metallurgy', name: '冶金',       prereqs: ['pottery'],           scholars: 8,  ticks: 250 },
  { id: 'writing',    name: '文字',       prereqs: ['agriculture'],       scholars: 10, ticks: 200 },
  { id: 'masonry',    name: '建筑术',     prereqs: ['metallurgy'],        scholars: 8,  ticks: 180 },
  { id: 'navigation', name: '航海术',     prereqs: ['writing'],           scholars: 12, ticks: 350 },
  { id: 'gunpowder',  name: '火药',       prereqs: ['metallurgy','writing'], scholars: 15, ticks: 500 },
  { id: 'printing',   name: '印刷术',     prereqs: ['gunpowder'],         scholars: 15, ticks: 400 },
  { id: 'industry',   name: '工业革命',   prereqs: ['gunpowder','navigation'], scholars: 20, ticks: 700 },
  { id: 'electricity',name: '电力',       prereqs: ['industry'],          scholars: 25, ticks: 900 },
  { id: 'flight',     name: '航空',       prereqs: ['electricity'],       scholars: 25, ticks: 800 },
  { id: 'computing',  name: '计算机',     prereqs: ['electricity'],       scholars: 30, ticks: 1000},
  { id: 'space',      name: '太空探索',   prereqs: ['computing','flight'], scholars: 40, ticks: 1500},
];

const TRIBE_NAMES = [
  '炎帝','黄帝','蚩尤','共工','伏羲','女娲','神农','少昊',
  '颛顼','帝喾','鲧','禹','羿','后稷','契','伯益',
  '皋陶','苍舒','隤敳','梼戭','大临','庭坚','仲容','叔达',
];

const TRIBE_COLORS = [
  '#e74c3c','#3498db','#27ae60','#f39c12',
  '#8e44ad','#1abc9c','#e67e22','#e91e63',
  '#00bcd4','#7cb342','#ff5722','#5c6bc0',
  '#26a69a','#ef5350','#66bb6a','#ffa726',
];

const ERAS = [
  { name: '石器时代', maxTech: 0 },
  { name: '原始时代', maxTech: 1 },
  { name: '青铜时代', maxTech: 3 },
  { name: '古典时代', maxTech: 5 },
  { name: '中世纪',   maxTech: 7 },
  { name: '文艺复兴', maxTech: 9 },
  { name: '工业时代', maxTech: 11 },
  { name: '现代',     maxTech: 13 },
  { name: '太空时代', maxTech: 999 },
];

// Simulation parameters
const FOOD_PER_POP      = 0.012;
const PROD_SCALE        = 0.015;
const GROWTH_BASE       = 0.0025;
const GROWTH_SURPLUS    = 0.003;
const GROWTH_DEFICIT    = -0.005;
const MIN_POP           = 5;
const TICKS_PER_YEAR    = 100;

// ════════════════════ WORLD GENERATION ════════════════════
function generateTerrain(size, seed) {
  const elev = new SimplexNoise(seed);
  const moist = new SimplexNoise(seed + 7777);
  const terrain = new Uint8Array(size * size);

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      // Multi-octave elevation
      let e = 0, amp = 1, freq = 1, maxAmp = 0;
      for (let oct = 0; oct < 6; oct++) {
        e += elev.noise2D(x * freq / size * 4, y * freq / size * 4) * amp;
        maxAmp += amp;
        amp *= 0.5;
        freq *= 2;
      }
      e = (e / maxAmp + 1) * 0.5; // [0,1]

      // Edge falloff (island shape)
      const cx = x / size - 0.5, cy = y / size - 0.5;
      const edgeDist = 1 - Math.sqrt(cx*cx + cy*cy) * 2.2;
      e = e * Math.max(0, Math.min(1, edgeDist + 0.3));

      // Moisture
      const m = (moist.noise2D(x / size * 3, y / size * 3) + 1) * 0.5;

      // Classify
      let t;
      if (e < 0.32)       t = TERRAIN.OCEAN;
      else if (e < 0.38)  t = TERRAIN.SHALLOW;
      else if (e < 0.41)  t = TERRAIN.BEACH;
      else if (e < 0.62)  t = m > 0.55 ? TERRAIN.FOREST : TERRAIN.PLAINS;
      else if (e < 0.76)  t = m > 0.50 ? TERRAIN.FOREST : TERRAIN.HILLS;
      else if (e < 0.86)  t = TERRAIN.MOUNTAIN;
      else                 t = TERRAIN.SNOW;

      terrain[y * size + x] = t;
    }
  }
  return terrain;
}

// ════════════════════ TRIBE ════════════════════
class Tribe {
  constructor(id, name, x, y, color) {
    this.id = id;
    this.name = name;
    this.x = x;
    this.y = y;
    this.color = color;
    this.population = 60 + Math.random() * 80;
    this.food = 100 + Math.random() * 50;
    this.wood = 30;
    this.stone = 10;
    this.iron = 0;
    this.techs = new Set();
    this.researching = null;
    this.researchProgress = 0;
    this.alive = true;
    this.influenceRadius = 6; // visual only
  }

  hasTech(id)   { return this.techs.has(id); }
  techCount()   { return this.techs.size; }

  getFoodMultiplier() {
    let m = 1;
    if (this.hasTech('toolmaking'))  m += 0.4;
    if (this.hasTech('archery'))     m += 0.6;
    if (this.hasTech('agriculture')) m += 1.2;
    return m;
  }

  getMineMultiplier() {
    let m = 1;
    if (this.hasTech('metallurgy')) m += 1.0;
    if (this.hasTech('industry'))   m += 1.0;
    return m;
  }

  getResearchMultiplier() {
    let m = 1;
    if (this.hasTech('writing'))    m += 1.0;
    if (this.hasTech('printing'))   m += 0.5;
    if (this.hasTech('computing'))  m += 2.0;
    return m;
  }

  canResearch(techId) {
    if (this.techs.has(techId)) return false;
    const tech = TECH_TREE.find(t => t.id === techId);
    return tech && tech.prereqs.every(p => this.techs.has(p));
  }

  autoSelectResearch() {
    const available = TECH_TREE.filter(t => this.canResearch(t.id));
    if (available.length === 0) { this.researching = null; return; }
    // Prefer earlier techs but with randomness
    const weights = available.map((t, i) => 1 / (i + 1) + Math.random() * 0.5);
    const total = weights.reduce((a, b) => a + b, 0);
    let r = Math.random() * total;
    for (let i = 0; i < available.length; i++) {
      r -= weights[i];
      if (r <= 0) {
        this.researching = available[i].id;
        this.researchProgress = 0;
        return;
      }
    }
    this.researching = available[0].id;
    this.researchProgress = 0;
  }
}

// ════════════════════ SIMULATION ════════════════════
class Simulation {
  constructor() {
    this.terrain = null;
    this.tribes = [];
    this.year = 1;
    this.tickCount = 0;
    this.events = [];
    this.selectedId = -1;
    this.eventCallbacks = [];
    this.stateCallbacks = [];
  }

  newWorld(seed) {
    seed = seed || (Math.random() * 999999) | 0;
    this.terrain = generateTerrain(WORLD_SIZE, seed);
    this.tribes = this._placeTribes(10 + ((seed % 5) | 0));
    this.year = 1;
    this.tickCount = 0;
    this.events = [];
    this.selectedId = this.tribes.length > 0 ? this.tribes[0].id : -1;
    this._emitEvent({ type: 'system', text: `新世界诞生，种子 #${seed}`, year: 1 });
    this._emitState();
  }

  _placeTribes(count) {
    const candidates = [];
    for (let y = 5; y < WORLD_SIZE - 5; y++) {
      for (let x = 5; x < WORLD_SIZE - 5; x++) {
        const t = this.terrain[y * WORLD_SIZE + x];
        if (t >= TERRAIN.PLAINS && t <= TERRAIN.HILLS) {
          candidates.push({ x, y, score: TERRAIN_RESOURCES[t].food + (t === TERRAIN.PLAINS ? 0.3 : 0) });
        }
      }
    }
    // Fisher-Yates shuffle
    for (let i = candidates.length - 1; i > 0; i--) {
      const j = (Math.random() * (i + 1)) | 0;
      const tmp = candidates[i]; candidates[i] = candidates[j]; candidates[j] = tmp;
    }

    const tribes = [];
    const used = new Set();
    for (const c of candidates) {
      if (tribes.length >= count) break;
      // Ensure minimum separation
      let tooClose = false;
      for (const t of tribes) {
        if (Math.abs(c.x - t.x) + Math.abs(c.y - t.y) < 25) { tooClose = true; break; }
      }
      if (tooClose) continue;
      const id = tribes.length;
      tribes.push(new Tribe(id, TRIBE_NAMES[id % TRIBE_NAMES.length], c.x, c.y, TRIBE_COLORS[id % TRIBE_COLORS.length]));
      tribes[tribes.length - 1].autoSelectResearch();
    }
    return tribes;
  }

  tick() {
    this.tickCount++;
    if (this.tickCount % TICKS_PER_YEAR === 0) this.year++;

    for (const tribe of this.tribes) {
      if (!tribe.alive) continue;
      this._updateTribe(tribe);
    }

    this._processInteractions();

    // Random events every ~50 ticks
    if (this.tickCount % 50 === 0) this._randomEvent();

    // Remove dead tribes from selection
    if (this.selectedId >= 0) {
      const sel = this.tribes.find(t => t.id === this.selectedId);
      if (!sel || !sel.alive) {
        const alive = this.tribes.find(t => t.alive);
        this.selectedId = alive ? alive.id : -1;
      }
    }

    this._emitState();
  }

  _updateTribe(tribe) {
    const radius = Math.min(Math.ceil(Math.sqrt(tribe.population) * 0.5), 20);
    const r = Math.ceil(radius);
    let foodBase = 0, woodBase = 0, stoneBase = 0, ironBase = 0, cells = 0;

    for (let dy = -r; dy <= r; dy++) {
      for (let dx = -r; dx <= r; dx++) {
        if (dx*dx + dy*dy > radius*radius) continue;
        const wx = tribe.x + dx, wy = tribe.y + dy;
        if (wx < 0 || wx >= WORLD_SIZE || wy < 0 || wy >= WORLD_SIZE) continue;
        const t = this.terrain[wy * WORLD_SIZE + wx];
        if (t <= TERRAIN.SHALLOW) continue;
        const res = TERRAIN_RESOURCES[t];
        foodBase += res.food;
        woodBase += res.wood;
        stoneBase += res.stone;
        ironBase += res.iron;
        cells++;
      }
    }

    const eff = Math.min(tribe.population / 80, 1.5);
    tribe.food  += (foodBase  * eff * tribe.getFoodMultiplier() * PROD_SCALE) - tribe.population * FOOD_PER_POP;
    tribe.wood  += woodBase  * eff * PROD_SCALE;
    tribe.stone += stoneBase * eff * tribe.getMineMultiplier() * PROD_SCALE;
    tribe.iron  += ironBase  * eff * tribe.getMineMultiplier() * PROD_SCALE;

    // Resource caps
    tribe.food  = Math.min(tribe.food,  tribe.population * 6);
    tribe.wood  = Math.min(tribe.wood,  tribe.population * 4);
    tribe.stone = Math.min(tribe.stone, tribe.population * 3);
    tribe.iron  = Math.min(tribe.iron,  tribe.population * 2);

    // Population growth
    let gr = GROWTH_BASE;
    if (tribe.food > 10)  gr += GROWTH_SURPLUS;
    if (tribe.food < 0)   gr += GROWTH_DEFICIT;
    if (tribe.food < -10) gr += GROWTH_DEFICIT;

    const maxPop = cells * 5 * (1 + tribe.techCount() * 0.3);
    if (tribe.population > maxPop * 0.7 && maxPop > 0) {
      gr *= Math.max(0.1, (maxPop - tribe.population) / (maxPop * 0.3));
    }

    tribe.population += tribe.population * gr;

    // Starvation
    if (tribe.food < -20) {
      tribe.population *= 0.85;
      tribe.food = 0;
      this._emitEvent({ type: 'disaster', text: `${tribe.name} 遭遇严重饥荒！`, year: this.year });
    }

    tribe.population = Math.max(MIN_POP, tribe.population);

    // Research
    if (tribe.researching) {
      const tech = TECH_TREE.find(t => t.id === tribe.researching);
      if (tech) {
        const scholars = tribe.population * (0.04 + tribe.techCount() * 0.01);
        // Diminishing returns: rate approaches 1 asymptotically
        const baseRate = 1 - Math.exp(-scholars / (tech.scholars * 15));
        const rate = baseRate * tribe.getResearchMultiplier();
        tribe.researchProgress += rate;
        if (tribe.researchProgress >= tech.ticks) {
          tribe.techs.add(tech.id);
          tribe.researching = null;
          tribe.researchProgress = 0;
          this._emitEvent({ type: 'tech', text: `${tribe.name} 发明了「${tech.name}」！`, year: this.year });
          tribe.autoSelectResearch();
          // Victory check
          if (tech.id === 'space') {
            this._emitEvent({ type: 'victory', text: `🏆 ${tribe.name} 率先进入太空时代！文明胜利！`, year: this.year });
          }
        }
      }
    }

    // Death check
    if (tribe.population <= MIN_POP && tribe.food < 2) {
      tribe.alive = false;
      this._emitEvent({ type: 'extinction', text: `${tribe.name} 灭亡了。`, year: this.year });
    }
  }

  _processInteractions() {
    const alive = this.tribes.filter(t => t.alive);
    for (let i = 0; i < alive.length; i++) {
      for (let j = i + 1; j < alive.length; j++) {
        const a = alive[i], b = alive[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        const range = 20 + (a.hasTech('navigation') || b.hasTech('navigation') ? 10 : 0)
                         + (a.hasTech('flight') || b.hasTech('flight') ? 20 : 0);
        if (dist > range) continue;

        // Trade
        if (Math.random() < 0.03) {
          a.food += 0.3; b.food += 0.3;
          a.wood += 0.2; b.wood += 0.2;
        }

        // Cultural diffusion
        if (Math.random() < 0.005) {
          const src = Math.random() < 0.5 ? a : b;
          const tgt = src === a ? b : a;
          const spreadable = [...src.techs].filter(id => !tgt.hasTech(id));
          if (spreadable.length > 0) {
            const tid = spreadable[(Math.random() * spreadable.length) | 0];
            tgt.techs.add(tid);
            const tname = TECH_TREE.find(t => t.id === tid).name;
            this._emitEvent({ type: 'culture', text: `${tgt.name} 从 ${src.name} 学习了「${tname}」`, year: this.year });
          }
        }

        // War
        if (Math.random() < 0.004) {
          const aS = a.population * (1 + (a.hasTech('gunpowder') ? 1.5 : 0) + (a.hasTech('masonry') ? 0.5 : 0));
          const bS = b.population * (1 + (b.hasTech('gunpowder') ? 1.5 : 0) + (b.hasTech('masonry') ? 0.5 : 0));
          if (aS > bS * 1.4) {
            b.population *= 0.75;
            if (b.population < MIN_POP + 5) b.alive = false;
            this._emitEvent({ type: 'war', text: `${a.name} 击败了 ${b.name}！`, year: this.year });
          } else if (bS > aS * 1.4) {
            a.population *= 0.75;
            if (a.population < MIN_POP + 5) a.alive = false;
            this._emitEvent({ type: 'war', text: `${b.name} 击败了 ${a.name}！`, year: this.year });
          } else {
            a.population *= 0.9; b.population *= 0.9;
            this._emitEvent({ type: 'war', text: `${a.name} 与 ${b.name} 交战，两败俱伤`, year: this.year });
          }
        }

        // Merge
        if (Math.random() < 0.002) {
          const big = a.population > b.population ? a : b;
          const sml = a.population > b.population ? b : a;
          if (big.population > sml.population * 3 && sml.techCount() <= big.techCount()) {
            big.population += sml.population * 0.7;
            sml.alive = false;
            this._emitEvent({ type: 'merge', text: `${sml.name} 并入了 ${big.name}`, year: this.year });
          }
        }
      }
    }
  }

  _randomEvent() {
    const alive = this.tribes.filter(t => t.alive);
    if (alive.length === 0) return;
    const r = Math.random();
    if (r < 0.15) {
      const t = alive[(Math.random() * alive.length) | 0];
      const bonus = 10 + Math.random() * 30;
      t.food += bonus;
      this._emitEvent({ type: 'event', text: `${t.name} 发现了丰饶的猎场 (+${bonus|0} 食物)`, year: this.year });
    } else if (r < 0.25) {
      const t = alive[(Math.random() * alive.length) | 0];
      const loss = 5 + Math.random() * 15;
      t.population *= (1 - loss / 100);
      this._emitEvent({ type: 'disaster', text: `${t.name} 遭遇瘟疫 (人口 -${loss|0}%)`, year: this.year });
    } else if (r < 0.32) {
      const t = alive[(Math.random() * alive.length) | 0];
      t.population += 10 + Math.random() * 20;
      this._emitEvent({ type: 'event', text: `${t.name} 迎来了一批移民`, year: this.year });
    } else if (r < 0.37) {
      const t = alive[(Math.random() * alive.length) | 0];
      t.stone += 15 + Math.random() * 20;
      this._emitEvent({ type: 'event', text: `${t.name} 发现了富矿`, year: this.year });
    }
  }

  getEra() {
    const maxTech = Math.max(0, ...this.tribes.filter(t => t.alive).map(t => t.techCount()));
    for (const era of ERAS) {
      if (maxTech <= era.maxTech) return era.name;
    }
    return ERAS[ERAS.length - 1].name;
  }

  getTotalPop() {
    return this.tribes.filter(t => t.alive).reduce((s, t) => s + t.population, 0);
  }

  getAliveCount() {
    return this.tribes.filter(t => t.alive).length;
  }

  getSelected() {
    return this.tribes.find(t => t.id === this.selectedId && t.alive) || null;
  }

  selectTribe(id) {
    this.selectedId = id;
    this._emitState();
  }

  onEvent(cb)      { this.eventCallbacks.push(cb); }
  onStateChange(cb) { this.stateCallbacks.push(cb); }

  _emitEvent(evt) {
    this.events.unshift(evt);
    if (this.events.length > 200) this.events.length = 200;
    for (const cb of this.eventCallbacks) cb(evt);
  }

  _emitState() {
    const state = {
      year: this.year,
      tickCount: this.tickCount,
      era: this.getEra(),
      totalPop: this.getTotalPop(),
      aliveCount: this.getAliveCount(),
      tribes: this.tribes.map(t => ({
        id: t.id, name: t.name, x: t.x, y: t.y,
        population: t.population, alive: t.alive, color: t.color,
        food: t.food, wood: t.wood, stone: t.stone, iron: t.iron,
        techs: [...t.techs],
        researching: t.researching,
        researchProgress: t.researchProgress,
      })),
      selectedId: this.selectedId,
    };
    for (const cb of this.stateCallbacks) cb(state);
  }
}

return {
  SimplexNoise, WORLD_SIZE, TERRAIN, TERRAIN_COLORS,
  TERRAIN_RESOURCES, TECH_TREE, TRIBE_NAMES, TRIBE_COLORS, ERAS,
  TICKS_PER_YEAR, Simulation,
};
})();
