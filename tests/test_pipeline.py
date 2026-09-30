import sys, os, unittest
from pathlib import Path

# Add project root to sys.path so 'engine' is always discoverable
PROJECT_ROOT = str(Path(__file__).resolve().parent.parent)
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from engine.multilingual_ingestion import IngestionPipeline
from engine.data_fusion import DataFusionEngine
from engine.hotspot_analyzer import HotspotAnalyzer

class TestJanSetu(unittest.TestCase):
    def test_pii_scrubbing(self):
        cleaned, had_pii = IngestionPipeline.scrub_pii("Mera phone 9876543210 hai.")
        self.assertTrue(had_pii)
        self.assertIn("[REDACTED_PHONE]", cleaned)

    def test_hotspots_bounds(self):
        hotspots = HotspotAnalyzer(DataFusionEngine().build_fused_profiles()).analyze_all()
        self.assertGreater(len(hotspots), 0)
        for h in hotspots:
            self.assertTrue(0.0 <= h['priority_hotspot_score'] <= 100.0)

if __name__ == '__main__':
    unittest.main()
