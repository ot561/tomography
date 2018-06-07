#############################################################
# Title: Quantum state simulation
#
# Date created: 7th June 2018
#
# Language:    Python 3
#
# Overview:    
#
# Details:
#
# Usage: to be imported
#
#############################################################

import numpy as np
from scipy.stats import unitary_group as ug
from input import *

def density(dp):
    x = np.random.uniform(0,1) # Generate x
    print("The value of x is: ", x, "\n")
    realMat = np.random.random((2,2))
    U = ug.rvs(2) # Random unitary 
    print("The random unitary is: \n")
    print(U,"\n")
    # Check that U is actually unitary
    U_dag = np.matrix.getH(U)
    test = np.matmul(U_dag,U)
    print("Check that U * U^+ = I: \n")
    print(np.around(test,dp),"\n")
    # Compute the density matrix
    diag = np.matrix([[x,0],[0,1-x]])
    dens = U * diag * U_dag
    print("The density matrix is:\n\n", dens,"\n")
    # Check the density matrix
    print("The trace of the density matrix is:", np.around(np.trace(dens),dp))
    print("The eigenvalues are:", np.around(np.linalg.eig(dens)[0],dp), "which should both be positive.")
    return dens

def simulate(dens,meas,dp):
    yes_or_no("Is it correct")
    print("The measurements are X, Y and Z:\n\n",meas[0],"\n\n",meas[1],"\n\n and \n\n",meas[2],".\n")
    print("X is",meas[0])
    eigenvalues =  np.zeros(3,dtype=complex).tolist()
    eigenvectors = np.zeros(3,dtype=complex).tolist()
    # Compute the eigenvectors and eigenvalues of X, Y and Z
    for n in range(3):
        eigenvalues[n], eigenvectors[n] = np.linalg.eig(np.asmatrix(meas[n]))
        # The eigenvectors should be real
        print("The eigenvectors of X are\n\n", eigenvectors[n],"\n")
        print("And the eigenvalues of X are:", eigenvalues[n])
        # Python stores the eigenvectors as the columns of a matrix, so
        # a corresponding eigenvalue-eigenvector pair is accessed
        # like X_values[n], X_vectors[:,n] where n is 0 or 1.

    # Compute the projectors for X, Y and Z:
    proj = np.zeros((3,2),dtype=complex).tolist()
    p = proj
    for n in range(3):
        for m in range(2):
            proj[n][m] = eigenvectors[n][:,m] * np.matrix.getH(eigenvectors[n][:,m])    
            p[n][m] = np.trace(dens * proj[n][m]).real
            print("The probability of",n,m," are:", np.around(p[n][m],dp))

    # Generate the measurement data
    prob =  np.zeros(3,dtype=complex).tolist()
    meas = prob
    # User input: select number of measurements
    samples = get_user_int("Choose the number of measurements in each basis:")
    for n in range(3):
        meas[n] = np.random.choice(eigenvalues[n], samples, p=p[n]);

    return meas[0], meas[1], meas[2]
