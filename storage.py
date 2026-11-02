import json
import os
from datetime import date

from models import (
    Book, Magazine, ReferenceBook,
    StudentMember, ResearchStudent, FacultyMember, NotifiedMember,
)


def _item_to_dict(item):
    return {
        "item_type": type(item).__name__,
        "item_id": item.item_id,
        "title": item.title,
        "available": item.available,
    }


def _member_to_dict(member):
    return {
        "member_type": type(member).__name__,
        "member_id": member.member_id,
        "name": member.name,
        "borrowing_limit": member.borrowing_limit,
    }


def save_data(manager, file_path):
    data = {
        "items": [_item_to_dict(item) for item in manager.items.values()],
        "members": [_member_to_dict(member) for member in manager.members.values()],
        "loans": list(manager.loans.values()),
    }
    temporary_path = f"{file_path}.tmp"
    with open(temporary_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)
    os.replace(temporary_path, file_path)


def load_data(manager, file_path):
    if not os.path.exists(file_path):
        return

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid JSON in '{file_path}': {error}") from error

    if not isinstance(data, dict):
        raise ValueError("The data file must contain a JSON object.")
    for section in ("items", "members", "loans"):
        if section not in data or not isinstance(data[section], list):
            raise ValueError(f"Invalid or missing '{section}' section in data file.")

    item_classes = {
        "Book": Book, "Magazine": Magazine, "ReferenceBook": ReferenceBook
    }
    member_classes = {
        "StudentMember": StudentMember,
        "ResearchStudent": ResearchStudent,
        "FacultyMember": FacultyMember,
        "NotifiedMember": NotifiedMember,
    }

    # Build temporary collections; assign them only after all records validate.
    items, members, loans = {}, {}, {}

    for record in data["items"]:
        if not isinstance(record, dict):
            raise ValueError("Each item record must be a JSON object.")
        item_type = record.get("item_type")
        item_class = item_classes.get(item_type)
        item_id, title, available = (
            record.get("item_id"), record.get("title"), record.get("available")
        )
        if item_class is None:
            raise ValueError(f"Unknown item type: {item_type}")
        if not isinstance(item_id, str) or not item_id.strip():
            raise ValueError("Each item needs a non-empty string item_id.")
        if not isinstance(title, str) or not title.strip():
            raise ValueError(f"Invalid title for item '{item_id}'.")
        if not isinstance(available, bool):
            raise ValueError(f"Invalid availability for item '{item_id}'.")
        if item_id in items:
            raise ValueError(f"Duplicate item ID in JSON: {item_id}")
        items[item_id] = item_class(item_id, title, available)

    for record in data["members"]:
        if not isinstance(record, dict):
            raise ValueError("Each member record must be a JSON object.")
        member_type = record.get("member_type")
        member_class = member_classes.get(member_type)
        member_id, name, limit = (
            record.get("member_id"), record.get("name"), record.get("borrowing_limit")
        )
        if member_class is None:
            raise ValueError(f"Unknown member type: {member_type}")
        if not isinstance(member_id, str) or not member_id.strip():
            raise ValueError("Each member needs a non-empty string member_id.")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Invalid name for member '{member_id}'.")
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError(f"Invalid borrowing limit for member '{member_id}'.")
        if member_id in members:
            raise ValueError(f"Duplicate member ID in JSON: {member_id}")
        members[member_id] = member_class(member_id, name, limit)

    for record in data["loans"]:
        if not isinstance(record, dict):
            raise ValueError("Each loan record must be a JSON object.")
        item_id = record.get("item_id")
        member_id = record.get("member_id")
        issue_date = record.get("issue_date")
        due_date = record.get("due_date")
        if item_id not in items or member_id not in members:
            raise ValueError("A loan refers to an unknown item or member.")
        if item_id in loans:
            raise ValueError(f"Duplicate active loan for item '{item_id}'.")
        if not isinstance(issue_date, str) or not isinstance(due_date, str):
            raise ValueError("Loan dates must be ISO-format strings.")
        date.fromisoformat(issue_date)
        date.fromisoformat(due_date)
        loans[item_id] = {
            "item_id": item_id,
            "member_id": member_id,
            "issue_date": issue_date,
            "due_date": due_date,
        }

    # Reconstruct current availability and each member's active-loan count.
    for item in items.values():
        item.checkin()
    for member in members.values():
        member.clear_loans()
    for item_id, loan in loans.items():
        if not items[item_id].is_lendable:
            raise ValueError(f"Non-lendable item '{item_id}' has an active loan.")
        items[item_id].checkout()
        members[loan["member_id"]].add_loan(item_id)

    manager.items = items
    manager.members = members
    manager.loans = loans
