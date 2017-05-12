# coding: utf-8
import calendar
import datetime
import pytz

from django.utils.deprecation import MiddlewareMixin


class VisitTimeMiddleware(MiddlewareMixin):
    """
    Used to set cookies with various times, which we use to mark comments as
    "new".

    We use raw cookies rather than sessions, because we want these values
    to be directly accessible via JavaScript, so we can do the marking of
    "new" things with that, rather than in templates. So we avoid caching
    this stuff that should be dynamic.
    """

    # Number of days until cookies expire.
    cookie_duration = 14

    # How long until we re-set all the "new" labels on comments? Seconds.
    visit_length = 5400

    # These three are all based on values set and got from cookies:

    # The time of the last page view.
    # Set to now with every page view.
    last_view = None

    # When this current visit began.
    # This stays the same until self.visit_length seconds have elapsed,
    # at which point this "visit" is over and visit_start is set to now.
    visit_start = None

    # When the previous visit ended.
    # Comments newer than this get marked as "new".
    prev_visit_end = None

    def process_response(self, request, response):
        """First we get existing cookie values, then we set new ones."""

        request = self._set_vars_from_cookies(request)

        response = self._set_cookies(response)

        return response

    def _set_vars_from_cookies(self, request):
        """Reads in any existing cookie values."""

        last_view_cookie = request.COOKIES.get('last_view', '')
        if last_view_cookie != '':
            try:
                self.last_view = self.cookie_value_to_datetime(
                                                            last_view_cookie)
            except:
                pass

        visit_start_cookie = request.COOKIES.get('visit_start', '')
        if visit_start_cookie != '':
            try:
                self.visit_start = self.cookie_value_to_datetime(
                                                            visit_start_cookie)
            except:
                pass

        prev_visit_end_cookie = request.COOKIES.get('prev_visit_end', '')
        if prev_visit_end_cookie != '':
            try:
                self.prev_visit_end = self.cookie_value_to_datetime(
                                                        prev_visit_end_cookie)
            except:
                pass
        return request

    def _set_cookies(self, response):
        """Sets new cookie values."""

        time_now = datetime.datetime.now(pytz.utc)

        # What time will our cookies expire?
        cookie_expire = time_now + datetime.timedelta(self.cookie_duration)

        if self.last_view is None or self.visit_start is None:
            # User hasn't been here before.
            response.set_cookie('visit_start',
                                value=self.datetime_to_cookie_value(time_now),
                                expires=cookie_expire)

        elif self.visit_start is not None:
            # User has viewed a page before.
            current_visit_duration = time_now - self.visit_start
            if current_visit_duration.total_seconds() > self.visit_length:
                # This is a new visit for the user.
                response.set_cookie(
                        'prev_visit_end',
                        value=self.datetime_to_cookie_value(self.last_view),
                        expires=cookie_expire)
                response.set_cookie(
                            'visit_start',
                            value=self.datetime_to_cookie_value(time_now),
                            expires=cookie_expire)

        response.set_cookie('last_view',
                            value=self.datetime_to_cookie_value(time_now),
                            expires=cookie_expire)

        return response

    def cookie_value_to_datetime(self, str):
        """
        Takes a string from a cookie, a unix timestamp, and returns a
        datetime object, UTC.
        """
        naive_dt = datetime.datetime.fromtimestamp(int(str))
        return naive_dt.replace(tzinfo=pytz.utc)

    def datetime_to_cookie_value(self, dt):
        """Takes a datetime object and returns a UTC unix timestamp."""
        return calendar.timegm(dt.timetuple())
