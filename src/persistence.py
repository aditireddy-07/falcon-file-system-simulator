import json
import os
from datetime import datetime

from disk import VirtualDisk
from file_entry import FileEntry
from file_manager import FileManager


class PersistenceError(Exception):
    """Raised when FALCON cannot save or restore its state."""
    pass


class PersistenceManager:
    """Saves and restores the FALCON filesystem simulator state."""

    def __init__(self, state_file):
        self.state_file = os.path.abspath(state_file)

    def save(self, disk, manager):
        """Save disk and file metadata to a JSON file."""

        state = {
            "version": 1,
            "disk": {
                "total_blocks": disk.total_blocks,
                "block_size": disk.block_size,
                "blocks": disk.blocks,
            },
            "files": []
        }

        for file_entry in manager.files.values():
            state["files"].append({
                "name": file_entry.name,
                "content": file_entry.content,
                "size_bytes": file_entry.size_bytes,
                "allocation_method": file_entry.allocation_method,
                "allocated_blocks": file_entry.allocated_blocks,
                "index_block": file_entry.index_block,
                "block_links": file_entry.block_links,
                "created_at": file_entry.created_at.isoformat(),
            })

        directory = os.path.dirname(self.state_file)
        os.makedirs(directory, exist_ok=True)

        temporary_file = self.state_file + ".tmp"

        try:
            with open(temporary_file, "w", encoding="utf-8") as file:
                json.dump(state, file, indent=4)

            # Replace the old state only after the new JSON is written.
            os.replace(temporary_file, self.state_file)

        except (OSError, TypeError, ValueError) as error:
            if os.path.exists(temporary_file):
                try:
                    os.remove(temporary_file)
                except OSError:
                    pass

            raise PersistenceError(
                f"Could not save FALCON state: {error}"
            ) from error

    def load(self):
        """Load saved state and reconstruct the disk and file manager."""

        if not os.path.exists(self.state_file):
            return None

        try:
            with open(self.state_file, "r", encoding="utf-8") as file:
                state = json.load(file)

            if not isinstance(state, dict) or state.get("version") != 1:
                raise PersistenceError(
                    "Unsupported or invalid FALCON state-file version."
                )

            disk_data = state["disk"]
            total_blocks = disk_data["total_blocks"]
            block_size = disk_data["block_size"]
            saved_blocks = disk_data["blocks"]
            saved_files = state["files"]

            if (
                type(total_blocks) is not int
                or total_blocks <= 0
                or type(block_size) is not int
                or block_size <= 0
            ):
                raise PersistenceError("Invalid disk configuration.")

            if (
                not isinstance(saved_blocks, list)
                or len(saved_blocks) != total_blocks
            ):
                raise PersistenceError(
                    "The saved disk block list is invalid."
                )

            if not isinstance(saved_files, list):
                raise PersistenceError("The saved file list is invalid.")

            disk = VirtualDisk(
                total_blocks=total_blocks,
                block_size=block_size
            )
            disk.blocks = saved_blocks

            manager = FileManager(disk)
            restored_names = set()

            for saved_file in saved_files:
                name = saved_file["name"]
                content = saved_file["content"]
                method = saved_file["allocation_method"]

                if (
                    not isinstance(name, str)
                    or not name
                    or name in restored_names
                ):
                    raise PersistenceError(
                        "A saved file has an invalid or duplicate name."
                    )

                if not isinstance(content, str):
                    raise PersistenceError(
                        f"Invalid content for saved file '{name}'."
                    )

                if method not in ("contiguous", "linked", "indexed"):
                    raise PersistenceError(
                        f"Invalid allocation method for '{name}'."
                    )

                entry = FileEntry(
                    name=name,
                    content=content,
                    allocation_method=method
                )

                entry.allocated_blocks = saved_file["allocated_blocks"]
                entry.index_block = saved_file["index_block"]

                entry.block_links = {
                    int(block): (
                        int(next_block)
                        if next_block is not None
                        else None
                    )
                    for block, next_block
                    in saved_file["block_links"].items()
                }

                entry.created_at = datetime.fromisoformat(
                    saved_file["created_at"]
                )

                if saved_file["size_bytes"] != entry.size_bytes:
                    raise PersistenceError(
                        f"Saved size does not match content for '{name}'."
                    )

                manager.files[name] = entry
                restored_names.add(name)

            self._validate_restored_state(disk, manager)

            return disk, manager

        except PersistenceError:
            raise

        except (
            OSError,
            json.JSONDecodeError,
            KeyError,
            TypeError,
            ValueError,
            AttributeError
        ) as error:
            raise PersistenceError(
                f"Could not load FALCON state: {error}"
            ) from error

    @staticmethod
    def _validate_restored_state(disk, manager):
        """Validate restored file allocations and disk ownership."""

        expected_owners = [None] * disk.total_blocks

        for name, entry in manager.files.items():
            data_blocks = entry.allocated_blocks

            if not isinstance(data_blocks, list):
                raise PersistenceError(
                    f"Invalid allocated block list for '{name}'."
                )

            if entry.allocation_method not in (
                "contiguous", "linked", "indexed"
            ):
                raise PersistenceError(
                    f"Invalid allocation method for '{name}'."
                )

            required_blocks = (
                entry.size_bytes + disk.block_size - 1
            ) // disk.block_size

            if len(data_blocks) != required_blocks:
                raise PersistenceError(
                    f"Incorrect number of data blocks for '{name}'."
                )

            if len(set(data_blocks)) != len(data_blocks):
                raise PersistenceError(
                    f"Duplicate data blocks found for '{name}'."
                )

            for block_number in data_blocks:
                if (
                    type(block_number) is not int
                    or not 0 <= block_number < disk.total_blocks
                ):
                    raise PersistenceError(
                        f"Invalid block number for '{name}'."
                    )

                if expected_owners[block_number] is not None:
                    raise PersistenceError(
                        f"Block {block_number} is assigned more than once."
                    )

                expected_owners[block_number] = name

            # Contiguous allocation requires consecutive block numbers.
            if entry.allocation_method == "contiguous":
                if any(
                    data_blocks[i] != data_blocks[0] + i
                    for i in range(len(data_blocks))
                ):
                    raise PersistenceError(
                        f"Non-contiguous blocks found for '{name}'."
                    )

            # Linked allocation must connect each block to the next.
            if entry.allocation_method == "linked":
                links = entry.block_links

                if not isinstance(links, dict):
                    raise PersistenceError(
                        f"Invalid block links for '{name}'."
                    )

                expected_links = {
                    block: (
                        data_blocks[i + 1]
                        if i + 1 < len(data_blocks)
                        else None
                    )
                    for i, block in enumerate(data_blocks)
                }

                if links != expected_links:
                    raise PersistenceError(
                        f"Inconsistent linked allocation for '{name}'."
                    )

            elif entry.block_links:
                raise PersistenceError(
                    f"Unexpected block links for '{name}'."
                )

            # Indexed allocation requires a separate index block.
            if entry.allocation_method == "indexed":
                index_block = entry.index_block

                if (
                    type(index_block) is not int
                    or not 0 <= index_block < disk.total_blocks
                ):
                    raise PersistenceError(
                        f"Invalid index block for '{name}'."
                    )

                if expected_owners[index_block] is not None:
                    raise PersistenceError(
                        f"Index block {index_block} is assigned more than once."
                    )

                if index_block in data_blocks:
                    raise PersistenceError(
                        f"Index block overlaps data blocks for '{name}'."
                    )

                expected_owners[index_block] = f"{name} [index]"

            elif entry.index_block is not None:
                raise PersistenceError(
                    f"Unexpected index block for '{name}'."
                )

        # The disk's recorded owners must match the reconstructed allocations.
        if disk.blocks != expected_owners:
            raise PersistenceError(
                "Saved disk ownership does not match file allocations."
            )