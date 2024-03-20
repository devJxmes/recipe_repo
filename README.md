Created by: devillaJA

A Small Recipe App
Functions:
Login
Register
Add, Edit and Delete Recipe
Search using Recipe Name, Creator Name and Ingredient
Recipes are user specific
Comments and Rating are also user specific.


Note: Due to the complexity of setting up SQL Server containers in Docker, I opted not to use Docker. I also included the failed Docker files and Docker Compose. If you are unable to set up the app locally, I have also included screenshots.

Setting up:
Database
1. Open SSMS
2. Create a server instance named localhost
3. Import recipe_db.bak to restore the database
4. Check if recipe_db appears under the Database.
5. If its there you're done!

Flask
1. Install all the necessary dependencies included in the Requirements.txt using pip
2. Open a terminal and activate the env in env/Scripts/activate.bat
3. Once you see (env) at the beginning of the directory, you're done!
4. Enter flask run
