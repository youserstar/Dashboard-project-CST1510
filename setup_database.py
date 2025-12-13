import sqlite3
import pandas as pd
from datetime import datetime

class DatabaseManager:
    """Manages all database operations for the Intelligence Platform"""
    
    def __init__(self, db_path="intelligence.db"):
        import os
        # Get the directory where this script is located
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # Build path to database file in the same directory
        self.db_path = os.path.join(current_dir, db_path)
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """Establish database connection"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    # ==================== USER AUTHENTICATION ====================
    
    def verify_user(self, username, password_hash):
        """Verify user credentials"""
        self.connect()
        query = "SELECT username, role FROM users WHERE username = ? AND password_hash = ?"
        result = self.cursor.execute(query, (username, password_hash)).fetchone()
        self.close()
        return result
    
    def get_user_role(self, username):
        """Get user role"""
        self.connect()
        query = "SELECT role FROM users WHERE username = ?"
        result = self.cursor.execute(query, (username,)).fetchone()
        self.close()
        return result[0] if result else None
    
    # ==================== CYBERSECURITY OPERATIONS ====================
    
    def get_all_incidents(self):
        """Retrieve all cybersecurity incidents"""
        self.connect()
        query = "SELECT * FROM cyber_incidents"
        df = pd.read_sql_query(query, self.conn)
        self.close()
        return df
    
    def get_incidents_by_severity(self, severity):
        """Get incidents filtered by severity"""
        self.connect()
        query = "SELECT * FROM cyber_incidents WHERE severity = ?"
        df = pd.read_sql_query(query, self.conn, params=(severity,))
        self.close()
        return df
    
    def get_unresolved_incidents(self):
        """Get all unresolved incidents"""
        self.connect()
        query = "SELECT * FROM cyber_incidents WHERE status != 'Resolved'"
        df = pd.read_sql_query(query, self.conn)
        self.close()
        return df
    
    def update_incident_status(self, incident_id, new_status):
        """Update incident status"""
        self.connect()
        query = "UPDATE cyber_incidents SET status = ? WHERE incident_id = ?"
        self.cursor.execute(query, (new_status, incident_id))
        self.conn.commit()
        self.close()
    
    def add_incident(self, incident_type, severity, status, description):
        """Add new incident"""
        self.connect()
        query = """INSERT INTO cyber_incidents 
                   (incident_type, severity, status, description, reported_date) 
                   VALUES (?, ?, ?, ?, ?)"""
        self.cursor.execute(query, (incident_type, severity, status, description, datetime.now()))
        self.conn.commit()
        self.close()
    
    # ==================== DATA SCIENCE OPERATIONS ====================
    
    def get_all_datasets(self):
        """Retrieve all datasets metadata"""
        self.connect()
        query = "SELECT * FROM datasets_metadata"
        df = pd.read_sql_query(query, self.conn)
        self.close()
        return df
    
    def get_datasets_by_source(self, source):
        """Get datasets filtered by source"""
        self.connect()
        query = "SELECT * FROM datasets_metadata WHERE source = ?"
        df = pd.read_sql_query(query, self.conn, params=(source,))
        self.close()
        return df
    
    def add_dataset(self, dataset_name, source, size_mb, row_count, upload_date):
        """Add new dataset"""
        self.connect()
        query = """INSERT INTO datasets_metadata 
                   (dataset_name, source, size_mb, row_count, upload_date) 
                   VALUES (?, ?, ?, ?, ?)"""
        self.cursor.execute(query, (dataset_name, source, size_mb, row_count, upload_date))
        self.conn.commit()
        self.close()
    
    def delete_dataset(self, dataset_id):
        """Delete dataset"""
        self.connect()
        query = "DELETE FROM datasets_metadata WHERE dataset_id = ?"
        self.cursor.execute(query, (dataset_id,))
        self.conn.commit()
        self.close()
    
    # ==================== IT OPERATIONS ====================
    
    def get_all_tickets(self):
        """Retrieve all IT tickets"""
        self.connect()
        query = "SELECT * FROM it_tickets"
        df = pd.read_sql_query(query, self.conn)
        self.close()
        return df
    
    def get_tickets_by_status(self, status):
        """Get tickets filtered by status"""
        self.connect()
        query = "SELECT * FROM it_tickets WHERE status = ?"
        df = pd.read_sql_query(query, self.conn, params=(status,))
        self.close()
        return df
    
    def get_tickets_by_assignee(self, assignee):
        """Get tickets filtered by assigned staff"""
        self.connect()
        query = "SELECT * FROM it_tickets WHERE assigned_to = ?"
        df = pd.read_sql_query(query, self.conn, params=(assignee,))
        self.close()
        return df
    
    def update_ticket_status(self, ticket_id, new_status):
        """Update ticket status"""
        self.connect()
        query = "UPDATE it_tickets SET status = ? WHERE ticket_id = ?"
        self.cursor.execute(query, (new_status, ticket_id))
        self.conn.commit()
        self.close()
    
    def add_ticket(self, title, priority, status, assigned_to, description):
        """Add new ticket"""
        self.connect()
        query = """INSERT INTO it_tickets 
                   (title, priority, status, assigned_to, description, created_date) 
                   VALUES (?, ?, ?, ?, ?, ?)"""
        self.cursor.execute(query, (title, priority, status, assigned_to, description, datetime.now()))
        self.conn.commit()
        self.close()