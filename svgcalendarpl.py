#!/usr/bin/env python
'''
plcalendar.py
A calendar generator plugin for Inkscape, but also can be used as a standalone
command line application.

Copyright (C) 2016 Marek Nowaczyk <marekn.home(a)gmail.com>
- based on Aurelio A. Heckert <aurium(a)gmail.com> calendar.py Inkscape plugin

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
'''

__version__ = "1.0"

import inkex, simplestyle, re, calendar
from datetime import *
from plcalendar import get_holidays
from dateutil import parser

class SVGCalendar (inkex.Effect):

    def __init__(self):
        inkex.Effect.__init__(self)
        self.OptionParser.add_option("--tab",
          action="store", type="string",
          dest="tab")
        self.OptionParser.add_option("--month",
          action="store", type="int",
          dest="month", default=0,
          help="Month to be generated. If 0, then the entry year will be generated.")
        self.OptionParser.add_option("--year",
          action="store", type="int",
          dest="year", default=0,
          help="Year to be generated. If 0, then the current year will be generated.")
        self.OptionParser.add_option("--fill-empty-day-boxes",
          action="store", type="inkbool",
          dest="fill_edb", default=True,
          help="Fill empty day boxes with next month days.")
        self.OptionParser.add_option("--start-day",
          action="store", type="string",
          dest="start_day", default="mon",
          help='Week start day. ("sun" or "mon")')
        self.OptionParser.add_option("--weekend",
          action="store", type="string",
          dest="weekend", default="sat+sun",
          help='Define the weekend days. ("sat+sun" or "sat" or "sun")')
        self.OptionParser.add_option("--auto-organize",
          action="store", type="inkbool",
          dest="auto_organize", default=True,
          help='Automatically set the size and positions.')
        self.OptionParser.add_option("--months-per-line",
          action="store", type="int",
          dest="months_per_line", default=3,
          help='Number of months side by side.')
        self.OptionParser.add_option("--month-width",
          action="store", type="string",
          dest="month_width", default="6cm",
          help='The width of the month days box.')
        self.OptionParser.add_option("--month-margin",
          action="store", type="string",
          dest="month_margin", default="1cm",
          help='The space between the month boxes.')
        self.OptionParser.add_option("--color-year",
          action="store", type="string",
          dest="color_year", default="#888",
          help='Color for thAurelio A. Heckert <aurium(a)gmail.com> e year header.')
        self.OptionParser.add_option("--color-month",
          action="store", type="string",
          dest="color_month", default="#666",
          help='Color for the month name header.')
        self.OptionParser.add_option("--color-day-name",
          action="store", type="string",
          dest="color_day_name", default="#999",
          help='Color for the week day names header.')
        self.OptionParser.add_option("--color-day",
          action="store", type="string",
          dest="color_day", default="#000",
          help='Color for the common day box.')
        self.OptionParser.add_option("--color-other-holiday",
                dest="color_other_holiday", default="#FF6060",
                help='Kolor innego swieta lub urodzin.'),
        self.OptionParser.add_option("--color-weekend",
          action="store", type="string",
          dest="color_weekend", default="#777",
          help='Color for the weekend days.')
        self.OptionParser.add_option("--color-nmd",
          action="store", type="string",
          dest="color_nmd", default="#BBB",
          help='Color for the next month day, in enpty day boxes.')
        self.OptionParser.add_option("--font-month",
          action="store", type="string",
          dest="font_month", default="Arial Black",
          help='Font for months.')
        self.OptionParser.add_option("--font-day",
          action="store", type="string",
          dest="font_day", default="Arial",
          help='Font for days.')
        self.OptionParser.add_option("--month-names",
          action="store", type="string",
          dest="month_names", default='January February March April May June '+\
                              'July August September October November December',
          help='The month names for localization.')
        self.OptionParser.add_option("--day-names",
          action="store", type="string",
          dest="day_names", default='Sun Mon Tue Wed Thu Fri Sat',
          help='The week day names for localization.')
        self.OptionParser.add_option("--encoding",
          action="store", type="string",
          dest="input_encode", default='utf-8',
          help='The input encoding of the names.')
        self.OptionParser.add_option("--other-holidays",
            action="store", type="string", 
            dest="other_holidays", default="",
            help="List of dates of custom holidays special days"
                )

    def validate_options(self):
        #inkex.errormsg( self.options.input_encode )
        # Convert string names lists in real lists:
        m = re.match( '\s*(.*[^\s])\s*', self.options.month_names )
        self.options.month_names = re.split( '\s+', m.group(1) )
        m = re.match( '\s*(.*[^\s])\s*', self.options.day_names )
        self.options.day_names = re.split( '\s+', m.group(1) )
        # Validate names lists:
        if len(self.options.month_names) != 12:
          inkex.errormsg('The month name list "'+
                         str(self.options.month_names)+
                         '" is invalid. Using default.')
          self.options.month_names = ['January','February','March',
                                      'April',  'May',     'June',
                                      'July',   'August',  'September',
                                      'October','November','December']
        if len(self.options.day_names) != 7:
          inkex.errormsg('The day name list "'+
                         str(self.options.day_names)+
                         '" is invalid. Using default.')
          self.options.day_names = ['Sun','Mon','Tue','Wed','Thu','Fri','Sat']
        # Convert year 0 to current year:
        if self.options.year == 0: self.options.year = datetime.today().year
        # Set the calendar start day:
        if self.options.start_day=='sun':
          calendar.setfirstweekday(6)
        else:
          calendar.setfirstweekday(0)
        # Convert string numbers with unit to user space float numbers:
        self.options.month_width  = inkex.unittouu( self.options.month_width )
        self.options.month_margin = inkex.unittouu( self.options.month_margin )

        self.other_holidays = [parser.parse(d).date() for d in re.split("[ \t,]+", self.options.other_holidays)]
        

    # initial values:
    month_x_pos = 0
    month_y_pos = 0

    def calculate_size_and_positions(self):
        #month_margin month_width months_per_line auto_organize
        self.doc_w = inkex.unittouu(self.document.getroot().get('width'))
        self.doc_h = inkex.unittouu(self.document.getroot().get('height'))
        if self.options.auto_organize:
          if self.doc_h > self.doc_w:
            self.months_per_line = 3
          else:
            self.months_per_line = 4
        else:
          self.months_per_line = self.options.months_per_line
        #self.month_w = self.doc_w / self.months_per_line
        if self.options.auto_organize:
          self.month_w = (self.doc_w * 0.8) / self.months_per_line
          self.month_margin = self.month_w / 10
        else:
          self.month_w = self.options.month_width
          self.month_margin = self.options.month_margin
        self.day_w = self.month_w / 7
        self.day_h = self.month_w / 9
        self.month_h = self.day_w * 7
        if self.options.month == 0:
          self.year_margin = (( self.doc_w + self.day_w -
                               (self.month_w*self.months_per_line) -
                               (self.month_margin*(self.months_per_line-1))
                             ) / 2 ) #- self.month_margin
        else:
          self.year_margin = ( self.doc_w - self.month_w ) / 2
        self.style_day = {
          'font-size': str( self.day_w / 2 ),
          'font-family': self.options.font_day,
          'text-anchor': 'middle',
          'text-align': 'center',
          'fill': self.options.color_day
          }
        self.style_weekend = self.style_day.copy()
        self.style_weekend['fill'] = self.options.color_weekend
        self.style_nmd = self.style_day.copy()
        self.style_nmd['fill'] = self.options.color_nmd
        self.style_month = self.style_day.copy()
        self.style_month['fill'] = self.options.color_month
        self.style_month['font-size'] = str( self.day_w / 1.5 )
        self.style_month['font-weight'] = 'bold'
        self.style_month['font-family'] = self.options.font_month
        self.style_day_name = self.style_day.copy()
        self.style_day_name['fill'] = self.options.color_day_name
        self.style_day_name['font-size'] = str( self.day_w / 3 )
        self.style_year = self.style_day.copy()
        self.style_year['fill'] = self.options.color_year
        self.style_year['font-size'] = str( self.day_w * 2 )
        self.style_year['font-weight'] = 'bold'
        self.style_other_holiday = self.style_day.copy()
        self.style_other_holiday['fill'] = self.options.color_other_holiday

    def is_weekend(self, pos):
        # weekend values: "sat+sun" or "sat" or "sun"
        if self.options.start_day=='sun':
          if self.options.weekend=='sat+sun' and pos==0: return True
          if self.options.weekend=='sat+sun' and pos==6: return True
          if self.options.weekend=='sat' and pos==6: return True
          if self.options.weekend=='sun' and pos==0: return True
        else:
          if self.options.weekend=='sat+sun' and pos==5: return True
          if self.options.weekend=='sat+sun' and pos==6: return True
          if self.options.weekend=='sat' and pos==5: return True
          if self.options.weekend=='sun' and pos==6: return True
        return False

    def is_holiday(self, month, day):
        try:
            dt = date(int(self.options.year), month, day)
            return dt in self.holidays.itervalues()
        except:
            return False

    def is_other_holiday(self, month, day):
        try:
            dt = date(int(self.options.year), month, day)
            return dt in self.other_holidays
        except:
            return False

    def in_line_month(self, cal):
        cal2 = []
        for week in cal:
          for day in week:
            if day != 0:
              cal2.append(day)
        return cal2

    def write_month_header(self, g, m):
        txt_atts = {'style': simplestyle.formatStyle(self.style_month),
                    'x': str( (self.month_w - self.day_w) / 2 ),
                    'y': str( self.day_h / 5 ) }
        try:
          inkex.etree.SubElement(g, 'text', txt_atts).text = unicode(self.options.month_names[m-1], self.options.input_encode)
        except:
          inkex.errormsg('You must select your correct system encode.')
          exit(1)
        gw = inkex.etree.SubElement(g, 'g')
        week_x = 0
        if self.options.start_day=='sun':
          for wday in self.options.day_names:
            txt_atts = {'style': simplestyle.formatStyle(self.style_day_name),
                        'x': str( self.day_w * week_x ),
                        'y': str( self.day_h ) }
            try:
              inkex.etree.SubElement(gw, 'text', txt_atts).text = unicode(wday, self.options.input_encode)
            except:
              inkex.errormsg('You must select your correct system encode.')
              exit(1)
            week_x += 1
        else:
          w2 = self.options.day_names[1:]
          w2.append(self.options.day_names[0])
          for wday in w2:
            txt_atts = {'style': simplestyle.formatStyle(self.style_day_name),
                        'x': str( self.day_w * week_x ),
                        'y': str( self.day_h ) }
            try:
              inkex.etree.SubElement(gw, 'text', txt_atts).text = unicode(wday, self.options.input_encode)
            except:
              inkex.errormsg('You must select your correct system encode.')
              exit(1)
            week_x += 1

    def create_month(self, m):
        txt_atts = {
          'transform': 'translate('+str(self.year_margin +
                                       (self.month_w + self.month_margin) *
                                        self.month_x_pos) +
                                ','+str((self.day_h * 4) +
                                       (self.month_h * self.month_y_pos))+')',
          'id': 'month_'+str(m)+'_'+str(self.options.year) }
        g = inkex.etree.SubElement(self.year_g, 'g', txt_atts)
        self.write_month_header(g, m)
        gdays = inkex.etree.SubElement(g, 'g')
        cal = calendar.monthcalendar(self.options.year,m)
        if m == 1:
          before_month = \
            self.in_line_month( calendar.monthcalendar(self.options.year-1, 12) )
        else:
          before_month = \
            self.in_line_month( calendar.monthcalendar(self.options.year, m-1) )
        if m == 12:
          next_month = \
            self.in_line_month( calendar.monthcalendar(self.options.year+1, 1) )
        else:
          next_month = \
            self.in_line_month( calendar.monthcalendar(self.options.year, m+1) )
        if len(cal) < 6: # add a line after the last week
          cal.append([0,0,0,0,0,0,0])
        if len(cal) < 6: # add a line before the first week (Feb 2009)
          cal.reverse()
          cal.append([0,0,0,0,0,0,0])
          cal.reverse()
        # How mutch before month days will be showed:
        bmd = cal[0].count(0) + cal[1].count(0)
        before = True
        week_y = 0
        day_of_month = 1
        for week in cal:
          week_x = 0
          for day in week:
            style = self.style_day
            if self.is_weekend(week_x): 
                style = self.style_weekend
            if day == 0: style = self.style_nmd
            if (not before) and (self.is_other_holiday(m, day_of_month)):
                style = self.style_other_holiday
            if (not before) and (self.is_holiday(m, day_of_month)): 
                style = self.style_weekend
            txt_atts = {'style': simplestyle.formatStyle(style),
                        'x': str( self.day_w * week_x ),
                        'y': str( self.day_h * (week_y+2) ) }
            if day==0 and not self.options.fill_edb:
	      pass # draw nothing
	    elif day==0:
              if before:
                inkex.etree.SubElement(gdays, 'text', txt_atts).text = str( before_month[-bmd] )
                bmd -= 1
              else:
                inkex.etree.SubElement(gdays, 'text', txt_atts).text = str( next_month[bmd] )
                bmd += 1
            else:
              inkex.etree.SubElement(gdays, 'text', txt_atts).text = str(day)
              before = False
              day_of_month += 1
            week_x += 1
          week_y += 1
        self.month_x_pos += 1
        if self.month_x_pos >= self.months_per_line:
          self.month_x_pos = 0
          self.month_y_pos += 1

    def effect(self):
        self.validate_options()
        self.calculate_size_and_positions()
        parent = self.document.getroot()
        txt_atts = {
          'id': 'year_'+str(self.options.year) }
        self.year_g = inkex.etree.SubElement(parent, 'g', txt_atts)
        txt_atts = {'style': simplestyle.formatStyle(self.style_year),
                    'x': str( self.doc_w / 2 ),
                    'y': str( self.day_w * 1.5 ) }
        inkex.etree.SubElement(self.year_g, 'text', txt_atts).text = str(self.options.year)
        self.holidays = get_holidays(int(self.options.year))
        inkex.debug(self.other_holidays)
        inkex.debug(self.style_other_holiday)
        if self.options.month == 0:
          for m in range(1,13):
            self.create_month(m)
        else:
          self.create_month(self.options.month)


if __name__ == '__main__':   #pragma: no cover
    e = SVGCalendar()
    e.affect()
