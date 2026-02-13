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

def get_district_name(file_path):
    """Map file paths to Sim City style districts."""
    path = Path(file_path)
    parts = path.parts
    
    # Extract the main project directory name
    if len(parts) > 1:
        project = parts[1]
    else:
        project = "Mainframe"

    districts = {
        "autonomous-zoo": "Genome Sector",
        "autonomous-zoo-expansion": "Evolution Heights",
        "langtons-ant": "The Colony District",
        "prime-spiral": "Ulam Plaza",
        "Quine Garden": "Recursive Gardens",
        "game-of-life": "Conway Commons",
        "chess-simulation": "Grandmaster Square",
        "procedural-city-builder": "Core Architecture Zone"
    }
    
    base_name = districts.get(project, f"{project.replace('-', ' ').title()} District")
    return f"{base_name} // 0x{abs(hash(file_path)) % 0xFFFF:04X}"

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
    spacing = 8.0 # Increased spacing for more granulation
    
    for i, n in enumerate(nodes):
        row = i // cols
        col = i % cols
        
        x = col * spacing - (cols * spacing) / 2
        z = row * spacing - (cols * spacing) / 2
        
        complexity = n["complexity"]
        height = max(3.0, (complexity / avg_complexity) * 12.0)
        
        # Sim City Aesthetics & Granulation
        roof_decor = None
        if n["type"] == "class":
            color = "#4488ff" # Tech Blue
            b_type = "Corporate Tower"
            style = "modernist"
            if height > 10:
                roof_decor = "helipad"
        elif complexity > 15:
            color = "#ff4444" # Critical Core
            b_type = "Mainframe Nucleus"
            style = "industrial"
            roof_decor = "antenna_array"
        elif complexity > 8:
            color = "#ffaa44" # Warning Zone
            b_type = "Logic Processor"
            style = "skyscraper"
            roof_decor = "hvac_unit"
        else:
            color = "#888888" # Regular Node
            b_type = "Data Unit"
            style = "standard"
            if random.random() < 0.3:
                roof_decor = "small_antenna"

        buildings.append({
            "x": x,
            "z": z,
            "width": 4,
            "height": height,
            "depth": 4,
            "color": color,
            "style": style,
            "roof_decor": roof_decor,
            "name": n["name"],
            "type": b_type,
            "complexity": complexity,
            "file": n["file"],
            "address": get_district_name(n["file"])
        })

        # Procedural Gardens with more detail
        if random.random() < 0.25:
            gardens.append({
                "x": x + 5,
                "z": z + 5,
                "size": random.uniform(3, 5),
                "foliage": random.randint(3, 8)
            })

    # Enhanced Road Grid with light posts info
    for r in range(-15, 16):
        if r % 4 == 0:
            roads.append({"x": r * 10, "z": 0, "w": 3, "l": 400, "vertical": False, "lights": True})
            roads.append({"x": 0, "z": r * 10, "w": 3, "l": 400, "vertical": True, "lights": True})

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
    print("🏙️ Procedural City Builder - Hyper-Granularity Evolution")
    data = run_radon()
    city_data = generate_city(data)
    
    with open("city.json", "w") as f:
        json.dump(city_data, f, indent=2)
        
    print(f"✅ city.json updated with high-granularity data.")
    print(f"📊 Population: {city_data['stats']['urban_density']}")
    print(f"🖥️ Status: {city_data['stats']['mainframe_health']}")

if __name__ == "__main__":
    main()
