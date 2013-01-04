# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 OpenStack LLC.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from sqlalchemy import MetaData, Table
from migrate.changeset.constraint import ForeignKeyConstraint


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    snapshots = Table('snapshots', meta, autoload=True)
    volumes = Table('volumes', meta, autoload=True)

    ForeignKeyConstraint(
        columns=[snapshots.c.volume_id],
        refcolumns=[volumes.c.id]).create()


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    snapshots = Table('snapshots', meta, autoload=True)
    volumes = Table('volumes', meta, autoload=True)

    ForeignKeyConstraint(
        columns=[snapshots.c.volume_id],
        refcolumns=[volumes.c.id]).drop()
