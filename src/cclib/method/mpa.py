"""
cclib is a parser for computational chemistry log files.

See http://cclib.sf.net for more information.

Copyright (C) 2006 Noel O'Boyle and Adam Tenderholt

 This program is free software; you can redistribute and/or modify it
 under the terms of the GNU General Public License as published by the
 Free Software Foundation; either version 2, or (at your option) any later
 version.

 This program is distributed in the hope that it will be useful, but
 WITHOUT ANY WARRANTY, without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 General Public License for more details.

Contributions (monetary as well as code :-) are encouraged.
"""
import re,time
import Numeric
import random # For sometimes running the progress updater
from population import Population

class MPA(Population):
    """The Mulliken population analysis"""
    def __init__(self,*args):

        # Call the __init__ method of the superclass
        super(MPA, self).__init__(logname="MPA",*args)
        
    def __str__(self):
        """Return a string representation of the object."""
        return "MPA of" % (self.parser)

    def __repr__(self):
        """Return a representation of the object."""
        return 'MPA("%s")' % (self.parser)
    
    def calculate(self,indices=None,fupdate=0.05):
        """Perform a Mulliken population analysis given the results of a parser"""
    
        if not self.parser.parsed:
            self.parser.parse()

        #do we have the needed info in the parser?
        if not hasattr(self.parser,"mocoeffs") \
          and not ( hasattr(self.parser,"aooverlaps") \
                    or hasattr(self.parser, "fooverlaps") ) \
          and not hasattr(self.parser,"nbasis"):
            self.logger.error("Missing mocoeffs, aooverlaps/fooverlaps or nbasis")
            return False #let the caller of function know we didn't finish

        unrestricted=(len(self.parser.mocoeffs)==2)
        nmocoeffs=len(self.parser.mocoeffs[0])
        nbasis=self.parser.nbasis

        #determine number of steps, and whether process involves beta orbitals
        nstep=nmocoeffs
        self.logger.info("Creating attribute aoresults: array[3]")
        if unrestricted:
            self.aoresults=Numeric.zeros([2,nmocoeffs,nbasis],"f")
            nstep+=nmocoeffs
        else:
            self.aoresults=Numeric.zeros([1,nmocoeffs,nbasis],"f")

        #intialize progress if available
        if self.progress:
            self.progress.initialize(nstep)

        step=0
        for spin in range(len(self.parser.mocoeffs)):

            for i in range(nmocoeffs):

                if self.progress and random.random()<fupdate:
                    self.progress.update(step,"Mulliken Population Analysis")

                #X_{ai} = \sum_b c_{ai} c_{bi} S_{ab}
                #       = c_{ai} \sum_b c_{bi} S_{ab}
                #       = c_{ai} C(i) \cdot S(a)
                # X = C(i) * [C(i) \cdot S]
                # C(i) is 1xn and S is nxn, result of matrix mult is 1xn

                ci = self.parser.mocoeffs[spin][i]
                if hasattr(self.parser,"aooverlaps"):
                    temp = Numeric.matrixmultiply(ci,self.parser.aooverlaps)
                elif hasattr(self.parser,"fooverlaps"):
                    temp = Numeric.matrixmultiply(ci,self.parser.fooverlaps)

                self.aoresults[spin][i]=Numeric.multiply(ci,temp)

                step+=1

        if self.progress:
            self.progress.update(nstep,"Done")

        retval=super(MPA, self).partition(indices)

        if not retval:
            self.logger.error("Error in partitioning results")
            return False

#create array for mulliken charges
        self.logger.info("Creating fragcharges: array[1]")
        size=len(self.fragresults[0][0])
        self.fragcharges=Numeric.zeros([size],"f")
        
        for spin in range(len(self.fragresults)):

            for i in range(self.parser.homos[spin]+1):

                temp=Numeric.reshape(self.fragresults[spin][i],(size,))
                self.fragcharges=Numeric.add(self.fragcharges,temp)
        
        if not unrestricted:
            self.fragcharges=Numeric.multiply(self.fragcharges,2)

        return True

if __name__=="__main__":
    import doctest,mpa
    doctest.testmod(mpa,verbose=False)