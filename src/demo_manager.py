from disk import VirtualDisk
from file_manager import FileManager


def main():
    disk = VirtualDisk(total_blocks=10, block_size=512)
    manager = FileManager(disk)

    print("Creating files...")

    manager.create_file(
        "report.txt",
        "This is my FALCON operating systems project."
    )

    manager.create_file(
        "notes.txt",
        "Learning file allocation and management."
    )

    manager.display_files()
    disk.display()

    print("\nReading report.txt:")
    print(manager.read_file("report.txt"))

    print("\nUpdating notes.txt...")
    manager.update_file(
        "notes.txt",
        "FALCON manages files and virtual disk blocks."
    )

    print("Updated notes:")
    print(manager.read_file("notes.txt"))

    print("\nDeleting report.txt...")
    manager.delete_file("report.txt")

    manager.display_files()
    disk.display()


if __name__ == "__main__":
    main()