# rfi-globus-api
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Usage

```
Usage: python -m GlobusAPI [OPTIONS] COMMAND [ARGS]...

Options:
  --confidential-client-id TEXT         Globus API Confidential Client ID. This is the UUID of the service account. [required]
  --confidential-client-secret TEXT     Globus API Confidential Secret. This is the secret of the service account. [required]
  --help                                Show this message and exit.

Commands:
# Guest Collection Commands
  createguestcollection
  deleteguestcollection
  updateguestcollection
  getguestcollection
  guestcollectionlist

# Role Commands
  createrole
  deleterole
  getrole
  rolelist

# Groups Commands
  creategroup
  addgroupmembers
  getgroup
  grouplist
  changerolegroupmembers
  removegroupmembers
  setgroupmembers
  deletegroup

# Transfer Commands
  completetransfer
  submittransfer
  
# Delete Commands
  completedelete
  submitdelete

# Task Commands
  canceltasks
  successfultransfers
  gettask
  tasklist
  taskeventlist
  monitoredcollectionlist
  getmonitoredcollection
  geturl

# ACL Rule - Permissions Commands
  aclrulelist
  getaclrule
  addaclrule
  deleteaclrule
  updateaclrule

# Timer Commands
  listtimers
  gettimer
  createtimer
  deletetimer
  pausetimer
  resumetimer

Args:
  -v, --verbose                        Verbose output. Use multiple times for more
                                       output. -v for INFO, -vv for DEBUG. If you use
                                       it three or more times, then the verbose
                                       output would be equal of using it only 2 times
                                       e.g. -vvv for DEBUG, -vvvv for DEBUG, etc.
  --help                               Show this message and exit.

Use --help argument against any command to read the command specific arguments
```
---

## Build and Tests

You can use either `docker` or `podman` to containerize rfi-globus-api. In the following instructions replace `<containerization_tool>`
with either `podman` or `docker` depending on what you are using.

### Build the container

```bash
# pwd is repo root dir
<containerization_tool> build rfi-globus-api:X.Y.Z .
```

### Preparation before running tests

#### Setup of Globus Infrastructure

To run all the tests you will need to set up a Globus infrastructure of your own, so that the tests
can run against it. You will need:

**Globus Endpoint** set up with:
  * One **Storage gateway**
  * One **mapped collection** (with the ability to create guest collections for it)
  * Two **guest collections**.
    * One that will used as source collection populated with sample files/directories.
    * One that will used as destination collection.
* A **service account** set up in the Developer Tab of app.globus.org .
* The **service account** should be set as **administrator** to the **endpoint**, **mapped collection** and **guest collections**.
* The **service account** is allowed to create guest collections. This means that the appropriate **user-credentials** for the
  service account are set in the storage gateway, and that the service account is in the **list of users allowed to create
  guest collections** on the mapped collection.
* Two **testing users** that have a ORCID or GlobusID username/identity in Globus (e.g. `<ORCID>@orcid.org` or `<username>@globusid.org`).

If this is a S3 storage-gateway it must have a user-credential added to it with the access/secret keys to contact the
S3 endpoint.

#### Creation of custom ".env" file

Then create your ".env" file that will contain environmental variable that will be used during testing. Populate it as 
following, do not use quotes ("" or '') to signify them as strings, do not type whitespace after the `=` symbol:
```bash
GLOBUSAPI_CONFIDENTIAL_CLIENT_ID= # The UUID of your service account this needs to be added as admin to the endpoint,
                                  # mapped collection and guest collections that will be used as source and destination
                                  # collections for the transfer tests
GLOBUSAPI_CONFIDENTIAL_CLIENT_SECRET=  # The secret of the service account
GLOBUSAPI_ENDPOINT_ID=                 # The UUID of the Globus endpoint

GLOBUSAPI_STORAGE_GATEWAY_NAME=        # The display name of the Globus Storage Gateway on the Globus endpoint
GLOBUSAPI_STORAGE_GATEWAY_ID=          # The UUID of the Globus Storage Gateway 

GLOBUSAPI_MAPPED_COLLECTION_ID=        # The UUID of the Globus mapped collection on the Globus endpoint

GLOBUSAPI_SOURCE_COLLECTION_ID=        # The UUID of the Globus guest collection on the Globus mapped collection that contains sample data ready for transfer
GLOBUSAPI_SOURCE_COLLECTION_NAME=      # The display name of the Globus guest collection on the Globus mapped collection that contains sample data ready for transfer

GLOBUSAPI_DESTINATION_COLLECTION_ID=    # The UUID of the Globus guest collection on the Globus mapped collection that will receive the sample data from the other guest collection
GLOBUSAPI_DESTINATION_COLLECTION_NAME=  # The display name of the Globus guest collection on the Globus mapped collection that will receive the sample data from the other guest collection

GLOBUSAPI_TESTING_COLLECTION_NAME=      # A display name of your own choosing for the third "testing" guest collection that will be created and deleted during the tests
GLOBUSAPI_TESTING_COLLECTION2_NAME=     # A display name of your own choosing. This will be used when testing the ability to rename the display name of the third "testing" guest collection

GLOBUSAPI_TESTING_COLLECTION_BASEPATH=  # A valid base path for the third "testing" guest collection that will be created during tests

GLOBUSAPI_NON_EXISTING_STORAGE_GATEWAY= # A display name of a Storage Gateway that does not exist on the Globus endpoint. This is need to test that the correct errors/exceptions are raised when searching for Storage Gateway based on its name, which though do not exist
GLOBUSAPI_NON_EXISTING_COLLECTION_NAME= # A display name of a Collection that does not exist either as a mapped collection or guest collection on the Globus endpoint. This is need to test that the correct errors/exceptions are raised when searching for a collection based on its name, which though do not exist

GLOBUSAPI_TESTING_USER_IDENTITY=        # The full ORCID or GlobusID username/identity (e.g. <ORCID>@orcid.org or <username>@globusid.org) of the first "testing user" that will be used during the testing
GLOBUSAPI_TESTING_USER_NAME=            # The name of the first "testing user". It should be <First_name> <Last_name>  . With a whitespace between the first and last name
GLOBUSAPI_TESTING_USER_IDENTITY2=       # The full ORCID or GlobusID username/identity (e.g. <ORCID>@orcid.org or <username>@globusid.org) of the second "testing user" that will be used during the testing
GLOBUSAPI_TESTING_USER_NAME2=           # The full ORCID or GlobusID username/identity (e.g. <ORCID>@orcid.org or <username>@globusid.org) of the second "testing user" that will be used during the testing
GLOBUSAPI_ORGANISATION_EMAIL_ADDRESS_DOMAIN=   # The email address domain of the 2 testing users (do not add the "@" symbol in front). This is what follows after the "@" in the email addresses of the testing users

GLOBUSAPI_NON_EXISTING_ORCID_IDENTITY=   # A non exising ORCID username/identity, e.g. Not-A-Member@orcid.org
GLOBUSAPI_INCORRECT_ORCID_IDENTITY=      # An incorrect ORCID username/identity, aka does not exist, e.g. 0123-4567-8910-1112@orcid.org

GLOBUSAPI_TESTING_GROUP_NAME=            # A name for the group that will be created as part of the group methods tests

GLOBUSAPI_NON_EXISTING_GROUP_NAME=       # A name of group that does not exist, e.g. Non_Existing_Group

GLOBUSAPI_WAIT_PERIOD_FOR_TRANSFERS=     # The time interval in seconds (e.g. 60 for 1 minute, 120 for 2 minutes, etc.), that the tests will wait between status checks of the testing transfers. This is because for certain tests, testing transfers have to be concluded. If it is very small it can lead to very lengthy test logs, if it is too large the tests may take more time to complete.

```

#### Preparation of custom transfer_list.json file

Finaly modify the `tests/GlobusAPI/data/transfer_list.json` file based on the files and directories available for transfer in
the source collection. It should be a list of dictionaries. Each dictionary has 2 keys, `source_path` and
`destination_path`.

To transfer files use paths that include also the file, e.g.:
```
[{"source_path": "<source_collection_path>/file.ext", "destination_path": "<source_collection_path>/file.ext"}]
```

To transfer whole directories recursively then the paths should end with the "/" character, e.g.
```
[{"source_path": "<source_collection_path>/", "destination_path": "<source_collection_path>/"}]
```


### Run the tests with the container
```bash
# pwd is repo root dir
<containerization_tool> run -it --rm --name globus-api \
    -w /usr/local/GlobusAPI \
    -v $(pwd):/usr/local/GlobusAPI \
    --env-file .env
    --entrypoint="python" \
    globus-api:X.Y.Z \
        -m pytest \
            /usr/local/GlobusAPI/tests/GlobusAPI \
            --cov /usr/local/GlobusAPI/src \
            --cov-report term-missing \
            --log-cli-level=INFO

```

---
## How to contribute
### Via the public RFI-GlobusAPI GitHub Repo

RFI-GlobusAPI is also available to the public in its [public GitHub Repository]( https://github.com/rosalindfranklininstitute/rfi-globus-api).

You are welcomed to fork this repository and create new Pull Requests. Once these Pull Requests pass their review, they
will be authorised for merger to the main branch.

The review will include a private run of the tests, since it is computationally expensive for them to be run upon every
new commit.

---



