import math

class HotspotAnalyzer:
    def __init__(self, profiles): self.profiles = profiles

    def analyze_all(self):
        hotspots = []
        for p in self.profiles:
            fb, inf, inv, demo = p['citizen_feedback'], p['infrastructure'], p['investment'], p['demographics']
            cdi = min(100.0, (fb['critical_requests'] * 30.0) + (math.log1p(fb['total_upvotes']) * 6.0))
            idi = min(100.0, (100.0 - inf.get('jal_jeevan_fhtc_pct', 50.0)) * 0.4 + (100.0 - inf.get('pmgsy_all_weather_road_connectivity_pct', 50.0)) * 0.4 + (inf.get('water_quality_hazard_index', 50.0) * 0.2))
            dvi = min(100.0, demo.get('sc_st_population_pct', 30.0) * 0.5 + demo.get('below_poverty_line_pct', 30.0) * 0.5 + 6.0)
            fag = min(100.0, (inv.get('planned_capex_gap_cr', 200.0) / max(1.0, inv.get('central_budget_allocation_cr', 300.0))) * 60.0)

            phs = round((0.35 * cdi) + (0.30 * idi) + (0.20 * dvi) + (0.15 * fag), 2)
            tier = "Tier 1: Immediate National Intervention" if phs >= 70 else ("Tier 2: High Priority" if phs >= 55 else "Tier 3: Moderate")

            top_sec = sorted(fb.get('sector_counts', {}).items(), key=lambda x: x[1], reverse=True)
            hotspots.append({
                "district_id": p['district_id'], "name": p['name'], "state": p['state'],
                "priority_hotspot_score": phs, "priority_tier": tier,
                "indices": {"cdi": round(cdi, 1), "idi": round(idi, 1), "dvi": round(dvi, 1), "fag": round(fag, 1)},
                "top_sector_demand": top_sec[0][0] if top_sec else "General Infrastructure",
                "planned_capex_gap_cr": inv.get('planned_capex_gap_cr', 200.0)
            })
        hotspots.sort(key=lambda x: x['priority_hotspot_score'], reverse=True)
        return hotspots
