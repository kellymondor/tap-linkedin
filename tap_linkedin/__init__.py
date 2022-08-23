import singer

from tap_linkedin.client import LinkedInClient
from tap_linkedin.discover import discover
from tap_linkedin.sync import sync
from tap_linkedin.context import Context

REQUIRED_CONFIG_KEYS = [
    'keyword',
    'cookie',
    'x_li_identity',
    'csrf_token'
]

LOGGER = singer.get_logger()

@singer.utils.handle_top_exception(LOGGER)
def main():
    # Parse command line arguments
    args = singer.utils.parse_args(REQUIRED_CONFIG_KEYS)

    Context.state = args.state
    
    with LinkedInClient(args.config) as client:
        # If discover flag was passed, run discovery mode and dump output to stdout
        if args.discover:
            catalog = discover(client, args.config)
            catalog.dump()
        # Otherwise run in sync mode
        else:
            if args.catalog:
                catalog = args.catalog
            else:
                catalog = discover(client, args.config)
              
            sync(client)

if __name__ == "__main__":
    main()