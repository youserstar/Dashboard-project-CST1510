import sqlite3
import bcrypt
from datetime import datetime, timedelta
import random

# Connect to database
conn = sqlite3.connect('intelligence.db')
cursor = conn.cursor()

print("="*60)
print("Creating Database with Problem Examples")
print("="*60)


print("\n[1/5] Creating tables...")

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS cyber_incidents (
    incident_id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    status TEXT NOT NULL,
    reported_date TEXT NOT NULL,
    resolved_date TEXT,
    description TEXT
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS datasets_metadata (
    dataset_id INTEGER PRIMARY KEY AUTOINCREMENT,
    dataset_name TEXT NOT NULL,
    source TEXT NOT NULL,
    size_mb REAL NOT NULL,
    row_count INTEGER NOT NULL,
    upload_date TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS it_tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    priority TEXT NOT NULL,
    status TEXT NOT NULL,
    assigned_to TEXT NOT NULL,
    created_date TEXT NOT NULL,
    resolved_date TEXT,
    description TEXT
)
''')

print("✅ Tables created!")

# ==================== CREATE USERS ====================

print("\n[2/5] Creating users...")

users = [
    ('admin', 'admin123', 'Admin'),
    ('cyber_analyst', 'cyber123', 'Cybersecurity'),
    ('data_scientist', 'data123', 'Data Science'),
    ('it_support', 'it123', 'IT Operations')
]

for username, password, role in users:
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    try:
        cursor.execute(
            'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
            (username, password_hash, role)
        )
        print(f"✅ Created user: {username}")
    except sqlite3.IntegrityError:
        print(f"  User {username} already exists")

# ==================== PROBLEM 1: PHISHING BOTTLENECK ====================

print("\n[3/5] Creating Cybersecurity data with PHISHING BOTTLENECK...")

# Clear existing data
cursor.execute('DELETE FROM cyber_incidents')

incident_types = ['Phishing', 'Malware', 'DDoS', 'Unauthorized Access', 'Data Breach']
severities = ['Low', 'Medium', 'High']
statuses = ['Open', 'In Progress', 'Resolved']

# Create 100 incidents with PHISHING taking 5x longer
for i in range(100):
    incident_type = random.choice(incident_types)
    severity = random.choice(severities)
    status = random.choice(statuses)
    
    reported_date = datetime.now() - timedelta(days=random.randint(1, 90))
    
    # KEY PROBLEM: Phishing takes much longer to resolve
    if incident_type == 'Phishing' and status == 'Resolved':
        # Phishing: 12-18 days (avg ~15 days)
        resolution_days = random.randint(12, 18)
        resolved_date = reported_date + timedelta(days=resolution_days)
    elif status == 'Resolved':
        # Other incidents: 2-5 days (avg ~3 days)
        resolution_days = random.randint(2, 5)
        resolved_date = reported_date + timedelta(days=resolution_days)
    else:
        resolved_date = None
    
    # Create more Phishing incidents (47% increase simulation)
    if random.random() < 0.4:  # 40% chance of Phishing
        incident_type = 'Phishing'
    
    # Create more high-severity unresolved Phishing (23 cases)
    if incident_type == 'Phishing' and random.random() < 0.25:
        severity = 'High'
        status = random.choice(['Open', 'In Progress'])
        resolved_date = None
    
    description = f"Sample {incident_type} incident - {severity} severity"
    
    cursor.execute('''
        INSERT INTO cyber_incidents 
        (incident_type, severity, status, reported_date, resolved_date, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (incident_type, severity, status,
          reported_date.strftime('%Y-%m-%d'),
          resolved_date.strftime('%Y-%m-%d') if resolved_date else None,
          description))

print("✅ Created 100 incidents with Phishing bottleneck (15 days avg vs 3 days)")

# ==================== PROBLEM 2: MARKETING STORAGE HOG ====================

print("\n[4/5] Creating Data Science data with MARKETING STORAGE PROBLEM...")

# Clear existing data
cursor.execute('DELETE FROM datasets_metadata')

sources = ['Marketing', 'IT', 'Finance', 'Operations']
dataset_count = {'Marketing': 9, 'IT': 4, 'Finance': 4, 'Operations': 3}

dataset_id = 1
for source, count in dataset_count.items():
    for i in range(count):
        dataset_name = f"{source}_Dataset_{i+1:03d}"
        
        # KEY PROBLEM: Marketing has huge datasets (61% of storage)
        if source == 'Marketing':
            # Marketing: 100-600 MB each (total ~1247 MB for 9 datasets)
            size_mb = random.uniform(100, 600)
            # Old datasets not accessed recently
            days_old = random.randint(89, 201)
        elif source == 'Finance':
            # Finance: 80-150 MB (total ~412 MB)
            size_mb = random.uniform(80, 150)
            days_old = random.randint(10, 60)
        elif source == 'IT':
            # IT: 60-120 MB (total ~342 MB)
            size_mb = random.uniform(60, 120)
            days_old = random.randint(5, 45)
        else:
            # Operations: small datasets
            size_mb = random.uniform(20, 50)
            days_old = random.randint(15, 90)
        
        row_count = int(size_mb * random.uniform(1000, 5000))
        upload_date = datetime.now() - timedelta(days=days_old)
        
        cursor.execute('''
            INSERT INTO datasets_metadata 
            (dataset_name, source, size_mb, row_count, upload_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (dataset_name, source, size_mb, row_count, upload_date.strftime('%Y-%m-%d')))
        
        dataset_id += 1

print("✅ Created 20 datasets with Marketing consuming 61% of storage")

# ==================== PROBLEM 3: BOB SMITH PERFORMANCE ISSUE ====================

print("\n[5/5] Creating IT Operations data with STAFF PERFORMANCE PROBLEM...")

# Clear existing data
cursor.execute('DELETE FROM it_tickets')

priorities = ['Low', 'Medium', 'High']
ticket_statuses = ['Open', 'In Progress', 'Waiting for User', 'Resolved']
staff_members = ['Alice Johnson', 'Bob Smith', 'Charlie Davis', 'Diana Martinez']

ticket_titles = [
    'Password reset needed', 'Cannot access email', 'Printer not working',
    'Software installation', 'Network issue', 'VPN problem',
    'Computer slow', 'Application crash', 'New user setup',
    'Hardware replacement'
]

# Create 100 tickets with specific problems
for i in range(100):
    title = random.choice(ticket_titles)
    priority = random.choice(priorities)
    status = random.choice(ticket_statuses)
    assigned_to = random.choice(staff_members)
    
    created_date = datetime.now() - timedelta(days=random.randint(1, 60))
    
    # KEY PROBLEM 1: Bob Smith is 3.3x slower than Alice
    if status == 'Resolved':
        if assigned_to == 'Bob Smith':
            # Bob: 10-15 days (avg ~12.4 days)
            resolution_days = random.randint(10, 15)
        elif assigned_to == 'Diana Martinez':
            # Diana: 7-11 days (avg ~9.1 days)
            resolution_days = random.randint(7, 11)
        elif assigned_to == 'Charlie Davis':
            # Charlie: 4-7 days (avg ~5.2 days)
            resolution_days = random.randint(4, 7)
        else:  # Alice Johnson
            # Alice: 3-5 days (avg ~3.8 days) - FASTEST
            resolution_days = random.randint(3, 5)
        
        resolved_date = created_date + timedelta(days=resolution_days)
    else:
        resolved_date = None
    
    # KEY PROBLEM 2: "Waiting for User" adds 8 extra days
    if status == 'Waiting for User' and random.random() < 0.3:
        # These tickets will have been open longer
        created_date = datetime.now() - timedelta(days=random.randint(8, 15))
    
    # Bob has highest workload (18 open tickets)
    if status in ['Open', 'In Progress'] and random.random() < 0.35:
        assigned_to = 'Bob Smith'
    
    # Alice has lowest workload (8 open tickets)
    if status in ['Open', 'In Progress'] and assigned_to == 'Alice Johnson' and random.random() < 0.6:
        assigned_to = random.choice(['Bob Smith', 'Charlie Davis', 'Diana Martinez'])
    
    description = f"User reported: {title}"
    
    cursor.execute('''
        INSERT INTO it_tickets 
        (title, priority, status, assigned_to, created_date, resolved_date, description)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (title, priority, status, assigned_to,
          created_date.strftime('%Y-%m-%d'),
          resolved_date.strftime('%Y-%m-%d') if resolved_date else None,
          description))

print("✅ Created 100 tickets with Bob Smith 3.3x slower + 'Waiting for User' bottleneck")

# ==================== COMMIT AND VERIFY ====================

conn.commit()

print("\n" + "="*60)
print("VERIFICATION - Checking Problems are Present")
print("="*60)

# Verify Problem 1: Phishing bottleneck
cursor.execute('''
    SELECT incident_type, 
           AVG(JULIANDAY(resolved_date) - JULIANDAY(reported_date)) as avg_days
    FROM cyber_incidents
    WHERE resolved_date IS NOT NULL
    GROUP BY incident_type
    ORDER BY avg_days DESC
''')
print("\n🔐 CYBERSECURITY - Resolution Times:")
for row in cursor.fetchall():
    print(f"  {row[0]:<20} {row[1]:.1f} days")

# Verify Problem 2: Marketing storage
cursor.execute('''
    SELECT source, 
           SUM(size_mb) as total_mb,
           COUNT(*) as count
    FROM datasets_metadata
    GROUP BY source
    ORDER BY total_mb DESC
''')
print("\n📊 DATA SCIENCE - Storage by Department:")
total_storage = cursor.execute('SELECT SUM(size_mb) FROM datasets_metadata').fetchone()[0]
for row in cursor.fetchall():
    percentage = (row[1] / total_storage) * 100
    print(f"  {row[0]:<15} {row[1]:>8.1f} MB ({percentage:.0f}%) - {row[2]} datasets")

# Verify Problem 3: Bob Smith performance
cursor.execute('''
    SELECT assigned_to,
           AVG(JULIANDAY(resolved_date) - JULIANDAY(created_date)) as avg_days,
           COUNT(*) as count
    FROM it_tickets
    WHERE resolved_date IS NOT NULL
    GROUP BY assigned_to
    ORDER BY avg_days DESC
''')
print("\n🛠️ IT OPERATIONS - Staff Performance:")
for row in cursor.fetchall():
    print(f"  {row[0]:<20} {row[1]:.1f} days avg ({row[2]} tickets)")

# Check workload distribution
cursor.execute('''
    SELECT assigned_to, COUNT(*) as open_tickets
    FROM it_tickets
    WHERE status IN ('Open', 'In Progress')
    GROUP BY assigned_to
    ORDER BY open_tickets DESC
''')
print("\n🛠️ IT OPERATIONS - Current Workload:")
for row in cursor.fetchall():
    print(f"  {row[0]:<20} {row[1]} open tickets")

conn.close()