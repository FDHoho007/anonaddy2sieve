# Anonaddy2Sieve

This python script turns anonaddy/addy.io aliases into a sieve script. It fetches all aliases from `ANONADDY_URL` with `ANONADDY_API_KEY`.
For each alias the description is scanned for a sieve folder mapping that looks like this: "Lorem ipsum Sieve: Foo.Bar dolor sit amet ..."
The mapping needs to start with `KEYWORD` (default Sieve) followed by a colon.
The next word (no spaces) is parsed as the designated folder sieve should map incoming mails for that alias into.
If the folder name contains spaces it needs to be put in double quotes (").
The script will periodically (all `SLEEP_INTERVAL` seconds) generate a sieve script to `OUTPUT_FILE`.
You can then either program your sieve to use this as default or you could include in other scripts.