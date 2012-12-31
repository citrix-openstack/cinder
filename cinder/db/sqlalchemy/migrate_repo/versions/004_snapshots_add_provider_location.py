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

from sqlalchemy import Column, DateTime, Text, Boolean
from sqlalchemy import MetaData, Integer, String, Table, ForeignKey

from cinder.openstack.common import log as logging

LOG = logging.getLogger(__name__)


def upgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    snapshots = Table('snapshots', meta, autoload=True)
    provider_location = Column('provider_location', String(255))
    snapshots.create_column(provider_location)


def downgrade(migrate_engine):
    meta = MetaData()
    meta.bind = migrate_engine

    snapshots = Table('snapshots', meta, autoload=True)
    provider_location = snapshots.columns.provider_location
    provider_location.drop()
