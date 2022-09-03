
# BitCoin price back end 

Created a Python Flask app which constantly checks for Bitcoin value and emails any logged in user to their respective email every 10 mins if the Bitcoin value exceeds the user entered price.
# Steps to run app:
git clone this repo <br>
command <br>

git clone <repo_link> <br>

pip install -r requirements.txt <br>

go to directory you cloned in and run python3 app.py
<br>

run the Python app. By default it is 'localhost:5000'
use PostMan to send get and post requests. <br>

key_value = e07c9cdc-e7be-4e7e-8ba7-9c787e202292 send as query parameter for endpoints /getLogs and /getAllUsers
# Endpoints
/alerts/create (POST) : Takes a post request of json type example 
{"username":username, "email":email, "price":price}
Creates a User ORM object and adds it to the persisted sqlite database.

/alerts/delete (POST) : Takes a post with the username to delete example
{"username":<username>} deletes user from the database.


/getLogs?key=<key_value>&page=<page_num> (GET)
returns the json response paginated view of all the creations and deletions of users.

/getAllUsers?key=<key_value>&page=<page_num> (GET) 
returns paginated json response of all users and their details
<br>

returns error json response if the <key_value> doesn't match in the file.

# Bitcoin value

Bitcoin value is updated every 3 minutes and when the value increases to expected price of any user, an email is sent to the users informing the bitcoin price.
User Email is read from the persisted SQLite database. Which then uses Redis as a broker to send an email. <br>
  
  Example screenshots of endpoints
  
  ![image](https://user-images.githubusercontent.com/81566132/181879082-06435d39-fedd-4a81-a12f-e204175d0d79.png)

  ![image](https://user-images.githubusercontent.com/81566132/181879112-612fd728-197a-4138-b7b0-8b8a54b95256.png)
  
![image](https://user-images.githubusercontent.com/81566132/181879144-8321813b-9e43-47e2-a9b5-08c09fd6b6f8.png)

  ![image](https://user-images.githubusercontent.com/81566132/181879162-c9b2b502-88c8-4407-bb71-09b6924b5aa1.png)

  ![image](https://user-images.githubusercontent.com/81566132/181879346-d4e9fa09-0cf9-407c-99b1-3502387e0d17.png)
