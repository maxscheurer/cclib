# This file is part of cclib (http://cclib.github.io), a library for parsing
# and interpreting the results of computational chemistry packages.
#
# Copyright (C) 2014, the cclib development team
#
# The library is free software, distributed under the terms of
# the GNU Lesser General Public version 2.1 or later. You should have
# received a copy of the license along with cclib. You can also access
# the full license online at http://www.gnu.org/copyleft/lgpl.html.

"""A writer for chemical JSON (CJSON) files."""

import json

from . import filewriter


class CJSON(filewriter.Writer):
    """A writer for chemical JSON (CJSON) files."""

    def __init__(self, ccdata, *args, **kwargs):
        """Initialize the chemical JSON writer object.

        Inputs:
          ccdata - An instance of ccData, parsed from a logfile.
        """

        # Call the __init__ method of the superclass
        super(CJSON, self).__init__(ccdata, *args, **kwargs)

        self.generate_repr()

    def generate_repr(self):
        """Generate the CJSON representation of the logfile data."""

        # Generate the Open Babel/Pybel representation of the molecule.
        # Used for calculating SMILES/InChI, formula, MW, etc.
        obmol, pbmol = self._makeopenbabel_from_ccdata()

        cjson_dict = dict()
        cjson_dict['chemical json'] = 0

        # These are properties that can be collected using Open Babel.

        cjson_dict['smiles'] = pbmol.write('smiles')
        cjson_dict['inchi'] = pbmol.write('inchi')
        cjson_dict['inchikey'] = pbmol.write('inchikey')
        cjson_dict['formula'] = pbmol.formula

        cjson_dict['atoms'] = dict()
        cjson_dict['atoms']['elements'] = dict()
        cjson_dict['atoms']['elements']['number'] = self.ccdata.atomnos.tolist()
        cjson_dict['atoms']['coords'] = dict()
        cjson_dict['atoms']['coords']['3d'] = self.ccdata.atomcoords[-1].flatten().tolist()

        # Need to get connectivity information from Open Babel.
        # cjson_dict['bonds'] = dict()
        # cjson_dict['bonds']['connections'] = dict()
        # cjson_dict['bonds']['connections']['index'] = []
        # cjson_dict['bonds']['order'] = []

        cjson_dict['properties'] = dict()
        # Or is it pbmol.exactmass? Determine which is the isotopic
        # average and use that one.
        cjson_dict['properties']['molecular mass'] = pbmol.molwt

        cjson_dict['atomCount'] = obmol.NumAtoms()
        cjson_dict['heavyAtomCount'] = obmol.NumHvyAtoms()

        # These entries are likely to be added outside of Open Babel/cclib.
        # cjson_dict['annotations']
        # cjson_dict['diagram']
        # cjson_dict['3dStructure']

        # These are properties that can be collected using cclib.

        # Do there need to be any unit conversions here?
        homo_idx_alpha = int(self.ccdata.homos[0])
        homo_idx_beta = int(self.ccdata.homos[-1])
        energy_alpha_homo = self.ccdata.moenergies[0][homo_idx_alpha]
        energy_alpha_lumo = self.ccdata.moenergies[0][homo_idx_alpha + 1]
        energy_alpha_gap = energy_alpha_lumo - energy_alpha_homo
        energy_beta_homo = self.ccdata.moenergies[-1][homo_idx_beta]
        energy_beta_lumo = self.ccdata.moenergies[-1][homo_idx_beta + 1]
        energy_beta_gap = energy_beta_lumo - energy_beta_homo
        cjson_dict['energy'] = dict()
        cjson_dict['energy']['total'] = self.ccdata.scfenergies[-1]
        cjson_dict['energy']['alpha'] = dict()
        cjson_dict['energy']['alpha']['homo'] = energy_alpha_homo
        cjson_dict['energy']['alpha']['lumo'] = energy_alpha_lumo
        cjson_dict['energy']['alpha']['gap'] = energy_alpha_gap
        cjson_dict['energy']['beta'] = dict()
        cjson_dict['energy']['beta']['homo'] = energy_beta_homo
        cjson_dict['energy']['beta']['lumo'] = energy_beta_lumo
        cjson_dict['energy']['beta']['gap'] = energy_beta_gap

        cjson_dict['totalDipoleMoment'] = self._calculate_total_dipole_moment()

        # Can/should we append the entire original log file?
        # cjson_dict['files'] = dict()
        # cjson_dict['files']['log'] = []
        # cjson_dict['files']['log'].append()

        return json.dumps(cjson_dict)


if __name__ == "__main__":
    pass
