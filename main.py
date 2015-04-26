#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2
from google.appengine.ext import db
import re
import cgi

USERNAME = "XX"

def escape_html(s):
    return cgi.escape(s, quote = True)

USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
def valid_username(username):
    return USER_RE.match(username)

EMAIL_RE = re.compile(r'^[\S]+@[\S]+\.[\S]+$')
def valid_email(email):  
    return EMAIL_RE.match(email)

PASS_RE = re.compile(r"^.{3,20}$")
def valid_pass(password):   
    return PASS_RE.match(password)


jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))

class BlogPost(db.Model):
        title = db.StringProperty(required = True)
        body = db.TextProperty(required = True)
        created = db.DateTimeProperty(auto_now_add = True)  

class User(db.Model):
        username = db.StringProperty(required = True)
        password = db.EmailProperty(required = True)
        email = db.StringProperty(required = True)
        created = db.DateTimeProperty(auto_now_add = True)      
        
class MainHandler(webapp2.RequestHandler):
    def get(self):
        maintemplate = jinja_environment.get_template('main.html')
        blogpost = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC")
        # for b in blogpost:
            # self.response.out.write(blogpost.title)
        self.response.out.write(maintemplate.render(blogpost = blogpost))
        
        
class NewPostHandler(webapp2.RequestHandler):
    def get(self):
        
        template = jinja_environment.get_template('form.html')
        self.response.out.write(template.render(error="", title="", body=""))   
        
    def post(self):
        title = ""
        body = ""
        title = self.request.get("subject") 
        body = self.request.get("content")
        template = jinja_environment.get_template('form.html')
        if title and body:
            blog= BlogPost(title = title, body = body)
            blog.put()
            self.redirect("/%d"%blog.put().id_or_name())
        else:
            error = "We Expect both things DUDE!!!!"
            self.response.out.write(template.render(error = error, title = title, body = body))

class SignupHandler(webapp2.RequestHandler):

    def get(self):
        signuptemplate = jinja_environment.get_template('signupform.html')
        self.response.out.write(signuptemplate.render(error0="", error1="",error2="",error3="",error4="" , error5="", username="",email=""))

    
    def post(self):
        usr_username = self.request.get("username")
        usr_email = self.request.get("email")
        usr_password = self.request.get("password")
        usr_verify = self.request.get("verify") 
        error0="";error1="";error2="";error3="";error4="";error5=""
        global USERNAME 
        USERNAME = usr_username 
        username = valid_username(usr_username)
        email = valid_email(usr_email)
        password = valid_pass(usr_password)
        verify = valid_pass(usr_verify)
        
        signuptemplate = jinja_environment.get_template('signupform.html')
        user = User.all()
        
        if not (username):  
            error1 = "That is not a valid username"
        if not (email):  
            error2 = "That is not a valid email"
        if not (password):
            error3 = "That is not a valid password"
        if not (verify):
            error4 = "That is not a valid verify password"
        if (usr_password != usr_verify):
            error5 = "Passwords not matching!"
        for p in user:
            if (p.username == usr_username):
                error0= "User with this username already exists!"
            
            

        self.response.out.write(signuptemplate.render(error0=error0, error1=error1,error2=error2,error3=error3,error4=error4 , error5=error5, username=escape_html(usr_username),email=escape_html(usr_email)))
        if (username and password and email and verify and usr_password==usr_verify and error0==""):
            user = User(username=usr_username, password=usr_password, email=usr_email)
            user.put()
            self.response.headers.add_header('Set-Cookie', 'userID=9769797KJJHK; Path=/')
            self.redirect("/thanks" )

class ThanksHandler(webapp2.RequestHandler):
    def get(self): 
        global USERNAME
        username = USERNAME
        thankstemplate = jinja_environment.get_template('thanks.html')
        self.response.out.write(thankstemplate.render(username=username))  
            
class PermalinkHandler(webapp2.RequestHandler):
    def get(self, path):
        uniposttemplate = jinja_environment.get_template('permalink.html')
        blogpost = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC")
        for i in blogpost:
            if int(i.key().id_or_name()) == int(self.request.path[1:]):
                self.response.out.write(uniposttemplate.render(title = i.title,body=i.body))
            
            
        
app = webapp2.WSGIApplication([
    ('/', MainHandler),('/newpost',NewPostHandler), (r'/(\d+)', PermalinkHandler) , ('/signup',SignupHandler), ('/thanks', ThanksHandler)
], debug=True)
