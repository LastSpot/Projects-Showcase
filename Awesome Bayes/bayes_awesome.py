import random
from matplotlib import pyplot as plt


class BooleanVariableNode(object):
    """Class representing a single node in a Bayesian network.

    The conditional probability table (CPT) is stored as a dictionary, keyed by tuples of parent
    node values.
    """

    def __init__(self, var, parent_vars, cpt_entries):
        """Constuctor for node class.

        Args:
            var: string variable name
            parent_vars: a sequence of strings specifying the parent variable names
            cpt_entries: a dictionary specifying the CPT, keyed by a tuple of parent values, 
                with values specifying the prob that this variable=true
        """
        self.parents = parent_vars
        self.target = var
        self.cpt = cpt_entries  # (parent_val1, parent_val2, ...) => prob

    def get_parents(self):
        return self.parents
    
    def get_var(self):
        return self.target

    def get_prob_true(self, parent_vals):
        key = tuple(parent_vals)
        return self.cpt[key]

    def get_prob_false(self, parent_vals):
        return 1.0 - self.get_prob_true(parent_vals)


class SimpleSampler(object):
    """Sampler that generates samples with no evidence."""
    
    def __init__(self, nodes):
        self.nodes = nodes
    
    def generate_sample(self):
        """Create a single sample instance, returns a dictionary variable => value"""
        sample_vals = {}  # variable => value

        while len(sample_vals) < len(self.nodes):
            for node in self.nodes:
                var = node.get_var()
                if var not in sample_vals:  # we haven't generated a value for this var
                    parent_vars = node.get_parents()
                    if all([ p in sample_vals for p in parent_vars ]):  # all parent vals generated
                        parent_vals = tuple([ sample_vals[par] for par in parent_vars ])
                        prob_true = node.get_prob_true(parent_vals)
                        sample_vals[var] = random.random() < prob_true
        return sample_vals
        
    def get_prob(self, query_vals, num_samples):
        """Return the (joint) probability of the query variables.
        
        Args:
            query_vals: dictionary mapping variable => value 
            num_samples: number of simple samples to generate for the calculation

        Returns: empirical probability of query values
        """
        # 
        # Fill in the function body here
        #
        satisfy = 0

        if num_samples <= 0:
            return 0.0

        for i in range(0, num_samples):
            contain_condition = True
            sample = self.generate_sample()

            for key in query_vals.keys():
                for cond in sample:
                    if key == cond and query_vals.get(key) != sample.get(cond):
                        contain_condition = False

            if contain_condition:
                satisfy += 1

        return satisfy / num_samples  # Fix this line!

        
class RejectionSampler(SimpleSampler):
    """Sampler that generates samples given evidence using rejection sampling."""

    def get_prob(self, query_vals, evidence_vals, num_samples):
        """Return the conditional probability of the query variables, given evidence.
        
        Args:
            query_vals: dictionary mapping variable => value
            evidence_vals: dictionary mapping variable => value
            num_samples: number of simple samples to generate for the calculation (the number
                "kept" that agree with evidence will be significantly lower)

        Returns: empirical conditional probability of query values given evidence.  N.B.: if 
        all of the generated samples are rejected, it returns None.
        """
        # 
        # Fill in the function body here
        #
        satisfy = 0
        non_rejected = []

        for i in range(0, num_samples):
            sample = self.generate_sample()

            if evidence_vals != {}:
                contain_condition = True
                
                for cond in sample:
                    for key in evidence_vals.keys():

                        if key == cond and evidence_vals.get(key) != sample.get(cond):
                            contain_condition = False
                
                if contain_condition:
                    non_rejected.append(sample)
            
            else:
                non_rejected.append(sample)
        
        for element in non_rejected:
            contain_query = True

            for e in element:
                for key in query_vals:

                    if key == e and query_vals.get(key) != element.get(e):
                        contain_query = False

            if contain_query:
                satisfy += 1
        
        if len(non_rejected) == 0:
            return 0.0

        return satisfy / len(non_rejected)  # Fix this line!


class LikelihoodWeightingSampler(SimpleSampler):
    """Sampler that generates samples given evidence using likelihood weighting."""

    def generate_sample(self, evidence_vals):
        """Create a single sample instance that agrees with evidence.
        
        Returns a 2-tuple with a dictionary containing the sample (variable => value) and the 
        corresponding weight for that sample.
        """
        sample_vals = {}  # variable => value
        weight = 1.0

        while len(sample_vals) < len(self.nodes):    
            for node in self.nodes:
                var = node.get_var()
                if node not in sample_vals:
                    parent_vars = node.get_parents()
                    if all([ p in sample_vals for p in parent_vars ]):
                        parent_vals = tuple([ sample_vals[par] for par in parent_vars ])
                        if var in evidence_vals:  # if evidence, adjust the weight by the likelihood
                            val = evidence_vals[var]
                            sample_vals[var] = val
                            p = node.get_prob_true(parent_vals) if val else node.get_prob_false(parent_vals)
                            weight *= p
                        else:  # generate a value using the CPT
                            prob_true = node.get_prob_true(parent_vals)
                            sample_vals[var] = random.random() < prob_true
        return sample_vals, weight

    def get_prob(self, query_vals, evidence_vals, num_samples):
        """Return the conditional probability of the query variables, given evidence.
        
        Args:
            query_vals: dictionary mapping variable => value
            evidence_vals: dictionary mapping variable => value
            num_samples: number of weighted samples to generate for the calculation 

        Returns: empirical conditional probability of query values given evidence
        """
        # 
        # Fill in the function body here
        #
        satisfy_weight = 0
        total_weight = 0

        for i in range(0, num_samples):
            sample = self.generate_sample(evidence_vals)
            total_weight += sample[1]

            contain_query = True

            for cond in sample[0].keys():
                for key in query_vals.keys():

                    if key == cond and query_vals.get(key) != sample[0].get(cond):
                        contain_query = False

            if contain_query:
                satisfy_weight += sample[1]
        
        if total_weight == 0:
            return 0.0

        return satisfy_weight / total_weight  # Fix this line!


def compare_estimates(query, evidence, n, simp, rej, like):
    """Print out empirical estimations of posteriors using different samplers."""
    
    if not evidence:  # simple sampler can't handle evidence so skip if we have some
        print("simple:     {:.4f}".format(simp.get_prob(query, n)))
    print("rejection:  {:.4f}".format(rej.get_prob(query, evidence, n)))
    print("likelihood: {:.4f}\n".format(like.get_prob(query, evidence, n)))


def bayes_sample_size_plot(sampler1, sampler2, query, evidence, label1, label2, title, fname):
    """Create a plot comparing approximate value of a conditional probability for two samplers.

    Args:
        sampler1: first approximate sampler to compare
        sampler2: second approximate sampler to compare
        query: dict of form node => value for all query nodes
        evidence: dict of form node => value for all evidence nodes
        label1: plot label for first sampler
        label2: plot label for second sampler
        title: plot title
        fname: path of output pdf   
    """
    # 
    # Fill in the function body here
    #
    sample1 = []
    sample2 = []
    num_arr = []
    for i in range(50, 10000, 20):
        sample1.append(sampler1.get_prob(query, evidence, i))
        sample2.append(sampler2.get_prob(query, evidence, i))
        num_arr.append(i)

    return two_line_plot(num_arr, sample1, label1, num_arr, sample2, label2, title, fname)


def two_line_plot(xvals1, yvals1, label1, xvals2, yvals2, label2, title, outfile_path):
    plt.plot(xvals1, yvals1, label=label1, color='blue', marker=None, linestyle='solid', linewidth=0.75)
    plt.plot(xvals2, yvals2, label=label2, color='green', marker=None, linestyle='solid', linewidth=0.75)
    plt.title(title)
    plt.legend()
    plt.savefig(outfile_path)


##########################################
if __name__ == '__main__':

    # Palate, Moxie, Enrolled, Awesome Bayesian network
    #
    #    P   E  
    #    |  /|
    #    | / |
    #    vv  v
    #    M-->A
    #
    awesome_nodes = [
        BooleanVariableNode('P', (),        {(): 0.6}),
        BooleanVariableNode('E', (),        {(): 0.8}),
        BooleanVariableNode('M', ('P', 'E',), {(True, True): 0.7, 
                                             (True, False,): 0.5, 
                                             (False, True): 0.25,
                                             (False, False): 0.05}),
        BooleanVariableNode('A', ('M', 'E',), {(True, True): 0.9, 
                                             (True, False,): 0.75, 
                                             (False, True): 0.6,
                                             (False, False): 0.4}),
    ]

    sampler_simp = SimpleSampler(awesome_nodes)
    sampler_reject = RejectionSampler(awesome_nodes)
    sampler_like = LikelihoodWeightingSampler(awesome_nodes)

    n = 10000  # the number of samples to generate

    # Approximate some of the probabilities we've been thinking about
    print("Custom")
    compare_estimates({'M': False, 'E': False}, {}, n, sampler_simp, sampler_reject, sampler_like)

    print("a. P(enrolled)")
    compare_estimates({'E': True}, {}, n, sampler_simp, sampler_reject, sampler_like)

    print("b. P(moxie | -palate)")
    compare_estimates({'M': True}, {'P': False}, n, sampler_simp, sampler_reject, sampler_like)

    print("c. P(moxie)")
    compare_estimates({'M': True}, {}, n, sampler_simp, sampler_reject, sampler_like)
    
    print("d. P(moxie, awesome)")
    compare_estimates({'M': True, 'A': True}, {}, n, sampler_simp, sampler_reject, sampler_like)

    print("e. P(awesome)")
    compare_estimates({'A': True}, {}, n, sampler_simp, sampler_reject, sampler_like)

    print("f. P(-palate | moxie)")
    compare_estimates({'P': False}, {'M': True}, n, sampler_simp, sampler_reject, sampler_like)
    
    print("g. P(-palate | moxie, -enrolled)")
    compare_estimates({'P': False}, {'M': True, 'E': False}, n, sampler_simp, sampler_reject, sampler_like)


    # Create a plot illustrating how different samplers converge as a function of n
    bayes_sample_size_plot(sampler_reject, sampler_like, 
                           {'A': True}, {'P': False, 'E': False}, 
                           "rejection", "likelihood weighting", "P(awesome | -palate, -enroll) vs n", 
                           "bayes_awesome.pdf")
