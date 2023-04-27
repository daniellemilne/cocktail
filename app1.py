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
from flask_migrate import Migrate
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
from mocktail_data import mocktails


app = Flask(__name__, static_folder='static')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.secret_key = 'secret_key'
CORS(app)

mongo_client = MongoClient('mongodb://localhost:27017')
db = mongo_client.project  # database name
#new collection
cocktail_collection = db.cocktail
db_cocktails = cocktail_collection.find()
reviews_collection = db.reviews


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


@app.route('/')
def index():
    return render_template('index.html', cocktails=cocktails_data)

@app.route('/search', methods=['POST'])
def search():
    data = request.get_json() #Gets JSON data from the request
    ingredients = data.get('ingredients', []) or [data.get('ingredient', '')] #Retrieves the ingredients list from the JSON data

    # Split the input string by commas and strip any whitespace
    ingredients = [ingredient.strip() for ingredient in ','.join(ingredients).split(',')]

    print(f"Received data: {data}")  #  To print the received data
    print(f"Ingredients: {ingredients}")  # To print the ingredients

    base_url = 'https://www.thecocktaildb.com/api/json/v1/1/' #base URL for the cocktaildb api

    global cocktail_data
    cocktails_data = [] #empty list store cocktail data

    for ingredient in ingredients: #iterates through the list of ingredients
        search_url = f'{base_url}filter.php?i={ingredient}' #creates the search url for the ingredient 
        response = requests.get(search_url) #GET request for the ingredient
        print(response.json()) # prints the response
        ingredient_cocktails = response.json().get('drinks', []) #gets the list of drinks from the json response
        
        for cocktail in ingredient_cocktails:
            print(cocktail) # print the cocktail data
            cocktail_id = cocktail['idDrink'] #get the cocktail ID
            cocktails_data.append(cocktail) # appends the cocktail data to the cocktail_data list

    cocktails = []
    for cocktail_data in cocktails_data:
        cocktail_id = cocktail_data.get('idDrink')
        details_url = f'{base_url}lookup.php?i={cocktail_id}'
        details_response = requests.get(details_url)
        details_data = details_response.json().get('drinks')[0]

        ingredients = []
        for i in range(1, 16): #iterate through the ingredient keys in the details data (stringredient1 to 15)
            ingredient = details_data.get(f'strIngredient{i}')
            if ingredient:
                ingredients.append(ingredient)

        #creates a dictionary to store the cocktail data
        cocktail = {
            'id': str(cocktail_id),
            'name': details_data.get('strDrink'),
            'image': details_data.get('strDrinkThumb'),
            'description': details_data.get('strInstructions'),
            'ingredients': ingredients,
        }

        #appends the cocktail dictionary list
        cocktails.append(cocktail)
    #Prints final list
    print(cocktails)
    #Returns the cocktail list as a JSON object
    return jsonify(cocktails)



@app.route('/filter')
def filter():
    criteria = request.args.get('criteria', '').lower()
    filtered_cocktails = [c for c in cocktails if criteria in c['name'].lower()]
    return jsonify(filtered_cocktails)

@app.route('/top10')
def top10():
    return render_template('top10.html')

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
    name = request.form.get('name')
    email = request.form.get('email')
    subject = request.form.get('subject')
    message = request.form.get('message')

    # Prepare the email message
    email_body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
    email_subject = f"Contact Form: {subject}"
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, 'daniellemilne7@gmail.com', f'Subject: {email_subject}\n\n{email_body}')
        server.close()
        flash('Your message has been sent successfully!', 'success')
    except Exception as e:
        print('Something went wrong...', e)
        flash('An error occurred while sending your message. Please try again later.', 'error')

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

    return render_template('result.html', result=result)

reviews = {}  # Create a dictionary to store reviews by cocktail_id

# Add a new function to fetch recommended cocktails
def fetch_recommended_cocktails(main_ingredient):
    url = f"https://www.thecocktaildb.com/api/json/v1/1/filter.php?i={main_ingredient}"
    response = requests.get(url)

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        return []

    if data and data["drinks"]:
        #limit results to the top three
        return data["drinks"][:3]

    return []


@app.route('/cocktail/<string:cocktail_id>', methods=['GET', 'POST'])
def cocktail(cocktail_id):
    # Handle form submission
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

    # Fetch the cocktail details
    url = f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={cocktail_id}"
    response = requests.get(url)
    
    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        return None

    if data and data["drinks"]:
        cocktail_data = data["drinks"][0]
        
        # Extract ingredients
        ingredients = []
        for i in range(1, 16):
            ingredient = cocktail_data[f'strIngredient{i}']
            measurement = cocktail_data[f'strMeasure{i}']
            if ingredient and measurement:
                ingredients.append(f'{measurement.strip()} {ingredient.strip()}')
            elif ingredient:
                ingredients.append(ingredient.strip())
        
        cocktail = {
            "id": cocktail_data["idDrink"],
            "name": cocktail_data["strDrink"],
            "image": cocktail_data["strDrinkThumb"],
            "description": cocktail_data["strInstructions"],
            "ingredients": ingredients  # Add ingredients to the cocktail dictionary
            # Add more fields as needed
        }

        # Fetch the reviews for the current cocktail
        cocktail_reviews = list(reviews_collection.find({'cocktail_id': cocktail_id}))
        
        # Fetch the main ingredient
        main_ingredient = cocktail_data["strIngredient1"]

        # Fetch recommended cocktails
        recommended_cocktails = fetch_recommended_cocktails(main_ingredient)

        # Calculate the average star rating
        average_rating = calculate_average_rating(cocktail_reviews)

        return render_template('cocktail.html', cocktail=cocktail, reviews=cocktail_reviews, average_rating=average_rating, recommended_cocktails=recommended_cocktails)

    logging.error("No data found for the requested cocktail")
    return None


@app.route('/cocktail/<string:cocktail_id>/submit_review', methods=['POST'])
def submit_review(cocktail_id):
    name = request.form.get('name')
    review = request.form.get('review')
    star_rating = request.form.get('star_rating')

    # Find the cocktail and append the review
    for cocktail in cocktails:
        if cocktail["id"] == cocktail_id:
            cocktail["reviews"].append({
                "name": name,
                "review": review,
                "star_rating": star_rating,
            })
            break

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
            "comments": [{"user_id": comment["user_id"], "content": comment["comment"]} for comment in db_cocktail.get("comments", [])]
        })


    return render_template('wall.html', cocktails=cocktails_transformed)




@app.route('/save-cocktail/<int:cocktail_id>', methods=['POST'])
def save_cocktail(cocktail_id):
    cocktail = get_cocktail_by_id(cocktail_id)
    if cocktail:
        cocktail_collection.insert_one(cocktail)
        print(f"Cocktail with ID {cocktail_id} saved.")
    else:
        print(f"Cocktail with ID {cocktail_id} not found.")
    return redirect(url_for('savedDrinks'))



def get_saved_cocktails():
    return list(cocktail_collection.find())


@app.route('/saved-drinks')
def savedDrinks():
    saved_cocktails = get_saved_cocktails()
    print(saved_cocktails)  # This line to print saved_cocktails
    print(f"Saved cocktails: {saved_cocktails}")  # Add this line
    return render_template('SavedDrinks.html', saved_cocktails=saved_cocktails)


def get_cocktail_by_id(cocktail_id):
    api_url = f"https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={cocktail_id}"
    response = requests.get(api_url)
    if response.status_code == 200:
        data = response.json()
        if data["drinks"]:
            return data["drinks"][0]
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
    query = request.args.get('query', '')

    # You can use TheCocktailDB API to search for cocktails
    search_url = f"https://www.thecocktaildb.com/api/json/v1/1/search.php?s={query}"
    response = requests.get(search_url)

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError as e:
        logging.error(f"Error decoding JSON response: {e}")
        return None

    if data and data["drinks"]:
        cocktails = []
        for cocktail_data in data["drinks"]:
            cocktails.append({
                "id": cocktail_data["idDrink"],
                "name": cocktail_data["strDrink"],
                "image": cocktail_data["strDrinkThumb"],
                # Add more fields as needed
            })

        return render_template('searchgen_results.html', cocktails=cocktails)

    return render_template('searchgen_results.html', cocktails=None)

@app.route('/mocktails')
def mocktails_page():
    return render_template('mocktails.html', mocktails=mocktails)

@app.route('/mocktails', methods=['GET'])
def show_mocktails():
    return render_template('mocktails.html', mocktails=mocktails)


if __name__ == '__main__':
    app.run(debug=True)
