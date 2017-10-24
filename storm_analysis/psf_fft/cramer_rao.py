#!/usr/bin/env python
"""
PSF FFT object for Cramer-Rao bounds calculations.

Hazen 10/17
"""
import pickle

import storm_analysis.spliner.cramer_rao as cramerRao

import storm_analysis.psf_fft.psf_fft_c as psfFFTC


class CRPSFFn(cramerRao.CRPSFObject):
    """
    A PSF FFT based PSF Object for Cramer-Rao bounds calculations.
    """
    def __init__(self, psf_filename = None, **kwds):
        kwds["psf_filename"] = psf_filename
        super(CRPSFFn, self).__init__(**kwds)

        # Load the psf data.
        with open(psf_filename, 'rb') as fp:
            psf_data = pickle.load(fp)

        # Use C library to calculate the PSF and it's derivatives.
        psf = psf_data['psf']
        self.psf_fft_c = psfFFTC.PSFFFT(psf_data['psf'])

        # Additional initializations.
        self.zmax = psf_data["zmax"]
        self.zmin = psf_data["zmin"]
        self.scale_gSZ = (float(psf.shape[0]) - 1.0) / (self.zmax - self.zmin)

        # CR weights approximately ever 50nm.
        self.n_zvals = int(round((self.zmax - self.zmin)/25.0))
        
        self.delta_xy = self.pixel_size
        self.delta_z = (self.getZMax() - self.getZMin())/float(self.n_zvals)

    def cleanup(self):
        return self.psf_fft_c.cleanup()
    
    def getDeltaXY(self):
        """
        Return delta XY scaling term (in nanometers).
        """
        return self.delta_xy
        
    def getDeltaZ(self):
        """
        Return delta Z scaling term (in nanometers).
        """
        return self.delta_z
                
    def getDx(self, z_value):
        self.translate(z_value)
        return self.psf_fft_c.getPSFdx()

    def getDy(self, z_value):
        self.translate(z_value)
        return self.psf_fft_c.getPSFdy()
    
    def getDz(self, z_value):
        self.translate(z_value)
        return self.psf_fft_c.getPSFdz()

    def getNormalization(self):
        return self.normalization
        
    def getNZValues(self):
        return self.n_zvals
        
    def getPSF(self, z_value):
        self.translate(z_value)
        return self.psf_fft_c.getPSF()
    
    def getZMax(self):
        return self.zmax
    
    def getZMin(self):
        return self.zmin

    def translate(self, z_value):
        self.psf_fft_c.translate(0.0, 0.0, z_value * self.scale_gSZ)