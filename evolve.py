#!/usr/bin/env python3
import json
import os
import math
import random
import subprocess
import requests
from datetime import datetime
from pathlib import Path

def fetch_github_data(token):
    """Fetch tree and metadata for all repos via GitHub API."""
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    username = "Abhisheksinha1506"
    
    print(f"🌐 Fetching ecosystems for user: {username}")
    repos_url = f"https://api.github.com/users/{username}/repos?per_page=100"
    repos = requests.get(repos_url, headers=headers).json()
    
    all_nodes = {}
    
    # Only analyze selected repos to keep city manageable and relevant
    target_repos = [
        "autonomous-zoo", "autonomous-zoo-expansion", "langtons-ant", 
        "prime-spiral", "Quine-Garden", "game-of-life", "CityBuilder"
    ]

    for repo in repos:
        name = repo['name']
        if name not in target_repos and len(target_repos) > 0: continue
        
        print(f"📁 Analyzing District: {name}")
        tree_url = f"https://api.github.com/repos/{username}/{name}/git/trees/{repo['default_branch']}?recursive=1"
        tree_data = requests.get(tree_url, headers=headers).json()
        
        if 'tree' not in tree_data: continue
        
        metrics = []
        for item in tree_data['tree']:
            if item['type'] == 'blob' and item['path'].endswith(('.py', '.js', '.html', '.css', '.c')):
                # Use size/1000 as a proxy for complexity since we can't run radon without cloning
                # This ensures the city "looks" right based on file volume
                size_complexity = max(1, min(20, item.get('size', 0) // 500))
                metrics.append({
                    "name": Path(item['path']).stem,
                    "type": "class" if "evolve" in item['path'] else "func",
                    "complexity": size_complexity,
                    "file": f"{name}/{item['path']}"
                })
        
        all_nodes[name] = metrics
        
    return all_nodes

def run_radon():
    """Fallback local analysis."""

def get_district_name(file_path):
    """Map repo names to districts."""
    parts = file_path.split('/')
    project = parts[0] if len(parts) > 1 else "Mainframe"

    districts = {
        "autonomous-zoo": "Genome Sector",
        "autonomous-zoo-expansion": "Evolution Heights",
        "langtons-ant": "The Colony District",
        "prime-spiral": "Ulam Plaza",
        "Quine-Garden": "Recursive Gardens",
        "game-of-life": "Conway Commons",
        "CityBuilder": "Core Architecture Zone",
        "procedural-city-builder": "Core Architecture Zone"
    }
    
    base_name = districts.get(project, f"{project.replace('-', ' ').title()} District")
    return f"{base_name} // 0x{abs(hash(file_path)) % 0xFFFF:04X}"

def generate_city(data):
    """Generate city.json with buildings, gardens, and infrastructure."""
    buildings = []
    gardens = []
    roads = []
    
    # Flatten nodes from multi-repo data
    nodes = []
    if isinstance(data, dict) and any(isinstance(v, list) for v in data.values()):
        # API Crawler Format
        for repo, files in data.items():
            nodes.extend(files)
    else:
        # Radon Format fallback
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
    print("🏙️ Procedural City Builder - Evolution Pulse")
    token = os.getenv("GITHUB_TOKEN")
    
    if token:
        print("🤖 Running in Cloud Crawler Mode...")
        data = fetch_github_data(token)
    else:
        print("💻 Running in Local Radon Mode...")
        data = run_radon()
        
    city_data = generate_city(data)
    
    with open("city.json", "w") as f:
        json.dump(city_data, f, indent=2)
        
    print(f"✅ city.json updated.")
    print(f"📊 Population: {city_data['stats']['urban_density']}")
    print(f"🖥️ Status: {city_data['stats']['mainframe_health']}")

if __name__ == "__main__":
    main()
