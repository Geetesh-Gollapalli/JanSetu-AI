class PolicyRecommender:
    def __init__(self, hotspots): self.hotspots = hotspots

    def generate_recommendations(self):
        recs = []
        for h in self.hotspots:
            phs, name, state, sec = h['priority_hotspot_score'], h['name'], h['state'], h['top_sector_demand']
            recs.append({
                "project_id": f"PROJ-GATISHAKTI-{h['district_id']}",
                "title": f"{name} Special Fast-Track {sec} Intervention",
                "district_name": name, "state": state, "priority_score": phs,
                "lead_ministry": "Ministry of Jal Shakti" if "Water" in sec else "MoRTH / MoRD",
                "estimated_capex_cr": round(h['planned_capex_gap_cr'] * 0.4, 1),
                "target_beneficiaries": 250000,
                "rpgi_score": round((250000 * phs) / (max(50.0, h['planned_capex_gap_cr'] * 0.4) * 1000), 2)
            })
        recs.sort(key=lambda x: x['rpgi_score'], reverse=True)
        return recs
