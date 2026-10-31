# Summary

A long scroll-choreographed LANDING & OPERATIONAL COMMAND page for CycloneWatch AI / ReliefSense (The Coastal Disaster Triage & Emergency Response Engine for the Odisha State Emergency Operations Centre - SEOC). The visual thread runs from a real-time citizen storm photo upload to an automated multimodal triage verdict and tactical agency dispatch dossier. High-urgency crisis print register throughout: storm cream #e7e2d8 ground, emergency deep ink #171717, alert red #ef493c, radar crimson #b92725, paper dossier #fffdf8, and coastal storm loam #12181d for the dark cinematic stages. Anton for all display typography, Inter for body copy, and Martian Mono at 10.5px (+0.18em tracking) for telemetry readouts, GPS coordinates, SCADA feeder IDs, and SEOC timestamps. FIVE pinned scroll-scrubbed stages, all driven by CSS custom properties on :root via a single performant rAF scroll handler:

(1) Hero Stage (280svh, dark coastal storm ground #12181d): A full-bleed canvas drawing animated radar wind vectors and Doppler storm streamlines drifting on sines of atmospheric time. Centered two-line poster lockup ("STATE EMERGENCY OPERATIONS CENTRE / CYCLONEWATCH AI") driven by THREE independent CSS custom properties: --hero-type-y (0 to -90px), --hero-type-scale (1 to 0.74), and --hero-type-alpha (1 to 0), with live telemetry metadata pinned along the bottom edge;

(2) Clip-Wipe Manifesto (260svh, cream ground #e7e2d8): Holds the SEOC disaster response doctrine in 34-percent ink at clamp(32px, 5.2vw, 72px) over 16ch: "WHEN THE EYEWALL MAKES LANDFALL, EVERY SECOND OF RESCUE DISPATCH DEMANDS SUB-SECOND MULTIMODAL INTELLIGENCE." Overlaid by an identical copy in full ink, filled from bottom-up via clip-path: inset(calc(100% - var(--manifesto-wipe)) 0 0) while the whole sentence scales on --manifesto-scale;

(3) Horizontal Incident Rail (340svh, cream ground): An unpadded horizontal track of active field disaster incident cards (Downed 33kV Live Feeder, AIIMS Arterial Inundation, Blocked Highway Banyan Tree, Breached Culvert, Coastal Storm Surge), translated sideways by calc(-1 * progress * overflowWidth) where overflowWidth is dynamically measured, with a hairline alert-red progress scrubber beneath;

(4) The Printed Tactical Dossier Artifact (420svh, dark stage): A paper incident dispatch dossier at 3/4 aspect that dynamically prints itself as you scroll: calculates hazard severity (CRITICAL/HIGH), fills in GPS coordinates, binds the Gemma 4 vision confidence, activates 4 tactical dispatch cues cumulatively (SCADA Feeder Cut, ODRAF Zodiac Mobilization, BMC Dewatering, Route Clearing), prints live dispatch telemetry, and finally opens a dashed 2px ink perforation tear line;

(5) Parallax Radar Isobar Band (300svh, cream ground): 22 stacked atmospheric isobar and ocean wave contour curves generated via sine harmonics (every fifth contour in emergency red), parallaxing on --season-y and --season-scale, while three emergency command phases (Phase 01: Ingestion & EXIF Binding, Phase 02: Gemma 4 Multimodal Triage, Phase 03: Multi-Agency Dispatch) swap cleanly underneath.

Following the pinned stages:
(6) Live Interactive Field Ingestion Studio: Real-time citizen upload dropzone with automated EXIF GPS extraction, automated Odisha disaster corridor fallback simulator, live API connection to FastAPI backend (`/api/triage`), live GeoJSON map feed preview, and instant tactical classification.
(7) Ruled Agency Dispatch Table (ODRAF, TPCODL, BMC Drainage, Odisha Fire Services).
(8) SEOC Standard Operating Procedures Accordion.
(9) Emergency Telemetry Command Footer.

Every word, label, card, and row carries data-rev attributes with staggered micro-delays for a 200+ element authored motion budget.
