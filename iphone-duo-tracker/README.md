# iPhone Duo stock tracker

Polls Apple's pickup-availability endpoint for the iPhone Duo at three Colorado Apple Stores:

- Apple Cherry Creek (Denver)
- Apple Flatiron Crossing (Broomfield)
- Apple Twenty Ninth Street (Boulder)

It prints a status line on every check and sends a notification when a model newly becomes available for pickup at a store. Standard library only (Python 3.8+).

## Setup (required before first run)

`config.json` ships with `TODO_...` placeholders. The tracker refuses to run until they are replaced:

1. **Store numbers.** Apple's `R...` store numbers for the three stores. These could not be verified from the build environment; confirm them from Apple's store pages or the store's fulfillment data.
2. **Part numbers.** The US Apple part number for each configuration you want (for example `MXXX3LL/A`). Add one `models` entry per configuration.
3. Optional: set `ntfy_topic` (or the `NTFY_TOPIC` env var) to receive phone push alerts through [ntfy.sh](https://ntfy.sh). Pick a hard-to-guess topic name, since anyone who knows it can read the alerts.

## Run

```bash
cd iphone-duo-tracker
python3 test_tracker.py          # unit tests
python3 tracker.py --once        # one check
python3 tracker.py               # poll every interval_seconds (default 300)
```

## Caveats

- The endpoint is Apple's internal storefront API, not a documented public API. It can change without notice. The parser expects `body.content.pickupMessage.stores[].partsAvailability[part].pickupDisplay`; if Apple changes this, the output will show `no results returned` or `unknown` rather than false "in stock" alerts.
- The parser has been checked against a mocked response only. Run `--once` on your own machine to confirm the live response matches before relying on alerts.
- Don't poll too often. The default of 5 minutes is reasonable.
