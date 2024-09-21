from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import boto3

app = Flask(__name__)

# Configure SQLAlchemy for storing user data
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

# AWS S3 configuration
s3 = boto3.client('s3', region_name='us-east-1')
BUCKET_NAME = 'your-bucket-name'

# Database model for user
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    file_url = db.Column(db.String(200), nullable=False)

# Initialize database
@app.before_first_request
def create_tables():
    db.create_all()

# Endpoint for file upload and data storage
@app.route('/upload', methods=['POST'])
def upload_file():
    username = request.form['username']
    email = request.form['email']
    file = request.files['file']

    if file and email:
        # Save file locally and upload to S3
        filename = file.filename
        file.save(os.path.join('uploads', filename))
        s3.upload_file(os.path.join('uploads', filename), BUCKET_NAME, filename)

        # Store user data in DB with S3 file URL
        file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{filename}"
        new_user = User(username=username, email=email, file_url=file_url)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({'message': 'File uploaded and user data saved', 'file_url': file_url}), 200
    return jsonify({'error': 'Invalid request'}), 400

# Endpoint to retrieve file using email as query filter
@app.route('/files/<email>', methods=['GET'])
def get_file(email):
    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({'file_url': user.file_url}), 200
    return jsonify({'error': 'User not found'}), 404

if __name__ == "__main__":
    app.run(debug=True)
