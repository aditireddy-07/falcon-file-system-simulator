import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from disk import VirtualDisk


class TestVirtualDisk(unittest.TestCase):

    def test_initial_state(self):
        disk = VirtualDisk(total_blocks=10, block_size=512)

        self.assertEqual(disk.get_used_blocks(), 0)
        self.assertEqual(disk.get_free_block_count(), 10)
        self.assertEqual(disk.get_capacity_bytes(), 5120)

    def test_allocate_block(self):
        disk = VirtualDisk(total_blocks=5)

        block = disk.allocate_block("file_a.txt")

        self.assertEqual(block, 0)
        self.assertEqual(disk.get_used_blocks(), 1)
        self.assertEqual(disk.blocks[0], "file_a.txt")

    def test_free_block(self):
        disk = VirtualDisk(total_blocks=5)

        block = disk.allocate_block("file_a.txt")
        disk.free_block(block, "file_a.txt")

        self.assertIsNone(disk.blocks[block])
        self.assertEqual(disk.get_used_blocks(), 0)

    def test_disk_full(self):
        disk = VirtualDisk(total_blocks=1)

        disk.allocate_block("file_a.txt")

        with self.assertRaises(RuntimeError):
            disk.allocate_block("file_b.txt")

    def test_invalid_block_size(self):
        with self.assertRaises(ValueError):
            VirtualDisk(total_blocks=10, block_size=0)

    def test_cannot_free_another_owners_block(self):
        disk = VirtualDisk(total_blocks=5)

        block = disk.allocate_block("file_a.txt")

        with self.assertRaises(ValueError):
            disk.free_block(block, "file_b.txt")

        self.assertEqual(disk.blocks[block], "file_a.txt")


if __name__ == "__main__":
    unittest.main()
