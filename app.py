from flask import Flask, request, jsonify

app = Flask(__name__)


items = []
next_item_id = 1

@app.route('/items', methods=['GET'])
def get_items():
    """
    Endpoint to get all items.
    ---
    responses:
      200:
        description: A list of items.
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
    """
    return jsonify(items), 200

@app.route('/items', methods=['POST'])
def add_item():
    """
    Endpoint to add a new item.
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              description: Name of the item to add.
    responses:
      201:
        description: Item created successfully.
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
      400:
        description: Invalid input (e.g., name not provided).
    """
    global next_item_id
    if not request.json or not 'name' in request.json:
        return jsonify({"error": "Missing name in request body"}), 400
    
    new_item = {
        "id": next_item_id,
        "name": request.json['name']
    }
    items.append(new_item)
    next_item_id += 1
    return jsonify(new_item), 201

@app.route('/items/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """
    Endpoint to get a specific item by its ID.
    ---
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        description: The ID of the item to retrieve.
    responses:
      200:
        description: The requested item.
        schema:
          type: object
          properties:
            id:
              type: integer
            name:
              type: string
      404:
        description: Item not found.
    """
    item = next((item for item in items if item["id"] == item_id), None)
    if item:
        return jsonify(item), 200
    else:
        return jsonify({"error": "Item not found"}), 404

if __name__ == '__main__':
    
    items = []
    next_item_id = 1
    app.run(debug=True, port=5000)
