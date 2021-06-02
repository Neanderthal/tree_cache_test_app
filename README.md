# Tree cache
This code contains the implementation of cache for tree and was created for demonstration purposes.
 
- To run this code you must have installed **docker** first.
Run this docker command in project main directory:
 
`docker build -t test_app . && docker run -p 8080:8080 -it test_app`
 
After that, you will have a running application on [http://localhost:8080/](http://localhost:8080/)

This code is not supposed as concurrent. So if you run it without docker make sure you don't use a server with several workers more than one (e.g. uwsgi does by default).
 
The project consists of that files:
- tree_app/\_\_init\_\_.py - flask default application constructor
- tree_app/main.py - main endpoint for browse
- tree_app/api.py - these are the numbers of API endpoints that pretendto be swagger compatible but because of the lack of time it doesn't work in full. But you still can check it here [http://localhost:8080/api/doc](http://localhost:8080/api/doclink)
- tree_app/core.py - the core python implementation of algorithms to work with trees.
 
- templates/main.html - jinja template for the main page
- templates/static/main.js - javascript code for the main page
 
Also, there are a bunch of python developing related files.

The project gets its data from the file **test.json** in the **data** folder.

If for some reason you are going to run it without docker (e.g. for debugging purposes) you better install the environment before with **pipenv** like this:
```bash
pip install pipenv
pipenv install
pipenv shell
export FLASK_APP="tree_app:create_app()"
export FLASK_ENV=development
flask run -p 8080
```