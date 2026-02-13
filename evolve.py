#!/usr/bin/env python3
import json
import os
import math
import random
import subprocess
from datetime import datetime
from pathlib import Path

def run_radon():
    """Run radon to get complexity data."""
    try:
        # Check if radon is installed
        subprocess.run(["radon", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ Radon not found. Installing...")
        subprocess.run(["pip", "install", "radon"], check=True)

    target_dir = ".." 
    print(f"🔍 Analyzing complexity in: {target_dir}")
    
    result = subprocess.run(
        ["radon", "cc", target_dir, "-j"],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    return {}

def generate_city(data):
    """Generate city.json with buildings, gardens, and infrastructure."""
    buildings = []
    gardens = []
    roads = []
    
    # Identify files/complexities
    nodes = []
    for file, metrics in data.items():
        if isinstance(metrics, list):
            for m in metrics:
                nodes.append({
                    "name": m.get("name", "anon"),
                    "type": m.get("type", "func"),
                    "complexity": m.get("complexity", 1),
                    "file": file
                })
    
    if not nodes:
        return {"buildings": [], "gardens": [], "roads": [], "stats": {}}
    
    avg_complexity = sum(n["complexity"] for n in nodes) / len(nodes)
    
    # Place buildings on a grid
    cols = int(math.ceil(math.sqrt(len(nodes))))
    spacing = 6.0
    
    for i, n in enumerate(nodes):
        row = i // cols
        col = i % cols
        
        x = col * spacing - (cols * spacing) / 2
        z = row * spacing - (cols * spacing) / 2
        
        complexity = n["complexity"]
        height = max(2.5, (complexity / avg_complexity) * 10.0)
        
        # Sim City Aesthetics
        if n["type"] == "class":
            color = "#4488ff" # Tech Blue
            b_type = "Corporate Tower"
        elif complexity > 10:
            color = "#ff4444" # Critical Core
            b_type = "Mainframe Nucleus"
        else:
            color = "#888888" # Regular Node
            b_type = "Data Unit"

        buildings.append({
            "x": x,
            "z": z,
            "width": 3,
            "height": height,
            "depth": 3,
            "color": color,
            "name": n["name"],
            "type": b_type,
            "complexity": complexity,
            "file": n["file"]
        })

        # Procedural Gardens
        if random.random() < 0.2:
            gardens.append({
                "x": x + 3,
                "z": z + 3,
                "size": random.uniform(2, 4)
            })

    # Road Grid
    for r in range(-10, 11):
        if r % 3 == 0:
            roads.append({"x": r * 10, "z": 0, "w": 2, "l": 200, "vertical": False})
            roads.append({"x": 0, "z": r * 10, "w": 2, "l": 200, "vertical": True})

    # Sim City Style Stats
    stats = {
        "urban_density": f"{len(buildings)} structures",
        "mainframe_health": "Stable" if avg_complexity < 7 else "Stress Detected",
        "system_load": f"{int(avg_complexity * 10)}% Capacity",
        "last_evolution": datetime.now().strftime("%Y-%m-%d %H:%M")
    }

    return {
        "buildings": buildings, 
        "gardens": gardens, 
        "roads": roads, 
        "stats": stats
    }

def main():
    print("🏙️ Procedural City Builder - Analysis Step")
    data = run_radon()
    city_data = generate_city(data)
    
    with open("city.json", "w") as f:
        json.dump(city_data, f, indent=2)
        
    print(f"✅ city.json generated.")
    print(f"📊 {city_data['stats']['urban_density']}")
    print(f"🖥️ {city_data['stats']['mainframe_health']}")

if __name__ == "__main__":
    main()
