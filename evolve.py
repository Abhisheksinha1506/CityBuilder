#!/usr/bin/env python3
import json
import os
import math
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

    # Analyze current directory and parent (to get interesting metrics if this is in a subfolder)
    # For Autogit, we analyze the whole ecosystem if possible, or just this project.
    # The prompt says "repository's Python code". We'll look at the current project and its parent.
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
    """Generate city.json from radon data."""
    buildings = []
    functions = []
    
    # Flatten radon data
    for file_path, entries in data.items():
        for entry in entries:
            if entry.get("type") in ["function", "method", "class"]:
                functions.append({
                    "name": entry.get("name"),
                    "complexity": entry.get("complexity", 1),
                    "type": entry.get("type"),
                    "file": Path(file_path).name
                })
    
    # Sort by complexity
    functions.sort(key=lambda x: x["complexity"], reverse=True)
    
    max_buildings = 200 # Increased limit
    functions = functions[:max_buildings]
    
    if not functions:
        return {"buildings": [], "metrics": {"avg_complexity": 0, "total_functions": 0}}
        
    avg_complexity = sum(f["complexity"] for f in functions) / len(functions)
    
    spacing = 4 # More space for readability
    grid_size = int(math.ceil(math.sqrt(len(functions))))
    
    for i, func in enumerate(functions):
        complexity = func["complexity"]
        
        # Determine building dimensions based on type
        if func["type"] == "class":
            width, depth = 2.0, 2.0
            height = max(1.5, (complexity / avg_complexity) * 8.0)
            color = "#66aaff" # Blue for classes
        else:
            width, depth = 1.2, 1.2
            height = max(1.0, (complexity / avg_complexity) * 6.0)
            color = "#ff6666" if complexity > 10 else "#888888"
        
        x = (i % grid_size) * spacing - (grid_size * spacing / 2)
        z = (i // grid_size) * spacing - (grid_size * spacing / 2)
        
        buildings.append({
            "x": round(x, 2),
            "z": round(z, 2),
            "width": width,
            "depth": depth,
            "height": round(height, 2),
            "color": color,
            "name": func["name"],
            "type": func["type"],
            "file": func["file"],
            "complexity": complexity
        })
        
    return {
        "buildings": buildings,
        "metrics": {
            "avg_complexity": round(avg_complexity, 2),
            "total_functions": len(functions),
            "generation_time": datetime.now().isoformat()
        }
    }

def main():
    print("🏙️ Procedural City Builder - Analysis Step")
    data = run_radon()
    city_data = generate_city(data)
    
    with open("city.json", "w") as f:
        json.dump(city_data, f, indent=2)
        
    print(f"✅ city.json generated with {city_data['metrics']['total_functions']} buildings.")
    print(f"📊 Average Complexity: {city_data['metrics']['avg_complexity']}")

if __name__ == "__main__":
    main()
