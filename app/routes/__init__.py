from flask import Blueprint
from .upload_routes import upload_bp
from .board_routes import board_bp
from .other_routes import home_bp

blueprints = [upload_bp, board_bp, home_bp]
