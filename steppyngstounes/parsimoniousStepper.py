# Begin forwarded message:
# 
# From: David Huard <david.huard@gmail.com>
# Subject: Re: [SciPy-user] "smooth" plots
# Date: April 1, 2009 at 4:23:14 PM EDT
# To: "Guyer, Jonathan E. Dr." <jonathan.guyer@nist.gov>
# 
# Jonathan, 
# 
# Here are bits of code I've extracted from a project of mine.  You'll have
# to do some imports from numpy to get it to work.  It's not pretty, but it
# was enough for my use case.  I'd be interested to look at papers that
# discuss this problem if you have references nearby.  Note that I also
# have a version that calls func on multiple processes (using ipython).
# With 2 quad cores, this sped up considerably my application.
# 
# HTH, 
# 
# David


def parsimonious_computation(func, range, N, scale='dl', args=(),show=False):
    """Compute func parsimoniously N times over range -> x, func(x)
    
    Compute the function where the curvature is highest and where not many
    points have been computed. 
    
    """
    
    candidates = list(linspace(range[0], range[1], min(max([4, N/3]), 11)))
    y = []
    x = []
    
    while (len(x) < N):
        if show:
            plot(x,y,'bo')
            sleep(.2)
            
        if len(candidates) == 0 :
            candidates += find_candidate(x,y,scale).tolist()
        current_x = candidates.pop(0)
        current_y = func(current_x, *args)
        #print 'current: ',current_x, current_y
        x.append(current_x)
        x.sort()
        i = x.index(current_x)
        y.insert(i, current_y)

        #print i, x, y
        if show:
            plot([x[i]], [y[i]], 'ro')
            draw_if_interactive()

    return sortxy(x,y)



def sortxy(x, y):
    """Sort x and y so that x is in accending order."""
    sy = np.squeeze(asarray(y))
    sx = np.squeeze(asarray(x))
    si = sx.argsort()
    sx = sx[si]
    sy = sy[si]
    return np.squeeze(sx), np.squeeze(sy)  

def find_candidate(x,y,scale='dl'):
    """Given points (x,y) on a continuous curve, select a new x_i
    where the computation of y_i will yield valuable new information 
    about the curve. 
    
    Regions of high curvature are sampled preferably, as well as 
    regions scarcely sampled by x. 

    The scale parameter allows to populate according to dy or dl.
   
    """
    y = asarray(y)
    x = asarray(x)
    
    i = x.argsort()
    x.sort()
    y = y[i]
    
    dx = diff(x)
    dy = diff(y)
    dn2 = diff(y,2)
    dn2 = concatenate([[dn2[0]/2,], dn2, [dn2[-1]/2]])
    der2 = interp1d(x,dn2)
    dl = sqrt(dx**2 + dy**2)
    centerx = x[:-1]+dx/2
    d2 = der2(centerx)
    if scale == 'dl':
        cons = dl*sqrt(abs(d2))
    elif scale=='dy':
        cons = abs(dy)*abs(d2)
    else:
        raise 'Scale not recognized.',scale
    i = argmax(cons)
    #newx = x[max(0,i-1):i+1]+dx[max(0,i-1):i+1]/2.
    newx = array([centerx[i]])
    if len(newx) == 0:
        raise 'No candidate found.'
    #print cons, sqrt(abs(dy)), abs(d2), i, newx
    return newx

