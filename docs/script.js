// Live sensor simulation
const sensors = [
  { id: "ph-val",   statusId: "ph-card",   normal: () => (6.8 + Math.random() * 0.5).toFixed(2),         anomaly: () => (Math.random() > 0.5 ? (2 + Math.random() * 2).toFixed(2) : (10 + Math.random()).toFixed(2)), unit: "" },
  { id: "turb-val", statusId: "turb-card", normal: () => (1.2 + Math.random() * 0.6).toFixed(2) + " NTU", anomaly: () => (18 + Math.random() * 10).toFixed(1) + " NTU", unit: "" },
  { id: "cl-val",   statusId: "cl-card",   normal: () => (0.8 + Math.random() * 0.4).toFixed(2) + " mg/L", anomaly: () => (Math.random() * 0.04).toFixed(3) + " mg/L", unit: "" },
  { id: "flow-val", statusId: "flow-card", normal: () => (47 + Math.random() * 6).toFixed(1) + " L/min",  anomaly: () => (5 + Math.random() * 5).toFixed(1) + " L/min", unit: "" }
];

function updateSensors() {
  sensors.forEach((s, i) => {
    const card      = document.getElementById(s.statusId);
    const valueEl   = document.getElementById(s.id);
    const statusEl  = card ? card.querySelector(".sensor-status") : null;
    if (!valueEl || !statusEl) return;

    // cl-card is always anomaly for demo effect
    const isAnom = s.statusId === "cl-card";
    valueEl.textContent = isAnom ? s.anomaly() : s.normal();
    if (isAnom) {
      card.classList.add("anomaly-card");
      statusEl.className = "sensor-status anomaly";
      statusEl.textContent = "⚠ ANOMALY";
    } else {
      card.classList.remove("anomaly-card");
      statusEl.className = "sensor-status normal";
      statusEl.textContent = "NORMAL";
    }
  });
}

// Animate score counter
function animateScore(el, target, duration = 1500) {
  const start = performance.now();
  const from  = 0;
  function tick(now) {
    const t = Math.min((now - start) / duration, 1);
    el.textContent = Math.round(from + t * (target - from));
    if (t < 1) requestAnimationFrame(tick);
  }
  requestAnimationFrame(tick);
}

// Smooth scroll for nav links
document.querySelectorAll("a[href^='#']").forEach(a => {
  a.addEventListener("click", e => {
    e.preventDefault();
    document.querySelector(a.getAttribute("href"))
      ?.scrollIntoView({ behavior: "smooth" });
  });
});

// Intersection observer — animate cards on scroll
const observer = new IntersectionObserver(entries => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.style.opacity = "1";
      entry.target.style.transform = "translateY(0)";
    }
  });
}, { threshold: 0.1 });

document.querySelectorAll(".card, .team-card, .stack-item, .step").forEach(el => {
  el.style.opacity    = "0";
  el.style.transform  = "translateY(20px)";
  el.style.transition = "opacity 0.5s ease, transform 0.5s ease";
  observer.observe(el);
});

// Start live sensor updates
updateSensors();
setInterval(updateSensors, 2000);
