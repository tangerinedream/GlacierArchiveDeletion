# GlacierArchiveDeletion
A way to delete Glacier Archives using the Python boto3 SDK

# UseCase
When you need to delete Glacier Archives so that you can delete a vault, you will be looking for python code to do so - and this is it.  Glacier Vaults cannot be deleted if they contain any Archives.  The only way to delete the vault is by deleting all archives within the Vault which requires either the CLI or SDK.

AWS Documentation is fairly spotty, with the following page being your best and only starting point, but it is deficient and you'll spend many hours trying to figure this out (CoPilot, ChatGPT, and Q are not helpful here).  So, just use this and be happy.

https://docs.aws.amazon.com/code-library/latest/ug/python_3_glacier_code_examples.html
