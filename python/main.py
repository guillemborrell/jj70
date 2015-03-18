import webapp2
import jinja2
import os
import gdbm
import json
import random
import string
import time
import sha
from webapp2_extras import sessions

COST=150
ACCOMPANYING_COST=100

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class LoginHandler(webapp2.RequestHandler):
    def get(self):
        template_values = {}
        if self.request.get('error'):
            if self.request.get('error') == 'userexists':
                template_values['error'] = 'This user is already registered'
            if self.request.get('error') == 'security':
                template_values['error'] = 'Wrong answer to the antispam question'

        template = JINJA_ENVIRONMENT.get_template('login.html')
        self.response.write(template.render(template_values))

    def post(self):
        username = self.request.get('username')
        password = self.request.get('password')
        try:
            database = gdbm.open('database.gdbm','cf')
        except:
            time.sleep(0.1)
            database = gdbm.open('database.gdbm','cf')    

        if ('usr'+username).encode('ascii','ignore') in database:
            auth_info = json.loads(
                database[('usr'+username).encode('ascii','ignore')]
            )
            if auth_info['password'] == password:
                session_store = sessions.get_store(request=self.request)
                session = session_store.get_session()
                session['key'] = auth_info['key']
                session['username'] = username
                session_store.save_sessions(self.response)
                database.close()
                self.redirect('/jj70/abstracts')

            else:
                database.close()
                self.redirect('/jj70/login')
            
        else:
            database.close()
            self.redirect('/jj70/login')

        
class SignupHandler(webapp2.RequestHandler):
    def post(self):
        username = self.request.get('username')
        email = self.request.get('email')
        firstname = self.request.get('firstname')
        lastname = self.request.get('lastname')
        password = self.request.get('password')
        safety = self.request.get('icode')
        try:
            database = gdbm.open('database.gdbm','cf')
        except:
            time.sleep(1.0)
            database = gdbm.open('database.gdbm','cf')    


        if safety=='Salamanca' or safety=='salamanca':
            if 'usr'+username.encode('ascii','ignore') in database:
                database.close()
                self.redirect('/jj70/login?error=userexists')

            else:
                randstring = ''.join(
                    [random.choice(
                        string.ascii_letters + string.digits
                    ) for n in xrange(32)])
                auth_info = {'password':password,
                             'email':email,
                             'firstname':firstname,
                             'lastname':lastname,
                             'key':randstring}
                
                database[('usr'+username).encode('ascii','ignore')] = json.dumps(auth_info)
                session_store = sessions.get_store(request=self.request)
                session = session_store.get_session()
                session['key'] = randstring
                session['username'] = username
                session_store.save_sessions(self.response)
                database.close()
                self.redirect('/jj70/abstracts')

        else:
            database.close()
            self.redirect('/jj70/login?error=security')
            

class AbstractsHandler(webapp2.RequestHandler):
    def get(self):
        session_store = sessions.get_store(request=self.request)
        session = session_store.get_session()
        username = session.get('username')
        key = session.get('key')
        try:
            database = gdbm.open('database.gdbm','cf')
        except:
            time.sleep(1.0)
            database = gdbm.open('database.gdbm','cf')    

        if username:
            if ('usr'+username).encode('ascii','ignore') in database:
                auth_info = json.loads(
                    database[('usr'+username).encode('ascii','ignore')]
                )
    
                if auth_info['key'] == key:
                    template_values = {'auth':auth_info}
    
                    if 'abstract'+key.encode('ascii','ignore') in database:
                        abstract_info = json.loads(
                            database['abstract'+key.encode('ascii','ignore')]
                        )
                        abstract_info['text'] = abstract_info['text'].replace('\n','<br/>')
                        template_values['abstract_info'] = abstract_info
    
                    template = JINJA_ENVIRONMENT.get_template('abstracts.html')
                    database.close()
                    self.response.write(template.render(template_values))
                    
    
                else:
                    database.close()
                    self.redirect('/jj70/login')
                    
            else:
                database.close()
                self.redirect('/jj70/login')
    
        else:
            database.close()
            self.redirect('/jj70/login')

    def post(self):
        self.redirect('/jj70/abstracts')
            

class RegistrationHandler(webapp2.RequestHandler):
    def get(self):
        secret = 'qwertyasdf0123456789'
        regURL = 'http://torroja.dmt.upm.es/jj70/registration'
        okURL = 'http://torroja.dmt.upm.es/jj70/registration_successful'
        koURL = 'http://torroja.dmt.upm.es/jj70/registration_unsuccessful'
        order = ''.join(str(random.randint(0,9)) for _ in xrange(12))
        code = 334110855
        session_store = sessions.get_store(request=self.request)
        session = session_store.get_session()
        username = session.get('username')
        attendant = self.request.get('attendant')
        accompanying = self.request.get('accompanying')
        if accompanying == 'yes':
            cost = (COST + ACCOMPANYING_COST)*100
        else:
            cost = (COST)*100

        signature = sha.new(str(cost)+order+str(code)+'978'+'0'+regURL+secret)

        key = session.get('key')
        try:
            database = gdbm.open('database.gdbm','cf')
        except:
            time.sleep(1.0)
            database = gdbm.open('database.gdbm','cf')    

        if username:
            if ('usr'+username).encode('ascii','ignore') in database:
                auth_info = json.loads(
                    database[('usr'+username).encode('ascii','ignore')]
                )
    
                if auth_info['key'] == key:
                    registration = {'amount':cost,
                                    'accompanying':accompanying,
                                    'attendant':attendant,
                                    'order': order,
                                    'code':code,
                                    'URL':regURL,
                                    'URLOK':okURL,
                                    'URLKO':koURL,
                                    'terminal':1,
                                    'currency':978,
                                    'signature':signature.hexdigest()}
                    template_values = {'auth':auth_info,
                                       'registration':registration}    
                    template = JINJA_ENVIRONMENT.get_template('registration.html')
                    database.close()
                    self.response.write(template.render(template_values))
                    
    
                else:
                    database.close()
                    self.redirect('/jj70/login')
                    
            else:
                database.close()
                self.redirect('/jj70/login')
    
        else:
            database.close()
            self.redirect('/jj70/login')

    def post(self):
        self.redirect('/jj70/abstracts')


class OKHandler(webapp2.RequestHandler):
    def get(self):
        session_store = sessions.get_store(request=self.request)
        session = session_store.get_session()
        username = session.get('username')
        key = session.get('key')
        try:
            database = gdbm.open('database.gdbm','cf')
        except:
            time.sleep(1.0)
            database = gdbm.open('database.gdbm','cf')    

        if username:
            if ('usr'+username).encode('ascii','ignore') in database:
                auth_info = json.loads(
                    database[('usr'+username).encode('ascii','ignore')]
                )
    
                if auth_info['key'] == key:
                    template_values = {'auth':auth_info}    
                    template = JINJA_ENVIRONMENT.get_template('ok.html')
                    database.close()
                    self.response.write(template.render(template_values))
                    
    
                else:
                    database.close()
                    self.redirect('/jj70/login')
                    
            else:
                database.close()
                self.redirect('/jj70/login')
    
        else:
            database.close()
            self.redirect('/jj70/login')

    def post(self):
        self.redirect('/jj70/abstracts')


class KOHandler(webapp2.RequestHandler):
    def get(self):
        session_store = sessions.get_store(request=self.request)
        session = session_store.get_session()
        username = session.get('username')
        key = session.get('key')
        try:
            database = gdbm.open('database.gdbm','cf')
        except:
            time.sleep(1.0)
            database = gdbm.open('database.gdbm','cf')    

        if username:
            if ('usr'+username).encode('ascii','ignore') in database:
                auth_info = json.loads(
                    database[('usr'+username).encode('ascii','ignore')]
                )
    
                if auth_info['key'] == key:
                    template_values = {'auth':auth_info}    
                    template = JINJA_ENVIRONMENT.get_template('ko.html')
                    database.close()
                    self.response.write(template.render(template_values))
                    
    
                else:
                    database.close()
                    self.redirect('/jj70/login')
                    
            else:
                database.close()
                self.redirect('/jj70/login')
    
        else:
            database.close()
            self.redirect('/jj70/login')

    def post(self):
        self.redirect('/jj70/abstracts')



class AbstractResource(webapp2.RequestHandler):
    def get(self):
        session_store = sessions.get_store(request=self.request)
        session = session_store.get_session()
        username = session.get('username')
        key = session.get('key')
        try:
            database = gdbm.open('database.gdbm','cf')
        except:
            time.sleep(1.0)
            database = gdbm.open('database.gdbm','cf')    

        if 'abstract'+key.encode('ascii','ignore') in database:
            abstract = database['abstract'+key.encode('ascii','ignore')]
            database.close()
            self.response.out.headers['Content-Type'] = 'application/json'
            self.response.out.write(abstract)

        else:
            database.close()
            self.abort(404)
        
    def post(self):
        try:
            database = gdbm.open('database.gdbm','cf')
        except:
            time.sleep(1.0)
            database = gdbm.open('database.gdbm','cf')    

        session_store = sessions.get_store(request=self.request)
        session = session_store.get_session()
        username = session.get('username')
        key = session.get('key')
        database['abstract'+key.encode('ascii','ignore')] = self.request.body
        database.close()


routes = [
    (r'/jj70/login', LoginHandler),
    (r'/jj70/abstracts', AbstractsHandler),
    (r'/jj70/signup', SignupHandler),
    (r'/jj70/registration', RegistrationHandler),
    (r'/jj70/registration_successful', OKHandler),
    (r'/jj70/registration_unsuccessful', KOHandler),
    (r'/jj70/abstractresource', AbstractResource),
]


config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'WEReBjJZn8BHmQzKyFwci5A9fOzEWV16',
}

application = webapp2.WSGIApplication(routes=routes, debug=True, config=config)

