# aiomega

An asynchronous Python wrapper for the Mega SDK, providing C++ Python bindings for interacting with Mega.nz API.

## Overview

aiomega is a Python library that enables interaction with the Mega.nz API asynchronously. Utilizing the C++ Python bindings from the Mega SDK, this wrapper offers a Pythonic approach to manage your Mega account, manipulate files, and navigate through the file system of your Mega storage.

**Note:** The Mega SDK C++ Python bindings currently only support Linux. Therefore, this project is designed to be used within a Docker container, especially suited for development in Visual Studio Code using Dev Containers.

## Installation and Setup

### Using with Docker and VSCode

1. Ensure Docker is installed and running.
2. Install the "Remote - Containers" extension in Visual Studio Code.
3. Open the project folder in VSCode, then press `F1` and select "Remote-Containers: Open Folder in Container" to start developing inside a container.

### Build and Install within Docker

Once the project is opened in a Docker container through VSCode, it will automatically run `build.sh` to build the Mega SDK with Python bindings and place them in the `aiomega` directory. You can execute the script manually from the terminal:
```sh
vscode ➜ /workspaces/py-aiomega (main) $ ./build.sh
```
**Note:** You may need to ensure that the Docker container has access to the internet to clone repositories and install dependencies.

## Usage

Here’s a basic usage example that logs in and prints the used and total storage:
```python
from aiomega import AsyncMegaApi, MegaRequest, MegaAccountDetails

async def main():
    async with AsyncMegaApi(
        email="***@***.***, 
        password="***",
    ) as mega:
        # Send request to execution thread and wait for the response
        response: MegaRequest = await mega.getAccountDetails() 
        # Get account details from the response object
        account_details: MegaAccountDetails = response.getMegaAccountDetails()
        # Log storage usage
        logging.info(
            "Storage Used: {} of {}".format(
                account_details.getStorageUsed(),
                account_details.getStorageMax()
            )
        )

asyncio.run(main())
```