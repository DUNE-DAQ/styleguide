#!/bin/bash

if [[ "$#" != "1" ]]; then
    echo "Usage: "$(basename $0)" <file or directory to examine>" >&2
    echo
    cat <<EOF >&2

The DUNE C++ style guide this script tries to look for violations of can be found in 
https://github.com/DUNE-DAQ/styleguide/blob/dune-daq-cppguide/dune-daq-cppguide.md

Given a file, it will apply a linter (dunecpplint.py) to that file

Given a directory, it will apply dunecpplint.py to all the source
(*.cxx, *.cpp) and header (*.hpp) files in that directory as well as all of its
subdirectories.

EOF
    
    exit 1
fi

filename=$1

# -build/c++11/14 : No headers are explicitly disallowed

# -build/explicit_make_pair : related to a bug in g++ 4.6 where it couldn't handle explicit template arguments in make pair; no longer relevant

# -build/namespaces: for source (not header) files, allow using-directives

# -runtime/indentation_namespace: worry about whitespace with our formatting tools

# -readability/check: described in cpplint.py as "Checks the use of
# -CHECK and EXPECT macros" - i.e., DUNE doesn't need it as we don't
# -use those

# -readability/constructors: refers to unused Google macros

# -runtime/references: DUNE doesn't require that function arguments
#  which can be altered need to be pointers

# -runtime/string: DUNE doesn't require that static/global variables
#  be trivially destructible

# -runtime/vlog: refers to Google-specific VLOG function

# -whitespace: worry about this with our formatting tools


header_filters="-build/c++11,-build/c++14,-readability/check,-readability/constructors,-runtime/indentation_namespace,-runtime/references,-runtime/string,-runtime/vlog,-whitespace,-build/explicit_make_pair"
source_filters="-build/c++11,-build/c++14,-build/namespaces,-readability/check,-readability/constructors,-runtime/indentation_namespace,-runtime/references,-runtime/string,-runtime/vlog,-whitespace,-build/explicit_make_pair"
hxx_filters=${source_filters}",-build/include_what_you_use,-legal/copyright"

dev_filters=""
#dev_filters=",-build/include_order,-build/include_what_you_use,-legal/copyright,-build/header_guard,-build/define_used,-readability/namespace,-runtime/output_format"

header_files=""
source_files=""
hxx_files=""

if [[ -d $filename ]]; then
    header_files=$( find $filename -name "*.hpp" )
    source_files=$( find $filename -name "*.cxx" )" "$( find $filename -name "*.cpp" )
    hxx_files=$( find $filename -name "*.hxx" )
elif [[ -f $filename ]]; then

    if [[ "$filename" =~ ^.*cxx$ || "$filename" =~ ^.*cpp$ ]]; then
	source_files=$filename
    elif [[ "$filename" =~ ^.*hpp$ ]]; then
	header_files=$filename
    elif [[ "$filename" =~ ^.*hxx$ ]]; then
	hxx_files=$filename
    else
	echo "Filename provided has unknown extension; exiting..." >&2
	exit 1
    fi

else
    echo "Unable to find $filename; exiting..." >&2
    exit 2
fi

for header_file in $header_files; do

    # Run lint and capture output
    lint_output=$($( dirname $0 )/dunecpplint.py --quiet --extensions=hpp,cxx,cpp,hxx --headers=hpp --filter=${header_filters}${dev_filters} $header_file 2>&1)

    # Only print if there were violations
    if echo "$lint_output" | grep -q "Total errors found:"; then
        echo "$lint_output"
    fi

done

for source_file in $source_files; do

    # Run lint and capture output
    lint_output=$($( dirname $0 )/dunecpplint.py --quiet --extensions=hpp,cxx,cpp,hxx --headers=hpp --filter=${source_filters}${dev_filters} $source_file 2>&1)

    # Only print if there were violations
    if echo "$lint_output" | grep -q "Total errors found:"; then
        echo "$lint_output"
    fi

done

for hxx_file in $hxx_files; do

    # Run lint and capture output
    lint_output=$($( dirname $0 )/dunecpplint.py --quiet --extensions=hpp,cxx,cpp,hxx --headers=hpp --filter=${hxx_filters}${dev_filters} $hxx_file 2>&1)

    # Only print if there were violations
    if echo "$lint_output" | grep -q "Total errors found:"; then
        echo "$lint_output"
    fi

done


