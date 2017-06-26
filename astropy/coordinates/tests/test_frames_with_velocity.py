# -*- coding: utf-8 -*-
# Licensed under a 3-clause BSD style license - see LICENSE.rst

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import pytest

from ... import units as u
from ..builtin_frames import ICRS, Galactic, Galactocentric
from ...tests.helper import quantity_allclose


def test_api():
    # transform observed Barycentric velocities to full-space Galactocentric
    gc_frame = Galactocentric()
    icrs = ICRS(ra=151.*u.deg, dec=-16*u.deg, distance=101*u.pc,
                pm_ra_cosdec=21*u.mas/u.yr, pm_dec=-71*u.mas/u.yr,
                radial_velocity=71*u.km/u.s)
    icrs.transform_to(gc_frame)

    # transform a set of ICRS proper motions to Galactic
    icrs = ICRS(ra=151.*u.deg, dec=-16*u.deg,
                pm_ra_cosdec=21*u.mas/u.yr, pm_dec=-71*u.mas/u.yr)
    icrs.transform_to(Galactic)

    # transform a Barycentric RV to a GSR RV
    icrs = ICRS(ra=151.*u.deg, dec=-16*u.deg, distance=1.*u.pc,
                pm_ra_cosdec=0*u.mas/u.yr, pm_dec=0*u.mas/u.yr,
                radial_velocity=71*u.km/u.s)
    icrs.transform_to(Galactocentric)


def test_all_arg_options():
    # I think this is a list of all possible valid combinations of arguments.
    # Here we do a simple thing and just verify that passing them in, we have
    # access to the relevant attributes from the resulting object
    all_kwargs = []

    all_kwargs += [dict(ra=37.4*u.deg, dec=-55.8*u.deg)]
    all_kwargs += [dict(ra=37.4*u.deg, dec=-55.8*u.deg, distance=150*u.pc)]

    all_kwargs += [dict(ra=37.4*u.deg, dec=-55.8*u.deg,
                        pm_ra_cosdec=-21.2*u.mas/u.yr, pm_dec=17.1*u.mas/u.yr)]
    all_kwargs += [dict(ra=37.4*u.deg, dec=-55.8*u.deg, distance=150*u.pc,
                        pm_ra_cosdec=-21.2*u.mas/u.yr, pm_dec=17.1*u.mas/u.yr)]

    all_kwargs += [dict(ra=37.4*u.deg, dec=-55.8*u.deg,
                        radial_velocity=105.7*u.km/u.s)]
    all_kwargs += [dict(ra=37.4*u.deg, dec=-55.8*u.deg, distance=150*u.pc,
                        radial_velocity=105.7*u.km/u.s)]

    all_kwargs += [dict(ra=37.4*u.deg, dec=-55.8*u.deg, distance=150*u.pc,
                        pm_ra_cosdec=-21.2*u.mas/u.yr, pm_dec=17.1*u.mas/u.yr,
                        radial_velocity=105.7*u.km/u.s)]

    for i, kwargs in enumerate(all_kwargs):
        icrs = ICRS(**kwargs)

        for k in kwargs:
            getattr(icrs, k)


# these data are extracted from the vizier copy of XHIP:
# http://vizier.u-strasbg.fr/viz-bin/VizieR-3?-source=+V/137A/XHIP
_xhip_head = """
------ ------------ ------------ -------- -------- ------------ ------------ ------- -------- -------- ------- ------ ------ ------
       R            D            pmRA     pmDE                               Di      pmGLon   pmGLat   RV      U      V      W
HIP    AJ2000 (deg) EJ2000 (deg) (mas/yr) (mas/yr) GLon (deg)   GLat (deg)   st (pc) (mas/yr) (mas/yr) (km/s)  (km/s) (km/s) (km/s)
------ ------------ ------------ -------- -------- ------------ ------------ ------- -------- -------- ------- ------ ------ ------
"""[1:-1]
_xhip_data = """
    19 000.05331690 +38.30408633    -3.17   -15.37 112.00026470 -23.47789171  247.12    -6.40   -14.33    6.30    7.3    2.0  -17.9
    20 000.06295067 +23.52928427    36.11   -22.48 108.02779304 -37.85659811   95.90    29.35   -30.78   37.80  -19.3   16.1  -34.2
    21 000.06623581 +08.00723430    61.48    -0.23 101.69697120 -52.74179515  183.68    58.06   -20.23  -11.72  -45.2  -30.9   -1.3
 24917 080.09698238 -33.39874984    -4.30    13.40 236.92324669 -32.58047131  107.38   -14.03    -1.15   36.10  -22.4  -21.3  -19.9
 59207 182.13915108 +65.34963517    18.17     5.49 130.04157185  51.18258601   56.00   -18.98    -0.49    5.70    1.5    6.1    4.4
 87992 269.60730667 +36.87462906   -89.58    72.46  62.98053142  25.90148234  129.60    45.64   105.79   -4.00  -39.5  -15.8   56.7
115110 349.72322473 -28.74087144    48.86    -9.25  23.00447250 -69.52799804  116.87    -8.37   -49.02   15.00  -16.8  -12.2  -23.6
"""[1:-1]

# in principal we could parse the above as a table, but doing it "manually"
# makes this test less tied to Table working correctly
@pytest.mark.parametrize('hip,ra,dec,pmra,pmdec,glon,glat,dist,pmglon,pmglat,rv,U,V,W',
                         [[float(val) for val in row.split()] for row in _xhip_data.split('\n')])
def test_xhip_galactic(hip,ra, dec, pmra, pmdec, glon, glat, dist, pmglon, pmglat, rv, U, V, W):
    i = ICRS(ra*u.deg, dec*u.deg, dist*u.pc,
             pm_ra_cosdec=pmra*u.marcsec/u.yr, pm_dec=pmdec*u.marcsec/u.yr,
             radial_velocity=rv*u.km/u.s)
    g = i.transform_to(Galactic)

    # precision is limited by 2-deciimal digit string representation of pms
    assert quantity_allclose(g.pm_l_cosb, pmglon*u.marcsec/u.yr, atol=.01*u.marcsec/u.yr)
    assert quantity_allclose(g.pm_b, pmglat*u.marcsec/u.yr, atol=.01*u.marcsec/u.yr)

    # make sure UVW also makes sense
    uvwg = g.cartesian.differentials['s']
    # precision is limited by 1-decimal digit string representation of vels
    assert quantity_allclose(uvwg.d_x, U*u.km/u.s, atol=.1*u.km/u.s)
    assert quantity_allclose(uvwg.d_y, V*u.km/u.s, atol=.1*u.km/u.s)
    assert quantity_allclose(uvwg.d_z, W*u.km/u.s, atol=.1*u.km/u.s)
