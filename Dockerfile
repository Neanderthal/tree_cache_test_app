FROM python:3.8
WORKDIR /app
RUN pip install pipenv

ADD ./tree_app ./tree_app \
    ./data ./data \
    app.ini ./ \
    Pipfile.lock ./ \
    Pipfile ./ 
    
RUN pipenv install --system
 
EXPOSE 8080
CMD ["uwsgi", "app.ini"]
