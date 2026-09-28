// --- Données du jeu (seront chargées depuis l'API) ---
let table = null;
let startRobots = null;
let target = null;
let solution = null;        // liste des coups renvoyée par /solve
let solutionStep = 0;       // combien de coups de la solution sont "joués" en preview
let previewing = false;     // le mode prévisualisation est-il actif ?
let previewRobots = null;   // état des robots affiché pendant la preview
let currentConfig = null;   // { table, game } de la partie courante

const API = "http://127.0.0.1:8000";

// --- Données du jeu ---
const COLORS = ["red", "green", "blue", "yellow"];
const ROBOT_COLORS = {
  red: "#e6194b", green: "#3cb44b", blue: "#4363d8", yellow: "#f0c000",
};
const DIRECTIONS = { N: [0, -1], S: [0, 1], E: [1, 0], W: [-1, 0] };
const OPPOSITE = { N: "S", S: "N", E: "W", W: "E" };

function applyConfig(tableData, gameData) {
  currentConfig = { table: tableData, game: gameData };
  table = tableData;
  target = { robot: gameData.target_robot, cell: gameData.target_cell };
  startRobots = {};
  for (const color of COLORS) {
    startRobots[color] = gameData.robots[color];
  }

  // réinitialise complètement l'état du jeu
  buildWallSet();
  CELL = canvas.width / table.width;
  robots = structuredClone(startRobots);
  moveCount = 0;
  won = false;
  selected = "red";

  // ferme toute prévisualisation en cours
  previewing = false;
  solution = null;
  solutionStep = 0;
  document.getElementById("solution").innerHTML = "";
  document.getElementById("stats").innerHTML = "";
  document.getElementById("comparison").innerHTML = "";

  refresh();
}

async function newTable() {
  try {
    const resp = await fetch(`${API}/generate/table`, { method: "POST" });
    const data = await resp.json();
    applyConfig(data.table, data.game);
  } catch (err) {
    console.error("Échec de la génération de table :", err);
  }
}

async function newGame() {
  try {
    const resp = await fetch(`${API}/generate/game`, { method: "POST" });
    const data = await resp.json();
    applyConfig(data.table, data.game);
  } catch (err) {
    console.error("Échec de la génération de partie :", err);
  }
}

async function loadConfig() {
  // récupère la partie (robots, cible, arrivée) et la table qu'elle référence
  const gameResp = await fetch(`${API}/games/demo`);
  const gameData = await gameResp.json();

  const tableResp = await fetch(`${API}/tables/${gameData.table}`);
  const tableData = await tableResp.json();

  // remplit les variables du jeu à partir des données reçues
  table = tableData;
  target = { robot: gameData.target_robot, cell: gameData.target_cell };
  startRobots = {};
  for (const color of COLORS) {
    startRobots[color] = gameData.robots[color];
  }
  currentConfig = { table: tableData, game: gameData };
}




// --- État courant (modifiable en jouant) ---
let robots = structuredClone(startRobots);
let selected = "red";     // robot actif
let moveCount = 0;
let won = false;

// --- Ensemble des murs, avec les miroirs (comme add_wall en Python) ---
const wallSet = new Set();
function addWall(x, y, side) {
  wallSet.add(`${x},${y},${side}`);
  const [dx, dy] = DIRECTIONS[side];
  const nx = x + dx, ny = y + dy;
  if (nx >= 0 && nx < table.width && ny >= 0 && ny < table.height) {
    wallSet.add(`${nx},${ny},${OPPOSITE[side]}`);
  }
}

function buildWallSet() {
  wallSet.clear();
  for (const [x, y, side] of table.walls) addWall(x, y, side);
}
function hasWall(x, y, side) { return wallSet.has(`${x},${y},${side}`); }
function inBounds(x, y) { return x >= 0 && x < table.width && y >= 0 && y < table.height; }

// --- La règle de glissement (miroir fidèle du slide Python) ---
function slideFrom(start, direction, occupied) {
  const [dx, dy] = DIRECTIONS[direction];
  let [x, y] = start;
  while (true) {
    if (hasWall(x, y, direction)) break;
    const nx = x + dx, ny = y + dy;
    if (!inBounds(nx, ny)) break;
    if (occupied.has(`${nx},${ny}`)) break;
    x = nx; y = ny;
  }
  return [x, y];
}

function slide(start, direction) {
  const [dx, dy] = DIRECTIONS[direction];
  let [x, y] = start;
  // positions occupées par les AUTRES robots
  const occupied = new Set();
  for (const c of COLORS) {
    if (robots[c] !== robots[selected]) occupied.add(`${robots[c][0]},${robots[c][1]}`);
  }
  while (true) {
    if (hasWall(x, y, direction)) break;
    const nx = x + dx, ny = y + dy;
    if (!inBounds(nx, ny)) break;
    if (occupied.has(`${nx},${ny}`)) break;
    x = nx; y = ny;
  }
  return [x, y];
}

// --- Dessin ---
const canvas = document.getElementById("board");
const ctx = canvas.getContext("2d");
let CELL;

function computePreview() {
  // repart du départ et applique les `solutionStep` premiers coups
  const state = structuredClone(startRobots);
  for (let k = 0; k < solutionStep; k++) {
    const [robotIndex, direction] = solution[k];
    const color = COLORS[robotIndex];
    // cases occupées par les AUTRES robots, dans cet état de preview
    const occupied = new Set();
    for (const c of COLORS) {
      if (c !== color) occupied.add(`${state[c][0]},${state[c][1]}`);
    }
    state[color] = slideFrom(state[color], direction, occupied);
  }
  previewRobots = state;
}

function drawPreviewArrow() {
  // seulement en preview, et seulement s'il reste un coup à venir
  if (!previewing || solution === null) return;
  if (solutionStep >= solution.length) return;

  const [robotIndex, direction] = solution[solutionStep];
  const color = COLORS[robotIndex];
  const [x, y] = previewRobots[color];   // position du robot dans l'état de preview
  const [dx, dy] = DIRECTIONS[direction];

  const cx = x * CELL + CELL / 2;
  const cy = y * CELL + CELL / 2;
  const start_off = CELL / 2 - 4;              // on démarre au bord du robot
  const sx = cx + dx * start_off;
  const sy = cy + dy * start_off;
  const ex = cx + dx * CELL * 1.1;             // et on va un peu au-delà de la case
  const ey = cy + dy * CELL * 1.1;

  ctx.strokeStyle = ROBOT_COLORS[color];
  ctx.fillStyle = ROBOT_COLORS[color];
  ctx.lineWidth = 4;

  // la ligne
  ctx.beginPath();
  ctx.moveTo(sx, sy);
  ctx.lineTo(ex, ey);
  ctx.stroke();

  // la pointe
  const angle = Math.atan2(dy, dx);
  const head = 10;
  ctx.beginPath();
  ctx.moveTo(ex, ey);
  ctx.lineTo(ex - head * Math.cos(angle - Math.PI / 6), ey - head * Math.sin(angle - Math.PI / 6));
  ctx.lineTo(ex - head * Math.cos(angle + Math.PI / 6), ey - head * Math.sin(angle + Math.PI / 6));
  ctx.closePath();
  ctx.fill();
}

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.strokeStyle = "#ddd"; ctx.lineWidth = 1;
  for (let i = 0; i <= table.width; i++) {
    ctx.beginPath(); ctx.moveTo(i * CELL, 0); ctx.lineTo(i * CELL, canvas.height); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, i * CELL); ctx.lineTo(canvas.width, i * CELL); ctx.stroke();
  }

  const [tx, ty] = target.cell;
  ctx.strokeStyle = ROBOT_COLORS[target.robot]; ctx.lineWidth = 3;
  ctx.strokeRect(tx * CELL + 6, ty * CELL + 6, CELL - 12, CELL - 12);

  ctx.strokeStyle = "#000"; ctx.lineWidth = 4;
  for (const [x, y, side] of table.walls) {
    ctx.beginPath();
    if (side === "N") { ctx.moveTo(x*CELL, y*CELL); ctx.lineTo((x+1)*CELL, y*CELL); }
    if (side === "S") { ctx.moveTo(x*CELL, (y+1)*CELL); ctx.lineTo((x+1)*CELL, (y+1)*CELL); }
    if (side === "W") { ctx.moveTo(x*CELL, y*CELL); ctx.lineTo(x*CELL, (y+1)*CELL); }
    if (side === "E") { ctx.moveTo((x+1)*CELL, y*CELL); ctx.lineTo((x+1)*CELL, (y+1)*CELL); }
    ctx.stroke();
  }

  for (const color of COLORS) {
    const source = previewing ? previewRobots : robots;
    const [x, y] = source[color];
    ctx.fillStyle = ROBOT_COLORS[color];
    ctx.beginPath();
    ctx.arc(x*CELL + CELL/2, y*CELL + CELL/2, CELL/2 - 6, 0, 2*Math.PI);
    ctx.fill();
    // liseré blanc autour du robot sélectionné
    if (color === selected) {
      ctx.strokeStyle = "#fff"; ctx.lineWidth = 3; ctx.stroke();
    }
  }
  drawPreviewArrow();
}



// --- Interface (compteur, victoire) ---
function updateInfo() {
  document.getElementById("count").textContent = moveCount;
  document.getElementById("selected").textContent = selected;
  document.getElementById("status").textContent = won ? "Gagné !" : "";
}

function buildLegend() {
  const legend = document.getElementById("legend");
  legend.innerHTML = "";
  COLORS.forEach((color, i) => {
    const item = document.createElement("span");
    item.className = "legend-item" + (color === selected ? " active" : "");
    item.innerHTML =
      `<span class="dot" style="background:${ROBOT_COLORS[color]}"></span>${i + 1} = ${color}`;
    // clic sur la légende = sélectionner ce robot (pratique en plus du clavier)
    item.addEventListener("click", () => { selected = color; draw(); refresh(); });
    legend.appendChild(item);
  });
}

function refresh() {
  draw();  
  updateInfo();
  buildLegend();
}

// --- Clavier ---
const KEY_TO_DIR = { ArrowUp: "N", ArrowDown: "S", ArrowLeft: "W", ArrowRight: "E" };

document.addEventListener("keydown", (e) => {
  // changer de robot avec les touches 1-4
  if (["1", "2", "3", "4"].includes(e.key)) {
    selected = COLORS[Number(e.key) - 1];
    refresh();
    return;
  }
  if (won) return;                       // partie finie : on ignore les flèches
  const dir = KEY_TO_DIR[e.key];
  if (!dir) return;                      // touche non gérée
  e.preventDefault();                    // évite que la page défile

  const before = robots[selected];
  const after = slide(before, dir);
  if (after[0] !== before[0] || after[1] !== before[1]) {
    robots[selected] = after;
    moveCount++;

    // victoire ?
    const [rx, ry] = robots[target.robot];
    const [cx, cy] = target.cell;
    if (rx === cx && ry === cy) won = true;
    refresh();
  }
});

function previewForward() {
  if (!previewing || solution === null) return;
  if (solutionStep < solution.length) {
    solutionStep++;
    computePreview();
    refresh();
  }
}

function previewBackward() {
  if (!previewing || solution === null) return;
  if (solutionStep > 0) {
    solutionStep--;
    computePreview();
    refresh();
  }
}

function closePreview() {
  previewing = false;
  previewRobots = null;
  refresh();   // on redessine les vrais robots, la partie est intacte
}

// --- Bouton réinitialiser ---
function reset() {
  robots = structuredClone(startRobots);
  moveCount = 0;
  won = false;
  refresh();
}
document.getElementById("reset").addEventListener("click", reset);

document.getElementById("new-game").addEventListener("click", newGame);
document.getElementById("new-table").addEventListener("click", newTable);

document.getElementById("solve").addEventListener("click", showSolution);

document.getElementById("compare").addEventListener("click", compareAlgorithms);

document.getElementById("forward").addEventListener("click", previewForward);
document.getElementById("backward").addEventListener("click", previewBackward);
document.getElementById("close-preview").addEventListener("click", closePreview);

// --- Démarrage : on charge la config, PUIS on initialise le jeu ---
async function start() {
  try {
    await loadConfig();
  } catch (err) {
    console.error("Impossible de charger la configuration depuis l'API :", err);
    return;
  }

  // maintenant que table/startRobots/target sont remplis, on initialise
  buildWallSet();
  CELL = canvas.width / table.width; 
  robots = structuredClone(startRobots);
  refresh();
}

start();


const DIR_ARROWS = { N: "↑", S: "↓", E: "→", W: "←" };

async function showSolution() {
  try {
    const algo = document.getElementById("algo").value;
    const resp = await fetch(`${API}/solve`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        table: currentConfig.table,
        game: currentConfig.game,
        algorithm: algo,
      }),
    });
    const data = await resp.json();

    if (!data.solved) {
      document.getElementById("solution").textContent = "Aucune solution trouvée.";
      return;
    }

    solution = data.moves;
    displayStats(data, algo);
    solutionStep = 0;        // on repart du début
    previewing = true;
    computePreview();        // calcule la preview à l'étape 0 (= position de départ)
    displaySolutionList();
    refresh();
  } catch (err) {
    console.error("Échec de l'appel à /solve :", err);
  }
}

function displaySolutionList() {
  const container = document.getElementById("solution");
  container.innerHTML = "<strong>Solution :</strong> ";
  solution.forEach((coup, i) => {
    const color = COLORS[coup[0]];
    const arrow = DIR_ARROWS[coup[1]];
    const span = document.createElement("span");
    span.className = "move";
    span.style.color = ROBOT_COLORS[color];
    span.textContent = `${i + 1}. ${color} ${arrow}`;
    container.appendChild(span);
  });
}

function displayStats(data, algo) {
  const container = document.getElementById("stats");
  const seconds = data.elapsed.toFixed(4);
  const ALGO_NAMES = { bfs: "BFS", dijkstra: "Dijkstra", astar: "A*" };
  container.innerHTML = `
    <div class="stat"><span class="stat-label">Algorithme</span><span class="stat-value">${ALGO_NAMES[algo]}</span></div>
    <div class="stat"><span class="stat-label">Longueur</span><span class="stat-value">${data.length} coups</span></div>
    <div class="stat"><span class="stat-label">Nœuds explorés</span><span class="stat-value">${data.nodes_explored}</span></div>
    <div class="stat"><span class="stat-label">Temps</span><span class="stat-value">${seconds} s</span></div>
  `;
}

const ALGORITHMS = ["bfs", "dijkstra", "astar"];
const ALGO_LABELS = { bfs: "BFS", dijkstra: "Dijkstra", astar: "A*" };

async function compareAlgorithms() {
  try {
    // lance les trois résolutions en parallèle
    const requests = ALGORITHMS.map((algo) =>
      fetch(`${API}/solve`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          table: currentConfig.table,
          game: currentConfig.game,
          algorithm: algo,
        }),
      }).then((resp) => resp.json())
    );
    const results = await Promise.all(requests);

    displayComparison(ALGORITHMS, results);
  } catch (err) {
    console.error("Échec de la comparaison :", err);
  }
}

function displayComparison(algos, results) {
  const container = document.getElementById("comparison");
  let html = `
    <h3>Comparaison</h3>
    <table class="compare-table">
      <tr>
        <th>Algorithme</th>
        <th>Longueur</th>
        <th>Nœuds</th>
        <th>Temps (s)</th>
      </tr>`;
  algos.forEach((algo, i) => {
    const data = results[i];
    html += `
      <tr>
        <td>${ALGO_LABELS[algo]}</td>
        <td>${data.length}</td>
        <td>${data.nodes_explored}</td>
        <td>${data.elapsed.toFixed(4)}</td>
      </tr>`;
  });
  html += `</table>`;
  container.innerHTML = html;
}