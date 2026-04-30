# BVLOS Flight Planning Tool

A web-based flight planning tool for Beyond Visual Line of Sight (BVLOS) drone operations in Canada. Analyze airspace conflicts, population exposure, and regulatory compliance for your RPAS missions.

## Features

- 🗺️ **Interactive Map Display** - View flight paths on an interactive map centered on Alberta
- ✈️ **Airspace Analysis** - Check for conflicts with controlled airspace (CYA, CYR zones)
- 🏞️ **Parks & Protected Areas** - Visualize provincial and national parks
- 👥 **Population Density** - Assess population exposure along flight routes
- 📁 **KML/KMZ Support** - Upload mission plans from QGroundControl, Mission Planner
- 📊 **Conflict Detection** - Automated spatial analysis of airspace violations

## Quick Start

### Installation

1. **Clone and navigate**
```bash
git clone https://github.com/Ohdows14/BVLOS-Flight-Planning-Tool.git
cd BVLOS-Flight-Planning-Tool
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Add your data files to:**
   - `data/airspace/canadian_airspace.geojson`
   - `data/parks/alberta_parks.geojson`
   - `data/population/` (optional for v1.0)

4. **Run the app**
```bash
streamlit run app.py
```

Opens at `http://localhost:8501`

## Usage

1. Toggle map layers in the sidebar
2. Upload KML/KMZ flight plan
3. Review airspace conflicts
4. Analyze population exposure

## Data Structure

Place your files in:
```
data/
├── airspace/
│   ├── canadian_airspace.geojson (required)
│   ├── *.cub
│   └── *.sua
├── parks/
│   └── alberta_parks.geojson (required)
└── population/
    └── alberta_da.geojson (optional)
```

## Supported Formats

- **Flight Plans:** KML, KMZ
- **Airspace:** GeoJSON, .cub, .sua, Shapefile
- **Parks/Population:** GeoJSON, Shapefile

## Roadmap

- ✅ Map display & layer controls
- ✅ KML upload & flight path display  
- ⏳ Automated conflict detection
- 📋 SFOC report generation (planned)
- 🌦️ Weather integration (planned)

## Troubleshooting

**Module errors:**
```bash
pip install -r requirements.txt --upgrade
```

**Data not loading:** Ensure files are in correct `data/` subfolders

**Map not displaying:** Check Streamlit version >= 1.32.0

---

**Built for Canadian RPAS operators** | MIT License | April 2026
