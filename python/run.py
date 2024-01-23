"""
File for running app
"""
import argparse
from nr_verify.deployment import run_client, deploy_contract
from python.nr_verify.deployment.client import get_client, get_new_client, run_hier_ver

parser = argparse.ArgumentParser(description='Example Argument Parser')
# Add an argument for specifying a directory with -d or --directory
parser.add_argument('-d', '--deploy', action="store_true",
                    help='This implies deploy')
# Add an argument for a configuration file with -c or --config
parser.add_argument('-c', '--client', action="store_true",
                    help='This implies client')

parser.add_argument('-g', '--get', action="store_true",
                    help='This shows signatures')

parser.add_argument('-n', '--get_new', action="store_true",
                    help='This shows signatures')

parser.add_argument('-v', '--run_hier', action="store_true",
                    help='This hier verifies signatures')


# Parse the command-line arguments
args = parser.parse_args()
deploy_flag = args.deploy
client_flag = args.client
get_flag = args.get
get_new_flag = args.get_new

if deploy_flag:
    deploy_contract()
elif client_flag:
    run_client()
elif get_flag:
    get_client()
elif get_new_flag:
    get_new_client()
elif args.run_hier:
    run_hier_ver()
