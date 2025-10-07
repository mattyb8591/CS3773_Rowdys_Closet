from flask import Flask, render_template, jsonify, request, Blueprint
import os
from werkzeug.security import check_password_hash

item_bp = Blueprint("item", __name__)