from flask import Flask, render_template, jsonify, request, Blueprint, redirect
import os
from werkzeug.security import check_password_hash

profile_bp = Blueprint("profile", __name__)