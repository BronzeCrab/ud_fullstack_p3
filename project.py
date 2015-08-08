from flask import Flask, render_template, url_for,\
     request, redirect, flash, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)

# For connect to google

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Item Catalog"

# Connect to db

engine = create_engine('postgresql://austinnikov:123123@localhost/mydatabase')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

# Login


@app.route('/login')
def showLogin():
    categories = session.query(Category).all()
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state, categories=categories)

# User Helper Functions


def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# Connect to google


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the\
                        authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # Checking if user is already in db:
    got_id = getUserID(data['email'])
    if not got_id:
        got_id = createUser(login_session)

    login_session['user_id'] = got_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius:\
                  150px;-webkit-border-radius: 150px;-moz-border-radius:\
                  150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    print login_session
    return output

# Disconnect from google


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = credentials
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash('Successfully disconnected.')
        return redirect(url_for('showCategories'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        flash('Failed to revoke token for given user.')
        return redirect(url_for('showCategories'))


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    print "begin connecting to fb!"
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?'\
          'grant_type=fb_exchange_token&client_id={}&client_secret={}'\
          '&fb_exchange_token={}'.format(app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.2/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.2/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    print data
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, let's strip out the information before the equals sign in our
    # token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.2/me/picture?'\
          '{}&redirect=0&height=200&width=200'.format(token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<div style="text-align:center;">'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;'\
              'border-radius: 150px;-webkit-border-radius'\
              ': 150px;-moz-border-radius: 150px;">'
    output += '</div>'
    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    # print "facebook login session"
    # print login_session
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions' % facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['facebook_id']
    flash("you have been logged out")
    return redirect(url_for('showCategories'))

# ===use jsonify to return JSON===


@app.route('/categories/JSON/')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/categories/<category_name>/JSON/')
def categoryItemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=category.id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/categories/<category_name>/<item_name>/JSON/')
def categoryItemJSON(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(
        category_id=category.id, name=item_name).one()
    return jsonify(Item=[item.serialize])

# ===use jsonify to return JSON===


@app.route('/')
@app.route('/categories/')
def showCategories():
    categories = session.query(Category).all()
    # get last 10 items
    lastItems = session.query(Item).order_by(Item.id.desc()).limit(10)
    # I should get also name of the category for current item to display
    lastItemsAndCategories = []
    for item in lastItems:
        category = session.query(Category).filter_by(id=item.category_id).one()
        lastItemsAndCategories.append(
            {"item_name": item.name, "category_name": category.name})
    # checking if user is logged in to change Login button on Logout button
    if 'username' not in login_session:
        return render_template('categories.html', categories=categories,
                               lastItemsAndCategories=lastItemsAndCategories)
    elif 'facebook_id' in login_session:
        return render_template('categories.html', categories=categories,
                               lastItemsAndCategories=lastItemsAndCategories,
                               ifLoginFb=True)
    elif 'gplus_id' in login_session:
        return render_template('categories.html', categories=categories,
                               lastItemsAndCategories=lastItemsAndCategories,
                               ifLoginGp=True)


@app.route('/categories/newCategory/', methods=['GET', 'POST'])
def newCategory():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        try:
            category = session.query(Category).filter_by(
                name=request.form['name']).one()
        except:
            # create new category if there isn't any old with this name
            newCategory = Category(name=request.form['name'],
                                   user_id=login_session['user_id'])
            session.add(newCategory)
            session.commit()
            flash("new category created!")
            return redirect(url_for('showCategories'))
        else:
            flash("category wasn't created - this name is already token!")
            return redirect(url_for('newCategory'))
    else:
        categories = session.query(Category).all()
        return render_template('newCategory.html', categories=categories)


@app.route('/categories/<category_name>/delete/', methods=['GET', 'POST'])
def deleteCategory(category_name):
    if 'username' not in login_session:
        return redirect('/login')
    # if there is no 'username' key in login_session dict:
    deleteCategory = session.query(
        Category).filter_by(name=category_name).one()
    if login_session['user_id'] == deleteCategory.user_id:
        categories = session.query(Category).all()
        print deleteCategory
        if request.method == "POST":
            session.delete(deleteCategory)
            session.commit()
            flash("category was deleted!")
            return redirect(url_for('showCategories'))
        else:
            return render_template(
                'deleteCategory.html',
                category=deleteCategory,
                categories=categories)
    else:
        flash("You can't delete another's category")
        return redirect(url_for('showCategories'))


@app.route('/categories/<category_name>/newItem/', methods=['GET', 'POST'])
@app.route('/categories/newItem/', methods=['GET', 'POST'])
def newItem(category_name=None):
    """ Create new item in any directory """
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == "POST":
        # if not category_name then get it from form
        if not category_name:
            category_name = request.form['category']
        category = session.query(Category).filter_by(name=category_name).one()
        # testing if item with this name is already in database:
        try:
            session.query(Item).filter_by(
                category_id=category.id,
                name=request.form['name']).one()
        except:
            # if there is an exception - then I didn't find any
            # Item with this name
            # and i can make new one.
            InsertToCategory = session.query(
                Category).filter_by(name=category_name).one()

            newItem = Item(name=request.form['name'],
                           description=request.form['description'],
                           category_id=InsertToCategory.id,
                           user_id=login_session['user_id'])
            session.add(newItem)
            session.commit()
            flash("category's item was created!")
        else:
            flash("you can't create item with this name,\
                   please edit existing!")
        return redirect(url_for('showCategories'))
    else:
        categories = session.query(Category).all()
        # if we got category name, then it was the first route (from some
        # category)
        if category_name:
            return render_template(
                'newItem.html',
                categories=categories,
                category_name=category_name)
        else:
            # otherwise i'll have to get category's name from the user
            return render_template('newItem.html', categories=categories)


@app.route(
    '/categories/<category_name>/<item_name>/delete/',
    methods=[
        'GET',
        'POST'])
def deleteItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    itemTodel = session.query(Item).filter_by(
        category_id=category.id, name=item_name).one()
    if login_session['user_id'] == itemTodel.user_id:
        categories = session.query(Category).all()
        if request.method == "POST":
            session.delete(itemTodel)
            session.commit()
            flash("item was deleted!")
            return redirect(url_for('showItems', category_name=category.name))
        else:
            return render_template(
                'deleteItem.html',
                category=category,
                item=itemTodel,
                categories=categories)
    else:
        flash("You can't delete another's item")
        return redirect(url_for('showItems', category_name=category.name))


@app.route(
    '/categories/<category_name>/<item_name>/edit/',
    methods=[
        'GET',
        'POST'])
def editItem(category_name, item_name):
    if 'username' not in login_session:
        return redirect('/login')
    category = session.query(Category).filter_by(name=category_name).one()
    itemToEdit = session.query(Item).filter_by(
        category_id=category.id, name=item_name).one()
    if login_session['user_id'] == itemToEdit.user_id:
        categories = session.query(Category).all()
        if request.method == "POST":
            # there two variants: category was changed or not.
            # First condider the
            # case when category wasn't changed
            if category.name == request.form['category']:
                if request.form['name']:
                    itemToEdit.name = request.form['name']
                    itemToEdit.description = request.form['description']
                else:
                    flash("item's name can't be empty")
                    return redirect(
                        url_for(
                            'editItem',
                            category_name=category.name,
                            item_name=item_namea))
            else:
                # we must change category
                # for item - just delete old item and add
                # new item to new category
                session.delete(itemToEdit)
                # figuring out category to add new Item (i must figure out
                # category's id)
                category = session.query(Category).filter_by(
                    name=request.form['category']).one()
                itemToAdd = Item(name=request.form['name'],
                                 description=request.form['description'],
                                 category_id=category.id)
                session.add(itemToAdd)
            session.commit()
            flash("item was edited!")
            return redirect(url_for('showItems', category_name=category.name))
        else:
            return render_template(
                'editItem.html',
                category=category,
                item=itemToEdit,
                categories=categories)
    else:
        flash("You can't edit this item!")
        return redirect(url_for('showItems', category_name=category.name))


@app.route('/categories/<category_name>/')
def showItems(category_name):
    categoryToShow = session.query(
        Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(category_id=categoryToShow.id).all()
    categories = session.query(Category).all()
    return render_template('items.html', items=items,
                           categories=categories,
                           amountOfItems=len(items),
                           categoryToShow=categoryToShow)


@app.route('/categories/<category_name>/<item_name>/')
def showItem(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(
        category_id=category.id, name=item_name).one()
    categories = session.query(Category).all()
    return render_template(
        'item.html',
        item=item,
        categories=categories,
        category=category)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
