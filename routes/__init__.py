from flask import Blueprint
from routes.upload_routes import upload_bp
from routes.board_routes import board_bp

blueprints = [upload_bp, board_bp]