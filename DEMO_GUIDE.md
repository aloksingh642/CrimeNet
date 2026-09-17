# CrimeNet Intelligence - Demo Guide

## Quick Start (Current Running Instance)

The system is already running:

- **Frontend**: https://5173-i0lhmbnllt0rf8xj8ivkx.e2b.app (or http://localhost:5173 locally)
- **Backend**: https://8000-i0lhmbnllt0rf8xj8ivkx.e2b.app (or http://localhost:8000 locally)
- **API Docs**: http://localhost:8000/docs

### Login
- Username: `investigator` / Password: `invest123`
- Username: `admin` / Password: `admin123`
- Username: `analyst` / Password: `analyst123`

---

## Demonstration Scenario: CASE-2026-001

### Step 1: Login
Go to `/login` and use investigator credentials.

### Step 2: Dashboard
You will see:
- Active Cases: 10
- Total Entities: ~500+ nodes
- Relationships: ~1000+ edges
- Incidents: 300
- Communities: 5 detected
- Pattern Alerts: Multiple anomalies

The dashboard shows:
- Most Connected Entities (Degree Centrality)
- Detected Communities
- Pattern Alerts with explainable evidence
- Entity Distribution

### Step 3: Open Case CASE-2026-001
- Go to Cases → Click CASE-2026-001
- Title: "Cross-Community Financial & Communication Analysis"
- Shows network overview, most connected entities, investigation workflow

### Step 4: Graph Explorer
- Go to Graph Explorer
- See 300 nodes (configurable) with color coding:
  - Blue: Person
  - Green: Phone
  - Orange: Vehicle
  - Red: Location
  - Purple: Organization
- **Interactions**:
  - Zoom with mouse wheel
  - Drag to pan
  - Click node to see details
  - Click edge to see relationship evidence
  - Use filters: Node Type, Relationship Type
  - Change layouts: Cose, Circle, Grid, Tree
- **Shortest Path**:
  - Enter source: `person_1`
  - Enter target: `person_10`
  - Click "Find Path"
  - Shows path like: Person A → Phone → Communication → Phone → Person B

### Step 5: Entity Explorer
- Search for "Rahul Sharma" or any name
- See results across persons, phones, vehicles, etc.
- Shows 50 sample persons with community assignment and centrality

### Step 6: Analytics
- **Network Density**: e.g., 0.015
- **Components**: e.g., 3 disconnected components
- **Degree Centrality**: Top 10 most connected with interpretation:
  - "High network connectivity - potentially significant network position"
  - Evidence: "Connected to 15 entities directly"
- **Betweenness**: Bridge entities
- **PageRank & Closeness**: Visual bar charts
- **Communities**: 5 clusters with:
  - Size, edge count, density
  - Central nodes
  - Type distribution
  - Description

### Step 7: Pattern Detection / Findings
- Shows anomalies:
  - **Communication Spike**: "Communication increased from 3/week to 27/week (800% increase)"
    - Evidence: WHAT, WHY, WHEN, WHO, baseline, current, increase %
  - **Unusual Transaction**: "₹1,200,000 exceeds average ₹45,000"
    - Evidence: mean, stdev, threshold
  - **Location Overlap**: "Repeated activity at Central Market"
  - **Bridge Entity**: High betweenness
  - **High Connectivity**: Degree > threshold
- Actions: Save to Case, Mark Reviewed, False Positive
- **Explainable AI**: Every finding shows WHAT, WHY, WHEN, WHO, evidence

### Step 8: Timeline
- Chronological view of:
  - Incidents (red)
  - Communications (green)
  - Transactions (blue)
  - Documents (gray)
- Filter by type
- Shows entities, location, timestamp

### Step 9: Evidence Explorer
- Enter source: "Rahul" and target: "Amit"
- Shows supporting evidence:
  - Communications: 14 calls
  - Transactions
  - Incidents
  - Each with confidence, timestamp, content

### Step 10: Documents & NLP
- View 100 synthetic FIR-style documents
- Example: "Rahul Sharma was seen near Central Market with Amit Verma. Vehicle HR26AB1234 observed."
- Click "Process NLP" → Extracts:
  - PERSON: Rahul Sharma, Amit Verma
  - LOCATION: Central Market
  - VEHICLE: HR26AB1234
  - DATE: 12 March
  - Relationships: ASSOCIATED_WITH, OBSERVED_AT

### Step 11: Reports
- Select a case → Generates report with:
  - Executive summary
  - Network statistics
  - Most connected entities
  - Communities
  - Detected patterns
  - Disclaimer: "Analytical findings require human verification"

### Step 12: Audit Logs
- Shows all investigator actions:
  - LOGIN
  - CASE_CREATED
  - GRAPH_VIEWED
  - ANALYTICS_VIEWED
  - REPORT_GENERATED
  - etc.

---

## Key Design Principles Demonstrated

1. **Not Criminal Accusation**: System says "High network connectivity - requires investigator review" NOT "is criminal"
2. **Explainable**: Every result has WHAT, WHY, WHEN, WHO, evidence
3. **Evidence-Backed**: Relationships have source, timestamp, confidence, evidence_id
4. **Human Oversight**: Findings can be marked reviewed, false positive, saved
5. **Synthetic Data**: Clearly labeled DEMO / SYNTHETIC DATA everywhere
6. **Professional UI**: Clean enterprise intelligence system, not hacker graphics

---

## Architecture Highlights

- **Frontend**: React + TypeScript + Vite + Tailwind + Cytoscape.js + Recharts
- **Backend**: FastAPI + SQLAlchemy + Pydantic + JWT + NetworkX
- **Databases**: PostgreSQL (SQLite fallback) + Neo4j (NetworkX fallback)
- **AI/ML**: Regex + deterministic patterns + spaCy optional + NetworkX analytics + statistical anomaly detection
- **Security**: JWT, password hashing, RBAC, CORS, audit logging

---

## API Quick Test

```bash
# Health
curl http://localhost:8000/api/health

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"investigator","password":"invest123"}'

# Use token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"investigator","password":"invest123"}' | jq -r .access_token)

curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/dashboard

curl -H "Authorization: Bearer $TOKEN" "http://localhost:8000/api/graph?limit=100"

curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/analytics/centrality
```

---

## Future Enhancements (Not in Demo but Architected For)

- Real Neo4j with APOC + GDS for large scale
- HuggingFace Transformers for better NER
- Leaflet map for geospatial view
- Temporal graph analysis
- Advanced ML: Isolation Forest, GNNs
- Evidence chain of custody
- Multi-language support

---

**Classification**: DEMO / SYNTHETIC DATA - FOR TRAINING PURPOSES ONLY
**Disclaimer**: Analytical findings are decision-support outputs and require human verification.
