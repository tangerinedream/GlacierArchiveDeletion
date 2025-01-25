# Glacier Archive Cleanup Tool

## Overview
The Glacier Archive Cleanup Tool is a Python-based utility for managing Amazon Glacier vaults. This tool allows you to delete all archives within a specified Glacier vault and subsequently delete the vault itself. The tool provides detailed logging and handles throttling and retry mechanisms to ensure a smooth and reliable cleanup process.

## Features
- Retrieves and processes the inventory of archives in an Amazon Glacier vault.
- Deletes all archives in the vault.
- Deletes the vault after all archives are removed.
- Logs key events, progress, and metrics, including the deletion rate of archives.
- Configurable logging levels to control the verbosity of log output.

## Prerequisites
Before using this tool, ensure that the following requirements are met:

1. **AWS Credentials**: Ensure that your AWS credentials are configured. You can set them up via the AWS CLI or environment variables.
   ```bash
   aws configure
   ```
2. **IAM Permissions**: The IAM role or user must have the following permissions:
   - `glacier:DescribeVault`
   - `glacier:InitiateJob`
   - `glacier:GetJobOutput`
   - `glacier:DeleteArchive`
   - `glacier:DeleteVault`
3. **Python Version**: Python 3.9 or higher is recommended.
4. **Dependencies**: Install the required Python libraries using `pip`:
   ```bash
   pip install boto3
   ```

## Configuration
1. Create a file named `VaultsToBeDeleted.txt` in the same directory as the script. List the names of the Glacier vaults to be processed, one per line. Example:
   ```
   Vault1
   Vault2
   Vault3
   ```
2. (Optional) Modify the region in the script if you are working in a region other than `us-east-1`.

## Usage
1. Clone the repository or copy the script to your local machine.
2. Run the script:
   ```bash
   python GlacierArchiveDelete.py
   ```
3. Monitor the progress through the `app.log` file, which is created in the same directory as the script.

## Logging
The tool logs all actions to a file named `app.log` with timestamps and log levels. Key metrics, including elapsed time and deletion rate, are logged for each processed vault.

## Script Overview

### Main Components
- **`remove_all_archives_and_the_vault`**: The primary function for retrieving the vault inventory, deleting archives, and deleting the vault.
- **`log_elapsed_time`**: Logs metrics, including the elapsed time and deletion rate.
- **`check_vault_exists`**: Validates the existence of a specified Glacier vault.
- **`get_glacier_client`** and **`get_glacier_resource`**: Initialize and return AWS Glacier client and resource instances.
- **`setup_logger`**: Configures the logging mechanism.

### Process Flow
1. **Vault Existence Check**: Ensures the specified vault exists before proceeding.
2. **Inventory Retrieval**: Initiates a Glacier job to retrieve the inventory of archives.
3. **Archive Deletion**: Iterates through the inventory and deletes each archive while handling throttling.
4. **Vault Deletion**: Deletes the vault after all archives are removed.
5. **Logging**: Outputs progress, metrics, and errors to the log file.

## Example Output
### Console
```plaintext
Processing vault: Vault1
Processing vault: Vault2
```
### Log File (`app.log`)
```plaintext
[2025-01-24 12:00:00][INFO][Starting process to delete archives and vault: Vault1]
[2025-01-24 12:20:00][INFO][Elapsed time for Vault1 containing 1000 archives was 0:20:00 including Glacier job time of 0:15:00. Deletion rate: 0.8333 archives/second.]
```

## Error Handling
- **Missing Vault**: Logs an error if the specified vault does not exist.
- **File Not Found**: Logs an error if the `VaultsToBeDeleted.txt` file is missing.
- **API Throttling**: Implements a sleep mechanism to handle API rate limits.

## Limitations
- The tool does not support vaults containing archives larger than the maximum retrieval job size.
- Requires `VaultsToBeDeleted.txt` to contain valid vault names.

## License
This tool is open-source and available under the MIT License.

## Contact
For issues or feature requests, please open an issue in the repository or contact the maintainer.

