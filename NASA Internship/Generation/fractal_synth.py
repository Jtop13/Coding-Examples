import numpy as np

def fractal_synth(hpar=0.5, nfreq=64, std=None, phase=None, output_ft=False, verbose=False):
    """
    A Python implementation of the 2-D piece of the fractal synthesizer
    developed in IDL by Frank Varosi, HSTX @ NASA/GSFC, 1995.
    
    From IDL source code:
    ; FROM Varosi vlibm AstroContrib Library
    ; http://www.astro.washington.edu/deutsch/idl/htmlhelp/slibrary22.html - library discription
    ; http://www.astro.washington.edu/deutsch-bin/getpro/library21.html?GRIDXY  - modules location (gridxy.pro, etc.)

    ; see also http://www.astro.washington.edu/deutsch-bin/getpro/library22.html?FRACTAL_CLOUD  - 3-D fractal clouds
    ; ( it contains several external calls)

    ;Viewing contents of file '../idl/idllib/astron/contrib/varosi/vlibm/allpro/fractal_synth.pro'

    PURPOSE:
        Synthesize a fractal embedded in 2-D (a fractal curve) using power-law spectral technique.
    
    CALLING: 
        fluc, phase, ft = fractal_synth(verbose=True, output_ft=True)
        fluc, phase = fractal_synth(hpar=.2, nfreq=25)
        
    INPUTS:
        hpar:  H parameter determining the theoretical fractal dimension D. (default=0.5)
            Should normally be in the range 0 to 1 so that D = E - H,
            where E = embedding dimension (in this case, 2). The theoretical fractal
            dimension is approached as number of frequencies goes infinite.
            The power-law exponent of power spectral density = -(2*H+E-1).
            Statistically, the average variance of points on the fractal
            scales as the distance between the points to the power 2*H.
        
        nfreq:  Number of frequencies to use in spectral synthesis. (default=64)
            Note, output sequence will be length 2*nfreq.
            
        std:  Standard deviation of random noise added to amplitudes. (default=None)
        
        phase: Array of length nfreq+1, each element in [0,1].  (optional)
            If not set, a random array is selected from the uniform distribution.
            Pass this argument to keep the same phases while changing H.
            Internally, this phase array is scaled to between 0 and 2*pi.
            
        output_ft: Set as True to return the Fourier spectrum used to 
            generate the synthesized curve. (default=False)

        verbose: Set as True for more printed output. (default=False)
        
    OUTPUT:
        nominal
            - A 2-tuple holding the synthesized fractal curve and the phase array used.
                (fractal_curve, phase)
                    
        if output_ft == True
            - A 3-tuple that includes the Fourier spectrum used 
                (fractal_curve, phase, fourier_spectrum)

    ADAPTED BY: Ayris Narock (ADNET/GSFC) 2020 

    """
    
    edim = 2
    ndim = edim - 1
    
    hpar = float(hpar)
    nfreq = int(nfreq) 
    assert nfreq > 0, "\'nfreq\' must be > 0"
    
    if verbose:
        fdim = edim-hpar
        if fdim < 1:
            fdim = 1
        elif fdim > 2:
            fdim = 2
        print("fractal dimension = {fdim}".format(fdim=fdim))
        
    power = -( hpar + 0.5 )
    with np.errstate(divide='ignore'):
        fa = np.arange(nfreq+1)**power
    fa[0] = 0
    nf = np.size(fa)
        
    rng = np.random.default_rng()
    
    if std:
        fa = fa + rng.normal(scale=std, size=nf)
        fa[fa < 0] = 0
        fa[0] = 0

    if phase is None:
        phase = rng.uniform(size=nf)
    else:
        phase = np.array(phase)
        assert np.size(phase) == nf, "\'phase\' must be length {} (\'nfreq\'+1)".format(nf)

    fc = fa * np.e**(2 * np.pi * complex(0,1) * phase)
    fourier_spectrum = np.append(fc[0:-1],  np.flip(np.conj(fc[1:])))
    fractal_curve = np.fft.ifft(fourier_spectrum).real

    if output_ft:
        return (fractal_curve, phase, fourier_spectrum)
    else:
        return (fractal_curve, phase)