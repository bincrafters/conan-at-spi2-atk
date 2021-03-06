from conans import ConanFile, Meson, tools
from conans.errors import ConanInvalidConfiguration
import os
import shutil


class AtSPI2AtkConan(ConanFile):
    name = "at-spi2-atk"
    description = "library that bridges ATK to At-Spi2 D-Bus service."
    topics = ("conan", "atk", "accessibility")
    url = "https://github.com/bincrafters/conan-at-spi2-atk"
    homepage = "https://gitlab.gnome.org/GNOME/at-spi2-atk"
    license = "LGPL-2.1-or-later"
    generators = "pkg_config"
    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        }
    default_options = {
        "shared": False,
        "fPIC": True,
        }

    _source_subfolder = "source_subfolder"
    _build_subfolder = "build_subfolder"

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if not tools.which('meson'):
            self.build_requires('meson/0.54.2')
        if not tools.which('pkg-config'):
            self.build_requires('pkgconf/1.7.3')

    def requirements(self):
        self.requires('at-spi2-core/2.38.0@bincrafters/stable')
        self.requires('atk/2.36.0')
        self.requires('libxml2/2.9.10')
        self.requires('glib/2.67.0', override=True)

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def _configure_meson(self):
        meson = Meson(self)
        args=[]
        args.append('--wrap-mode=nofallback')
        meson.configure(build_folder=self._build_subfolder, source_folder=self._source_subfolder, pkg_config_paths='.', args=args)
        return meson

    def build(self):
        for package in self.deps_cpp_info.deps:
            lib_path = self.deps_cpp_info[package].rootpath
            for dirpath, _, filenames in os.walk(lib_path):
                for filename in filenames:
                    if filename.endswith('.pc'):
                        shutil.copyfile(os.path.join(dirpath, filename), filename)
                        tools.replace_prefix_in_pc_file(filename, lib_path)
        meson = self._configure_meson()
        meson.build()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        meson = self._configure_meson()
        meson.install()
        tools.rmdir(os.path.join(self.package_folder, 'lib', 'pkgconfig'))

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
        self.cpp_info.includedirs = [os.path.join('include', 'at-spi2-atk', '2.0')]
        self.cpp_info.names['pkg_config'] = 'atk-bridge-2.0'
