#!/usr/bin/env python3
#config.py - it consists of configuration for each env variable
#run.py to get the config get the server and run it 

"""
HTTP Server for Nivi Systems
A modern HTTP server with REST API endpoints, error handling, and logging.
"""

import json
import logging
import os
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading
import time

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
            '/health': self.handle_health,
            '/api/status': self.handle_status,
            '/api/time': self.handle_time,
            '/api/echo': self.handle_echo,
            '/api/users': self.handle_users,
        }
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        self.handle_request('GET')
    
    def do_POST(self):
        """Handle POST requests."""
        self.handle_request('POST')
    
    def do_PUT(self):
        """Handle PUT requests."""
        self.handle_request('PUT')
    
    def do_DELETE(self):
        """Handle DELETE requests."""
        self.handle_request('DELETE')
    
    def handle_request(self, method):
        """Route requests to appropriate handlers."""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        logger.info(f"{method} {path} - {self.client_address[0]}")
        
        if path in self.routes:
            try:
                self.routes[path]()
            except Exception as e:
                logger.error(f"Error handling {path}: {str(e)}")
                self.send_error_response(500, f"Internal server error: {str(e)}")
        else:
            self.send_error_response(404, "Endpoint not found")
    
    def send_json_response(self, data, status_code=200):
        """Send JSON response."""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        
        response = json.dumps(data, indent=2)
        self.wfile.write(response.encode('utf-8'))
    
    def send_error_response(self, status_code, message):
        """Send error response."""
        error_data = {
            "error": True,
            "status_code": status_code,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(error_data, status_code)
    
    def get_request_body(self):
        """Get request body as JSON."""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            body = self.rfile.read(content_length)
            try:
                return json.loads(body.decode('utf-8'))
            except json.JSONDecodeError:
                return None
        return None
    
    def handle_root(self):
        """Handle root endpoint."""
        data = {
            "message": "Welcome to Nivi Systems HTTP Server",
            "version": "1.0.0",
            "endpoints": {
                "health": "/health",
                "status": "/api/status",
                "time": "/api/time",
                "echo": "/api/echo",
                "users": "/api/users"
            },
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(data)
    
    def handle_health(self):
        """Handle health check endpoint."""
        data = {
            "status": "healthy",
            "uptime": time.time() - self.server.start_time,
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(data)
    
    def handle_status(self):
        """Handle status endpoint."""
        data = {
            "server": "Nivi Systems HTTP Server",
            "status": "running",
            "version": "1.0.0",
            "threads": threading.active_count(),
            "timestamp": datetime.now().isoformat()
        }
        self.send_json_response(data)
    
    def handle_time(self):
        """Handle time endpoint."""
        data = {
            "current_time": datetime.now().isoformat(),
            "timestamp": int(time.time()),
            "timezone": "UTC"
        }
        self.send_json_response(data)
    
    def handle_echo(self):
        """Handle echo endpoint - returns request data."""
        if self.command == 'GET':
            # Get query parameters
            parsed_path = urlparse(self.path)
            query_params = parse_qs(parsed_path.query)
            data = {
                "method": self.command,
                "path": self.path,
                "query_params": query_params,
                "headers": dict(self.headers),
                "timestamp": datetime.now().isoformat()
            }
        else:
            # Get request body for POST/PUT
            body = self.get_request_body()
            data = {
                "method": self.command,
                "path": self.path,
                "body": body,
                "headers": dict(self.headers),
                "timestamp": datetime.now().isoformat()
            }
        
        self.send_json_response(data)
    
    def handle_users(self):
        """Handle users endpoint - simple CRUD operations."""
        if self.command == 'GET':
            # Return list of users (mock data)
            users = [
                {"id": 1, "name": "John Doe", "email": "john@example.com"},
                {"id": 2, "name": "Jane Smith", "email": "jane@example.com"},
                {"id": 3, "name": "Bob Johnson", "email": "bob@example.com"}
            ]
            self.send_json_response({"users": users, "count": len(users)})
        
        elif self.command == 'POST':
            # Create new user
            body = self.get_request_body()
            if not body:
                self.send_error_response(400, "Request body is required")
                return
            
            # Mock user creation
            new_user = {
                "id": 4,  # In real app, this would be generated
                "name": body.get("name", ""),
                "email": body.get("email", ""),
                "created_at": datetime.now().isoformat()
            }
            self.send_json_response({"user": new_user, "message": "User created successfully"}, 201)
        
        else:
            self.send_error_response(405, f"Method {self.command} not allowed for this endpoint")
    
    def log_message(self, format, *args):
        """Override to use our logger instead of stderr."""
        logger.info(f"{self.address_string()} - {format % args}")


class MyHTTPServer:
    """Custom HTTP server with additional features."""
    
    def __init__(self, host='localhost', port=8000):
        self.host = host
        self.port = port
        self.start_time = time.time()
        self.server = None
    
    def start(self):
        """Start the HTTP server."""
        try:
            self.server = HTTPServer((self.host, self.port), MyHTTPRequestHandler)
            self.server.start_time = self.start_time
            
            logger.info(f"Starting HTTP server on {self.host}:{self.port}")
            logger.info("Available endpoints:")
            logger.info("  GET  /           - Server information")
            logger.info("  GET  /health     - Health check")
            logger.info("  GET  /api/status - Server status")
            logger.info("  GET  /api/time   - Current time")
            logger.info("  GET  /api/echo   - Echo request data")
            logger.info("  GET  /api/users  - List users")
            logger.info("  POST /api/users  - Create user")
            logger.info("  POST /api/echo   - Echo request data")
            
            self.server.serve_forever()
            
        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
            self.stop()
        except Exception as e:
            logger.error(f"Server error: {str(e)}")
            self.stop()
    
    def stop(self):
        """Stop the HTTP server."""
        if self.server:
            logger.info("Stopping HTTP server...")
            self.server.shutdown()
            self.server.server_close()
            logger.info("Server stopped")


def main():
    """Main function to start the server."""
    # Get configuration from environment variables
    host = os.getenv('HOST', 'localhost')
    port = int(os.getenv('PORT', 8000))
    
    logger.info("Initializing Nivi Systems HTTP Server...")
    
    # Create and start server
    server = MyHTTPServer(host, port)
    
    try:
        server.start()
    except KeyboardInterrupt:
        logger.info("Received interrupt signal")
    finally:
        server.stop()


if __name__ == '__main__':
    main()
