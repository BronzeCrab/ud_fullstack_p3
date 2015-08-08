# ud_fullstack_p3

I've decided to make a web app about different sports - my favorite are grappling and acrobatics. So there are two categories and few items inside them.

### To run my project:

1. First of all, I've decided to use postgres, so you should be able to create a postgres db on your machine. When you've done with it, please fill file `db.cfg` with postgres username, password and db name. Please fill it like this, without any quotes or whitespaces:<br>
![example db.cfg](https://cloud.githubusercontent.com/assets/5002732/9095807/056c37f4-3bc2-11e5-9d53-886951efadee.png)<br>
when you'll run `database_setup.py` will pasrse `db.cfg`. and take your data  from it.
2. When you've filled `db.cfg` with your username, pass and db name, you are ready to run `python database_setup.py`, it will create db schema - 3 tables `category`,`item` and `userinfo`.
3. Run `python lotsofitems.py` to fill the db with my data under dummy user, this user will have id=1
4. Now run `python project.py`. And check out my project. 

### Description of project:

1. I've used <a href="https://github.com/n33/skel">skel</a> to make responsive site. So I have beatiful sidebar for my categories.<br>
![view of app](https://cloud.githubusercontent.com/assets/5002732/9152037/4e7ad876-3e22-11e5-8081-bb10cdb68f81.png)<br>
2. I've added login via facebook and google and local permission system: only that user who created item and category can delete or edit items or categories.
3. One can't create two items with same names inside one category. Only user with id that match to user_id field inside the item or category table can edit or delete items.
4. I've added gifs and videos to my items. I don't know if it right desicion to load them not from db but directly from my project folder - but i do it like this, just put links inside html to my `/static/images` directory. And videos i've loaded just like links to yuotube insude `iframe` tags.
