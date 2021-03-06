from pathlib import PureWindowsPath, PurePosixPath
from buildbot.steps.source.git import Git
from buildbot.steps.shell import ShellCommand
from buildbot.steps.transfer import FileUpload, DirectoryUpload
from buildbot.steps.mswin import Robocopy
from buildbot.process.factory import BuildFactory
from buildbot.process.properties import Property, Interpolate, renderer
from buildbot.status.results import FAILURE, SUCCESS
from buildbot.steps.master import MasterShellCommand

# Constants

# Properties
python_exe_prop          = Property('python_exe', default='python')
dir_command_prop         = Property('dir_command')
run_cpp_builds_prop      = Property('run_cpp_builds')
run_release_builds_prop  = Property('run_release_builds')
hide_cpp_builds_prop     = Property('hide_cpp_builds')
hide_release_builds_prop = Property('hide_release_builds')

# Git Repositories
nim_git_url      = 'https://github.com/nim-lang/Nim'
csources_git_url = 'https://github.com/nimrod-code/csources'
scripts_git_url  = 'https://github.com/nimrod-code/nim-buildbot'

repositories = {
    nim_git_url      : 'nim',
    csources_git_url : 'csources',
    scripts_git_url  : 'scripts'
}

# Resource Directories
resource_dirs = {
    'current_dir'  : './',
    'nim_dir'      : 'build/',
    'csources_dir' : 'build/csources/',
    'scripts_dir'  : 'scripts/',
    'tester_dir'   : 'tests/testament/',
    'absolute_idir': '{workdir}'
}

# Common Build Step Parameters
common_git_parameters = {
    'haltOnFailure'    : True,
    'description'      : 'Updating',
    'descriptionDone'  : 'Updated',
    'mode'             : 'full',
    'method'           : 'clobber',
    'shallow'          : True,
    'retry'            : (10, 20),
    'progress'         : True,
    'clobberOnFailure' : True
}


# Utility Functions
def step_has_property(name, default=None, giveResults=False):
    def check_for_property(step):
        result = step.getProperty(name)
        if result is None:
            return default
        else:
            return result
    if giveResults:
        return lambda results, s: check_for_property(s)
    else:
        return check_for_property


def step_has_properties(names, default=None, giveResults=False, sentinal=None):
    def check_for_property(step):
        for name in names:
            result = step.getProperty(name)
            if result is not sentinal:
                return result
        return default
    if giveResults:
        return lambda results, s: check_for_property(s)
    else:
        return check_for_property


def gen_dest_filename(s):
    parts = s.rsplit('.', 1)
    result = '{1}-{0}'.format('{buildnumber[0]}', parts[0])
    if len(parts) > 1:
        result = result + '.' + parts[1]
    return result

def gen_description(present_tense, running_tense, done_tense, action, sep=' '):
    return dict(
        name=present_tense + sep + action,
        description=running_tense,
        descriptionDone=done_tense,
        descriptionSuffix=action
    )

def get_codebase(change_dict):
    return repositories[change_dict['repository']]


# Cross-Platform Environment Calculation
class PlatformPaths:
    pass
windows_directories = PlatformPaths()
posix_directories = PlatformPaths()
for key, value in resource_dirs.iteritems():
    setattr(windows_directories, key, PureWindowsPath(value))
    setattr(posix_directories, key, PurePosixPath(value))
for platform in [windows_directories, posix_directories]:
    platform.base_env = {
        'PATH': [
            str(platform.current_dir),
            str(platform.nim_dir / 'bin'),
            'bin',
            "${PATH}"
        ]
    }
windows_directories.nim_exe = "nim.exe"
posix_directories.nim_exe = "nim"


def inject_paths(func):
    def wrapper(platform, *args, **kwargs):
        platform_directories = posix_directories
        if platform == 'windows':
            platform_directories = windows_directories
        return func(platform_directories, *args, **kwargs)
    return wrapper


# Build Steps

@inject_paths
def update_utility_scripts(platform):
    """
    Updates the utility scripts used by other steps.
    """
    common_parameters = common_git_parameters.copy()
    common_parameters['haltOnFailure'] = False

    return [
        Git(
            name              = "Update Utility Scripts",
            descriptionSuffix = ' Utility Scripts',
            repourl           = scripts_git_url,
            codebase          = repositories[scripts_git_url],
            workdir           = str(platform.scripts_dir),
            alwaysUseLatest   = True,
            hideStepIf        = False,
            flunkOnWarnings   = False,
            flunkOnFailure    = False,
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
            name              = "Update Local Nim Repository",
            descriptionSuffix = ' Local Nim Repository',
            repourl           = nim_git_url,
            codebase          = repositories[nim_git_url],
            workdir           = str(platform.nim_dir),
            **common_git_parameters
        ),

        Git(
            name              = "Update Local CSources Repository",
            descriptionSuffix = ' Local CSources Repository',
            repourl           = csources_git_url,
            codebase          = repositories[csources_git_url],
            workdir           = str(platform.csources_dir),
            alwaysUseLatest   = True,
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
    csources_filter = str(platform.csources_dir / '*')
    nim_clean_cmd = ['git', 'clean', '-x', '-f', '-e', csources_filter, '-d']
    csources_clean_cmd = ['git', 'clean', '-x', '-f', '-d']

    return [
        ShellCommand(
            command           = nim_clean_cmd,
            workdir           = str(platform.nim_dir),
            haltOnFailure     = False,
            flunkOnFailure    = False,
            warnOnFailure     = True,
            flunkOnWarnings   = False,
            **gen_description(
                'Clean', 'Cleaning', 'Cleaned', 'Local Nim Repository'
            )
        ),

        ShellCommand(
            command           = csources_clean_cmd,
            workdir           = str(platform.nim_dir),
            haltOnFailure     = False,
            flunkOnFailure    = False,
            warnOnFailure     = True,
            flunkOnWarnings   = False,
            **gen_description(
                'Clean', 'Cleaning', 'Cleaned', 'Local CSources Repository',
            )
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
            command           = csources_script_cmd,
            workdir           = str(platform.csources_dir),
            haltOnFailure     = True,
            **gen_description(
                'Build', 'Building', 'Built', 'Basic CSources Binary'
            )
        )
    ]


@inject_paths
def normalize_nim_names(platform):
    """
    Makes sure that both a 'nim' and 'nimrod' binary are present.
    """
    bin_dir = str(platform.nim_dir / 'bin')
    script_path = str(platform.scripts_dir / 'normalize_nim.py')

    return [
        ShellCommand(
            command           = [python_exe_prop, script_path, bin_dir],
            workdir           = str(platform.current_dir),
            hideStepIf        = False,
            **gen_description(
                'Normalize', 'Normalizing', 'Normalized', 'Binary Names'
            )
        )
    ]


@inject_paths
def compile_koch(platform):
    """
    Compiles the koch utility.
    """
    return [
        ShellCommand(
            command           = ['nim', 'c', 'koch.nim'],
            workdir           = str(platform.nim_dir),
            env               = platform.base_env,
            haltOnFailure     = True,
            **gen_description(
                'Compile', 'Compiling', 'Compiled', 'Koch Binary'
            )
        )
    ]


@inject_paths
def boot_nimrod_debug(platform):
    nimfile_dir = str(platform.current_dir / "compiler" / 'nim.nim')

    return [
        ShellCommand(
            command           = ['koch', 'boot'],
            workdir           = str(platform.nim_dir),
            env               = platform.base_env,
            haltOnFailure     = True,
            **gen_description(
                'Bootstrap', 'Booting', 'Booted', 
                'Debug Version of Nim Compiler (With C Backend)',
            )
        ),

        ShellCommand(
            command           = ['nim', 'c', '-d:release', nimfile_dir],
            workdir           = str(platform.nim_dir),
            env               = platform.base_env,
            haltOnFailure     = False,

            doStepIf=step_has_property(
                name    = run_release_builds_prop.key,
                default = True
            ),
            hideStepIf=step_has_property(
                name        = hide_release_builds_prop.key,
                default     = False,
                giveResults = True
            ),

            **gen_description(
                'Bootstrap', 'Booting', 'Booted', 
                'Release Version of Nim Compiler (With C Backend)',
            )
        ),

        ShellCommand(
            command           = ['nim', 'cpp', nimfile_dir],
            workdir           = str(platform.nim_dir),
            env               = platform.base_env,

            haltOnFailure     = False,
            warnOnFailure     = False,
            flunkOnFailure    = False,
            flunkOnWarnings   = False,

            doStepIf=step_has_property(
               name = run_cpp_builds_prop.key,
               default       = True
            ),
            hideStepIf=step_has_property(
               name = hide_cpp_builds_prop.key,
               default       = False,
               giveResults  = True
            ),

            **gen_description(
                'Bootstrap', 'Booting', 'Booted', 
                'Debug Version of Nim Compiler (With C++ Backend)',
            )
        ),
    ]


@inject_paths
def boot_nimrod_release(platform):

    return [
        ShellCommand(
            command           = ['koch', 'boot', '-d:release'],
            workdir           = str(platform.nim_dir),
            env               = platform.base_env,
            haltOnFailure     = True,
            **gen_description(
                'Bootstrap', 'Booting', 'Booted', 
                'Release Version of Nim Compiler (With C Backend)',
            )
        ),

        ShellCommand(
            command           = ['koch', 'csources', '-d:release'],
            workdir           = str(platform.nim_dir),
            env               = platform.base_env,
            haltOnFailure     = True,
            **gen_description(
                'Generate', 'Generating', 'Generated', 'C Sources'
            )
        ),
    ]



def FormatInterpolate(format_string):
    @renderer
    def render_revision(props):
        return format_string.format(**props.properties)
    return render_revision

@inject_paths
def run_testament(platform):
    test_url = "test-data/{buildername[0]}/{got_revision[0][nim]}/"
    test_directory = 'public_html/' + test_url

    html_test_results = 'testresults.html'
    html_test_results_dest = gen_dest_filename(html_test_results)
    db_test_results = 'testament.db'
    db_test_results_dest = gen_dest_filename(db_test_results)

    return [
        ShellCommand(
            command           = ['koch', 'test'],
            workdir           = str(platform.nim_dir),
            env               = platform.base_env,
            haltOnFailure     = True,
            timeout           = None,
            **gen_description(
                'Run', 'Running', 'Run', 'Testament'
            )
        ),

        MasterShellCommand(
            command    = ['mkdir', '-p', FormatInterpolate(test_directory)],
            path       = "public_html",
            hideStepIf = True
        ),

        FileUpload(
            slavesrc   = html_test_results,
            workdir    = str(platform.nim_dir),
            url        = FormatInterpolate(test_url + html_test_results_dest),
            masterdest = FormatInterpolate(
                test_directory + html_test_results_dest
            ),
        ),

        FileUpload(
            slavesrc   = db_test_results,
            workdir    = str(platform.nim_dir),
            url        = FormatInterpolate(test_url + db_test_results_dest),
            masterdest = FormatInterpolate(
                test_directory + db_test_results_dest
            ),
        )
    ]

@inject_paths
def upload_release(platform):
    upload_url = "test-data/{buildername[0]}/{got_revision[0][nim]}/"
    test_directory = 'public_html/' + upload_url

    nim_exe_source = str(platform.nim_dir / "bin" / platform.nim_exe)
    nim_exe_dest = gen_dest_filename(platform.nim_exe)

    return [
        MasterShellCommand(
            command    = ['mkdir', '-p', FormatInterpolate(test_directory)],
            path       = "public_html",
            hideStepIf = True
        ),

        FileUpload(
            slavesrc   = nim_exe_source,
            workdir    = str(platform.nim_dir),
            url        = FormatInterpolate(upload_url + nim_exe_dest),
            masterdest = FormatInterpolate(
                test_directory + nim_exe_dest
            ),
        ),

    ]


@inject_paths
def generate_installer(platform):
    script_src = str(platform.current_dir / 'build' / "tools" / "niminst" / 'EnvVarUpdate.nsh')
    script_dst = str(platform.current_dir / 'build' / "build")

    dlls_src = str(platform.current_dir / ".." / "dlls")
    dlls_dst = str(platform.current_dir / "build" / "bin")

    upload_src = str(platform.current_dir / 'build' / 'build')
    upload_dst = "installer-data/{buildername[0]}/{got_revision[0][nim]}/"
    upload_url = 'public_html/' + upload_dst

    return [
        ShellCommand(
            command           = ['copy', '/Y', script_src, script_dst],
            env               = platform.base_env,
            workdir           = str(platform.current_dir),
            haltOnFailure     = True,
            **gen_description(
                'Copy', 'Copying', 'Copied', 'NSIS Installer Script'
            )
        ),

        Robocopy(
            source            = dlls_src,
            destination       = dlls_dst,
            env               = platform.base_env,
            workdir           = str(platform.current_dir),
            haltOnFailure     = True,
            decodeRC          = {i: SUCCESS for i in range(0,8)},
            **gen_description(
                'Copy', 'Copying', 'Copied', 'Installer DLL\'s'
            )
        ),

        ShellCommand(
            command           = ['koch', 'nsis', '-d:release'],
            workdir           = str(platform.nim_dir),
            env               = platform.base_env,
            haltOnFailure     = True,
            **gen_description(
                'Generate', 'Generating', 'Generated', 'NSIS Installer'
            )
        ),

        DirectoryUpload(
            slavesrc   = upload_src,
            masterdest = upload_dst,
            workdir    = str(platform.current_dir),
            url        = FormatInterpolate(upload_url),
            compress   = 'bz2'
        )
    ]

# Build Configurations
def construct_nim_build(platform, csources_script_cmd, f=None):
    if f is None:
        f = BuildFactory()

    steps = []
    steps.extend(update_utility_scripts(platform))
    steps.extend(update_repositories(platform))
    steps.extend(clean_repositories(platform))
    steps.extend(build_csources(platform, csources_script_cmd))
    steps.extend(normalize_nim_names(platform))
    steps.extend(compile_koch(platform))
    steps.extend(boot_nimrod_debug(platform))
    steps.extend(run_testament(platform))
    #steps.extend(upload_release(platform))
    for step in steps:
        f.addStep(step)

    return f

def construct_nim_release(platform, csources_script_cmd, f=None):
    if f is None:
        f = BuildFactory()

    steps = []
    steps.extend(update_utility_scripts(platform))
    steps.extend(update_repositories(platform))
    steps.extend(clean_repositories(platform))
    steps.extend(build_csources(platform, csources_script_cmd))
    steps.extend(normalize_nim_names(platform))
    steps.extend(compile_koch(platform))
    steps.extend(boot_nimrod_release(platform))
    steps.extend(generate_installer(platform))
    for step in steps:
        f.addStep(step)

    return f
