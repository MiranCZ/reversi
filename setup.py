from setuptools import setup, Extension
from setuptools.command.build_ext import build_ext
from Cython.Build import cythonize
import os
import shutil


class CustomBuildExt(build_ext):
    def finalize_options(self):
        build_ext.finalize_options(self)
        self.inplace = True

    def run(self):
        try:
            super().run()
        except Exception:
            print("WARNING: Failed to build Cython extensions. Installation will continue without them.")
            self.extensions = []

    def build_extension(self, ext):
        try:
            super().build_extension(ext)
        except Exception as e:
            print(f"WARNING: Failed to build extension {ext.name}. Skipping it. Error: {e}")


# removes temp build directories and files
def clean_build_artifacts():
    if os.path.exists("build"):
        shutil.rmtree("build")
    egg_info = [d for d in os.listdir() if d.endswith(".egg-info")]
    for e in egg_info:
        shutil.rmtree(e)

    # clear unneeded .c files, they are compiled anyway and therefore no longer needed
    collected_modules = [(m.sources[0].removesuffix("pyx") + "c") for m in extensions]
    for module in collected_modules:
        if os.path.exists(module):
            os.remove(module)


extensions = [
    Extension("reversi.bot.optimized.montecarlo", ["reversi/bot/optimized/montecarlo.pyx"])
]

setup(
    # ext_modules=[cythonize(name) for name in cython_modules],
    ext_modules=cythonize(extensions),
    language='c++',
    cmdclass={"build_ext": CustomBuildExt},
    zip_safe=False
)

clean_build_artifacts()
