from flask import Flask, render_template, jsonify, request, Blueprint
import os
from werkzeug.security import check_password_hash

home_bp = Blueprint("home", __name__)