#############################################################
# Title: Quantum state simulation
#
# Date created: 7th June 2018
#
# Language: Python 3
#
# Overview: This file contains various functions for
#           generating simulated states and measurement
#           data. 
#
# Details:
#
# Usage: to be imported
#
#############################################################

import numpy as np
from scipy.stats import unitary_group as ug
from input import *

# Function: density(dp)
#   Generate a density matrix. The functions
#   provides the user with the option to 
#   enter the matrix manually, or it generates
#   the matrix at random. 
#
def density(dp):
    print("===== Density matrix generation =====\n")
    print("A density matrix is required to test")
    print("the state tomography proceedure. It")
    print("can be input manually or generated")
    print("randomly.")
    response = yes_or_no("Do you want to enter a density matrix manually? ")
    if response == 0:
        # Request matrix dimension
        while 1==1:
            dim = get_user_value("Specify the matrix dimension", "integer")
            if dim >= 2: 
                if bin(dim).count("1") == 1: break
                else: print("Matrix dimension should be power of 2")  
            else: print("Matrix dimension must be at least 2")
        # Populate matrix
        dens = np.asmatrix(np.zeros((dim,dim), dtype=complex))
        while 1==1:
            for m in np.ndindex((dim,dim)):
                dens[m] = get_user_value("Input element " + str(m), "complex")
            # Print and check the density matrix
            response = yes_or_no("Is this the correct density matrix?\n\n"+str(dens)+"\n\n")
            if response == 0: break
            else: print("Enter the density matrix again.")
    else: 
        # Generate a random matrix
        print("\nThe random density matrix will be generated")
        print("by generating random eignevalues x and 1-x")
        print("and then conjugating the resulting diagonal")
        print("matrix by a random unitary matrix U\n")
        x = np.random.uniform(0,1) # Generate x
        while 1==1:
            print("Picked random eigenvalues:\n\n\t ",x,",",1-x)
            realMat = np.random.random((2,2))
            U = np.asmatrix(ug.rvs(2)) # Random unitary 
            print("\nThe random matrix U is: \n")
            print(U,"\n")
            # Check that U is actually unitary
            U_dag = np.matrix.getH(U)
            if(U_dag * U - np.asmatrix([[1,0],[0,1]]) > 1e-5).any(): 
                print("Bug: failed to generate unitary matrix")
                print("Exiting")
                exit(1)
            #print("Check that U * U^+ = I: \n")
            #print(np.around(test,dp),"\n")
            # Compute the density matrix
            diag = np.matrix([[x,0],[0,1-x]])
            dens = U * diag * U_dag
            print("The density matrix is:\n\n", dens,"\n")
            # Check the density matrix
            print("The trace of the density matrix is", np.around(np.trace(dens),dp), "which should be 1.")
            print("The eigenvalues", np.around(np.linalg.eig(dens)[0],dp), "should both be positive.")
            response = yes_or_no("Does everything look OK? ")
            if response == 0: break
            elif yes_or_no("Try to generate density matrix again? ") == 0:
                print("Attempting to generate density matrix...")
            else: exit()
        return dens

def simulate(dens,meas_ops,dp):
    print("\n===== Generate measurement data =====\n")
    print("The X measurements are simulated by")
    print("computing the projectors P = |+><+| and ")
    print("P = |-><-| for each measurement outcome")
    print("and then computing the probability using")
    print("prob = tr(pP), where p is the density")
    print("matrix. Then samples are taken from")
    print("a discrete distribution defined by the")
    print("measurement probabilities. The process")
    print("is repeated for Y and Z.\n")
    eigenvalues = {} #np.zeros(3,dtype=complex).tolist()
    eigenvectors = {} #np.zeros(3,dtype=complex).tolist()
    # Compute the eigenvectors and eigenvalues of X, Y and Z
    for key in meas_ops:
        eigenvalues[key], eigenvectors[key] = np.linalg.eig(np.asmatrix(meas_ops[key]))

    # Compute the projectors for X, Y and Z:
    proj = {}#np.zeros((3,2),dtype=complex).tolist()
    p = {}#proj
    for key in meas_ops:
        proj[key] = ([eigenvectors[key][:,0] * np.matrix.getH(eigenvectors[key][:,0]),
                      eigenvectors[key][:,1] * np.matrix.getH(eigenvectors[key][:,1])])
        p[key] = ([np.trace(dens * proj[key][0]).real, np.trace(dens * proj[key][1]).real])
    print("Finished calculating the projectors.\n")
    for key in meas_ops:
        print("The probabilities associated with",key,"are:", np.around(p[key],dp))
        
    # Generate the measurement data
    meas_dat = {}
    # User input: select number of measurements
    samples = get_user_value("\nChoose the number of measurements in each basis","integer")
    for key in meas_ops:
        meas_dat[key] = np.random.choice(eigenvalues[key], samples, p=p[key]);

    return meas_dat
