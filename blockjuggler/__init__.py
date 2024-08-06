from __future__ import print_function

import sys
import traceback
from datetime import date, datetime, timedelta, time

import click
import recurring_ical_events
from icalendar import Calendar
from pytz import all_timezones, timezone, utc
from tzlocal import get_localzone

MIDNIGHT = time(0, 0, 0)

__version__ = "0.5"

def tj_datetime(dt):
    '''Timezone aware datetime to YYYY-MM-DD DayofWeek HH:MM str in localtime.
    '''
    return dt.strftime("%Y-%m-%d-%H:%M-%z")


def org_date(dt, tz):
    '''Timezone aware date to YYYY-MM-DD DayofWeek in localtime.
    '''
    if hasattr(dt, "astimezone"):
        dt = dt.astimezone(tz)
    return dt.strftime("<%Y-%m-%d %a>")


def event_is_declined(comp, emails):
    attendee_list = comp.get('ATTENDEE', None)
    if attendee_list:
        if not isinstance(attendee_list, list):
            attendee_list = [attendee_list]
        for att in attendee_list:
            if att.params.get('PARTSTAT', '') == 'DECLINED' and att.params.get('CN', '') in emails:
                return True
    return False


class IcalError(Exception):
    pass


class Convertor():
    RECUR_TAG = ":RECURRING:"

    # Do not change anything below

    def __init__(self, resource_id, days=90, emails=None, continue_on_error=False):
        """
        days: Window length in days (left & right from current time). Has
        to be positive.
        emails: list of user email addresses (to deal with declined events)
        """
        if emails is None:
            emails = []
        self.resource_id = resource_id
        self.emails = set(emails)
        self.days = days
        self.continue_on_error = continue_on_error

    def __call__(self, ics_file, org_file):
        try:
            cal = Calendar.from_ical(ics_file.read())
        except ValueError as e:
            msg = "Parsing error: {}".format(e)
            raise IcalError(msg)

        now = datetime.now(utc)
        start = (now - timedelta(days=self.days)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = (now + timedelta(days=self.days)).replace(hour=0, minute=0, second=0, microsecond=0)

        slots = []
        for comp in recurring_ical_events.of(
            cal, keep_recurrence_attributes=True
        ).between(start, end):
            if event_is_declined(comp, self.emails):
                continue
            try:
                slot = self.create_slot(comp)
                slots.append(slot)
            except Exception:
                print("Exception when processing:\n", file=sys.stderr)
                print(comp.to_ical().decode('utf-8') + "\n", file=sys.stderr)
                if self.continue_on_error:
                    print(traceback.format_exc(), file=sys.stderr)
                else:
                    raise

        org_file.write(f"supplement resource {self.resource_id} {'{'}\n")
        org_file.write(self.create_leaves(start, end, slots))
        org_file.write("}\n")

    def create_slot(self, comp):
        """Extract a working slot (start/end time) from the calendar event."""
        summary = None
        if "SUMMARY" in comp:
            summary = comp['SUMMARY'].to_ical().decode("utf-8")
            summary = summary.replace('\\,', ',')
        location = None
        if "LOCATION" in comp:
            location = comp['LOCATION'].to_ical().decode("utf-8")
            location = location.replace('\\,', ',')
        if not any((summary, location)):
            summary = u"(No title)"
        else:
            summary += " - " + location if location and self.include_location else ''

        # Get start/end/duration
        ev_start = None
        ev_end = None
        duration = None
        if "DTSTART" in comp:
            ev_start = comp["DTSTART"].dt
        if "DTEND" in comp:
            ev_end = comp["DTEND"].dt
            if ev_start is not None:
                duration = ev_end - ev_start
        elif "DURATION" in comp:
            duration = comp["DURATION"].dt
            if ev_start is not None:
                ev_end = ev_start + duration

        if not isinstance(ev_start, datetime):
            ev_start = datetime.combine(ev_start, time(0, tzinfo=utc))
        if not isinstance(ev_end, datetime):
            ev_end = datetime.combine(ev_end, time(0, tzinfo=utc))

        return ev_start, ev_end, summary

    def create_leaves(self, start, end, slots):
        """Construct TJ leaves statements to fill gaps between slots."""
        output = []
        last_time = None

        # FIXME check for overlap?
        slots = sorted(slots)

        for slot_start, slot_end, summary in slots:
            output.append(u"  # {}\n".format(summary))
            output.append(u"  # {} - {}\n".format(slot_start, slot_end))

            if last_time is None:
                output.append("  leaves project {} - {}\n".format(
                    "${projectstart}",
                    tj_datetime(slot_start)
                ))
            elif slot_start > last_time:
                output.append("  leaves project {} - {}\n".format(
                    tj_datetime(last_time),
                    tj_datetime(slot_start)
                ))
            last_time = slot_end

        output.append("  leaves project {} - {}\n".format(
            tj_datetime(last_time),
            "${projectend}"
        ))

        return ''.join(output)


@click.command(context_settings={"help_option_names": ['-h', '--help']})
@click.option(
    "--email",
    "-e",
    multiple=True,
    default=None,
    help="User email address (used to deal with declined events). You can write multiple emails with as many -e options as you like.")
@click.option(
    "--days",
    "-d",
    default=90,
    type=click.IntRange(0, clamp=True),
    help=("Window length in days (left & right from current time. Default is 90 days). "
          "Has to be positive."))
@click.option(
    "--resource-id",
    "-r",
    default="r1",
    help="TaskJuggler resource id.")
@click.option(
    "--continue-on-error",
    default=False,
    is_flag=True,
    help="Pass this to attempt to continue even if some events are not handled",
)
@click.argument("ics_file", type=click.File("r", encoding="utf-8"))
@click.argument("org_file", type=click.File("w", encoding="utf-8"))
@click.version_option(__version__)
def main(ics_file, org_file, email, days, resource_id, continue_on_error):
    """Convert ICAL format into org-mode.

    Files can be set as explicit file name, or `-` for stdin or stdout::

        $ blockjuggler in.ical out.org

        $ blockjuggler in.ical - > out.org

        $ cat in.ical | blockjuggler - out.org

        $ cat in.ical | blockjuggler - - > out.org
    """
    convertor = Convertor(days=days, resource_id=resource_id,
                          emails=email, continue_on_error=continue_on_error)
    try:
        convertor(ics_file, org_file)
    except IcalError as e:
        click.echo(str(e), err=True)
        raise click.Abort()
