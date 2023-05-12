# =======================================================================================
#
# This python module contains routines and utilities which will interpret the
# FATES fortran code base to return information on the use of parameters.
# This does not parse the CDL or NC files, this only parses the fortran code.
#
# This module will help:
#   1) List the parameters found in a given file
#   2) Determine the parameter names found therein
#   3) Determine the parameter's name in the parameter file
#
# Note: This module can be used to determine usage of any sybmol associated with
#       the instantiation of a structure.  Ie, you can search for all parameters
#       in the 'EDPftvarcon_inst%' structure.  In FATES, the EDParamsMod and SFParamsMod
#       don't use a structure to hold their parameters though.
#
# =======================================================================================

import code  # For development: code.interact(local=dict(globals(), **locals()))


class f90_param_type:

    # -----------------------------------------------
    # PFTParamType stucture. A list of these will be
    # generated that denotes the PFT parameters used.
    # -----------------------------------------------

    def __init__(self,var_sym,var_name,in_f90):

        self.var_sym  = var_sym   # Name of parameter in FORTRAN code
        self.var_name = var_name  # Parameter's name in the parameter file
        self.in_f90   = in_f90    # Are we passing this value to the f90 code?

        
def GetParamsInFile(filename):
    
    with open(filename,"r") as f:
        contents = f.readlines()
    checkstr = 'real(r8)'

    strclose = ',)( '

    var_list = []
    found = False

    for line in contents:
        if checkstr in line.lower():

            # We compare all in lower-case
            # There may be more than one parameter in a line,
            # so evaluate, pop-off, and try again

            substr   = line.lower()

            p1 = substr.find('::')+len('::')


            # Check for a comment symbol. If this
            # symbol is commenting out the variable
            # then we will ignore
            pcomment = substr.find('!')
            if(pcomment<0):
                pcomment=1000

            # This makes sure that if the line
            # has a comment, that it does not come before
            # the parameter symbol

            if ( (p1>len(checkstr)) and (p1 < pcomment)):

                # Identify the symbol by starting at the first
                # character after the %, and ending at a list
                # of possible symols including space
                substr2=substr[p1:].lstrip()

                pend=substr2.find('(')
                if (pend<0):
                    # This is likely a scalar
                    # if so, go out to the comment
                    # if no comment, just accept lenght as as
                    pend=substr2.find('!')
                if(pend<0):
                    pend=len(substr2)

                found=True
                substr2=substr2[:pend].rstrip()
                var_list.append(f90_param_type(substr2,'',True))


    if (not found):
        print(f'No parameters with prefix: {checkstr}')
        print(f'were found in file: {filename}')
        print('If this is expected, remove that file from search list.')
        exit(2)

    return(var_list)
    


        
def GetSymbolUsage(filename,checkstr_in):

    # ---------------------------------------------------------------------
    # This procedure will check a fortran file and return a list (non-unique)
    # of all the PFT parameters found in the code.
    # Note: This will only determine the symbol name in code, this will
    #       not determine the symbol name in the parameter file.
    # ---------------------------------------------------------------------

    checkstr = checkstr_in.lower()

    with open(filename,"r") as f:
        contents = f.readlines()
    strclose = ',)( '

    var_list = []
    found = False


    for line in contents:
        if checkstr in line.lower():

            if (checkstr[-1] != '%'):
                print('The GetSymbolUsage() procedure requires')
                print(' that a structure ending with % is passed in')
                print(f' check_str: --{check_str}--')
                exit(2)

            # We compare all in lower-case
            # There may be more than one parameter in a line,
            # so evaluate, pop-off, and try again

            substr   = line.lower()

            search_substr=True

            while(search_substr):

                p1 = substr.find(checkstr)+len(checkstr)

                pcomment = substr.find('!')
                if(pcomment<0):
                    pcomment=1000

                # This makes sure that if the line
                # has a comment, that it does not come before
                # the parameter symbol

                if( (p1>len(checkstr)) and (p1 < pcomment)):
                    found = True

                    # Identify the symbol by starting at the first
                    # character after the %, and ending at a list
                    # of possible symols including space
                    substr2=substr[p1:]
                    pend0=-1
                    for ch in strclose:
                        pend = substr2.find(ch)
                        if(pend>0):
                            substr2=substr2[:pend]
                            pend0=pend

                    var_list.append(f90_param_type(substr2,'',True))
                    if(pend0!=-1):
                        substr=substr[pend0:]
                    else:
                        print('Could not correctly identify the parameter string')
                        exit(2)

                else:
                    search_substr=False



    if (not found):
        print(f'No parameters with prefix: {checkstr}')
        print(f'were found in file: {filename}')
        print('If this is expected, remove that file from search list.')
        exit(2)


    return(var_list)




def GetPFTParmFileSymbols(var_list,pft_filename):

    with open(pft_filename,"r") as f:
        contents = f.readlines()
    var_name_list = []
    for var in var_list:
        for i,line in enumerate(contents):
            if (var.var_sym in line) and ('data' in line) and ('=' in line):
                var.var_name = contents[i-2].split()[-1].strip('\'')

    return(var_list)


def MakeListUnique(list_in):

    # This procedure simply filters
    # an input list and returns the unique entries

    unique_list = []
    for var in list_in:
        found = any((var.var_sym == uvar.var_sym) for uvar in unique_list)
        if(not found):
            unique_list.append(var)

    return(unique_list)
