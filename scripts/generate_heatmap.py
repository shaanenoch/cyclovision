"""
CycloneAI - Explainability Heatmap Generator
Generates Grad-CAM / Attention heatmap overlay from a satellite image.
"""
import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.config import DEMO_DATA_DIR, UPLOADS_DIR
from ml.explainability.gradcam import GradCamExplainer

def main():
    parser = argparse.ArgumentParser(description="Generate AI Attention Heatmap for Cyclone Image")
    parser.add_argument("--image", type=str, default=str(DEMO_DATA_DIR / "demo_satellite_ir.png"), help="Path to input satellite image")
    parser.add_argument("--output", type=str, default="cli_heatmap.png", help="Output filename in uploads/")
    args = parser.parse_args()

    print("=" * 60)
    print("CycloneAI: Explainability Grad-CAM Heatmap Generator")
    print("=" * 60)
    print(f"Input Image: {args.image}")
    
    explainer = GradCamExplainer()
    res = explainer.generate_heatmap(args.image, output_filename=args.output)
    
    print(f"Heatmap Generated: {res['heatmap_path']}")
    print(f"Caption: {res['caption']}")
    print(f"Peak Attention Coordinates: ({res['attention_peak_x']}, {res['attention_peak_y']})")
    print("=" * 60)

if __name__ == "__main__":
    main()
