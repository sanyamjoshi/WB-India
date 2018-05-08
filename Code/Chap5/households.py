'''
------------------------------------------------------------------------
This module contains the functions that generate the variables
associated with households' optimization in the steady-state or in the
transition path of the overlapping generations model with S-period lived
agents and endogenous labor supply from Chapter 7 of the OG textbook.

This Python module imports the following module(s): None

This Python module defines the following function(s):
    get_cons()
    MU_c_stitch()
    MDU_n_stitch()
    get_n_errors()
    get_b_errors()
    get_cnb_vecs()
    c1_bSp1err()
------------------------------------------------------------------------
'''
# Import packages
import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import os

'''
------------------------------------------------------------------------
    Functions
------------------------------------------------------------------------
'''


def get_cons(r, w, b, b_sp1, n, e):
    '''
    --------------------------------------------------------------------
    Calculate household consumption given prices, labor supply, current
    wealth, and savings
    --------------------------------------------------------------------
    INPUTS:
    r     = scalar or (p,) vector, current interest rate or time path of
            interest rates over remaining life periods
    w     = scalar or (p,) vector, current wage or time path of wages
            over remaining life periods
    b     = scalar or (p,) vector, current period wealth or time path of
            current period wealths over remaining life periods
    b_sp1 = scalar or (p,) vector, savings for next period or time path
            of savings for next period over remaining life periods
    n     = scalar or (p,) vector, current labor supply or time path of
            labor supply over remaining life periods
    e     = scalar or (p,) vector, current labor productivity or time
            path of labor productivity over remaining life periods


    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION: None

    OBJECTS CREATED WITHIN FUNCTION:
    cons = scalar or (p,) vector, current consumption or time path of
           consumption over remaining life periods

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: cons
    --------------------------------------------------------------------
    '''
    cons = ((1 + r) * b) + (w * n * e) - b_sp1

    return cons


def MU_c_stitch(cvec, sigma, graph=False):
    '''
    --------------------------------------------------------------------
    Generate marginal utility(ies) of consumption with CRRA consumption
    utility and stitched function at lower bound such that the new
    hybrid function is defined over all consumption on the real
    line but the function has similar properties to the Inada condition.

    u'(c) = c ** (-sigma) if c >= epsilon
          = g'(c) = 2 * b2 * c + b1 if c < epsilon

        such that g'(epsilon) = u'(epsilon)
        and g''(epsilon) = u''(epsilon)

        u(c) = (c ** (1 - sigma) - 1) / (1 - sigma)
        g(c) = b2 * (c ** 2) + b1 * c + b0
    --------------------------------------------------------------------
    INPUTS:
    cvec  = scalar or (p,) vector, individual consumption value or
            lifetime consumption over p consecutive periods
    sigma = scalar >= 1, coefficient of relative risk aversion for CRRA
            utility function: (c**(1-sigma) - 1) / (1 - sigma)
    graph = boolean, =True if want plot of stitched marginal utility of
            consumption function

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION: None

    OBJECTS CREATED WITHIN FUNCTION:
    epsilon    = scalar > 0, positive value close to zero
    c_s        = scalar, individual consumption
    c_s_cnstr  = boolean, =True if c_s < epsilon
    b1         = scalar, intercept value in linear marginal utility
    b2         = scalar, slope coefficient in linear marginal utility
    MU_c       = scalar or (p,) vector, marginal utility of consumption
                 or vector of marginal utilities of consumption
    p          = integer >= 1, number of periods remaining in lifetime
    cvec_cnstr = (p,) boolean vector, =True for values of cvec < epsilon

    FILES CREATED BY THIS FUNCTION:
        MU_c_stitched.png

    RETURNS: MU_c
    --------------------------------------------------------------------
    '''
    epsilon = 0.0001
    if np.ndim(cvec) == 0:
        c_s = cvec
        c_s_cnstr = c_s < epsilon
        if c_s_cnstr:
            b2 = (-sigma * (epsilon ** (-sigma - 1))) / 2
            b1 = (epsilon ** (-sigma)) - 2 * b2 * epsilon
            MU_c = 2 * b2 * c_s + b1
        else:
            MU_c = c_s ** (-sigma)
    elif np.ndim(cvec) == 1:
        p = cvec.shape[0]
        cvec_cnstr = cvec < epsilon
        MU_c = np.zeros(p)
        MU_c[~cvec_cnstr] = cvec[~cvec_cnstr] ** (-sigma)
        b2 = (-sigma * (epsilon ** (-sigma - 1))) / 2
        b1 = (epsilon ** (-sigma)) - 2 * b2 * epsilon
        MU_c[cvec_cnstr] = 2 * b2 * cvec[cvec_cnstr] + b1

    if graph:
        '''
        ----------------------------------------------------------------
        cur_path    = string, path name of current directory
        output_fldr = string, folder in current path to save files
        output_dir  = string, total path of images folder
        output_path = string, path of file name of figure to be saved
        cvec_CRRA   = (1000,) vector, support of c including values
                      between 0 and epsilon
        MU_CRRA     = (1000,) vector, CRRA marginal utility of
                      consumption
        cvec_stitch = (500,) vector, stitched support of consumption
                      including negative values up to epsilon
        MU_stitch   = (500,) vector, stitched marginal utility of
                      consumption
        ----------------------------------------------------------------
        '''
        # Create directory if images directory does not already exist
        cur_path = os.path.split(os.path.abspath(__file__))[0]
        output_fldr = "images"
        output_dir = os.path.join(cur_path, output_fldr)
        if not os.access(output_dir, os.F_OK):
            os.makedirs(output_dir)

        # Plot steady-state consumption and savings distributions
        cvec_CRRA = np.linspace(epsilon / 2, epsilon * 3, 1000)
        MU_CRRA = cvec_CRRA ** (-sigma)
        cvec_stitch = np.linspace(-0.00005, epsilon, 500)
        MU_stitch = 2 * b2 * cvec_stitch + b1
        fig, ax = plt.subplots()
        plt.plot(cvec_CRRA, MU_CRRA, ls='solid', label='$u\'(c)$: CRRA')
        plt.plot(cvec_stitch, MU_stitch, ls='dashed', color='red',
                 label='$g\'(c)$: stitched')
        # for the minor ticks, use no labels; default NullFormatter
        minorLocator = MultipleLocator(1)
        ax.xaxis.set_minor_locator(minorLocator)
        plt.grid(b=True, which='major', color='0.65', linestyle='-')
        plt.title('Marginal utility of consumption with stitched ' +
                  'function', fontsize=14)
        plt.xlabel(r'Consumption $c$')
        plt.ylabel(r'Marginal utility $u\'(c)$')
        plt.xlim((-0.00005, epsilon * 3))
        # plt.ylim((-1.0, 1.15 * (b_ss.max())))
        plt.legend(loc='upper right')
        output_path = os.path.join(output_dir, "MU_c_stitched")
        plt.savefig(output_path)
        # plt.show()

    return MU_c


def MDU_n_stitch(nvec, params, graph=False):
    '''
    --------------------------------------------------------------------
    Generate marginal disutility(ies) of labor with elliptical
    disutility of labor function and stitched functions at lower bound
    and upper bound of labor supply such that the new hybrid function is
    defined over all labor supply on the real line but the function has
    similar properties to the Inada conditions at the upper and lower
    bounds.

    v'(n) = (b / l_tilde) * ((n / l_tilde) ** (upsilon - 1)) *
            ((1 - ((n / l_tilde) ** upsilon)) ** ((1-upsilon)/upsilon))
            if n >= eps_low <= n <= eps_high
          = g_low'(n)  = 2 * b2 * n + b1 if n < eps_low
          = g_high'(n) = 2 * d2 * n + d1 if n > eps_high

        such that g_low'(eps_low) = u'(eps_low)
        and g_low''(eps_low) = u''(eps_low)
        and g_high'(eps_high) = u'(eps_high)
        and g_high''(eps_high) = u''(eps_high)

        v(n) = -b *(1 - ((n/l_tilde) ** upsilon)) ** (1/upsilon)
        g_low(n)  = b2 * (n ** 2) + b1 * n + b0
        g_high(n) = d2 * (n ** 2) + d1 * n + d0
    --------------------------------------------------------------------
    INPUTS:
    nvec   = scalar or (p,) vector, labor supply value or labor supply
             values over remaining periods of lifetime
    params = length 3 tuple, (l_tilde, b_ellip, upsilon)
    graph  = Boolean, =True if want plot of stitched marginal disutility
             of labor function

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION: None

    OBJECTS CREATED WITHIN FUNCTION:
    l_tilde       = scalar > 0, time endowment for each agent each per
    b_ellip       = scalar > 0, scale parameter for elliptical utility
                    of leisure function
    upsilon       = scalar > 1, shape parameter for elliptical utility
                    of leisure function
    eps_low       = scalar > 0, positive value close to zero
    eps_high      = scalar > 0, positive value just less than l_tilde
    n_s           = scalar, individual labor supply
    n_s_low       = boolean, =True for n_s < eps_low
    n_s_high      = boolean, =True for n_s > eps_high
    n_s_uncstr    = boolean, =True for n_s >= eps_low and
                    n_s <= eps_high
    MDU_n         = scalar or (p,) vector, marginal disutility or
                    marginal utilities of labor supply
    b1            = scalar, intercept value in linear marginal
                    disutility of labor at lower bound
    b2            = scalar, slope coefficient in linear marginal
                    disutility of labor at lower bound
    d1            = scalar, intercept value in linear marginal
                    disutility of labor at upper bound
    d2            = scalar, slope coefficient in linear marginal
                    disutility of labor at upper bound
    p             = integer >= 1, number of periods remaining in life
    nvec_s_low    = boolean, =True for n_s < eps_low
    nvec_s_high   = boolean, =True for n_s > eps_high
    nvec_s_uncstr = boolean, =True for n_s >= eps_low and
                    n_s <= eps_high

    FILES CREATED BY THIS FUNCTION:
        MDU_n_stitched.png

    RETURNS: MDU_n
    --------------------------------------------------------------------
    '''
    l_tilde, b_ellip, upsilon = params
    eps_low = 0.000001
    eps_high = l_tilde - 0.000001
    # This if is for when nvec is a scalar
    if np.ndim(nvec) == 0:
        n_s = nvec
        n_s_low = n_s < eps_low
        n_s_high = n_s > eps_high
        n_s_uncstr = (n_s >= eps_low) and (n_s <= eps_high)
        if n_s_uncstr:
            MDU_n = \
                ((b_ellip / l_tilde) * ((n_s / l_tilde) **
                 (upsilon - 1)) * ((1 - ((n_s / l_tilde) ** upsilon)) **
                 ((1 - upsilon) / upsilon)))
        elif n_s_low:
            b2 = (0.5 * b_ellip * (l_tilde ** (-upsilon)) *
                  (upsilon - 1) * (eps_low ** (upsilon - 2)) *
                  ((1 - ((eps_low / l_tilde) ** upsilon)) **
                  ((1 - upsilon) / upsilon)) *
                  (1 + ((eps_low / l_tilde) ** upsilon) *
                  ((1 - ((eps_low / l_tilde) ** upsilon)) ** (-1))))
            b1 = ((b_ellip / l_tilde) * ((eps_low / l_tilde) **
                  (upsilon - 1)) *
                  ((1 - ((eps_low / l_tilde) ** upsilon)) **
                  ((1 - upsilon) / upsilon)) - (2 * b2 * eps_low))
            MDU_n = 2 * b2 * n_s + b1
        elif n_s_high:
            d2 = (0.5 * b_ellip * (l_tilde ** (-upsilon)) *
                  (upsilon - 1) * (eps_high ** (upsilon - 2)) *
                  ((1 - ((eps_high / l_tilde) ** upsilon)) **
                  ((1 - upsilon) / upsilon)) *
                  (1 + ((eps_high / l_tilde) ** upsilon) *
                  ((1 - ((eps_high / l_tilde) ** upsilon)) ** (-1))))
            d1 = ((b_ellip / l_tilde) * ((eps_high / l_tilde) **
                  (upsilon - 1)) *
                  ((1 - ((eps_high / l_tilde) ** upsilon)) **
                  ((1 - upsilon) / upsilon)) - (2 * d2 * eps_high))
            MDU_n = 2 * d2 * n_s + d1
    # This if is for when nvec is a one-dimensional vector
    elif np.ndim(nvec) == 1:
        p = nvec.shape[0]
        nvec_low = nvec < eps_low
        nvec_high = nvec > eps_high
        nvec_uncstr = np.logical_and(~nvec_low, ~nvec_high)
        MDU_n = np.zeros(p)
        MDU_n[nvec_uncstr] = (
            (b_ellip / l_tilde) *
            ((nvec[nvec_uncstr] / l_tilde) ** (upsilon - 1)) *
            ((1 - ((nvec[nvec_uncstr] / l_tilde) ** upsilon)) **
             ((1 - upsilon) / upsilon)))
        b2 = (0.5 * b_ellip * (l_tilde ** (-upsilon)) * (upsilon - 1) *
              (eps_low ** (upsilon - 2)) *
              ((1 - ((eps_low / l_tilde) ** upsilon)) **
              ((1 - upsilon) / upsilon)) *
              (1 + ((eps_low / l_tilde) ** upsilon) *
              ((1 - ((eps_low / l_tilde) ** upsilon)) ** (-1))))
        b1 = ((b_ellip / l_tilde) * ((eps_low / l_tilde) **
              (upsilon - 1)) *
              ((1 - ((eps_low / l_tilde) ** upsilon)) **
              ((1 - upsilon) / upsilon)) - (2 * b2 * eps_low))
        MDU_n[nvec_low] = 2 * b2 * nvec[nvec_low] + b1
        d2 = (0.5 * b_ellip * (l_tilde ** (-upsilon)) * (upsilon - 1) *
              (eps_high ** (upsilon - 2)) *
              ((1 - ((eps_high / l_tilde) ** upsilon)) **
              ((1 - upsilon) / upsilon)) *
              (1 + ((eps_high / l_tilde) ** upsilon) *
              ((1 - ((eps_high / l_tilde) ** upsilon)) ** (-1))))
        d1 = ((b_ellip / l_tilde) * ((eps_high / l_tilde) **
              (upsilon - 1)) *
              ((1 - ((eps_high / l_tilde) ** upsilon)) **
              ((1 - upsilon) / upsilon)) - (2 * d2 * eps_high))
        MDU_n[nvec_high] = 2 * d2 * nvec[nvec_high] + d1

    if graph:
        '''
        ----------------------------------------------------------------
        cur_path    = string, path name of current directory
        output_fldr = string, folder in current path to save files
        output_dir  = string, total path of images folder
        output_path = string, path of file name of figure to be saved
        nvec_ellip  = (1000,) vector, support of n including values
                      between 0 and eps_low and between eps_high and
                      l_tilde
        MU_CRRA     = (1000,) vector, CRRA marginal utility of
                      consumption
        cvec_stitch = (500,) vector, stitched support of consumption
                      including negative values up to epsilon
        MU_stitch   = (500,) vector, stitched marginal utility of
                      consumption
        ----------------------------------------------------------------
        '''
        # Create directory if images directory does not already exist
        cur_path = os.path.split(os.path.abspath(__file__))[0]
        output_fldr = "images"
        output_dir = os.path.join(cur_path, output_fldr)
        if not os.access(output_dir, os.F_OK):
            os.makedirs(output_dir)

        # Plot steady-state consumption and savings distributions
        nvec_ellip = np.linspace(eps_low / 2, eps_high +
                                 ((l_tilde - eps_high) / 5), 1000)
        MDU_ellip = (
            (b_ellip / l_tilde) *
            ((nvec_ellip / l_tilde) ** (upsilon - 1)) *
            ((1 - ((nvec_ellip / l_tilde) ** upsilon)) **
             ((1 - upsilon) / upsilon)))
        n_stitch_low = np.linspace(-0.05, eps_low, 500)
        MDU_stitch_low = 2 * b2 * n_stitch_low + b1
        n_stitch_high = np.linspace(eps_high, l_tilde + 0.000005, 500)
        MDU_stitch_high = 2 * d2 * n_stitch_high + d1
        fig, ax = plt.subplots()
        plt.plot(nvec_ellip, MDU_ellip, ls='solid', color='black',
                 label='$v\'(n)$: Elliptical')
        plt.plot(n_stitch_low, MDU_stitch_low, ls='dashed', color='red',
                 label='$g\'(n)$: low stitched')
        plt.plot(n_stitch_high, MDU_stitch_high, ls='dotted',
                 color='blue', label='$g\'(n)$: high stitched')
        # for the minor ticks, use no labels; default NullFormatter
        minorLocator = MultipleLocator(1)
        ax.xaxis.set_minor_locator(minorLocator)
        plt.grid(b=True, which='major', color='0.65', linestyle='-')
        plt.title('Marginal utility of consumption with stitched ' +
                  'function', fontsize=14)
        plt.xlabel(r'Labor $n$')
        plt.ylabel(r'Marginal disutility $v\'(n)$')
        plt.xlim((-0.05, l_tilde + 0.01))
        # plt.ylim((-1.0, 1.15 * (b_ss.max())))
        plt.legend(loc='upper left')
        output_path = os.path.join(output_dir, "MDU_n_stitched")
        plt.savefig(output_path)
        # plt.show()

    return MDU_n


def get_n_errors(nvec, *args):
    '''
    --------------------------------------------------------------------
    Generates vector of static Euler errors that characterize the
    optimal lifetime labor supply decision. Because this function is
    used for solving for lifetime decisions in both the steady-state and
    in the transition path, lifetimes will be of varying length.
    Lifetimes in the steady-state will be S periods. Lifetimes in the
    transition path will be p in [2, S] periods
    --------------------------------------------------------------------
    INPUTS:
    nvec = (p,) vector, distribution of labor supply by age n_p
    args = either length 8 tuple or length 10 tuple, is (w, e, sigma,
           l_tilde, chi_n_vec, b_ellip, upsilon, diff, cvec) in most
           cases. In the time path for the age-S individuals in period
           1, the tuple is (wpath, sigma, l_tilde, chi_n_vec, b_ellip,
           upsilon, diff, rpath, b_s_vec, b_sp1_vec)

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:
        MU_c_stitch()
        MDU_n_stitch()

    OBJECTS CREATED WITHIN FUNCTION:
    w           = scalar > 0 or (p,) vector, steady-state wage or time
                  path of wage
    e           = scalar or (p,) vector, current labor productivity or time
                  path of labor productivity over remaining life periods
    sigma       = scalar > 0, coefficient of relative risk aversion
    l_tilde     = scalar > 0, time endowment of each agent in each per
    chi_n_vec   = (p,) vector, values for chi^n_p
    b_ellip     = scalar > 0, fitted value of b for elliptical
                  disutility of labor
    upsilon     = scalar > 1, fitted value of upsilon for elliptical
                  disutility of labo
    diff        = Boolean, =True if use simple difference Euler errors.
                  Use percent difference errors otherwise
    cvec        = (p,) vector, distribution of consumption by age c_p
    mu_c        = (p,) vector, marginal utility of consumption
    mdun_params = length 3 tuple, (l_tilde, b_ellip, upsilon)
    mdu_n       = (p,) vector, marginal disutility of labor supply
    n_errors    = (p,) vector, Euler errors characterizing optimal labor
                  supply nvec

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: n_errors
    --------------------------------------------------------------------
    '''
    if len(args) == 9:
        # Steady-state, and almost all of TPI solutions pass in cvec.
        # args is length 8
        (wpath, sigma, e, l_tilde, chi_n_vec, b_ellip, upsilon, diff,
            cvec) = args

    else:
        # solving for n_{S,1} in TPI does not pass in cvec, but passes
        # in rpath, b_s_vec, and b_sp1_vec instead. args is length 10
        (wpath, sigma, e, l_tilde, chi_n_vec, b_ellip, upsilon, diff,
            rpath, b_s_vec, b_sp1_vec) = args
        cvec = get_cons(rpath, wpath, b_s_vec, b_sp1_vec, nvec, e)

    mu_c = MU_c_stitch(cvec, sigma)
    mdun_params = (l_tilde, b_ellip, upsilon)
    mdu_n = MDU_n_stitch(nvec, mdun_params)
    if diff:
        n_errors = (wpath * e * mu_c) - chi_n_vec * mdu_n
    else:
        n_errors = ((wpath * e * mu_c) / (chi_n_vec * mdu_n)) - 1

    return n_errors


def get_b_errors(cvec, *args):
    '''
    --------------------------------------------------------------------
    Generates vector of dynamic Euler errors that characterize the
    optimal lifetime savings decision. Because this function is used for
    solving for lifetime decisions in both the steady-state and in the
    transition path, lifetimes will be of varying length. Lifetimes in
    the steady-state will be S periods. Lifetimes in the transition path
    will be p in [2, S] periods
    --------------------------------------------------------------------
    INPUTS:
    cvec = (p,) vector, distribution of consumption by age c_p
    args = length 3 tuple, (beta, sigma, diff)

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:
        MU_c_stitch()

    OBJECTS CREATED WITHIN FUNCTION:
    r        = scalar > 0 or (p-1,) vector, steady-state interest rate or
               time path of interest rates
    beta     = scalar in (0,1), discount factor
    sigma    = scalar > 0, coefficient of relative risk aversion
    diff     = boolean, =True if use simple difference Euler errors. Use
               percent difference errors otherwise.
    mu_c     = (p-1,) vector, marginal utility of current consumption
    mu_cp1   = (p-1,) vector, marginal utility of next period consumpt'n
    b_errors = (p-1,) vector, Euler errors characterizing optimal
               savings bvec

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: b_errors
    --------------------------------------------------------------------
    '''
    (r, beta, sigma, diff) = args
    mu_c = MU_c_stitch(cvec[:-1], sigma)
    mu_cp1 = MU_c_stitch(cvec[1:], sigma)

    if diff:
        b_errors = (beta * (1 + r) * mu_cp1) - mu_c
    else:
        b_errors = ((beta * (1 + r) * mu_cp1) / mu_c) - 1

    return b_errors


def bn_errors(bn_vec, *args):
    '''
    --------------------------------------------------------------------
    Computes labor supply and savings Euler errors for given b_{s+1} and
    n_s vectors and given the path of interest rates and wages
    --------------------------------------------------------------------
    INPUTS:
    bn_vec = (2p-1,) vector, values for remaining life n_s and b_{s+1}
    args   = length 11 tuple, (rpath, wpath, b_init, p, beta, sigma, e,
             l_tilde, chi_n_vec, b_ellip, upsilon, diff)

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:
        get_cons()
        get_n_errors()
        get_b_errors()

    OBJECTS CREATED WITHIN FUNCTION:
    rpath     = (p,) vector, time path of interest rates over remaining
                lifetime
    wpath     = (p,) vector, time path of wages over remaining lifetime
    b_init    = scalar, initial wealth
    p         = integer >= 1, number of periods remaining in lifetime
    beta      = scalar in (0,1), discount factor
    sigma     = scalar > 0, coefficient of relative risk aversion
    e         = scalar or (p,) vector, current labor productivity or
                time path of labor productivity over remaining life
                periods
    l_tilde   = scalar > 0, per-period time endowment for every agent
    chi_n_vec = (p,) vector, values for chi^n_s for remaining lifetime
    b_ellip   = scalar > 0, fitted value of b for elliptical disutility
                of labor
    upsilon   = scalar > 1, fitted value of upsilon for elliptical
                disutility of labor
    b_sp1_vec = (p-1,) vector, savings over remaining lifetime
    n_vec     = (p,) vector, labor supply over remaining lifetime
    b_s_vec   = (p-1,) vector, wealth over remaining lifetime
    n_args    = length 8 tuple, args to pass into hh.get_n_errors()
    n_errors  = (p,) vector, remaining lifetime labor supply Euler
                errors
    b_args    = length 3 tuple, args to pass into hh.get_b_errors()
    b_errors  = (p-1,) vector, remaining lifetime savings Euler errors
    bn_errors = (2p-1,) vector, remaining lifetime savings and labor
                supply Euler errors

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: bn_errors
    --------------------------------------------------------------------
    '''
    (rpath, wpath, b_init, p, beta, sigma, e, l_tilde, chi_n_vec,
     b_ellip, upsilon, diff) = args
    b_sp1_vec = np.append(bn_vec[:p - 1], 0.0)
    n_vec = bn_vec[p - 1:]
    b_s_vec = np.append(b_init, b_sp1_vec[:-1])
    c_vec = get_cons(rpath, wpath, b_s_vec, b_sp1_vec, n_vec, e)
    n_args = (wpath, sigma, e, l_tilde, chi_n_vec, b_ellip, upsilon,
              diff, c_vec)
    n_errors = get_n_errors(n_vec, *n_args)
    b_args = (rpath[1:p], beta, sigma, diff)
    b_errors = get_b_errors(c_vec, *b_args)
    bn_errors = np.hstack((b_errors, n_errors))

    return bn_errors


def get_cnb_vecs(c_init, rpath, wpath, args):
    '''
    --------------------------------------------------------------------
    Generate lifetime consumption vector for individual given a guess
    for initial consumption c_{S-p+1}, initial wealth b_{S-p+1}, a path
    for interest rates, wages, and parameters beta and sigma using
    household first order equations

    c_{s+1,t+1} = c_{s,t} * ([beta * (1 + r_{t+1})] ** (1 / sigma))

    w_t * (c_{s,t} ** (-sigma)) = chi_n_s * g'(n_{s,t})
    --------------------------------------------------------------------
    INPUTS:
    c_init = scalar > 0, consumption in initial period of lifetime c_{S-p+1}
    rpath  = (p,) vector, path of interest rates over lifetime
    wpath  = (p,) vector, path of wages over lifetime
    args   = length 8 tuple, (b_init, beta, sigma, l_tilde, b_ellip,
             upsilon, chi_n_vec, diff)

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:
        get_n_errors()
        get_b_errors()

    OBJECTS CREATED WITHIN FUNCTION:
    b_init    = scalar, initial wealth b_{S-p+1}
    beta      = scalar in (0, 1), discount factor
    sigma     = scalar >= 1, coefficient of relative risk aversion
    e         = scalar or (p,) vector, current labor productivity or
                time path of labor productivity over remaining life
                periods
    l_tilde   = scalar > 0, per-period time endowment for every agent
    b_ellip   = scalar > 0, fitted value of b for elliptical disutility
                of labor
    upsilon   = scalar > 1, fitted value of upsilon for elliptical
                disutility of labor
    chi_n_vec = (p,) vector, values for chi^n_s over remaining lifetime
    diff      = boolean, =True if simple difference Euler error,
                otherwise percent deviation Euler error
    p         = integer >= 1, number of periods remaining in a
                household's life
    cvec      = (p,) vector, household lifetime consumption given c1
    nvec      = (p,) vector, household lifetime labor supply given c1
    bvec      = (p,) vector, household lifetime savings given c_{S-p+1}
                and b_{S-p+1} where b1=0
    per       = integer >= 1, index of period number
    n_options = length 1 dict, options for opt.root(get_n_s,...)
    n_args    = length 8 tuple, (c_s, w_t, sigma, l_tilde, chi_n_s,
                b_ellip, upsilon, diff)
    result_n  = results object, solution from opt.root(get_n_s,...)
    n_errors  = (p,) vector, labor supply Euler errors
    b_args    = length 3 tuple, (beta, sigma, diff)
    b_errors  = (p-1,) vector, savings Euler errors
    b_Sp1     = scalar, savings after the last period of life. Should be
                zero in equilibrium

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: cvec, nvec, bvec, b_Sp1, n_errors, b_errors
    --------------------------------------------------------------------
    '''
    (b_init, beta, sigma, e, l_tilde, b_ellip, upsilon, chi_n_vec,
        diff) = args
    p = rpath.shape[0]
    cvec = np.zeros(p)
    nvec = np.zeros(p)
    bvec = np.zeros(p)
    for per in range(p):
        if per == 0:
            bvec[per] = b_init
            cvec[per] = c_init
        else:
            bvec[per] = ((1 + rpath[per - 1]) * bvec[per - 1] +
                         wpath[per - 1] * e[per - 1] * nvec[per - 1] -
                         cvec[per - 1])
            cvec[per] = cvec[per - 1] * ((beta * (1 + rpath[per])) **
                                         (1 / sigma))
        n_options = {'maxiter': 500}
        n_args = (wpath[per], sigma, e[per], l_tilde, chi_n_vec[per],
                  b_ellip, upsilon, diff, cvec[per])
        result_n = \
            opt.root(get_n_errors, l_tilde / 2, args=(n_args),
                     method='lm', tol=1e-14, options=(n_options))
        nvec[per] = result_n.x
    n_args = (wpath, sigma, e, l_tilde, chi_n_vec, b_ellip, upsilon,
              diff, cvec)
    n_errors = get_n_errors(nvec, *n_args)
    b_args = (beta, sigma, diff)
    b_errors = get_b_errors(cvec, rpath[1:], b_args)
    b_Sp1 = ((1 + rpath[-1]) * bvec[-1] + wpath[-1] * e[-1] * nvec[-1]
             - cvec[-1])

    return cvec, nvec, bvec, b_Sp1, n_errors, b_errors


def c1_bSp1err(c1_init, *args):
    '''
    --------------------------------------------------------------------
    Given value for c1, as well as w and r, solve for household
    lifetime decisions c_{s,t}, n_{s,t}, and b_{s+1,t+1}, and return
    implied savings for period after last period of life b_{S+1}. This
    savings amount b_{S+1} should be zero in equilibrium.
    --------------------------------------------------------------------
    INPUTS:
    c1_init = scalar > 0, assumed initial period consumption for
              individual
    args    = length 10 tuple, (b_init, beta, sigma, l_tilde, b_ellip,
              upsilon, chi_n_vec, rpath, wpath, diff)

    OTHER FUNCTIONS AND FILES CALLED BY THIS FUNCTION:
        get_cnb_vecs()

    OBJECTS CREATED WITHIN FUNCTION:
    b_init    = scalar, initial period wealth
    beta      = scalar in (0, 1), discount factor
    sigma     = scalar >= 1, coefficient of relative risk aversion
    b_ellip   = scalar > 0, fitted value of b for elliptical disutility
                of labor
    e         = scalar or (p,) vector, current labor productivity or
                time path of labor productivity over remaining life
                periods
    l_tilde   = scalar > 0, per-period time endowment for every agent
    upsilon   = scalar > 1, fitted value of upsilon for elliptical
                disutility of labor
    chi_n_vec = (p,) vector, values for chi^n_s for remaining lifetime
    rpath     = (p,) vector, path of interest rates over remaining life
    wpath     = (p,) vector, path of wages over remaining lifetime
    diff      = boolean, =True if simple difference Euler errors,
                otherwise percent deviation Euler errors
    cnb_args  = length 8 tuple, args to pass into get_cnb_vecs()
    cvec      = (p,) vector, household lifetime consumption given c1
    nvec      = (p,) vector, household lifetime labor supply given c1
    bvec      = (p,) vector, household lifetime savings given c1
                (b_{S-p+1}, b_{S-p+2}, ...bS) where b1=0
    b_Sp1     = scalar, residual amount left for individual savings in
                period after last period of life based on c_{S-p+1},
                Euler equations, and budget constraints. b_Sp1 should be
                zero in equilibrium
    n_errors  = (p,) vector, remaining lifetime labor supply Euler
                errors
    b_errors  = (p-1,) vector, remaining lifetime savings Euler errors

    FILES CREATED BY THIS FUNCTION: None

    RETURNS: b_Sp1
    --------------------------------------------------------------------
    '''
    (b_init, beta, sigma, e, l_tilde, b_ellip, upsilon, chi_n_vec, rpath,
        wpath, diff) = args
    cnb_args = (b_init, beta, sigma, e, l_tilde, b_ellip, upsilon,
                chi_n_vec, diff)
    cvec, nvec, bvec, b_Sp1, n_errors, b_errors = \
        get_cnb_vecs(c1_init, rpath, wpath, cnb_args)

    return b_Sp1
