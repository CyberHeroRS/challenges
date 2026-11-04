project('modern', 'cpp',
  version : '0.1',
  default_options : [
    'cpp_std=c++26',  # Mmmm myes
    'warning_level=3',
    'buildtype=debugoptimized',
    'strip=false',
    'cpp_args=-march=native'
  ]
)

py = import('python').find_installation('python3', required: true)
cpp = meson.get_compiler('cpp')
stdcxxexp = cpp.find_library('stdc++exp', required : true)
libmd = cpp.find_library('md', required : true)
tss2_esys = dependency('tss2-esys', required : true)
tss2_tctildr = dependency('tss2-tctildr', required : true)

# Check for C++26 debugging support
if not cpp.has_header('debugging')
  error('Compiler does not support C++26 <debugging> header yet.')
endif

# Check for SIMD support
has_simd = cpp.has_header('simd')
has_experimental_simd = cpp.has_header('experimental/simd')

if not has_simd and not has_experimental_simd
  error('Compiler does not support std::simd.')
endif


prebuild_gen = custom_target(
  'prebuild-gen',
  input: files('routing.py', 'src/generated_perm.template.cpp'),
  output: 'generated_perm.inc',
  command: [py, '@INPUT@'],
  capture: true,
  build_by_default: true,
)

executable('chall',
  [
    'src/main.cpp',
    prebuild_gen,
  ],
  include_directories: ['src', '.'],
  dependencies: [stdcxxexp, libmd, tss2_esys, tss2_tctildr]
)
