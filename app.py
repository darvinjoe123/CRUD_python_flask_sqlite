from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    dob = db.Column(db.DateTime, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    hobbies = db.Column(db.String(200))
    interests = db.Column(db.String(500))


# Create the database and tables
with app.app_context():
    db.create_all()


@app.route('/users', methods=['GET'])
def get_users():
    user_list = list_users()
    return jsonify(users=user_list)


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    user_data = {
        'Id': user.id,
        'Name': f"{user.first_name} {user.last_name}",
        'Email': user.email,
        'Age': calculate_age(user.dob),
        'Gender': user.gender,
        'Hobbies': user.hobbies.split(', ') if user.hobbies else [],
        'Interests': user.interests[:30] if user.interests else ""
    }
    return jsonify(user=user_data)


@app.route('/users/filter/age', methods=['GET'])
def filter_users_by_age():
    try:
        min_age = int(request.args.get('min_age'))
        max_age = int(request.args.get('max_age'))
    except ValueError:
        return jsonify(message='Invalid age values'), 400

    if min_age < 0 or max_age < 0 or min_age > max_age:
        return jsonify(message='Invalid age range'), 400
    total_users = list_users()
    user_list = []
    for user in total_users:
        if min_age <= user["Age"] <= max_age:
            user_list.append(user)

    return jsonify(filtered_users=user_list)

@app.route('/users/filter/name', methods=['GET'])
def filter_users_by_name():
    name_prefix = request.args.get('name_prefix')

    if not name_prefix:
        return jsonify(message='Name prefix is required'), 400

    filtered_users = User.query.filter(
        (User.first_name.like(f'{name_prefix}%')) | (
            User.last_name.like(f'{name_prefix}%'))
    ).all()

    user_list = []
    for user in filtered_users:
        user_data = {
            'Id': user.id,
            'Name': f"{user.first_name} {user.last_name}",
            'Email': user.email,
            'Age': calculate_age(user.dob),
            'Gender': user.gender,
            'Hobbies': user.hobbies.split(', ') if user.hobbies else [],
            'Interests': user.interests[:30] if user.interests else ""
        }
        user_list.append(user_data)

    return jsonify(filtered_users=user_list)


@app.route('/users/filter/hobbies', methods=['GET'])
def filter_users_by_hobbies():
    selected_hobbies = request.args.getlist('hobbies[]')
    print(selected_hobbies)
    print(', '.join(selected_hobbies))
    if not selected_hobbies:
        return jsonify(message='At least one hobby must be selected'), 400

    filtered_users = User.query.filter(
        User.hobbies.contains(', '.join(selected_hobbies))
    ).all()

    user_list = []
    for user in filtered_users:
        user_data = {
            'Id': user.id,
            'Name': f"{user.first_name} {user.last_name}",
            'Email': user.email,
            'Age': calculate_age(user.dob),
            'Gender': user.gender,
            'Hobbies': user.hobbies.split(', ') if user.hobbies else [],
            'Interests': user.interests[:30] if user.interests else ""
        }
        user_list.append(user_data)

    return jsonify(filtered_users=user_list)


@app.route('/users', methods=['POST'])
def add_user():
    data = request.json

    new_user = User(
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        dob=datetime.strptime(data['dob'], '%Y-%m-%d'),
        gender=data['gender'],
        hobbies=data['hobbies'],
        interests=data['interests']
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify(message='User added successfully')


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json

    user.first_name = data['first_name']
    user.last_name = data['last_name']
    user.email = data['email']
    user.dob = datetime.strptime(data['dob'], '%Y-%m-%d')
    user.gender = data['gender']
    user.hobbies = data['hobbies']
    user.interests = data['interests']

    db.session.commit()

    return jsonify(message='User updated successfully')


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return jsonify(message='User deleted successfully')


def calculate_age(dob):
    today = datetime.today()
    age = today.year - dob.year - \
        ((today.month, today.day) < (dob.month, dob.day))
    return age

def list_users():
    users = User.query.paginate()

    user_list = []
    for user in users.items:
        user_data = {
            'Id': user.id,
            'Name': f"{user.first_name} {user.last_name}",
            'Email': user.email,
            'Age': calculate_age(user.dob),
            'Gender': user.gender,
            'Hobbies': user.hobbies.split(', ') if user.hobbies else [],
            'Interests': user.interests[:30] if user.interests else ""
        }
        user_list.append(user_data)
    return user_list

if __name__ == '__main__':
    app.run(debug=True)
