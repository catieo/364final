# SI 364 Final Project: A Music Discovery App 
Catie Olson 
<br>
### Brief Description: 
This application will provide music recommendations to the user via the Spotify API based on criteria that they enter in a form.  Users can register for an account and log in.  Registered users can select which of these song recommendations he or she likes and save them in playlists.  The user can view, update, or delete any playlists they have created.  Users cannot see playlists created by other users. Any user (even if not logged in) can also view all songs and artists that have been suggested to previous users.  Users can also see all songs that have been suggested organized by artist.

### Additional Models:
There are no additional models to install, but you must have a Spotify account to request an access token (see below). 

### How to use: 
* IMPORTANT FIRST STEP: Go to [https://beta.developer.spotify.com/console/get-recommendations/] and scroll to the bottom of the page. Click 'Get token'. Press 'OK'. Copy the OAuth Token and paste it into spotify_info_template.py where specified. Tokens expire after a few hours, so repeat this step as necessary to run! You must have a Spotify account to request this token.
* On the home page of the app, you will be asked if you would like song recommendations based on an artist or a genre. You must enter the word "artist" or the word "genre" and will be taken to the corresponding entry form.  
* On the next page, if you chose "artist", you should enter a correct spelling of the name of any musical artist you like. If you chose "genre", you should enter a correct spelling of any musical genre you like. 
* To see a list of all songs that have been suggested by the app from all previous searches, click the link in the navigation for "See all songs". 
* To see a list of all artists whose songs have been suggested by the app from all previous searchs, click the link in the navigation for "See all artists". On this page, you can click on the name of the artist to see the names of their songs that are saved. 
* To create a playlist, you must be logged in. Click the link in the navigation for "Create a new playlist". On this page, you should enter the desired name of your playlist. You cannot name a new playlist the same name as one that already exists.  To choose multiple songs from the list of options, hold the command key on Mac (control on PC) and click the names of the songs you'd like to add to the playlist. 
* To see all of your playlists, click the link in the navigation for "See all playlists". On this page, you have the options of viewing the songs on each playlist, updating the name of each playlist, or deleting each playlist. To view the songs on each playlist, simply click on the name of the playlist. To update the name of the playlist, click the "Update" button and enter the new name in the form that follows.  To delete the playlist, simply click the "Delete" button.  

### List of routes: 
* `/login` -> `login.html`
* `/logout` -> logs out the current user 
* `/register` -> `register.html`
* `/` -> `index.html`
* `/artist_search` -> `artist_search.html` and `search_results.html`
* `/genre_search` -> `genre_search.html` and `search_results.html`
* `/all_songs` -> `all_songs.html`
* `/all_artists` -> `all_artists.html`
* `/artist_songs/<artist_name>` -> `artist_songs.html`
* `/create_playlist` -> `create_playlist.html`
* `/all_playlists` -> `all_playlists.html`
* `/playlist/<id_num>` -> `playlist.html`
* `/update_playlist/<playlist_name>` -> `update_playlist.html`
* `/delete_playlist/<playlist_name>` -> deletes the playlist and redirects to `/all_playlists`

### Code Requirements:
* **Ensure that your SI364final.py file has all the setup (app.config values, import statements, code to run the app if that file is run, etc) necessary to run the Flask application, and the application runs correctly on http://localhost:5000 (and the other routes you set up). Your main file must be called SI364final.py, but of course you may include other files if you need.**
* **A user should be able to load http://localhost:5000 and see the first page they ought to see on the application.**

* **Include navigation in base.html with links (using a href tags) that lead to every other page in the application that a user should be able to click on.**

* **Ensure that all templates in the application inherit (using template inheritance, with extends) from base.html and include at least one additional block.**

* **Must use user authentication (which should be based on the code you were provided to do this e.g. in HW4).**

* **Must have data associated with a user and at least 2 routes besides logout that can only be seen by logged-in users.**

* **At least 3 model classes besides the User class.**

* **At least one one:many relationship that works properly built between 2 models.**

* **At least one many:many relationship that works properly built between 2 models.**

* **Successfully save data to each table.**

* **Successfully query data from each of your models (so query at least one column, or all data, from every database table you have a model for) and use it to effect in the application (e.g. won't count if you make a query that has no effect on what you see, what is saved, or anything that happens in the app).**

* **At least one query of data using an .all() method and send the results of that query to a template.**

* **At least one query of data using a .filter_by(... and show the results of that query directly (e.g. by sending the results to a template) or indirectly (e.g. using the results of the query to make a request to an API or save other data to a table).**

* **At least one helper function that is not a get_or_create function should be defined and invoked in the application.**

* **At least two get_or_create functions should be defined and invoked in the application (such that information can be saved without being duplicated / encountering errors).** 

* **At least one error handler for a 404 error and a corresponding template.**

* **At least one error handler for any other error (pick one -- 500? 403?) and a corresponding template.**

* **Include at least 4 template .html files in addition to the error handling template files.**

* **At least one Jinja template for loop and at least two Jinja template conditionals should occur amongst the templates.**

* **At least one request to a REST API that is based on data submitted in a WTForm OR data accessed in another way online (e.g. scraping with BeautifulSoup that does accord with other involved sites' Terms of Service, etc).**

* **Your application should use data from a REST API or other source such that the application processes the data in some way and saves some information that came from the source to the database (in some way).** 

At least one WTForm that sends data with a GET request to a new page.

* **At least one WTForm that sends data with a POST request to the same page. (NOT counting the login or registration forms provided for you in class.)**

* **At least one WTForm that sends data with a POST request to a new page. (NOT counting the login or registration forms provided for you in class.)**

* **At least two custom validators for a field in a WTForm, NOT counting the custom validators included in the log in/auth code.**

* **Include at least one way to update items saved in the database in the application (like in HW5).**

* **Include at least one way to delete items saved in the database in the application (also like in HW5).**

* **Include at least one use of redirect.**

* **Include at least two uses of url_for. (HINT: Likely you'll need to use this several times, really.)**

* **Have at least 5 view functions that are not included with the code we have provided. (But you may have more! Make sure you include ALL view functions in the app in the documentation and navigation as instructed above.)** 

### Additional Requirements for Extra Points: 

* (100 points) Include a use of an AJAX request in your application that accesses and displays useful (for use of your application) data.
* **(100 points) Create, run, and commit at least one migration.**
* (100 points) Include file upload in your application and save/use the results of the file. (We did not explicitly learn this in class, but there is information available about it both online and in the Grinberg book.)
* **(100 points) Deploy the application to the internet (Heroku) — only counts if it is up when we grade / you can show proof it is up at a URL and tell us what the URL is in the README. (Heroku deployment as we taught you is 100% free so this will not cost anything.)**
* (100 points) Implement user sign-in with OAuth (from any other service), and include that you need a specific-service account in the README, in the same section as the list of modules that must be installed.

