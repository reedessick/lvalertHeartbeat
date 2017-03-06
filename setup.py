#!/usr/bin/env python

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup

setup(
    name='lvalertHeartbeat',
    version='1.0',
    description='a monitor to ensure lvalert listeners are responding to alerts',
    author='Reed Essick',
    author_email='reed.essick@ligo.org',
    license='GNU General Public License Version 3',
    packages=[
        'lvalertHeartbeat', 
    ],
    scripts=[
        'bin/lvalert_heartbeat-client',
        'bin/lvalert_heartbeat-server',
    ],
    data_files=[('etc',[]),],
    install_requires=['lvalert'],
)
