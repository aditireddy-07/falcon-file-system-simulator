import sys
import unittest
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from disk import VirtualDisk
from file_manager import FileManager


class TestFileManager(unittest.TestCase):

    def setUp(self):
        self.disk = VirtualDisk(total_blocks=10, block_size=10)
        self.manager = FileManager(self.disk)

    def test_create_file(self):
        self.manager.create_file("a.txt", "Hello")

        self.assertEqual(self.manager.read_file("a.txt"), "Hello")
        self.assertEqual(self.disk.get_used_blocks(), 1)

    def test_create_file_contiguous_allocation(self):
        file_entry = self.manager.create_file(
            "report.txt",
            "A" * 25,
            "contiguous"
        )

        self.assertEqual(file_entry.allocated_blocks, [0, 1, 2])
        self.assertEqual(file_entry.allocation_method, "contiguous")
        self.assertEqual(self.disk.get_used_blocks(), 3)

    def test_create_file_linked_allocation(self):
        file_entry = self.manager.create_file(
            "notes.txt",
            "A" * 25,
            "linked"
        )

        blocks = file_entry.allocated_blocks

        self.assertEqual(len(blocks), 3)
        self.assertEqual(file_entry.allocation_method, "linked")
        self.assertEqual(file_entry.block_links[blocks[0]], blocks[1])
        self.assertEqual(file_entry.block_links[blocks[1]], blocks[2])
        self.assertIsNone(file_entry.block_links[blocks[2]])
        self.assertEqual(self.disk.get_used_blocks(), 3)

    def test_create_file_indexed_allocation(self):
        file_entry = self.manager.create_file(
            "data.txt",
            "A" * 25,
            "indexed"
        )

        self.assertEqual(len(file_entry.allocated_blocks), 3)
        self.assertEqual(file_entry.allocation_method, "indexed")
        self.assertIsNotNone(file_entry.index_block)
        self.assertEqual(self.disk.get_used_blocks(), 4)

    def test_invalid_allocation_method(self):
        with self.assertRaises(ValueError):
            self.manager.create_file(
                "a.txt",
                "Hello",
                "invalid"
            )

        self.assertEqual(self.disk.get_used_blocks(), 0)
        self.assertEqual(len(self.manager.list_files()), 0)

    def test_duplicate_file(self):
        self.manager.create_file("a.txt", "Hello")

        with self.assertRaises(FileExistsError):
            self.manager.create_file("a.txt", "Again")

    def test_read_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            self.manager.read_file("missing.txt")

    def test_update_file(self):
        self.manager.create_file("a.txt", "Hello")
        self.manager.update_file("a.txt", "Hello World!")

        self.assertEqual(
            self.manager.read_file("a.txt"),
            "Hello World!"
        )
        self.assertEqual(self.disk.get_used_blocks(), 2)

    def test_failed_creation_rolls_back_allocations(self):
        self.manager.create_file("a.txt", "A" * 90)

        with self.assertRaises(RuntimeError):
            self.manager.create_file("b.txt", "B" * 20)

        self.assertEqual(self.disk.get_used_blocks(), 9)
        self.assertEqual(len(self.manager.list_files()), 1)

    def test_failed_update_preserves_original_file(self):
        self.manager.create_file("a.txt", "A" * 90)

        with self.assertRaises(RuntimeError):
            self.manager.update_file("a.txt", "B" * 110)

        self.assertEqual(self.manager.read_file("a.txt"), "A" * 90)
        self.assertEqual(self.disk.get_used_blocks(), 9)

    def test_delete_file(self):
        self.manager.create_file("a.txt", "Hello")
        self.manager.delete_file("a.txt")

        self.assertEqual(self.disk.get_used_blocks(), 0)

        with self.assertRaises(FileNotFoundError):
            self.manager.read_file("a.txt")

    def test_delete_indexed_file_releases_index_block(self):
        file_entry = self.manager.create_file(
            "data.txt",
            "A" * 25,
            "indexed"
        )

        self.assertEqual(self.disk.get_used_blocks(), 4)

        self.manager.delete_file("data.txt")

        self.assertEqual(self.disk.get_used_blocks(), 0)
        self.assertEqual(file_entry.allocated_blocks, [])
        self.assertIsNone(file_entry.index_block)

    def test_list_files(self):
        self.manager.create_file("a.txt", "Hello")
        self.manager.create_file("b.txt", "World")

        files = self.manager.list_files()
        file_names = [entry["name"] for entry in files]

        self.assertEqual(file_names, ["a.txt", "b.txt"])
        self.assertEqual(len(files), 2)


if __name__ == "__main__":
    unittest.main()