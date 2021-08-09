# DynamicFlare

Update dynamic DNS entries for accounts on CloudFlare's DNS service.


## Installation

1. Clone this repository

2. `cd` into the root directory
```
cd dynamicflare
```

3. Create a python virtual environment
```bash
python3 -m venv venv
```

4. Activate the created virtual environment
```bash
source venv/bin/activate
```

5. Install requirements
```bash
pip install -r requirements.txt
```


## Configuration

1. Create a CloudFlare API token as explained [here](https://support.cloudflare.com/hc/en-us/articles/200167836-Managing-API-Tokens-and-Keys). Use the `Edit zone DNS` template. In the `Zone Resources` section include the zones you want to update with this script.

2. Create a `config.json` file next to the `main.py` file in `dynamicflare` repository. 
`config.json` file must contain:
    - `cloudflare_token` - your CloudFlare API token
    - `records` - list of A record objects, each containing:
        - `domain` - base domain name for this A record
        - `record` - A record name

`config.json` example:
```
{
    "cloudflare_token": "_your_cloudflare_api_token_",
    "records": [
        {
            "domain": "domainone.com",
            "record": "domainone.com"
        },
        {
            "domain": "domainone.com",
            "record": "subone.domainone.com"
        },
        {
            "domain": "domaintwo.com",
            "record": "domaintwo.com"
        }
    ]
}
```


## Running

1. Create a new, or edit an existing, `crontab` file.
```bash
crontab -e
```

2. Add a command line which runs the script to the `crontab` file. I would suggest using full paths to the venv's python interpreter and to the python script. Here is an example which will run the script every 5 minutes:
```bash
*/5 * * * * /full/path/to/dynamicflare/venv/bin/python /full/path/to/dynamicflare/main.py
```

3. Verify your crontab file changes.
```bash
crontab -l
```


## Logging

1. Pipe the output of your cron command through logger so it ends up in the `syslog`. Add `2>&1 | logger -t dynamicflare` to the cron command:
```bash
*/5 * * * * /full/path/to/dynamicflare/venv/bin/python /full/path/to/dynamicflare/main.py 2>&1 | logger -t dynamicflare
```

2. Query `syslog` with the `dynamicflare` tag to see the logs:
```bash
grep "dynamicflare" /var/log/syslog
```


## License

**DynamicFlare** is a free software under terms of the `MIT License`.

Copyright (C) 2021 by [Toni Sredanović](https://tsredanovic.github.io/), toni.sredanovic@gmail.com

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
