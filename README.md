# CrimeNet Intelligence — AI-Powered Criminal Network Analysis System

**Problem Statement ID: 26189**

**DEMO / SYNTHETIC DATA - FOR TRAINING PURPOSES ONLY**

A professional investigator-assistance platform that analyzes structured and unstructured crime/intelligence records and helps investigators discover relationships between people, organizations, phone numbers, vehicles, locations, incidents, and financial entities.

> **Important**: This system is an ANALYTICAL ASSISTANCE TOOL. It does NOT automatically declare that a person is a criminal. Every result is accompanied by explainable evidence and requires human investigator review.

## 🎯 Project Purpose

```
Crime/Intelligence Data
        ↓
Data Ingestion
        ↓
Data Cleaning & Normalization
        ↓
NLP / Entity Extraction
        ↓
Entity Resolution
        ↓
Relationship Extraction
        ↓
Graph Database
        ↓
Graph Analytics
        ↓
Community Detection
        ↓
Anomaly / Pattern Detection
        ↓
Investigator Dashboard
```

The system identifies:
- Observed relationships (with evidence)
- Potentially significant connections
- Unusual patterns
- Network structures
- Entities requiring investigator review

## 🏗️ Architecture

```
React Frontend (Vite + TypeScript + Tailwind)
       |
       | REST API
       ↓
FastAPI Backend (Python)
       |
       ├────────────── PostgreSQL (structured data)
       |
       ├────────────── Neo4j (graph) + NetworkX fallback
       |
       └────────────── AI/ML Pipeline
                      ├── spaCy / regex NLP
                      ├── Entity Resolution
                      ├── NetworkX Analytics
                      └── Anomaly Detection
```

### Backend Layers
- API layer (`app/api/`)
- Service layer (`app/services/`)
- Data access layer (`app/models/`)
- AI/ML layer (`app/ai/`)
- Graph layer (`app/graph/`)
- Analytics layer (`app/analytics/`)
- Security layer (`app/security/`)

## 🛠️ Technology Stack

**Frontend:**
- React 18 + TypeScript
- Vite
- Tailwind CSS
- Cytoscape.js (graph visualization)
- Recharts (analytics)
- Lucide Icons

**Backend:**
- Python 3.11+
- FastAPI + Pydantic
- SQLAlchemy
- PostgreSQL (with SQLite fallback for demo)
- Neo4j (with NetworkX in-memory fallback)
- NetworkX, scikit-learn, python-jose

**AI/ML:**
- Regex + deterministic patterns
- spaCy (optional)
- NetworkX for graph algorithms
- Statistical anomaly detection

**Infrastructure:**
- Docker + Docker Compose
- JWT Authentication
- REST API

## 📦 Installation

### Option 1: Docker (Recommended for full stack)

```bash
# Clone and setup
git clone <repo>
cd crime-net

# Copy env
cp .env.example .env

# Start all services
docker-compose up --build

# Access:
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Neo4j Browser: http://localhost:7474 (neo4j/crimenet123)
```

### Option 2: Local Development

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Set env
export DATABASE_URL=sqlite:///./crimenet.db
export SECRET_KEY=demo-secret-key

# Run
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🔐 Demo Credentials

| Username | Password | Role |
|----------|----------|------|
| investigator | invest123 | INVESTIGATOR |
| admin | admin123 | ADMIN |
| analyst | analyst123 | ANALYST |

## 📊 Synthetic Data Generator

The system includes a deterministic synthetic data generator that creates:

- 500+ synthetic people (with communities)
- 300+ phone numbers
- 200+ vehicles
- 50+ organizations
- 100+ locations
- 1,000+ communications (with spikes for anomaly detection)
- 500+ transactions (with unusual amounts)
- 300+ incidents
- 100+ documents (FIR-style)
- 10 cases including **CASE-2026-001: Cross-Community Financial & Communication Analysis**

**Communities:**
- Community A: 30 people - Logistics Network
- Community B: 25 people - Trading Network
- Community C: 20 people - Transport Network
- Community D: 35 people - Market Network
- Community E: 15 people - Loose Network
- Plus bridge entities, high-degree nodes, cross-community links

Run manually:
```bash
python scripts/generate_data.py
```

## 🔍 Features

### 1. Authentication & Authorization
- JWT authentication
- Roles: ADMIN, INVESTIGATOR, ANALYST
- Protected routes

### 2. Case Management
- Create, view, update cases
- Case detail with network overview
- Workflow guidance

### 3. Data Ingestion
- Document upload
- Synthetic data auto-generation
- FIR-style document processing

### 4. NLP Pipeline
- **Regex extraction:** phones, vehicles (HR26XX0001), emails, dates, accounts
- **Pattern extraction:** person names (First Last), locations (with keywords like Market, Nagar)
- **spaCy fallback:** PERSON, ORG, GPE if model available
- **Relationship extraction:** proximity-based (person-person, person-location, etc.)

### 5. Entity Resolution
- Normalized name comparison
- Fuzzy matching (Jaccard + SequenceMatcher)
- Initials handling: "R. Sharma" vs "Rahul Sharma"
- Evidence: name similarity, shared phone/vehicle/location
- **Does NOT auto-merge** - shows "Possible duplicate" with approve/reject

### 6. Graph Database
- Neo4j with NetworkX fallback (works without Docker)
- Nodes: Person, Phone, Vehicle, Organization, Location, Incident, FinancialAccount, Document, Case
- Relationships: CALLED, OWNS, TRANSFERRED_TO, COMMUNICATED_WITH, FINANCIAL_LINK, etc.
- Metadata: source, timestamp, confidence, evidence_id

### 7. Graph Explorer
- Cytoscape.js interactive visualization
- Zoom, pan, node selection
- Filtering by type, relationship
- Shortest path between two entities
- Neighborhood expansion
- Layouts: Cose, Circle, Grid, Tree
- Click node/edge to see evidence

### 8. Network Analytics
- **Degree Centrality:** Most connected
- **Betweenness:** Bridge positions
- **Closeness:** Reachability
- **PageRank:** Influence
- **Density & Components**
- **Neutral language:** "High network connectivity" NOT "criminal"

### 9. Community Detection
- Greedy modularity (NetworkX)
- Cluster members, central nodes, type distribution
- Density, edge counts

### 10. Anomaly Detection (Explainable)
- **Communication spike:** avg 3/week → 27/week
- **Unusual transaction:** statistical threshold (mean + 2.5σ)
- **Location overlap:** repeated incidents at same location
- **Bridge entity:** high betweenness
- **High connectivity:** degree > mean + 2σ
- **Cross-community link:** bridge edges
- Every anomaly explains WHAT, WHY, WHEN, WHO, evidence

### 11. Timeline Analysis
- Chronological view of incidents, comms, transactions, docs
- Filtering by type, date, entity

### 12. Evidence Explorer
- Trace relationship → source records
- Shows communications, transactions, incidents supporting a link
- Confidence scores

### 13. Investigator Dashboard
- Top cards: Active Cases, Entities, Relationships, Incidents, Patterns, Communities
- Network overview, most connected, communities, recent events, pattern alerts
- Professional dark/light UI (no hacker graphics)

### 14. Reports
- Case report: executive summary, network stats, most connected, communities, patterns, disclaimer
- Neutral wording: "Entity A had 17 interactions with Entity B"
- Includes disclaimer: "Analytical findings require human verification"

### 15. Audit Logging
- Logs: login, case creation, document upload, graph exploration, report generation
- Stores user, action, timestamp, resource

## 🔌 API Endpoints

```
POST   /api/auth/login
GET    /api/auth/me
GET    /api/cases
POST   /api/cases
GET    /api/cases/{id}
GET    /api/entities/search?q=...
GET    /api/entities/person/{id}
GET    /api/entities/stats
GET    /api/graph?limit=300&node_type=Person
GET    /api/graph/path?source=person_1&target=person_2
GET    /api/graph/neighbors/{node_id}
POST   /api/graph/rebuild
GET    /api/analytics/centrality
GET    /api/analytics/communities
GET    /api/analytics/anomalies
GET    /api/analytics/overview
POST   /api/documents
POST   /api/documents/{id}/process
GET    /api/timeline
GET    /api/evidence/relationship/{source}/{target}
GET    /api/findings/anomalies
POST   /api/findings/{id}/review?action=save
GET    /api/reports/case/{case_id}
GET    /api/audit-logs
GET    /api/dashboard
GET    /api/health
```

## 🧪 Testing

```bash
cd backend
pytest tests/ -v
```

Includes tests for:
- Authentication
- Case creation
- Entity extraction
- Entity resolution
- Graph queries
- Centrality
- Community detection
- Anomaly detection
- API endpoints

## 📁 Project Structure

```
crime-net/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Layout.tsx
│   │   │   └── GraphViewer.tsx
│   │   ├── pages/
│   │   │   ├── Login.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Cases.tsx
│   │   │   ├── CaseDetail.tsx
│   │   │   ├── Entities.tsx
│   │   │   ├── GraphExplorer.tsx
│   │   │   ├── Analytics.tsx
│   │   │   ├── Timeline.tsx
│   │   │   ├── Evidence.tsx
│   │   │   ├── Documents.tsx
│   │   │   ├── Findings.tsx
│   │   │   ├── Reports.tsx
│   │   │   └── AuditLogs.tsx
│   │   ├── services/api.ts
│   │   ├── types/
│   │   └── utils/
│   └── package.json
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── ai/
│   │   │   ├── nlp_pipeline.py
│   │   │   └── entity_resolution.py
│   │   ├── graph/
│   │   │   ├── neo4j_client.py
│   │   │   └── graph_service.py
│   │   ├── analytics/
│   │   │   ├── centrality.py
│   │   │   └── anomaly.py
│   │   ├── security/
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt
├── scripts/
│   └── generate_data.py
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🎬 Demo Scenario: CASE-2026-001

1. **Login** as investigator / invest123
2. **Dashboard** shows 10 cases, 500+ entities, 1000+ relationships, 5 communities, pattern alerts
3. **Open CASE-2026-001**: Cross-Community Financial & Communication Analysis
4. **Graph Explorer**: See interconnected entities - persons, phones, vehicles, locations
5. **Select entity**: Graph expands showing neighborhood - phones, vehicles, locations, incidents
6. **Shortest path**: Select two persons → shows path via phone communication, financial link
7. **Analytics**: View centrality metrics - high connectivity = "Potentially significant network position"
8. **Communities**: 5 clusters detected, each with members, central nodes, shared locations
9. **Anomalies**: Click "Unusual communication increase" → explains baseline 4/week → 31/week, 675% increase, period, entities
10. **Evidence**: See source records - 14 calls, 3 document mentions, 5 location overlaps
11. **Save finding** to case
12. **Generate report**: Case summary with disclaimer

## 🔒 Privacy & Ethics

- **No real data**: All data is synthetic, fictional names, phone numbers, vehicles
- **Clear labeling**: "DEMO / SYNTHETIC DATA" everywhere
- **No auto-accusation**: System never says "is criminal", only "requires review"
- **Explainable**: Every result shows WHAT, WHY, evidence, confidence
- **Human oversight**: All findings need investigator verification
- **Audit trail**: All actions logged
- **Designed for replacement**: Authorized orgs can replace synthetic source with approved datasets

## ⚠️ Limitations

- Synthetic data only - not for production law enforcement without proper authorization
- Neo4j optional - falls back to NetworkX (limited scalability)
- spaCy model optional - regex fallback works but less accurate
- No real-time streaming (batch processing)
- No geospatial map (coordinates exist but no map UI - can be added with Leaflet)
- Simple anomaly detection (statistical, not deep learning)

## 🚀 Future Improvements

- Real Neo4j with APOC + GDS for large-scale graph
- HuggingFace Transformers for better NER
- Sentence-transformers for semantic entity resolution
- Leaflet/OpenStreetMap for geospatial view
- Temporal graph analysis
- Advanced ML: Isolation Forest, GNNs
- Role-based case access control
- Evidence chain of custody
- Multi-language support (Hindi, etc.)

## 📄 License

MIT License - For demonstration and educational purposes.

## 🤝 Contributing

This is a prototype for Problem Statement 26189. For production use, ensure:
- Proper authorization for data sources
- Privacy compliance (GDPR, etc.)
- Security audit
- Bias testing
- Human rights review

---

**Built with:** FastAPI, React, NetworkX, Tailwind CSS, Cytoscape.js

**Classification:** DEMO / SYNTHETIC DATA - FOR TRAINING PURPOSES ONLY

**Disclaimer:** Analytical findings are decision-support outputs and require human verification. This system is an investigator-assistance tool and does NOT automatically declare any person as criminal.
