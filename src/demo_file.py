from file_entry import FileEntry

file = FileEntry(
    name="report.txt",
    content="FALCON is my operating systems project.",
    allocation_method="contiguous"
)

file.allocated_blocks = [0, 1]

print("FALCON FILE METADATA")
print("-" * 35)

file.display()

print("\nMetadata dictionary:")
print(file.get_metadata())

print("\nUpdating file contents...")

file.update_content(
    "FALCON simulates file allocation and management."
)

file.display()