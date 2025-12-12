import socket
import json
import sys

# Configuration
HOST = '127.0.0.1'
PORT = 5432

def get_user_input():
    """Prompt the user for application details."""
    print("\n--- College Admission Application ---")
    data = {}
    data['name'] = input("Full Name: ")
    data['address'] = input("Address: ")
    data['qualifications'] = input("Educational Qualifications (e.g., BSc Computer Science): ")
    
    # Validate course choice
    available_courses = ["MSc in Cyber Security", "MSc Information Systems & computing", "MSc Data Analytics"]
    print(f"Available Courses: {', '.join(available_courses)}")
    while True:
        course = input("Which course do you wish to enroll in?: ")
        if course in available_courses:
            data['course'] = course
            break
        else:
            print("Invalid course name. Please select from the list.")

    data['start_year_month'] = input("Intended start year and month (e.g., 2026 Sep): ")
    
    return data

def send_application(app_data):
    """Connect to the server and send the application data."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((HOST, PORT))
            print(f"[*] Connected to server at {HOST}:{PORT}")
            
            # Serialize data to JSON and encode to bytes
            data_payload = json.dumps(app_data).encode('utf-8')
            s.sendall(data_payload)
            print("[*] Application data sent. Waiting for server response...")
            
            # Receive response
            response_data = s.recv(1024)
            if response_data:
                response = json.loads(response_data.decode('utf-8'))
                return response
            else:
                return {'status': 'error', 'message': 'No response received.'}

        except ConnectionRefusedError:
            return {'status': 'error', 'message': 'Connection refused. Is the server running?'}
        except Exception as e:
            return {'status': 'error', 'message': f'A network error occurred: {e}'}

def main():
    app_data = get_user_input()
    response = send_application(app_data)

    print("\n--- Server Response ---")
    if response['status'] == 'success':
        print(f"SUCCESS: {response['message']}")
        print(f"Your unique application number is: {response['application_id']}")
        print("Please use this number for all future correspondence.")
    else:
        print(f"ERROR: {response['message']}")
    print("-------------------------")

if __name__ == "__main__":
    main()
