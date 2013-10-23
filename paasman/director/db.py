# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""

# TODO: or use redis for all persistence instead?

#from contextlib import contextmanager

#from sqlalchemy import create_engine, MetaData
#from sqlalchemy.orm import scoped_session, sessionmaker
#from sqlalchemy.ext.declarative import declarative_base

#engine = create_engine("sqlite:///dpaasman.db")

#metadata = MetaData()
#session = scoped_session(sessionmaker(autocommit=False,
#    autoflush=False,
#    bind=engine)
#)

#Base = declarative_base(metadata=metadata)
#Base.query = session.query_property()

#@contextmanager
#def session_scope():
#    try:
#        yield session
#    except:
#        session.rollback()
#        raise
#    finally:
#        session.remove()