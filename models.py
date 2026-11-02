from abc import ABC, abstractmethod


class LibraryItem(ABC):
    """Abstract base class for every library item."""

    def __init__(self, item_id, title, available=True):
        self.item_id = item_id
        self.title = title
        self._available = bool(available)

    @property
    def available(self):
        """Read-only access to availability."""
        return self._available

    def checkout(self):
        if not self._available:
            raise ValueError(f"Item {self.item_id} is already checked out.")
        self._available = False

    def checkin(self):
        self._available = True

    @abstractmethod
    def loan_period_days(self):
        raise NotImplementedError

    @property
    def is_lendable(self):
        return self.loan_period_days() > 0

    def __str__(self):
        status = "Available" if self.available else "Borrowed"
        return f"{self.item_id} | {self.title} | {type(self).__name__} | {status}"


# Single inheritance.
class Book(LibraryItem):
    def __init__(self, item_id, title, available=True):
        super().__init__(item_id, title, available)

    def loan_period_days(self):
        return 14


class Magazine(LibraryItem):
    def __init__(self, item_id, title, available=True):
        super().__init__(item_id, title, available)

    def loan_period_days(self):
        return 7


class ReferenceBook(LibraryItem):
    def __init__(self, item_id, title, available=True):
        super().__init__(item_id, title, available)

    def loan_period_days(self):
        # A zero-day period consistently means this item cannot be borrowed.
        return 0


class Member:
    def __init__(self, member_id, name, borrowing_limit):
        self.member_id = member_id
        self.name = name
        self.borrowing_limit = int(borrowing_limit)
        self._active_loans = set()

    @property
    def borrowed_count(self):
        return len(self._active_loans)

    @property
    def borrowed_item_ids(self):
        return tuple(self._active_loans)

    def can_borrow(self):
        return self.borrowed_count < self.borrowing_limit

    def add_loan(self, item_id):
        if not self.can_borrow():
            raise ValueError(f"{self.name} has reached the borrowing limit.")
        self._active_loans.add(item_id)

    def remove_loan(self, item_id):
        self._active_loans.discard(item_id)

    def clear_loans(self):
        """Controlled method used when rebuilding state from saved loans."""
        self._active_loans.clear()

    def __str__(self):
        return (
            f"{self.member_id} | {self.name} | {type(self).__name__} | "
            f"{self.borrowed_count}/{self.borrowing_limit} borrowed"
        )


# Hierarchical inheritance: both classes inherit from Member.
class StudentMember(Member):
    def __init__(self, member_id, name, borrowing_limit=3):
        super().__init__(member_id, name, borrowing_limit)


class FacultyMember(Member):
    def __init__(self, member_id, name, borrowing_limit=5):
        super().__init__(member_id, name, borrowing_limit)


# Multilevel inheritance: ResearchStudent -> StudentMember -> Member.
class ResearchStudent(StudentMember):
    def __init__(self, member_id, name, borrowing_limit=5):
        super().__init__(member_id, name, borrowing_limit)


class NotificationMixin:
    def send_notice(self, message):
        print(f"[NOTICE to {self.name} ({self.member_id})] {message}")


# Multiple inheritance. MRO: NotifiedMember -> Member -> NotificationMixin -> object.
# Member appears first, so its constructor is used; NotificationMixin adds behaviour.
class NotifiedMember(Member, NotificationMixin):
    def __init__(self, member_id, name, borrowing_limit=3):
        super().__init__(member_id, name, borrowing_limit)
