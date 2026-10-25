import os
import tempfile
import unittest
import sys

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src"))
)

from disk import VirtualDisk
from file_manager import FileManager
from persistence import PersistenceManager, PersistenceError


class TestPersistence(unittest.TestCase):

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.state_file = os.path.join(
            self.temp_directory.name,
            "falcon_state.json"
        )

        self.persistence = PersistenceManager(self.state_file)
        self.disk = VirtualDisk(total_blocks=20, block_size=16)
        self.manager = FileManager(self.disk)

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_save_and_restore_file_content(self):
        self.manager.create_file(
            "notes.txt",
            "FALCON persistence test",
            "contiguous"
        )

        self.persistence.save(self.disk, self.manager)
        restored = self.persistence.load()

        self.assertIsNotNone(restored)
        restored_disk, restored_manager = restored

        self.assertEqual(
            restored_manager.read_file("notes.txt"),
            "FALCON persistence test"
        )
        self.assertEqual(restored_disk.blocks, self.disk.blocks)

    def test_restore_allocation_methods(self):
        self.manager.create_file("a.txt", "hello", "contiguous")
        self.manager.create_file("b.txt", "world", "linked")
        self.manager.create_file("c.txt", "testing", "indexed")

        self.persistence.save(self.disk, self.manager)
        restored_disk, restored_manager = self.persistence.load()

        for name in ("a.txt", "b.txt", "c.txt"):
            with self.subTest(filename=name):
                original = self.manager.files[name]
                restored = restored_manager.files[name]

                self.assertEqual(
                    restored.allocation_method,
                    original.allocation_method
                )
                self.assertEqual(
                    restored.allocated_blocks,
                    original.allocated_blocks
                )
                self.assertEqual(
                    restored.index_block,
                    original.index_block
                )
                self.assertEqual(
                    restored.block_links,
                    original.block_links
                )

        self.assertEqual(restored_disk.blocks, self.disk.blocks)

    def test_restore_disk_configuration(self):
        self.manager.create_file("a.txt", "hello", "contiguous")
        self.persistence.save(self.disk, self.manager)

        restored_disk, _ = self.persistence.load()

        self.assertEqual(restored_disk.total_blocks, 20)
        self.assertEqual(restored_disk.block_size, 16)

    def test_restore_creation_timestamp(self):
        self.manager.create_file("a.txt", "hello", "contiguous")
        original_time = self.manager.files["a.txt"].created_at

        self.persistence.save(self.disk, self.manager)
        _, restored_manager = self.persistence.load()

        self.assertEqual(
            restored_manager.files["a.txt"].created_at,
            original_time
        )

    def test_restore_empty_filesystem(self):
        self.persistence.save(self.disk, self.manager)
        restored_disk, restored_manager = self.persistence.load()

        self.assertEqual(restored_manager.files, {})
        self.assertEqual(
            restored_disk.get_free_block_count(),
            20
        )

    def test_load_missing_state_file(self):
        result = self.persistence.load()
        self.assertIsNone(result)

    def test_corrupted_json_raises_error(self):
        with open(self.state_file, "w", encoding="utf-8") as file:
            file.write("{ invalid JSON")

        with self.assertRaises(PersistenceError):
            self.persistence.load()

    def test_saved_file_survives_delete_from_original_manager(self):
        self.manager.create_file("a.txt", "important data", "indexed")
        self.persistence.save(self.disk, self.manager)

        self.manager.delete_file("a.txt")

        _, restored_manager = self.persistence.load()

        self.assertIn("a.txt", restored_manager.files)
        self.assertEqual(
            restored_manager.read_file("a.txt"),
            "important data"
        )


if __name__ == "__main__":
    unittest.main()
