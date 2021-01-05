pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'worldpossible_scriptlauncher')
gnome = import('gnome')

gnome.compile_resources('worldpossible-scriptlauncher',
  'worldpossible_scriptlauncher.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'worldpossible-scriptlauncher.in',
  output: 'worldpossible-scriptlauncher',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

worldpossible_scriptlauncher_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'scriptlauncherlogger.py',
]

install_data(worldpossible_scriptlauncher_sources, install_dir: moduledir)
