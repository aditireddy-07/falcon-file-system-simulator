class AllocationError(RuntimeError):
    """Raised when a file cannot be allocated on the virtual disk."""


class AllocationManager:
    """Implements contiguous, linked, and indexed file allocation."""

    def __init__(self, disk):
        self.disk = disk

    def allocate(self, file_entry, method):
        """Allocate blocks using the selected allocation method."""

        if method not in {"contiguous", "linked", "indexed"}:
            raise ValueError("Unknown allocation method.")

        if file_entry.allocated_blocks or file_entry.index_block is not None:
            raise AllocationError(
                "This file already has allocated blocks."
            )

        data_block_count = (
            file_entry.size_bytes + self.disk.block_size - 1
        ) // self.disk.block_size

        if data_block_count == 0:
            file_entry.allocation_method = method
            return []

        if method == "contiguous":
            blocks = self._allocate_contiguous(
                file_entry.name, data_block_count
            )
            file_entry.allocated_blocks = blocks

        elif method == "linked":
            blocks = self._allocate_linked(
                file_entry.name, data_block_count
            )
            file_entry.allocated_blocks = blocks

            file_entry.block_links = {
                blocks[i]: blocks[i + 1]
                for i in range(len(blocks) - 1)
            }

            file_entry.block_links[blocks[-1]] = None

        else:
            blocks, index_block = self._allocate_indexed(
                file_entry.name, data_block_count
            )

            file_entry.allocated_blocks = blocks
            file_entry.index_block = index_block

        file_entry.allocation_method = method

        return file_entry.allocated_blocks.copy()

    def _allocate_contiguous(self, owner, count):
        """Allocate a sequence of consecutive free blocks."""

        free_blocks = self.disk.get_free_blocks()

        for start in range(len(free_blocks) - count + 1):
            candidate = free_blocks[start:start + count]

            if len(candidate) != count:
                continue

            consecutive = all(
                candidate[i] + 1 == candidate[i + 1]
                for i in range(len(candidate) - 1)
            )

            if consecutive:
                for block_number in candidate:
                    self.disk.blocks[block_number] = owner

                return candidate

        raise AllocationError(
            "Not enough consecutive free blocks."
        )

    def _allocate_linked(self, owner, count):
        """Allocate blocks connected by simulated pointers."""

        if len(self.disk.get_free_blocks()) < count:
            raise AllocationError("Not enough free blocks.")

        allocated = []

        try:
            for _ in range(count):
                allocated.append(
                    self.disk.allocate_block(owner)
                )

        except RuntimeError as error:
            for block_number in allocated:
                self.disk.free_block(block_number, owner)

            raise AllocationError(
                "Linked allocation failed."
            ) from error

        return allocated

    def _allocate_indexed(self, owner, count):
        """Allocate data blocks and one separate index block."""

        if len(self.disk.get_free_blocks()) < count + 1:
            raise AllocationError(
                "Not enough free blocks for indexed allocation."
            )

        allocated_data = []
        index_block = None

        try:
            for _ in range(count):
                allocated_data.append(
                    self.disk.allocate_block(owner)
                )

            index_block = self.disk.allocate_block(
                f"{owner} [index]"
            )

        except RuntimeError as error:
            for block_number in allocated_data:
                self.disk.free_block(block_number, owner)

            if index_block is not None:
                self.disk.free_block(
                    index_block, f"{owner} [index]"
                )

            raise AllocationError(
                "Indexed allocation failed."
            ) from error

        return allocated_data, index_block

    def release(self, file_entry):
        """Release all data blocks and the index block, if present."""

        owner = file_entry.name

        for block_number in file_entry.allocated_blocks:
            self.disk.free_block(block_number, owner)

        if file_entry.index_block is not None:
            self.disk.free_block(
                file_entry.index_block, f"{owner} [index]"
            )

        file_entry.allocated_blocks = []
        file_entry.index_block = None
        file_entry.block_links = {}