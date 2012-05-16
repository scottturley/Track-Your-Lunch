import datetime

from google.appengine.ext import db

class Restaurant(db.Model):
   name = db.StringProperty(required=True)

class Person(db.Model):
   name = db.StringProperty(required=True)

class LunchAmount(db.Model):
   amount_paid = db.IntegerProperty()
   amount_owed = db.IntegerProperty()
   person_owed = db.ReferenceProperty(reference_class=Person)

class Lunch(db.Model):
   """Models the actual lunch event."""
   lunch_name   = db.StringProperty(required=True)
   restaurant   = db.ReferenceProperty(reference_class=Restaurant)
   total_cost   = db.IntegerProperty()
   lunch_date   = db.DateTimeProperty(auto_now=True)
   
class LunchParticipant(db.Model):
   """Models the participants who ate lunch together."""
   lunch       = db.ReferenceProperty(reference_class=Lunch)
   the_person  = db.ReferenceProperty(reference_class=Person)
   amounts     = db.ReferenceProperty(reference_class=LunchAmount)

