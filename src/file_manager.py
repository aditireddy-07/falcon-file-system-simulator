from file_entry import FileEntry
from allocation import AllocationManager


class FileManager:
    """
    Manages simulated files and their disk-block allocations.
    Supports contiguous, linked, and indexed allocation.
    """

    def __init__(self, disk):
        self.disk = disk
        self.files = {}
        self.allocator = AllocationManager(disk)

    def create_file(self, name, content="", allocation_method="contiguous"):
        """Create a file using the selected allocation strategy."""

        if name in self.files:
            raise FileExistsError(f"File '{name}' already exists.")

        if not isinstance(content, str):
            raise TypeError("File content must be a string.")

        if allocation_method not in {"contiguous", "linked", "indexed"}:
            raise ValueError("Invalid allocation method.")

        file_entry = FileEntry(
            name,
            content,
            allocation_method
        )

        self.allocator.allocate(file_entry, allocation_method)
        self.files[name] = file_entry

        return file_entry

    def read_file(self, name):
        """Return the contents of a file."""

        if name not in self.files:
            raise FileNotFoundError(f"File '{name}' does not exist.")

        return self.files[name].content

    def update_file(self, name, new_content):
        """
        Update file contents transactionally.

        If allocation fails, restore the original disk and file state.
        """

        if name not in self.files:
            raise FileNotFoundError(f"File '{name}' does not exist.")

        if not isinstance(new_content, str):
            raise TypeError("File content must be a string.")

        file_entry = self.files[name]

        # Save the original disk state.
        original_disk = self.disk.blocks.copy()

        # Save the original file state.
        original_content = file_entry.content
        original_size = file_entry.size_bytes
        original_blocks = file_entry.allocated_blocks.copy()
        original_index_block = file_entry.index_block
        original_block_links = file_entry.block_links.copy()
        original_method = file_entry.allocation_method

        try:
            # Release the old allocation before allocating the new size.
            self.allocator.release(file_entry)

            # Update the file's content and size.
            file_entry.update_content(new_content)

            # Allocate blocks again using the same strategy.
            self.allocator.allocate(file_entry, original_method)

        except Exception:
            # Restore the disk exactly as it was.
            self.disk.blocks[:] = original_disk

            # Restore the file's metadata and allocation.
            file_entry.content = original_content
            file_entry.size_bytes = original_size
            file_entry.allocated_blocks = original_blocks
            file_entry.index_block = original_index_block
            file_entry.block_links = original_block_links
            file_entry.allocation_method = original_method

            raise

    def delete_file(self, name):
        """Delete a file and release its allocated blocks."""

        if name not in self.files:
            raise FileNotFoundError(f"File '{name}' does not exist.")

        file_entry = self.files[name]

        self.allocator.release(file_entry)
        del self.files[name]

    def list_files(self):
        """Return metadata for all files."""

        return [
            file_entry.get_metadata()
            for file_entry in self.files.values()
        ]

    def display_files(self):
        """Display all files managed by FALCON."""

        if not self.files:
            print("No files found.")
            return

        print("\nFALCON FILE MANAGER")
        print("-" * 45)

        for file_entry in self.files.values():
            file_entry.display()