# -*- coding: utf-8 -*-
"""
    authors
    =======
    mikhln-9
    sanpet-8
"""

# TODO: models

import sqlalchemy as sa
from paasman.director.db import Base

class Application(Base): # change to Base
    __tablename__ = "applications"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String, index=True)
    status = sa.Column(sa.Enum("deployed", "undeployed", name="deployed_status"), nullable=False)
    # TODO: add auto-scaling, #processes, #instances etc

#class Node(Base):
#    __tablename__ = "nodes"
#
#    id = sa.Column(sa.Integer, primary_key=True)
#    name = sa.Column(sa.String, unique=True)
#    private_ip = sa.Column(sa.String, nullable=False, unique=True) # or?