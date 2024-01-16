class RingBuffer:
    """
    A datastructure that acts as a single fixed size circular buffer

    This implementation assumes the buffer is always full and thus needs to be initialized with a
    default value. Use `add` to overwrite the oldest value, and `get` to retrieve the value at a
    particular index. The 0th index is the oldest value and nth - 1 index is the newest value.
    """
    def __init__(self, size, default):
        """
        Initializes a new RingBuffer

        Parameters
        ----------
        size : type
            Number of items the buffer can hold
        default
            Default value for buffer items
        """
        self.buffer = [default] * size
        self.endIndex = len(self.buffer) - 1

    def add(self, item):
        """
        Add an item to the ring buffer

        Overwrites the oldex item in the array (index 0)

        Parameters
        ----------
        item
            Item to add to the buffer
        """
        self.endIndex  = (self.endIndex + 1) % len(self.buffer)
        self.buffer[self.endIndex] = item

    def get(self, index):
        """
        Get an item in the array at a particular index

        The 0th index is the oldest item in the array and the nth-1 index is the newest item in the array.

        Parameters
        ----------
        index : int
            Index of the item to retrieve

        Returns
        -------
        any
            Item at the specified index in the array
        """
        if index < 0 or index >= len(self.buffer):
            raise IndexError("Out of range")

        # Since it's a full ring buffer, the start index is right after the end
        start_index = (self.endIndex + 1) % len(self.buffer)
        actual_index = (start_index + index) % len(self.buffer)
        return self.buffer[actual_index]

    def __len__(self):
        return len(self.buffer)