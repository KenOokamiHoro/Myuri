'''connect to backend database with sqlalchemy'''
import sqlalchemy
import sqlalchemy.ext.declarative
import sqlalchemy.orm 
import datetime

class dbc:
    '''a datatbase connection.'''
    def __init__(self, uri):
        self.engine = sqlalchemy.create_engine(uri, echo=True)
        self.base = sqlalchemy.ext.declarative.declarative_base()
        self.Session = sqlalchemy.orm.sessionmaker()
        self.Session.configure(bind = self.engine)
        self.session=None
        

class ChatLogMessage(sqlalchemy.ext.declarative.declarative_base()):
    '''messages model'''
    __tablename__ = 'messages'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    time = sqlalchemy.Column(sqlalchemy.DateTime)
    channel = sqlalchemy.Column(sqlalchemy.String(64), index=True)
    nick = sqlalchemy.Column(sqlalchemy.String(64), index=True)
    messages = sqlalchemy.Column(sqlalchemy.Text())

def log_message(dbc,channel,nick,message):
    dbc.session=dbc.Session()
    log_item = ChatLogMessage(time=datetime.datetime.now(),
                              channel=channel,
                              nick=nick,
                              messages=message)
    dbc.session.add(log_item)
    dbc.session.commit()

if __name__ == "__main__":
    engine = sqlalchemy.create_engine('sqlite:///home/horo/repo/utils.yoitsu.moe/data-dev.sqlite', echo=True)
    Session.configure(bind=engine)


