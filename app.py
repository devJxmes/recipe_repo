from flask import Flask, render_template, url_for, request ,redirect, flash, session
from flask_sqlalchemy import  SQLAlchemy
from sqlalchemy import or_, create_engine
import urllib, random, string

params = urllib.parse.quote_plus("DRIVER={SQL Server};"
                                 "SERVER=localhost;"
                                 "DATABASE=recipe_db;")


app = Flask(__name__)
app.secret_key = "PYTHON"
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect={}".format(params)
db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = 'users' 
    user_id = db.Column(db.Integer,autoincrement = True, primary_key = True)
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(50))
    name = db.Column(db.String(50))

class Recipes(db.Model):
    __tablename__ = 'recipe' 
    recipe_id = db.Column(db.Integer, autoincrement = True, primary_key = True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(50))
    ingredients = db.Column(db.String(256))
    steps = db.Column(db.String(256))
    prep_time = db.Column(db.Integer)

class Comments(db.Model):
    __tablename__ = 'comments' 
    comment_id = db.Column(db.Integer,autoincrement = True, primary_key = True)
    recipe_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    comment = db.Column(db.String(50))
    
class Ratings(db.Model):
    __tablename__ = 'rating' 
    rating_id = db.Column(db.Integer,autoincrement = True, primary_key = True)
    recipe_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    value = db.Column(db.Integer)


@app.route('/')
def base():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if 'user_id' in session:
        flash("You are already logged in!", "info")
        return redirect(url_for('home'))
    else:
        return render_template('login.html')
    

@app.route('/logout')
def logout():
    flash("You have been successfully logged out!", "info")
    session.pop("user_id",None)
    return redirect(url_for('login'))

@app.route('/login/new', methods = ["POST"])
def check_acc():
    username = request.form['username']
    password = request.form['password']
    user = Users.query.filter_by(username=username, password=password).first()
    
    if user:
        session["user_id"] = user.user_id
        return redirect(url_for('home'))
    else:
        flash("Invalid username or password", "info")
        return redirect(url_for('login'))
    

@app.route('/register')
def reg():
    return render_template('register.html')

@app.route('/register/new', methods = ["POST"])
def reg_new():
    
    username = request.form["username"] 
    password = request.form["password"]
    name = request.form["name"]
    existing_user = Users.query.filter_by(username=username).first()
    
    if existing_user:
        flash("Account already exists!", "info")
        return redirect(url_for('reg'))
    else:
        new_acc = Users(username=username, password=password, name=name)
        db.session.add(new_acc)
        db.session.commit()
        flash("Account successfully created!", "info")
        return redirect(url_for('login'))
    
    

@app.route('/home')
def home():
     
    if 'user_id' in session:
        user_id = session['user_id']
        recipes = db.session.query(Recipes.recipe_id, Recipes.user_id, Recipes.name.label('recipe_name'), Recipes.ingredients, Recipes.steps, Recipes.prep_time, Users.name
        ).join(
            Users, Recipes.user_id == Users.user_id
        ).order_by(
            Recipes.recipe_id.desc()
        )
        return render_template('home.html', recipes=recipes)
    
    else:
        flash("Error! You are not logged in", "info")
        return redirect(url_for('login'))

@app.route('/recipes')
def add():
    if 'user_id' in session:
        return render_template('add_recipe.html')
    else:
        flash("Error! You are not logged in", "info")
        return redirect(url_for('login'))

@app.route('/recipes/add', methods = ["POST"])
def add_recipe():
    name = request.form["name"]
    user_id =  session.get('user_id')
    ingredients = request.form["ingredients"]
    steps = request.form["steps"]
    prep_time = request.form["prep_time"]
    
    new_recipe = Recipes(user_id=user_id, name=name, ingredients=ingredients, steps=steps, prep_time=prep_time)
    db.session.add(new_recipe)
    db.session.commit()
    
    flash("Recipe successfully added!", "info")
    return redirect(url_for('home'))

@app.route('/recipes/<int:recipe_id>')
def view(recipe_id):
    if 'user_id' in session:
        recipe = db.session.query(Recipes.recipe_id, Recipes.user_id, Recipes.name.label('recipe_name'), Recipes.ingredients, Recipes.steps, Recipes.prep_time, Users.user_id, Users.name
        ).join(
            Users, Recipes.user_id == Users.user_id
        ).filter(
            Recipes.recipe_id == recipe_id
        ).first()
        
        comments = db.session.query(Comments.comment, Users.name
        ).join(
            Users, Comments.user_id == Users.user_id
        ).filter(
            Comments.recipe_id == recipe_id
        ).all()
        
        ratings = db.session.query(Ratings.value, Users.name
        ).join(
            Users, Ratings.user_id == Users.user_id
        ).filter(
            Ratings.recipe_id == recipe_id
        ).all()

        if ratings:
            total_ratings = sum(rating.value for rating in ratings)
            average_rating = round(total_ratings / len(ratings), 2)
            
        else:
            average_rating = 0
        
        return render_template('view_recipe.html', recipe=recipe, comments=comments, ratings=ratings, average_rating=average_rating)
    else:
        flash("Error! You are not logged in", "info")
        return redirect(url_for('login'))

@app.route('/recipes/comment/<int:recipe_id>', methods = ["POST"])
def comment(recipe_id):
    user_id =  session.get('user_id')
    comment = request.form["comment"]
    
    new_comment= Comments(recipe_id=recipe_id, user_id=user_id, comment=comment)
    db.session.add(new_comment)
    db.session.commit()
    
    return redirect(request.referrer)

@app.route('/recipes/rating/<int:recipe_id>', methods = ["POST"])
def rating(recipe_id):
    user_id =  session.get('user_id')
    rating = request.form["rating"]
    existing_rate = Ratings.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
    
    if existing_rate:
        flash("You've already rated this recipe!", "info")
        return redirect(request.referrer)
    else:
        new_rating= Ratings(recipe_id=recipe_id, user_id=user_id, value=rating)
        db.session.add(new_rating)
        db.session.commit()
        
        flash("Recipe successfully rated!", "info")
        return redirect(request.referrer)
    
@app.route('/search', methods = ["POST"])
def search():
    search_value = request.form["search"]
    search_result = db.session.query(Recipes.recipe_id, Recipes.user_id, Recipes.name.label('recipe_name'), Recipes.ingredients, Recipes.steps, Recipes.prep_time, Users.name
    ).join(
        Users, Recipes.user_id == Users.user_id
    ).filter(
        or_(
        Recipes.name.ilike(f'%{search_value}%'),
        Recipes.ingredients.ilike(f'%{search_value}%'),
        Users.name.ilike(f'%{search_value}%')
        )
    ).all()
    if search_result:
        return render_template('search.html', search_results=search_result)
    else:
        flash("Search result is empty!", "info")
        return render_template('search.html')
    
@app.route('/recipe/edit/<int:recipe_id>', methods = ["PUT","GET","POST"])    
def edit(recipe_id):
    user_id = Recipes.query.filter_by(recipe_id=recipe_id).with_entities(Recipes.user_id).first()
    user_id = int(user_id[0])
    
    if (session.get('user_id') == user_id):
        if request.method == "POST":
        
            if request.form.get('_method') == 'PUT':
                update = Recipes.query.get(recipe_id)
                update.name = request.form["name"]
                update.ingredients = request.form["ingredients"]
                update.steps = request.form["steps"]
                update.prep_time = request.form["prep_time"]
                
                db.session.commit()
                flash("Recipe successfully updated!", "info")
                return redirect(request.referrer)
        
        elif request.method == "GET":
            recipe = db.session.query(Recipes.recipe_id, Recipes.name.label('recipe_name'), Recipes.ingredients, Recipes.steps, Recipes.prep_time
            ).filter(
                Recipes.recipe_id == recipe_id
            ).first()
            return render_template('edit_recipe.html', recipe=recipe)
    else:
        flash("Error! You don't have access to this recipe", "info")
        return redirect(url_for('home'))
        
        
    
@app.route('/recipe/delete/<int:recipe_id>', methods = ["POST"])    
def delete(recipe_id):
    user_id = Recipes.query.filter_by(recipe_id=recipe_id).with_entities(Recipes.user_id).first()
    user_id = int(user_id[0])
    
    if (session.get('user_id') == user_id):

        Recipes.query.filter_by(recipe_id=recipe_id).delete()
        Comments.query.filter_by(recipe_id=recipe_id).delete()
        Ratings.query.filter_by(recipe_id=recipe_id).delete()

        db.session.commit()
        flash("Recipe successfully deleted!", "info")
        return redirect(url_for('home'))
    else:
        flash("Error! You don't have access to this recipe", "info")
        return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)