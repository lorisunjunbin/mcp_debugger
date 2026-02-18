# MCP debugger

MCP streaming server and client using Python. Router is used to inspect the traffic between server and client.

### Prerequisites

- Python 3.14 or newer
- The `mcp` Python package (install with `pip install mcp`)

### Installation & Setup

1. **Create and activate a virtual environment (recommended):**

   ```pwsh
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # On Windows
   # or
   source venv/bin/activate      # On Linux/macOS
   ```

2. **Install required dependencies:**

   ```pwsh
   pip install "mcp[cli]" fastapi requests
   ```

### Files

- **Server:** [server.py](mcp_server.py)
- **Client:** [client.py](mcp_client.py)
- **Router:** [router.py](mcp_router.py)

### Running the Classic HTTP Streaming Server

1. Start the mcp server:

   ```pwsh
   python mcp_server.py
   ```

2. Start router as debugger:

   ```pwsh
   python mcp_router.py
   ```

3. Run client:

   ```
   python mcp_client.py
   ```

4. Check request/response logs in router terminal.



