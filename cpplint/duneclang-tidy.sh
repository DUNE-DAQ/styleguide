#!/bin/env bash

if [[ "$#" != "2" ]]; then

cat<<EOF >&2

    Usage: $(basename $0) <full pathname of compile_commands.json for your build> <file or directory to examine> 

Given a file, it will apply a linter (clang-tidy) to that file

Given a directory, it will apply clang-tidy to all the
source (*.cc) and header (*.hh) files in that directory as well as all
of its subdirectories.


compile_commands.json is a file which this script needs to forward to
clang-tidy. It can be automatically produced in a cmake build; to get
cmake to do this, add the following line to your CMakeLists.txt file:

set(CMAKE_EXPORT_COMPILE_COMMANDS ON CACHE BOOL "Set to ON to produce a compile_commands.json file which clang-tidy can use" FORCE)

More detail can be found in
https://cmake.org/cmake/help/v3.5/variable/CMAKE_EXPORT_COMPILE_COMMANDS.html

EOF

    exit 1
fi

compile_commands=$1

# May also want to add logic making sure this file is up-to-date
if [[ ! -f $compile_commands ]]; then
    echo "CMake-produced compile commands file $compile_commands not found; exiting..." >&2
    exit 3
fi


filename=$2

source_files=""

if [[ -d $filename ]]; then
    source_files=$( find $filename -name "*.cc" ) 
elif [[ -f $filename ]]; then

    if [[ "$filename" =~ ^.*cc$ ]]; then
	source_files=$filename
    elif [[ "$filename" =~ ^.*hh$ ]]; then
	echo $(basename $0)" can only accept source files, not header files; exiting..." >&2
	exit 1
    else
	echo "Filename provided has unknown extension; exiting..." >&2
	exit 1
    fi

else
    echo "Unable to find $filename; exiting..." >&2
    exit 2
fi


clang_products_dir=/cvmfs/fermilab.opensciencegrid.org/products/larsoft
. $clang_products_dir/setup
retval="$?"

if [[ "$retval" == 0 ]]; then
    echo "Set up the products directory $clang_products_dir"
else
    cat<<EOF >&2

There was a problem setting up the products directory 
$clang_products_dir ;
exiting...

EOF

    exit 1
fi

clang_version=$( ups list -aK+ clang | sort -n | tail -1 | sed -r 's/^\s*\S+\s+"([^"]+)".*/\1/' )

if [[ -n $clang_version ]]; then

    setup clang $clang_version
    retval="$?"

    if [[ "$retval" == "0" ]]; then
	echo "Set up clang $clang_version"
    else

	cat <<EOF

Error: there was a problem executing "setup clang $clang_version"
(return value was $retval). Please check the products directories
you've got set up. Exiting...

EOF

	exit 1
    fi

else

    cat<<EOF >&2

Error: a products directory containing clang isn't set up. Exiting...
EOF
    exit 2

fi

musts="bugprone-assert-side-effect,\
bugprone-copy-constructor-init,\
bugprone-infinite-loop,\
bugprone-integer-division,\
bugprone-macro-parentheses,\
bugprone-macro-repeated-side-effects,\
bugprone-move-forwarding-reference,\
bugprone-multiple-statement-macro,\
bugprone-reserved-identifier,\
bugprone-sizeof-expression,\
bugprone-string-integer-assignment,\
bugprone-throw-keyword-missing,\
bugprone-undefined-memory-manipulation,\
bugprone-unhandled-self-assignment,\
bugprone-unused-raii,\
bugprone-unused-return-value,\
bugprone-use-after-move,\
cert-dcl58-cpp,\
cert-env33-c,\
cert-err34-c,\
cert-err58-cpp,\
cert-oop57-cpp,\
cppcoreguidelines-init-variables,\
cppcoreguidelines-interfaces-global-init,\
cppcoreguidelines-macro-usage,\
cppcoreguidelines-narrowing-conversions,\
cppcoreguidelines-no-malloc,\
cppcoreguidelines-pro-bounds-constant-array-index,\
cppcoreguidelines-pro-bounds-pointer-arithmetic,\
cppcoreguidelines-pro-type-const-cast,\
cppcoreguidelines-pro-type-cstyle-cast,\
cppcoreguidelines-pro-type-reinterpret-cast,\
cppcoreguidelines-pro-type-static-cast-downcast,\
cppcoreguidelines-slicing,\
cppcoreguidelines-special-member-functions,\
fuchsia-trailing-return,\
fuchsia-virtual-inheritance,\
google-default-arguments,\
google-global-names-in-headers,\
misc-definitions-in-headers,\
misc-misplaced-const,\
misc-non-private-member-variables-in-classes,\
misc-throw-by-value-catch-by-reference,\
misc-uniqueptr-reset-release,\
misc-unused-alias-decls,\
misc-unused-using-decls,\
modernize-avoid-bind,\
modernize-avoid-c-arrays,\
modernize-concat-nested-namespaces,\
modernize-deprecated-headers,\
modernize-deprecated-ios-base-aliases,\
modernize-shrink-to-fit,\
modernize-use-auto,\
modernize-use-bool-literals,\
modernize-use-nullptr,\
performance-for-range-copy,\
performance-implicit-conversion-in-loop,\
performance-inefficient-algorithm,\
performance-inefficient-string-concatenation,\
performance-inefficient-vector-operation,\
performance-move-const-arg,\
performance-move-constructor-init,\
performance-unnecessary-copy-initialization,\
performance-unnecessary-value-param,\
readability-avoid-const-params-in-decls,\
readability-const-return-type,\
readability-container-size-empty,\
readability-deleted-default,\
readability-implicit-bool-conversion,\
readability-redundant-access-specifiers,\
readability-redundant-control-flow,\
readability-redundant-preprocessor,\
readability-redundant-smartptr-get,\
readability-static-definition-in-anonymous-namespace,\
readability-uniqueptr-delete-release"


maybes="bugprone-dynamic-static-initializers,\
bugprone-exception-escape,\
bugprone-fold-init-type,\
bugprone-forward-declaration-namespace,\
bugprone-forwarding-reference-overload,\
bugprone-incorrect-roundings,\
bugprone-misplaced-widening-cast,\
bugprone-parent-virtual-call,\
bugprone-spuriously-wake-up-functions,\
bugprone-suspicious-include,\
bugprone-suspicious-memset-usage,\
bugprone-too-small-loop-variable,\
bugprone-undelegated-constructor,\
cert-err60-cpp,\
cert-mem57-cpp,\
cert-msc50-cpp,\
cert-msc51-cpp,\
google-readability-casting,\
google-readability-todo,\
google-runtime-int,\
google-runtime-operator,\
hicpp-exception-baseclass,\
hicpp-multiway-paths-covered,\
misc-no-recursion,\
misc-unconventional-assign-operator,\
misc-unused-parameters,\
modernize-make-shared,\
modernize-make-unique,\
modernize-use-default-member-init,\
modernize-use-emplace,\
modernize-use-nodiscard,\
modernize-use-uncaught-exceptions,\
performance-type-promotion-in-math-fn,\
readability-delete-null-pointer,\
readability-function-size,\
readability-identifier-naming,\
readability-inconsistent-declaration-parameter-name,\
readability-isolate-declaration"



for source_file in $source_files; do

    echo
    echo "=========================Validating $source_file========================="

    clang-tidy -p=$compile_commands -checks=${musts},${maybes} -header-filter=.* $source_file # -- -I/home/nfs/dunecet/products/gcc/v6_4_0/Linux64bit+3.10-2.17/include/c++/6.4.0   

done
