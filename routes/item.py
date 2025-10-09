from flask import Flask, render_template, jsonify, request, Blueprint, redirect
import os
from werkzeug.security import check_password_hash
from app import get_db_connection


item_bp = Blueprint("item", __name__, template_folder="routes")