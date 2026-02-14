
# MobilityGraph

Sistem Semantic Web/Knowledge Graph untuk perencanaan rute wisata Jakarta berbasis RDF/Turtle.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run API server
uvicorn app.main:app --reload

# Open browser
# API Docs: http://localhost:8000/docs
# Frontend: http://localhost:8000
```

## Features
- ✅ Multi-modal routing (MRT, LRT, TransJakarta)
- ✅ Jakarta tourist destinations (Ancol, Kota Tua, TMII, Monas)
- ✅ Region-based filtering
- ✅ Interactive map visualization
- ✅ Cost estimation

## Project Structure
```
├── app/              # FastAPI backend
├── mobilitygraph/    # Core RDF/routing library
├── dataTTL/          # RDF data files
├── static/           # Frontend (Tailwind CSS)
├── validation/       # SHACL shapes
└── tests/            # Pytest tests
```
>>>>>>> 99d712b (initial commit)
>>>>>>> b6afe7a (Initial commit)
