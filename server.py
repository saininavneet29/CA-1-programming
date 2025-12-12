import socket
import sqlite3
import json
import threading
import os

# Configuration
HOST = '127.0.0.1'
PORT = 5432
DATABASE_FILE = 'applications.db'

def setup_database():
    """Ensure the database and table exist."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            qualifications TEXT NOT NULL,
            course TEXT NOT NULL,
            start_year_month TEXT NOT NULL,
            application_id TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

def generate_app_id(app_id):
    """Generates a unique, formatted application ID based on the DB row ID."""
    # A simple way to create a unique ID for external reference
    return f"APP-{app_id:05d}"

def store_application(data):
    """Stores application data in the database and returns the generated ID."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    
    # Insert data into the table
    cursor.execute('''
        INSERT INTO applications (name, address, qualifications, course, start_year_month, application_id)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        data['name'],
        data['address'],
        data['qualifications'],
        data['course'],
        data['start_year_month'],
        'TEMP_ID' # Placeholder, will update after getting rowid
    ))
    
    row_id = cursor.lastrowid
    final_app_id = generate_app_id(row_id)
    
    cursor.execute('''
        UPDATE applications SET application_id = ? WHERE id = ?
    ''', (final_app_id, row_id))
    
    conn.commit()
    conn.close()
    return final_app_id

def handle_client(conn, addr):
    """Handle incoming client connection and data processing."""
    print(f"[+] New connection from {addr}")
    try:
        data = conn.recv(4096)
        if not data:
            print(f"[-] No data from {addr}")
            return
        
        app_data = json.loads(data.decode('utf-8'))
        print(f"[+] Received application data for: {app_data['name']}")

        app_id = store_application(app_data)
        
        response = {
            'status': 'success',
            'message': 'Application received successfully.',
            'application_id': app_id
        }
        
        conn.sendall(json.dumps(response).encode('utf-8'))
        print(f"[+] Sent confirmation ID {app_id} back to {addr}")

    except json.JSONDecodeError:
        print(f"[-] Failed to decode JSON from {addr}")
        error_resp = {'status': 'error', 'message': 'Invalid data format.'}
        conn.sendall(json.dumps(error_resp).encode('utf-8'))
    except Exception as e:
        print(f"[-] An error occurred: {e}")
        error_resp = {'status': 'error', 'message': 'Internal server error.'}
        conn.sendall(json.dumps(error_resp).encode('utf-8'))
    finally:
        conn.close()
        print(f"[-] Connection closed with {addr}")

def start_server():
    """Main function to start the TCP server."""
    setup_database()
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[*] Server listening on {HOST}:{PORT}")
        
        while True:
            conn, addr = s.accept()
            client_thread = threading.Thread(target=handle_client, args=(conn, addr))
            client_thread.start()

if __name__ == "__main__":
    start_server()
