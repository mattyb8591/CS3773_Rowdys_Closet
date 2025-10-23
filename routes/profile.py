from flask import Flask, render_template, jsonify, request, Blueprint, redirect, current_app
import os
from werkzeug.security import check_password_hash

profile_bp = Blueprint("profile", __name__, template_folder="templates", static_folder="static")

@profile_bp.route("/", methods=["GET"])
def index():
    return render_template("profile.html")