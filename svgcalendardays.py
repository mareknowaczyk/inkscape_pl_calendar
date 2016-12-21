"""
  Inkscape calendar plugin - days drawing functions

"""
import inkex, simplestyle
import calendar as cm

class BasicDayMaker(object):

    """Basic calendar day maker, used by svg calendar plugin"""

    def __init__(self, plugin_options):
       self.plugin_options = plugin_options
       self.before_month = []
       self.next_month = []
       self.week_x = 0
       self.week_y = 0
       self.before = True
    
    def onBeforeMonth(self, svg_calendar ,month, days_group, calendar):
        """Event called before first day of month created

        :svg_calendar: SVGCalendar object
        :month: created month
        :days_group: days group in svg tree
        :calendar: calendar object

        """
        self.gdays = days_group
        self.active_month = month
        self.calendar = calendar

        if month == 1:
          svg_calendar.before_month = \
            svg_calendar.in_line_month(cm.monthcalendar(svg_calendar.options.year-1, 12) )
        else:
          self.before_month = \
            svg_calendar.in_line_month(cm.monthcalendar(svg_calendar.options.year, month-1) )
        if month == 12:
          self.next_month = \
            svg_calendar.in_line_month(cm.monthcalendar(svg_calendar.options.year+1, 1) )
        else:
          self.next_month = \
            svg_calendar.in_line_month(cm.monthcalendar(svg_calendar.options.year, month+1) )
        if len(calendar) < 6: # add a line after the last week
          calendar.append([0,0,0,0,0,0,0])
        if len(calendar) < 6: # add a line before the first week (Feb 2009)
          calendar.reverse()
          calendar.append([0,0,0,0,0,0,0])
          calendar.reverse()
        # How mutch before month days will be showed:
        self.bmd = calendar[0].count(0) + calendar[1].count(0)
        self.before = True
        self.week_y = -1
        self.day_of_month = 1
 

    def onNewWeek(self, week):
        """Event called on every new week.

        :week: new week list

        """
        self.week_x = 0
        self.week_y += 1

    def write_month_header(self, svg_calendar, g, month):
        txt_atts = {'style': simplestyle.formatStyle(svg_calendar.style_month),
                    'x': str( (svg_calendar.month_w - svg_calendar.day_w) / 2 ),
                    'y': str( svg_calendar.day_h / 5 ) }
        week_x = 0
        try:
          inkex.etree.SubElement(g, 'text', txt_atts).text = unicode(svg_calendar.options.month_names[month-1], svg_calendar.options.input_encode)
        except:
          inkex.errormsg('You must select your correct system encode.')
          exit(1)
        gw = inkex.etree.SubElement(g, 'g')
        if svg_calendar.options.start_day=='sun':
          for wday in svg_calendar.options.day_names:
            txt_atts = {'style': simplestyle.formatStyle(svg_calendar.style_day_name),
                        'x': str( svg_calendar.day_w * week_x ),
                        'y': str( svg_calendar.day_h ) }
            try:
              inkex.etree.SubElement(gw, 'text', txt_atts).text = unicode(wday, svg_calendar.options.input_encode)
            except:
              inkex.errormsg('You must select your correct system encode.')
              exit(1)
            week_x += 1
        else:
          w2 = svg_calendar.options.day_names[1:]
          w2.append(svg_calendar.options.day_names[0])
          for wday in w2:
            txt_atts = {'style': simplestyle.formatStyle(svg_calendar.style_day_name),
                        'x': str( svg_calendar.day_w * week_x ),
                        'y': str( svg_calendar.day_h ) }
            try:
              inkex.etree.SubElement(gw, 'text', txt_atts).text = unicode(wday, svg_calendar.options.input_encode)
            except:
              inkex.errormsg('You must select your correct system encode.')
              exit(1)
            week_x += 1
 

    def make(self, svg_calendar, month, week, day, day_style):
        """Makes single calendar day

        :svg_calendar: SVGCalendar object
        :month: month of day
        :week: week of day
        :day: affected day
        :day_style: affected day style

        """
        pass
        txt_atts = {'style': simplestyle.formatStyle(day_style),
                    'x': str( svg_calendar.day_w * self.week_x + svg_calendar._day_offset_x ),
                    'y': str( svg_calendar.day_h * (self.week_y+2) + svg_calendar._day_offset_y) }

        if (day <> 0) and (svg_calendar.options.frame_enabled):
            svg_calendar.draw_SVG_square(
                    svg_calendar.day_w -2,
                    svg_calendar.day_h -2,
                    svg_calendar.day_w * self.week_x+1 - int(svg_calendar.day_w / 2), 
                    svg_calendar.day_h * (self.week_y+2) + 1 -int(1.5 * svg_calendar.day_h / 2), 
                    self.gdays,
                    svg_calendar.options.frame_color,
                    svg_calendar.options.frame_fill,
                    day_style
            )
        if day==0 and not svg_calendar.options.fill_edb:
          pass # draw nothing
        elif day==0:
          if self.before:
            inkex.etree.SubElement(self.gdays, 'text', txt_atts).text = str( self.before_month[-self.bmd] )
            self.bmd -= 1
          else:
            inkex.etree.SubElement(self.gdays, 'text', txt_atts).text = str( self.next_month[self.bmd] )
            self.bmd += 1
        else:
          inkex.etree.SubElement(self.gdays, 'text', txt_atts).text = str(day)
          self.before = False
          self.day_of_month += 1
        self.week_x += 1




class DayMakersFactory(object):

    """Factory of calendar day makers object"""

    @staticmethod
    def make(plugin_options):
        """Produces day maker object that depends on plugin_options"""
        return BasicDayMaker(plugin_options)
