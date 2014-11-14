# -*- python -*-
# ex: set syntax=python:

# This is the buildbot config file for downloading, booting, testing, and
# and packaging the Nim compiler.

# The following is a list of properties that can be used to influence the
# build processes. All these property names are assigned to variables of the
# same name with '_property_name':
#  - 'python_exe': Name of the python executable to call when using
#                  python scripts. Defaults to 'python'.
#
#  - 'run_cpp_builds': Whether to run builds which use the C++ compiler.
#                      Defaults to true.
#
#  - 'run_release_builds': Whether to run release builds. Defaults to true.
#
#  - 'hide_cpp_builds': Whether to show builds which use the C++ compiler.
#                       Defaults to false.
#
#  - 'hide_release_builds': Whether to show release builds. Defaults to false.

# Global Configuration
from build_steps import construct_nim_build, python_exe_property_name

# Main configuration dictionary.
c = BuildmasterConfig = {}


# Buildslave Configuration
from buildbot.buildslave import BuildSlave

# Build slaves controlled by the master server
# We use at least two slaves for each platform - a 32 bit slave, and a 64-bit
# slave.

default_slave_params = {
}

c['slaves'] = [
    # Windows slaves
    BuildSlave(
        "windows-x64-slave-1", "",
        properties={},
        **default_slave_params
    ),

    BuildSlave(
        "windows-x32-slave-1", "",
        properties={},
        **default_slave_params
    ),


    # Linux slaves
    BuildSlave(
        "linux-x64-slave-1", "",
        properties={},
        **default_slave_params
    ),

    BuildSlave(
        "linux-x32-slave-1", "",
        properties={},
        **default_slave_params
    ),


    # Mac slaves
    BuildSlave(
        "mac-x64-slave-1", "",
        properties={},
        **default_slave_params
    ),

    BuildSlave(
        "mac-x32-slave-1", "",
        properties={},
        **default_slave_params
    ),

    BuildSlave(
        "linux-arm5-slave-1", "",
        properties={
            python_exe_property_name: 'python27'
        },
        **default_slave_params
    )
]

all_slave_names = [slave.name for slave in c['slaves']]


# PROTOCOLS

# 'protocols' contains information about protocols which master will use for
# communicating with slaves.
# You must define at least 'port' option that slaves could connect to your
# master with this protocol.
# 'port' must match the value configured into the buildslaves (with their
# --master option)

c['protocols'] = {'pb': {'port': 9989}}


# CHANGESOURCES
from buildbot.changes.pb import PBChangeSource

# List of sources to retrieve change notifications from.
# We get our sources from notifications sent by the github hook bot on a port.

c['change_source'] = [
    PBChangeSource(
        user='',
        passwd=''
    )
]


# BUILDERS
from buildbot.config import BuilderConfig

# List of builds and their build steps

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
            csources_script_cmd='sh build.sh',
            platform='linux'
        )
    ),
    BuilderConfig(
        name="linux-x32-builder",
        slavenames=["linux-x32-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='sh build.sh',
            platform='linux'
        )
    ),
    BuilderConfig(
        name="mac-x64-builder",
        slavenames=["mac-x64-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='sh build.sh',
            platform='mac'
        )
    ),
    BuilderConfig(
        name="mac-x32-builder",
        slavenames=["mac-x32-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='sh build.sh',
            platform='mac'
        )
    ),
    BuilderConfig(
        name="linux-arm5-builder",
        slavenames=["linux-arm5-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='sh build.sh',
            platform='linux'
        )
    ),
]

all_builder_names = [builder.name for builder in c['builders']]


# SCHEDULERS
from buildbot.schedulers.basic import AnyBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler

# Configure the Schedulers, which decide how to react to incoming changes.

c['schedulers'] = [
    # Main scheduler, activated when a branch in the Nim repository is changed.
    AnyBranchScheduler(
        name="git-build-scheduler",
        treeStableTimer=None,
        builderNames=all_builder_names
    ),

    # Force-build scheduler, activated when its button is clicked on the
    # build admins page.
    ForceScheduler(
        name="force-build-scheduler",
        builderNames=all_builder_names,
        buttonName="Force Compiler Build",
        label='Manual Compiler Build'
        properties=[]
    )
]


# STATUS TARGETS
from buildbot.status import html
from buildbot.status.web import authz, auth

# 'status' is a list of Status Targets. The results of each build will be
# pushed to these targets. buildbot/status/*.py has a variety to choose from,
# including web pages, email senders, and IRC bots.

c['status'] = []

authz_cfg = authz.Authz(
    # change any of these to True to enable; see the manual for more
    # options
    auth=auth.BasicAuth([("", "")]),
    gracefulShutdown=False,
    forceBuild='auth',  # use this to test your slave once it is set up
    forceAllBuilds='auth',
    pingBuilder=False,
    stopBuild='auth',
    stopAllBuilds='auth',
    cancelPendingBuild='auth',
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

c['buildbotURL'] = "http://build.nim-lang.org:8010/"

# DB URL

c['db'] = {
    # This specifies what database buildbot uses to store its state.  You can
    # leave this at its default for all but the largest installations.
    'db_url': "sqlite:///state.sqlite",
}
