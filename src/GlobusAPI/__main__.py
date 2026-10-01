"""
   Copyright [2025] [Rosalind Franklin Institute]

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import click

from .cli.collections import (
    createguestcollection,
    createrole,
    deleteguestcollection,
    deleterole,
    getguestcollection,
    getrole,
    guestcollectionlist,
    rolelist,
    updateguestcollection,
)
from .cli.groups import (
    addgroupmembers,
    changerolegroupmembers,
    creategroup,
    deletegroup,
    getgroup,
    grouplist,
    removegroupmembers,
    setgroupmembers,
)
from .cli.timers import (
    createtimer,
    deletetimer,
    gettimer,
    listtimers,
    pausetimer,
    resumetimer,
)
from .cli.transfers import (
    aclrulelist,
    addaclrule,
    canceltasks,
    completedelete,
    completetransfer,
    deleteaclrule,
    getaclrule,
    getmonitoredcollection,
    gettask,
    geturl,
    monitoredcollectionlist,
    submitdelete,
    submittransfer,
    successfultransfers,
    taskeventlist,
    tasklist,
    updateaclrule,
)
from .logging.logging import get_logger

logger = get_logger(stdout=True)


@click.group()
@click.option(
    "--confidential-client-id",
    required=True,
    type=str,
    help="Globus API Confidential Client ID.",
)
@click.option(
    "--confidential-client-secret",
    required=True,
    type=str,
    help="Globus API Confidential Client Secret.",
)
@click.pass_context
def cli(ctx, **kargs):
    ctx.ensure_object(dict)
    ctx.obj.update(kargs)

    # Set the logging level for the whole application
    get_logger(stdout=True)


if __name__ == "__main__":
    logger.debug("Starting...")
    # Transfer commands
    cli.add_command(successfultransfers)
    cli.add_command(submittransfer)
    cli.add_command(submitdelete)
    cli.add_command(completetransfer)
    cli.add_command(completedelete)
    cli.add_command(canceltasks)
    cli.add_command(gettask)
    cli.add_command(tasklist)
    cli.add_command(taskeventlist)
    cli.add_command(monitoredcollectionlist)
    cli.add_command(getmonitoredcollection)
    # ACL Rule commands
    cli.add_command(aclrulelist)
    cli.add_command(getaclrule)
    cli.add_command(addaclrule)
    cli.add_command(deleteaclrule)
    cli.add_command(updateaclrule)
    # URL commands
    cli.add_command(geturl)
    # Group commands
    cli.add_command(creategroup)
    cli.add_command(deletegroup)
    cli.add_command(getgroup)
    cli.add_command(grouplist)
    cli.add_command(setgroupmembers)
    cli.add_command(addgroupmembers)
    cli.add_command(changerolegroupmembers)
    cli.add_command(removegroupmembers)
    # Guest Collection commands
    cli.add_command(createguestcollection)
    cli.add_command(deleteguestcollection)
    cli.add_command(updateguestcollection)
    cli.add_command(getguestcollection)
    cli.add_command(guestcollectionlist)
    # Role commands
    cli.add_command(createrole)
    cli.add_command(deleterole)
    cli.add_command(getrole)
    cli.add_command(rolelist)

    # Timer commands
    cli.add_command(listtimers)
    cli.add_command(gettimer)
    cli.add_command(createtimer)
    cli.add_command(deletetimer)
    cli.add_command(pausetimer)
    cli.add_command(resumetimer)
    try:
        cli(auto_envvar_prefix="GLOBUSAPI")
    except Exception as ex:
        logger.exception("Halting...", exc_info=ex)
        raise ex
