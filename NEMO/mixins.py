from __future__ import annotations

import datetime
from datetime import timedelta
from typing import Dict, Optional, TYPE_CHECKING

from dateutil import rrule
from django.core.exceptions import NON_FIELD_ERRORS
from django.utils import timezone

from NEMO.utilities import beginning_of_the_day, format_datetime, get_recurring_rule, RecurrenceFrequency

if TYPE_CHECKING:
	from NEMO.models import User

DF = "SHORT_DATE_FORMAT"
DTF = "SHORT_DATETIME_FORMAT"


class CalendarDisplayMixin:
	"""
	Inherit from this class to express that a class type can be displayed in the NEMO calendar.
	Calling get_visual_end() will artificially lengthen the end time so the event is large enough to
	be visible and clickable.
	"""

	start = None
	end = None

	def get_visual_end(self):
		if self.end is None:
			return max(self.start + timedelta(minutes=15), timezone.now())
		else:
			return max(self.start + timedelta(minutes=15), self.end)


class BillableItemMixin:
	"""
	Mixin to be used for any billable item, currently only used by adjustment requests
	TODO: refactor billing api and other places to leverage this mixin
	"""

	AREA_ACCESS = "area_access"
	TOOL_USAGE = "tool_usage"
	REMOTE_WORK = "remote_work"
	TRAINING = "training"
	CONSUMABLE = "consumable"
	MISSED_RESERVATION = "missed_reservation"

	def get_customer(self) -> User:
		if self.get_real_type() in [
			BillableItemMixin.AREA_ACCESS,
			BillableItemMixin.REMOTE_WORK,
			BillableItemMixin.CONSUMABLE,
		]:
			return self.customer
		elif self.get_real_type() in [BillableItemMixin.TOOL_USAGE, BillableItemMixin.MISSED_RESERVATION]:
			return self.user
		elif self.get_real_type() == BillableItemMixin.TRAINING:
			return self.trainee

	def get_operator(self) -> Optional[User]:
		if self.get_real_type() == BillableItemMixin.AREA_ACCESS:
			return self.staff_charge.staff_member if self.staff_charge else None
		elif self.get_real_type() == BillableItemMixin.TOOL_USAGE:
			return self.operator
		elif self.get_real_type() == BillableItemMixin.REMOTE_WORK:
			return self.staff_member
		elif self.get_real_type() == BillableItemMixin.TRAINING:
			return self.trainer
		elif self.get_real_type() == BillableItemMixin.CONSUMABLE:
			return self.merchant
		elif self.get_real_type() == BillableItemMixin.MISSED_RESERVATION:
			return self.creator

	def get_item(self) -> str:
		if self.get_real_type() == BillableItemMixin.AREA_ACCESS:
			return f"{self.area} access"
		elif self.get_real_type() == BillableItemMixin.TOOL_USAGE:
			return f"{self.tool} usage"
		elif self.get_real_type() == BillableItemMixin.REMOTE_WORK:
			return "Staff time"
		elif self.get_real_type() == BillableItemMixin.TRAINING:
			return f"{self.get_type_display()} training"
		elif self.get_real_type() == BillableItemMixin.CONSUMABLE:
			quantity = f" (x {self.quantity}" if self.quantity > 1 else ""
			return f"{self.consumable}{quantity}"
		elif self.get_real_type() == BillableItemMixin.MISSED_RESERVATION:
			return f"{self.tool or self.area} missed reservation"

	def get_start(self) -> Optional[datetime.datetime]:
		if self.get_real_type() in [
			BillableItemMixin.AREA_ACCESS,
			BillableItemMixin.TOOL_USAGE,
			BillableItemMixin.REMOTE_WORK,
			BillableItemMixin.MISSED_RESERVATION,
		]:
			return self.start

	def get_end(self) -> Optional[datetime.datetime]:
		if self.get_real_type() in [
			BillableItemMixin.AREA_ACCESS,
			BillableItemMixin.TOOL_USAGE,
			BillableItemMixin.REMOTE_WORK,
			BillableItemMixin.MISSED_RESERVATION,
		]:
			return self.end
		elif self.get_real_type() in [BillableItemMixin.TRAINING, BillableItemMixin.CONSUMABLE]:
			return self.date

	def get_operator_action(self) -> str:
		if self.get_real_type() == BillableItemMixin.AREA_ACCESS:
			return "entered "
		elif self.get_real_type() == BillableItemMixin.TOOL_USAGE:
			return "performed "
		elif self.get_real_type() == BillableItemMixin.REMOTE_WORK:
			return ""
		elif self.get_real_type() == BillableItemMixin.TRAINING:
			return "trained "
		elif self.get_real_type() == BillableItemMixin.CONSUMABLE:
			return "charged "
		elif self.get_real_type() == BillableItemMixin.MISSED_RESERVATION:
			return "created "

	def get_real_type(self) -> str:
		from NEMO.models import (
			AreaAccessRecord,
			UsageEvent,
			StaffCharge,
			TrainingSession,
			ConsumableWithdraw,
			Reservation,
		)

		if isinstance(self, AreaAccessRecord):
			return BillableItemMixin.AREA_ACCESS
		elif isinstance(self, UsageEvent):
			return BillableItemMixin.TOOL_USAGE
		elif isinstance(self, StaffCharge):
			return BillableItemMixin.REMOTE_WORK
		elif isinstance(self, TrainingSession):
			return BillableItemMixin.TRAINING
		elif isinstance(self, ConsumableWithdraw):
			return BillableItemMixin.CONSUMABLE
		elif isinstance(self, Reservation):
			return BillableItemMixin.MISSED_RESERVATION

	def get_billable_type(self) -> str:
		from NEMO.models import AreaAccessRecord, UsageEvent

		if isinstance(self, AreaAccessRecord):
			if self.staff_charge:
				return BillableItemMixin.REMOTE_WORK
			return BillableItemMixin.AREA_ACCESS
		elif isinstance(self, UsageEvent):
			if self.remote_work:
				return BillableItemMixin.REMOTE_WORK
			return BillableItemMixin.TOOL_USAGE
		else:
			return self.get_real_type()

	def get_display(self, user: User = None) -> str:
		customer_display = f" for {self.get_customer()}"
		operator_display = f" {self.get_operator_action()}by {self.get_operator()}"
		user_display = ""
		if not user or user != self.get_customer():
			user_display += customer_display
		if self.get_operator() and self.get_customer() != self.get_operator():
			if not user or user != self.get_operator():
				user_display += operator_display
		charge_time = ""
		if self.get_start() and self.get_end():
			charge_time = f" from {format_datetime(self.get_start(), DTF)} to {format_datetime(self.get_end(), DTF)}"
		elif self.get_start() or self.get_end():
			charge_time = f" on {format_datetime(self.get_start() or self.get_end(), DTF)}"
		return f"{self.get_item()}{user_display}{charge_time}"


class RecurrenceMixin:
	@property
	def get_rec_frequency_enum(self):
		return RecurrenceFrequency(self.rec_frequency)

	def get_recurrence(self) -> rrule:
		if self.rec_start and self.rec_frequency:
			return get_recurring_rule(
				self.rec_start, self.get_rec_frequency_enum, self.rec_until, self.rec_interval, self.rec_count
			)

	def next_recurrence(self, inc=False) -> datetime:
		today = beginning_of_the_day(datetime.datetime.now(), in_local_timezone=False)
		recurrence = self.get_recurrence()
		return recurrence.after(today, inc=inc) if recurrence else None

	def get_recurrence_interval_display(self) -> str:
		if not self.rec_start or not self.rec_frequency:
			return ""
		interval = f"{self.rec_interval} " if self.rec_interval != 1 else ""
		f_enum = self.get_rec_frequency_enum
		frequency = f"{f_enum.display_text}s" if self.rec_interval != 1 else f_enum.display_text
		return f"Every {interval}{frequency}"

	def get_recurrence_display(self) -> str:
		rec_display = ""
		if self.rec_start and self.rec_frequency:
			start = f", starting {format_datetime(self.rec_start, 'SHORT_DATE_FORMAT')}"
			end = ""
			if self.rec_until or self.rec_count:
				end = f" and ending "
				if self.rec_until:
					end += f"on {format_datetime(self.rec_until, 'SHORT_DATE_FORMAT')}"
				elif self.rec_count:
					end += f"after {self.rec_count} iterations" if self.rec_count != 1 else f"after one time"
					if self.get_recurrence():
						end += f" on {format_datetime(list(self.get_recurrence())[-1], 'SHORT_DATE_FORMAT')}"
			return f"{self.get_recurrence_interval_display()}{start}{end}"
		return rec_display

	def clean_recurrence(self) -> Dict:
		errors = {}
		if not self.rec_start:
			errors["rec_start"] = "This field is required."
		if not self.rec_frequency:
			errors["rec_frequency"] = "This field is required."
		if self.rec_until and self.rec_count:
			errors[NON_FIELD_ERRORS] = "'count' and 'until' cannot be used at the same time."
		return errors