from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin


app = Flask(__name__)
cors = CORS(app)

# Set up SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
db = SQLAlchemy(app)

# Define database model
class UserData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chat_id = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    stored_url = db.Column(db.String(300), nullable=False)

# Create database
@app.before_request
def create_tables():
    db.create_all()

# API endpoint to store data
@app.route('/api/store', methods=['POST'])
def store_data():
    data = request.json
    user = UserData(chat_id=data['ChatID'], name=data['Name'], email=data['Email'], stored_url=data['storedURL'])
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'Data stored successfully'}), 201

# API endpoint to get storedURL by email
@app.route('/api/retrieve', methods=['GET'])
def retrieve_url():
    email = request.args.get('email')
    user = UserData.query.filter_by(email=email).first()
    if user:
        return jsonify({'storedURL': user.stored_url}), 200
    return jsonify({'error': 'User not found'}), 404

# Serve the HTML form
#@app.route('/')
#def form():
#    return render_template('upload_form.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
