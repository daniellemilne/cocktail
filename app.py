from flask import session
from flask import Flask, render_template, request, jsonify, redirect, flash, url_for, json
import requests
from flask_cors import CORS
from flask_mail import Mail, Message 
import smtplib
from authlib.integrations.flask_client import OAuth
from flask_session import Session
from urllib.parse import urlencode
import logging
from pymongo import MongoClient
import os
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from flask.json import JSONEncoder
import re


app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'secret_key'
CORS(app)

mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client.project  # database name
#new collection
cocktail_collection = db.cocktail
db_cocktails = cocktail_collection.find()
reviews_collection = db["reviews"]
cocktail_gen = db.cocktail_gen
saved_cocktail_collection = db["saved_cocktails"]
saved_cocktails = db["saved_cocktails"]


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId):
            return str(obj)
        return super().default(obj)

app.json_encoder = CustomJSONEncoder


class Constants:
    JWT_PAYLOAD = 'jwt_payload'
    PROFILE_KEY = 'profile'

constants = Constants()


app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

oauth = OAuth(app)

auth0 = oauth.register(
    'auth0',
    client_id='hbRr1b243My0zXQeWJTgrvqRfigcIh5o',
    client_secret='IJkqNPdEAOpfuGfGn5x7IzrRJOc3XRkXqntj0lEJDzGEETydY10iuHWRf0fIzI5B',
    api_base_url='https://dev-m6f6h3yifogp6uyw.us.auth0.com',  
    access_token_url='https://dev-m6f6h3yifogp6uyw.us.auth0.com/oauth/token',
    authorize_url='https://dev-m6f6h3yifogp6uyw.us.auth0.com/authorize',
     jwks_uri='https://dev-m6f6h3yifogp6uyw.us.auth0.com/.well-known/jwks.json',
    client_kwargs={
        'scope': 'openid profile email',
    },
)



gmail_user = 'daniellemilne7@gmail.com'
gmail_password = 'kqerfrwxssrsihid'


# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'daniellemilne7@gmail.com'  #  email address
app.config['MAIL_PASSWORD'] = 'kqerfrwxssrsihid'  #  Gmail password
app.config['MAIL_DEFAULT_SENDER'] = 'daniellemilne7@gmail.com'  #  Gmail email address

mail = Mail(app)


cocktails = list(db_cocktails)
cocktails_data = []
get_saved_cocktails = []
saved_cocktails_list = [] 

def insert_cocktail(name, image, description, ingredients, instructions):
    cocktail_gen.insert_one({
        "name": name,
        "image": image,
        "description": description,
        "ingredients": ingredients,
        "instructions": instructions
    })

def add_cocktail(name, image_filename, description, ingredients):
    cocktail = {
        'name': name,
        'image': f'static/img/{image_filename}', # Update to include full path
        'description': description,
        'ingredients': ingredients
    }
    cocktail_collection.insert_one(cocktail)


@app.route('/')
def index():
    return render_template('index.html', cocktails=cocktails_data)

@app.route('/search', methods=['POST'])
def search():
    # Get the JSON data from the request and retrieve the ingredients
    data = request.get_json()
    ingredients = data.get('ingredients', []) or [data.get('ingredient', '')]
    # Split the ingredients string into a list and remove any extra whitespace
    ingredients = [ingredient.strip() for ingredient in ','.join(ingredients).split(',')]

    print(f"Received data: {data}")
    print(f"Ingredients: {ingredients}")

    found_cocktails_data = []

    # Find cocktails containing all specified ingredients
    ingredient_cocktails = list(cocktail_gen.find({"ingredients": {"$all": ingredients}}))
    # Loop through the found cocktails and add them to the found_cocktails_data list
    for cocktail in ingredient_cocktails:
        print(cocktail)
        found_cocktails_data.append(cocktail)  # Add the cocktail data to the found_cocktails_data list
    # Find cocktails containing at least one of the specified ingredients
    found_cocktails = cocktail_gen.find({"ingredients": {"$in": ingredients}})
    # Create a list of dictionaries with the relevant cocktail information
    cocktails = [
        {
            "id": str(cocktail["_id"]),
            "name": cocktail["name"],
            "image": f"/static/img/{cocktail['image']}",
            "description": cocktail["description"],
            "ingredients": cocktail["ingredients"],
            "ingredient_quantities": cocktail.get("ingredient_quantities", []), 
        }
        for cocktail in found_cocktails_data
    ]
    print(f"Found cocktails: {found_cocktails}")

    print(cocktails)
    # Return the cocktails as a JSON object
    return jsonify(cocktails=cocktails)




@app.route('/filter')
def filter():
    criteria = request.args.get('criteria', '').lower()
    filtered_cocktails = list(cocktail_gen.find({"name": {"$regex": criteria, "$options": "i"}}))
    return jsonify(filtered_cocktails)


@app.route('/top10')
def top10():
    top10_cocktails = list(db.cocktail_gen.find({"mocktail": {"$exists": False}}).limit(10))
    return render_template('top10.html', cocktails=top10_cocktails)


@app.route('/Learn')
def Learn():
    return render_template('Learn.html')

@app.route('/Ingredients')
def Ingredients():
    return render_template('Ingredients.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/contact', methods=['POST'])
def handle_contact_form():
    # Get form data from the request
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    # Prepare the email message
    email_body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
    email_subject = f"Contact Form: {subject}"
    
    try:
        # Set up and connect to the email server using SSL
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        # Send the email
        server.sendmail(gmail_user, 'daniellemilne7@gmail.com', f'Subject: {email_subject}\n\n{email_body}')
        server.close()
        # Show a success message to the user
        flash('Your message has been sent successfully!', 'success')
    except Exception as e:
        # If an error occurs, print the error and show an error message to the user
        print('Something went wrong...', e)
        flash('An error occurred while sending your message. Please try again later.', 'error')

    # Redirect the user back to the contact page
    return redirect('/contact')


@app.route('/submitvideo', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        recipe = request.form['recipe']
        video = request.form['video']

        # Send an email
        msg = Message('New Video Submission',
                      recipients=['daniellemilne7@gmail.com'])  #your email address
        msg.body = f'Name: {name}\nEmail: {email}\nRecipe: {recipe}\nVideo: {video}'
        mail.send(msg)

        # Show a success message
        flash('Your submission has been received successfully!', 'success')

        # Redirect to a thank you page or any other page
        return redirect('/submitvideo')
    else:
        # Clear existing flashed messages when loading the page with a GET request
        session.pop('_flashes', None)
    return render_template('submitvideo.html')


@app.route('/login')
def login():
    return auth0.authorize_redirect(redirect_uri='http://127.0.0.1:5000/callback')

@app.route('/callback')
def callback_handling():
    token = auth0.authorize_access_token()
    resp = auth0.get('userinfo')
    userinfo = resp.json()

    session[constants.JWT_PAYLOAD] = userinfo
    session[constants.PROFILE_KEY] = {
        'user_id': userinfo['sub'],
        'name': userinfo['name'],
        'picture': userinfo['picture']
    }
    return redirect('/')


@app.route('/logout')
def logout():
    session.clear()
    params = {
        'returnTo': 'http://127.0.0.1:5000',
        'client_id': 'hbRr1b243My0zXQeWJTgrvqRfigcIh5o'
    }
    return redirect(auth0.api_base_url + '/v2/logout?' + urlencode(params))

@app.route('/')
def dashboard():
    if 'profile' in session:
        return render_template('index.html', userinfo=session['profile'])
    else:
        return render_template('index.html')


@app.route('/quiz')
def quiz():
    return render_template('quiz.html')

# Query the database to get the sweet and sour cocktails
sweet_cocktails = list(cocktail_gen.find({"taste": "sweet"}))
sour_cocktails = list(cocktail_gen.find({"taste": "sour"}))

@app.route('/result', methods=['POST'])
def result():
    # Calculate the quiz results here
    sweet = 0
    sour = 0

    for key, value in request.form.items():
        if value == 'sweet':
            sweet += 1
        elif value == 'sour':
            sour += 1

    # Determine the final result
    result = 'sweet' if sweet > sour else 'sour'

    if result == 'Sweet':
        recommended_cocktails = sweet_cocktails
    else:
        recommended_cocktails = sour_cocktails
        
    return render_template('result.html', result=result, recommended_cocktails=recommended_cocktails)

reviews = {}  # Create a dictionary to store reviews by cocktail_id

# Remove the first fetch_recommended_cocktails function that uses thecocktaildb.com API

def fetch_recommended_cocktails(main_ingredient):
    recommended_cocktails = list(cocktail_gen.find({"ingredients": main_ingredient}).limit(3))
    print(f"Main ingredient: {main_ingredient}")
    print(f"Recommended cocktails: {recommended_cocktails}")
    return recommended_cocktails



@app.route('/cocktail/<string:cocktail_id>', methods=['GET', 'POST'])
def cocktail(cocktail_id):
    
    # Handle form submission for reviews
    if request.method == 'POST':
        name = request.form.get('name')
        review_text = request.form.get('review')
        star_rating = request.form.get('star_rating')

        review = {
            'cocktail_id': cocktail_id,
            'name': name,
            'review': review_text,
            'star_rating': star_rating
        }

        reviews_collection.insert_one(review)

        return redirect(f'/cocktail/{cocktail_id}')
    
    # Extract the 24-character hex string from the given ObjectId string
    cocktail_id_cleaned = re.sub(r"[^0-9a-fA-F]", "", cocktail_id)
    cocktail_data = cocktail_gen.find_one({"_id": ObjectId(cocktail_id_cleaned)})

    if cocktail_data:
        # Fetch the reviews for the current cocktail
        cocktail_reviews = list(reviews_collection.find({'cocktail_id': cocktail_id}))
        
        # Fetch the main ingredient
        main_ingredient = cocktail_data["ingredients"][0]

        # Fetch recommended cocktails
        recommended_cocktails = fetch_recommended_cocktails(main_ingredient)

        # Calculate the average star rating
        average_rating = calculate_average_rating(cocktail_reviews)

        return render_template('cocktail.html', cocktail=cocktail_data, reviews=cocktail_reviews, average_rating=average_rating, recommended_cocktails=recommended_cocktails)

    logging.error("No data found for the requested cocktail")
    return "Cocktail not found", 404

@app.route('/cocktail/<string:cocktail_id>/submit_review', methods=['POST'])
def submit_review(cocktail_id):
    if request.method == 'POST':
        name = request.form.get('name')
        review_text = request.form.get('review')
        star_rating = request.form.get('star_rating')

        review = {
            'cocktail_id': cocktail_id,
            'name': name,
            'review': review_text,
            'star_rating': star_rating
        }

        reviews_collection.insert_one(review)

        return redirect(f'/cocktail/{cocktail_id}')

@app.route('/cocktail/<string:cocktail_id>/edit_review/<string:review_id>', methods=['GET', 'POST'])
def edit_review(cocktail_id, review_id):
    if request.method == 'POST':
        # Update the review
        name = request.form.get('name')
        review_text = request.form.get('review')
        star_rating = request.form.get('star_rating')
        
        reviews_collection.update_one(
            {'_id': ObjectId(review_id)},
            {'$set': {
                'name': name,
                'review': review_text,
                'star_rating': star_rating
            }}
        )
        
        return redirect(f'/cocktail/{cocktail_id}')

    # Fetch the review to be edited
    review = reviews_collection.find_one({'_id': ObjectId(review_id)})
    
    return render_template('edit_review.html', review=review, cocktail_id=cocktail_id)

@app.route('/cocktail/<string:cocktail_id>/delete_review/<string:review_id>', methods=['POST'])
def delete_review(cocktail_id, review_id):
    # Delete the review
    reviews_collection.delete_one({'_id': ObjectId(review_id)})
    
    return redirect(f'/cocktail/{cocktail_id}')




def calculate_average_rating(reviews):
    if not reviews:
        return None

    total_rating = 0
    for review in reviews:
        total_rating += int(review['star_rating'])

    average_rating = total_rating / len(reviews)
    return round(average_rating, 2)

@app.route('/amaretto')
def amaretto():
    return render_template('amaretto.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/trivia')
def trivia():
    return render_template('trivia.html')

@app.route('/wall')
def wall():
    
    db_cocktails = cocktail_collection.find()

    cocktails_transformed = []
    for db_cocktail in db_cocktails:
        name = db_cocktail.get("name") or db_cocktail.get("strDrink")
        image = db_cocktail.get("image") or db_cocktail.get("strDrinkThumb")
        if image and not image.startswith("http"):
            image = url_for('static', filename=f'uploads/{image}')

        cocktails_transformed.append({
            "id": str(db_cocktail["_id"]),
            "name": name,
            "image": image,
            "likes": len(db_cocktail.get("likes", [])),
            "dislikes": len(db_cocktail.get("dislikes", [])),
            "comments": [{"user_id": comment["user_id"], "content": comment["comment"]} for comment in db_cocktail.get("comments", [])]
        })


    return render_template('wall.html', cocktails=cocktails_transformed)


@app.route('/save-cocktail', methods=['POST'])
def save_cocktail():
    cocktail_id = request.form.get('cocktail_id')
    print(f"Received cocktail_id: {cocktail_id}")
    cocktail = get_cocktail_by_id(cocktail_id)

    if cocktail:
        try:
            # Check if the cocktail is already saved
            existing_saved_cocktail = saved_cocktails.find_one({"cocktail_id": cocktail_id})
            
            if not existing_saved_cocktail:
                # Save the cocktail to the 'saved_cocktails' collection
                saved_cocktails.insert_one({
                    "cocktail_id": cocktail_id,
                    "cocktail_data": cocktail
                })
                return redirect(url_for('saved_drinks'))
            else:
                print(f"Cocktail with ID {cocktail_id} is already saved")
                return redirect(url_for('saved_drinks'))

        except Exception as e:
            print(f"Error saving cocktail: {str(e)}")
            return jsonify({"error": "An error occurred while saving the cocktail"}), 500
    else:
        print(f"No cocktail found with ID: {cocktail_id}")
        return jsonify({"error": "Cocktail not found"}), 404

def get_saved_cocktails():
    return list(saved_cocktails.find())


@app.route('/saved-drinks')
def saved_drinks():
    # Fetch all saved cocktails
    all_saved_cocktails = list(saved_cocktails.find())
    print("All saved cocktails:", all_saved_cocktails)
    return render_template('SavedDrinks.html', saved_cocktails=all_saved_cocktails)

@app.route('/unsave/<string:cocktail_id>', methods=['POST'])
def unsave_cocktail(cocktail_id):
    # Remove the cocktail from the saved cocktails list
    saved_cocktails.delete_one({"cocktail_data._id": ObjectId(cocktail_id)})
    return redirect('/saved-drinks')



def get_cocktail_by_id(cocktail_id):
    try:
        # Assuming 'cocktail_gen' is the reference to your MongoDB collection
        cocktail = cocktail_gen.find_one({"_id": ObjectId(cocktail_id)})
        if cocktail:
            return cocktail
        else:
            print(f"No cocktail found with ID: {cocktail_id}")
            return None
    except Exception as e:
        print(f"Error fetching cocktail with ID {cocktail_id}: {str(e)}")
        return None



@app.route('/profile')
def profile():
    user = {
        'name': 'John Smith',
        'profile_picture_url': url_for('static', filename='img/default_profile_picture.jpg')
    }
    return render_template('profile.html', user=user)


@app.route('/upload_cocktail', methods=['POST'])
def upload_cocktail():
    if 'profile' not in session:
        flash('You need to be logged in to upload a cocktail.', 'error')
        return redirect(url_for('wall'))

    name = request.form.get('name')
    image = request.files.get('image')
    description = request.form.get('description')

    image_filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

    new_cocktail = {
        "name": name,
        "image": image_filename,
        "description": description,
        "user_id": session['profile']['user_id'],
        "likes": [],
        "dislike": [],
        "comments": []
    }

    cocktail_collection.insert_one(new_cocktail)
    flash('Cocktail uploaded successfully!', 'success')
    return redirect(url_for('wall'))

@app.route('/wall/<string:cocktail_id>/like', methods=['POST'])
def like_cocktail(cocktail_id):
    user_id = session.get(constants.PROFILE_KEY, {}).get('user_id')
    if not user_id:
        flash('You must be logged in to like a cocktail.', 'error')
        return redirect('/wall')

    db_cocktail = cocktail_collection.find_one({"_id": ObjectId(cocktail_id)})
    if user_id not in db_cocktail.get("likes", []):
        cocktail_collection.update_one({"_id": ObjectId(cocktail_id)}, {"$addToSet": {"likes": user_id}})

    return redirect('/wall')

@app.route('/wall/<string:cocktail_id>/dislike', methods=['POST'])
def dislike_cocktail(cocktail_id):
    user_id = session.get(constants.PROFILE_KEY, {}).get('user_id')
    if not user_id:
        flash('You must be logged in to dislike a cocktail.', 'error')
        return redirect('/wall')

    db_cocktail = cocktail_collection.find_one({"_id": ObjectId(cocktail_id)})
    if user_id not in db_cocktail.get("dislikes", []):
        cocktail_collection.update_one({"_id": ObjectId(cocktail_id)}, {"$addToSet": {"dislikes": user_id}})

    return redirect('/wall')



@app.route('/wall/<string:cocktail_id>/comment', methods=['POST'])
def comment_cocktail(cocktail_id):
    user_id = session.get(constants.PROFILE_KEY, {}).get('user_id')
    if not user_id:
        flash('You must be logged in to comment on a cocktail.', 'error')
        return redirect('/wall')

    content = request.form.get('comment')

    comment = {"user_id": user_id, "comment": content}
    cocktail_collection.update_one({"_id": ObjectId(cocktail_id)}, {"$push": {"comments": comment}})

    return redirect('/wall')

@app.route('/wall/<string:cocktail_id>/share', methods=['POST'])
def share_cocktail(cocktail_id):
    user_id = session.get(constants.PROFILE_KEY, {}).get('user_id')
    if not user_id:
        flash('You must be logged in to share a cocktail.', 'error')
        return redirect('/wall')

    email = request.form.get('email')

    # Send an email to the recipient with the cocktail's details
    db_cocktail = cocktail.find_one({"_id": ObjectId(cocktail_id)})
    msg = Message(
        'A friend shared a cocktail with you',
        recipients=[email],
    )
    msg.body = f"Hey, your friend just shared '{db_cocktail['name']}' with you. Check it out on our app!"
    mail.send(msg)

    flash('Cocktail shared successfully!', 'success')
    return redirect('/wall')


@app.route('/searchgen')
def searchgen():
    # Get the search query from the request
    query = request.args.get('query', '')

    # Search for cocktails in the MongoDB database based on the name with case-insensitive regex
    found_cocktails = cocktail_gen.find({"name": {"$regex": query, "$options": "i"}})

    cocktails = []
    # Loop through the found cocktails and create a list of dictionaries with the relevant cocktail information
    for cocktail_data in found_cocktails:
        cocktails.append({
            "id": str(cocktail_data["_id"]),
            "name": cocktail_data["name"],
            "image": f"/static/img/{cocktail_data['image']}",
            "description": cocktail_data["description"],
            "ingredients": cocktail_data["ingredients"],
            "ingredient_quantities": cocktail_data.get("ingredient_quantities", []),
            # Add more fields as needed
        })
     # Render the search results template with the found cocktails or None if no cocktails were found
    return render_template('searchgen_results.html', cocktails=cocktails if cocktails else None)

@app.route('/mocktails')
def mocktails():
    mocktails_cursor = db.cocktail_gen.find({"mocktail": True})
    mocktails = list(mocktails_cursor)
    
    for mocktail in mocktails:
        print(mocktail)
        
    return render_template('mocktails.html', mocktails=mocktails)


if __name__ == '__main__':
    app.run(debug=True)
