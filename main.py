#Python
import json
from uuid import UUID
from datetime import date, datetime
from typing import Optional, List




#Pydantic
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import Field


#fastapi
from fastapi import FastAPI
from fastapi import status
from fastapi import Body
from fastapi import Form, Path
from fastapi import HTTPException
from fastapi.responses import JSONResponse



app = FastAPI()

#models

class UserBase(BaseModel):
    user_id : UUID = Field(...)
    email : EmailStr = Field(...)

class UserLogin(UserBase):
    password : str = Field(
        ...,
        min_length=8,
        max_length=20
    )


class User(UserBase):
    first_name : str = Field(
        ...,
        min_length=1,
        max_length=50,
    )
    last_name : str = Field(
        ...,
        min_length=1,
        max_length=50,
    )
    birth_date : Optional[date] = Field(default=None)


class UserRegister(User):
    password : str = Field(
        ...,
        min_length=8,
        max_length=20
    )    


class Tweet(BaseModel):
    tweet_id : UUID = Field(...)
    content : str = Field(
        ...,
        min_length=1,
        max_length=250
        )
    created_at : datetime = Field(default=datetime.now())
    updated_at : Optional[datetime] = Field(default=None)
    by : User = Field(...)

class successlogin(BaseModel):
    message : str = Field(default="Login Successfully")

#Path Operations

##Users

### Register a user
@app.post(
    path="/signup",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register a user",
    tags=["Users"]
)
def signup(user : UserRegister = Body(...)):
    """
    Sign up


    This path operation register a user in the app

    Parameters:
    - Request body parameter:
        - user : UserRegister

    Returns a json with the basic user information
    - User_ id : UUID
    - Email : EmailStr
    - first_name : str
    - last_name : str
    - birth_date : date
    """

    with open("users.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        user_dict = user.dict()
        user_dict["user_id"] = str(user_dict["user_id"])
        user_dict["birth_date"] = str(user_dict["birth_date"])
        results.append(user_dict)
        f.seek(0)
        f.write(json.dumps(results))
        return user


### Login a user
@app.post(
    path="/login",
    response_model=successlogin,
    status_code=status.HTTP_200_OK,
    summary="Login a user",
    tags=["Users"]
)
def Login(
    email_authorization : EmailStr =  Form(...),
    password_authorization : str = Form(...)
    ):
    """
    Log in

    This is to Log in a user

    Parameters:
    - Request body parameter:
        - email_authorization : EmailStr 
        - password_authorization : str

    Returns a succesfully login if the user is in data base, if user is not in data base will not log in
    
    """

    with open("users.json", "r", encoding="utf-8") as f:
        authentication = json.loads(f.read())
        
        for authenticator in authentication:
            if email_authorization == authenticator["email"] and password_authorization == authenticator["password"]:
                return successlogin(email_authorization=email_authorization)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Could not be completed")
    
        
### Show all users
@app.get(
    path="/users",
    response_model=List[User],
    status_code=status.HTTP_200_OK,
    summary="Show all users",
    tags=["Users"]
)
def show_all_users():
    """
    Show all users

    This path operation shows all users in the app

    Parameters:
    - 

    Returns a json list with all users in the app with the following keys:

    - User_ id : UUID
    - Email : EmailStr
    - first_name : str
    - last_name : str
    - birth_date : date
    """

    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        return results


### Show a user
@app.get(
    path="/users/{user_name}",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Show a user",
    tags=["Users"]
)
def show_a_user(
    user_name : str = Path(...)
):
    """
    Show a user

    This is for showing an specific user

    Parameters:
    - user_name: str

    Returns the user information if it is in the data base if not will raise an error 404
    """

    
    with open("users.json","r", encoding="utf-8") as file:
        user_results = json.loads(file.read())
        
        for search_user in user_results:
            if search_user["first_name"] == user_name:
                return search_user
            elif user_name not in search_user["first_name"]:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Name not found in the data base")
                
### Delete a user        
@app.delete(
    path="/users/{user_email}/delete",
    response_model=str,
    status_code=status.HTTP_200_OK,
    summary="Delete a user",
    tags=["Users"]
)
def delete_a_user(
    user_email : EmailStr = Path(...) 
):

    """
    Delete a user

    This is for deleting a user

    Parameters:
    - user_email :  EmailStr

    Returns 
    """
    with open("users.json","r", encoding="utf-8") as file:
        user_result = json.loads(file.read())

        for search_user in user_result:
            if search_user["email"] == user_email:

                user_result.remove(search_user)

                with open("users.json","w",encoding="utf-8") as file:
                    file.seek(0)
                    file.write(json.dumps(user_result))
                return "The user deleted was {}".format(user_email)


### Update a user
@app.put(
    path="/users/{user_email}/update",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Update a user",
    tags=["Users"]
)
def update_a_user(
    user_email : EmailStr = Path(...),
    user : UserRegister = Body(...)
):
    """
    Update a user

    This is for updatind an existing user in the json data base

    Parameters:
    - user_email : EmailStr
    - user : UserRegister

    Returns the user information depending of the user email input, and in the model UserRegister will be changed
    that User information

    """

    user_email = str(user_email)
    user_dict = user.dict()
    user_dict["user_id"] = str(user_dict["user_id"])
    user_dict["email"] = str(user_dict["email"])
    user_dict["birth_date"] = str(user_dict["birth_date"])

    with open("users.json","r+",encoding="utf-8") as file:

        user_results = json.loads(file.read())

        for searching_user in user_results:

            if searching_user["email"] == user_email:
                
                #In the list to localize the user
                user_results[user_results.index(searching_user)] =user_dict 
                
                with open("users.json", "w", encoding="utf-8") as file:
                    file.seek(0)
                    file.write(json.dumps(user_results))
                return user_dict

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found in the data base")


##Tweets

### Show all tweets
@app.get(
    path="/",
    response_model=List[Tweet],
    status_code=status.HTTP_200_OK,
    summary="Show all tweets",
    tags=["Tweets"]
    )
def home():
    """
    Show all users

    This path operation shows all tweets in the app

    Parameters:
    - 

    Returns a json list with all tweets in the app with the following keys:

    - tweet_id : UUID 
    - content : str 
    - created_at : datetime 
    - updated_at : Optional[datetime]
    - by : User
    """

    with open("users.json", "r", encoding="utf-8") as f:
        results = json.loads(f.read())
        return results


### Post a tweet
@app.post(
    path="/post",
    response_model=Tweet,
    status_code=status.HTTP_201_CREATED,
    summary="Post a tweet",
    tags=["Tweets"]
)
def post_tweet(tweet: Tweet = Body(...)):
    """
    Post a tweet


    This path operation post a tweet in the app

    Parameters:
    - Request body parameter:
        - tweet : Tweet

    Returns a json with the basic tweet information

    - tweet_id : UUID 
    - content : str 
    - created_at : datetime 
    - updated_at : Optional[datetime]
    - by : User 
    """

    with open("tweets.json", "r+", encoding="utf-8") as f:
        results = json.loads(f.read())
        tweet_dict = tweet.dict()
        tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
        tweet_dict["created_at"] = str(tweet_dict["created_at"])
        tweet_dict["updated_at"] = str(tweet_dict["updated_at"])
        tweet_dict["by"]["user_id"] = str(tweet_dict["by"]["user_id"])
        tweet_dict["by"]["birth_date"] = str(tweet_dict["by"]["birth_date"])
        results.append(tweet_dict)
        f.seek(0)
        f.write(json.dumps(results))
        return tweet


### Show a tweet
@app.get(
    path="/tweets/{email_user}",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="Show a tweet",
    tags=["Tweets"]
)
def show_a_tweet(
    email_user : EmailStr = Path(...) 
):
    """
    Show a tweet

    This will show the information of a tweet

    Parameters:
    - email_user : EmailStr

    Returns the model of a tweet depending of the email typed as input
    """
    
    with open("tweets.json","r",encoding="utf-8") as file:
        tweet_results = json.loads(file.read())
        
        for searchtweet in tweet_results:
            if email_user == searchtweet["by"]["email"]:
                return searchtweet
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found in the data base")



### Delete a tweet
@app.delete(
    path="/tweets/{user_email}/delete",
    response_model=str,
    status_code=status.HTTP_200_OK,
    summary="Delete a tweet",
    tags=["Tweets"]
)
def delete_a_tweet(
    user_email : EmailStr = Path(...)
):
    """
    Delete a tweet

    This will delete a tweet through consulting the email of the user creator   

    Parameters:
    - user_email : EmailStr

    Returns the email that was attached with the tweet, if it is not found it will return a 404 error
    """
    
    with open("tweets.json","r+",encoding="utf-8") as file:
        tweet_result = json.loads(file.read())
        
        for searchtweet in tweet_result:
            if user_email == searchtweet["by"]["email"]:
                tweet_result.remove(searchtweet)

                with open("tweets.json","w",encoding="utf-8") as file:
                    file.seek(0)
                    file.write(json.dumps(tweet_result))
                return "the email deleted was {}".format(user_email)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tweet not found"
        )


### Update a tweet
@app.put(
    path="/tweets/{user_email}/update",
    response_model=Tweet,
    status_code=status.HTTP_200_OK,
    summary="update a tweet",
    tags=["Tweets"]
)
def update_a_tweet(
    user_email : EmailStr = Path(...),
    tweet : Tweet = Body(...)
):

    """
    Update a tweet

    This will update a content of a tweet

    Parameters:
    - user_email : EmailStr 
    - tweet : Tweet

    Returns the model Tweet updated only if the email introducet is in the json file 
    
    """
    user_email = str(user_email)
    tweet_dict = tweet.dict()
    tweet_dict["tweet_id"] = str(tweet_dict["tweet_id"])
    tweet_dict["created_at"] = str(tweet_dict["created_at"])
    tweet_dict["updated_at"] = str(tweet_dict["updated_at"])
    tweet_dict["by"]["user_id"] = str(tweet_dict["by"]["user_id"])
    tweet_dict["by"]["birth_date"] = str(tweet_dict["by"]["birth_date"])

    with open("tweets.json","r+",encoding="utf-8") as file:
        tweet_result = json.loads(file.read())

        for search_tweet in tweet_result:
            if search_tweet["by"]["email"] == user_email:
                tweet_result[tweet_result.index(search_tweet)] = tweet_dict

                with open("tweets.json","w",encoding="utf-8") as file:
                    file.seek(0)
                    file.write(json.dumps(tweet_result))
                return tweet_dict

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User email not found in the data base")