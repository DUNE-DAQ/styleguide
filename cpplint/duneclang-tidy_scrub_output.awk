BEGIN {
    
    RS="^"
    
    in_ers_lint=0

}


{
    # Get rid of complaints about external headers
    if ($0 ~ /^[[:space:]~]*\/cvmfs\/dunedaq.*opensciencegrid.org.*/) {
       next
    }

    # ...and catch instances of external header errors where the awk record includes the opening blurb

    if (NR == 1 && $0 ~ /Error while processing/ && $0 ~ /\/cvmfs/) {
	next
    }

    # Get rid of complaints about moo-generated code
    if ($0 ~/\/codegen\//) {
       next	
    }

    # Get rid of complaints about TLOG expansions
    if ($0 ~ /TLOG/) {
       next
    }

    # Get rid of complainst about BOOST expansions
    if ($0 ~ /BOOST_/) {
	next
    }

    # Get rid of spurious (and lengthy) complaint about template
    # parameters in iomanager's FollyQueue.hpp as well as other
    # spurious folly complaints (FollyMPMCQueue not existing, e.g.)

    if ($0 ~ /Folly.*Queue/) {
	next
    }
    
    # Get rid of complaints about ERS expansions
    if ($0 ~ /ERS_/) {
	#printf("\nMatched ERS_, setting in_ers_lint to 1")
	in_ers_lint = 1
        next
    }

    # Usually an expanded ERS macro has several warnings and
    # errors. They include expansions from /cvmfs-located headers, as
    # well as complaints about copy-by-values in expressions like
    # "((std::string)connection_name)((std::string)message))". We
    # don't need or want them cluttering up the linting output

    if (in_ers_lint == 1) {
	if ($0 ~ /xpanded from here/ || $0 ~ /\(\(.*\).*\)/) {
	    next
	}
    }

    in_ers_lint = 0

    # Users don't need to know about low-level clang-tidy details
    if ($0 ~ /Use -system-headers to display errors from system headers as well/) {
	next
    }

    if ($0 ~ /DEFINE_DUNE_DAQ_MODULE/) {
	next
    }

    if ($0 ~ /xpanded from here[[:space:]~:]*\/cvmfs/) {
	next
    }

    if ($0 ~ /note:.*requested here/) {  # Possibly too draconian
	next
    }

    print
}
