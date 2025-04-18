from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Orchestrator Agent is running!'

@app.route('/request', methods=['POST'])
def handle_request():
    data = request.get_json()
    if not data or 'request_type' not in data:
        return jsonify({'error': 'Invalid request payload'}), 400

    request_type = data.get('request_type')
    # Basic placeholder logic: Acknowledge receipt
    # In the future, this will involve actual delegation logic
    print(f"Received request of type: {request_type}")

    # Simulate delegation based on request type
    target_agent = "Unknown Agent"
    if request_type == 'product_research':
        target_agent = "Product Research Agent"
    elif request_type == 'market_analysis':
        target_agent = "Market Analysis Agent"
    # Add more elif blocks for other agent types

    message = f"Request type '{request_type}' received. Delegating to {target_agent}..."
    return jsonify({'message': message}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080) 