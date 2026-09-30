import json
from pathlib import Path

class DataFusionEngine:
    def __init__(self, data_dir=None):
        self.data_dir = Path(data_dir or f"{Path(__file__).resolve().parent.parent}/data")
        with open(self.data_dir / "districts_demographics.json") as f: self.districts_data = json.load(f)
        with open(self.data_dir / "infrastructure_indices.json") as f: self.infra_data = json.load(f)
        with open(self.data_dir / "public_investment_plans.json") as f: self.invest_data = json.load(f)
        with open(self.data_dir / "citizen_requests_seed.json") as f: self.citizen_requests = json.load(f)

    def build_fused_profiles(self):
        signals = {}
        for req in self.citizen_requests:
            d = req.get("district_id")
            if not d: continue
            if d not in signals: signals[d] = {"total_requests": 0, "critical_requests": 0, "total_upvotes": 0, "total_affected_est": 0, "sector_counts": {}}
            sig = signals[d]
            sig["total_requests"] += 1
            if req.get("urgency_level") == "Critical": sig["critical_requests"] += 1
            sig["total_upvotes"] += req.get("upvotes_support_count", 1)
            sig["total_affected_est"] += req.get("affected_population_estimate", 1000)
            sec = req.get("sector", "General")
            sig["sector_counts"][sec] = sig["sector_counts"].get(sec, 0) + 1

        fused = []
        for dist in self.districts_data:
            d_id = dist["district_id"]
            inf = self.infra_data.get(d_id, {})
            inv = self.invest_data.get(d_id, {})
            fb = signals.get(d_id, {"total_requests": 0, "critical_requests": 0, "total_upvotes": 0, "total_affected_est": 0, "sector_counts": {}})
            fused.append({"district_id": d_id, "name": dist["name"], "state": dist["state"], "demographics": dist, "infrastructure": inf, "investment": inv, "citizen_feedback": fb})
        return fused
