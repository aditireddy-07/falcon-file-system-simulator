import sys
import unittest
from pathlib import Path

# Add the project's src folder to Python's module search path.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
SRC_FOLDER = PROJECT_ROOT / "src"
sys.path.insert(0, str(SRC_FOLDER))

from disk import VirtualDisk
from file_entry import FileEntry
from allocation import AllocationManager, AllocationError


class TestAllocationManager(unittest.TestCase):

    def test_contiguous_allocation(self):
        disk = VirtualDisk(total_blocks=10, block_size=10)
        manager = AllocationManager(disk)
        file_entry = FileEntry("report.txt", "A" * 25)

        allocated = manager.allocate(file_entry, "contiguous")

        self.assertEqual(allocated, [0, 1, 2])
        self.assertEqual(disk.get_used_blocks(), 3)

    def test_linked_allocation(self):
        disk = VirtualDisk(total_blocks=10, block_size=10)
        manager = AllocationManager(disk)
        file_entry = FileEntry("notes.txt", "A" * 25)

        allocated = manager.allocate(file_entry, "linked")

        self.assertEqual(len(allocated), 3)

        self.assertEqual(
            file_entry.block_links[allocated[0]],
            allocated[1]
        )

        self.assertEqual(
            file_entry.block_links[allocated[1]],
            allocated[2]
        )

        self.assertIsNone(
            file_entry.block_links[allocated[2]]
        )

    def test_indexed_allocation(self):
        disk = VirtualDisk(total_blocks=10, block_size=10)
        manager = AllocationManager(disk)
        file_entry = FileEntry("data.txt", "A" * 25)

        allocated = manager.allocate(file_entry, "indexed")

        self.assertEqual(len(allocated), 3)
        self.assertIsNotNone(file_entry.index_block)
        self.assertEqual(disk.get_used_blocks(), 4)

    def test_contiguous_allocation_failure(self):
        disk = VirtualDisk(total_blocks=5, block_size=10)

        # Occupy blocks 0, 1, and 2.
        disk.allocate_block("existing_a")
        disk.allocate_block("existing_b")
        disk.allocate_block("existing_c")

        # Free block 1, leaving free blocks 1, 3, and 4.
        disk.free_block(1, "existing_b")

        self.assertEqual(
            disk.get_free_blocks(),
            [1, 3, 4]
        )

        manager = AllocationManager(disk)
        file_entry = FileEntry("large.txt", "A" * 30)

        # Three consecutive blocks are required, but none are available.
        with self.assertRaises(AllocationError):
            manager.allocate(file_entry, "contiguous")

        # Failed allocation must not occupy additional blocks.
        self.assertEqual(disk.get_used_blocks(), 2)
        self.assertEqual(file_entry.allocated_blocks, [])

    def test_invalid_allocation_method(self):
        disk = VirtualDisk(total_blocks=10, block_size=10)
        manager = AllocationManager(disk)
        file_entry = FileEntry("report.txt", "Hello")

        with self.assertRaises(ValueError):
            manager.allocate(file_entry, "invalid")

    def test_release_allocated_blocks(self):
        disk = VirtualDisk(total_blocks=10, block_size=10)
        manager = AllocationManager(disk)
        file_entry = FileEntry("data.txt", "A" * 25)

        manager.allocate(file_entry, "indexed")
        manager.release(file_entry)

        self.assertEqual(disk.get_used_blocks(), 0)
        self.assertEqual(file_entry.allocated_blocks, [])
        self.assertIsNone(file_entry.index_block)
        self.assertEqual(file_entry.block_links, {})

    def test_indexed_allocation_failure_rolls_back(self):
        disk = VirtualDisk(total_blocks=3, block_size=10)
        manager = AllocationManager(disk)
        file_entry = FileEntry("large.txt", "A" * 25)

        # Three data blocks plus one index block are required,
        # but the disk only has three blocks.
        with self.assertRaises(AllocationError):
            manager.allocate(file_entry, "indexed")

        # The failed operation must leave the disk unchanged.
        self.assertEqual(disk.get_used_blocks(), 0)
        self.assertEqual(file_entry.allocated_blocks, [])
        self.assertIsNone(file_entry.index_block)

    def test_linked_allocation_failure_rolls_back(self):
        disk = VirtualDisk(total_blocks=3, block_size=10)
        manager = AllocationManager(disk)
        file_entry = FileEntry("large.txt", "A" * 35)

        # Four data blocks are required, but only three are available.
        with self.assertRaises(AllocationError):
            manager.allocate(file_entry, "linked")

        # No blocks should remain allocated after failure.
        self.assertEqual(disk.get_used_blocks(), 0)
        self.assertEqual(file_entry.allocated_blocks, [])
        self.assertEqual(file_entry.block_links, {})


if __name__ == "__main__":
    unittest.main()