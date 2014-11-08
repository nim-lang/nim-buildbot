from functools import wraps
from pathlib import PureWindowsPath, PurePosixPath
from buildbot.status.results import SUCCESS
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.process.factory import BuildFactory

# Constants

# Git Urls
nim_git_url = 'git://github.com/Araq/Nimrod'
csources_git_url = 'git://github.com/nimrod-code/csources'
scripts_git_url = 'git://github.com/nimrod-code/nim-buildbot'


# Resource directories
resource_dirs = {
    'current_dir': './',
    'nim_dir': 'build/',
    'csources_dir': 'build/csources/',
    'scripts_dir': 'scripts/',
}


class PlatformPaths:
    pass
windows_directories = PlatformPaths()
posix_directories = PlatformPaths()
for key, value in resource_dirs.iteritems():
    setattr(windows_directories, key, PureWindowsPath(value))
    setattr(posix_directories, key, PurePosixPath(value))


# Utility Functions

def inject_paths(func):
    def wrapper(platform, *args, **kwargs):
        platform_directories = posix_directories
        if platform == 'windows':
            platform_directories = windows_directories
        return func(platform_directories, *args, **kwargs)
    return wrapper

has_passed = lambda results, step: results == SUCCESS

# Build Steps

# Common build step parameters
common_git_parameters = {
    'haltOnFailure': True,
    'description': 'Updating',
    'descriptionDone': 'Updated',

    'mode': 'incremental',
    'retry': (10, 20),

    'progress': True,
    'clobberOnFailure': True
}

# Steps


@inject_paths
def update_utility_scripts(platform):
    """
    Updates the utility scripts used by other steps.
    """
    common_parameters = common_git_parameters.copy()
    common_parameters['haltOnFailure'] = False

    return [
        Git(
            name="Update Utility Scripts",
            descriptionSuffix=' Utility Scripts',

            repourl=scripts_git_url,
            alwaysUseFull=True,

            workdir=str(platform.scripts_dir),
            hideStepIf=has_passed,
            **common_parameters
        )
    ]


@inject_paths
def update_repositories(platform):
    """
    Adds the steps needed to update the csources and Nimrod repositories.
    """
    return [
        Git(
            name="Update Local Nim Repository",
            descriptionSuffix=' Local Nim Repository',

            repourl=nim_git_url,

            workdir=str(platform.nim_dir),
            **common_git_parameters
        ),
        Git(
            name="Update Local CSources Repository",
            descriptionSuffix=' Local CSources Repository',

            repourl=csources_git_url,
            alwaysUseLatest=True,

            workdir=str(platform.csources_dir),
            **common_git_parameters
        )
    ]


@inject_paths
def clean_repositories(platform):
    """
    Adds the steps needed to clean the Nimrod and CSources repositories.
    Requires that the repositories already exist, in the layout done by
    update_repositories.
    """
    return [
        ShellCommand(
            name='Clean Local Nim Repository',
            description='Cleaning',
            descriptionDone='Cleaned',
            descriptionSuffix=' Local Nim Repository',

            command=[
                'git', 'clean', '-x', '-f', '-e', str(platform.csources_dir / '*'), '-d'],
            workdir=str(platform.nim_dir),
            haltOnFailure=True,
        ),

        ShellCommand(
            name='Clean Local CSources Repository',
            description='Cleaning',
            descriptionDone='Cleaned',
            descriptionSuffix=' Local CSources Repository',

            command=['git', 'clean', '-x', '-f', '-d'],
            workdir=str(platform.nim_dir),
            haltOnFailure=True,
        )
    ]


@inject_paths
def build_csources(platform, csources_script_cmd):
    """
    Builds the csources binary. Requires that the csources repository be
    present and that a suitable C compiler be present on the system path.
    """
    return [
        ShellCommand(
            name='Build Basic Nim Binary',
            description='Building',
            descriptionDone='Built',
            descriptionSuffix=' Basic CSources Binary',

            command=csources_script_cmd,
            workdir=str(platform.csources_dir),
            haltOnFailure=True,
        )
    ]


@inject_paths
def normalize_nim_names(platform):
    """
    Makes sure that both a 'nim' and 'nimrod' binary are present.
    """
    return [
        ShellCommand(
            name='Normalizing Binary Names',
            description='Normalizing',
            descriptionDone='Normalized',
            descriptionSuffix=' Binary Names',

            command=['python', str(platform.scripts_dir / 'normalize_nim.py')],
            workdir=str(platform.nim_dir / 'bin'),
            hideStepIf=has_passed
        )
    ]


@inject_paths
def compile_koch(platform):
    """
    Compiles the koch utility.
    """
    base_env = {
        'PATH': [
            str(platform.current_dir),
            str(platform.current_dir / 'bin'),
            "${PATH}"
        ]
    }

    return [
        ShellCommand(
            name='Compile Koch',
            description='Compiling',
            descriptionDone='Compiled',
            descriptionSuffix=' Koch Binary',

            command=['nimrod', 'c', 'koch.nim'],
            env=base_env,
            workdir=str(platform.nim_dir),
            haltOnFailure=True,
        )
    ]


@inject_paths
def boot_nimrod_with_c_backend(platform):
    base_env = {
        'PATH': [
            str(platform.current_dir),
            str(platform.current_dir / 'bin'),
            "${PATH}"
        ]
    }

    return [
        ShellCommand(
            name='Bootstrap Release Version of Nim Compiler (With C Backend)',
            description='Booting',
            descriptionDone='Booted',
            descriptionSuffix=' Release Nim Compiler (With C Backend)',

            command=['nimrod', 'c', str(platform.nim_dir / 'compiler' / 'nim.nim'), '-d:release'],
            workdir=str(platform.nim_dir),
            env=base_env,
            haltOnFailure=False,
        ),

        ShellCommand(
            name='Bootstrap Debug Version of Nim Compiler (With C Backend)',
            description='Booting',
            descriptionDone='Booted',
            descriptionSuffix=' Debug Nim Compiler (With C Backend)',

            command=['koch', 'boot'],
            workdir=str(platform.nim_dir),
            env=base_env,
            haltOnFailure=True,
        )
    ]


@inject_paths
def run_testament(platform):
    base_env = {
        'PATH': [
            str(platform.current_dir),
            str(platform.current_dir / 'bin'),
            "${PATH}"
        ]
    }

    return [
        ShellCommand(
            name='Run Testament',
            description='Running',
            descriptionDone='Run',
            descriptionSuffix=' Testament',

            command=['koch', 'test'],
            workdir=str(platform.nim_dir),
            env=base_env,
            haltOnFailure=True,
        )
    ]


@inject_paths
def generate_csources(platform):
    base_env = {
        'PATH': [
            str(platform.current_dir),
            str(platform.current_dir / 'bin'),
            "${PATH}"
        ]
    }

    return [
        ShellCommand(
            name='Generate CSources',
            description='Generating',
            descriptionDone='Generated',
            descriptionSuffix=' CSources',

            command=['koch', 'csources'],
            workdir=str(platform.nim_dir),
            env=base_env,
            haltOnFailure=True,
        )
    ]


@inject_paths
def generate_zip(platform):
    base_env = {
        'PATH': [
            str(platform.current_dir),
            str(platform.current_dir / 'bin'),
            "${PATH}"
        ]
    }

    return [
        ShellCommand(
            name='Generate CSources',
            description='Generating',
            descriptionDone='Generated',
            descriptionSuffix=' CSources',

            command=['koch', 'csources'],
            workdir=str(platform.nim_dir),
            env=base_env,
            haltOnFailure=True,
        )
    ]


@inject_paths
def generate_installer(platform):
    base_env = {
        'PATH': [
            str(platform.current_dir),
            str(platform.current_dir / 'bin'),
            "${PATH}"
        ]
    }

    return [
        ShellCommand(
            name='Generate CSources',
            description='Generating',
            descriptionDone='Generated',
            descriptionSuffix=' CSources',

            command=['koch', 'nsis'],
            workdir=str(platform.nim_dir),
            env=base_env,
            haltOnFailure=True,
        )
    ]


# Build Configurations
def construct_nim_build(platform, csources_script_cmd, f=None):
    if f is None:
        f = BuildFactory()

    steps = []
    steps.extend(update_repositories(platform))
    steps.extend(clean_repositories(platform))
    steps.extend(build_csources(platform, csources_script_cmd))
    steps.extend(normalize_nim_names(platform))
    steps.extend(compile_koch(platform))
    steps.extend(boot_nimrod_with_c_backend(platform))
    steps.extend(run_testament(platform))
    for step in steps:
        f.addStep(step)

    return f
