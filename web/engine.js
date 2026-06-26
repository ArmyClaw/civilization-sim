// engine.js — Civilization Simulation Engine (Enhanced)
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

// Terrain suitability for expansion (higher = easier to claim)
const TERRAIN_EXPAND_COST = [999, 999, 3, 1, 2, 4, 8, 999]; // ocean/shallow/snow = blocked

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

// Era color overlays (rgba for blending)
const ERA_OVERLAYS = [
  { r: 0,   g: 0,   b: 0,   a: 0    }, // 0: 石器时代 - no overlay
  { r: 0,   g: 0,   b: 0,   a: 0    }, // 1: 原始时代
  { r: 10,  g: -5,  b: -10, a: 0.06 }, // 2: 青铜时代 - slightly warmer
  { r: 5,   g: 0,   b: -10, a: 0.08 }, // 3: 古典时代 - borders clearer
  { r: -5,  g: -5,  b: 5,   a: 0.08 }, // 4: 中世纪 - cooler
  { r: 0,   g: 5,   b: -5,  a: 0.06 }, // 5: 文艺复兴
  { r: -15, g: -10, b: -15, a: 0.12 }, // 6: 工业时代 - grey/brown
  { r: -10, g: -10, b: -5,  a: 0.10 }, // 7: 现代 - desaturated
  { r: 5,   g: 0,   b: 10,  a: 0.08 }, // 8: 太空时代 - bluish bright
];

const TECH_TREE = [
  { id: 'toolmaking', name: '工具制造',   prereqs: [],                          scholars: 2,  ticks: 40  },
  { id: 'archery',    name: '弓箭',       prereqs: ['toolmaking'],              scholars: 3,  ticks: 35  },
  { id: 'agriculture',name: '农业',       prereqs: ['toolmaking'],              scholars: 5,  ticks: 60  },
  { id: 'pottery',    name: '陶器',       prereqs: ['agriculture'],             scholars: 5,  ticks: 50  },
  { id: 'metallurgy', name: '冶金',       prereqs: ['pottery'],                 scholars: 8,  ticks: 100 },
  { id: 'writing',    name: '文字',       prereqs: ['agriculture'],             scholars: 10, ticks: 80  },
  { id: 'masonry',    name: '建筑术',     prereqs: ['metallurgy'],              scholars: 8,  ticks: 70  },
  { id: 'navigation', name: '航海术',     prereqs: ['writing'],                 scholars: 12, ticks: 120 },
  { id: 'gunpowder',  name: '火药',       prereqs: ['metallurgy','writing'],    scholars: 15, ticks: 150 },
  { id: 'printing',   name: '印刷术',     prereqs: ['gunpowder'],               scholars: 15, ticks: 120 },
  { id: 'industry',   name: '工业革命', prereqs: ['gunpowder','navigation'],  scholars: 20, ticks: 200 },
  { id: 'electricity',name: '电力',      prereqs: ['industry'],                scholars: 25, ticks: 250 },
  { id: 'flight',     name: '航空',       prereqs: ['electricity'],             scholars: 25, ticks: 200 },
  { id: 'computing',  name: '计算机',     prereqs: ['electricity'],             scholars: 30, ticks: 250 },
  { id: 'space',      name: '太空探索',   prereqs: ['computing','flight'],       scholars: 40, ticks: 400 },
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

// Building types
const BUILDING_TYPES = {
  farm:      { name: '农场',   icon: '🌾', food: 2,   wood: 0,   stone: 0,   iron: 0,   military: 0, research: 0, defense: 0, trade: 0 },
  mine:      { name: '矿场',   icon: '⛏️', food: 0,   wood: 0,   stone: 1.5, iron: 1,   military: 0, research: 0, defense: 0, trade: 0 },
  barracks:  { name: '兵营',   icon: '⚔️', food: 0,   wood: 0,   stone: 0.5, iron: 0.5, military: 1.5, research: 0, defense: 0, trade: 0 },
  academy:   { name: '学院',   icon: '📚', food: 0,   wood: 0.3, stone: 0.5, iron: 0,   military: 0, research: 1,   defense: 0, trade: 0 },
  market:    { name: '市场',   icon: '🏪', food: 0.5, wood: 0,   stone: 0,   iron: 0,   military: 0, research: 0, defense: 0, trade: 1 },
  wall:      { name: '城墙',   icon: '🏰', food: 0,   wood: 0,   stone: 2,   iron: 0.5, military: 0, research: 0, defense: 2, trade: 0 },
};

// Simulation parameters
const FOOD_PER_POP      = 0.006;
const PROD_SCALE        = 0.015;
const GROWTH_BASE       = 0.004;
const GROWTH_SURPLUS    = 0.005;
const GROWTH_DEFICIT    = -0.003;
const MIN_POP           = 3;
const TICKS_PER_YEAR    = 100;
const CORRUPTION_THRESHOLD = 800;  // population above which corruption kicks in
const SPLIT_THRESHOLD     = 2000; // population that may cause split

// ════════════════════ WORLD GENERATION ════════════════════
function generateTerrain(size, seed) {
  const elev = new SimplexNoise(seed);
  const moist = new SimplexNoise(seed + 7777);
  const terrain = new Uint8Array(size * size);

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      let e = 0, amp = 1, freq = 1, maxAmp = 0;
      for (let oct = 0; oct < 6; oct++) {
        e += elev.noise2D(x * freq / size * 4, y * freq / size * 4) * amp;
        maxAmp += amp;
        amp *= 0.5;
        freq *= 2;
      }
      e = (e / maxAmp + 1) * 0.5;
      const cx = x / size - 0.5, cy = y / size - 0.5;
      const edgeDist = 1 - Math.sqrt(cx*cx + cy*cy) * 2.2;
      e = e * Math.max(0, Math.min(1, edgeDist + 0.3));
      const m = (moist.noise2D(x / size * 3, y / size * 3) + 1) * 0.5;

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
    this.influenceRadius = 6;
    this.territorySize = 0;
    this.buildings = { farm: 0, mine: 0, barracks: 0, academy: 0, market: 0, wall: 0 };
    this.buildCooldown = 0; // ticks until next build attempt
    this.militaryPower = 0;
    this.defensePower = 0;
    this.corruption = 0;
    this.settlementLevel = 0; // 0=部落, 1=村庄, 2=城镇, 3=城市, 4=大都市
  }

  hasTech(id)   { return this.techs.has(id); }
  techCount()   { return this.techs.size; }

  getFoodMultiplier() {
    let m = 1;
    if (this.hasTech('toolmaking'))  m += 0.4;
    if (this.hasTech('archery'))     m += 0.6;
    if (this.hasTech('agriculture')) m += 1.2;
    // Building bonuses
    m += this.buildings.farm * 0.15;
    return m;
  }

  getMineMultiplier() {
    let m = 1;
    if (this.hasTech('metallurgy')) m += 1.0;
    if (this.hasTech('industry'))   m += 1.0;
    m += this.buildings.mine * 0.12;
    return m;
  }

  getResearchMultiplier() {
    let m = 1;
    if (this.hasTech('writing'))    m += 1.0;
    if (this.hasTech('printing'))   m += 0.5;
    if (this.hasTech('computing'))  m += 2.0;
    // Building bonus
    m += this.buildings.academy * 0.25;
    // Larger tribes have more scholars
    m *= 1 + Math.log10(Math.max(1, this.population)) * 0.15;
    return m;
  }

  getMilitaryMultiplier() {
    let m = 1;
    if (this.hasTech('gunpowder')) m += 1.5;
    if (this.hasTech('masonry'))   m += 0.5;
    if (this.hasTech('industry')) m += 1.0;
    m += this.buildings.barracks * 0.2;
    // Corruption reduces military efficiency
    m *= (1 - this.corruption * 0.3);
    return m;
  }

  getDefenseMultiplier() {
    let m = 1;
    m += this.buildings.wall * 0.3;
    return m;
  }

  getTradeMultiplier() {
    let m = 1;
    m += this.buildings.market * 0.15;
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

  getMaxBuildings() {
    // Base 3 + 1 per 50 pop + 1 per 2 techs
    return 3 + Math.floor(this.population / 50) + Math.floor(this.techCount() / 2);
  }

  getTotalBuildings() {
    return Object.values(this.buildings).reduce((a, b) => a + b, 0);
  }

  updateSettlementLevel() {
    if (this.population >= 2000) this.settlementLevel = 4;
    else if (this.population >= 800) this.settlementLevel = 3;
    else if (this.population >= 300) this.settlementLevel = 2;
    else if (this.population >= 100) this.settlementLevel = 1;
    else this.settlementLevel = 0;
  }
}

// ════════════════════ SIMULATION ════════════════════
class Simulation {
  constructor() {
    this.terrain = null;
    this.territory = null; // Int16Array, -1 = unclaimed, tribe.id = owner
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
    this.territory = new Int16Array(WORLD_SIZE * WORLD_SIZE).fill(-1);
    this.tribes = this._placeTribes(10 + ((seed % 5) | 0));
    // Initialize territory for each tribe (claim starting cell + neighbors)
    for (const tribe of this.tribes) {
      this._claimInitialTerritory(tribe);
    }
    this.year = 1;
    this.tickCount = 0;
    this.events = [];
    this.selectedId = this.tribes.length > 0 ? this.tribes[0].id : -1;
    this._emitEvent({ type: 'system', text: `新世界诞生，种子 #${seed}`, year: 1 });
    this._emitState();
  }

  _claimInitialTerritory(tribe) {
    const dirs = [[0,0],[-1,0],[1,0],[0,-1],[0,1],[-1,-1],[1,-1],[-1,1],[1,1]];
    for (const [dx, dy] of dirs) {
      const nx = tribe.x + dx, ny = tribe.y + dy;
      if (nx >= 0 && nx < WORLD_SIZE && ny >= 0 && ny < WORLD_SIZE) {
        const idx = ny * WORLD_SIZE + nx;
        const t = this.terrain[idx];
        if (TERRAIN_EXPAND_COST[t] < 999 && this.territory[idx] === -1) {
          this.territory[idx] = tribe.id;
        }
      }
    }
    tribe.territorySize = this._countTerritory(tribe.id);
  }

  _countTerritory(tribeId) {
    let count = 0;
    for (let i = 0; i < this.territory.length; i++) {
      if (this.territory[i] === tribeId) count++;
    }
    return count;
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
    for (let i = candidates.length - 1; i > 0; i--) {
      const j = (Math.random() * (i + 1)) | 0;
      const tmp = candidates[i]; candidates[i] = candidates[j]; candidates[j] = tmp;
    }

    const tribes = [];
    for (const c of candidates) {
      if (tribes.length >= count) break;
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

    // Territory expansion every 10 ticks
    if (this.tickCount % 10 === 0) {
      for (const tribe of this.tribes) {
        if (!tribe.alive) continue;
        this._expandTerritory(tribe);
      }
    }

    // Building decisions every 30 ticks
    if (this.tickCount % 30 === 0) {
      for (const tribe of this.tribes) {
        if (!tribe.alive) continue;
        this._autoBuild(tribe);
      }
    }

    // Random events every ~50 ticks
    if (this.tickCount % 50 === 0) this._randomEvent();

    // Update selection
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
    // Gather resources from territory cells
    let foodBase = 0, woodBase = 0, stoneBase = 0, ironBase = 0;
    // Sample territory instead of full scan for performance
    const sampleStep = Math.max(1, Math.floor(tribe.territorySize / 100));
    let sampleCount = 0;
    for (let i = 0; i < this.territory.length; i += sampleStep) {
      if (this.territory[i] === tribe.id) {
        const t = this.terrain[i];
        const res = TERRAIN_RESOURCES[t];
        foodBase += res.food;
        woodBase += res.wood;
        stoneBase += res.stone;
        ironBase += res.iron;
        sampleCount++;
      }
    }
    // Scale back to full territory
    const scale = tribe.territorySize / Math.max(1, sampleCount);
    foodBase *= scale;
    woodBase *= scale;
    stoneBase *= scale;
    ironBase *= scale;

    // Building production bonuses (flat)
    foodBase += tribe.buildings.farm * 3;
    stoneBase += tribe.buildings.mine * 2;
    ironBase += tribe.buildings.mine * 1.5;

    const eff = Math.min(tribe.population / 80, 1.5);

    // Corruption effect
    if (tribe.population > CORRUPTION_THRESHOLD) {
      tribe.corruption = Math.min(0.5, (tribe.population - CORRUPTION_THRESHOLD) / (SPLIT_THRESHOLD * 2));
    } else {
      tribe.corruption *= 0.98;
    }
    const corruptionEff = 1 - tribe.corruption * 0.2;

    tribe.food  += (foodBase  * eff * tribe.getFoodMultiplier() * PROD_SCALE * corruptionEff) - tribe.population * FOOD_PER_POP;
    tribe.wood  += woodBase  * eff * PROD_SCALE * corruptionEff;
    tribe.stone += stoneBase * eff * tribe.getMineMultiplier() * PROD_SCALE * corruptionEff;
    tribe.iron  += ironBase  * eff * tribe.getMineMultiplier() * PROD_SCALE * corruptionEff;

    // Resource caps
    tribe.food  = Math.min(tribe.food,  tribe.population * 8);
    tribe.wood  = Math.min(tribe.wood,  tribe.population * 4);
    tribe.stone = Math.min(tribe.stone, tribe.population * 3);
    tribe.iron  = Math.min(tribe.iron,  tribe.population * 2);

    // Population dynamics with logistic curve
    const territoryMax = tribe.territorySize * 8 * (1 + tribe.techCount() * 0.5);
    let gr = GROWTH_BASE;
    if (tribe.food > 10)  gr += GROWTH_SURPLUS;
    if (tribe.food < 0)   gr += GROWTH_DEFICIT;
    if (tribe.food < -10) gr += GROWTH_DEFICIT;

    // Logistic growth approaching carrying capacity
    const carryingCap = Math.max(tribe.population, territoryMax);
    if (tribe.population > carryingCap * 0.7) {
      gr *= Math.max(0.05, (carryingCap - tribe.population) / (carryingCap * 0.3));
    }

    tribe.population += tribe.population * gr;

    // Starvation cycle
    if (tribe.food < -50) {
      tribe.population *= 0.92;
      tribe.food = 0;
      this._emitEvent({ type: 'disaster', text: `${tribe.name} 遭遇严重饥荒！`, year: this.year });
    }

    tribe.population = Math.max(MIN_POP, tribe.population);

    // Update settlement level
    tribe.updateSettlementLevel();

    // Research (much faster)
    if (tribe.researching) {
      const tech = TECH_TREE.find(t => t.id === tribe.researching);
      if (tech) {
        const scholars = tribe.population * (0.04 + tribe.techCount() * 0.01);
        const baseRate = 1 - Math.exp(-scholars / (tech.scholars * 8));
        const rate = baseRate * tribe.getResearchMultiplier();
        tribe.researchProgress += rate;
        if (tribe.researchProgress >= tech.ticks) {
          tribe.techs.add(tech.id);
          tribe.researching = null;
          tribe.researchProgress = 0;
          this._emitEvent({ type: 'tech', text: `${tribe.name} 发明了「${tech.name}」！`, year: this.year });
          tribe.autoSelectResearch();
          if (tech.id === 'space') {
            this._emitEvent({ type: 'victory', text: `🏆 ${tribe.name} 率先进入太空时代！文明胜利！`, year: this.year });
          }
        }
      }
    }

    // Update military power
    tribe.militaryPower = tribe.population * tribe.getMilitaryMultiplier();
    tribe.defensePower = tribe.population * tribe.getDefenseMultiplier();

    // Death check (much harder to go extinct)
    if (tribe.population <= MIN_POP && tribe.food < -30) {
      tribe.alive = false;
      // Release territory
      for (let i = 0; i < this.territory.length; i++) {
        if (this.territory[i] === tribe.id) this.territory[i] = -1;
      }
      this._emitEvent({ type: 'extinction', text: `${tribe.name} 灭亡了。`, year: this.year });
    }

    // Splitting check for large empires
    if (tribe.population >= SPLIT_THRESHOLD && Math.random() < 0.001 * tribe.corruption) {
      this._trySplit(tribe);
    }
  }

  _trySplit(tribe) {
    // Find a border cell for the new splinter
    const borderCells = [];
    for (let y = 1; y < WORLD_SIZE - 1; y++) {
      for (let x = 1; x < WORLD_SIZE - 1; x++) {
        if (this.territory[y * WORLD_SIZE + x] !== tribe.id) continue;
        // Check if this is a border cell
        let isBorder = false;
        for (const [dx, dy] of [[-1,0],[1,0],[0,-1],[0,1]]) {
          const nx = x + dx, ny = y + dy;
          if (this.territory[ny * WORLD_SIZE + nx] !== tribe.id) {
            isBorder = true;
            break;
          }
        }
        if (isBorder) borderCells.push({ x, y });
      }
    }
    if (borderCells.length === 0) return;

    const cell = borderCells[(Math.random() * borderCells.length) | 0];
    const splitPop = tribe.population * 0.3;
    tribe.population *= 0.7;

    // Create new tribe
    const newId = this.tribes.length;
    const newName = TRIBE_NAMES[newId % TRIBE_NAMES.length];
    const newColor = TRIBE_COLORS[newId % TRIBE_COLORS.length];
    const newTribe = new Tribe(newId, newName, cell.x, cell.y, newColor);
    newTribe.population = splitPop;
    newTribe.food = tribe.food * 0.3;
    newTribe.wood = tribe.wood * 0.2;
    newTribe.stone = tribe.stone * 0.2;
    newTribe.iron = tribe.iron * 0.2;
    // Copy some techs
    for (const t of tribe.techs) {
      if (Math.random() < 0.6) newTribe.techs.add(t);
    }
    newTribe.autoSelectResearch();
    this.tribes.push(newTribe);

    // Transfer nearby territory to the new tribe
    const radius = 5;
    for (let dy = -radius; dy <= radius; dy++) {
      for (let dx = -radius; dx <= radius; dx++) {
        const nx = cell.x + dx, ny = cell.y + dy;
        if (nx < 0 || nx >= WORLD_SIZE || ny < 0 || ny >= WORLD_SIZE) continue;
        const idx = ny * WORLD_SIZE + nx;
        if (this.territory[idx] === tribe.id && Math.random() < 0.3) {
          this.territory[idx] = newId;
        }
      }
    }

    // Recalculate territories
    tribe.territorySize = this._countTerritory(tribe.id);
    newTribe.territorySize = this._countTerritory(newId);

    this._emitEvent({ type: 'event', text: `${tribe.name} 因内部分裂产生了 ${newName}！`, year: this.year });
  }

  _expandTerritory(tribe) {
    // Expansion speed based on population density and tech
    const expandChance = 0.02 + tribe.techCount() * 0.008 + Math.min(tribe.population / 500, 0.05);
    // Agriculture expands into plains/farmland faster
    const hasAgri = tribe.hasTech('agriculture');
    // Navigation expands coastal territory
    const hasNav = tribe.hasTech('navigation');

    // Collect frontier cells (owned cells adjacent to unclaimed)
    // For performance, we iterate in chunks near existing territory
    // Use a BFS-like approach: check borders of current territory
    const frontier = [];
    for (let y = 1; y < WORLD_SIZE - 1; y++) {
      for (let x = 1; x < WORLD_SIZE - 1; x++) {
        const idx = y * WORLD_SIZE + x;
        if (this.territory[idx] !== tribe.id) continue;
        // Check 4 neighbors
        for (const [dx, dy] of [[-1,0],[1,0],[0,-1],[0,1]]) {
          const nx = x + dx, ny = y + dy;
          const nIdx = ny * WORLD_SIZE + nx;
          if (this.territory[nIdx] === -1) {
            const t = this.terrain[nIdx];
            const cost = TERRAIN_EXPAND_COST[t];
            if (cost < 999) {
              frontier.push({ x: nx, y: ny, cost, idx: nIdx });
            }
          }
        }
      }
    }

    // Shuffle and try to expand
    for (let i = frontier.length - 1; i > 0; i--) {
      const j = (Math.random() * (i + 1)) | 0;
      const tmp = frontier[i]; frontier[i] = frontier[j]; frontier[j] = tmp;
    }

    let expanded = 0;
    const maxExpand = Math.ceil(tribe.population / 60) + tribe.techCount();

    for (const cell of frontier) {
      if (expanded >= maxExpand) break;
      if (Math.random() > expandChance) continue;

      // Tech bonuses for specific terrain
      let bonus = 0;
      const t = this.terrain[cell.idx];
      if (hasAgri && (t === TERRAIN.PLAINS || t === TERRAIN.BEACH)) bonus = 0.3;
      if (hasNav && (t === TERRAIN.BEACH || t === TERRAIN.SHALLOW)) bonus = 0.4;
      if (t === TERRAIN.MOUNTAIN && tribe.hasTech('masonry')) bonus = 0.2;

      if (Math.random() < (0.1 + bonus) / cell.cost) {
        this.territory[cell.idx] = tribe.id;
        expanded++;
      }
    }

    tribe.territorySize += expanded;
  }

  _autoBuild(tribe) {
    if (tribe.buildCooldown > 0) {
      tribe.buildCooldown--;
      return;
    }

    const maxB = tribe.getMaxBuildings();
    if (tribe.getTotalBuildings() >= maxB) return;

    // Decide what to build based on needs
    const priorities = [];
    if (tribe.food < tribe.population * 2)  priorities.push('farm');
    if (tribe.stone < 20)                    priorities.push('mine');
    if (tribe.iron < 5 && tribe.hasTech('metallurgy')) priorities.push('mine');
    if (tribe.techCount() >= 2 && Math.random() < 0.3) priorities.push('academy');
    if (Math.random() < 0.2) priorities.push('market');
    if (tribe.militaryPower < tribe.population * 0.8 && Math.random() < 0.2) priorities.push('barracks');
    if (tribe.population > 200 && Math.random() < 0.15) priorities.push('wall');
    if (priorities.length === 0) return;

    const chosen = priorities[(Math.random() * priorities.length) | 0];
    const btype = BUILDING_TYPES[chosen];

    // Check resources
    if (tribe.stone >= btype.stone * 10 && tribe.wood >= btype.wood * 10 && tribe.iron >= btype.iron * 10) {
      tribe.stone -= btype.stone * 10;
      tribe.wood -= btype.wood * 10;
      tribe.iron -= btype.iron * 10;
      tribe.buildings[chosen]++;
      tribe.buildCooldown = 20;
      if (tribe.buildings[chosen] <= 2) { // Only log first few
        this._emitEvent({ type: 'event', text: `${tribe.name} 建造了 ${btype.icon} ${btype.name}`, year: this.year });
      }
    }
  }

  _processInteractions() {
    const alive = this.tribes.filter(t => t.alive);
    for (let i = 0; i < alive.length; i++) {
      for (let j = i + 1; j < alive.length; j++) {
        const a = alive[i], b = alive[j];
        const dx = a.x - b.x, dy = a.y - b.y;
        const dist = Math.sqrt(dx*dx + dy*dy);
        const range = 25 + (a.hasTech('navigation') || b.hasTech('navigation') ? 15 : 0)
                         + (a.hasTech('flight') || b.hasTech('flight') ? 25 : 0);
        if (dist > range) continue;

        // Trade (enhanced with building bonuses)
        if (Math.random() < 0.04) {
          const tradeMult = (a.getTradeMultiplier() + b.getTradeMultiplier()) * 0.5;
          a.food += 0.3 * tradeMult; b.food += 0.3 * tradeMult;
          a.wood += 0.2 * tradeMult; b.wood += 0.2 * tradeMult;
          a.stone += 0.1 * tradeMult; b.stone += 0.1 * tradeMult;
        }

        // Cultural diffusion (enhanced with markets)
        const diffusionChance = 0.008 + (a.buildings.market + b.buildings.market) * 0.003;
        if (Math.random() < diffusionChance) {
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

        // Enhanced war system
        const warChance = 0.002 + (a.population > 300 ? 0.001 : 0) + (b.population > 300 ? 0.001 : 0);
        if (Math.random() < warChance) {
          this._war(a, b);
        }

        // Merge (peaceful absorption)
        if (Math.random() < 0.002) {
          const big = a.population > b.population ? a : b;
          const sml = a.population > b.population ? b : a;
          if (big.population > sml.population * 3 && sml.techCount() <= big.techCount()) {
            big.population += sml.population * 0.7;
            // Transfer territory
            for (let k = 0; k < this.territory.length; k++) {
              if (this.territory[k] === sml.id) this.territory[k] = big.id;
            }
            big.territorySize = this._countTerritory(big.id);
            sml.alive = false;
            sml.territorySize = 0;
            this._emitEvent({ type: 'merge', text: `${sml.name} 并入了 ${big.name}`, year: this.year });
          }
        }
      }
    }
  }

  _war(a, b) {
    const aS = a.militaryPower * (1 + Math.random() * 0.2);
    const bS = b.militaryPower * (1 + Math.random() * 0.2);

    // Apply defense
    const aDef = a.defensePower;
    const bDef = b.defensePower;

    if (aS > bS * 1.2 + bDef * 0.5) {
      // A wins
      const ratio = Math.min(0.5, (aS - bS) / (aS + bS));
      b.population *= (1 - ratio * 0.5);
      // Refugee effect
      const refugees = Math.floor(b.population * ratio * 0.1);
      b.population -= refugees;
      // Territory transfer: a claims border cells from b
      const transferred = this._transferBorderTerritory(b.id, a.id, Math.floor(ratio * 10) + 2);
      a.territorySize = this._countTerritory(a.id);
      b.territorySize = this._countTerritory(b.id);

      if (b.population < MIN_POP + 5) {
        b.alive = false;
        // Transfer all remaining territory
        for (let k = 0; k < this.territory.length; k++) {
          if (this.territory[k] === b.id) this.territory[k] = a.id;
        }
        a.territorySize = this._countTerritory(a.id);
        b.territorySize = 0;
        this._emitEvent({ type: 'war', text: `${a.name} 征服了 ${b.name}！夺取 ${transferred} 格领土`, year: this.year });
      } else {
        this._emitEvent({ type: 'war', text: `${a.name} 击败 ${b.name}，夺取 ${transferred} 格领土，产生 ${refugees} 难民`, year: this.year });
      }
    } else if (bS > aS * 1.2 + aDef * 0.5) {
      // B wins
      const ratio = Math.min(0.5, (bS - aS) / (aS + bS));
      a.population *= (1 - ratio * 0.5);
      const refugees = Math.floor(a.population * ratio * 0.1);
      a.population -= refugees;
      const transferred = this._transferBorderTerritory(a.id, b.id, Math.floor(ratio * 10) + 2);
      a.territorySize = this._countTerritory(a.id);
      b.territorySize = this._countTerritory(b.id);

      if (a.population < MIN_POP + 5) {
        a.alive = false;
        for (let k = 0; k < this.territory.length; k++) {
          if (this.territory[k] === a.id) this.territory[k] = b.id;
        }
        b.territorySize = this._countTerritory(b.id);
        a.territorySize = 0;
        this._emitEvent({ type: 'war', text: `${b.name} 征服了 ${a.name}！夺取 ${transferred} 格领土`, year: this.year });
      } else {
        this._emitEvent({ type: 'war', text: `${b.name} 击败 ${a.name}，夺取 ${transferred} 格领土，产生 ${refugees} 难民`, year: this.year });
      }
    } else {
      // Draw - minor losses
      a.population *= 0.97; b.population *= 0.97;
      this._emitEvent({ type: 'war', text: `${a.name} 与 ${b.name} 交战，两败俱伤`, year: this.year });
    }
  }

  _transferBorderTerritory(fromId, toId, count) {
    const borders = [];
    for (let y = 1; y < WORLD_SIZE - 1; y++) {
      for (let x = 1; x < WORLD_SIZE - 1; x++) {
        const idx = y * WORLD_SIZE + x;
        if (this.territory[idx] !== fromId) continue;
        let isBorder = false;
        for (const [dx, dy] of [[-1,0],[1,0],[0,-1],[0,1]]) {
          const nx = x + dx, ny = y + dy;
          if (this.territory[ny * WORLD_SIZE + nx] !== fromId) {
            isBorder = true;
            break;
          }
        }
        if (isBorder) borders.push(idx);
      }
    }

    // Shuffle and transfer up to count
    for (let i = borders.length - 1; i > 0; i--) {
      const j = (Math.random() * (i + 1)) | 0;
      const tmp = borders[i]; borders[i] = borders[j]; borders[j] = tmp;
    }

    let transferred = 0;
    for (let i = 0; i < Math.min(count, borders.length); i++) {
      this.territory[borders[i]] = toId;
      transferred++;
    }
    return transferred;
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
    } else if (r < 0.42) {
      // Random tech breakthrough!
      const t = alive[(Math.random() * alive.length) | 0];
      const available = TECH_TREE.filter(tc => t.canResearch(tc.id));
      if (available.length > 0) {
        const tc = available[(Math.random() * available.length) | 0];
        t.techs.add(tc.id);
        if (t.researching === tc.id) {
          t.researching = null;
          t.researchProgress = 0;
          t.autoSelectResearch();
        }
        this._emitEvent({ type: 'tech', text: `⚡ ${t.name} 取得了技术突破「${tc.name}」！`, year: this.year });
      }
    } else if (r < 0.46) {
      // Building destruction (war/fire)
      const t = alive[(Math.random() * alive.length) | 0];
      const keys = Object.keys(t.buildings).filter(k => t.buildings[k] > 0);
      if (keys.length > 0) {
        const k = keys[(Math.random() * keys.length) | 0];
        t.buildings[k]--;
        this._emitEvent({ type: 'disaster', text: `${t.name} 的${BUILDING_TYPES[k].name}被摧毁了`, year: this.year });
      }
    }
  }

  getEra() {
    const maxTech = Math.max(0, ...this.tribes.filter(t => t.alive).map(t => t.techCount()));
    for (const era of ERAS) {
      if (maxTech <= era.maxTech) return era.name;
    }
    return ERAS[ERAS.length - 1].name;
  }

  getEraIndex() {
    const maxTech = Math.max(0, ...this.tribes.filter(t => t.alive).map(t => t.techCount()));
    for (let i = 0; i < ERAS.length; i++) {
      if (maxTech <= ERAS[i].maxTech) return i;
    }
    return ERAS.length - 1;
  }

  getEraDistribution() {
    // Count tribes per era
    const dist = {};
    for (const tribe of this.tribes) {
      if (!tribe.alive) continue;
      let eraName = '未知';
      for (const era of ERAS) {
        if (tribe.techCount() <= era.maxTech) { eraName = era.name; break; }
      }
      dist[eraName] = (dist[eraName] || 0) + 1;
    }
    return dist;
  }

  getTerritoryPercent(tribeId) {
    let owned = 0, total = 0;
    for (let i = 0; i < this.territory.length; i++) {
      if (this.terrain[i] > TERRAIN.SHALLOW) { // land cells only
        total++;
        if (this.territory[i] === tribeId) owned++;
      }
    }
    return total > 0 ? owned / total : 0;
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
      eraIndex: this.getEraIndex(),
      totalPop: this.getTotalPop(),
      aliveCount: this.getAliveCount(),
      eraDistribution: this.getEraDistribution(),
      tribes: this.tribes.map(t => ({
        id: t.id, name: t.name, x: t.x, y: t.y,
        population: t.population, alive: t.alive, color: t.color,
        food: t.food, wood: t.wood, stone: t.stone, iron: t.iron,
        techs: [...t.techs],
        researching: t.researching,
        researchProgress: t.researchProgress,
        territorySize: t.territorySize,
        buildings: { ...t.buildings },
        militaryPower: t.militaryPower,
        defensePower: t.defensePower,
        corruption: t.corruption,
        settlementLevel: t.settlementLevel,
        territoryPercent: this.getTerritoryPercent(t.id),
      })),
      selectedId: this.selectedId,
    };
    for (const cb of this.stateCallbacks) cb(state);
  }
}

return {
  SimplexNoise, WORLD_SIZE, TERRAIN, TERRAIN_COLORS, TERRAIN_EXPAND_COST,
  TERRAIN_RESOURCES, TECH_TREE, TRIBE_NAMES, TRIBE_COLORS, ERAS, ERA_OVERLAYS,
  BUILDING_TYPES, TICKS_PER_YEAR, Simulation,
};
})();
