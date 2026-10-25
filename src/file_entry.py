from datetime import datetime


class FileEntry:
    """
    Stores metadata and contents for a simulated file.
    """

    def __init__(self, name, content="", allocation_method="contiguous"):
        if not isinstance(name, str) or not name.strip():
            raise ValueError("File name cannot be empty.")

        if not isinstance(content, str):
            raise TypeError("File content must be a string.")

        allowed_methods = {"contiguous", "linked", "indexed"}

        if allocation_method not in allowed_methods:
            raise ValueError("Invalid allocation method.")

        self.name = name
        self.content = content
        self.size_bytes = len(content.encode("utf-8"))
        self.allocation_method = allocation_method
        self.allocated_blocks = []

        # Additional metadata for allocation algorithms.
        self.index_block = None
        self.block_links = {}

        self.created_at = datetime.now()

    def update_content(self, new_content):
        """Update the file contents and recalculate its size."""

        if not isinstance(new_content, str):
            raise TypeError("File content must be a string.")

        self.content = new_content
        self.size_bytes = len(new_content.encode("utf-8"))

    def get_metadata(self):
        """Return the file metadata as a dictionary."""

        return {
            "name": self.name,
            "size_bytes": self.size_bytes,
            "allocation_method": self.allocation_method,
            "allocated_blocks": self.allocated_blocks.copy(),
            "index_block": self.index_block,
            "block_links": self.block_links.copy(),
            "created_at": self.created_at.isoformat(),
        }

    def display(self):
        """Print the file's metadata."""

        print(f"\nFile name          : {self.name}")
        print(f"File size          : {self.size_bytes} bytes")
        print(f"Allocation method  : {self.allocation_method}")
        print(f"Allocated blocks   : {self.allocated_blocks}")
        print(f"Index block        : {self.index_block}")
        print(f"Block links        : {self.block_links}")
        print(f"Created at         : {self.created_at}")