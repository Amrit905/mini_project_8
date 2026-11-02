from pathlib import Path

from library_service import LibraryManager, create_item, create_member
from storage import load_data, save_data


DATA_FILE = Path(__file__).with_name("data.json")


def get_non_empty(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("This field cannot be empty.")


def register_item(manager):
    print("\\nItem types: book, magazine, reference")
    item_type = get_non_empty("Enter item type: ").lower()
    item_id = get_non_empty("Enter item ID: ")
    title = get_non_empty("Enter title: ")
    manager.register_item(create_item(item_type, item_id, title))
    print("Item registered successfully.")


def register_member(manager):
    print("\\nMember types: student, research, faculty, notified")
    member_type = get_non_empty("Enter member type: ").lower()
    member_id = get_non_empty("Enter member ID: ")
    name = get_non_empty("Enter member name: ")
    manager.register_member(create_member(member_type, member_id, name))
    print("Member registered successfully.")


def borrow_item(manager):
    member_id = get_non_empty("Enter member ID: ")
    item_id = get_non_empty("Enter item ID: ")
    due_date = manager.borrow(member_id, item_id)
    print(f"Borrow successful: {item_id} issued to {member_id}.")
    print("Due date:", due_date)


def return_item(manager):
    item_id = get_non_empty("Enter item ID to return: ")
    result = manager.return_item(item_id)
    print("Return successful.")
    print("Overdue days:", result["overdue_days"])
    print("Fine: Rs.", result["fine"])


def show_menu():
    print("\\n========== LIBRARY LENDING SYSTEM ==========")
    print("1. Register library item")
    print("2. Register member")
    print("3. Borrow item")
    print("4. Return item")
    print("5. View reports")
    print("6. Exit")


def main():
    manager = LibraryManager()
    try:
        load_data(manager, DATA_FILE)
        print(f"Welcome to {manager.library_name}.")
    except (OSError, ValueError, TypeError, KeyError) as error:
        print("Could not load saved library data:", error)
        print("Starting with an empty in-memory library.")
        manager = LibraryManager()

    while True:
        show_menu()
        choice = input("Enter your choice: ").strip()
        try:
            if choice == "1":
                register_item(manager)
                save_data(manager, DATA_FILE)
            elif choice == "2":
                register_member(manager)
                save_data(manager, DATA_FILE)
            elif choice == "3":
                borrow_item(manager)
                save_data(manager, DATA_FILE)
            elif choice == "4":
                return_item(manager)
                save_data(manager, DATA_FILE)
            elif choice == "5":
                manager.report_all()
            elif choice == "6":
                save_data(manager, DATA_FILE)
                print("Library data saved. Goodbye!")
                break
            else:
                print("Invalid choice. Enter a number from 1 to 6.")
        except (ValueError, OSError, TypeError) as error:
            print("Operation could not be completed:", error)


if __name__ == "__main__":
    main()
