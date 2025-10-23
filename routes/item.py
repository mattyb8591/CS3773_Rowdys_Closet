from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app
import os
from werkzeug.security import check_password_hash

item_bp = Blueprint("item", __name__, template_folder="templates", static_folder="static")

@item_bp.route("/", methods=["GET"])
def index():
    
    return render_template("item.html")