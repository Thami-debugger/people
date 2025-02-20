from flask import Flask, render_template, jsonify, redirect, url_for, request
import qrcode
import os

app = Flask(__name__)

queue = []
served_queue = []
missing_queue = []
current_number = 0
average_time_per_person = 5  # in minutes

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/join_queue')
def join_queue():
    global queue
    new_number = len(queue) + len(served_queue) + len(missing_queue) + 1
    queue.append(new_number)
    img = qrcode.make(f'http://localhost:5000/queue_status/{new_number}')
    img_path = f'static/queue_{new_number}.png'
    img.save(img_path)
    return render_template('queue.html', number=new_number, image_url=img_path)

@app.route('/queue_status/<int:number>')
def queue_status(number):
    return render_template('queue.html', number=number, image_url=f'static/queue_{number}.png')

@app.route('/current_status')
def current_status():
    global current_number, queue, average_time_per_person
    if queue:
        current_number = queue[0]
    wait_time = (len(queue) * average_time_per_person) - average_time_per_person
    return jsonify({
        'current_number': current_number,
        'queue_length': len(queue),
        'average_wait_time': max(0, wait_time)
    })

@app.route('/admin')
def admin():
    return render_template('admin.html', queue=queue, current_number=current_number)

@app.route('/serve_next', methods=['POST'])
def serve_next():
    global queue, served_queue
    if queue:
        served_queue.append(queue.pop(0))
    return redirect(url_for('admin'))

@app.route('/mark_missing/<int:number>', methods=['POST'])
def mark_missing(number):
    global queue, missing_queue
    if number in queue:
        queue.remove(number)
        missing_queue.append(number)
    return redirect(url_for('admin'))

if __name__ == '__main__':
    app.run(debug=True)
