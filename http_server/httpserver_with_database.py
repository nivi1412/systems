# httpserver_with_database.py

import json
import logging
import os
import sys
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import time
from sqlalchemy import create_engine, Column, String, Integer, DateTime
import redis
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError

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

# Database setup
Base = declarative_base()

class User(Base):
    __tablename__ = 'people'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    occupation = Column(String, nullable=False)
    place = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Database connection
DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/mydb"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class MyHTTPRequestHandler(BaseHTTPRequestHandler):
    """Custom HTTP request handler with REST API endpoints."""

    def __init__(self, *args, **kwargs):
        self.routes = {
            '/': self.handle_root,
            '/users': self.handle_GET,
        }
        # Redis client (env-configurable, defaults for Docker local)
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = int(os.getenv('REDIS_PORT', '6379'))
        redis_db = int(os.getenv('REDIS_DB', '0'))
        self.redis_ttl_seconds = int(os.getenv('REDIS_TTL_SECONDS', '300'))
        self.redis_enabled = os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
        self.redis = None
        if self.redis_enabled:
            try:
                self.redis = redis.Redis(host=redis_host, port=redis_port, db=redis_db, decode_responses=True)
                # Quick ping to validate connection
                self.redis.ping()
                logger.info(f"Connected to Redis at {redis_host}:{redis_port}/{redis_db}")
            except Exception as e:
                logger.warning(f"Redis unavailable: {e}. Proceeding without cache.")
                self.redis = None
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
                "PATCH": "/user/<id>",
                "DELETE": "/user/<id>",
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

        try:
            db = SessionLocal()
            
            # Attempt cache hit first
            cache_key = None
            if self.redis:
                # Key based on endpoint and sorted query params for stability
                qp_items = sorted((k, (query_params.get(k, [None])[0] or '')) for k in ["name","place","occupation"]) 
                cache_key = "users:" + ";".join([f"{k}={v}" for k,v in qp_items])
                cached = self.redis.get(cache_key)
                if cached:
                    self.send_json_response(json.loads(cached))
                    return

            # Extract filters
            name = query_params.get("name", [None])[0]
            place = query_params.get("place", [None])[0]
            occupation = query_params.get("occupation", [None])[0]

            # Build query
            query = db.query(User)
            
            if name:
                query = query.filter(User.name.ilike(f"%{name}%"))
            if place:
                query = query.filter(User.place.ilike(f"%{place}%"))
            if occupation:
                query = query.filter(User.occupation.ilike(f"%{occupation}%"))

            users = query.all()
            
            if not users:
                self.send_error_response(404, "No matching users found")
                return

            # Convert to dict format
            users_data = []
            for user in users:
                users_data.append({
                    "id": user.id,
                    "name": user.name,
                    "age": user.age,
                    "occupation": user.occupation,
                    "place": user.place,
                    "created_at": user.created_at.isoformat(),
                    "updated_at": user.updated_at.isoformat() if user.updated_at else None
                })

            response_payload = {"users": users_data, "count": len(users_data)}

            # Write to cache
            if self.redis and cache_key:
                try:
                    self.redis.setex(cache_key, self.redis_ttl_seconds, json.dumps(response_payload))
                except Exception as e:
                    logger.warning(f"Failed to write GET cache: {e}")

            self.send_json_response(response_payload)
            
        except SQLAlchemyError as e:
            logger.error(f"Database error in GET /users: {str(e)}")
            self.send_error_response(500, "Database error occurred")
        finally:
            db.close()

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

        try:
            db = SessionLocal()
            
            new_user = User(
                name=body["name"],
                age=body["age"],
                occupation=body["occupation"],
                place=body["place"]
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            
            created_payload = {
                "message": "User created successfully",
                "id": new_user.id
            }

            # Write-through to Redis: cache single entity and invalidate list keys
            if self.redis:
                try:
                    self.redis.setex(f"user:{new_user.id}", self.redis_ttl_seconds, json.dumps({
                        "id": new_user.id,
                        "name": new_user.name,
                        "age": new_user.age,
                        "occupation": new_user.occupation,
                        "place": new_user.place,
                        "created_at": new_user.created_at.isoformat() if new_user.created_at else None,
                        "updated_at": new_user.updated_at.isoformat() if new_user.updated_at else None,
                    }))
                    # Invalidate users list caches
                    self._invalidate_users_list_cache()
                except Exception as e:
                    logger.warning(f"Failed to write-through POST to Redis: {e}")

            self.send_json_response(created_payload, status_code=201)
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error in POST /user: {str(e)}")
            self.send_error_response(500, "Database error occurred")
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # PATCH /user/<id>
    # -------------------------------------------------------------------------
    def handle_PATCH_user(self):
        parsed_path = urlparse(self.path)
        parts = parsed_path.path.split('/')
        if len(parts) < 3 or not parts[2]:
            self.send_error_response(400, "User ID (id) is required in path, e.g. /user/<id>")
            return

        user_id = parts[2]
        body = self.get_request_body()
        if not body:
            self.send_error_response(400, "Request body is required")
            return

        try:
            db = SessionLocal()
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                self.send_error_response(404, f"User with ID {user_id} not found")
                return

            allowed_updates = ["occupation", "place"]
            updated_fields = {}
            
            for key in allowed_updates:
                if key in body:
                    setattr(user, key, body[key])
                    updated_fields[key] = body[key]
            
            user.updated_at = datetime.utcnow()
            db.commit()
            
            response_payload = {
                "message": f"User {user_id} updated successfully",
                "updated_fields": updated_fields
            }

            # Update Redis cache for this user and invalidate list caches
            if self.redis:
                try:
                    self.redis.setex(f"user:{user_id}", self.redis_ttl_seconds, json.dumps({
                        "id": user.id,
                        "name": user.name,
                        "age": user.age,
                        "occupation": user.occupation,
                        "place": user.place,
                        "created_at": user.created_at.isoformat() if user.created_at else None,
                        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
                    }))
                    self._invalidate_users_list_cache()
                except Exception as e:
                    logger.warning(f"Failed to update Redis on PATCH: {e}")

            self.send_json_response(response_payload)
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error in PATCH /user: {str(e)}")
            self.send_error_response(500, "Database error occurred")
        finally:
            db.close()

    # -------------------------------------------------------------------------
    # DELETE /user/<id>
    # -------------------------------------------------------------------------
    def handle_DELETE_user(self):
        parsed_path = urlparse(self.path)
        parts = parsed_path.path.split('/')
        if len(parts) < 3 or not parts[2]:
            self.send_error_response(400, "User ID (id) is required in path, e.g. /user/<id>")
            return

        user_id = parts[2]
        
        try:
            db = SessionLocal()
            
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                self.send_error_response(404, f"User with ID {user_id} not found")
                return
            
            db.delete(user)
            db.commit()
            
            # Delete from Redis and invalidate list caches
            if self.redis:
                try:
                    self.redis.delete(f"user:{user_id}")
                    self._invalidate_users_list_cache()
                except Exception as e:
                    logger.warning(f"Failed to delete Redis key on DELETE: {e}")

            self.send_json_response({"message": f"User {user_id} deleted successfully"})
            
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error in DELETE /user: {str(e)}")
            self.send_error_response(500, "Database error occurred")
        finally:
            db.close()

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

    # ------------------------------
    # Redis helpers
    # ------------------------------
    def _invalidate_users_list_cache(self):
        if not self.redis:
            return
        try:
            for key in self.redis.scan_iter(match="users:*"):
                self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Failed invalidating users list cache: {e}")


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
            self.server = HTTPServer((self.host, self.port), MyHTTPRequestHandler)
            self.server.start_time = self.start_time

            logger.info(f"Starting HTTP server on {self.host}:{self.port}")
            logger.info("Available endpoints:")
            logger.info("  GET    /           - Server info")
            logger.info("  GET    /users      - List users (filters: name, place, occupation)")
            logger.info("  POST   /user       - Create user")
            logger.info("  PATCH  /user/<id>  - Update user")
            logger.info("  DELETE /user/<id>  - Delete user")

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
