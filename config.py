# -*- python -*-
# ex: set syntax=python:

# This is the buildbot config file for downloading, booting, testing, and
# and packaging the Nim compiler.

# The following is a list of properties that can be used to influence the
# build processes.
#  - 'python_exe': Name of the python executable to call when using
#                  python scripts. Defaults to 'python'.
#
#  - 'run_cpp_builds': Whether to run builds which use the C++ compiler.
#                      Defaults to true.
#
#  - 'run_release_builds': Whether to run release builds. Defaults to true.
#
#  - 'hide_cpp_builds': Whether to hide builds which use the C++ compiler.
#                       Defaults to false.
#
#  - 'hide_release_builds': Whether to hide release builds. Defaults to false.


# Global Configuration
import os
from build_steps import construct_nim_build, python_exe_prop, get_codebase
from build_steps import construct_nim_release

# Main configuration dictionary.
c = BuildmasterConfig = {}


# Codebase configuration
c['codebaseGenerator'] = get_codebase


# Buildslave Configuration
# Build slaves are remote servers used by the build master to perform remote
# actions, such as running a build.
# All build slaves *must* have a name of the format:
#    "{operating system}-{architecture}-slave-{slave number}"
#
# This allows for automatic categorization into various variables.

from buildbot.buildslave import BuildSlave
from infostore import slave_passwords, buildbot_admin_emails

default_slave_params = {
    'notify_on_missing': buildbot_admin_emails
}

c['slaves'] = [
    # Windows slaves
    BuildSlave(
        "windows-x64-slave-1", slave_passwords[0],
        properties={},
        **default_slave_params
    ),

    BuildSlave(
        "windows-x32-slave-1", slave_passwords[1],
        properties={},
        **default_slave_params
    ),


    # Linux slaves
    BuildSlave(
        "linux-x64-slave-1", slave_passwords[2],
        properties={},
        **default_slave_params
    ),

    BuildSlave(
        "linux-x32-slave-1", slave_passwords[3],
        properties={},
        **default_slave_params
    ),

    BuildSlave(
        "linux-arm5-slave-1", slave_passwords[6],
        properties={
            python_exe_prop.key: 'python2',
            'run_release_builds': False
        },
        **default_slave_params
    ),

    BuildSlave(
        "linux-arm6-slave-1", slave_passwords[7],
        properties={
            python_exe_prop.key: 'python2',
            'run_release_builds': False
        },
        **default_slave_params
    ),

    BuildSlave(
        "linux-arm7-slave-1", slave_passwords[8],
        properties={
            python_exe_prop.key: 'python2',
            'run_release_builds': False
        },
        **default_slave_params
    ),

    # FreeBSD
    BuildSlave(
        "freebsd-x64-slave-1", slave_passwords[9],
        properties={
            python_exe_prop.key: 'python2'
        },
        **default_slave_params
    ),

    # Mac slaves
    BuildSlave(
        "mac-x64-slave-1", slave_passwords[10],
        properties={
            python_exe_prop.key: 'python'
        },
        **default_slave_params
    ),

    # BuildSlave(
    #     "mac-x32-slave-1", '',
    #     properties={},
    #     **default_slave_params
    # ),
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
# List of sources to retrieve change notifications from.
# We get our sources from notifications sent by the github hook bot on a port.

from buildbot.changes.pb import PBChangeSource
from infostore import change_source_credentials

c['change_source'] = [
    PBChangeSource(
        user=change_source_credentials[0][0],
        passwd=change_source_credentials[0][1],
    )
]


# BUILDERS
# List of builds and their build steps

from buildbot.config import BuilderConfig

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
    # BuilderConfig(
    #     name="mac-x32-builder",
    #     slavenames=["mac-x32-slave-1"],
    #     factory=construct_nim_build(
    #         csources_script_cmd='sh build.sh',
    #         platform='mac'
    #     )
    # ),
    BuilderConfig(
        name="linux-arm5-builder",
        slavenames=["linux-arm5-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='sh build.sh',
            platform='linux'
        )
    ),

    BuilderConfig(
        name="linux-arm6-builder",
        slavenames=["linux-arm6-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='sh build.sh',
            platform='linux'
        )
    ),

    BuilderConfig(
        name="linux-arm7-builder",
        slavenames=["linux-arm7-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='sh build.sh',
            platform='linux'
        )
    ),

    BuilderConfig(
        name="freebsd-x64-builder",
        slavenames=["freebsd-x64-slave-1"],
        factory=construct_nim_build(
            csources_script_cmd='sh build.sh',
            platform='freebsd'
        )
    ),

    BuilderConfig(
        name="windows-x64-installer",
        slavenames=["windows-x64-slave-1"],
        factory=construct_nim_release(
            csources_script_cmd='build64.bat',
            platform='windows'
        )
    ),
    BuilderConfig(
        name="windows-x32-installer",
        slavenames=["windows-x32-slave-1"],
        factory=construct_nim_release(
            csources_script_cmd='build.bat',
            platform='windows'
        )
    ),
]

all_builder_names = []
all_installer_names = []
for builder in c['builders']:
    if 'builder' in builder.name:
        all_builder_names.append(builder.name)
    elif 'installer' in builder.name:
        all_installer_names.append(builder.name)
    else:
        raise Exception("Bad builder config name '{0}'".format(builder.name))

# SCHEDULERS
# Configure the Schedulers, which decide how to react to incoming changes.

from buildbot.schedulers.basic import AnyBranchScheduler
from buildbot.schedulers.forcesched import ForceScheduler

c['schedulers'] = [
    # Main scheduler, activated when a branch in the Nim repository is changed.
    AnyBranchScheduler(
        name="git-build-scheduler",
        treeStableTimer=None,
        builderNames=all_builder_names,
        codebases={
            'nim': {'repository': ''},
            'csources': {'repository': ''},
            'scripts': {'repository': ''},
        }
    ),

    # Force-build scheduler, activated when its button is clicked on the
    # build admins page.
    ForceScheduler(
        name="force-build-scheduler",
        builderNames=all_builder_names,
        buttonName="Force Compiler Build",
        properties=[],
        codebases={
            'nim': {'repository': ''},
            'csources': {'repository': ''},
            'scripts': {'repository': ''},
        }
    ),

    ForceScheduler(
        name="force-installer-scheduler",
        builderNames=all_installer_names,
        buttonName="Force Installer Build",
        properties=[],
        codebases={
            'nim': {'repository': ''},
            'csources': {'repository': ''},
            'scripts': {'repository': ''},
        }
    )
]


# STATUS TARGETS
# Set up the various target for build status.
# In particular, we set up a page to handle requests for individual test
# results, as well as a page to handle retrieving build status badges

from buildbot.status import html
from buildbot.status.web import authz, auth
from buildbot.status.builder import Results
from buildbot.status.web.base import HtmlResource
from buildbot.status.mail import MailNotifier
from buildbot.status import words
from buildbot.status.github import GitHubStatus

from twisted.web.static import File

from infostore import user_credentials, irc_credentials
from infostore import buildbot_admin_emails, github_token

# Set up the custom build status

# Email notifier
mn = MailNotifier(
    fromaddr="buildbot@nim-lang.org",
    subject="Nim-Buildbot: %(builder)s requires attention.",
    mode=['change', 'problem', 'warnings', 'exception'],
    builders=None,
    sendToInterestedUsers=False,
    extraRecipients=buildbot_admin_emails
)

# IRC bot
irc = words.IRC(
    host="irc.freenode.net",
    channels=[{"channel": "#nimbuild"}],
    nick=irc_credentials['username'],
    password=irc_credentials['password'],
    useColors=False,
    notify_events={
        'finished': 1,
        'failure': 1,
        'exception': 1,
    }
)

# Github Status
gs = GitHubStatus(
    token=github_token,
    repoOwner="nim-lang",
    repoName="Nim",
    startDescription='Build started.',
    endDescription='Build done.'
)

c['status'] = [irc, gs]

class BuilderResource(HtmlResource):

    """
    Helper class for per-builder resources
    """

    def content(self, request, ctx):
        """Display a build status image like Travis does."""
        status = self.getStatus(request)

        # Get the parameters.
        name = request.args.get('builder', (None,))[0]
        number = request.args.get('number', (None,))[0]
        if name is None:
            return 'builder parameter missing'

        # Check if the builder in parameter exists.
        try:
            builder = status.getBuilder(name)
        except NameError:
            return "invalid builder '%s'" % builder

        # Check if the given build is valid
        if number is not None:
            try:
                number = int(number)
            except ValueError:
                return "invalid build number '%s'" % number

        # Check if the given build exists.
        if number == -1 or number is None:
            build = builder.getLastFinishedBuild()
        else:
            build = builder.getBuild(int(number))
        if not build:
            return "unknown build number '%s'" % number

        return self.content_hook(request, ctx, builder, build, number)

from datetime import datetime
from buildbot.util import UTC

class StatusImageResource(BuilderResource):
    contentType = 'image/svg+xml'

    def content_hook(self, request, ctx, builder, build, number):
        """Display a build status image like Travis does."""
        start_time, end_time = build.getTimes()
        target_time = end_time or start_time or datetime.utcnow()
        if isinstance(target_time, float):
            target_time = datetime.fromtimestamp(target_time, UTC)
        
        request.setHeader('Cache-Control', 'no-cache')
        request.setHeader('Last-Modified', target_time.strftime('%a, %d %b %Y %H:%M:%S GMT'))

        # SUCCESS, WARNINGS, FAILURE, SKIPPED or EXCEPTION
        res = build.getResults()
        resname = Results[res]

        img = 'public_html/status-img/status_image_%s.svg' % resname
        here = os.path.dirname(__file__)
        imgfile = os.path.join(here, img)

        imgcontent = open(imgfile, 'rb').read()

        return imgcontent


class NimBuildStatus(html.WebStatus):

    def setupUsualPages(self, numbuilds, num_events, num_events_max):
        File.contentTypes[".db"] = "application/x-sqlite3"

        html.WebStatus.setupUsualPages(
            self, numbuilds, num_events, num_events_max)
        self.putChild("buildstatusimage", StatusImageResource())



authz_cfg = authz.Authz(
    # change any of these to True to enable; see the manual for more
    # options
    auth=auth.BasicAuth(user_credentials),
    gracefulShutdown=False,
    forceBuild='auth',
    forceAllBuilds='auth',
    pingBuilder=False,
    stopBuild='auth',
    stopAllBuilds='auth',
    cancelPendingBuild='auth',
)
c['status'].append(NimBuildStatus(http_port=8010, authz=authz_cfg))


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

c['buildbotURL'] = "http://buildbot.nim-lang.org/"

# DB URL

c['db'] = {
    # This specifies what database buildbot uses to store its state.  You can
    # leave this at its default for all but the largest installations.
    'db_url': "sqlite:///state.sqlite",
}
