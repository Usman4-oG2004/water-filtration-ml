
// ── Counter animation ─────────────────────────────────────────────────────
function animateCounters() {
  document.querySelectorAll('.stat-val[data-target]').forEach(el => {
    const target = parseInt(el.dataset.target);
    const dur = 1800;
    const start = performance.now();
    function tick(now) {
      const t = Math.min((now - start) / dur, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      el.textContent = Math.round(ease * target).toLocaleString();
      if (t < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  });
}

// ── Metric bars animation ──────────────────────────────────────────────────
function animateMetricBars() {
  document.querySelectorAll('.metric-bar').forEach(el => {
    const w = el.style.width;
    el.style.width = '0';
    setTimeout(() => { el.style.width = w; }, 300);
  });
}

// ── Intersection observers ─────────────────────────────────────────────────
const io = new IntersectionObserver(entries => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.style.opacity = '1';
      e.target.style.transform = 'translateY(0)';
    }
  });
}, { threshold: 0.1 });

const metricsIo = new IntersectionObserver(entries => {
  entries.forEach(e => { if (e.isIntersecting) { animateMetricBars(); metricsIo.disconnect(); } });
}, { threshold: 0.3 });

document.querySelectorAll('.pipe-step,.team-card,.proof-card,.sensor-card,.stat').forEach(el => {
  el.style.opacity = '0';
  el.style.transform = 'translateY(18px)';
  el.style.transition = 'opacity .5s ease, transform .5s ease';
  io.observe(el);
});

document.querySelector('.metrics') && metricsIo.observe(document.querySelector('.metrics'));

// ── Terminal live log ──────────────────────────────────────────────────────
const log = document.getElementById('terminal-log');
const lines = [
  { t: 'line-info',   msg: '$ python generate_data.py' },
  { t: 'line-normal', msg: '[✓] Dataset saved: 1050 rows (1000 normal + 50 anomalies)' },
  { t: 'line-info',   msg: '$ python train_model.py' },
  { t: 'line-info',   msg: '[1/4] Loading data...' },
  { t: 'line-info',   msg: '[2/4] Scaling features...' },
  { t: 'line-info',   msg: '[3/4] Training Isolation Forest model...' },
  { t: 'line-normal', msg: '[4/4] Saving model and scaler...' },
  { t: 'line-normal', msg: 'Training complete.' },
  { t: 'line-normal', msg: '  Total samples : 1050' },
  { t: 'line-warn',   msg: '  Flagged anomalies : 53 (5.0%)' },
  { t: 'line-normal', msg: '  Model saved   : models/anomaly_model.pkl' },
  { t: 'line-info',   msg: '$ python detect_anomalies.py' },
  { t: 'line-info',   msg: '[1/4] Loading model, scaler and data...' },
  { t: 'line-info',   msg: '[2/4] Running anomaly detection...' },
  { t: 'line-info',   msg: '[3/4] Saving results...' },
  { t: 'line-normal', msg: 'Detection Summary' },
  { t: 'line-normal', msg: '  Total samples   : 1050' },
  { t: 'line-anomaly', msg: '  Anomalies found : 53 (5.0%)' },
  { t: 'line-normal', msg: '  Results saved   : outputs/results.csv' },
  { t: 'line-info',   msg: '[4/4] Generating visualisation...' },
  { t: 'line-normal', msg: '  Plot saved: outputs/anomaly_detection_report.png' },
  { t: 'line-normal', msg: 'Done. Review outputs/ folder for full results.' },
  { t: 'line-info',   msg: '' },
  { t: 'line-info',   msg: '$ # Watching live sensor stream...' },
];

let lineIdx = 0;
function printNextLine() {
  if (lineIdx >= lines.length) { lineIdx = 13; }
  const { t, msg } = lines[lineIdx++];
  const div = document.createElement('div');
  div.className = t;
  div.textContent = msg || ' ';
  log.appendChild(div);
  log.scrollTop = log.scrollHeight;
  setTimeout(printNextLine, lineIdx < 13 ? 180 : 800);
}
printNextLine();

// ── Live anomaly score chart ───────────────────────────────────────────────
const labels = Array.from({ length: 60 }, (_, i) => i + 1);
const normalScore  = () => parseFloat((0.04 + Math.random() * 0.1).toFixed(3));
const anomalyScore = () => parseFloat((-0.15 - Math.random() * 0.2).toFixed(3));

const scoreData = labels.map((_, i) => [5,18,34,47,55].includes(i) ? anomalyScore() : normalScore());

const pointColors = scoreData.map(v => v < 0 ? 'rgba(248,113,113,1)' : 'rgba(74,222,128,1)');

const ctx = document.getElementById('scoreChart').getContext('2d');
const scoreChart = new Chart(ctx, {
  type: 'line',
  data: {
    labels,
    datasets: [{
      label: 'Anomaly Score',
      data: scoreData,
      borderColor: 'rgba(56,189,248,0.7)',
      borderWidth: 1.5,
      pointRadius: 3,
      pointBackgroundColor: pointColors,
      fill: {
        target: { value: 0 },
        above: 'rgba(74,222,128,0.05)',
        below: 'rgba(248,113,113,0.15)'
      },
      tension: 0.3
    }]
  },
  options: {
    responsive: true,
    animation: { duration: 800 },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: ctx => `Score: ${ctx.raw} ${ctx.raw < 0 ? '⚠ ANOMALY' : '✓ NORMAL'}`
        }
      }
    },
    scales: {
      x: { grid: { color: '#1e293b' }, ticks: { color: '#64748b', font: { size: 10 } } },
      y: {
        grid: { color: '#1e293b' },
        ticks: { color: '#64748b', font: { size: 10 } },
        border: { dash: [4, 4] }
      }
    }
  }
});

// Add zero threshold line plugin
Chart.register({
  id: 'zeroLine',
  afterDraw(chart) {
    const { ctx, scales: { y, x } } = chart;
    const yZero = y.getPixelForValue(0);
    ctx.save();
    ctx.strokeStyle = 'rgba(248,113,113,0.6)';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(x.left, yZero);
    ctx.lineTo(x.right, yZero);
    ctx.stroke();
    ctx.restore();
  }
});

// Push a new point every 2s
setInterval(() => {
  const isAnom = Math.random() < 0.08;
  const newVal = isAnom ? anomalyScore() : normalScore();
  scoreChart.data.labels.push(scoreChart.data.labels.length + 1);
  scoreChart.data.datasets[0].data.push(newVal);
  scoreChart.data.datasets[0].pointBackgroundColor.push(newVal < 0 ? 'rgba(248,113,113,1)' : 'rgba(74,222,128,1)');
  if (scoreChart.data.labels.length > 80) {
    scoreChart.data.labels.shift();
    scoreChart.data.datasets[0].data.shift();
    scoreChart.data.datasets[0].pointBackgroundColor.shift();
  }
  scoreChart.update();
}, 2000);

// ── Pie chart ─────────────────────────────────────────────────────────────
const pie = document.getElementById('pieChart');
if (pie) {
  new Chart(pie.getContext('2d'), {
    type: 'doughnut',
    data: {
      labels: ['Normal (95%)', 'Anomaly (5%)'],
      datasets: [{ data: [1000, 50], backgroundColor: ['rgba(74,222,128,0.8)', 'rgba(248,113,113,0.8)'], borderWidth: 0, hoverOffset: 6 }]
    },
    options: {
      plugins: { legend: { labels: { color: '#94a3b8', font: { size: 11 } } } },
      cutout: '65%'
    }
  });
}

// ── Live sensor cards ──────────────────────────────────────────────────────
function rnd(min, max, dec=2) { return parseFloat((min + Math.random() * (max - min)).toFixed(dec)); }

function updateSensors() {
  const sensors = [
    { id:'ph',   normal:() => rnd(6.8,7.5),        anomaly:() => Math.random()>.5?rnd(2,5):rnd(9.5,12), unit:'',       min:6.5, max:8.5,  safeMin:6.5, safeMax:8.5  },
    { id:'turb', normal:() => rnd(1.1,2.2),         anomaly:() => rnd(18,40),                            unit:' NTU',   min:0,   max:50,   safeMin:0,   safeMax:5    },
    { id:'cl',   normal:() => rnd(0.8,1.4),         anomaly:() => rnd(0,0.05),                           unit:' mg/L',  min:0,   max:5,    safeMin:0.2, safeMax:4    },
    { id:'flow', normal:() => rnd(45,56,1),         anomaly:() => rnd(5,15,1),                           unit:' L/min', min:0,   max:80,   safeMin:35,  safeMax:65   }
  ];
  sensors.forEach(s => {
    const isAnom = s.id === 'cl'; // keep chlorine always anomaly for demo
    const val    = isAnom ? s.anomaly() : s.normal();
    const card   = document.getElementById('card-' + s.id);
    const badge  = document.getElementById('badge-' + s.id);
    const valEl  = document.getElementById('val-'  + s.id);
    const fillEl = document.getElementById('fill-' + s.id);
    if (!card) return;
    valEl.textContent = val + s.unit;
    const pct = Math.min(100, Math.max(0, ((val - s.min) / (s.max - s.min)) * 100));
    fillEl.style.width = pct + '%';
    if (isAnom) {
      card.classList.add('anomaly'); badge.className='sensor-badge anomaly'; badge.textContent='⚠ ANOMALY'; fillEl.classList.add('anomaly');
    } else {
      card.classList.remove('anomaly'); badge.className='sensor-badge normal'; badge.textContent='NORMAL'; fillEl.classList.remove('anomaly');
    }
  });
}
updateSensors();
setInterval(updateSensors, 2000);

// ── Smooth scroll ──────────────────────────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    document.querySelector(a.getAttribute('href'))?.scrollIntoView({behavior:'smooth'});
  });
});

// ── Run counter on load ────────────────────────────────────────────────────
window.addEventListener('load', () => {
  setTimeout(animateCounters, 400);
});
