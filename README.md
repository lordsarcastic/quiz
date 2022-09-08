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
Documentation for the application is available in [JSON](https://www.getpostman.com/collections/39791e227bb260b4dcfd) and [web-based](https://documenter.getpostman.com/view/23092372/VVBXw5K5) format on Postman.

### Guide
A video containing how to use the API is listed on [Youtube](https://www.youtube.com/playlist?list=PLnrSKtGWKVktMKdsmKEUPo1rHpEbLpwJ2)

## To do
This section contains uncompleted features for the application
- Constraints on number of questions per quiz: Maximum number of questions for a quiz is meant to be 10
- Quiz taken by user: A user should be able to access the list of quizzes that they have taken and view the results
- More tests: The test section of the application is not as comprehensive and needs more work
