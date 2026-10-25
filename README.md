# FALCON — File Allocation, Logging, Consistency and Operating-system Navigation

**A Python-based File System Simulator for Operating Systems**

FALCON is an educational file system simulator developed using Python to demonstrate fundamental operating system concepts related to disk space management, file allocation, file operations, persistence, and logging.

The project simulates a virtual disk divided into fixed-size blocks and implements three classic file allocation strategies: contiguous allocation, linked allocation, and indexed allocation. It also supports file creation, reading, updating, deletion, and restoration of saved filesystem state.

## Features

- **Virtual Disk Management:** Simulates a disk containing a configurable number of fixed-size blocks.
- **Contiguous Allocation:** Stores a file's data in consecutive disk blocks.
- **Linked Allocation:** Represents a file as a linked sequence of allocated blocks.
- **Indexed Allocation:** Uses a separate index block to represent the locations of a file's data blocks.
- **File Operations:** Supports creating, reading, updating, deleting, and listing files.
- **Disk Space Monitoring:** Tracks used and free blocks and calculates storage utilization.
- **Persistent Storage:** Saves filesystem state in JSON format and restores it when the application restarts.
- **Logging:** Records application events, including successful operations and errors.
- **Error Handling:** Handles invalid operations and allocation failures.
- **Rollback Mechanisms:** Helps preserve filesystem consistency when supported operations fail.
- **Automated Testing:** Uses Python's built-in `unittest` framework to verify core functionality.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core implementation |
| JSON | Filesystem state serialization |
| Logging module | Application event logging |
| `unittest` | Automated testing |
| Visual Studio Code | Development environment |
| Git and GitHub | Version control and project hosting |

## Project Structure

```text
falcon-file-system-simulator/
│
├── data/
│   └── falcon_state.json
│
├── docs/
│
├── screenshots/
│
├── src/
│   ├── allocation.py
│   ├── demo_disk.py
│   ├── demo_file.py
│   ├── demo_manager.py
│   ├── disk.py
│   ├── file_entry.py
│   ├── file_manager.py
│   ├── logging_config.py
│   ├── main.py
│   └── persistence.py
│
├── tests/
│   ├── test_allocation.py
│   ├── test_disk.py
│   ├── test_file_manager.py
│   ├── test_logging_config.py
│   └── test_persistence.py
│
├── .venv/
└── README.md
```

*Note: `data/falcon_state.json` and `logs/falcon.log` are created or updated as the application runs. The exact contents of these directories may vary.*

## System Architecture

FALCON is organized into separate modules, with each module responsible for a specific part of the simulated filesystem.

```text
                 ┌──────────────────────┐
                 │       main.py        │
                 │   User Interface     │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │    FileManager       │
                 │   File Operations   │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │  AllocationManager   │
                 │  Allocation Methods  │
                 └──────────┬───────────┘
                            │
                 ┌──────────▼───────────┐
                 │     VirtualDisk      │
                 │   Block Management   │
                 └──────────────────────┘

        ┌─────────────────┐  ┌─────────────────┐
        │ PersistenceManager│ │ Logging System  │
        │ Save and Restore │ │ Event Recording │
        └─────────────────┘  └─────────────────┘
```

The main interface accepts user choices and invokes the file manager. The file manager coordinates file operations with the allocation manager, which manages block allocation on the virtual disk. The persistence manager saves and restores filesystem state, while the logging system records application events.

## File Allocation Methods

### 1. Contiguous Allocation

In contiguous allocation, a file occupies consecutive blocks on the virtual disk.

**Example:**

```text
File A → [0] [1] [2] [3]
```

**Advantages**
- Simple to understand and implement.
- Supports efficient sequential access.
- Makes locating consecutive file blocks straightforward.

**Limitations**
- Requires a sufficiently large consecutive region of free blocks.
- Can suffer from external fragmentation.

### 2. Linked Allocation

In linked allocation, a file occupies blocks that are connected through references to the next block.

**Example:**

```text
[2] → [7] → [4] → [9] → None
```

**Advantages**
- File blocks do not need to be consecutive.
- Can use scattered free blocks.

**Limitations**
- Accessing a particular block may require following preceding links.
- Incorrect links could affect traversal of the file's blocks.

### 3. Indexed Allocation

In indexed allocation, a separate index block records the locations of a file's data blocks.

**Example:**

```text
Index Block
     │
     ├── Data Block 3
     ├── Data Block 6
     └── Data Block 8
```

**Advantages**
- Data blocks can be located without requiring consecutive storage.
- Provides a centralized representation of a file's block locations.

**Limitations**
- Requires an additional index block.
- The index block consumes storage space.

## Installation and Execution

### Prerequisites

- Python 3
- Visual Studio Code or another Python-compatible editor
- A terminal such as Windows Command Prompt or PowerShell

### 1. Clone the Repository

After publishing the project to GitHub, clone it using:

```bash
git clone <YOUR-GITHUB-REPOSITORY-URL>
```

Navigate to the project directory:

```bash
cd falcon-file-system-simulator
```

Replace the placeholder with your actual GitHub repository URL.

### 2. Create a Virtual Environment

On Windows:

```bash
python -m venv .venv
```

### 3. Activate the Virtual Environment

For Command Prompt:

```cmd
.venv\Scripts\activate
```

For PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Run the Application

From the project root directory:

```bash
python src/main.py
```

Follow the menu displayed in the terminal to perform filesystem operations.

## Running the Tests

FALCON uses Python's built-in `unittest` framework.

Run all tests from the project root:

```bash
python -m unittest discover -s tests -v
```

To run individual test modules:

```bash
python -m unittest tests.test_disk -v
python -m unittest tests.test_allocation -v
python -m unittest tests.test_file_manager -v
python -m unittest tests.test_persistence -v
python -m unittest tests.test_logging_config -v
```

### Current Test Results

The project has successfully passed **38 automated unit tests** in the current development environment.

The tests cover disk management, allocation methods, file operations, persistence, logging, and failure-handling behavior.

## Data Persistence

FALCON stores the simulated filesystem state in:

```text
data/falcon_state.json
```

The saved state includes disk configuration, block ownership, file contents, allocation information, and creation timestamps.

When the application starts, it attempts to restore the previously saved state. This allows files and their allocation information to remain available across application restarts.

## Logging

Application events are recorded in:

```text
logs/falcon.log
```

The log records timestamps, severity levels, and messages about application activity.

Logging supports debugging and helps track filesystem operations and errors.

## Learning Objectives

This project demonstrates practical applications of the following operating system concepts:

- File system organization
- Disk block allocation
- Contiguous, linked, and indexed allocation
- Free-space and used-space tracking
- File metadata management
- Storage persistence
- Error handling and rollback
- Application logging
- Unit testing and software modularity

## Scope and Limitations

FALCON is an educational filesystem simulator. It manages a virtual disk represented in Python memory and persists its state using JSON.

It does not replace or modify the host operating system's actual filesystem. Its allocation strategies model selected filesystem concepts for learning and demonstration.

## Future Enhancements

Possible future improvements include:

- A graphical user interface.
- Visualization of allocated and free disk blocks.
- Search and filtering for files.
- More detailed disk fragmentation analysis.
- Additional consistency checks and recovery scenarios.
- Performance comparisons between allocation strategies.
- More extensive integration and edge-case testing.

## Conclusion

FALCON provides a modular, testable way to explore filesystem operations and disk allocation strategies. By combining virtual disk management, multiple allocation methods, persistent state, logging, and automated tests, it offers a practical foundation for understanding important operating system concepts.

---

**Project:** FALCON — File Allocation, Logging, Consistency and Operating-system Navigation  
**Domain:** Operating Systems  
**Language:** Python