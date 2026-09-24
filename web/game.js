// --- Données du jeu ---
const COLORS = ["red", "green", "blue", "yellow"];
const ROBOT_COLORS = {
  red: "#e6194b", green: "#3cb44b", blue: "#4363d8", yellow: "#f0c000",
};
const DIRECTIONS = { N: [0, -1], S: [0, 1], E: [1, 0], W: [-1, 0] };
const OPPOSITE = { N: "S", S: "N", E: "W", W: "E" };

const table = {
  width: 8,
  height: 8,
  walls: [[3, 0, "E"], [5, 4, "S"], [5, 4, "W"]],
};

const startRobots = {
  red: [0, 0], green: [7, 7], blue: [3, 7], yellow: [7, 3],
};
const target = { robot: "red", cell: [3, 6] };

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
for (const [x, y, side] of table.walls) addWall(x, y, side);

function hasWall(x, y, side) { return wallSet.has(`${x},${y},${side}`); }
function inBounds(x, y) { return x >= 0 && x < table.width && y >= 0 && y < table.height; }

// --- La règle de glissement (miroir fidèle du slide Python) ---
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
const CELL = canvas.width / table.width;

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
    const [x, y] = robots[color];
    ctx.fillStyle = ROBOT_COLORS[color];
    ctx.beginPath();
    ctx.arc(x*CELL + CELL/2, y*CELL + CELL/2, CELL/2 - 6, 0, 2*Math.PI);
    ctx.fill();
    // liseré blanc autour du robot sélectionné
    if (color === selected) {
      ctx.strokeStyle = "#fff"; ctx.lineWidth = 3; ctx.stroke();
    }
  }
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

// --- Bouton réinitialiser ---
function reset() {
  robots = structuredClone(startRobots);
  moveCount = 0;
  won = false;
  refresh();
}
document.getElementById("reset").addEventListener("click", reset);

// --- Démarrage ---
refresh();