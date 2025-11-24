# 🌍 3D World Population Visualization

An interactive 3D visualization of global population density using hexagonal grids. Explore population distribution across countries with stunning visual effects, dynamic theming, and real-time rendering.

![Population Density Map](https://img.shields.io/badge/Deck.gl-Latest-blue) ![H3](https://img.shields.io/badge/H3-Hexagonal_Grid-green) ![License](https://img.shields.io/badge/license-MIT-orange)

## ✨ Features

- **🗺️ Interactive 3D Map**: Fly across the globe with smooth camera controls and pan/zoom capabilities
- **📊 H3 Hexagonal Grid**: Population data visualized using Uber's H3 hexagonal hierarchical spatial index at 400m resolution
- **🎨 Multiple Themes**: 13+ built-in color presets including Nordic Blue, Emerald, Magma, Cyberpunk, and more
- **💡 Dynamic Lighting**: Adjustable directional lighting with shadow effects for enhanced depth perception
- **🌐 200+ Countries**: Pre-processed population data covering the entire world
- **📸 Export**: Snapshot feature to capture and download your current view
- **⚡ Performance Optimized**: Dynamic data sampling for smooth interaction even with millions of data points
- **🎯 Adaptive Scaling**: Automatic view-based scaling to maintain visual consistency across zoom levels

## 🚀 Quick Start

### Prerequisites

- Python 3.7+ (for data processing)
- Modern web browser with WebGL support
- [Kontur Population Dataset](https://data.humdata.org/dataset/kontur-population-dataset) (20231101 release)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/tingkart/hex_population_world_map.git
   cd hex_population_world_map
   ```

2. **Download the population dataset**
   
   Download `kontur_population_20231101.gpkg` from [Kontur Population Dataset](https://data.humdata.org/dataset/kontur-population-dataset) and place it in the project root directory.

3. **Set up Python environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install pandas h3 shapely geopandas
   ```

4. **Generate country data** (optional - only needed for new countries)
   ```bash
   python generate_world_data.py
   ```
   
   This will process the GeoPackage and generate CSV files for each country in `public/data/`.

5. **Serve the application**
   ```bash
   python -m http.server 8066
   ```
   
   Open your browser to `http://localhost:8066`

## 📁 Project Structure

```
├── index.html                    # Main application
├── generate_world_data.py        # Multi-threaded data processor for all countries
├── process_data.py              # Norway-specific data processor (legacy)
├── world_countries.geojson      # Country boundaries
├── norway.geojson               # Norway-specific boundaries
├── public/
│   ├── data/                    # Country-specific CSV files (CHN.csv, USA.csv, etc.)
│   └── countries.json           # Country metadata (centroids, bounding boxes)
└── README.md
```

## 🎮 Usage

### Controls

- **Pan**: Click and drag
- **Zoom**: Scroll wheel / Pinch
- **Rotate**: Right-click and drag
- **Tilt**: Ctrl + drag (vertical)

### UI Features

- **Country Selector**: Switch between 200+ countries instantly
- **Settings Panel**: Customize lighting, themes, and visual effects
- **Snapshot Tool**: Export high-resolution PNG images of your current view
- **Legend**: Displays population density scale

### Available Themes

| Theme | Description | Best For |
|-------|-------------|----------|
| Nordic Blue | Icy blue gradient (default) | Clean, professional presentations |
| Emerald | Green to teal gradient | Natural, organic feel |
| Magma | Orange to purple gradient | High-contrast visualizations |
| Cyberpunk | Purple to cyan gradient | Dark mode, futuristic style |
| Golden Hour | Brown to gold gradient | Warm, inviting visualizations |
| Viridis | Perceptually uniform purple-yellow | Scientific accuracy |
| Ocean | Teal to aqua gradient | Maritime themes |

## 🔧 Data Processing

### Understanding the Pipeline

1. **Source Data**: Kontur Population GeoPackage (H3 resolution 8 ≈ 400m hexagons)
2. **Country Filtering**: Uses GeoJSON boundaries to filter H3 cells per country
3. **Output Format**: Lightweight CSV files (`h3_index, population`)
4. **Metadata**: JSON index with country codes, names, centroids, and bounding boxes

### Processing Custom Countries

To process specific countries or update data:

```python
# Edit generate_world_data.py configuration
DB_PATH = 'kontur_population_20231101.gpkg'
GEOJSON_PATH = 'world_countries.geojson'
OUTPUT_DIR = 'public/data'

# Run the processor
python generate_world_data.py
```

The script uses multiprocessing to parallelize country processing across all CPU cores.

## 🛠️ Technology Stack

- **[Deck.gl](https://deck.gl/)**: WebGL-powered visualization framework
- **[H3](https://h3geo.org/)**: Hexagonal hierarchical spatial indexing
- **[MapLibre GL](https://maplibre.org/)**: Base map rendering
- **[Pandas](https://pandas.pydata.org/)**: Data processing
- **[Shapely](https://shapely.readthedocs.io/)**: Geometric operations

## 🌟 Key Technical Features

### Adaptive View-Based Scaling

The visualization dynamically adjusts the height scale based on:
- Global maximum population in the dataset
- Visible maximum population in the current viewport
- Smooth transitions when panning/zooming

### Shadow Rendering

Realistic shadows are cast on a transparent ground plane, enhancing depth perception without cluttering the visualization.

### Performance Optimization

- **Data Sampling**: Automatically samples large datasets when more than 5 million points are visible
- **Debounced Updates**: View state changes are debounced to prevent excessive recalculations
- **Efficient Data Format**: CSV files without headers minimize file size and parsing time

## 📊 Dataset Information

**Source**: [Kontur Population Dataset](https://data.humdata.org/dataset/kontur-population-dataset)  
**Release**: 20231101  
**Resolution**: H3 Level 8 (≈ 400m hexagons)  
**Coverage**: Global  
**License**: CC BY 4.0

> Each hexagon represents population density within a 400-meter area, providing highly granular insights into human settlement patterns.

## 🤝 Contributing

Contributions are welcome! Here are some ways you can help:

- 🐛 Report bugs and issues
- 💡 Suggest new features or themes
- 📝 Improve documentation
- 🎨 Add new color schemes
- ⚡ Optimize performance

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Kontur](https://www.kontur.io/)** for the comprehensive population dataset
- **[Uber](https://www.uber.com/)** for the H3 hexagonal grid system
- **[Deck.gl](https://deck.gl/)** for the powerful visualization framework
- **[Natural Earth](https://www.naturalearthdata.com/)** for country boundary data

## 📧 Contact

For questions, suggestions, or collaboration opportunities, please open an issue or reach out through GitHub.

---

**Made with ❤️ for data visualization and geographic exploration**
