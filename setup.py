import os
import subprocess
import sys
from distutils.spawn import find_executable

from setuptools import Extension, setup
from setuptools.command.build_ext import build_ext


class CMakeBuild(build_ext):
    def run(self):
        if sys.platform == "win32":
            generator = "MinGW Makefiles"
            make = find_executable("mingw32-make")
        else:
            generator = "Unix Makefiles"
            make = find_executable("make")
        if not make:
            raise RuntimeError("Cannot find make executable")
        cmake = find_executable("cmake")
        if not cmake:
            raise RuntimeError("Cannot find cmake executable")
        subprocess.check_call(
            [
                cmake,
                ".",
                "-G",
                generator,
                "-DCMAKE_BUILD_TYPE=Debug" if self.debug else "",
                "-DPYEXT_SUFFIX=%s" % self.get_ext_filename(""),
                "-DPYLIB_DIRECTORY=%s" % self.build_lib if not self.inplace else "",
                "-DPYTHON_EXECUTABLE=%s" % sys.executable,
            ],
        )
        subprocess.check_call(
            [make, "-j%d" % (self.parallel or os.cpu_count()), "retro"],
        )


platform_globs = [
    "*-%s/*" % plat
    for plat in [
        "Nes",
        "Snes",
        "Genesis",
        "Atari2600",
        "GameBoy",
        "Sms",
        "GameGear",
        "PCEngine",
        "GbColor",
        "GbAdvance",
        "32x",
        "Saturn",
    ]
]

setup(
    ext_modules=[Extension("retro._retro", ["CMakeLists.txt", "src/*.cpp"])],
    cmdclass={"build_ext": CMakeBuild},
    package_data={
        "retro.data.stable": platform_globs,
        "retro.data.experimental": platform_globs,
        "retro.data.contrib": platform_globs,
    },
)
