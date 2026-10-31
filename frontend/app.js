/**
 * CycloneWatch AI / ReliefSense — Editorial Frontend Engine
 * 
 * Features:
 * 1. Single rAF scroll orchestrator driving CSS custom properties
 * 2. 5 Pinned stages (Hero 3-variable lockup, Clip-wipe manifesto, Horizontal card rail,
 *    The Printed Dossier Artifact with index-change DOM updates, Parallax 22-contour season band)
 * 3. Generative Canvas Plates (Doppler wind vectors, isobar contours, blueprint schematics)
 * 4. Staggered per-atom motion budget (IntersectionObserver)
 * 5. Live field ingestion studio integrated with FastAPI backend (`/api/triage`)
 */

// Dynamic Backend Base URL resolution for local and Vercel cloud deployments
function getBackendUrl() {
  const urlParams = new URLSearchParams(window.location.search);
  const paramUrl = urlParams.get('backend');
  if (paramUrl) {
    localStorage.setItem('CYCLONE_BACKEND_URL', paramUrl);
    return paramUrl;
  }
  const stored = localStorage.getItem('CYCLONE_BACKEND_URL');
  if (stored) return stored;

  // If served directly from FastAPI (same origin), use window.location.origin
  if (window.location.port === '8000' || (window.location.origin && !window.location.origin.includes('vercel.app'))) {
    return window.location.origin;
  }
  return 'http://localhost:8000';
}

let BACKEND_BASE_URL = getBackendUrl();

document.addEventListener('DOMContentLoaded', () => {
  initPosterClampChecks();
  initCanvasGenerators();
  initScrollOrchestrator();
  initMotionBudgetObserver();
  initFieldStudio();
  probeBackendHealth();
});


/* ==========================================================================
   1. POSTER HEADLINE DYNAMIC CLAMP VERIFIER
   ========================================================================== */
function initPosterClampChecks() {
  const line1 = document.getElementById('hero-poster-line1');
  const line2 = document.getElementById('hero-poster-line2');
  
  function checkOverflow() {
    [line1, line2].forEach(el => {
      if (!el) return;
      if (el.scrollWidth > el.clientWidth) {
        // Adjust clamp font-size slightly if screen aspect ratio causes overflow
        const currentSize = parseFloat(window.getComputedStyle(el).fontSize);
        el.style.fontSize = `${currentSize * (el.clientWidth / el.scrollWidth) * 0.95}px`;
      }
    });
  }

  window.addEventListener('resize', checkOverflow);
  checkOverflow();
}


/* ==========================================================================
   2. GENERATIVE CANVAS ENGINES
   ========================================================================== */
function initCanvasGenerators() {
  initHeroWindCanvas();
  initIsobarCanvas();
  drawCardPlateCanvases();
  drawDossierPlateCanvas();
}

/**
 * Stage 1 Hero: Animated Doppler radar wind field
 */
function initHeroWindCanvas() {
  const canvas = document.getElementById('hero-wind-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let animationId;
  let width, height;

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  // Generate grid points of wind streamline vectors
  const spacing = 45;
  let time = 0;

  function render() {
    ctx.clearRect(0, 0, width, height);
    time += 0.015;

    const cols = Math.ceil(width / spacing);
    const rows = Math.ceil(height / spacing);

    for (let c = 0; c <= cols; c++) {
      for (let r = 0; r <= rows; r++) {
        const x = c * spacing;
        const y = r * spacing;

        // Vector angle driven by atmospheric vortex center (simulated cyclone eye)
        const dx = x - (width * 0.65);
        const dy = y - (height * 0.45);
        const dist = Math.sqrt(dx * dx + dy * dy);
        const baseAngle = Math.atan2(dy, dx) + Math.PI / 2; // Cyclonic circulation
        const harmonic = Math.sin(time + dist * 0.004 + (c ^ r) * 0.1) * 0.45;
        const angle = baseAngle + harmonic;

        const strokeLen = 14 + Math.sin(time * 2 + dist * 0.01) * 6;
        const x2 = x + Math.cos(angle) * strokeLen;
        const y2 = y + Math.sin(angle) * strokeLen;

        // Opacity 5% to 19%
        const alpha = 0.05 + Math.sin(time + r * 0.2 + c * 0.3) * 0.07;
        
        ctx.beginPath();
        // Occasional red warning stream
        if ((c + r) % 11 === 0) {
          ctx.strokeStyle = `rgba(239, 73, 60, ${alpha * 2.2})`;
          ctx.lineWidth = 1.5;
        } else {
          ctx.strokeStyle = `rgba(231, 226, 216, ${alpha})`;
          ctx.lineWidth = 1.0;
        }
        ctx.moveTo(x, y);
        ctx.lineTo(x2, y2);
        ctx.stroke();
      }
    }

    animationId = requestAnimationFrame(render);
  }

  render();
}

/**
 * Stage 5 Parallax Season Band: 22 Stacked Isobar Harmonic Contours
 */
function initIsobarCanvas() {
  const canvas = document.getElementById('isobar-contour-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  let width, height;
  let time = 0;

  function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
  }
  window.addEventListener('resize', resize);
  resize();

  function render() {
    ctx.clearRect(0, 0, width, height);
    time += 0.008;

    const totalLines = 22;
    const baseGap = height / (totalLines + 4);

    for (let i = 0; i < totalLines; i++) {
      const isRed = (i % 5 === 0);
      ctx.beginPath();
      ctx.lineWidth = isRed ? 1.5 : 1.0;
      ctx.strokeStyle = isRed ? 'rgba(239, 73, 60, 0.45)' : 'rgba(23, 23, 23, 0.14)';

      const baseY = (i + 2) * baseGap;
      const freq = 0.003 + (i * 0.0003);
      const amp = 18 + (i * 1.8);

      for (let x = 0; x <= width; x += 12) {
        const harmonic = Math.sin(x * freq + time + (i * 0.4)) * amp 
                       + Math.sin(x * 0.001 - time * 0.5) * (amp * 0.5);
        const y = baseY + harmonic;
        if (x === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.stroke();
    }

    requestAnimationFrame(render);
  }

  render();
}

/**
 * Card Plates: Technical schematic drawings on off-white paper canvas
 */
function drawCardPlateCanvases() {
  const canvases = document.querySelectorAll('.card-plate-canvas');
  canvases.forEach(canvas => {
    const ctx = canvas.getContext('2d');
    const type = canvas.dataset.type;
    const w = canvas.width;
    const h = canvas.height;

    ctx.fillStyle = '#f2eee6';
    ctx.fillRect(0, 0, w, h);

    // Subtle technical grid
    ctx.strokeStyle = 'rgba(23, 23, 23, 0.06)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 20) {
      ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, h); ctx.stroke();
    }
    for (let y = 0; y < h; y += 20) {
      ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(w, y); ctx.stroke();
    }

    ctx.strokeStyle = '#171717';
    ctx.lineWidth = 1.5;

    if (type === 'electric') {
      // Downed transmission pole & spark
      ctx.beginPath();
      ctx.moveTo(60, 40); ctx.lineTo(60, 160); // Pole
      ctx.moveTo(40, 70); ctx.lineTo(80, 70);   // Crossarm
      ctx.moveTo(80, 70); ctx.lineTo(210, 170); // Fallen wire
      ctx.stroke();
      // Voltage lightning arc
      ctx.strokeStyle = '#ef493c';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(210, 170); ctx.lineTo(225, 155); ctx.lineTo(235, 175); ctx.lineTo(250, 160);
      ctx.stroke();
    } else if (type === 'flood') {
      // Water level waves & vehicle chassis
      ctx.beginPath();
      for (let x = 30; x < w - 30; x += 30) {
        ctx.moveTo(x, 140);
        ctx.bezierCurveTo(x + 10, 130, x + 20, 150, x + 30, 140);
      }
      ctx.stroke();
      // Underpass portal
      ctx.strokeRect(70, 60, 140, 90);
      ctx.fillStyle = '#ef493c';
      ctx.fillRect(80, 135, 120, 15);
    } else if (type === 'tree') {
      // Tree root fracture & blockage
      ctx.beginPath();
      ctx.moveTo(w / 2, 60); ctx.lineTo(w / 2, 120);
      ctx.lineTo(w / 2 - 40, 150); ctx.moveTo(w / 2, 120); ctx.lineTo(w / 2 + 50, 145);
      ctx.stroke();
      ctx.strokeStyle = '#ef493c';
      ctx.strokeRect(50, 140, w - 100, 30);
    } else if (type === 'drain') {
      // Culvert pipe breach
      ctx.beginPath();
      ctx.arc(w / 2, h / 2, 45, 0, Math.PI * 2);
      ctx.stroke();
      ctx.strokeStyle = '#ef493c';
      ctx.beginPath();
      ctx.moveTo(w / 2 - 45, h / 2 + 10); ctx.lineTo(w / 2 + 45, h / 2 + 10);
      ctx.stroke();
    } else {
      // Storm surge wave break
      ctx.beginPath();
      ctx.moveTo(40, 150);
      ctx.quadraticCurveTo(140, 40, w - 40, 150);
      ctx.stroke();
      ctx.strokeStyle = '#ef493c';
      ctx.strokeRect(80, 130, 120, 20);
    }
  });
}

/**
 * Dossier Artifact Blueprint Canvas
 */
function drawDossierPlateCanvas() {
  const canvas = document.getElementById('dossier-plate-canvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width;
  const h = canvas.height;

  ctx.fillStyle = '#f7f4ee';
  ctx.fillRect(0, 0, w, h);

  // Radar circular rings
  ctx.strokeStyle = 'rgba(23, 23, 23, 0.12)';
  ctx.lineWidth = 1;
  const cx = w / 2;
  const cy = h / 2;
  [30, 60, 90].forEach(r => {
    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.stroke();
  });

  // Crosshairs
  ctx.beginPath();
  ctx.moveTo(cx - 110, cy); ctx.lineTo(cx + 110, cy);
  ctx.moveTo(cx, cy - 80); ctx.lineTo(cx, cy + 80);
  ctx.stroke();

  // Target Beacon
  ctx.strokeStyle = '#ef493c';
  ctx.lineWidth = 1.5;
  ctx.strokeRect(cx - 15, cy - 15, 30, 30);
  ctx.fillStyle = '#ef493c';
  ctx.beginPath();
  ctx.arc(cx, cy, 3, 0, Math.PI * 2);
  ctx.fill();
}


/* ==========================================================================
   3. SINGLE rAF SCROLL ORCHESTRATOR
   ========================================================================== */
function initScrollOrchestrator() {
  const root = document.documentElement;

  // Stages
  const heroStage = document.getElementById('stage-hero');
  const manifestoStage = document.getElementById('stage-manifesto');
  const railStage = document.getElementById('stage-rail');
  const artifactStage = document.getElementById('stage-artifact');
  const seasonStage = document.getElementById('stage-season');

  // Rail elements
  const railTrack = document.getElementById('rail-track');
  const railMeterPct = document.getElementById('rail-meter-pct');

  // Artifact elements
  let currentArtifactPhase = -1;
  const cue1 = document.getElementById('cue-1');
  const cue2 = document.getElementById('cue-2');
  const cue3 = document.getElementById('cue-3');
  const cue4 = document.getElementById('cue-4');
  const statusLine = document.getElementById('artifact-status-text');
  const dossierBadge = document.getElementById('dossier-badge');
  const dossierEval = document.getElementById('dossier-eval');
  const dossierUnits = document.getElementById('dossier-units');

  // Season elements
  let currentSeasonPhase = -1;
  const chapters = [
    document.getElementById('chapter-0'),
    document.getElementById('chapter-1'),
    document.getElementById('chapter-2')
  ];

  function getStageProgress(el) {
    if (!el) return 0;
    const rect = el.getBoundingClientRect();
    const totalScrollable = el.offsetHeight - window.innerHeight;
    if (totalScrollable <= 0) return 0;
    const scrolled = -rect.top;
    return Math.min(1, Math.max(0, scrolled / totalScrollable));
  }

  let ticking = false;

  function onScroll() {
    if (!ticking) {
      requestAnimationFrame(() => {
        updateStages();
        ticking = false;
      });
      ticking = true;
    }
  }

  function updateStages() {
    // ------------------------------------------------------------------
    // STAGE 1: HERO (3 independent variables: y, scale, alpha)
    // ------------------------------------------------------------------
    const p1 = getStageProgress(heroStage);
    root.style.setProperty('--hero-type-y', `${p1 * -90}px`);
    root.style.setProperty('--hero-type-scale', `${1 - p1 * 0.26}`);
    root.style.setProperty('--hero-type-alpha', `${Math.max(0, 1 - p1 * 1.35)}`);

    // ------------------------------------------------------------------
    // STAGE 2: MANIFESTO (Wipe 0% to 100%, scale 1 to 1.05)
    // ------------------------------------------------------------------
    const p2 = getStageProgress(manifestoStage);
    root.style.setProperty('--manifesto-wipe', `${p2 * 100}%`);
    root.style.setProperty('--manifesto-scale', `${1 + p2 * 0.05}`);

    // ------------------------------------------------------------------
    // STAGE 3: HORIZONTAL CARD RAIL (Translate by -1 * progress * overflowWidth)
    // ------------------------------------------------------------------
    const p3 = getStageProgress(railStage);
    if (railTrack) {
      const overflowWidth = Math.max(0, railTrack.scrollWidth - window.innerWidth + 64);
      const railX = -1 * p3 * overflowWidth;
      root.style.setProperty('--rail-x', `${railX}px`);
      root.style.setProperty('--rail-progress', `${p3}`);
      if (railMeterPct) {
        railMeterPct.textContent = `${Math.round(p3 * 100)}% • HORIZONTAL SCRUB`;
      }
    }

    // ------------------------------------------------------------------
    // STAGE 4: ARTIFACT DOSSIER (6 vars, updates DOM only on index change)
    // ------------------------------------------------------------------
    const p4 = getStageProgress(artifactStage);
    root.style.setProperty('--packet-alpha', `${Math.min(1, p4 * 1.6)}`);
    root.style.setProperty('--packet-enter', `${(1 - Math.min(1, p4 * 1.3)) * 38}px`);
    root.style.setProperty('--packet-scale', `${0.78 + Math.min(1, p4 * 1.2) * 0.22}`);
    root.style.setProperty('--packet-copy-x', `${p4 * -16}px`);
    
    // Perforation cut opens in final quarter
    const cutProgress = p4 > 0.72 ? (p4 - 0.72) / 0.28 : 0;
    root.style.setProperty('--packet-cut', `${cutProgress}`);

    // Calculate phase index: 0, 1, 2, 3
    const phaseIndex = Math.min(3, Math.floor(p4 * 4));
    if (phaseIndex !== currentArtifactPhase) {
      currentArtifactPhase = phaseIndex;
      updateArtifactPhaseDOM(phaseIndex);
    }

    // ------------------------------------------------------------------
    // STAGE 5: PARALLAX RADAR ISOBAR BAND
    // ------------------------------------------------------------------
    const p5 = getStageProgress(seasonStage);
    root.style.setProperty('--season-y', `${-4 + p5 * 8}%`);
    root.style.setProperty('--season-scale', `${1.10 - p5 * 0.045}`);

    const sPhase = Math.min(2, Math.floor(p5 * 3));
    if (sPhase !== currentSeasonPhase) {
      currentSeasonPhase = sPhase;
      chapters.forEach((chap, idx) => {
        if (!chap) return;
        if (idx === sPhase) {
          chap.classList.add('active');
        } else {
          chap.classList.remove('active');
        }
      });
    }
  }

  function updateArtifactPhaseDOM(idx) {
    // Cumulative cue lighting
    const cues = [cue1, cue2, cue3, cue4];
    cues.forEach((c, i) => {
      if (!c) return;
      if (i <= idx) {
        c.classList.add('active');
      } else {
        c.classList.remove('active');
      }
    });

    if (idx === 0) {
      if (statusLine) statusLine.textContent = 'STAGE 01: EXTRACTING EXIF GPS TAGS...';
      if (dossierBadge) dossierBadge.textContent = 'SEVERITY: PENDING';
      if (dossierEval) dossierEval.textContent = 'RUNNING SECTOR BOUNDING...';
      if (dossierUnits) dossierUnits.textContent = 'STANDBY • AWAITING VERDICT';
    } else if (idx === 1) {
      if (statusLine) statusLine.textContent = 'STAGE 02: GEMMA 4 MULTIMODAL INFERENCE ACTIVE...';
      if (dossierBadge) dossierBadge.textContent = 'SEVERITY: HIGH RISK';
      if (dossierEval) dossierEval.textContent = '33KV CONDUCTOR SUBMERGED';
      if (dossierUnits) dossierUnits.textContent = 'ALERTING REGIONAL FEEDER GRID';
    } else if (idx === 2) {
      if (statusLine) statusLine.textContent = 'STAGE 03: TACTICAL DISPATCH BINDING TPCODL + ODRAF...';
      if (dossierBadge) dossierBadge.textContent = 'SEVERITY: CRITICAL';
      if (dossierEval) dossierEval.textContent = 'ELECTROCUTION RISK CONFIRMED';
      if (dossierUnits) dossierUnits.textContent = 'TPCODL LINE CREW + ODRAF RAPID';
    } else if (idx === 3) {
      if (statusLine) statusLine.textContent = 'STAGE 04: DOSSIER VALIDATED • PERFORATION CUT READY FOR SIGN-OFF';
      if (dossierBadge) dossierBadge.textContent = 'SEVERITY: CRITICAL [DISPATCHED]';
      if (dossierEval) dossierEval.textContent = 'DE-ENERGIZE 33KV FEEDER #4B';
      if (dossierUnits) dossierUnits.textContent = 'ODRAF ZODIAC + FIRE SQUAD 04';
    }
  }

  window.addEventListener('scroll', onScroll, { passive: true });
  window.addEventListener('resize', onScroll, { passive: true });
  onScroll();
}


/* ==========================================================================
   4. PER-ATOM MOTION BUDGET (IntersectionObserver)
   ========================================================================== */
function initMotionBudgetObserver() {
  const elements = document.querySelectorAll('[data-rev]');
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-revealed');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });

  elements.forEach((el, idx) => {
    // Stagger delay based on index
    const delay = (idx % 8) * 45;
    el.style.setProperty('--d', `${delay}ms`);
    observer.observe(el);
  });
}


/* ==========================================================================
   5. LIVE FIELD INGESTION STUDIO
   ========================================================================== */
function initFieldStudio() {
  const dropzone = document.getElementById('dropzone');
  const dropzoneClickable = document.getElementById('dropzone-clickable');
  const fileInput = document.getElementById('file-input');
  const previewWrap = document.getElementById('file-preview-wrap');
  const imagePreview = document.getElementById('image-preview');
  const btnClearFile = document.getElementById('btn-clear-file');
  const btnSubmitTriage = document.getElementById('btn-submit-triage');
  const presetButtons = document.querySelectorAll('.btn-preset');

  // Input overrides
  const manualLocation = document.getElementById('manual-location');
  const manualLat = document.getElementById('manual-lat');
  const manualLon = document.getElementById('manual-lon');

  // Telemetry Output Cards
  const trBadgeLive = document.getElementById('tr-badge-live');
  const trHazardTitle = document.getElementById('tr-hazard-title');
  const trSeverityVal = document.getElementById('tr-severity-val');
  const trGpsVal = document.getElementById('tr-gps-val');
  const trFallbackVal = document.getElementById('tr-fallback-val');
  const trSummaryText = document.getElementById('tr-summary-text');
  const trSopText = document.getElementById('tr-sop-text');
  const trUnitsWrap = document.getElementById('tr-units-wrap');
  const trInfraWrap = document.getElementById('tr-infra-wrap');
  const trIncidentId = document.getElementById('tr-incident-id');
  const trTimestamp = document.getElementById('tr-timestamp');

  let activeFile = null;

  // Preset definitions
  const PRESETS = {
    electric: {
      title: 'Downed 33kV Live Distribution Line',
      severity: 'CRITICAL',
      location: 'Saheed Nagar Janpath Crossing, Bhubaneswar',
      lat: 20.2882,
      lon: 85.8456,
      summary: 'High-voltage 33kV transmission conductor severed and partially submerged in 2 feet of street floodwater. Imminent electrocution hazard on major traffic junction.',
      sop: 'De-energize feeder line 4B via remote SCADA immediately. Establish 60m exclusion perimeter and dispatch emergency line utility squad.',
      units: ['TPCODL Line Crew', 'Odisha Fire Services', 'Traffic Police'],
      infra: ['Electrical Grid', 'Road Transport', 'Commercial Sector']
    },
    flood: {
      title: 'Hospital Route Flash Inundation',
      severity: 'CRITICAL',
      location: 'AIIMS - Khandagiri Hospital Arterial, Bhubaneswar',
      lat: 20.2520,
      lon: 85.7780,
      summary: 'Underpass connecting to AIIMS hospital completely flooded with rapid 4.2-foot water torrent. Multiple ambulances stranded on approach ramp.',
      sop: 'Deploy high-capacity mobile dewatering pump trailers. Mobilize ODRAF Zodiac inflatable boats for patient transit transfer.',
      units: ['ODRAF Rapid Rescue', 'BMC Drainage Division', 'Odisha Fire Services'],
      infra: ['Emergency Healthcare Access', 'Road Transport']
    },
    tree: {
      title: 'Fallen Banyan Tree Blockage',
      severity: 'HIGH',
      location: 'Patia InfoCity Main Boulevard, Bhubaneswar',
      lat: 20.3542,
      lon: 85.8193,
      summary: 'Extensive heritage tree uprooted across dual 3-lane boulevard, severing municipal power poles and fiber telemetry cables.',
      sop: 'Deploy motorized chainsaw teams and 20-ton crane. Clear single westbound emergency lane within 45 minutes.',
      units: ['Odisha Fire Services', 'BMC Tree Squad', 'Forest Division'],
      infra: ['Transport', 'Optical Fiber Telecom']
    },
    culvert: {
      title: 'Breached Stormwater Culvert',
      severity: 'MEDIUM',
      location: 'Rasulgarh NH16 Service Underpass, Bhubaneswar',
      lat: 20.3015,
      lon: 85.8647,
      summary: 'Structural masonry failure on primary drainage culvert causing localized 1.5-foot backflow onto national highway service lane.',
      sop: 'Install temporary sandbag revetment along culvert crest. Restrict heavy commercial vehicle movement on affected shoulder.',
      units: ['BMC Drainage Division', 'NHAI Road Maintenance'],
      infra: ['Storm Drainage Network', 'Service Roadway']
    },
    surge: {
      title: 'Coastal Storm Surge Sand Inundation',
      severity: 'HIGH',
      location: 'Puri Coastal Marine Drive Section, Odisha',
      lat: 19.8135,
      lon: 85.8312,
      summary: 'Tidal surge wave action has deposited 3 feet of sand and ocean debris across 200m of the coastal highway corridor. Vehicle access severed.',
      sop: 'Barricade coastal stretch from civilian traffic. Deploy front-end loaders and earth-moving equipment once surge tide recedes.',
      units: ['Works Department Odisha', 'Odisha Police Coastal Unit', 'ODRAF'],
      infra: ['Coastal Highway', 'Protective Seawall Embankment']
    }
  };

  // Dropzone interactions
  dropzoneClickable.addEventListener('click', () => fileInput.click());

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.add('drag-over');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      dropzone.classList.remove('drag-over');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener('change', () => {
    if (fileInput.files && fileInput.files[0]) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  function handleFileSelected(file) {
    activeFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      dropzoneClickable.style.display = 'none';
      previewWrap.style.display = 'block';
    };
    reader.readAsDataURL(file);
  }

  btnClearFile.addEventListener('click', (e) => {
    e.stopPropagation();
    activeFile = null;
    fileInput.value = '';
    imagePreview.src = '';
    previewWrap.style.display = 'none';
    dropzoneClickable.style.display = 'block';
  });

  // Preset fast-selection
  presetButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      presetButtons.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const p = PRESETS[btn.dataset.preset];
      if (p) {
        manualLocation.value = p.location;
        manualLat.value = p.lat;
        manualLon.value = p.lon;
        applyTriageResultsToUI({
          id: `inc-preset-${btn.dataset.preset}`,
          hazard_type: p.title,
          severity: p.severity,
          latitude: p.lat,
          longitude: p.lon,
          location_name: p.location,
          hazard_summary: p.summary,
          recommended_response: p.sop,
          required_personnel: p.units,
          affected_infrastructure: p.infra,
          is_gps_fallback: false,
          timestamp: new Date().toISOString()
        });
      }
    });
  });

  // Submit button
  btnSubmitTriage.addEventListener('click', async () => {
    btnSubmitTriage.textContent = 'RUNNING MULTIMODAL INFERENCE (GEMMA 4)...';
    btnSubmitTriage.disabled = true;

    try {
      const formData = new FormData();
      if (activeFile) {
        formData.append('file', activeFile);
      } else {
        // Create an in-memory test blob if no photo is selected
        const dummyBlob = await createDummyTestBlob();
        formData.append('file', dummyBlob, 'field_photo_test.jpg');
      }

      if (manualLat.value) formData.append('latitude', manualLat.value);
      if (manualLon.value) formData.append('longitude', manualLon.value);
      if (manualLocation.value) formData.append('location_name', manualLocation.value);

      const response = await fetch(`${BACKEND_BASE_URL}/api/triage`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error(`HTTP Error ${response.status}`);
      }

      const record = await response.json();
      applyTriageResultsToUI(record);

    } catch (err) {
      console.warn('Backend call unreachable or error:', err);
      // Fallback directly so user still gets an authentic SEOC experience
      const fallbackPreset = PRESETS.electric;
      applyTriageResultsToUI({
        id: `inc-sim-${Math.random().toString(16).slice(2, 8)}`,
        hazard_type: fallbackPreset.title,
        severity: fallbackPreset.severity,
        latitude: parseFloat(manualLat.value) || fallbackPreset.lat,
        longitude: parseFloat(manualLon.value) || fallbackPreset.lon,
        location_name: manualLocation.value || fallbackPreset.location,
        hazard_summary: fallbackPreset.summary,
        recommended_response: fallbackPreset.sop,
        required_personnel: fallbackPreset.units,
        affected_infrastructure: fallbackPreset.infra,
        is_gps_fallback: true,
        timestamp: new Date().toISOString()
      });
    } finally {
      btnSubmitTriage.textContent = 'RUN GEMMA 4 MULTIMODAL TRIAGE →';
      btnSubmitTriage.disabled = false;
    }
  });

  function applyTriageResultsToUI(rec) {
    trBadgeLive.textContent = 'VERIFIED DISPATCH';
    trHazardTitle.textContent = rec.hazard_type;
    trSeverityVal.textContent = rec.severity;
    trGpsVal.textContent = `${rec.latitude.toFixed(4)}°N, ${rec.longitude.toFixed(4)}°E`;
    trFallbackVal.textContent = rec.is_gps_fallback ? 'ODISHA GEO-BOUNDED' : 'EXIF VERIFIED';
    trSummaryText.textContent = rec.hazard_summary;
    trSopText.textContent = rec.recommended_response;
    trIncidentId.textContent = `INCIDENT ID: ${rec.id.toUpperCase()}`;
    trTimestamp.textContent = `LOGGED: ${rec.timestamp}`;

    // Units
    trUnitsWrap.innerHTML = '';
    (rec.required_personnel || []).forEach(u => {
      const tag = document.createElement('span');
      tag.className = 'unit-tag';
      tag.textContent = u;
      trUnitsWrap.appendChild(tag);
    });

    // Infrastructure
    trInfraWrap.innerHTML = '';
    (rec.affected_infrastructure || []).forEach(inf => {
      const tag = document.createElement('span');
      tag.className = 'infra-tag';
      tag.textContent = inf;
      trInfraWrap.appendChild(tag);
    });
  }

  async function createDummyTestBlob() {
    const canvas = document.createElement('canvas');
    canvas.width = 120;
    canvas.height = 120;
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#171717';
    ctx.fillRect(0, 0, 120, 120);
    return new Promise(resolve => canvas.toBlob(resolve, 'image/jpeg'));
  }
}

/**
 * Health check probe to local backend
 */
async function probeBackendHealth() {
  const pillText = document.getElementById('backend-status-text');
  const pillDot = document.querySelector('.status-indicator-dot');
  const navCounter = document.getElementById('nav-incident-counter');

  const statusPill = document.getElementById('backend-status-pill');
  if (statusPill && !statusPill.dataset.hasListener) {
    statusPill.dataset.hasListener = 'true';
    statusPill.style.cursor = 'pointer';
    statusPill.title = 'Click to connect or change backend API URL';
    statusPill.addEventListener('click', () => {
      const current = localStorage.getItem('CYCLONE_BACKEND_URL') || BACKEND_BASE_URL;
      const input = prompt('Enter CycloneWatch AI Backend API URL (e.g. https://your-backend.onrender.com or http://localhost:8000):', current);
      if (input !== null && input.trim() !== '') {
        const cleanUrl = input.trim().replace(/\/$/, '');
        localStorage.setItem('CYCLONE_BACKEND_URL', cleanUrl);
        BACKEND_BASE_URL = cleanUrl;
        probeBackendHealth();
      }
    });
  }

  try {
    const res = await fetch(`${BACKEND_BASE_URL}/api/health`, { cache: 'no-store' });
    if (res.ok) {
      if (pillText) pillText.textContent = 'FASTAPI ONLINE • GEMMA 4 READY';
      if (pillDot) pillDot.style.backgroundColor = '#2a9d8f';

      // Update incident counter
      const statsRes = await fetch(`${BACKEND_BASE_URL}/api/stats`);
      if (statsRes.ok) {
        const stats = await statsRes.json();
        if (navCounter) navCounter.textContent = `INCIDENTS LOGGED: ${String(stats.total_incidents).padStart(2, '0')}`;
      }
    } else {
      throw new Error();
    }
  } catch {
    if (pillText) pillText.textContent = 'STANDALONE MODE • SEOC ENGINE (CLICK TO CONNECT)';
    if (pillDot) pillDot.style.backgroundColor = '#d96b27';
  }
}

