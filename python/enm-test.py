#############################################################
# Title: Testing extended norm minimisation
#
# Date created: 14th July 2018
#
# Language:    Cpp
#
# Overview:    The program tests the linear estimator
#              for a single qubit density matrix
#
# Details:     The script performs the following steps:
#
#              1) Set x in [0,1] as the purity parameter;
#                 pick a random unitary U; and compute
#
#
#                          -       -
#                         | x     0 |
#                 p = U * |         | * U^
#                         | 0   1-x |
#                          -       -
#
#                 The closer x is to 1 or 0, the more
#                 pure is the state.
#
#              2) Fix a set of measurement operators,
#                 and generate sample data from the
#                 distribution of outcomes implied by
#                 the state p.
#
#              3) Compute the density matrix using the
#                 linear estimator
#
#              4) Compute the distance between the
#                 estimate and the true density matrix
#                 for each of the different distances
#                 (operator norm, Hilbert-Schmidt norm,
#                 fidelity).
#
#              5) Perform averages of each distance at each
#                 value of x. Plot the average distances
#                 as a function of x for all the values of
#                 x.
#
#              6) Repeat steps 1-4 for different values
#                 of x and repeat each value of x a large
#                 number of times. Store all the distances.
#
# Usage: python3 enm-test.py
#
#############################################################

# Include
import importlib
import numpy as np
from scipy.stats import unitary_group as ug
import scipy as sc
import simulation
importlib.reload(simulation)
import estimation
importlib.reload(estimation)
import stats
importlib.reload(stats)
import matplotlib.pyplot as plt
import estimation
importlib.reload(estimation)
from matplotlib.offsetbox import AnchoredText
import cProfile
import pstats
from progress import *

pr = cProfile.Profile()
pr.enable()
# ======= Test parameter ===============================
M = 2000  # Number of purity parameters x to try
x_start = 0 # Specify purity parameter x range
x_end = 1
N = 500  # Number of random density matrices per x value
S = 500  # Number of samples of each measurement to
        # simulate for each density matrix 
# ======================================================

av_distances = np.zeros([M,3])
non_physical = np.zeros(M) # Proportion of non-physical estimates

# Preliminaries: compute the projectors

I = np.matrix([[1,0],[0,1]])
X = np.matrix([[0,1],[1,0]])
Y = np.matrix([[0,-1j],[1j,0]])
Z = np.matrix([[1,0],[0,-1]])

values_X, vectors_X = np.linalg.eig(X)
proj_X = np.zeros([2,2,2])
proj_X[0,:,:] = np.matmul(vectors_X[:,0], np.matrix.getH(vectors_X[:,0]))
proj_X[1,:,:] = np.matmul(vectors_X[:,1], np.matrix.getH(vectors_X[:,1]))

values_Y, vectors_Y = np.linalg.eig(Y)
proj_Y = np.zeros([2,2,2])
proj_Y[0,:,:] = np.matmul(vectors_Y[:,0], np.matrix.getH(vectors_Y[:,0]))
proj_Y[1,:,:] = np.matmul(vectors_Y[:,1], np.matrix.getH(vectors_Y[:,1]))

values_Z, vectors_Z = np.linalg.eig(Z)
proj_Z = np.zeros([2,2,2])
proj_Z[0,:,:] = np.matmul(vectors_Z[:,0], np.matrix.getH(vectors_Z[:,0]))
proj_Z[1,:,:] = np.matmul(vectors_Z[:,1], np.matrix.getH(vectors_Z[:,1]))

# Open a file for writing
file = open("enm_test_1.dat", "w")
file.write("Distances between estimated and original density matrices using various distances:\n\n")
file.write("PURITY, \tOPERATOR, \tTRACE, \t\tFIDELITY\n")

# Define x -- put a loop here ----------------------------------------- LOOP for x between 0 and 1
#
# This loop runs through different values of the purity parameter x,
# and tests the ability of the linear estimator in each case
#

dist_op = np.zeros([N,1])
dist_trace = np.zeros([N,1])
dist_fid = np.zeros([N,1])

dp = 5

#for k,n in itertools.product(range(M),range(N)):
for k in range(M):
    non_physical_count = 0 # Temporary counter for non-physical estimates
    
    # Loop N times for each value of x ------------------ inner loop -- N trials for each x
    #
    # This loop generates N random density matrices for each fixed value of x
    # which used to simulate measurement data and run the estimator
    #
    for n in range(N):
        # Step 1: Prepare the density matrix
        #
        # The purity parameter x is picked between 0
        # and 1.
        #
        # Note: any time a numerical check is performed
        # and printed out, I've rounded the result to
        # make it more readable. Set the decimal places
        # to keep using the dp variable.
        #
        x = x_start + k * (x_end - x_start)/M
        #pr.enable()
        dens = simulation.random_density(x)
        #values_dens,vectors_dens = np.linalg.eig(dens)
        #pr.disable()
        
        # Step 2: Generate measurement data
        #
        # Generate data for X, Y and Z measurements
        #
        #pr.enable()
        X_data = simulation.simulate(dens,proj_X,values_X,S)
        Y_data = simulation.simulate(dens,proj_Y,values_Y,S)
        Z_data = simulation.simulate(dens,proj_Z,values_Z,S)

        proj = np.concatenate((proj_X, proj_Y, proj_Z), axis=0)
        #print(proj)

        #print(result)
        #pr.disable()
        # Step 3: Estimate density matrix
        #
        # Compute linear estimator
        #
        # Then tr(pI) is computed by requiring that
        # the density matrix be normalised
        #
        dens_est = estimation.ENM.enm_XYZ(X_data, Y_data, Z_data)[0]
        
        # Step 4: Compute and the distances
        #
        # Compute distances between the estimated
        # and true density matrix using the
        # different distance fuctions.
        #
        dist_op[n] = stats.distance_op(dens, dens_est)
        dist_trace[n] = stats.distance_trace(dens, dens_est)
        #pr.enable()
        dist_fid[n] = stats.distance_fid(dens, dens_est)
        #dist_fid[n] = stats.distance_fid_2(values_dens,vectors_dens,dens_est)
        #pr.disable()
        # Count the number of non-physical matrices
        #
        eigenvalues = np.linalg.eigvals(dens_est)
        if eigenvalues[0] < 0 or eigenvalues[1] < 0:
            non_physical_count = non_physical_count + 1

        #p = (k*N+n)/(M*N)
        #show_progress(pr,p)
        
    # Step 5: Average the distances 
    #
    # Average the distances for each value of x
    #
    #print(eigenvalues[0])
    av_distances[k,:] = [np.mean(dist_op), np.mean(dist_trace), np.mean(dist_fid)]
    file.write("{0:.5f},\t{1:.5f},\t{2:.5f}, \t{3:.5f}\n".format(x, np.mean(dist_op),
                                                                   np.mean(dist_trace),
                                                                   np.mean(dist_fid)))
    non_physical[k] = non_physical_count/N
    p = (k+1)/M
    show_progress(pr,p)

file.close
    
pr.disable()
pr.create_stats()

ps = pstats.Stats(pr)
total_time = ps.total_tt
#pr.print_stats(sort='cumulative')

# Step 6: Process the data 
#
# Store in a file, plot, etc.
x_values = np.linspace(x_start, x_end, M)

fig, ax1 = plt.subplots()
ax1.set_xlabel('Purity parameter')
ax1.set_ylabel('Estimate error distance')
ax1.plot(x_values, av_distances[:,0], '.',color='tab:red', label='Operator distance')
ax1.plot(x_values, av_distances[:,1], '.',color='tab:green', label='Trace distance' )
ax1.plot(x_values, av_distances[:,2], '.',color='tab:blue', label='Fidelity')
ax1.legend(loc=3, ncol=1)

ax2=ax1.twinx()
ax2.set_ylabel('Probability')
ax2.plot(x_values,non_physical, '+', color='tab:brown',label='Non-physical')
atext = AnchoredText("Number of purity parameters: " + str(M) + "\n"
                     +"Density matrices: "+ str(N) + "\n"
                     +"Samples per measurement: " + str(S) + "\n"
                     +"Total running time:  " + str(np.around(total_time,3)) + "s",
                     loc=2)
ax2.add_artist(atext)
ax2.legend(loc=1)

fig.tight_layout()
plt.show()
