import boto3
import time
import json
from datetime import datetime
from botocore.exceptions import ClientError
import logging


def remove_all_archives_and_the_vault(vault_name, glacier_client, glacier_resource):
    """
    Removes all archives from a specified Glacier vault and deletes the vault.
    
    Parameters:
        vault_name (str): The name of the Glacier vault.
        glacier_client (boto3.client): The Glacier client for API interactions.
        glacier_resource (boto3.resource): The Glacier resource for managing resources.
    """
    # 1. Log the start of the vault deletion process
    logger.info('#######################################################################################')
    vault_process_start_time = datetime.now()
    logger.info(f"{vault_process_start_time}: Starting process to delete archives and vault: {vault_name}")

    # 2. Check if the vault exists
    if not check_vault_exists(vault_name, glacier_client):
        logger.error(f"Error: Vault {vault_name} does not exist. Skipping.")
        return

    # 3. Initiate an inventory retrieval job for the vault
    response = glacier_client.initiate_job(
        vaultName=vault_name,
        jobParameters={'Type': 'inventory-retrieval'}
    )
    job_id = response['jobId']

    # 4. Poll until the inventory retrieval job is complete
    while True:
        logger.info(f"Checking job status as of {datetime.now()}...")
        job_description = glacier_client.describe_job(
            vaultName=vault_name,
            jobId=job_id
        )
        if job_description['Completed']:
            break
        time.sleep(60 * 20)  # Wait 20 minutes before checking again

    # 5. Retrieve the inventory report
    glacier_inventory_start_time = datetime.now()
    job_output = glacier_client.get_job_output(
        vaultName=vault_name,
        jobId=job_id,
        range='bytes=0-'
    )
    inventory_data = job_output['body'].read()
    inventory_dict = json.loads(inventory_data.decode('utf-8'))
    archive_list = inventory_dict['ArchiveList']

    # 6. Log the number of archives and begin deletion
    logger.info(f'Number of Archives: {len(archive_list)}')
    logger.info(f'Processing deletions in vault {vault_name}')

    # 7. Process and delete each archive
    archive_idx, success_count, failure_count = 0, 0, 0
    for archive in archive_list:
        archive_id = archive['ArchiveId']
        archive_resource = glacier_resource.Archive("-", vault_name, archive_id)
        try:
            archive_resource.delete()
            logger.debug(f'ArchiveID #{archive_idx}: Delete SUCCEEDED')
            success_count += 1
        except Exception as e:
            logger.error(f'ArchiveID #{archive_idx}: Delete FAILED - {e}')
            failure_count += 1
        archive_idx += 1

        # 8. Log progress every 10,000 archives
        if archive_idx % 10000 == 0:
            logger.info(f"{datetime.now()} Progress: {archive_idx} processed...")

        # 9. Avoid API throttling by sleeping every 100 deletions
        if archive_idx % 100 == 0:
            time.sleep(1)

    # 10. Log the deletion results
    logger.info(f'Total Archives: {archive_idx}')
    logger.info(f'Total SUCCESS: {success_count}')
    logger.info(f'Total FAIL: {failure_count}')

    # 11. Log the elapsed time and archive deletion rate
    vault_process_end_time = datetime.now()
    elapsed_time = vault_process_end_time - vault_process_start_time
    glacier_time = glacier_inventory_start_time - vault_process_start_time
    log_elapsed_time(vault_name, archive_idx, elapsed_time, glacier_time)


def log_elapsed_time(vault_name, archive_count, elapsed_time, glacier_time):
    """
    Logs the elapsed time for processing a vault and the deletion rate.
    
    Parameters:
        vault_name (str): The name of the Glacier vault.
        archive_count (int): Total number of archives processed.
        elapsed_time (timedelta): Total elapsed time for the process.
        glacier_time (timedelta): Time taken for the Glacier inventory job.
    """
    archives_per_second = archive_count / elapsed_time.total_seconds() if elapsed_time.total_seconds() > 0 else 0.0
    logger.info(
        f'Elapsed time for {vault_name} containing {archive_count} archives was {elapsed_time} '
        f'including Glacier job time of {glacier_time}. '
        f'Deletion rate: {archives_per_second:.4f} archives/second.'
    )


def check_vault_exists(vault_name, glacier_client):
    """
    Checks if a Glacier vault exists by describing it.
    
    Parameters:
        vault_name (str): The name of the Glacier vault.
        glacier_client (boto3.client): The Glacier client for API interactions.
    
    Returns:
        bool: True if the vault exists, False otherwise.
    """
    try:
        glacier_client.describe_vault(vaultName=vault_name)
        return True
    except ClientError as e:
        if e.response['Error']['Code'] == 'ResourceNotFoundException':
            return False
        logger.error(f"Error checking vault existence for {vault_name}: {e}")
        return False


def get_glacier_client(region='us-east-1'):
    """
    Initializes and returns a boto3 Glacier client for a specified region.
    
    Parameters:
        region (str): The AWS region to connect to. Defaults to 'us-east-1'.
    
    Returns:
        boto3.client: The Glacier client instance.
    """
    return boto3.client('glacier', region_name=region)


def get_glacier_resource():
    """
    Initializes and returns a boto3 Glacier resource.
    
    Returns:
        boto3.resource: The Glacier resource instance.
    """
    return boto3.resource('glacier')


def setup_logger(log_level):
    """
    Sets up and returns a logger for the application.
    
    Parameters:
        log_level (int): Logging level (e.g., logging.INFO or logging.DEBUG).
    
    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger("GlacierArchiveCleanup")
    logger.setLevel(log_level)
    handler = logging.FileHandler('app.log', mode='w')
    formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(message)s]')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


if __name__ == "__main__":
    # Initialize logging
    logger = setup_logger(logging.INFO)

    # Define the AWS region for Glacier client
    region = 'us-east-1'
    glacier_client = get_glacier_client(region)
    glacier_resource = get_glacier_resource()

    # Read vault names from a file and process each vault
    try:
        with open('VaultsToBeDeleted.txt', 'r') as file:
            vault_names = [line.strip() for line in file if line.strip()]
        if not vault_names:
            logger.error("No vaults to process. Ensure 'VaultsToBeDeleted.txt' contains vault names.")
        for vault in vault_names:
            logger.info(f"Processing vault: {vault}")
            remove_all_archives_and_the_vault(vault, glacier_client, glacier_resource)
    except FileNotFoundError:
        logger.error("Error: 'VaultsToBeDeleted.txt' file not found.")
