import os
from lunch_db import *
import urllib
import datetime
import shlex
import logging

from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

def lunchdate_key(lunchdate_name=None):
   """Constructs a datastore key for a lunch date entity."""
   return db.Key.from_path('Lunch', lunchdate_name or 'default_lunchdate')

class SuccessPage(webapp.RequestHandler):
   def get(self):
      template_values = {}
      path = os.path.join(os.path.dirname(__file__), 'success.html')
      self.response.out.write(template.render(path, template_values))

class MainPage(webapp.RequestHandler):
   def get(self):
      template_values = {}

      path = os.path.join(os.path.dirname(__file__), 'index.html')
      self.response.out.write(template.render(path, template_values))

class NewLunch(webapp.RequestHandler):
   def get(self):

      all_people = Person.all()

      people = []

      for person in all_people:
         people.append(person.name)

      template_values = {
          'people': people
      }

      path = os.path.join(os.path.dirname(__file__), 'NewLunch.html')
      self.response.out.write(template.render(path, template_values))


def urldecode(query):
   d = {}
   a = query.split('&')
   for s in a:
      if s.find('='):
         k,v = map(urllib.unquote, s.split('='))
         v = v.replace('+', ' ')

         try:
            d[k] = v
         except KeyError:
            d[k] = v
   return d 

class PayerPage(webapp.RequestHandler):
   def get(self):
      params = urldecode(self.request.query_string)

      restaurant_name      = params['restaurant']
      new_participants_str = params['new_participants']
      participants_str     = params['participants']
      total_amount         = 100 * int(params['total_amount'])

      lunchdate_name   = str(restaurant_name) + '_' + str(datetime.datetime.now()) 

      participants = []

      if new_participants_str != "":
         participants     = new_participants_str.split(', ')

      if participants_str != "":
         participants.append(participants_str)

      lunch_date        = Lunch(lunch_name=lunchdate_name, total_cost=total_amount)
      lunch_participant = LunchParticipant()
      restaurant        = Restaurant(name=restaurant_name)

      lunch_date.restaurant = restaurant.put()
      lunch_amount = LunchAmount(amount_paid = 0, amount_owed = 0)

      for participant in participants:
         logging.info('participant = %s', participant)

         person_db = Person(name=participant)
 
         check_person = Person.all(keys_only=True).filter('name =', participant).get()

         if not check_person:
            person_db.put()
         else:
            person_db = check_person

         lunch_participant         = LunchParticipant(the_person=person_db)
         lunch_participant.lunch   = lunch_date.put()
         lunch_participant.amounts = lunch_amount.put()
         lunch_participant.put()

      amount_owed =  int(params['total_amount'])/(len(participants))

      template_values = {
         'people':  participants,
         'total_amount': total_amount,
         'lunch_date': lunchdate_name,
         'amount_owed': amount_owed,
      }
      path = os.path.join(os.path.dirname(__file__), 'Payers.html')
      self.response.out.write(template.render(path, template_values))


class PayerAdd(webapp.RequestHandler):
   def get(self):
      params = urldecode(self.request.query_string)

      payer            = params['payer']
      amount           = 100*int(params['amount'])
      lunch_date       = params['lunch_date_name']
      each_amount_owed = 100*int(params['amount_owed'])

      this_lunch         = Lunch.all().filter('lunch_name =', lunch_date).get()
      lunch_participants = LunchParticipant.all().filter('lunch =', this_lunch)
      
      for person in lunch_participants:
         if person.the_person.name == payer:
              lunch_amount   = LunchAmount(amount_paid = amount)
              lunch_amount.put()
              person.amounts = lunch_amount
              person.put()
         else:
              this_person_owed = Person.all().filter('name =', payer).get()
              lunch_amount = LunchAmount(amount_owed = each_amount_owed, person_owed = this_person_owed)
              lunch_amount.put()
              person.amounts   = lunch_amount
              person.put()

      template_values = {
      }

      self.redirect('/success?' + urllib.urlencode(template_values))


class NewPayer(webapp.RequestHandler):
   def post(self):
      amount       = self.request.get("Amount1")
      amount_owed  = self.request.get("amount_owed")
      payer        = self.request.get("payer")
      lunch_date   = self.request.get("lunch_date_name")

      template_values = {
         'payer':           payer,
         'amount':          amount,
         'lunch_date_name': lunch_date,
         'amount_owed':     amount_owed,
      }

      self.redirect('/add_payer?' + urllib.urlencode(template_values))

class LunchPage(webapp.RequestHandler):
   def post(self):
      restaurant       = self.request.get("restaurant")
      new_participants = self.request.get("new_participants")
      participants     = self.request.get("participants")
      total_amount     = self.request.get("amount")

      for participant in participants:
         logging.info('participant 1 = %s', participant)

      template_values = {
         'restaurant':       restaurant,
         'new_participants': new_participants,
         'participants':     participants,
         'total_amount':     total_amount,
      }

      self.redirect('/get_payer?' + urllib.urlencode(template_values))
	

application = webapp.WSGIApplication([('/', MainPage),
                                      ('/get_payer', PayerPage),
                                      ('/add_payer', PayerAdd),
                                      ('/submit_lunch', LunchPage),
                                      ('/submit_payer', NewPayer),
                                      ('/NewLunch', NewLunch),
                                      ('/success', SuccessPage)],
                                      debug=True)

def main():
   run_wsgi_app(application)

if __name__ == "__main__":
   main()
