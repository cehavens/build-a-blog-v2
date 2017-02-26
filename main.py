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

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)

class Posts(db.Model):
    title = db.StringProperty(required = True)
    body = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class MainPage(Handler):
    def get(self):
        self.render("front.html")

class NewPost(Handler):
    def render_new(self, title="", body="", error=""):

        self.render("newpost.html", title=title, body=body, error=error)

    def get(self):
        self.render_new()

    def post(self):
        title = self.request.get("title")
        body = self.request.get("body")

        if title and body:
            a = Posts(title = title, body = body)
            a.put()

            self.redirect("/blog/"+str(a.key().id()))
        else:
            error = "we need both a title and a body"
            self.render_new(title, body, error)

class Blog(Handler):
    def render_blog(self, title="", body="", error=""):
        posts = db.GqlQuery("SELECT * FROM Posts ORDER BY created DESC LIMIT 5")

        self.render("blog.html", title=title, body=body, posts=posts)

    def get(self):
        self.render_blog()

class ViewPostHandler(Handler):
    def render_blog(self, title="", body="", error=""):
        posts = db.GqlQuery("SELECT * FROM Posts ORDER BY created DESC LIMIT 5")

        self.render("blog.html", title=title, body=body, posts=posts)

    def get(self, id):
        post = Posts.get_by_id(int(id))

        if post:
            self.render("singlepost.html",post=post)
        else:
            error = "There is no post with that ID"
            self.render("singlepost.html", post=post, error=error)



app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    ('/blog', Blog),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
