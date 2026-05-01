# Flight Delay Dashboard

An interactive flight delay dashboard built on top of the **Palantir Foundry** ontology API.

## What it does

- Displays all 178 US airports on a live map, color-coded by average departure delay
- Click any airport to see routes fanning out to every destination, colored by delay severity
- Filter by month to see how airport performance changed throughout 2023
- Search airports by name, code, or city with autocomplete

## Tech Stack

- **Backend:** Python / FastAPI — connects to Palantir Foundry via the REST API SDK
- **Data:** Palantir Foundry ontology (`ExampleAirport`, `ExampleFlight`) — server-side aggregation via `group_by`
- **Frontend:** Vanilla JS + Leaflet.js — interactive map with popups, polylines, and live filtering

## Setup

1. Clone the repo
2. Create a virtual environment and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and fill in your Foundry credentials:
   ```
   FOUNDRY_HOSTNAME=your-stack.palantirfoundry.com
   FOUNDRY_TOKEN=your-token-here
   ```
4. Run the server:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Open `http://localhost:8000`

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /airports` | All airports with coordinates and average delays |
| `GET /delays?month=4` | Per-airport delay averages filtered by month |
| `GET /routes/{code}` | All routes from a given airport with avg delays |
