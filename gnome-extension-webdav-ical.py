#!/usr/bin/python2
#
# This is an extension for Gnome3 to support remote calendars w/o evolution.
# Copyright (C) 2011 Thomas Wouters <thomas@tcpdump.be>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>
#

#================== CONFIG ================
url = 'https://server.exampe.tld/calendar.ics'
username = 'username'
passwd = 'password'

#================ END CONFIG ==============

import gtk
import dbus
import dbus.service
import dbus.mainloop.glib

from time import mktime
from pywebcal import WebCal, ICal
from datetime import datetime, timedelta
from dateutil.tz import tzical, gettz

class CalendarService(dbus.service.Object):
	busname = 'org.gnome.Shell.CalendarServer'
	object_path = '/org/gnome/Shell/CalendarServer'

	def __init__(self):
		bus = dbus.service.BusName(self.busname,
					bus=dbus.SessionBus(),
					replace_existing=True)

		super(CalendarService, self).__init__(bus, self.object_path)
 
	@dbus.service.method('org.gnome.Shell.CalendarServer',
						 in_signature='xxb', out_signature='a(sssbxxa{sv})')
	def GetEvents(self, since, until, force_reload):

		wc = WebCal(url, username, passwd)
		uids = wc.get_calendar_uids()
		
		isoformat = "%Y-%m-%dT%H:%M:%S.%f"
		
		events = []
		for uid in uids:
			cal = ICal(wc.get_calendar(uid))
		
			feed = cal.get_events()
			for event in feed:
				start_date = event.get_start_datetime()
				end_date = event.get_end_datetime()
				if ((end_date - start_date) == timedelta(1)):
					allday = True
				else:
					allday = False
				start = int(mktime(start_date.timetuple()))
				end = int(mktime(end_date.timetuple()))
				events.append((
					'',
					str(event.get_summary()),
					'',
					allday,
					start,
					end,
					{}))
		return events

if __name__ == '__main__':
	dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

	myservice = CalendarService()
	gtk.main()
