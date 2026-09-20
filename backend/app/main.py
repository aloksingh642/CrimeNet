from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .config import settings, get_cors_origins
from .database import init_db, get_db, SessionLocal
from .models.user import User
from .security.auth import get_password_hash, authenticate_user, create_access_token
from .api import auth, cases, entities, graph, analytics, documents, timeline, evidence, findings, audit, reports
from datetime import timedelta
import os

app = FastAPI(
    title="CrimeNet Intelligence - AI-Powered Criminal Network Analysis",
    description="DEMO / SYNTHETIC DATA - Investigator assistance platform for network analysis",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(cases.router)
app.include_router(entities.router)
app.include_router(graph.router)
app.include_router(analytics.router)
app.include_router(documents.router)
app.include_router(timeline.router)
app.include_router(evidence.router)
app.include_router(findings.router)
app.include_router(audit.router)
app.include_router(reports.router)


@app.on_event("startup")
def startup_event():
    init_db()

    # Create default users if not exist
    db = SessionLocal()

    try:
        import app.models.all_models  # ensure all models registered

        # Check if users exist
        existing = db.query(User).count()

        if existing == 0:
            print("Creating demo users...")

            demo_users = [
                {
                    "username": "admin",
                    "password": "admin123",
                    "email": "admin@crimenet.demo",
                    "full_name": "System Administrator",
                    "role": "ADMIN",
                },
                {
                    "username": "investigator",
                    "password": "invest123",
                    "email": "investigator@crimenet.demo",
                    "full_name": "Senior Investigator",
                    "role": "INVESTIGATOR",
                },
                {
                    "username": "analyst",
                    "password": "analyst123",
                    "email": "analyst@crimenet.demo",
                    "full_name": "Intelligence Analyst",
                    "role": "ANALYST",
                },
            ]

            for u in demo_users:
                hashed = get_password_hash(u["password"])

                user = User(
                    username=u["username"],
                    email=u["email"],
                    hashed_password=hashed,
                    full_name=u["full_name"],
                    role=u["role"],
                )

                db.add(user)

            db.commit()
            print("Demo users created")

        # Check if synthetic data exists, if not, generate
        from .models.person import Person

        person_count = db.query(Person).count()

        if person_count == 0:
            print("No synthetic data found, generating...")

            try:
                from scripts.generate_data import generate_all_data

                generate_all_data(db)

                print("Synthetic data generated")

            except Exception as e:
                print(f"Failed to generate synthetic data: {e}")

                import traceback
                traceback.print_exc()

        # Build graph
        try:
            from .graph.graph_service import graph_service

            print("Building graph...")

            graph_service.build_full_graph(db)

            print("Graph built")

        except Exception as e:
            print(f"Graph build failed: {e}")

    finally:
        db.close()


@app.get("/")
def root():
    return {
        "message": "CrimeNet Intelligence API",
        "version": "1.0.0",
        "environment": "DEMO / SYNTHETIC DATA",
        "disclaimer": "This system uses synthetic data for demonstration. It is an investigator-assistance tool, not an automated criminal determination system.",
        "docs": "/docs",
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT,
        "synthetic_data": True,
        "message": "DEMO / SYNTHETIC DATA",
    }


@app.post("/api/auth/token")
def login_for_swagger(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = authenticate_user(
        db,
        form_data.username,
        form_data.password,
    )

    if not user:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=401,
            detail="Invalid credentials",
        )

    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": (
                user.role.value
                if hasattr(user.role, "value")
                else str(user.role)
            ),
        },
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@app.get("/api/dashboard")
def dashboard(db: Session = Depends(get_db)):
    from .models.person import Person
    from .models.case import Case
    from .models.incident import Incident
    from .models.communication import Communication
    from .models.financial import Transaction
    from .graph.graph_service import graph_service
    from .analytics.centrality import analytics_service
    from .analytics.anomaly import anomaly_detector

    try:
        # Get graph data
        graph_data = graph_service.get_graph_data(limit=500)

        # Calculate network metrics
        centrality = analytics_service.calculate_centrality(graph_data)

        # Community detection returns:
        # {
        #     node_id: community_id
        # }
        communities = analytics_service.detect_communities(graph_data)

        # Detect anomalies
        anomalies = anomaly_detector.detect_all(
            db,
            graph_data,
        )

        # Convert community mapping into dashboard-friendly groups.
        community_groups = {}

        if isinstance(communities, dict):
            for node_id, community_id in communities.items():
                community_key = str(community_id)

                if community_key not in community_groups:
                    community_groups[community_key] = []

                community_groups[community_key].append(node_id)

        community_list = []

        for community_id, members in community_groups.items():
            community_list.append(
                {
                    "community_id": community_id,
                    "members": members,
                    "size": len(members),
                }
            )

        stats = {
            "active_cases": db.query(Case).count(),
            "entities": len(graph_data.get("nodes", [])),
            "relationships": len(graph_data.get("edges", [])),
            "incidents": db.query(Incident).count(),
            "communications": db.query(Communication).count(),
            "transactions": db.query(Transaction).count(),
            "communities": len(community_list),
            "anomalies": len(anomalies),
            "persons": db.query(Person).count(),
        }

        community_list = []

        if isinstance(communities, dict):
            community_groups = {}

            for node_id, community_id in communities.items():
                key = str(community_id)

                if key not in community_groups:
                    community_groups[key] = []

                community_groups[key].append(node_id)

            for community_id, members in community_groups.items():
                community_list.append({
                    "community_id": community_id,
                    "members": members,
                    "size": len(members)
                })

        return {
            "stats": stats,
            "centrality": centrality,
            "communities": community_list[:5],
            "anomalies": anomalies[:5],
            "classification": "DEMO / SYNTHETIC DATA"
        }

    except Exception as e:
        import traceback

        traceback.print_exc()

        return {
            "error": str(e),
            "stats": {},
        }