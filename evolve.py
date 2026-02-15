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
    repos_data = requests.get(repos_url, headers=headers).json()
    
    if isinstance(repos_data, dict) and "message" in repos_data:
        print(f"❌ API Error: {repos_data['message']}")
        return {}

    all_nodes = {}
    
    # Only analyze selected repos to keep city manageable and relevant
    target_repos = [
        "autonomous-zoo", "autonomous-zoo-expansion", "langtons-ant", 
        "prime-spiral", "Quine-Garden", "game-of-life", "CityBuilder"
    ]

    for repo in repos_data:
        name = repo['name']
        if name not in target_repos and len(target_repos) > 0: continue
        
        print(f"📁 Analyzing District: {name}")
        tree_url = f"https://api.github.com/repos/{username}/{name}/git/trees/{repo['default_branch']}?recursive=1"
        tree_data = requests.get(tree_url, headers=headers).json()
        
        if 'tree' not in tree_data: continue
        
        metrics = []
        for item in tree_data['tree']:
            if item['type'] == 'blob' and item['path'].endswith(('.py', '.js', '.html', '.css', '.c')):
                # Use size/500 as a proxy for complexity since we can't run radon without cloning
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
    """Fallback local analysis using radon for cyclomatic complexity."""
    print("🔍 Scanning local codebase with radon...")
    data = {}
    for root, _, files in os.walk('.'):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    output = subprocess.check_output(['radon', 'cc', '-j', path])
                    metrics = json.loads(output)
                    data[path] = [m for m in metrics.values() if isinstance(m, list)][0]  # Flatten
                except Exception as e:
                    print(f"⚠️ Radon failed on {path}: {e}")
    return data

def get_address(file_path, x, z):
    """Generate a specific human-readable address."""
    parts = file_path.split('/')
    project = parts[0] if len(parts) > 1 else "Mainframe"

    districts = {
        "autonomous-zoo": "Genome Sector",
        "autonomous-zoo-expansion": "Evolution Heights",
        "langtons-ant": "The Colony",
        "prime-spiral": "Ulam Plaza",
        "Quine-Garden": "Recursive Gardens",
        "game-of-life": "Conway Commons",
        "CityBuilder": "Core Architecture Zone",
        "procedural-city-builder": "Core Architecture Zone"
    }
    
    district = districts.get(project, f"{project.replace('-', ' ').title()} District")
    
    # Street Name Generator
    streets = ["Mainframe Ave", "Kernel Street", "Logic Lane", "Process Parkway", "Silicon Way", "Bit Blvd", "Data Drive"]
    street = streets[abs(hash(file_path)) % len(streets)]
    
    # Block mapping
    block = f"Block {chr(65 + (abs(int(x)) % 26))}"
    
    return f"{district} // {street} // {block}"

def generate_city(data):
    """Generate city.json with detailed buildings, gardens, and infrastructure."""
    buildings = []
    gardens = []
    roads = []
    vehicles = []  # For traffic simulation
    billboards = []  # For ads/granulation
    
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
        return {"buildings": [], "gardens": [], "roads": [], "vehicles": [], "billboards": [], "stats": {}}
    
    avg_complexity = sum(n["complexity"] for n in nodes) / len(nodes)
    
    # Group by district (repo)
    districts = {}
    for n in nodes:
        repo = n["file"].split('/')[0]
        if repo not in districts:
            districts[repo] = []
        districts[repo].append(n)
    
    # Spread districts across city
    district_centers = [
        {"x": -150, "z": -150}, {"x": 150, "z": -150}, {"x": -150, "z": 150}, {"x": 150, "z": 150},
        {"x": 0, "z": 0}, {"x": -300, "z": 0}, {"x": 300, "z": 0}, {"x": 0, "z": -300}, {"x": 0, "z": 300}
    ]
    district_index = 0
    
    for repo, district_nodes in districts.items():
        if district_index >= len(district_centers):
            break
        center = district_centers[district_index]
        district_index += 1
        
        cols = int(math.ceil(math.sqrt(len(district_nodes))))
        spacing = 20.0  # Wider for SimCity feel
        
        for i, n in enumerate(district_nodes):
            row = i // cols
            col = i % cols
            
            x = center["x"] + col * spacing - (cols * spacing) / 2 + random.uniform(-5, 5)  # Jitter for organic layout
            z = center["z"] + row * spacing - (cols * spacing) / 2 + random.uniform(-5, 5)
            
            complexity = n["complexity"]
            height = max(6.0, (complexity / avg_complexity) * 30.0)  # Taller, varied
            
            # Detailed styles
            style_options = ["modern", "industrial", "cyberpunk", "art_deco", "brutalist", "futuristic"]
            style = random.choice(style_options) if complexity > 5 else "standard"
            
            roof_decor = random.choice(["helipad", "antenna_array", "billboard", "roof_garden", "solar_panels", "water_tank", "neon_sign", None])
            
            color = "#ff4444" if complexity > 15 else "#4488ff" if n["type"] == "class" else "#888888"
            
            # Window details for granulation
            windows = {
                "count": random.randint(20, 100) * complexity,  # More windows on complex buildings
                "pattern": random.choice(["grid", "random", "striped", "diagonal"]),
                "lit_percent": random.uniform(0.4, 0.9)  # For night lights
            }
            
            # New: Interiors - Simple data for floors/rooms
            num_floors = max(1, int(height / 5))  # ~5 units per floor
            interiors = {
                "floors": num_floors,
                "rooms_per_floor": random.randint(4, 12),
                "room_types": random.sample(["office", "server_room", "lobby", "conference", "elevator"], k=random.randint(2, 5)),
                "furniture_density": random.uniform(0.3, 0.8)  # For procedural furniture in JS
            }
            
            buildings.append({
                "x": x,
                "z": z,
                "width": random.uniform(8, 16),
                "height": height,
                "depth": random.uniform(8, 16),
                "color": color,
                "style": style,
                "roof_decor": roof_decor,
                "name": n["name"],
                "type": "Skyscraper" if height > 20 else "Building",
                "complexity": complexity,
                "file": n["file"],
                "address": get_address(n["file"], x, z),
                "windows": windows,
                "upgrades": random.randint(0, 3),  # For sim: Levels up over time
                "interiors": interiors  # New field
            })
            
            # Gardens/Parks
            if random.random() < 0.35:
                gardens.append({
                    "x": x + random.uniform(-15, 15),
                    "z": z + random.uniform(-15, 15),
                    "size": random.uniform(10, 30),
                    "foliage": random.randint(15, 50),
                    "type": random.choice(["park", "fountain", "statue", "plaza"])
                })
            
            # Billboards for detail
            if random.random() < 0.25 and complexity > 5:
                billboards.append({
                    "x": x + random.uniform(-10, 10),
                    "z": z - 10,  # In front
                    "text": f"{n['name']} Sector",
                    "size": random.uniform(5, 10),
                    "neon": random.choice([True, False])
                })
    
    # Roads: Connect districts with highways
    road_width = 6
    for i in range(len(district_centers) - 1):
        start = district_centers[i]
        end = district_centers[i+1]
        dx = end["x"] - start["x"]
        dz = end["z"] - start["z"]
        length = math.sqrt(dx**2 + dz**2)
        vertical = abs(dz) > abs(dx)
        traffic = random.randint(10, 30)  # Busier roads
        roads.append({
            "x": start["x"],
            "z": start["z"],
            "w": road_width,
            "l": length,
            "vertical": vertical,
            "lights": True,
            "traffic": traffic,
            "type": "highway" if length > 200 else "street"
        })
    
    # Vehicles for traffic sim
    for road_idx, road in enumerate(roads):
        for _ in range(road["traffic"]):
            vehicles.append({
                "road_id": road_idx,
                "position": random.uniform(0, 1),  # Fraction along road
                "speed": random.uniform(0.02, 0.08),  # For animation
                "type": random.choice(["car", "truck", "bus", "bike"]),
                "direction": random.choice([1, -1])  # Bidirectional
            })
    
    # Stats for game HUD
    stats = {
        "urban_density": f"{len(buildings)} structures",
        "district_count": len(districts),
        "traffic_level": sum(r["traffic"] for r in roads),
        "green_space": len(gardens),
        "mainframe_health": "Stable" if avg_complexity < 10 else "High Activity",
        "system_load": f"{int((avg_complexity / 20) * 100)}%",
        "last_evolution": datetime.now().strftime("%Y-%m-%d %H:%M IST"),
        "population": len(buildings) * random.randint(50, 200),  # Sim metric
        "happiness": int(50 + (len(gardens) / max(1, len(buildings))) * 50)  # Based on green space
    }

    return {
        "buildings": buildings, 
        "gardens": gardens, 
        "roads": roads,
        "vehicles": vehicles,
        "billboards": billboards,
        "stats": stats
    }

def save_city(city_data):
    """Save city data to city.json."""
    with open("city.json", "w") as f:
        json.dump(city_data, f, indent=2)
    print(f"✅ city.json updated.")
    print(f"📊 Population: {city_data['stats']['urban_density']}")
    print(f"🖥️ Status: {city_data['stats']['mainframe_health']}")

def main():
    print("🏙️ Procedural City Builder - Evolution Pulse")
    token = os.getenv("GITHUB_TOKEN")
    
    if token:
        print("🤖 Running in Cloud Crawler Mode...")
        data = fetch_github_data(token)
    else:
        print("💻 Running in Local Radon Mode...")
        data = run_radon()
        
    if data:
        city_data = generate_city(data)
        save_city(city_data)
    else:
        print("⚠️ No data collected. City remains unchanged.")

if __name__ == "__main__":
    main()