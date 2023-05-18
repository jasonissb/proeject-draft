# proeject-draft
it needs to import flask import Flask, render_template, session, request , redirect, url_for,jsonify
import sqlite3
from werkzeug.security import generate_password_hash,check_password_hash
from flask_socketio import SocketIO, send, emit, join_room, leave_room
import openai
import eventlet
