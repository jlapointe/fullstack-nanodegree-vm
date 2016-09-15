import os

import jinja2
import webapp2
import hmac

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

# Stuff for hashed cookies

SECRET = "sekrit"   #not a secure way to store this! for tutorial only.
def hash_str(s):
    return hmac.new(SECRET, s).hexdigest()

def make_secure_val(s):
    mystr = "%s|%s" % (s, hash_str(s))
    return mystr
    
def check_secure_val(h):
    a,b = h.split('|')
    if hash_str(a) == b:
        return a
    else:
        return None

#Database model for a blog post
class BlogPost(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

#Database model for a user
class User(db.Model):
    username = db.StringProperty(required = True)
    password = db.StringProperty(required = True)
    email = db.StringProperty()

#Utility class for HTTP handlers
class Handler(webapp2.RequestHandler):
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)
	
	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)
	
	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

#HTTP handler for the front page
class FrontPageHandler(Handler):
    def render_front_page(self, message=""):
        self.render('front.htm', message=message)
        
    def get(self):
        uid_cookie_str = self.request.cookies.get('user_id')
        
        if uid_cookie_str:
            uid_cookie_val = check_secure_val(uid_cookie_str)
            if uid_cookie_val:
                u_id = int(uid_cookie_val)
                u = User.get_by_id(u_id)
                username = u.username
                message = "Welcome, %s!" % username
            else:
                self.redirect(r'/signup')
        else:
            message = "Welcome!"
        
        self.render_front_page(message)

#HTTP handler for displaying all blog posts created by a user
class BlogHandler(Handler):
    def render_blog(self):
        blog_posts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created DESC")
        self.render('blog.htm', blog_posts=blog_posts)

    def get(self):
        self.render_blog()

#HTTP handlers for creating a new blog post
class NewPostHandler(Handler):
    def render_newpost_form(self, subject="", content="", error=""):
        self.render('newpost_form.htm', subject=subject, content=content, error=error)
        
    def get(self):
        self.render_newpost_form()
        
    def post(self):
    	subject = self.request.get('subject')
    	content = self.request.get('content')
    	
        if subject and content:
            b = BlogPost(subject = subject, content = content)
            b.put()
            b_id=b.key().id()
            self.redirect('/blog/%d' % b_id)
        else:
            error = "one or more empty fields"
            self.render_newpost_form(subject, content, error)

#HTTP handler(s) for accessing a specific blog entry
class BlogPostHandler(Handler):
    def render_blog_post(self, entry_id):
        blog_post = BlogPost.get_by_id(entry_id)
        self.render('blog_post.htm', blog_post=blog_post)
        
    def get(self, entry_id):
        self.render_blog_post(int(entry_id))  

#HTTP handlers for registering a new user
class SignupHandler(Handler):
    def render_signup_form(self, username="", email="", error=""):
        self.render('signup_form.htm', username=username, email=email, error=error)

    def get(self, username="", email="", error=""):
        self.render_signup_form(username=username, email=email, error=error) 
        
    def post(self):    #TODO: form validation
        username = self.request.get('username')
        password = self.request.get('password')
        verify = self.request.get('verify')
        email = self.request.get('email')
        
        if username and password and verify:
            if password == verify:
                #Store user in database
                u = User(username=username, password=password, email=email)
                u.put()
                u_id=u.key().id()
                
                #Create and store cookie for user id
                uid_cookie_val = make_secure_val(str(u_id))
                self.response.headers.add_header('Set-Cookie', 'user_id=%s; Path=/' % uid_cookie_val)
                self.redirect(r'/')
                return
            else:
                error = "password fields didn't match"
        else:
            error = "please complete all required fields"
        
        self.render_signup_form(username=username, email=email, error=error)
                

app = webapp2.WSGIApplication([
    (r'/', FrontPageHandler),
    (r'/newpost', NewPostHandler),
    (r'/signup', SignupHandler),
    (r'/blog', BlogHandler),
    (r'/blog/(\d+)', BlogPostHandler)
], debug=True)