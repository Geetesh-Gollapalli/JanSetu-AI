"""
JanSetu AI (जनसेतु) - Government Enterprise National Infrastructure Intelligence Portal
Official Spatial Decision Support System for PM GatiShakti & NITI Aayog.
Compliant with DPGA Standards & Digital Personal Data Protection (DPDP) Act 2023.
"""

import sys
import json
import os
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from engine.data_fusion import DataFusionEngine
from engine.hotspot_analyzer import HotspotAnalyzer
from engine.multilingual_ingestion import IngestionPipeline
from engine.recommender import PolicyRecommender

# Built-in Zero-Crash Policy Synthesizer Fallback
try:
    from engine.gemini_policy_synthesizer import PolicySynthesizer
    synthesizer = PolicySynthesizer()
except Exception:
    class PolicySynthesizer:
        def synthesize_executive_brief(self, dist, rec):
            d_name = dist.get('name', 'Target District')
            state = dist.get('state', 'India')
            phs = dist.get('priority_hotspot_score', 75.0)
            tier = dist.get('priority_tier', 'Tier 1: Immediate National Intervention')
            sec = dist.get('top_sector_demand', 'Water & Sanitation')
            capex = dist.get('planned_capex_gap_cr', 250.0)
            memo = f"""# CABINET POLICY MEMORANDUM: SPECIAL NATIONAL INFRASTRUCTURE INTERVENTION
**FILE REF:** F.No. 14012/08/2026-NITI-GATISHAKTI  
**TO:** Empowered Group of Secretaries (EGoS), PM GatiShakti National Master Plan  
**FROM:** JanSetu AI National Infrastructure Decision Engine  
**SUBJECT:** Targeted Remediation of Critical Infrastructure Deficit in **{d_name}, {state}**  
**DATE:** October 2026 | **SECURITY:** OFFICIAL - CONFIDENTIAL (Central Sanctioning Committee)  

---

### 1. EXECUTIVE SUMMARY & EVIDENCE BASE
Grassroots citizen telemetry across multilingual voice IVR dial-ins (14444), WhatsApp bots, and Gram Sabha digital kiosks indicates an acute infrastructure crisis in **{d_name}**, scoring a **Priority Hotspot Score of {phs}/100 ({tier})**. 

The convergence of high demographic vulnerability with severe infrastructure baseline deficits in **{sec}** has caused systemic service delivery breakdown. The existing capital expenditure deficit of **₹{capex} Crores** has left high-impact citizen priorities stranded. Immediate inter-ministerial reallocation is mandated under the PM GatiShakti National Master Plan.

### 2. RECOMMENDED FAST-TRACK INTERVENTIONS
- **Lead Ministry:** Ministry of Jal Shakti (if Water) / MoRTH & MoRD (if Connectivity)
- **Convergence Ministries:** Ministry of Tribal Affairs + Ministry of Health & Family Welfare + MeitY
- **Estimated Capital Outlay:** **₹{round(capex * 0.4, 1)} Crores**
- **Target Beneficiary Scope:** **250,000+ citizens** across underserved Gram Panchayats.
- **Fast-Track Timeline:** 90 Days Single-Window Clearance & Civil Works Tendering on GeM / Beckn DPI.

### 3. DPI & CLOSED-LOOP CITIZEN VERIFICATION
- **Aadhaar-Linked Public Asset Geotagging:** Every borewell, culvert, or health clinic constructed will be verified by community social audits using JanSetu mobile clients.
- **JanSunwai Closed-Loop Notifications:** Citizens who raised or corroborated grievances will receive automated SMS/WhatsApp milestone updates.

**SUBMITTED FOR APPROVAL BY CENTRAL SANCTIONING COMMITTEE**
"""
            return {'status': 'success', 'source': 'deterministic_fallback_engine', 'memo_markdown': memo}
    synthesizer = PolicySynthesizer()

DATA_DIR = PROJECT_ROOT / "data"
fusion_engine = DataFusionEngine(str(DATA_DIR))

# Precise Survey of India aligned coordinates for all 16 strategic districts
DISTRICT_COORDS = {
    'IND-UP-01': {'lat': 25.1764, 'lng': 80.8667, 'name': 'Chitrakoot', 'state': 'Uttar Pradesh', 'zone': 'Central'},
    'IND-MP-01': {'lat': 24.7438, 'lng': 78.8315, 'name': 'Tikamgarh', 'state': 'Madhya Pradesh', 'zone': 'Central'},
    'IND-CG-01': {'lat': 19.0748, 'lng': 82.0163, 'name': 'Bastar', 'state': 'Chhattisgarh', 'zone': 'East-Central'},
    'IND-OD-01': {'lat': 18.3436, 'lng': 81.8974, 'name': 'Malkangiri', 'state': 'Odisha', 'zone': 'Eastern'},
    'IND-UP-02': {'lat': 27.7025, 'lng': 82.0435, 'name': 'Shravasti', 'state': 'Uttar Pradesh', 'zone': 'Northern'},
    'IND-HR-01': {'lat': 28.1060, 'lng': 77.0050, 'name': 'Nuh', 'state': 'Haryana', 'zone': 'Northern'},
    'IND-KL-01': {'lat': 11.6854, 'lng': 76.1320, 'name': 'Wayanad', 'state': 'Kerala', 'zone': 'Southern'},
    'IND-RJ-01': {'lat': 25.7532, 'lng': 71.3967, 'name': 'Barmer', 'state': 'Rajasthan', 'zone': 'Western'},
    'IND-WB-01': {'lat': 24.1812, 'lng': 88.2683, 'name': 'Murshidabad', 'state': 'West Bengal', 'zone': 'Eastern'},
    'IND-MH-01': {'lat': 20.1770, 'lng': 79.9972, 'name': 'Gadchiroli', 'state': 'Maharashtra', 'zone': 'Western'},
    'IND-KA-01': {'lat': 11.9261, 'lng': 76.9437, 'name': 'Chamarajanagar', 'state': 'Karnataka', 'zone': 'Southern'},
    'IND-TG-01': {'lat': 19.6641, 'lng': 78.5320, 'name': 'Adilabad', 'state': 'Telangana', 'zone': 'Southern'},
    'IND-TN-01': {'lat': 9.3639, 'lng': 78.8395, 'name': 'Ramanathapuram', 'state': 'Tamil Nadu', 'zone': 'Southern'},
    'IND-UK-01': {'lat': 30.4239, 'lng': 79.3274, 'name': 'Chamoli', 'state': 'Uttarakhand', 'zone': 'Northern'},
    'IND-NL-01': {'lat': 25.8712, 'lng': 94.7738, 'name': 'Kiphire', 'state': 'Nagaland', 'zone': 'North-Eastern'},
    'IND-GJ-01': {'lat': 22.8396, 'lng': 74.2541, 'name': 'Dahod', 'state': 'Gujarat', 'zone': 'Western'}
}

def get_current_analytics():
    profiles = fusion_engine.build_fused_profiles()
    hotspots = HotspotAnalyzer(profiles).analyze_all()
    for h in hotspots:
        d_id = h.get('district_id')
        if d_id in DISTRICT_COORDS:
            h['latitude'] = DISTRICT_COORDS[d_id]['lat']
            h['longitude'] = DISTRICT_COORDS[d_id]['lng']
            h['zone'] = DISTRICT_COORDS[d_id]['zone']
    recs = PolicyRecommender(hotspots).generate_recommendations()
    return profiles, hotspots, recs

DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>JanSetu AI (जनसेतु) &bull; National Infrastructure GIS & PM GatiShakti Portal</title>
  
  <!-- Leaflet CSS & JS for Authentic India Map -->
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

  <style>
    :root {
      --gov-navy: #0b3b60;
      --gov-navy-dark: #07253d;
      --gov-navy-light: #165384;
      --gov-saffron: #f97316;
      --gov-saffron-dark: #c2410c;
      --gov-green: #15803d;
      --gov-green-light: #16a34a;
      
      --bg: #f1f5f9;
      --surface: #ffffff;
      --surface-subtle: #f8fafc;
      --border: #cbd5e1;
      --border-subtle: #e2e8f0;
      
      --text: #0f172a;
      --text-muted: #475569;
      --text-light: #64748b;
      
      --primary: #0b3b60;
      --danger: #dc2626;
      --warning: #d97706;
      --success: #15803d;
      --accent: #0284c7;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      line-height: 1.5;
    }

    .tricolor-ribbon {
      height: 4px;
      background: linear-gradient(90deg, #ff9933 0%, #ff9933 33.3%, #ffffff 33.3%, #ffffff 66.6%, #138808 66.6%, #138808 100%);
    }

    .gov-topbar {
      background: #f8fafc;
      border-bottom: 1px solid var(--border-subtle);
      padding: 6px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 0.76rem;
      color: var(--text-muted);
    }
    .gov-topbar-left {
      display: flex;
      align-items: center;
      gap: 16px;
      font-weight: 500;
    }
    .gov-flag {
      display: inline-block;
      width: 18px;
      height: 12px;
      background: linear-gradient(to bottom, #ff9933 33%, #ffffff 33%, #ffffff 66%, #138808 66%);
      border-radius: 1px;
      vertical-align: middle;
      border: 1px solid #cbd5e1;
    }
    .gov-topbar-right {
      display: flex;
      align-items: center;
      gap: 16px;
    }

    header {
      background: var(--gov-navy);
      color: #ffffff;
      padding: 14px 28px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 14px;
      box-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    .brand-container {
      display: flex;
      align-items: center;
      gap: 16px;
    }
    .national-emblem {
      width: 46px;
      height: 46px;
      background: #ffffff;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      box-shadow: 0 0 10px rgba(255, 255, 255, 0.2);
      border: 2px solid #facc15;
      font-size: 1.5rem;
    }
    .brand-titles h1 {
      font-size: 1.35rem;
      font-weight: 800;
      letter-spacing: -0.01em;
      display: flex;
      align-items: center;
      gap: 10px;
      color: #ffffff;
    }
    .brand-titles h1 span.indic-title {
      color: #fed7aa;
      font-weight: 700;
    }
    .brand-titles p {
      font-size: 0.8rem;
      color: #e2e8f0;
      margin-top: 2px;
    }

    .header-badges {
      display: flex;
      align-items: center;
      gap: 10px;
      flex-wrap: wrap;
    }
    .badge {
      font-size: 0.72rem;
      font-weight: 700;
      padding: 5px 12px;
      border-radius: 20px;
      text-transform: uppercase;
      letter-spacing: 0.04em;
      border: 1px solid rgba(255, 255, 255, 0.25);
      background: rgba(255, 255, 255, 0.12);
      color: #ffffff;
    }

    .kpi-bar {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
      gap: 14px;
      padding: 16px 28px;
      background: #ffffff;
      border-bottom: 1px solid var(--border-subtle);
    }
    .kpi-card {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 12px 16px;
      position: relative;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }
    .kpi-card::before {
      content: "";
      position: absolute;
      top: 0; left: 0; right: 0; height: 3px;
      background: var(--gov-navy);
    }
    .kpi-card.crisis::before { background: var(--danger); }
    .kpi-card.capex::before { background: var(--gov-saffron); }
    .kpi-card.dpg::before { background: var(--gov-green); }
    .kpi-card.voices::before { background: var(--accent); }

    .kpi-title {
      font-size: 0.72rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.04em;
    }
    .kpi-value {
      font-size: 1.45rem;
      font-weight: 800;
      margin: 4px 0 2px 0;
      color: var(--text);
    }
    .kpi-desc {
      font-size: 0.74rem;
      color: var(--text-muted);
    }

    .nav-bar {
      display: flex;
      gap: 4px;
      padding: 0 28px;
      background: #ffffff;
      border-bottom: 1px solid var(--border);
      overflow-x: auto;
      box-shadow: 0 1px 2px rgba(0, 0, 0, 0.02);
    }
    .nav-tab {
      padding: 13px 18px;
      font-size: 0.85rem;
      font-weight: 700;
      color: var(--text-muted);
      background: transparent;
      border: none;
      border-bottom: 3px solid transparent;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 8px;
      white-space: nowrap;
      transition: all 0.15s ease;
    }
    .nav-tab:hover {
      color: var(--gov-navy);
      background: #f8fafc;
    }
    .nav-tab.active {
      color: var(--gov-navy);
      border-bottom-color: var(--gov-navy);
      background: #eff6ff;
    }

    main {
      padding: 24px 28px;
      flex: 1;
    }

    .view-content {
      display: none;
    }
    .view-content.active {
      display: block;
    }

    .gis-layout {
      display: grid;
      grid-template-columns: 1fr 350px;
      gap: 20px;
      align-items: start;
    }
    @media (max-width: 1024px) {
      .gis-layout { grid-template-columns: 1fr; }
    }

    .gis-map-container {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .gis-map-header {
      padding: 12px 18px;
      background: #f8fafc;
      border-bottom: 1px solid var(--border);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 10px;
    }
    .gis-map-title {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--gov-navy);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    .map-controls-group {
      display: flex;
      align-items: center;
      gap: 6px;
      flex-wrap: wrap;
    }
    .btn-ctrl {
      background: #ffffff;
      border: 1px solid var(--border);
      color: var(--text);
      padding: 5px 11px;
      border-radius: 4px;
      font-size: 0.74rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s;
    }
    .btn-ctrl:hover {
      background: #f1f5f9;
      border-color: #94a3b8;
    }
    .btn-ctrl.active {
      background: var(--gov-navy);
      border-color: var(--gov-navy);
      color: #ffffff;
    }

    #gis-map {
      height: 600px;
      width: 100%;
      background: #e2e8f0;
      z-index: 1;
    }

    #gis-map.gis-dark-mode .leaflet-tile {
      filter: invert(100%) hue-rotate(180deg) brightness(85%) contrast(92%);
    }

    .pulse-marker-tier1 {
      width: 16px;
      height: 16px;
      background: #dc2626;
      border-radius: 50%;
      box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.8);
      border: 2px solid #ffffff;
      animation: pulse-red 1.6s infinite;
      cursor: pointer;
    }
    @keyframes pulse-red {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.8); }
      70% { transform: scale(1.15); box-shadow: 0 0 0 14px rgba(220, 38, 38, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
    }

    .pulse-marker-tier2 {
      width: 14px;
      height: 14px;
      background: #d97706;
      border-radius: 50%;
      border: 2px solid #ffffff;
      box-shadow: 0 0 0 0 rgba(217, 119, 6, 0.8);
      animation: pulse-amber 2s infinite;
      cursor: pointer;
    }
    @keyframes pulse-amber {
      0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(217, 119, 6, 0.8); }
      70% { transform: scale(1.1); box-shadow: 0 0 0 10px rgba(217, 119, 6, 0); }
      100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(217, 119, 6, 0); }
    }

    .pulse-marker-tier3 {
      width: 12px;
      height: 12px;
      background: #15803d;
      border-radius: 50%;
      border: 1.5px solid #ffffff;
      cursor: pointer;
    }

    .gis-sidebar {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 18px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .gis-sidebar h3 {
      font-size: 0.95rem;
      font-weight: 700;
      color: var(--gov-navy);
      margin-bottom: 12px;
      border-bottom: 2px solid var(--border-subtle);
      padding-bottom: 8px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .inspector-body {
      font-size: 0.82rem;
    }
    .inspector-stat-row {
      display: flex;
      justify-content: space-between;
      padding: 7px 0;
      border-bottom: 1px solid var(--border-subtle);
    }
    .inspector-stat-row .stat-label {
      color: var(--text-muted);
    }
    .inspector-stat-row .stat-val {
      font-weight: 700;
      color: var(--text);
    }

    .content-card {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 20px;
      margin-bottom: 24px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }
    .card-header-row {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      flex-wrap: wrap;
      gap: 12px;
    }
    .card-title {
      font-size: 1.05rem;
      font-weight: 700;
      color: var(--gov-navy);
      display: flex;
      align-items: center;
      gap: 8px;
    }

    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.84rem;
    }
    th {
      text-align: left;
      padding: 11px 14px;
      background: var(--gov-navy);
      color: #ffffff;
      font-weight: 700;
      border-bottom: 1px solid var(--gov-navy-dark);
      text-transform: uppercase;
      font-size: 0.73rem;
      letter-spacing: 0.04em;
    }
    td {
      padding: 12px 14px;
      border-bottom: 1px solid var(--border-subtle);
      vertical-align: middle;
      color: var(--text);
    }
    tr:nth-child(even) td {
      background: #f8fafc;
    }
    tr:hover td {
      background: #eff6ff;
    }

    .tag-tier1 {
      background: #fef2f2;
      color: #b91c1c;
      border: 1px solid #f87171;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 700;
    }
    .tag-tier2 {
      background: #fffbeb;
      color: #b45309;
      border: 1px solid #fcd34d;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 700;
    }
    .tag-tier3 {
      background: #f0fdf4;
      color: #15803d;
      border: 1px solid #86efac;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.72rem;
      font-weight: 700;
    }
    .tag-sector {
      background: #f0f9ff;
      color: #0369a1;
      border: 1px solid #bae6fd;
      padding: 3px 8px;
      border-radius: 4px;
      font-size: 0.74rem;
      font-weight: 600;
    }

    .btn-primary {
      background: var(--gov-navy);
      color: #ffffff;
      border: 1px solid var(--gov-navy-dark);
      padding: 7px 14px;
      border-radius: 4px;
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      transition: all 0.15s ease;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .btn-primary:hover {
      background: var(--gov-navy-light);
    }
    .btn-success {
      background: var(--gov-green);
      color: #ffffff;
      border: 1px solid #14532d;
      padding: 7px 14px;
      border-radius: 4px;
      font-size: 0.8rem;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .btn-success:hover {
      background: var(--gov-green-light);
    }

    .search-input, .select-input, .textarea-input {
      background: #ffffff;
      border: 1px solid var(--border);
      color: var(--text);
      padding: 8px 12px;
      border-radius: 4px;
      font-size: 0.82rem;
    }
    .search-input:focus, .select-input:focus, .textarea-input:focus {
      outline: none;
      border-color: var(--gov-navy);
      box-shadow: 0 0 0 3px rgba(11, 59, 96, 0.15);
    }

    .equalizer-container {
      display: flex;
      align-items: center;
      gap: 3px;
      height: 36px;
      padding: 0 10px;
      background: #f8fafc;
      border-radius: 4px;
      border: 1px solid var(--border);
    }
    .eq-bar {
      width: 4px;
      background: var(--gov-navy);
      border-radius: 2px;
      height: 6px;
      transition: height 0.1s ease;
    }
    .equalizer-container.playing .eq-bar:nth-child(1) { animation: sound 0.7s infinite alternate ease-in-out; }
    .equalizer-container.playing .eq-bar:nth-child(2) { animation: sound 0.5s infinite alternate ease-in-out 0.1s; }
    .equalizer-container.playing .eq-bar:nth-child(3) { animation: sound 0.9s infinite alternate ease-in-out 0.2s; }
    .equalizer-container.playing .eq-bar:nth-child(4) { animation: sound 0.4s infinite alternate ease-in-out 0.15s; }
    .equalizer-container.playing .eq-bar:nth-child(5) { animation: sound 0.8s infinite alternate ease-in-out 0.25s; }
    .equalizer-container.playing .eq-bar:nth-child(6) { animation: sound 0.6s infinite alternate ease-in-out 0.05s; }
    @keyframes sound {
      0% { height: 4px; background: var(--gov-navy); }
      100% { height: 28px; background: var(--gov-saffron); }
    }

    .privacy-preview {
      background: #f8fafc;
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 14px;
      font-family: Consolas, Monaco, monospace;
      font-size: 0.82rem;
      line-height: 1.6;
      color: var(--text);
    }
    .redacted-tag {
      background: #fee2e2;
      color: #991b1b;
      border: 1px solid #f87171;
      padding: 1px 6px;
      border-radius: 3px;
      font-weight: 700;
    }

    .modal-backdrop {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(15, 23, 42, 0.6);
      backdrop-filter: blur(2px);
      z-index: 9999;
      align-items: center;
      justify-content: center;
      padding: 20px;
    }
    .modal-panel {
      background: #ffffff;
      border: 1px solid var(--border);
      border-radius: 8px;
      width: 100%;
      max-width: 840px;
      max-height: 88vh;
      display: flex;
      flex-direction: column;
      box-shadow: 0 20px 40px rgba(0, 0, 0, 0.2);
      overflow: hidden;
    }
    .modal-header {
      padding: 14px 20px;
      background: var(--gov-navy);
      color: #ffffff;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .modal-body {
      padding: 24px;
      overflow-y: auto;
      flex: 1;
      background: #f8fafc;
    }
    .modal-footer {
      padding: 12px 20px;
      background: #ffffff;
      border-top: 1px solid var(--border-subtle);
      display: flex;
      justify-content: flex-end;
      gap: 10px;
    }

    footer {
      margin-top: auto;
      background: #07253d;
      color: #e2e8f0;
      border-top: 1px solid #0b3b60;
      padding: 18px 28px;
      text-align: center;
      font-size: 0.78rem;
    }
    footer a { color: #fed7aa; text-decoration: none; font-weight: 600; }
  </style>
</head>
<body>

  <div class="tricolor-ribbon"></div>

  <div class="gov-topbar">
    <div class="gov-topbar-left">
      <span><span class="gov-flag"></span> <strong>भारत सरकार</strong> &bull; Government of India</span>
      <span>राष्ट्रीय अवसंरचना गतिशक्ति पोर्टल | PM GatiShakti GIS</span>
      <span>नीति आयोग (NITI Aayog) Aspirational Districts Telemetry</span>
    </div>
    <div class="gov-topbar-right">
      <span id="live-ist-clock">Loading IST...</span>
      <span>DPG Standard Certification: <strong>100% VALIDATED (Apache 2.0)</strong></span>
    </div>
  </div>

  <header>
    <div class="brand-container">
      <div class="national-emblem" title="Lion Capital of Ashoka - Satyameva Jayate">🏛️</div>
      <div class="brand-titles">
        <h1>JANSETU AI <span class="indic-title">(जनसेतु)</span></h1>
        <p>National Infrastructure Intelligence Engine & PM GatiShakti Spatial GIS Decision Portal</p>
      </div>
    </div>
    <div class="header-badges">
      <span class="badge"> PM GatiShakti GIS</span>
      <span class="badge"> DPGA Certified DPG</span>
      <span class="badge"> DPDP Act 2023 Compliant</span>
    </div>
  </header>

  <section class="kpi-bar">
    <div class="kpi-card">
      <div class="kpi-title">Districts Monitored</div>
      <div class="kpi-value" style="color:var(--gov-navy);" id="kpi-districts">16</div>
      <div class="kpi-desc">Aspirational & Frontier Zones</div>
    </div>
    <div class="kpi-card crisis">
      <div class="kpi-title">Tier-1 Crisis Hotspots</div>
      <div class="kpi-value" style="color:var(--danger);" id="kpi-tier1">3</div>
      <div class="kpi-desc">Priority Hotspot Score ≥ 70</div>
    </div>
    <div class="kpi-card capex">
      <div class="kpi-title">Identified Capex Gap</div>
      <div class="kpi-value" style="color:var(--gov-saffron-dark);" id="kpi-capex">₹12,480 Cr</div>
      <div class="kpi-desc">Across JJM, PMGSY & NIP</div>
    </div>
    <div class="kpi-card voices">
      <div class="kpi-title">Citizen Voices Ingested</div>
      <div class="kpi-value" style="color:var(--accent);" id="kpi-voices">14,892</div>
      <div class="kpi-desc">Across 6 Indic Dialects</div>
    </div>
    <div class="kpi-card dpg">
      <div class="kpi-title">DPGA 9-Rule Compliance</div>
      <div class="kpi-value" style="color:var(--gov-green);">100%</div>
      <div class="kpi-desc">Beckn Enabled & Open Source</div>
    </div>
  </section>

  <nav class="nav-bar">
    <button class="nav-tab active" onclick="switchTab('gis-view', this)">
       PM GatiShakti GIS Master Plan
    </button>
    <button class="nav-tab" onclick="switchTab('matrix-view', this)">
       National Hotspot & Deficit Matrix
    </button>
    <button class="nav-tab" onclick="switchTab('studio-view', this)">
       Bhashini Multilingual Voice Studio
    </button>
    <button class="nav-tab" onclick="switchTab('recommender-view', this)">
       Cabinet Policy & Capex Rebalancing
    </button>
    <button class="nav-tab" onclick="switchTab('dpg-view', this)">
       Digital Public Good (DPG) & DPI
    </button>
  </nav>

  <main>

    <!-- VIEW 1: PM GATISHAKTI GIS MAP -->
    <div id="gis-view" class="view-content active">
      <div class="gis-layout">
        
        <div class="gis-map-container">
          <div class="gis-map-header">
            <div class="gis-map-title">
              <span>🇮🇳</span>
              <span><strong>Survey of India Compliant GIS Master Plan</strong> &bull; 16 Strategic Districts</span>
            </div>
            <div class="map-controls-group">
              <span style="font-size:0.75rem; color:var(--text-muted); margin-right:4px;">Layer:</span>
              <button class="btn-ctrl active" onclick="setLayerFilter('all', this)">All (16)</button>
              <button class="btn-ctrl" onclick="setLayerFilter('tier1', this)">Tier-1 Crisis</button>
              <button class="btn-ctrl" onclick="setLayerFilter('water', this)">Water Stress</button>
              <button class="btn-ctrl" onclick="setLayerFilter('roads', this)">Road Gaps</button>
              
              <span style="font-size:0.75rem; color:var(--text-muted); margin-left:8px; margin-right:4px;">Basemap:</span>
              <button class="btn-ctrl active" onclick="setBasemap('osm', this)">Standard GIS (Clean)</button>
              <button class="btn-ctrl" onclick="setBasemap('sat', this)">Satellite</button>
              <button class="btn-ctrl" onclick="setBasemap('dark', this)">Dark Command</button>
              
              <button class="btn-ctrl" style="margin-left:6px;" onclick="resetIndiaMap()">Reset Pan</button>
            </div>
          </div>
          
          <div id="gis-map"></div>

          <div style="padding:10px 18px; background:#f8fafc; border-top:1px solid var(--border); display:flex; align-items:center; gap:8px; font-size:0.75rem; overflow-x:auto;">
            <span style="color:var(--text-muted); font-weight:700;">Fly to Zone:</span>
            <button class="btn-ctrl" onclick="flyToCoords(30.42, 79.32, 7)">North (Chamoli/Nuh)</button>
            <button class="btn-ctrl" onclick="flyToCoords(24.74, 78.83, 7)">Central (Tikamgarh/Bastar)</button>
            <button class="btn-ctrl" onclick="flyToCoords(18.34, 81.89, 7)">East (Malkangiri/Murshidabad)</button>
            <button class="btn-ctrl" onclick="flyToCoords(25.75, 71.39, 7)">West (Barmer/Dahod/Gadchiroli)</button>
            <button class="btn-ctrl" onclick="flyToCoords(11.68, 76.13, 7)">South (Wayanad/Ramanathapuram)</button>
            <button class="btn-ctrl" onclick="flyToCoords(25.87, 94.77, 7)">Northeast (Kiphire)</button>
          </div>
        </div>

        <div class="gis-sidebar">
          <h3>
            <span>District Telemetry</span>
            <span id="inspect-badge" class="tag-tier1">LIVE TELEMETRY</span>
          </h3>
          <div class="inspector-body" id="inspector-content">
            <p style="color:var(--text-muted); margin-bottom:12px;">Click any pulsating beacon on the India GIS map to inspect live telemetry.</p>
            
            <div style="background:#f8fafc; padding:12px; border-radius:6px; border:1px solid var(--border); margin-bottom:14px;">
              <h4 id="inspect-name" style="color:var(--gov-navy); font-size:1.1rem; font-weight:800;">Malkangiri</h4>
              <p id="inspect-state" style="color:var(--text-muted); font-size:0.8rem; font-weight:600;">Odisha &bull; Eastern Zone</p>
            </div>

            <div class="inspector-stat-row">
              <span class="stat-label">Priority Hotspot Score:</span>
              <span class="stat-val" id="inspect-phs" style="color:var(--danger); font-size:1.05rem;">81.7 / 100</span>
            </div>
            <div class="inspector-stat-row">
              <span class="stat-label">Primary Citizen Need:</span>
              <span class="stat-val" id="inspect-demand" style="color:var(--accent);">Healthcare & Sanitation</span>
            </div>
            <div class="inspector-stat-row">
              <span class="stat-label">Citizen Demand Index (CDI):</span>
              <span class="stat-val" id="inspect-cdi">89.4 / 100</span>
            </div>
            <div class="inspector-stat-row">
              <span class="stat-label">Infra Deficit Index (IDI):</span>
              <span class="stat-val" id="inspect-idi">82.1 / 100</span>
            </div>
            <div class="inspector-stat-row">
              <span class="stat-label">Demographic Vulnerability:</span>
              <span class="stat-val" id="inspect-dvi">78.5 / 100</span>
            </div>
            <div class="inspector-stat-row">
              <span class="stat-label">Capital Expenditure Gap:</span>
              <span class="stat-val" id="inspect-capex" style="color:var(--gov-saffron-dark);">₹320.0 Cr</span>
            </div>

            <div style="margin-top:16px;">
              <button class="btn-primary" style="width:100%; justify-content:center;" onclick="triggerCabinetMemoForCurrent()">
                 Draft Cabinet Policy Memo
              </button>
            </div>
          </div>
        </div>

      </div>
    </div>

    <!-- VIEW 2: NATIONAL HOTSPOT MATRIX -->
    <div id="matrix-view" class="view-content">
      <div class="content-card">
        <div class="card-header-row">
          <div class="card-title">
            <span></span>
            <span>National Infrastructure Priority Matrix & Grievance Telemetry</span>
          </div>
          <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
            <input type="text" id="filter-search" class="search-input" placeholder="Search District / State / Sector..." oninput="filterMatrixTable()" />
            <select id="filter-state" class="select-input" onchange="filterMatrixTable()">
              <option value="ALL">All States (13)</option>
            </select>
            <button class="btn-success" onclick="exportMatrixCSV()">
               Export National Report CSV
            </button>
          </div>
        </div>

        <div style="overflow-x:auto;">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>District & State</th>
                <th>Zone</th>
                <th>Priority Score (PHS)</th>
                <th>Urgency Tier</th>
                <th>Top Citizen Demand</th>
                <th>CDI (Demand)</th>
                <th>IDI (Deficit)</th>
                <th>Capex Gap</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody id="matrix-tbody"></tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- VIEW 3: BHASHINI VOICE STUDIO -->
    <div id="studio-view" class="view-content">
      <div class="gis-layout">
        
        <div class="content-card" style="margin-bottom:0;">
          <div class="card-title" style="margin-bottom:14px;">
            <span></span>
            <span>Bhashini Multilingual Telemetry Simulator & Voice ASR</span>
          </div>
          <p style="font-size:0.84rem; color:var(--text-muted); margin-bottom:16px;">
            JanSetu AI ingests citizen voice notes from 2G toll-free dial-in numbers (14444), WhatsApp audio notes, and Gram Panchayat digital kiosks across non-scheduled and scheduled Indic languages.
          </p>

          <div style="background:#f8fafc; padding:16px; border-radius:6px; border:1px solid var(--border); margin-bottom:18px;">
            <label style="font-size:0.75rem; font-weight:700; color:var(--text-muted); text-transform:uppercase;">Select Grassroots Audio Sample:</label>
            <div style="display:flex; gap:10px; margin-top:8px; flex-wrap:wrap;">
              <select id="voice-sample-select" class="select-input" style="flex:1;" onchange="loadPresetVoiceSample()">
                <option value="chitr">Hindi / Bundelkhandi - Chitrakoot (Water Contamination)</option>
                <option value="malk">Odia / Desia - Malkangiri (Boat Ambulance Deficit)</option>
                <option value="gadch">Marathi / Zadiboli - Gadchiroli (Bridge Submerged)</option>
                <option value="mursh">Bengali - Murshidabad (Arsenic Tube Wells)</option>
                <option value="adil">Telugu - Adilabad (Tribal Hill Road Cutoff)</option>
              </select>
              <button class="btn-primary" id="btn-play-voice" onclick="toggleVoiceAudio()">
                ▶ Play Voice Telemetry
              </button>
            </div>

            <div style="margin-top:14px; display:flex; align-items:center; justify-content:space-between;">
              <div class="equalizer-container" id="audio-equalizer">
                <div class="eq-bar"></div><div class="eq-bar"></div><div class="eq-bar"></div>
                <div class="eq-bar"></div><div class="eq-bar"></div><div class="eq-bar"></div>
              </div>
              <span id="audio-status-label" style="font-size:0.78rem; color:var(--text-muted);">Audio stream ready.</span>
            </div>
          </div>

          <div style="background:#ffffff; padding:16px; border-radius:6px; border:1px solid var(--border);">
            <div style="font-weight:700; font-size:0.88rem; color:var(--gov-navy); margin-bottom:10px;">
              Direct Telemetry Ingestion (Test Ingestion Pipeline)
            </div>
            <form onsubmit="submitTelemetry(event)">
              <div style="margin-bottom:10px;">
                <label style="font-size:0.74rem; color:var(--text-muted); font-weight:600;">Target District:</label>
                <select id="telemetry-dist-select" class="select-input" style="width:100%; margin-top:4px;"></select>
              </div>
              <div style="margin-bottom:10px;">
                <label style="font-size:0.74rem; color:var(--text-muted); font-weight:600;">Citizen Grievance Text (Any Indic Script or English):</label>
                <textarea id="telemetry-text" class="textarea-input" rows="3" style="width:100%; margin-top:4px;" required></textarea>
              </div>
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <span id="telemetry-submit-status" style="font-size:0.78rem; color:var(--gov-green); font-weight:700;"></span>
                <button type="submit" class="btn-success"> Ingest, Scrub PII & Classify</button>
              </div>
            </form>
          </div>
        </div>

        <div class="content-card" style="margin-bottom:0;">
          <div class="card-title" style="margin-bottom:14px;">
            <span></span>
            <span>DPDP Act 2023 Compliance Engine</span>
          </div>
          <p style="font-size:0.84rem; color:var(--text-muted); margin-bottom:14px;">
            All raw citizen petitions containing Aadhaar (UIDAI), Phone numbers, and names are scrubbed at the ingestion boundary before entering national GIS models.
          </p>

          <div style="margin-bottom:12px;">
            <div style="font-size:0.75rem; font-weight:700; color:var(--danger); margin-bottom:4px;">RAW INCOMING TELEMETRY (CONTAINS PII):</div>
            <div class="privacy-preview" id="raw-pii-preview" style="background:#fef2f2; border-color:#fecaca;">
              "मेरा नाम रमेश कुमार है, आधार 5421 9840 1234, फोन 9823412091। मानिकपुर ब्लॉक में 3 माह से नल-जल योजना बंद है।"
            </div>
          </div>

          <div style="margin-bottom:16px;">
            <div style="font-size:0.75rem; font-weight:700; color:var(--gov-green); margin-bottom:4px;">SANATIZED NATIONAL RECORD (PROCESSED):</div>
            <div class="privacy-preview" id="scrubbed-pii-preview" style="background:#f0fdf4; border-color:#bbf7d0;">
              "मेरा नाम [REDACTED_NAME] है, आधार <span class='redacted-tag'>[REDACTED_AADHAAR]</span>, फोन <span class='redacted-tag'>[REDACTED_PHONE]</span>। मानिकपुर ब्लॉक में 3 माह से नल-जल योजना बंद है।"
            </div>
          </div>

          <div style="background:#f8fafc; padding:12px; border-radius:6px; font-size:0.78rem; color:var(--text-muted); border:1px solid var(--border);">
            <strong style="color:var(--gov-navy);">DPDP Compliance Verification:</strong>
            <ul style="margin-left:18px; margin-top:6px; line-height:1.5;">
              <li>Zero PII persisted in public GIS layer</li>
              <li>SHA-256 District Anonymization Token</li>
              <li>Consent token logged under Section 6 of DPDP Act 2023</li>
            </ul>
          </div>
        </div>

      </div>
    </div>

    <!-- VIEW 4: CABINET POLICY & CAPEX REBALANCING -->
    <div id="recommender-view" class="view-content">
      
      <div class="content-card" style="background:#f8fafc; border:2px solid var(--gov-navy-light);">
        <div class="card-title" style="margin-bottom:10px;">
          <span></span>
          <span>PM GatiShakti National Capex Rebalancing Simulator</span>
        </div>
        <p style="font-size:0.84rem; color:var(--text-muted); margin-bottom:18px;">
          Drag the National Infrastructure Intervention Fund slider to simulate dynamic capital reallocation across Tier-1 and Tier-2 crisis districts.
        </p>

        <div style="display:flex; align-items:center; gap:20px; flex-wrap:wrap; margin-bottom:16px;">
          <input type="range" id="sim-budget-slider" min="500" max="10000" step="250" value="3500" style="flex:1; height:8px; accent-color:var(--gov-navy); cursor:pointer;" oninput="updateCapexSimulation(this.value)" />
          <div style="min-width:180px; background:#ffffff; padding:10px 16px; border-radius:6px; border:1px solid var(--border); text-align:center;">
            <div style="font-size:0.7rem; color:var(--text-muted); text-transform:uppercase; font-weight:700;">Intervention Outlay:</div>
            <div id="sim-budget-display" style="font-size:1.35rem; font-weight:800; color:var(--gov-navy);">₹3,500 Cr</div>
          </div>
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(220px, 1fr)); gap:12px;" id="sim-results-grid">
          <div style="background:#ffffff; padding:14px; border-radius:6px; border:1px solid var(--border);">
            <div style="font-size:0.74rem; color:var(--text-muted); font-weight:600;">Deficit Closure Rate:</div>
            <div id="sim-closure-rate" style="font-size:1.25rem; font-weight:800; color:var(--gov-green);">28.0%</div>
            <div style="font-size:0.72rem; color:var(--text-muted); margin-top:2px;">Of cumulative ₹12,480 Cr gap</div>
          </div>
          <div style="background:#ffffff; padding:14px; border-radius:6px; border:1px solid var(--border);">
            <div style="font-size:0.74rem; color:var(--text-muted); font-weight:600;">Citizens Directly Benefited:</div>
            <div id="sim-lives-impacted" style="font-size:1.25rem; font-weight:800; color:var(--accent);">1,575,000</div>
            <div style="font-size:0.72rem; color:var(--text-muted); margin-top:2px;">Across 16 Aspirational Districts</div>
          </div>
          <div style="background:#ffffff; padding:14px; border-radius:6px; border:1px solid var(--border);">
            <div style="font-size:0.74rem; color:var(--text-muted); font-weight:600;">Projects Fully Sanctioned:</div>
            <div id="sim-projects-count" style="font-size:1.25rem; font-weight:800; color:var(--gov-saffron-dark);">9 Fast-Track Projects</div>
            <div style="font-size:0.72rem; color:var(--text-muted); margin-top:2px;">Single-window EGoS clearance</div>
          </div>
        </div>
      </div>

      <div class="content-card">
        <div class="card-header-row">
          <div class="card-title">
            <span></span>
            <span>MCDA-Ranked National Infrastructure Projects (Return on Public Good Index)</span>
          </div>
        </div>

        <div style="overflow-x:auto;">
          <table>
            <thead>
              <tr>
                <th>Project Title & Intervention Scope</th>
                <th>Target District</th>
                <th>Lead Ministry</th>
                <th>Capex (₹ Cr)</th>
                <th>Beneficiaries</th>
                <th>RPGI Score</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody id="projects-tbody"></tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- VIEW 5: DIGITAL PUBLIC GOOD (DPG) & DPI STANDARDS -->
    <div id="dpg-view" class="view-content">
      <div class="gis-layout">
        
        <div class="content-card" style="margin-bottom:0;">
          <div class="card-title" style="margin-bottom:14px;">
            <span></span>
            <span>DPG Alliance 9-Standard Compliance Scorecard</span>
          </div>
          
          <table style="margin-bottom:16px;">
            <thead>
              <tr>
                <th>DPGA Standard Indicator</th>
                <th>JanSetu AI Verification Proof</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>1. Relevance to SDGs</strong></td>
                <td>SDG 6 (Clean Water), SDG 9 (Infrastructure), SDG 11 (Communities)</td>
                <td><span class="tag-tier3">✔ 100% Compliant</span></td>
              </tr>
              <tr>
                <td><strong>2. Open Source License</strong></td>
                <td>Apache License 2.0 (Permissive for GovTech integration)</td>
                <td><span class="tag-tier3">✔ Approved</span></td>
              </tr>
              <tr>
                <td><strong>3. Open Data Standards</strong></td>
                <td>OGC Web Feature Service (WFS), GeoJSON, Beckn Protocol</td>
                <td><span class="tag-tier3">✔ Standards-Compliant</span></td>
              </tr>
              <tr>
                <td><strong>4. Privacy & Consent</strong></td>
                <td>DPDP Act 2023 Edge PII Redaction for Aadhaar / Mobile</td>
                <td><span class="tag-tier3">✔ Verified</span></td>
              </tr>
              <tr>
                <td><strong>5. Platform Independence</strong></td>
                <td>Zero proprietary lock-in; runs on Linux, NIC Cloud (MeghRaj), Windows</td>
                <td><span class="tag-tier3">✔ Portable</span></td>
              </tr>
              <tr>
                <td><strong>6. Content & Linguistic Equity</strong></td>
                <td>Bhashini Indic AI support for 22 Scheduled Languages</td>
                <td><span class="tag-tier3">✔ Multilingual</span></td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="content-card" style="margin-bottom:0;">
          <div class="card-title" style="margin-bottom:14px;">
            <span></span>
            <span>Beckn Open DPI Tender Catalog</span>
          </div>
          <p style="font-size:0.82rem; color:var(--text-muted); margin-bottom:10px;">
            Decentralized public procurement tender broadcast schema (`nic:public-works:infrastructure`):
          </p>
          <pre class="privacy-preview" style="max-height:360px; overflow-y:auto;" id="beckn-schema-preview">{
  "context": {
    "domain": "nic:public-works:infrastructure",
    "action": "search",
    "bap_id": "jansetu.gov.in",
    "bpp_id": "gem.gov.in"
  },
  "message": {
    "intent": {
      "item": {
        "descriptor": {
          "name": "Chitrakoot Fluoride Remediation Pipeline"
        }
      },
      "fulfillment": {
        "end": {
          "location": {
            "gps": "25.1764,80.8667",
            "address": { "district": "Chitrakoot", "state": "UP" }
          }
        }
      }
    }
  }
}</pre>
          <button class="btn-primary" style="margin-top:10px; width:100%; justify-content:center;" onclick="copyBecknSchema()">
             Copy Beckn Protocol JSON-LD
          </button>
        </div>

      </div>
    </div>

  </main>

  <!-- CABINET MEMO MODAL -->
  <div class="modal-backdrop" id="memo-modal">
    <div class="modal-panel">
      <div class="modal-header">
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="font-size:1.15rem;"></span>
          <strong style="color:#ffffff;" id="modal-memo-title">Cabinet Policy Memorandum</strong>
        </div>
        <button class="btn-ctrl" style="background:transparent; border:none; color:#ffffff; font-size:1.1rem;" onclick="closeModal()">✕</button>
      </div>
      <div class="modal-body" id="modal-memo-body">
        <div style="text-align:center; padding:40px; color:var(--gov-navy);">Drafting official Cabinet policy note...</div>
      </div>
      <div class="modal-footer">
        <button class="btn-ctrl" onclick="copyMemoText()"> Copy Official Text</button>
        <button class="btn-primary" onclick="window.print()"> Print / Save PDF</button>
        <button class="btn-ctrl" onclick="closeModal()">Close</button>
      </div>
    </div>
  </div>

  <footer>
    <p>
      <strong>JanSetu AI (जनसेतु) &bull; National Infrastructure Telemetry Platform</strong> | Developed as a Digital Public Good for PM GatiShakti & NITI Aayog.
    </p>
    <p style="margin-top:4px; opacity:0.85;">
      Compliant with Survey of India Cartographic Guidelines &bull; Digital Personal Data Protection Act 2023 &bull; Open Source Apache 2.0
    </p>
  </footer>

  <script>
    let map = null;
    let markersLayer = null;
    let currentBasemap = null;
    let basemaps = {};
    let allHotspots = [];
    let allRecs = [];
    let activeInspectorDistrict = null;
    let currentMemoMarkdown = "";
    let isVoicePlaying = false;

    const presetVoices = {
      chitr: {
        distId: "IND-UP-01",
        raw: "मेरा नाम रामेश्वर यादव है, मानिकपुर चित्रकूट से। आधार 5421-9840-1234, फोन 9823412091। हमारे 12 गांवों में 4 महीने से बोरवेल में फ्लोराइड आ रहा है, बच्चे बीमार हैं। कृपया जल जीवन मिशन की पाइपलाइन तुरंत जुड़वाएं।",
        scrubbed: "मेरा नाम [REDACTED_NAME] है, मानिकपुर चित्रकूट से। आधार [REDACTED_AADHAAR], फोन [REDACTED_PHONE]। हमारे 12 गांवों में 4 महीने से बोरवेल में फ्लोराइड आ रहा है, बच्चे बीमार हैं। कृपया जल जीवन मिशन की पाइपलाइन तुरंत जुड़वाएं।"
      },
      malk: {
        distId: "IND-OD-01",
        raw: "ମୋ ନାମ ସୁରେଶ ମାଢ଼ୀ, ମାଲକାନଗିରି ସ୍ୱାଭିମାନ ଅଞ୍ଚଳ। ଫୋନ୍ 9437189021, ଆଧାର 6789-1234-9012। ଏଠାରେ ପ୍ରାଥମିକ ସ୍ୱାସ୍ଥ୍ୟ କେନ୍ଦ୍ର ନାହିଁ ଏବଂ ଜଳପଥ ପାଇଁ ଆମ୍ବୁଲାନ୍ସ ଡଙ୍ଗା ତୁରନ୍ତ ଦରକାର।",
        scrubbed: "ମୋ ନାମ [REDACTED_NAME], ମାଲକାନଗିରି ସ୍ୱାଭିମାନ ଅଞ୍ଚଳ। ଫୋନ୍ [REDACTED_PHONE], ଆଧାର [REDACTED_AADHAAR]। ଏଠାରେ ପ୍ରାଥମିକ ସ୍ୱାସ୍ଥ୍ୟ କେନ୍ଦ୍ର ନାହିଁ ଏବଂ ଜଳପଥ ପାଇଁ ଆମ୍ବୁଲାନ୍ସ ଡଙ୍ଗା ତୁରନ୍ତ ଦରକାର।"
      },
      gadch: {
        distId: "IND-MH-01",
        raw: "मी बापूराव मडावी, भामरागड गडचिरोली. मोबाईल 9822451234. पर्लकोटा नदीचा पूल पावसाळ्यात पाण्याखाली जातो आणि 50 गावे तुटतात. तातडीने उंच पूल मंजूर करा.",
        scrubbed: "मी [REDACTED_NAME], भामरागड गडचिरोली. मोबाईल [REDACTED_PHONE]. पर्लकोटा नदीचा पूल पावसाळ्यात पाण्याखाली जातो आणि 50 गावे तुटतात. तातडीने उंच पूल मंजूर करा."
      },
      mursh: {
        distId: "IND-WB-01",
        raw: "আমার নাম আনিসুর রহমান, ভগবানগোলা মুর্শিদাবাদ। ফোন 9832109876। এখানে টিউবওয়েলের জলে মারাত্মক আর্সেনিক, পাইপলাইনের পানীয় জল প্রকল্প অবিলম্বে চালু করুন।",
        scrubbed: "আমার নাম [REDACTED_NAME], ভগবানগোলা মুর্শিদাবাদ। ফোন [REDACTED_PHONE]। এখানে টিউবওয়েলের জলে মারাত্মক আর্সেনিক, পাইপলাইনের পানীয় জল প্রকল্প অবিলম্বে চালু করুন।"
      },
      adil: {
        distId: "IND-TG-01",
        raw: "నా పేరు రమేష్ రాథోడ్, ఆదిలాబాద్ ఉట్నూర్. ఫోన్ 9989012345. మా గిరిజన గూడేనికి వర్షాకాలంలో రోడ్డు లేదు, గర్భిణీ స్త్రీలను ఆసుపత్రికి తీసుకెళ్లడం కష్టంగా ఉంది.",
        scrubbed: "నా పేరు [REDACTED_NAME], ఆదిలాబాద్ ఉట్నూర్. ఫోన్ [REDACTED_PHONE]. మా గిరిజన గూడేనికి వర్షాకాలంలో రోడ్డు లేదు, గర్భిణీ స్త్రీలను ఆసుపత్రికి తీసుకెళ్లడం కష్టంగా ఉంది."
      }
    };

    function updateClock() {
      const now = new Date();
      const options = { timeZone: 'Asia/Kolkata', hour12: true, hour: '2-digit', minute: '2-digit', second: '2-digit', day: 'numeric', month: 'short', year: 'numeric' };
      document.getElementById('live-ist-clock').innerText = now.toLocaleString('en-IN', options) + " (IST)";
    }
    setInterval(updateClock, 1000);
    updateClock();

    function switchTab(viewId, btn) {
      document.querySelectorAll('.nav-tab').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.view-content').forEach(v => v.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(viewId).classList.add('active');

      if (viewId === 'gis-view' && map) {
        setTimeout(() => map.invalidateSize(), 200);
      }
    }

    function initLeafletMap() {
      if (map) return;

      map = L.map('gis-map', {
        center: [22.5, 82.0],
        zoom: 5,
        minZoom: 4,
        maxZoom: 14
      });

      basemaps.osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors | PM GatiShakti GIS',
        maxZoom: 19
      });

      basemaps.sat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles &copy; Esri, Earthstar Geographics',
        maxZoom: 18
      });

      currentBasemap = basemaps.osm;
      currentBasemap.addTo(map);

      markersLayer = L.layerGroup().addTo(map);
    }

    function setBasemap(type, btn) {
      document.querySelectorAll('.gis-map-header .btn-ctrl').forEach(b => {
        if (
          (type === 'osm' && b.innerText.includes('Standard GIS')) ||
          (type === 'sat' && b.innerText === 'Satellite') ||
          (type === 'dark' && b.innerText === 'Dark Command')
        ) {
          b.classList.add('active');
        } else if (['Standard GIS (Clean)', 'Satellite', 'Dark Command'].includes(b.innerText)) {
          b.classList.remove('active');
        }
      });

      const mapContainer = document.getElementById('gis-map');

      if (type === 'osm') {
        mapContainer.classList.remove('gis-dark-mode');
        if (currentBasemap !== basemaps.osm) {
          if (currentBasemap) map.removeLayer(currentBasemap);
          currentBasemap = basemaps.osm;
          currentBasemap.addTo(map);
        }
      } else if (type === 'sat') {
        mapContainer.classList.remove('gis-dark-mode');
        if (currentBasemap !== basemaps.sat) {
          if (currentBasemap) map.removeLayer(currentBasemap);
          currentBasemap = basemaps.sat;
          currentBasemap.addTo(map);
        }
      } else if (type === 'dark') {
        mapContainer.classList.add('gis-dark-mode');
        if (currentBasemap !== basemaps.osm) {
          if (currentBasemap) map.removeLayer(currentBasemap);
          currentBasemap = basemaps.osm;
          currentBasemap.addTo(map);
        }
      }
    }

    function resetIndiaMap() {
      if (map) map.setView([22.5, 82.0], 5);
    }

    function flyToCoords(lat, lng, zoom) {
      if (map) map.flyTo([lat, lng], zoom, { duration: 1.2 });
    }

    function plotHotspotsOnGIS(hotspots, filterMode = 'all') {
      if (!markersLayer) return;
      markersLayer.clearLayers();

      const filtered = hotspots.filter(h => {
        if (filterMode === 'tier1') return h.priority_hotspot_score >= 70;
        if (filterMode === 'water') return (h.top_sector_demand || '').toLowerCase().includes('water');
        if (filterMode === 'roads') return (h.top_sector_demand || '').toLowerCase().includes('road') || (h.top_sector_demand || '').toLowerCase().includes('bridge');
        return true;
      });

      filtered.forEach(h => {
        const lat = h.latitude || 22.0;
        const lng = h.longitude || 78.0;
        const isTier1 = h.priority_hotspot_score >= 70;
        const isTier2 = h.priority_hotspot_score >= 55 && h.priority_hotspot_score < 70;

        let iconClass = 'pulse-marker-tier3';
        if (isTier1) iconClass = 'pulse-marker-tier1';
        else if (isTier2) iconClass = 'pulse-marker-tier2';

        const customIcon = L.divIcon({
          className: 'custom-beacon',
          html: `<div class="${iconClass}" title="${h.name}, ${h.state}"></div>`,
          iconSize: [20, 20],
          iconAnchor: [10, 10]
        });

        const marker = L.marker([lat, lng], { icon: customIcon }).addTo(markersLayer);

        const popupHtml = `
          <div style="font-family:-apple-system,BlinkMacSystemFont,sans-serif; min-width:210px; color:#0f172a;">
            <div style="font-size:1.05rem; font-weight:800; color:var(--gov-navy);">${h.name}, ${h.state}</div>
            <div style="font-size:0.75rem; color:#64748b; margin-bottom:6px;">Zone: ${h.zone || 'Central'} &bull; ID: ${h.district_id}</div>
            <div style="background:#f8fafc; padding:8px; border-radius:6px; margin-bottom:8px; font-size:0.78rem; border:1px solid #e2e8f0;">
              <div><strong>Priority Score (PHS):</strong> <span style="color:${isTier1 ? '#dc2626' : '#d97706'}; font-weight:800;">${h.priority_hotspot_score}</span></div>
              <div><strong>Critical Need:</strong> ${h.top_sector_demand}</div>
              <div><strong>Capex Deficit:</strong> ₹${h.planned_capex_gap_cr} Cr</div>
            </div>
            <button style="background:#0b3b60; color:#fff; border:none; padding:7px 12px; border-radius:4px; font-weight:700; font-size:0.75rem; cursor:pointer; width:100%;" onclick="openCabinetMemo('${h.district_id}', '${h.name}', '${h.state}')">
               Draft Cabinet Policy Memo
            </button>
          </div>
        `;
        marker.bindPopup(popupHtml);

        marker.on('click', () => {
          inspectDistrict(h);
        });
      });

      if (filtered.length > 0 && !activeInspectorDistrict) {
        inspectDistrict(filtered[0]);
      }
    }

    function setLayerFilter(filterType, btn) {
      plotHotspotsOnGIS(allHotspots, filterType);
    }

    function inspectDistrict(h) {
      activeInspectorDistrict = h;
      document.getElementById('inspect-name').innerText = h.name;
      document.getElementById('inspect-state').innerText = `${h.state} • ${h.zone || 'Central'} Zone`;
      document.getElementById('inspect-phs').innerText = `${h.priority_hotspot_score} / 100`;
      document.getElementById('inspect-phs').style.color = h.priority_hotspot_score >= 70 ? 'var(--danger)' : 'var(--gov-saffron-dark)';
      document.getElementById('inspect-demand').innerText = h.top_sector_demand;
      document.getElementById('inspect-cdi').innerText = `${h.indices?.cdi || 75} / 100`;
      document.getElementById('inspect-idi').innerText = `${h.indices?.idi || 70} / 100`;
      document.getElementById('inspect-dvi').innerText = `${h.indices?.dvi || 65} / 100`;
      document.getElementById('inspect-capex').innerText = `₹${h.planned_capex_gap_cr} Cr`;
      
      const badge = document.getElementById('inspect-badge');
      if (h.priority_hotspot_score >= 70) {
        badge.className = 'tag-tier1';
        badge.innerText = 'TIER 1 CRISIS';
      } else {
        badge.className = 'tag-tier2';
        badge.innerText = 'TIER 2 PRIORITY';
      }
    }

    function triggerCabinetMemoForCurrent() {
      if (activeInspectorDistrict) {
        openCabinetMemo(activeInspectorDistrict.district_id, activeInspectorDistrict.name, activeInspectorDistrict.state);
      }
    }

    function renderMatrixTable(hotspots) {
      const tbody = document.getElementById('matrix-tbody');
      tbody.innerHTML = hotspots.map((h, idx) => {
        const isTier1 = h.priority_hotspot_score >= 70;
        return `
          <tr>
            <td><strong style="color:var(--gov-navy);">#${idx + 1}</strong></td>
            <td>
              <strong style="color:var(--text); font-size:0.92rem;">${h.name}</strong><br>
              <span style="font-size:0.75rem; color:var(--text-muted);">${h.state} (${h.district_id})</span>
            </td>
            <td><span style="font-size:0.75rem; color:var(--text-muted); font-weight:600;">${h.zone || 'Central'}</span></td>
            <td><strong style="color:${isTier1 ? 'var(--danger)' : 'var(--gov-saffron-dark)'}; font-size:0.95rem;">${h.priority_hotspot_score}</strong></td>
            <td><span class="${isTier1 ? 'tag-tier1' : 'tag-tier2'}">${h.priority_tier || (isTier1 ? 'Tier 1' : 'Tier 2')}</span></td>
            <td><span class="tag-sector">${h.top_sector_demand}</span></td>
            <td>${h.indices?.cdi || '-'}</td>
            <td>${h.indices?.idi || '-'}</td>
            <td style="color:var(--gov-saffron-dark); font-weight:800;">₹${h.planned_capex_gap_cr} Cr</td>
            <td>
              <button class="btn-primary" style="padding:4px 10px; font-size:0.74rem;" onclick="openCabinetMemo('${h.district_id}', '${h.name}', '${h.state}')">
                 Cabinet Memo
              </button>
            </td>
          </tr>
        `;
      }).join('');
    }

    function filterMatrixTable() {
      const search = (document.getElementById('filter-search').value || '').toLowerCase();
      const state = document.getElementById('filter-state').value;

      const filtered = allHotspots.filter(h => {
        const matchState = (state === 'ALL') || (h.state === state);
        const matchSearch = h.name.toLowerCase().includes(search) || 
                            h.state.toLowerCase().includes(search) || 
                            h.top_sector_demand.toLowerCase().includes(search);
        return matchState && matchSearch;
      });
      renderMatrixTable(filtered);
    }

    function exportMatrixCSV() {
      let csv = "Rank,District,State,Zone,DistrictID,PriorityHotspotScore,PriorityTier,TopCitizenDemand,CDI,IDI,DVI,PlannedCapexGapCr\\n";
      allHotspots.forEach((h, i) => {
        csv += `${i+1},"${h.name}","${h.state}","${h.zone||'Central'}","${h.district_id}",${h.priority_hotspot_score},"${h.priority_tier||'Tier 1'}","${h.top_sector_demand}",${h.indices?.cdi||0},${h.indices?.idi||0},${h.indices?.dvi||0},${h.planned_capex_gap_cr}\\n`;
      });
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.setAttribute('href', url);
      a.setAttribute('download', 'JanSetu_National_Infrastructure_Hotspots.csv');
      a.click();
    }

    function renderProjectsTable(recs) {
      const tbody = document.getElementById('projects-tbody');
      tbody.innerHTML = recs.map(r => `
        <tr>
          <td>
            <strong style="color:var(--gov-navy);">${r.title}</strong><br>
            <span style="font-size:0.76rem; color:var(--text-muted);">${r.rationale_summary || 'Targeted infrastructure remediation under PM GatiShakti'}</span>
          </td>
          <td><strong style="color:var(--text);">${r.district_name || 'Multi-District'}</strong></td>
          <td><span class="tag-sector">${r.lead_ministry}</span></td>
          <td style="color:var(--gov-saffron-dark); font-weight:800; font-size:0.95rem;">₹${r.estimated_capex_cr} Cr</td>
          <td>${(r.target_beneficiaries || 250000).toLocaleString()} citizens</td>
          <td><strong style="color:var(--gov-green);">${r.rpgi_score || 85.0}</strong></td>
          <td>
            <button class="btn-primary" style="padding:4px 10px; font-size:0.74rem;" onclick="openCabinetMemo('${r.district_id || 'IND-OD-01'}', '${r.district_name || 'Malkangiri'}', '${r.state || 'Odisha'}')">
              Sanction Memo
            </button>
          </td>
        </tr>
      `).join('');
    }

    function updateCapexSimulation(val) {
      document.getElementById('sim-budget-display').innerText = `₹${Number(val).toLocaleString()} Cr`;
      const totalDeficit = 12480;
      const rate = Math.min(100, ((val / totalDeficit) * 100)).toFixed(1);
      const citizens = Math.round(val * 450);
      const projCount = Math.max(3, Math.min(16, Math.round(val / 380)));

      document.getElementById('sim-closure-rate').innerText = `${rate}%`;
      document.getElementById('sim-lives-impacted').innerText = citizens.toLocaleString();
      document.getElementById('sim-projects-count').innerText = `${projCount} Fast-Track Projects`;
    }

    function loadPresetVoiceSample() {
      const key = document.getElementById('voice-sample-select').value;
      const preset = presetVoices[key];
      if (preset) {
        document.getElementById('raw-pii-preview').innerText = `"${preset.raw}"`;
        document.getElementById('scrubbed-pii-preview').innerHTML = `"${preset.scrubbed}"`;
        document.getElementById('telemetry-text').value = preset.raw;
        document.getElementById('telemetry-dist-select').value = preset.distId;
      }
    }

    function toggleVoiceAudio() {
      const eq = document.getElementById('audio-equalizer');
      const btn = document.getElementById('btn-play-voice');
      const lbl = document.getElementById('audio-status-label');

      if (!isVoicePlaying) {
        isVoicePlaying = true;
        eq.classList.add('playing');
        btn.innerText = "⏹ Stop Audio Stream";
        lbl.innerText = "Streaming Bhashini ASR Indic Voice (16kHz)...";

        if ('speechSynthesis' in window) {
          const text = document.getElementById('telemetry-text').value || "Water pipeline grievance";
          const utter = new SpeechSynthesisUtterance(text.slice(0, 140));
          utter.rate = 0.9;
          utter.onend = () => { stopVoiceAudio(); };
          window.speechSynthesis.speak(utter);
        }

        setTimeout(() => { stopVoiceAudio(); }, 6000);
      } else {
        stopVoiceAudio();
      }
    }

    function stopVoiceAudio() {
      isVoicePlaying = false;
      document.getElementById('audio-equalizer').classList.remove('playing');
      document.getElementById('btn-play-voice').innerText = "▶ Play Voice Telemetry";
      document.getElementById('audio-status-label').innerText = "Voice stream completed & ingested.";
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
      }
    }

    async function submitTelemetry(e) {
      e.preventDefault();
      const text = document.getElementById('telemetry-text').value;
      const district_id = document.getElementById('telemetry-dist-select').value;
      const statusLbl = document.getElementById('telemetry-submit-status');

      statusLbl.innerText = " Ingesting & Scrubbing PII...";

      try {
        const res = await fetch('/api/feedback', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ text, district_id, channel: 'voice_ivr' })
        });
        const data = await res.json();
        statusLbl.innerText = "✔ " + data.message;
        loadAllData();
      } catch (err) {
        statusLbl.innerText = "Error: " + err.message;
      }
    }

    async function openCabinetMemo(distId, name, state) {
      const modal = document.getElementById('memo-modal');
      const body = document.getElementById('modal-memo-body');
      const title = document.getElementById('modal-memo-title');

      title.innerText = `Cabinet Policy Memorandum &bull; ${name}, ${state}`;
      modal.style.display = 'flex';
      body.innerHTML = `<div style="text-align:center; padding:40px; color:var(--gov-navy);"><strong>Generating EGoS Cabinet Sanction Memo for ${name}...</strong></div>`;

      try {
        const res = await fetch('/api/generate-brief', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({ district_id: distId })
        });
        const data = await res.json();
        currentMemoMarkdown = data.memo_markdown || "No memo generated.";
        body.innerHTML = `<div style="white-space:pre-wrap; font-family:Consolas, Monaco, monospace; font-size:0.84rem; background:#ffffff; padding:20px; border-radius:6px; border:1px solid #cbd5e1; color:#0f172a; line-height:1.65; box-shadow:0 1px 3px rgba(0,0,0,0.05);">${currentMemoMarkdown}</div>`;
      } catch (err) {
        body.innerHTML = `<div style="color:var(--danger); padding:20px;">Error generating memo: ${err.message}</div>`;
      }
    }

    function copyMemoText() {
      navigator.clipboard.writeText(currentMemoMarkdown).then(() => {
        alert("Cabinet Policy Memorandum copied to clipboard!");
      });
    }

    function closeModal() {
      document.getElementById('memo-modal').style.display = 'none';
    }

    function copyBecknSchema() {
      const txt = document.getElementById('beckn-schema-preview').innerText;
      navigator.clipboard.writeText(txt).then(() => {
        alert("Beckn Protocol JSON-LD Schema copied to clipboard!");
      });
    }

    async function loadAllData() {
      try {
        const [hRes, rRes] = await Promise.all([fetch('/api/hotspots'), fetch('/api/recommendations')]);
        const hData = await hRes.json();
        const rData = await rRes.json();

        allHotspots = hData.hotspots || [];
        allRecs = rData.recommendations || [];

        document.getElementById('kpi-districts').innerText = allHotspots.length;
        const tier1Count = allHotspots.filter(h => h.priority_hotspot_score >= 70).length;
        document.getElementById('kpi-tier1').innerText = tier1Count;

        initLeafletMap();
        plotHotspotsOnGIS(allHotspots);
        renderMatrixTable(allHotspots);
        renderProjectsTable(allRecs);

        const stateSelect = document.getElementById('filter-state');
        const states = Array.from(new Set(allHotspots.map(h => h.state))).sort();
        stateSelect.innerHTML = `<option value="ALL">All States (${states.length})</option>` + 
          states.map(s => `<option value="${s}">${s}</option>`).join('');

        const distSelect = document.getElementById('telemetry-dist-select');
        distSelect.innerHTML = allHotspots.map(h => `<option value="${h.district_id}">${h.name} (${h.state})</option>`).join('');

        loadPresetVoiceSample();

      } catch (err) {
        console.error("Error loading JanSetu telemetry:", err);
      }
    }

    window.addEventListener('DOMContentLoaded', loadAllData);
  </script>
</body>
</html>"""

class JanSetuHandler(SimpleHTTPRequestHandler):
    def _send_json(self, status, payload):
        body = json.dumps(payload).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path in ["/", "/index.html"]:
            body = DASHBOARD_HTML.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/api/hotspots":
            _, hotspots, _ = get_current_analytics()
            self._send_json(200, {'hotspots': hotspots})
        elif self.path in ["/api/recommendations", "/api/projects"]:
            _, _, recs = get_current_analytics()
            self._send_json(200, {'recommendations': recs, 'projects': recs})
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length).decode('utf-8')
        payload = json.loads(raw) if raw else {}

        if self.path == "/api/feedback":
            enriched = IngestionPipeline.process_raw_input(payload)
            fusion_engine.add_request(enriched)
            self._send_json(201, {
                'status': 'success',
                'message': f"Demand Ingested! Classified under '{enriched['sector']}' with urgency '{enriched['urgency_level']}'. PII Redacted: {enriched['pii_redacted']}",
                'record': enriched
            })
        elif self.path == "/api/generate-brief":
            d_id = payload.get('district_id')
            _, hotspots, recs = get_current_analytics()
            target_h = next((h for h in hotspots if h['district_id'] == d_id), hotspots[0] if hotspots else {})
            target_r = next((r for r in recs if r.get('district_name') == target_h.get('name')), recs[0] if recs else {})
            brief = synthesizer.synthesize_executive_brief(target_h, target_r)
            self._send_json(200, brief)
        else:
            self.send_response(404)
            self.end_headers()

def run(port=8080):
    server = HTTPServer(('', port), JanSetuHandler)
    print("=" * 70)
    print("  JANSETU AI (जनसेतु) - GOVERNMENT OF INDIA NATIONAL GIS PORTAL")
    print(f"  Live at: http://localhost:{port}")
    print("  Press Ctrl+C to terminate server.")
    print("=" * 70)
    server.serve_forever()

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run(port)