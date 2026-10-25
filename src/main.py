import os

from disk import VirtualDisk
from file_manager import FileManager
from persistence import PersistenceManager, PersistenceError
from logging_config import setup_logger


PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

STATE_FILE = os.path.join(
    PROJECT_ROOT,
    "data",
    "falcon_state.json"
)

logger = setup_logger(PROJECT_ROOT)


def save_state(persistence, disk, manager):
    """Save the current filesystem state."""
    try:
        persistence.save(disk, manager)
        logger.info("Filesystem state saved successfully.")
        print("\nFALCON state saved successfully.")
        return True

    except PersistenceError as error:
        logger.error("Failed to save filesystem state: %s", error)
        print(f"\nError saving FALCON state: {error}")
        return False


def create_file(manager, persistence, disk):
    print("\n--- Create File ---")

    name = input("Enter file name: ").strip()
    content = input("Enter file content: ")

    print("\nAllocation methods:")
    print("1. Contiguous")
    print("2. Linked")
    print("3. Indexed")

    method_choice = input("Choose allocation method (1-3): ").strip()

    methods = {
        "1": "contiguous",
        "2": "linked",
        "3": "indexed"
    }

    method = methods.get(method_choice)

    if method is None:
        print("Invalid allocation method.")
        logger.warning(
            "Invalid allocation method selected: %r",
            method_choice
        )
        return

    try:
        manager.create_file(name, content, method)

        logger.info(
            "File '%s' created using %s allocation.",
            name,
            method
        )

        print(f"File '{name}' created successfully.")

        if not save_state(persistence, disk, manager):
            print(
                "Warning: The file exists in memory, but its changes "
                "could not be saved."
            )

    except Exception as error:
        logger.error(
            "File creation failed for '%s': %s",
            name,
            error
        )
        print(f"Error creating file: {error}")


def read_file(manager):
    print("\n--- Read File ---")
    name = input("Enter file name: ").strip()

    try:
        content = manager.read_file(name)
        logger.info("File '%s' read successfully.", name)

        print("\nFile content:")
        print(content)

    except Exception as error:
        logger.error("Failed to read file '%s': %s", name, error)
        print(f"Error reading file: {error}")


def update_file(manager, persistence, disk):
    print("\n--- Update File ---")
    name = input("Enter file name: ").strip()
    new_content = input("Enter new content: ")

    try:
        manager.update_file(name, new_content)

        logger.info("File '%s' updated successfully.", name)
        print(f"File '{name}' updated successfully.")

        if not save_state(persistence, disk, manager):
            print(
                "Warning: The update exists in memory, but its changes "
                "could not be saved."
            )

    except Exception as error:
        logger.error("File update failed for '%s': %s", name, error)
        print(f"Error updating file: {error}")


def delete_file(manager, persistence, disk):
    print("\n--- Delete File ---")
    name = input("Enter file name: ").strip()

    try:
        manager.delete_file(name)

        logger.info("File '%s' deleted successfully.", name)
        print(f"File '{name}' deleted successfully.")

        if not save_state(persistence, disk, manager):
            print(
                "Warning: The deletion exists in memory, but its changes "
                "could not be saved."
            )

    except Exception as error:
        logger.error("File deletion failed for '%s': %s", name, error)
        print(f"Error deleting file: {error}")


def list_files(manager):
    print("\n--- Files ---")
    manager.display_files()
    logger.info("File listing displayed.")


def view_disk_status(disk):
    print("\n--- Disk Status ---")

    used_count = disk.get_used_blocks()
    free_count = disk.get_free_block_count()
    total_capacity = disk.get_capacity_bytes()
    used_capacity = disk.get_used_capacity_bytes()
    free_capacity = total_capacity - used_capacity

    usage_percentage = (
        (used_count / disk.total_blocks) * 100
        if disk.total_blocks
        else 0
    )

    print(f"Total blocks: {disk.total_blocks}")
    print(f"Used blocks: {used_count}")
    print(f"Free blocks: {free_count}")
    print(f"Block size: {disk.block_size} bytes")
    print(f"Total capacity: {total_capacity} bytes")
    print(f"Used capacity: {used_capacity} bytes")
    print(f"Free capacity: {free_capacity} bytes")
    print(f"Disk usage: {usage_percentage:.2f}%")

    disk.display()
    logger.info("Disk status displayed.")


def view_file_metadata(manager):
    print("\n--- File Metadata ---")
    name = input("Enter file name: ").strip()

    if name not in manager.files:
        print("File not found.")
        logger.warning("Metadata requested for missing file '%s'.", name)
        return

    metadata = manager.files[name].get_metadata()

    for key, value in metadata.items():
        print(f"{key}: {value}")

    logger.info("Metadata displayed for file '%s'.", name)


def display_menu():
    print("\n========== FALCON ==========")
    print(
        "File Allocation, Logging, Consistency and Operating-system Navigation"
    )
    print("============================")
    print("1. Create file")
    print("2. Read file")
    print("3. Update file")
    print("4. Delete file")
    print("5. List files")
    print("6. View disk status")
    print("7. View file metadata")
    print("8. Exit")
    print("============================")


def main():
    persistence = PersistenceManager(STATE_FILE)

    logger.info("FALCON started.")

    try:
        restored_state = persistence.load()

        if restored_state is None:
            disk = VirtualDisk(total_blocks=100, block_size=512)
            manager = FileManager(disk)

            print(
                "No previous FALCON state found. "
                "Starting a new filesystem."
            )
            logger.info("Initialized a new filesystem.")

        else:
            disk, manager = restored_state

            print("Previous FALCON state restored successfully.")
            logger.info("Previous filesystem state restored successfully.")

    except PersistenceError as error:
        logger.exception("Could not restore FALCON state.")
        print(f"\nCould not restore FALCON state: {error}")
        print("Please preserve the state file for inspection.")
        print(
            "FALCON will stop rather than overwrite potentially "
            "recoverable data."
        )
        return

    try:
        while True:
            display_menu()
            choice = input("Enter your choice (1-8): ").strip()

            if choice == "1":
                create_file(manager, persistence, disk)

            elif choice == "2":
                read_file(manager)

            elif choice == "3":
                update_file(manager, persistence, disk)

            elif choice == "4":
                delete_file(manager, persistence, disk)

            elif choice == "5":
                list_files(manager)

            elif choice == "6":
                view_disk_status(disk)

            elif choice == "7":
                view_file_metadata(manager)

            elif choice == "8":
                if save_state(persistence, disk, manager):
                    logger.info("FALCON stopped.")
                    print("Exiting FALCON. Goodbye!")
                    break

                print("FALCON could not save its state.")
                retry = input(
                    "Exit anyway without a confirmed save? (y/n): "
                ).strip().lower()

                if retry == "y":
                    logger.warning(
                        "FALCON exited without a confirmed final save."
                    )
                    print("Exiting FALCON without a confirmed save.")
                    break

            else:
                print(
                    "Invalid choice. Please enter a number from 1 to 8."
                )
                logger.warning("Invalid menu choice: %r", choice)

    except (EOFError, KeyboardInterrupt):
        logger.warning("FALCON interrupted by the user.")
        print("\nFALCON interrupted.")

        if save_state(persistence, disk, manager):
            logger.info("State saved after interruption.")

    finally:
        logger.info("FALCON session ended.")


if __name__ == "__main__":
    main()
