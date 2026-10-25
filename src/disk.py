class VirtualDisk:
    """
    Represents a simulated disk divided into fixed-size blocks.
    """

    def __init__(self, total_blocks=100, block_size=512):
        if not isinstance(total_blocks, int) or isinstance(total_blocks, bool) or total_blocks <= 0:
            raise ValueError("Total blocks must be a positive integer.")

        if not isinstance(block_size, int) or isinstance(block_size, bool) or block_size <= 0:
            raise ValueError("Block size must be a positive integer.")

        self.total_blocks = total_blocks
        self.block_size = block_size

        # None means that a block is free.
        # A non-None value identifies the block's owner.
        self.blocks = [None] * total_blocks

    def allocate_block(self, owner):
        """
        Allocate the first available block to an owner.
        Returns the allocated block number.
        """
        if not isinstance(owner, str) or not owner.strip():
            raise ValueError("Owner must be a non-empty string.")

        for block_number, current_owner in enumerate(self.blocks):
            if current_owner is None:
                self.blocks[block_number] = owner
                return block_number

        raise RuntimeError("Disk is full. No free blocks available.")

    def free_block(self, block_number, owner):
        """
        Release a block if it belongs to the specified owner.
        """
        if not isinstance(block_number, int) or isinstance(block_number, bool):
            raise TypeError("Block number must be an integer.")

        if block_number < 0 or block_number >= self.total_blocks:
            raise IndexError("Invalid block number.")

        if self.blocks[block_number] is None:
            raise ValueError("Block is already free.")

        if self.blocks[block_number] != owner:
            raise ValueError("Block does not belong to the specified owner.")

        self.blocks[block_number] = None

    def get_free_blocks(self):
        """Return the block numbers that are currently free."""
        return [
            block_number
            for block_number, owner in enumerate(self.blocks)
            if owner is None
        ]

    def get_used_blocks(self):
        """Return the number of allocated blocks."""
        return sum(owner is not None for owner in self.blocks)

    def get_free_block_count(self):
        """Return the number of free blocks."""
        return self.total_blocks - self.get_used_blocks()

    def get_capacity_bytes(self):
        """Return the total simulated disk capacity in bytes."""
        return self.total_blocks * self.block_size

    def get_used_capacity_bytes(self):
        """Return the capacity occupied by allocated blocks."""
        return self.get_used_blocks() * self.block_size

    def display(self):
        """Display the current state of every disk block."""
        print("\nFALCON VIRTUAL DISK")
        print("-" * 35)

        for block_number, owner in enumerate(self.blocks):
            status = f"ALLOCATED ({owner})" if owner is not None else "FREE"
            print(f"Block {block_number:03}: {status}")

        print("-" * 35)
        print(f"Total blocks : {self.total_blocks}")
        print(f"Used blocks  : {self.get_used_blocks()}")
        print(f"Free blocks  : {self.get_free_block_count()}")
        print(f"Total size   : {self.get_capacity_bytes()} bytes")
        print(f"Used size    : {self.get_used_capacity_bytes()} bytes")
