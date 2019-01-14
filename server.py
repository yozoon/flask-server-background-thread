#!/usr/bin/env python
from time import sleep
from datetime import datetime
from threading import Thread
from queue import Queue
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

namespace='/test'

async_mode = 'eventlet'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'verysecretphrase'
socketio = SocketIO(app, async_mode=async_mode)

thread = None
running = False
qtask = None
q = Queue()

def worker_task():
    global running
    print("Thread started")
    while running:
        """ Put blocking code that might take longer to execute here """
        sleep(5)
        q.put(str(datetime.now()))
    print("Thread stopped")

def queue_task():
    count = 0
    while True:
        socketio.sleep(0.5)
        count += 1
        if not q.empty():
            item = q.get()
            print(item)
            q.task_done()
            socketio.emit('log', item, namespace=namespace)

@app.before_first_request
def init_job():
    global qtask
    qtask = socketio.start_background_task(queue_task)

@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)

@socketio.on('action', namespace=namespace)
def start(action):
    global thread
    global running
    if action.lower() == 'start':
        if not thread == None:
            if thread.is_alive():
                socketio.emit('message', 'Thread is active', namespace=namespace)
                return
        thread = Thread(target = worker_task)
        thread.daemon = True
        running = True
        socketio.emit('message', 'Thread created', namespace=namespace)
        thread.start()
        return
    elif action.lower() == 'stop':
        running = False
        if not thread == None:
            if thread.is_alive():
                print('Told the thread to stop')
                socketio.emit('message', 'Told the thread to stop', namespace=namespace)
                return    
        socketio.emit('message', 'Thread is not running', namespace=namespace)
        return

@socketio.on('stop', namespace=namespace)
def stop():
    global thread
    global running
    running = False
    print("Told the thread to stop")
    socketio.emit('message', "Told the thread to stop", namespace=namespace)

# This function is called when a web browser connects
@socketio.on('connect', namespace=namespace)
def connect():
    global qtask
    if qtask == None:
        qtask = socketio.start_background_task(queue_task)
    
    print('Client connected', request.sid)
    emit('connect')

# Notification that a client has disconnected
@socketio.on('disconnect', namespace=namespace)
def disconnect():
    print('Client disconnected', request.sid)
    emit('disconnect')

# Ping-pong allows Javascript in the web page to calculate the
# connection latency, averaging over time
@socketio.on('measure', namespace=namespace)
def ping_pong():
    emit('pong')

if __name__ == "__main__":
    socketio.run(app, host='127.0.0.1', port=8000)
