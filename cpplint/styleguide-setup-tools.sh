
#------------------------------------------------------------------------------
HERE=$(cd $(dirname $(readlink -f ${BASH_SOURCE})) && pwd)

function spack_get_clang() {

    clang_spack_dir="/cvmfs/dunedaq.opensciencegrid.org/spack/externals"

    if [[ -z $SPACK_ROOT ]]; then
	echo "Error: the Spack environment doesn't seem to be set up. Exiting..." >&2
	exit 100
    fi

    llvmdir=$( spack find -p llvm | sed -r -n 's!.*('$clang_spack_dir'.*)$!\1!p' )
    
    if [[ -z $llvmdir ]]; then
	echo "Spack appears to be set up (SPACK_ROOT == $SPACK_ROOT) but unable to find directory for package llvm. Exiting..." >&2
	exit 101
    fi

    theclang=$( which clang 2>/dev/null )
    if ! [[ -n $( $theclang ) && "$theclang" =~ "^${llvmdir}/bin/clang" ]]; then
	cmd="spack load llvm"
	$cmd
	if [[ "$?" != "0" ]]; then
	    echo "Unable to successfully call \"$cmd\"; exiting..." >&2
	    exit 11
	fi
    fi
}

function ups_get_clang() {
    clang_products_dir=/cvmfs/dunedaq.opensciencegrid.org/products

    if [[ -d $clang_products_dir ]]; then
	. $clang_products_dir/setup
	retval="$?"
    else
	cat <<EOF >&2

The $clang_products_dir products area
is not found; this is currently needed for the script to find clang-tidy. Exiting...

EOF
	exit 20;
    fi

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


}
