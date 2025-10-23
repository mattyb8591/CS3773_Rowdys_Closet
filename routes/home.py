from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app
import os
from werkzeug.security import check_password_hash

home_bp = Blueprint("home", __name__, template_folder="templates", static_folder="static")

@home_bp.route("/", methods=["GET"])
def home():
    return render_template("home.html")