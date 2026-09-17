"""
Synthetic Data Generator for CrimeNet Intelligence
DEMO / SYNTHETIC DATA - No real PII

Generates:
- 500+ persons
- 300+ phones
- 200+ vehicles
- 50+ organizations
- 100+ locations
- 1000+ communications
- 500+ transactions
- 300+ incidents
- 100+ documents
"""

import random
import string
from datetime import datetime, timedelta
from faker import Faker
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from sqlalchemy.orm import Session

# Try to import models
try:
    from app.models.all_models import *
    from app.models.person import Person
    from app.models.phone import Phone
    from app.models.vehicle import Vehicle
    from app.models.organization import Organization
    from app.models.location import Location
    from app.models.incident import Incident
    from app.models.financial import FinancialAccount, Transaction
    from app.models.communication import Communication
    from app.models.evidence import Document, Evidence
    from app.models.case import Case
    from app.models.finding import Finding
    from app.models.user import User
    from app.database import Base
except ImportError as e:
    print(f"Import error: {e}, trying alternative")
    try:
        from backend.app.models.all_models import *
        from backend.app.models.person import Person
        from backend.app.models.phone import Phone
        from backend.app.models.vehicle import Vehicle
        from backend.app.models.organization import Organization
        from backend.app.models.location import Location
        from backend.app.models.incident import Incident
        from backend.app.models.financial import FinancialAccount, Transaction
        from backend.app.models.communication import Communication
        from backend.app.models.evidence import Document, Evidence
        from backend.app.models.case import Case
        from backend.app.models.finding import Finding
        from backend.app.models.user import User
    except Exception as e2:
        print(f"Second import error: {e2}")
        pass

# Synthetic data constants - fictional only
FIRST_NAMES = [
    "Rahul", "Amit", "Vikram", "Suresh", "Rajesh", "Priya", "Anjali", "Sunita",
    "Arjun", "Karan", "Rohan", "Sneha", "Pooja", "Neha", "Vijay", "Ajay",
    "Ramesh", "Mahesh", "Deepak", "Sanjay", "Manoj", "Anil", "Sunil", "Ravi",
    "Aarav", "Vivaan", "Aditya", "Vihaan", "Arnav", "Sai", "Kabir", "Ayaan",
    "Krishna", "Ishaan", "Ananya", "Diya", "Saanvi", "Pari", "Myra", "Sara",
    "Riya", "Advik", "Reyansh", "Mohammed", "Samar", "Atharv", "Pranav", "Harsh",
    "Nikhil", "Abhishek", "Gaurav", "Varun", "Kunal", "Akash", "Siddharth", "Harshit",
    "Divya", "Kavita", "Shalini", "Meena", "Rekha", "Geeta", "Sarita", "Kiran",
    "Prakash", "Ashok", "Vinod", "Rakesh", "Dinesh", "Mukesh", "Rajiv", "Sanjay"
]

LAST_NAMES = [
    "Sharma", "Verma", "Singh", "Kumar", "Patel", "Gupta", "Jain", "Yadav",
    "Reddy", "Nair", "Mehta", "Shah", "Malhotra", "Kapoor", "Chopra", "Bansal",
    "Saxena", "Mishra", "Tiwari", "Pandey", "Dubey", "Chaudhary", "Rastogi", "Agarwal",
    "Goel", "Bhatia", "Khanna", "Arora", "Sethi", "Kohli", "Gill", "Sidhu",
    "Bedi", "Dhawan", "Grover", "Saini", "Chawla", "Luthra", "Sarin", "Bakshi",
    "Khatri", "Oberoi", "Sodhi", "Ahluwalia", "Sahni", "Chadha", "Anand", "Vohra"
]

OCCUPATIONS = [
    "Business Owner", "Trader", "Driver", "Shopkeeper", "Contractor", "Manager",
    "Sales Executive", "Technician", "Engineer", "Teacher", "Consultant", "Analyst",
    "Logistics Coordinator", "Warehouse Manager", "Import Export", "Real Estate",
    "Transport Operator", "Restaurant Owner", "Mobile Shop Owner", "Freelancer",
    "Student", "Unemployed", "Retired", "Self Employed", "Daily Wage"
]

VEHICLE_MAKES = ["Maruti", "Hyundai", "Tata", "Mahindra", "Honda", "Toyota", "Bajaj", "Hero"]
VEHICLE_MODELS = ["Swift", "Baleno", "Alto", "Creta", "Nexon", "Scorpio", "City", "Innova", "Splendor", "Pulsar"]
VEHICLE_TYPES = ["Sedan", "Hatchback", "SUV", "Motorcycle", "Truck", "Auto"]

LOCATION_NAMES = [
    "Central Market", "Nehru Nagar", "Gandhi Colony", "Shivaji Park", "MG Road", "Sector 18",
    "Lajpat Nagar", "Karol Bagh", "Connaught Place", "Dwarka Sector 5", "Rohini Sector 15",
    "Pitampura", "Janakpuri", "Uttam Nagar", "Rajouri Garden", "Paschim Vihar", "Model Town",
    "Azadpur Mandi", "Sadar Bazar", "Chandni Chowk", "Paharganj", "Karol Bagh Market",
    "Laxmi Nagar", "Preet Vihar", "Mayur Vihar", "Noida Sector 62", "Gurgaon Cyber City",
    "Sohna Road", "Manesar", "Faridabad Industrial Area", "Ballabgarh", "Okhla Phase 2",
    "Jasola", "Sarita Vihar", "Lajpat Nagar Market", "South Extension", "Greater Kailash",
    "Vasant Kunj", "Chattarpur", "Mehrauli", "Saket", "Malviya Nagar", "Hauz Khas",
    "Green Park", "AIIMS Area", "Nehru Place", "Kalkaji", "Govindpuri", "Tughlakabad"
]

ORG_NAMES = [
    "Sharma Enterprises", "Verma Trading Co", "Singh Logistics", "Kumar Industries",
    "Patel Exports", "Gupta & Sons", "Jain Corporation", "Yadav Transport",
    "Reddy Constructions", "Nair Solutions", "Mehta Industries", "Shah Traders",
    "Malhotra Group", "Kapoor Enterprises", "Chopra Logistics", "Bansal Industries",
    "Delhi Cargo Movers", "North India Traders", "Metro Suppliers", "City Distributors",
    "Global Imports", "Express Couriers", "Fast Track Logistics", "Prime Movers",
    "Royal Transport", "Golden Enterprises", "Silver Line Trading", "Blue Star Logistics"
]

ORG_TYPES = ["Private Limited", "Partnership", "Proprietorship", "LLP", "Trading", "Logistics", "Transport", "Retail"]

INCIDENT_TYPES = [
    "Theft", "Fraud", "Suspicious Activity", "Vehicle Sightings", "Financial Irregularity",
    "Unauthorized Gathering", "Property Dispute", "Missing Person Report", "Cyber Complaint",
    "Nuisance", "Trespassing", "Document Verification", "Routine Check", "Information Report"
]

def generate_phone_number():
    """Generate synthetic Indian phone number"""
    first_digit = random.choice(['6', '7', '8', '9'])
    remaining = ''.join(random.choices(string.digits, k=9))
    return f"{first_digit}{remaining}"

def generate_vehicle_number():
    """Generate synthetic Indian vehicle number"""
    state = random.choice(["DL", "HR", "UP", "MH", "KA", "TN", "GJ", "RJ", "PB"])
    district = random.randint(1, 99)
    series = ''.join(random.choices(string.ascii_uppercase, k=random.choice([1, 2])))
    number = random.randint(1000, 9999)
    return f"{state}{district:02d}{series}{number}"

def generate_account_number():
    """Generate masked account number"""
    masked = "XXXX" + ''.join(random.choices(string.digits, k=random.randint(4, 8)))
    return masked

def generate_all_data(db: Session, seed: int = 42):
    """Generate all synthetic data"""
    random.seed(seed)
    
    print(f"Generating synthetic data with seed {seed}...")
    
    # Clear existing data (except users)
    try:
        db.query(Finding).delete()
        db.query(Transaction).delete()
        db.query(Communication).delete()
        db.query(Evidence).delete()
        db.query(Document).delete()
        db.query(Incident).delete()
        db.query(FinancialAccount).delete()
        db.query(Vehicle).delete()
        db.query(Phone).delete()
        db.query(Organization).delete()
        db.query(Location).delete()
        db.query(Person).delete()
        db.query(Case).delete()
        db.commit()
    except Exception as e:
        print(f"Clear failed (may be first run): {e}")
        db.rollback()
    
    # Generate Locations (100)
    print("Generating locations...")
    locations = []
    for i in range(100):
        loc = Location(
            name=random.choice(LOCATION_NAMES) + f" {i+1}" if i >= len(LOCATION_NAMES) else random.choice(LOCATION_NAMES),
            address=f"{random.randint(1, 500)}, {random.choice(LOCATION_NAMES)}, New Delhi - {random.randint(110001, 110099)}",
            latitude=28.5 + random.uniform(-0.5, 0.5),
            longitude=77.0 + random.uniform(-0.5, 0.5),
            location_type=random.choice(["Market", "Residential", "Commercial", "Industrial", "Transport Hub", "Public Place"]),
            risk_level=random.choice(["LOW", "MEDIUM", "HIGH"])
        )
        db.add(loc)
        locations.append(loc)
    db.commit()
    for loc in locations:
        db.refresh(loc)
    
    # Generate Organizations (50)
    print("Generating organizations...")
    organizations = []
    for i in range(50):
        org = Organization(
            name=random.choice(ORG_NAMES) + f" {i+1}" if i < 20 else f"{random.choice(FIRST_NAMES)} {random.choice(ORG_TYPES)} {i}",
            type=random.choice(ORG_TYPES),
            industry=random.choice(["Logistics", "Trading", "Transport", "Retail", "Services", "Manufacturing"]),
            location=random.choice(locations).name if locations else "Delhi",
            description=f"Synthetic organization for demo purposes - {random.choice(ORG_TYPES)}"
        )
        db.add(org)
        organizations.append(org)
    db.commit()
    for org in organizations:
        db.refresh(org)
    
    # Generate Persons (500)
    print("Generating persons...")
    persons = []
    # Create communities
    communities = [
        {"size": 30, "name": "Community A - Logistics Network"},
        {"size": 25, "name": "Community B - Trading Network"},
        {"size": 20, "name": "Community C - Transport Network"},
        {"size": 35, "name": "Community D - Market Network"},
        {"size": 15, "name": "Community E - Loose Network"},
    ]
    
    person_idx = 0
    community_assignments = []
    
    for comm_idx, comm in enumerate(communities):
        for _ in range(comm["size"]):
            first = random.choice(FIRST_NAMES)
            last = random.choice(LAST_NAMES)
            name = f"{first} {last}"
            
            # Create some variations for entity resolution demo
            if random.random() < 0.05:
                # Create alias variations
                if random.random() < 0.5:
                    alias_name = f"{first[0]}. {last}"
                else:
                    alias_name = f"{first} {last[0]}."
            else:
                alias_name = None
            
            aliases = []
            if alias_name:
                aliases = [alias_name]
            
            person = Person(
                name=name,
                aliases=str(aliases),
                date_of_birth=f"{random.randint(1970, 2000)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                gender=random.choice(["Male", "Female", "Other"]),
                occupation=random.choice(OCCUPATIONS),
                risk_review_status=random.choice(["PENDING_REVIEW", "UNDER_REVIEW", "REVIEWED", "CLEARED"]),
                degree_centrality=0.0,
                community_id=comm_idx
            )
            db.add(person)
            persons.append(person)
            community_assignments.append(comm_idx)
            person_idx += 1
    
    # Remaining persons - random
    remaining = 500 - len(persons)
    for _ in range(remaining):
        first = random.choice(FIRST_NAMES)
        last = random.choice(LAST_NAMES)
        person = Person(
            name=f"{first} {last}",
            aliases="[]",
            date_of_birth=f"{random.randint(1970, 2000)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            gender=random.choice(["Male", "Female"]),
            occupation=random.choice(OCCUPATIONS),
            risk_review_status=random.choice(["PENDING_REVIEW", "REVIEWED"]),
            community_id=random.randint(0, 6)
        )
        db.add(person)
        persons.append(person)
    
    db.commit()
    for p in persons:
        db.refresh(p)
    
    print(f"Generated {len(persons)} persons")
    
    # Generate Phones (300)
    print("Generating phones...")
    phones = []
    for i in range(300):
        owner = random.choice(persons) if random.random() < 0.9 else None
        phone = Phone(
            phone_number=generate_phone_number(),
            owner_id=owner.id if owner else None,
            owner_name=owner.name if owner else None,
            carrier=random.choice(["Airtel", "Jio", "Vodafone", "BSNL"]),
            status="ACTIVE"
        )
        db.add(phone)
        phones.append(phone)
    db.commit()
    for ph in phones:
        db.refresh(ph)
    
    # Generate Vehicles (200)
    print("Generating vehicles...")
    vehicles = []
    for i in range(200):
        owner = random.choice(persons) if random.random() < 0.85 else None
        vehicle = Vehicle(
            registration_number=generate_vehicle_number(),
            vehicle_type=random.choice(VEHICLE_TYPES),
            make=random.choice(VEHICLE_MAKES),
            model=random.choice(VEHICLE_MODELS),
            color=random.choice(["White", "Black", "Silver", "Red", "Blue", "Grey"]),
            owner_id=owner.id if owner else None,
            owner_name=owner.name if owner else None
        )
        db.add(vehicle)
        vehicles.append(vehicle)
    db.commit()
    for v in vehicles:
        db.refresh(v)
    
    # Generate Financial Accounts (200)
    print("Generating financial accounts...")
    accounts = []
    for i in range(200):
        owner = random.choice(persons) if random.random() < 0.9 else None
        acc = FinancialAccount(
            masked_account_number=generate_account_number(),
            institution=random.choice(["State Bank", "HDFC Bank", "ICICI Bank", "Axis Bank", "Kotak Bank", "PNB"]),
            account_type=random.choice(["Savings", "Current", "Business"]),
            owner_id=owner.id if owner else None,
            owner_name=owner.name if owner else None,
            balance_range=random.choice(["<1L", "1L-5L", "5L-10L", "10L-50L", ">50L"])
        )
        db.add(acc)
        accounts.append(acc)
    db.commit()
    for acc in accounts:
        db.refresh(acc)
    
    # Generate Communications (1000+)
    print("Generating communications...")
    communications = []
    # Create community-based communications
    for _ in range(1000):
        # 70% within same community, 30% cross-community (bridge)
        if random.random() < 0.7 and len(persons) > 10:
            # Same community
            comm_persons = [p for p in persons if p.community_id == random.choice([0,1,2,3])]
            if len(comm_persons) < 2:
                comm_persons = random.sample(persons, 2)
            else:
                comm_persons = random.sample(comm_persons, min(2, len(comm_persons)))
        else:
            comm_persons = random.sample(persons, 2)
        
        # Find phones for these persons
        src_phones = [ph for ph in phones if ph.owner_id == comm_persons[0].id]
        dst_phones = [ph for ph in phones if ph.owner_id == comm_persons[1].id] if len(comm_persons) > 1 else []
        
        src_phone = random.choice(src_phones) if src_phones else random.choice(phones)
        dst_phone = random.choice(dst_phones) if dst_phones else random.choice(phones)
        
        if src_phone.id == dst_phone.id:
            continue
        
        # Create time with some spikes for anomaly detection
        base_time = datetime.now() - timedelta(days=random.randint(0, 90))
        # 10% chance of being in recent spike period
        if random.random() < 0.1:
            base_time = datetime.now() - timedelta(days=random.randint(0, 7))
        
        comm = Communication(
            source_phone=src_phone.phone_number,
            source_phone_id=src_phone.id,
            destination_phone=dst_phone.phone_number,
            destination_phone_id=dst_phone.id,
            timestamp=base_time - timedelta(hours=random.randint(0, 24), minutes=random.randint(0, 60)),
            duration_seconds=random.randint(10, 600),
            communication_type=random.choice(["CALL", "SMS", "WHATSAPP"]),
            location=random.choice(locations).name if locations else None
        )
        db.add(comm)
        communications.append(comm)
    
    # Add spike for anomaly: make 2 persons communicate a lot recently
    if len(phones) >= 2:
        spike_phone1 = phones[0]
        spike_phone2 = phones[1]
        for _ in range(30):
            comm = Communication(
                source_phone=spike_phone1.phone_number,
                source_phone_id=spike_phone1.id,
                destination_phone=spike_phone2.phone_number,
                destination_phone_id=spike_phone2.id,
                timestamp=datetime.now() - timedelta(days=random.randint(0, 3), hours=random.randint(0, 23)),
                duration_seconds=random.randint(30, 300),
                communication_type="CALL",
                location=random.choice(locations).name if locations else None
            )
            db.add(comm)
    
    db.commit()
    print(f"Generated {len(communications)} communications")
    
    # Generate Transactions (500+)
    print("Generating transactions...")
    transactions = []
    for i in range(500):
        sender = random.choice(accounts)
        receiver = random.choice(accounts)
        while receiver.id == sender.id:
            receiver = random.choice(accounts)
        
        # Amounts: mostly normal, some unusual for anomaly
        if random.random() < 0.05:
            amount = random.uniform(500000, 2000000)  # Unusual high
        else:
            amount = random.uniform(1000, 100000)
        
        txn = Transaction(
            transaction_id=f"TXN{random.randint(100000, 999999)}{i}",
            sender_account=sender.masked_account_number,
            sender_account_id=sender.id,
            receiver_account=receiver.masked_account_number,
            receiver_account_id=receiver.id,
            amount=round(amount, 2),
            timestamp=datetime.now() - timedelta(days=random.randint(0, 90), hours=random.randint(0, 23)),
            location=random.choice(locations).name if locations else None,
            transaction_type=random.choice(["NEFT", "IMPS", "UPI", "RTGS", "CASH_DEPOSIT"]),
            description=f"Synthetic transaction for demo - {random.choice(['Payment', 'Transfer', 'Settlement', 'Advance'])}",
            risk_flag="HIGH" if amount > 500000 else "NORMAL"
        )
        db.add(txn)
        transactions.append(txn)
    
    db.commit()
    print(f"Generated {len(transactions)} transactions")
    
    # Generate Incidents (300)
    print("Generating incidents...")
    incidents = []
    for i in range(300):
        loc = random.choice(locations) if locations else None
        incident = Incident(
            incident_number=f"FIR-{datetime.now().year}-{1000+i}",
            incident_type=random.choice(INCIDENT_TYPES),
            date=datetime.now() - timedelta(days=random.randint(0, 120), hours=random.randint(0, 23)),
            location=loc.name if loc else random.choice(LOCATION_NAMES),
            location_id=loc.id if loc else None,
            description=f"On {datetime.now().strftime('%d %B')}, {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)} was observed near {loc.name if loc else 'Central Market'} with {random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}. Vehicle {generate_vehicle_number()} was noted. The incident was reported as {random.choice(INCIDENT_TYPES).lower()}.",
            source=random.choice(["FIR", "Intelligence Report", "Patrol Report", "Public Tip", "Surveillance"]),
            severity=random.choice(["LOW", "MEDIUM", "HIGH"]),
            status=random.choice(["OPEN", "UNDER_INVESTIGATION", "CLOSED"])
        )
        db.add(incident)
        incidents.append(incident)
    db.commit()
    print(f"Generated {len(incidents)} incidents")
    
    # Generate Documents (100)
    print("Generating documents...")
    documents = []
    doc_templates = [
        "{person1} was seen near {location} with {person2}. Vehicle {vehicle} was observed near the location on {date}.",
        "FIR Report: On {date}, complainant reported that {person1} met {person2} at {location}. The vehicle {vehicle} was associated with both individuals.",
        "Intelligence Input: {person1}'s phone communicated with {person2}'s phone multiple times. Location {location} appears to be a common meeting point.",
        "Surveillance Report: At {location}, {person1} and {person2} were observed together. Transaction between their associated accounts noted.",
        "Communication intercept: Phone {phone1} contacted {phone2} {count} times in past week. Both numbers associated with {location} area.",
        "Financial Alert: Account {account1} transferred Rs. {amount} to {account2}. Both accounts linked to {person1} and {person2}.",
        "Vehicle sighting: {vehicle} registered to {person1} was seen at {location} on {date}. {person2} was also present.",
        "Location analysis: {location} shows repeated presence of {person1}, {person2}, and {person3} during overlapping time periods.",
    ]
    
    for i in range(100):
        p1 = random.choice(persons)
        p2 = random.choice(persons)
        while p2.id == p1.id:
            p2 = random.choice(persons)
        p3 = random.choice(persons)
        loc = random.choice(locations)
        veh = random.choice(vehicles)
        ph1 = random.choice(phones)
        ph2 = random.choice(phones)
        acc1 = random.choice(accounts)
        acc2 = random.choice(accounts)
        
        template = random.choice(doc_templates)
        text = template.format(
            person1=p1.name,
            person2=p2.name,
            person3=p3.name,
            location=loc.name,
            vehicle=veh.registration_number,
            date=(datetime.now() - timedelta(days=random.randint(0, 60))).strftime("%d %B %Y"),
            phone1=ph1.phone_number,
            phone2=ph2.phone_number,
            count=random.randint(5, 20),
            account1=acc1.masked_account_number,
            account2=acc2.masked_account_number,
            amount=f"{random.randint(10000, 500000):,}"
        )
        
        doc = Document(
            title=f"Document {i+1} - {random.choice(['FIR', 'Intelligence', 'Surveillance', 'Financial', 'Communication'])} Report",
            text=text,
            document_type=random.choice(["FIR", "Intelligence Report", "Surveillance", "Financial Report", "Communication Log"]),
            source=random.choice(["Police Station", "Intelligence Unit", "Field Report", "Digital Evidence"]),
            uploaded_by="system",
            processing_status="PENDING"
        )
        db.add(doc)
        documents.append(doc)
    
    db.commit()
    print(f"Generated {len(documents)} documents")
    
    # Generate Cases (10)
    print("Generating cases...")
    cases = []
    case_titles = [
        "Cross-Community Financial & Communication Analysis",
        "Market Area Surveillance - Central Network",
        "Vehicle Movement Pattern Investigation",
        "Communication Spike Analysis - Logistics Cluster",
        "Financial Transaction Chain Review",
        "Multi-Location Overlap Investigation",
        "Bridge Entity Identification - Community Link",
        "High Connectivity Node Review",
        "Unusual Transaction Pattern - Trading Network",
        "Comprehensive Network Analysis - Sector 18"
    ]
    
    for i, title in enumerate(case_titles):
        case = Case(
            case_number=f"CASE-{datetime.now().year}-{i+1:03d}",
            title=title,
            description=f"Demo case for investigation: {title}. This case includes synthetic data analysis of interconnected entities, communications, and financial transactions. Classification: DEMO / SYNTHETIC DATA.",
            status=random.choice(["OPEN", "IN_PROGRESS", "UNDER_REVIEW"]),
            priority=random.choice(["LOW", "MEDIUM", "HIGH"]),
            investigator_id=1,
            investigator_name="Senior Investigator",
            associated_entities=str({"persons": [p.id for p in random.sample(persons, 5)], "locations": [loc.id for loc in random.sample(locations, 3)]})
        )
        db.add(case)
        cases.append(case)
    
    db.commit()
    print(f"Generated {len(cases)} cases")
    
    print("Synthetic data generation complete!")
    print(f"Summary: {len(persons)} persons, {len(phones)} phones, {len(vehicles)} vehicles, {len(locations)} locations, {len(organizations)} orgs, {len(transactions)} txns, {len(communications)} comms, {len(incidents)} incidents, {len(documents)} docs, {len(cases)} cases")
    
    return {
        "persons": len(persons),
        "phones": len(phones),
        "vehicles": len(vehicles),
        "locations": len(locations),
        "organizations": len(organizations),
        "transactions": len(transactions),
        "communications": len(communications),
        "incidents": len(incidents),
        "documents": len(documents),
        "cases": len(cases)
    }

if __name__ == "__main__":
    # Direct run
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
    from app.database import SessionLocal
    db = SessionLocal()
    try:
        generate_all_data(db)
    finally:
        db.close()
