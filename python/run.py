"""
File for running app
"""
from nr_verify.deployment import run_client, deploy_contract

TYPE = "deploy"


if TYPE == "deploy":
    deploy_contract()
else:
    run_client()
