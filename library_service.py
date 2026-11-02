from datetime import date, timedelta

from models import (
    Book, Magazine, ReferenceBook,
    StudentMember, ResearchStudent, FacultyMember, NotifiedMember,
    NotificationMixin,
)


class LibraryManager:
    library_name = "Community Library"
    max_active_loans_default = 3

    def __init__(self):
        self.items = {}
        self.members = {}
        # Active loans are keyed by item ID.
        self.loans = {}

    @classmethod
    def set_default_borrowing_policy(cls, limit):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("The default borrowing limit must be a positive integer.")
        cls.max_active_loans_default = limit

    def register_item(self, item):
        if item.item_id in self.items:
            raise ValueError(f"Item ID '{item.item_id}' already exists.")
        self.items[item.item_id] = item

    def register_member(self, member):
        if member.member_id in self.members:
            raise ValueError(f"Member ID '{member.member_id}' already exists.")
        self.members[member.member_id] = member

    def borrow(self, member_id, item_id):
        if member_id not in self.members:
            raise ValueError(f"Member '{member_id}' does not exist.")
        if item_id not in self.items:
            raise ValueError(f"Item '{item_id}' does not exist.")

        member = self.members[member_id]
        item = self.items[item_id]

        if item_id in self.loans or not item.available:
            raise ValueError("This item is not available for borrowing.")
        if not item.is_lendable:
            raise ValueError("Reference books cannot be borrowed.")
        if not member.can_borrow():
            raise ValueError("The member has reached their borrowing limit.")

        issue_date = date.today()
        due_date = issue_date + timedelta(days=item.loan_period_days())

        item.checkout()
        member.add_loan(item_id)
        self.loans[item_id] = {
            "item_id": item_id,
            "member_id": member_id,
            "issue_date": issue_date.isoformat(),
            "due_date": due_date.isoformat(),
        }

        if isinstance(member, NotificationMixin):
            member.send_notice(f"'{item.title}' was issued. Due date: {due_date}.")
        return due_date

    @staticmethod
    def calculate_fine(overdue_days, fine_per_day=5):
        return max(0, overdue_days) * fine_per_day

    def return_item(self, item_id):
        if item_id not in self.loans:
            raise ValueError(f"Item '{item_id}' has no active loan.")

        loan = self.loans[item_id]
        member = self.members[loan["member_id"]]
        item = self.items[item_id]

        due_date = date.fromisoformat(loan["due_date"])
        overdue_days = max(0, (date.today() - due_date).days)
        fine = self.calculate_fine(overdue_days)

        item.checkin()
        member.remove_loan(item_id)
        del self.loans[item_id]

        if isinstance(member, NotificationMixin):
            member.send_notice(
                f"'{item.title}' was returned. Overdue days: {overdue_days}; fine: Rs. {fine}."
            )

        return {
            "item_id": item_id,
            "member_id": member.member_id,
            "overdue_days": overdue_days,
            "fine": fine,
        }

    def overdue_loans(self):
        today = date.today()
        return [
            loan for loan in self.loans.values()
            if date.fromisoformat(loan["due_date"]) < today
        ]

    def report_items(self):
        print("\\n--- Complete Catalogue ---")
        if not self.items:
            print("No items registered.")
        for item in self.items.values():
            print(item)

    def report_available_items(self):
        print("\\n--- Available Items ---")
        available = [item for item in self.items.values() if item.available]
        if not available:
            print("No items are currently available.")
        for item in available:
            print(item)

    def report_active_loans(self):
        print("\\n--- Active Loans ---")
        if not self.loans:
            print("No active loans.")
        for loan in self.loans.values():
            print(
                f'{loan["item_id"]} | {loan["member_id"]} | '
                f'Issued: {loan["issue_date"]} | Due: {loan["due_date"]}'
            )

    def report_overdue_loans(self):
        print("\\n--- Overdue Loans ---")
        overdue = self.overdue_loans()
        if not overdue:
            print("No overdue loans.")
        for loan in overdue:
            days = (date.today() - date.fromisoformat(loan["due_date"])).days
            print(
                f'{loan["item_id"]} | {loan["member_id"]} | '
                f'Due: {loan["due_date"]} | Overdue: {days} day(s)'
            )

    def report_members(self):
        print("\\n--- Members and Borrowed-Item Counts ---")
        if not self.members:
            print("No members registered.")
        for member in self.members.values():
            print(member)

    def report_all(self):
        self.report_items()
        self.report_available_items()
        self.report_active_loans()
        self.report_overdue_loans()
        self.report_members()


def create_item(item_type, item_id, title):
    classes = {"book": Book, "magazine": Magazine, "reference": ReferenceBook}
    item_class = classes.get(item_type.lower())
    if item_class is None:
        raise ValueError("Item type must be book, magazine, or reference.")
    return item_class(item_id, title)


def create_member(member_type, member_id, name):
    classes = {
        "student": StudentMember,
        "research": ResearchStudent,
        "faculty": FacultyMember,
        "notified": NotifiedMember,
    }
    member_class = classes.get(member_type.lower())
    if member_class is None:
        raise ValueError("Member type must be student, research, faculty, or notified.")
    return member_class(member_id, name)
