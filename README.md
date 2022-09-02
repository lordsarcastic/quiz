# backend
A web application for creating and taking quizzes online
## How to use
### Requirements:
- Docker and Docker Compose


### Begin
#### Running the application
- Clone the repo with `git clone git@git.toptal.com:screening/Ayodeji-Adeoti.git`
- `cd` into the repo
- Duplicate the file named ".env.example", rename the new copy to ".env" within the same directory. You can edit the values there as you want save for the `POSTGRES_HOST` and `POSTGRES_PORT` which I do not recommend except you know what you are doing.
- Perform migrations with `docker-compose run web python manage.py migrate`
- Create your superuser account with `docker-compose run web python manage.py createsuperuser`. Fill in required details. Note that your password won't display on the screen. Type blindly and trust the god of Django to log it in.
- To start the server, run `docker-compose up`
- You can start making requests by visiting [http://localhost:10000](http://localhost:10000)

### Documentation
Documentation for the application is available in JSON format on [Postman](https://www.getpostman.com/collections/39791e227bb260b4dcfd)