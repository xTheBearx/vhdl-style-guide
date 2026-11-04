# -*- coding: utf-8 -*-
"""
Vendor libraries: the component declarations of vendor primitives and macros, read from the user's own installation
of the vendor tools, so that designs which use them analyze. Nothing from the vendors is copied into mhsg.

The design section lists them under vendor_libraries, before the libraries of the design are analyzed:

    vendor_libraries:
      - xilinx                                  # unisim and xpm, under $XILINX_VIVADO
      - vendor: microchip
        family: polarfire
        path: /opt/microchip/Libero_SoC_v2024.1
      - library: unisim                         # explicit files, for any vendor
        files: [/tools/Xilinx/Vivado/2024.1/data/vhdl/src/unisims/unisim_VCOMP.vhd]
      - vendor: xilinx                          # without an installation: stub packages written from the
        stubs: true                             # instances of the design, see stubs.py

A component of a vendor library has no entity, so GHDL keeps each instance as a black box, whose clock domain
behaviour is then declared, see black_box.py. Only declaration files are read: a library of simulation models
would make GHDL synthesize the models instead.

The locations below are where the vendors' installations keep these files. They can differ between versions:
when a file is not found, the error lists every location tried, and path or files overrides them.
"""

import glob
import os

from mhsg import exceptions

# vendor -> (environment variables that hold the installation directory, [(library, [candidate files], required)])
# A candidate is relative to the installation directory, may contain {family}, and may be a glob pattern.
VENDORS = {
    "xilinx": (
        ("XILINX_VIVADO", "XILINX_VIVADO_HOME"),
        [
            ("unisim", ["data/vhdl/src/unisims/unisim_VPKG.vhd"], False),
            ("unisim", ["data/vhdl/src/unisims/unisim_VCOMP.vhd"], True),
            ("xpm", ["data/ip/xpm/xpm_VCOMP.vhd"], False),
        ],
    ),
    "microchip": (
        ("LIBERO_INSTALL_DIR", "LIBERO_ROOT", "SYNPLIFY_PRO_ROOT"),
        [
            (
                "{family}",
                [
                    "Designer/lib/vhdl/{family}.vhd",
                    "SynplifyPro/lib/microsemi/{family}.vhd",
                    "lib/microsemi/{family}.vhd",
                    "SynplifyPro/lib/actel/{family}.vhd",
                    "lib/actel/{family}.vhd",
                ],
                True,
            ),
        ],
    ),
    "intel": (
        ("QUARTUS_ROOTDIR", "QUARTUS_ROOT"),
        [
            ("altera_mf", ["eda/sim_lib/altera_mf_components.vhd"], True),
            ("altera", ["eda/sim_lib/altera_primitives_components.vhd"], False),
            ("lpm", ["eda/sim_lib/220pack.vhd"], False),
            ("{family}", ["eda/sim_lib/{family}_components.vhd"], False),
        ],
    ),
    "lattice": (
        ("RADIANT_HOME", "LSC_RADIANT", "LSC_DIAMOND", "DIAMOND_HOME", "FOUNDRY"),
        [
            ("{family}", ["cae_library/synthesis/vhdl/{family}.vhd", "../cae_library/synthesis/vhdl/{family}.vhd"], True),
        ],
    ),
}
# Vendors whose libraries depend on the device family
FAMILY_VENDORS = ("microchip", "lattice")


class VendorLibrary:
    def __init__(self, sName, lFiles, sVendor, bStubs=False):
        self.name = sName
        self.files = lFiles
        self.vendor = sVendor
        # The files are stub packages written from the design, see stubs.py
        self.stubs = bStubs


def resolve(lEntries, dEnvironment=None):
    """Returns the VendorLibrary list of the vendor_libraries of a design section, or raises a ConfigurationError."""
    dEnvironment = os.environ if dEnvironment is None else dEnvironment
    lReturn = []
    for oEntry in lEntries or []:
        if isinstance(oEntry, str):
            oEntry = {"vendor": oEntry}
        if not isinstance(oEntry, dict):
            raise exceptions.ConfigurationError("ERROR: each vendor library is a vendor name, a map with vendor, or a map with library and files")
        if oEntry.get("stubs"):
            for sName in stub_libraries(oEntry):
                add(lReturn, VendorLibrary(sName, [], str(oEntry.get("vendor", "")).lower(), True))
            continue
        if "library" in oEntry:
            lFiles = [os.path.expandvars(str(s)) for s in oEntry.get("files") or []]
            for sFile in lFiles:
                if not os.path.isfile(sFile):
                    raise exceptions.ConfigurationError(f"ERROR: vendor library {oEntry['library']}: file {sFile} does not exist")
            if not lFiles:
                raise exceptions.ConfigurationError(f"ERROR: vendor library {oEntry['library']} lists no files")
            add(lReturn, VendorLibrary(str(oEntry["library"]), lFiles, str(oEntry.get("vendor", ""))))
            continue
        for oLibrary in vendor_libraries(oEntry, dEnvironment):
            add(lReturn, oLibrary)
    return lReturn


def stub_libraries(dEntry):
    """The names of the libraries of a vendor library entry with stubs: true."""
    if "library" in dEntry:
        if dEntry.get("files"):
            raise exceptions.ConfigurationError(f"ERROR: vendor library {dEntry['library']}: stubs and files exclude each other")
        return [str(dEntry["library"]).lower()]
    sVendor = str(dEntry.get("vendor", "")).lower()
    if sVendor not in VENDORS:
        raise exceptions.ConfigurationError(f"ERROR: unknown vendor {sVendor or '(none)'}; expected one of {', '.join(VENDORS)}, or library and stubs")
    sFamily = str(dEntry.get("family", "")).lower()
    if sVendor in FAMILY_VENDORS and not sFamily:
        raise exceptions.ConfigurationError(f"ERROR: vendor {sVendor} needs family, the device family, such as polarfire or ecp5u")
    lReturn = []
    for sLibrary, _, _ in VENDORS[sVendor][1]:
        if "{family}" in sLibrary and not sFamily:
            continue
        sName = sLibrary.format(family=sFamily)
        if sName not in lReturn:
            lReturn.append(sName)
    return lReturn


def add(lLibraries, oLibrary):
    """Adds a library, joining it with an earlier one of the same name."""
    for oExisting in lLibraries:
        if oExisting.name.lower() == oLibrary.name.lower():
            oExisting.files += [s for s in oLibrary.files if s not in oExisting.files]
            return
    lLibraries.append(oLibrary)


def vendor_libraries(dEntry, dEnvironment):
    sVendor = str(dEntry.get("vendor", "")).lower()
    if sVendor not in VENDORS:
        raise exceptions.ConfigurationError(f"ERROR: unknown vendor {sVendor or '(none)'}; expected one of {', '.join(VENDORS)}, or library and files")
    lVariables, lLibraries = VENDORS[sVendor]
    sFamily = str(dEntry.get("family", "")).lower()
    if sVendor in FAMILY_VENDORS and not sFamily:
        raise exceptions.ConfigurationError(f"ERROR: vendor {sVendor} needs family, the device family, such as polarfire or ecp5u")
    sPath = os.path.expandvars(str(dEntry["path"])) if dEntry.get("path") else None
    lRoots = [sPath] if sPath else [dEnvironment[s] for s in lVariables if dEnvironment.get(s)]
    if not lRoots:
        raise exceptions.ConfigurationError(
            f"ERROR: vendor {sVendor}: the installation is not known; set path in the vendor library, or one of the environment variables {', '.join(lVariables)}",
        )
    lReturn = []
    lTried = []
    for sLibrary, lCandidates, bRequired in lLibraries:
        if "{family}" in sLibrary and not sFamily:
            continue
        sName = sLibrary.format(family=sFamily)
        sFound = None
        for sRoot in lRoots:
            for sCandidate in lCandidates:
                sPattern = os.path.normpath(os.path.join(sRoot, sCandidate.format(family=sFamily)))
                lTried.append(sPattern)
                lMatches = sorted(glob.glob(sPattern)) if glob.has_magic(sPattern) else ([sPattern] if os.path.isfile(sPattern) else [])
                if lMatches:
                    sFound = lMatches[0]
                    break
            if sFound:
                break
        if sFound:
            add(lReturn, VendorLibrary(sName, [sFound], sVendor))
        elif bRequired:
            sTried = "\n  ".join(lTried)
            raise exceptions.ConfigurationError(
                f"ERROR: vendor {sVendor}: no declarations for library {sName} were found. Tried:\n  {sTried}\n"
                f"Set path to the installation, or list the files with library and files.",
            )
    return lReturn
