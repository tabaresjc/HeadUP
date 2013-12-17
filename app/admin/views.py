from flask import Blueprint, render_template, flash, redirect, session, url_for, request, g, jsonify
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask.ext.wtf import Form
from app import app, login_manager

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template("admin/dashboard.html",
        title = 'Dashboard',
        content = 'Administration Site')