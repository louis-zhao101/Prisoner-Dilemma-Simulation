from simulations_updated import *
from cleaning import *
from visualization import *
from analysis import *
import matplotlib.pyplot as plt
import numpy.polynomial.polynomial as poly
import time
import os 

def complexity_graph():
        # timer
        node_count = [i for i in range (500, 2500, 500)]
        time_elapsed = []

        for i in (node_count):
                start = time.time()
                
                num_nodes = i
                numIterations = 1
                
                # generate network
                nodes, adj = generate_random_network("BA", num_nodes, p=0.9)
                # nodes, adj = facebook_clean()

                
                # run simulation
                saveRate = 1

                simulation = Simulation(numIterations, saveRate, strategy= 2) # choose from 0, 1, 2
                
                nodes_list, adj_list = simulation(nodes, adj)


                # calculations
                # G = nx.convert_matrix.from_numpy_matrix(adj)
                # shortest = nx.average_shortest_path_length(G)
                # closeness = nx.closeness_centrality(G)
                # print("Closeness: " + str(sum(closeness.values())/len(adj)))
                
                # print("Clustering: " + str(nx.average_clustering(G)))

                end = time.time()
                elapsed = abs(end-start)
                time_elapsed.append(elapsed)
                print("Node count: {0}, Time Elapsed: {1} seconds".format(i, elapsed))            

        # convert to np array
        x = np.array(node_count)
        y = np.array(time_elapsed)    
        
        # plot with line of best fit
        #a, b, c = np.polyfit(node_count, time_elapsed, 2)
        plt.plot(x, y, 'o')
        #plt.plot(node_count, a*time_elapsed**2 + b*time_elapsed + c)
        coefs = poly.polyfit(x, y, 2)
        print("raw coefs: " + repr(coefs))

        x_new = np.linspace(x[0], x[-1], num=len(x)*10)
        ffit = poly.polyval(x_new, coefs)
        
        sig_figs = 7
        # formula = "{0}x^3 + {1}x^2 + {2}x + {3}".format(round(coefs[0],sig_figs), round(coefs[1],sig_figs), round(coefs[2], sig_figs), round(coefs[3], sig_figs))
        formula = "{0}x^2 + {1}x+ {2}".format(round(coefs[2],sig_figs), round(coefs[1],sig_figs), round(coefs[0], sig_figs))
        print("formatted formula: " + repr(formula))
        plt.plot(x_new, ffit, label=formula)
        
        # plt.text(0, 1,'matplotlib', horizontalalignment='center',
        #      verticalalignment='center'))
        plt.legend()
        plt.show()             
        plt.close()


def load_data(fileName):
        start = time.perf_counter()
        
        dir_path = os.path.dirname(os.path.realpath(__file__))   
        
        fd = open(f'{dir_path}/savedInfo/adjMat_{fileName}.pickle', 'rb')
        adj_list = pickle.load(fd)

        fd = open(f'{dir_path}/savedInfo/nodesDict_{fileName}.pickle', 'rb')
        nodes_list = pickle.load(fd)
        
        numIterations = len(nodes_list)-1       # -1 since it included the initial, uniterated graph as well
        
        print(f'time used to unpickle : {time.perf_counter()-start}s')
        
        return nodes_list, adj_list, numIterations


if __name__ == '__main__':
        start = time.perf_counter()


# USER INPUT PROCESSING

        model = str(input("Model (default: ER): ") or "ER")
        strat = int(input("Strat # (default: 3): ") or "3")

        if model == 'ER' or model =='WS' or model =='BA':
            num_nodes = int(input("Node # (default: 1000): ") or "1000")
            p = float(input("p (default: 0.1): ") or 0.1) if model == 'ER' or 'WS' else 0.1
        else:
            num_nodes = 200
            p = 0.1
        numIterations = int(input("Iteration # (default: 5): ",) or "5")
            
        k = 2
        payoff = 0 # int(input("Payoff # (default: 0): ") or "0")
        saveRate = 1
        m = 3
        
        
        ## generate filename
                
        if model == 'ER':
            fileName = '{}_n={}_p={}_strat{}_payoff{}_saveRate{}_numIter{}'.format(model, num_nodes, p, strat, payoff, saveRate, numIterations)
        elif model == 'WS':
            fileName = '{}_n={}_p={}_k={}_strat{}_payoff{}_saveRate{}_numIter{}'.format(model, num_nodes, p, k, strat, payoff, saveRate, numIterations)
        elif model == 'BA':
            fileName = '{}_n={}_m={}_strat{}_payoff{}_saveRate{}_numIter{}'.format(model, num_nodes, m, strat, payoff, saveRate, numIterations)
        else:
            fileName = '{}_strat{}_payoff{}_saveRate{}_numIter{}'.format(model, strat, payoff, saveRate, numIterations)
        
        
        dir_path = os.path.dirname(os.path.realpath(__file__))   
        file_path = "{}/{}/{}{}{}".format(dir_path, "savedInfo", "adjMat_", fileName, ".pickle")
        
        load_flag = 0
        if os.path.exists(file_path):
                load_flag = int(input("File exists, would you like to load? (1-yes, 0-no, default: 1): ") or "1")
                
        

# BEGIN SIMULATION

        # Step 1. generate network
        nodes, adj = generate_network(model, num_nodes, cooperator_proportion=0.5,  p = p, m =m, k =k, seed =100)
        # nodes, adj = facebook_clean()
        # nodes, adj = karate_clean()


        # Step 2. run simulation
        
        start = time.perf_counter()
        
        if load_flag:
            nodes_list, adj_list, numIterations = load_data(fileName)              # Load pickles to save time
        else:
            simulation = Simulation(numIterations, saveRate, strat, payoff, fileName)
            nodes_list, adj_list = simulation(nodes, adj)
            print(f'time used to simulate: {time.perf_counter()-start}s')
        
        # Step 3. run all measurements
        start = time.perf_counter()
        measures_list = all_measures_master(nodes_list, adj_list, "{0}+s{1}+p{2}".format(model, strat, payoff))
        community_detection_list = community_detection(nodes_list, adj_list)
        
        print(f'time used to calculate measures: {time.perf_counter()-start}s')
        
        
        # Step 4. Visualize
        
        # start = time.perf_counter()
        
        visualize(nodes_list, adj_list, measures_list, community_detection_list, numIterations, "{0}+s{1}+p{2}".format(model, strat, payoff), pos_lock=True)
         # 4th parameter (model name) is for bookkeeping purposes
         # 5th parameter (defaulted to True) means position is LOCKED for future iteration
         # choose False to recalculate the position of Nodes every iteration (which significantly slows down the process)
        
        
        # print(f'time used to visualize: {time.perf_counter()-start}s \n')

        # complexity_graph()