from flask import Flask, request, jsonify
from flask_cors import CORS
from database import init_db, get_db_connection
import datetime

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}}) # Allow all origins for simplicity, can be restricted for production

init_db()

@app.route('/tasks', methods=['GET'])
def get_tasks():
    conn = get_db_connection()
    tasks = conn.execute('SELECT * FROM tasks ORDER BY is_completed ASC, priority ASC, due_date ASC').fetchall()
    conn.close()
    return jsonify([dict(task) for task in tasks])

@app.route('/tasks', methods=['POST'])
def add_task():
    data = request.json
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400
    
    title = data['title']
    priority = int(data.get('priority', 3))
    due_date = data.get('due_date') # Expecting YYYY-MM-DD
    
    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO tasks (title, priority, is_completed, due_date) VALUES (?, ?, ?, ?)',
        (title, priority, False, due_date)
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    
    return jsonify({'id': new_id, 'message': 'Task created'}), 201

@app.route('/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    data = request.json
    conn = get_db_connection()
    
    fields = []
    values = []
    allowed_fields = ['title', 'priority', 'is_completed', 'due_date']
    
    for key in allowed_fields:
        if key in data:
            fields.append(f"{key} = ?")
            values.append(data[key])
            
    if not fields:
        conn.close()
        return jsonify({'error': 'No valid fields to update'}), 400
        
    values.append(id)
    query = f"UPDATE tasks SET {', '.join(fields)} WHERE id = ?"
    
    conn.execute(query, values)
    conn.commit()
    conn.close()
    
    return jsonify({'message': 'Task updated'})

@app.route('/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM tasks WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Task deleted'})

@app.route('/', methods=['GET'])
def index():
    return jsonify({'message': 'Hello, World!'}), 200

if __name__ == '__main__':
    app.run(debug=True, port=8000)
