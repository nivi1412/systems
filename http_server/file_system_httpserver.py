import json
import logging
import os
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import time
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('server.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP request handler with REST API endpoints."""

    def __init__(self, *args, **kwargs):
        self.routes = {
            '/': self.handle_root,
            '/users': self.handle_GET,
        }
        super().__init__(*args, **kwargs)

    # HTTP method handlers
    def do_GET(self):
        self.handle_request('GET')

    def do_POST(self):
        self.handle_request('POST')

    def do_PATCH(self):
        self.handle_request('PATCH')

    def do_DELETE(self):
        self.handle_request('DELETE')

    # -------------------------------------------------------------------------
    # ROUTING LOGIC
    # -------------------------------------------------------------------------
    def handle_request(self, method):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        logger.info(f"{method} {path} - {self.client_address[0]}")

        try:
            # User-related endpoints
            if path == '/user' and method == 'POST':
                self.handle_POST_user()
            elif path.startswith('/user/') and method == 'PATCH':
                self.handle_PATCH_user()
            elif path.startswith('/user/') and method == 'DELETE':
                self.handle_DELETE_user()
            elif path in self.routes:
                self.routes[path]()
            else:
                self.send_error_response(404, "Endpoint not found")
        except Exception as e:
            logger.error(f"Error handling {path}: {str(e)}")
            self.send_error_response(500, f"Internal server error: {str(e)}")

    # -------------------------------------------------------------------------
    # ROOT ENDPOINT
    # -------------------------------------------------------------------------
    def handle_root(self):
        data = {
            "message": "Welcome to Nivi Systems HTTP Server",
            "version": "1.1.0",
            "endpoints": {
                "GET": "/users",
                "POST": "/user",
                "PATCH": "/user/<uuid>",
                "DELETE": "/user/<uuid>",
            },
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(data)

    # -------------------------------------------------------------------------
    # GET /users
    # -------------------------------------------------------------------------
    def handle_GET(self):
        parsed_path = urlparse(self.path)
        query_params = parse_qs(parsed_path.query)

        if os.path.exists("users.json"):
            with open("users.json", "r") as f:
                users = json.load(f)
        else:
            users = []

        # Extract filters
        name = query_params.get("name", [None])[0]
        place = query_params.get("place", [None])[0]
        occupation = query_params.get("occupation", [None])[0]

        # Apply filters
        filtered_users = users
        if name:
            filtered_users = [u for u in filtered_users if u["name"].lower() == name.lower()]
        if place:
            filtered_users = [u for u in filtered_users if u["place"].lower() == place.lower()]
        if occupation:
            filtered_users = [u for u in filtered_users if u["occupation"].lower() == occupation.lower()]

        if not filtered_users:
            self.send_error_response(404, "No matching users found")
            return

        self.send_json_response({"users": filtered_users, "count": len(filtered_users)})

    # -------------------------------------------------------------------------
    # POST /user
    # -------------------------------------------------------------------------
    def handle_POST_user(self):
        body = self.get_request_body()
        if not body:
            self.send_error_response(400, "Request body is required")
            return

        required_fields = ["name", "age", "occupation", "place"]
        for field in required_fields:
            if field not in body:
                self.send_error_response(400, f"Missing field: {field}")
                return

        new_user = {
            "id": str(uuid.uuid4()),
            "name": body["name"],
            "age": body["age"],
            "occupation": body["occupation"],
            "place": body["place"],
            "created_at": datetime.now().isoformat()
        }

        self.server.users.append(new_user)
        with open("users.json", "w") as f:
            json.dump(self.server.users, f, indent=2)

        self.send_json_response({
            "message": "User created successfully",
            "uuid": new_user["id"]
        }, status_code=201)

    # -------------------------------------------------------------------------
    # PATCH /user/<uuid>
    # -------------------------------------------------------------------------
    def handle_PATCH_user(self):
        parsed_path = urlparse(self.path)
        parts = parsed_path.path.split('/')
        if len(parts) < 3 or not parts[2]:
            self.send_error_response(400, "User ID (UUID) is required in path, e.g. /user/<uuid>")
            return

        user_id = parts[2]
        body = self.get_request_body()
        if not body:
            self.send_error_response(400, "Request body is required")
            return

        allowed_updates = ["occupation", "place"]
        for user in self.server.users:
            if user["id"] == user_id:
                for key in allowed_updates:
                    if key in body:
                        user[key] = body[key]
                user["updated_at"] = datetime.now().isoformat()
                with open("users.json", "w") as f:
                    json.dump(self.server.users, f, indent=2)
                self.send_json_response({
                    "message": f"User {user_id} updated successfully",
                    "updated_fields": {k: v for k, v in body.items() if k in allowed_updates}
                })
                return

        self.send_error_response(404, f"User with ID {user_id} not found")

    # -------------------------------------------------------------------------
    # DELETE /user/<uuid>
    # -------------------------------------------------------------------------
    def handle_DELETE_user(self):
        parsed_path = urlparse(self.path)
        parts = parsed_path.path.split('/')
        if len(parts) < 3 or not parts[2]:
            self.send_error_response(400, "User ID (UUID) is required in path, e.g. /user/<uuid>")
            return

        user_id = parts[2]
        for user in self.server.users:
            if user["id"] == user_id:
                self.server.users.remove(user)
                with open("users.json", "w") as f:
                    json.dump(self.server.users, f, indent=2)
                self.send_json_response({"message": f"User {user_id} deleted successfully"})
                return

        self.send_error_response(404, f"User with ID {user_id} not found")

    # -------------------------------------------------------------------------
    # UTILITIES
    # -------------------------------------------------------------------------
    def send_json_response(self, data, status_code=200):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))

    def send_error_response(self, status_code, message):
        error_data = {
            "error": True,
            "status_code": status_code,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(error_data, status_code)

    def get_request_body(self):
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            try:
                return json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                return None
        return None


# -----------------------------------------------------------------------------
# SERVER CLASS
# -----------------------------------------------------------------------------
class MyHTTPServer:
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.start_time = time.time()
        self.server = None

    def start(self):
        try:
            if os.path.exists("users.json"):
                with open("users.json", "r") as f:
                    users = json.load(f)
            else:
                users = []

            self.server = HTTPServer((self.host, self.port), MyHTTPRequestHandler)
            self.server.start_time = self.start_time
            self.server.users = users

            logger.info(f"Starting HTTP server on {self.host}:{self.port}")
            logger.info("Available endpoints:")
            logger.info("  GET    /           - Server info")
            logger.info("  GET    /users      - List users (filters: name, place, occupation)")
            logger.info("  POST   /user       - Create user")
            logger.info("  PATCH  /user/<uuid> - Update user")
            logger.info("  DELETE /user/<uuid> - Delete user")

            self.server.serve_forever()

        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
            self.stop()
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            self.stop()

    def stop(self):
        if self.server:
            logger.info("Stopping HTTP server...")
            self.server.shutdown()
            self.server.server_close()
            logger.info("Server stopped")


# -----------------------------------------------------------------------------
# MAIN
# -----------------------------------------------------------------------------
def main():
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', 8000))
    logger.info("Initializing Nivi Systems HTTP Server...")
    server = MyHTTPServer(host, port)
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        server.stop()


if __name__ == '__main__':
    main()
