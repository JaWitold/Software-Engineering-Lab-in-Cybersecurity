"""
File for running app
"""
import argparse
from nr_verify.deployment import run_client, deploy_contract


parser = argparse.ArgumentParser(description='Example Argument Parser')
# Add an argument for specifying a directory with -d or --directory
parser.add_argument('-d', '--deploy', action="store_true",
                    help='This implies deploy')
# Add an argument for a configuration file with -c or --config
parser.add_argument('-c', '--client', action="store_true",
                    help='This implies client')
# Parse the command-line arguments
args = parser.parse_args()
deploy_flag = args.deploy
client_flag = args.client
if deploy_flag:
    deploy_contract()
elif client_flag:
    run_client()
