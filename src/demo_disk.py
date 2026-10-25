from disk import VirtualDisk

disk = VirtualDisk(total_blocks=10, block_size=512)

disk.allocate_block("report.txt")
disk.allocate_block("report.txt")
disk.allocate_block("notes.txt")

disk.display()

disk.free_block(0, "report.txt")

print("\nAfter freeing block 0:")
disk.display()