# -*- python -*-
# ex: set syntax=python:

# This is the buildbot config file for downloading, booting, testing, and
# and packaging the Nim compiler.

# Global Configuration
# Main configuration dictionary.
c = BuildmasterConfig = {}

# BUILDSLAVES
from buildbot.buildslave import BuildSlave

# Build slaves controlled by the master server
# We use at least two slaves for each platform - a 32 bit slave, and a 64-bit
# slave

default_slave_params = {
}

c['slaves'] = [
    # Windows slaves
    BuildSlave(
        "windows-x64-slave-1", "pass",
        properties={},
        **default_slave_params
    ),

    BuildSlave(
        "windows-x32-slave-1", "pass",
        properties={},
        **default_slave_params
    ),


    # Linux slaves
    BuildSlave(
        "linux-x64-slave-1", "pass",
        properties={},
        **default_slave_params
    ),

    BuildSlave(
        "linux-x32-slave-1", "pass",
        properties={},
        **default_slave_params
    ),


    # Mac slaves
    BuildSlave(
        "mac-x64-slave-1", "pass",
        properties={},
        **default_slave_params
    ),

    BuildSlave(
        "mac-x32-slave-1", "pass",
        properties={},
        **default_slave_params
    ),
]

all_slave_names = [slave.name for slave in c['slaves']]

# 'protocols' contains information about protocols which master will use for
# communicating with slaves.
# You must define at least 'port' option that slaves could connect to your master
# with this protocol.
# 'port' must match the value configured into the buildslaves (with their
# --master option)
c['protocols'] = {'pb': {'port': 9989}}

# CHANGESOURCES
from buildbot.changes.pb import PBChangeSource

# List of sources to retrieve change notifications from.
# We get our sources from notifications sent by the github hook bot on a port.

c['change_source'] = [
    PBChangeSource(
        user='octobot',
        passwd='0ct0c@t'
    )
]

# SCHEDULERS
from buildbot.schedulers.basic import AnyBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler, AnyPropertyParameter

# Configure the Schedulers, which decide how to react to incoming changes.


force_build_properties = [
    AnyPropertyParameter("Branch Name"), AnyPropertyParameter("Solo Action")
]
all_builders = [
    "windows-x64-builder", "windows-x32-builder",
    "linux-x64-builder", "linux-x32-builder",
    "mac-x64-builder", "mac-x32-builder"
]

c['schedulers'] = [
    # Main scheduler, activated when a branch in the Nim repository is changed.
    AnyBranchScheduler(
        name="git-build-scheduler",
        treeStableTimer=None,
        builderNames=all_builders
    ),

    # These schedulers are activated when their buttons are clicked on the
    # build admins page.
    ForceScheduler(
        name="force-build-scheduler",
        builderNames=all_builders,
        buttonName="Force Compiler Build",
        properties=[]
    )
]

# BUILDERS
from build_steps import construct_nim_build

# List of builds and their build steps
# name=,
# haltOnFailure=,
# flunkOnWarnings=,
# flunkOnFailure=,
# warnOnWarnings=,
# warnOnFailure=,
# alwaysRun=,
# description=,
# descriptionDone=,
# descriptionSuffix=,
# doStepIf=,
# hideStepIf=


# Package Nimrod in Zip
# package_factory = BuildFactory()
# package_factory.addStep(
#     Thing(
#         name='Packaging Compiler'
#         haltOnFailure=True
#         description='Packaging'
#         descriptionDone='Packaged'
#     )
# )
# Add binary paths to environment
# Compile koch
# Bootstrap Nim using C backend in debug mode
# Bootstrap Nim using C backend in release mode
# Bootstrap Nim using C++ backend in debug mode
# Bootstrap Nim using C++ backend in release mode

from buildbot.config import BuilderConfig
all_slaves = [
    "windows-x64-slave-1", "windows-x32-slave-1",
    "linux-x64-slave-1", "linux-x32-slave-1",
    "mac-x64-slave-1", "mac-x32-slave-1"
]

c['builders'] = [
    BuilderConfig(
        name="windows-x64-builder",
        slavenames=["windows-x64-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='build64.bat',
            platform='windows'
        )
    ),
    BuilderConfig(
        name="windows-x32-builder",
        slavenames=["windows-x32-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='build.bat',
            platform='windows'
        )
    ),
    BuilderConfig(
        name="linux-x64-builder",
        slavenames=["linux-x64-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='./build.sh',
            platform='linux'
        )
    ),
    BuilderConfig(
        name="linux-x32-builder",
        slavenames=["linux-x32-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='./build.sh',
            platform='linux'
        )
    ),
    BuilderConfig(
        name="mac-x64-builder",
        slavenames=["mac-x64-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='./build.sh',
            platform='mac'
        )
    ),
    BuilderConfig(
        name="mac-x32-builder",
        slavenames=["mac-x32-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='./build.sh',
            platform='mac'
        )
    )
]

# STATUS TARGETS

# 'status' is a list of Status Targets. The results of each build will be
# pushed to these targets. buildbot/status/*.py has a variety to choose from,
# including web pages, email senders, and IRC bots.

c['status'] = []

from buildbot.status import html
from buildbot.status.web import authz, auth

authz_cfg = authz.Authz(
    # change any of these to True to enable; see the manual for more
    # options
    auth=auth.BasicAuth([("admin", "password")]),
    gracefulShutdown=False,
    forceBuild='auth',  # use this to test your slave once it is set up
    forceAllBuilds=True,
    pingBuilder=False,
    stopBuild=True,
    stopAllBuilds=True,
    cancelPendingBuild=True,
)
c['status'].append(html.WebStatus(http_port=8010, authz=authz_cfg))

# PROJECT IDENTITY

# the 'title' string will appear at the top of this buildbot
# installation's html.WebStatus home page (linked to the
# 'titleURL') and is embedded in the title of the waterfall HTML page.

c['title'] = "Nim Compiler"
c['titleURL'] = "http://nimrod-lang.org"

# the 'buildbotURL' string should point to the location where the buildbot's
# internal web server (usually the html.WebStatus page) is visible. This
# typically uses the port number set in the Waterfall 'status' entry, but
# with an externally-visible host name which the buildbot cannot figure out
# without some help.

c['buildbotURL'] = "http://localhost:8010/"

# DB URL

c['db'] = {
    # This specifies what database buildbot uses to store its state.  You can leave
    # this at its default for all but the largest installations.
    'db_url': "sqlite:///state.sqlite",
}
