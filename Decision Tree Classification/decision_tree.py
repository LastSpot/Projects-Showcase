import csv
import random
import math

def read_data(csv_path):
    """Read in the training data from a csv file.
    
    The examples are returned as a list of Python dictionaries, with column names as keys.
    """
    examples = []
    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for example in csv_reader:
            for k, v in example.items():
                if v == '':
                    example[k] = None
                else:
                    try:
                        example[k] = float(v)
                    except ValueError:
                         example[k] = v
            examples.append(example)
    return examples


def train_test_split(examples, test_perc):
    """Randomly data set (a list of examples) into a training and test set."""
    test_size = round(test_perc*len(examples))    
    shuffled = random.sample(examples, len(examples))
    return shuffled[test_size:], shuffled[:test_size]


class TreeNodeInterface():
    """Simple "interface" to ensure both types of tree nodes must have a classify() method."""
    def classify(self, example): 
        raise NotImplementedError


class DecisionNode(TreeNodeInterface):
    """Class representing an internal node of a decision tree."""

    def __init__(self, test_attr_name, test_attr_threshold, child_lt, child_ge, miss_lt):
        """Constructor for the decision node.  Assumes attribute values are continuous.

        Args:
            test_attr_name: column name of the attribute being used to split data
            test_attr_threshold: value used for splitting
            child_lt: DecisionNode or LeafNode representing examples with test_attr_name
                values that are less than test_attr_threshold
            child_ge: DecisionNode or LeafNode representing examples with test_attr_name
                values that are greater than or equal to test_attr_threshold
            miss_lt: True if nodes with a missing value for the test attribute should be 
                handled by child_lt, False for child_ge                 
        """    
        self.test_attr_name = test_attr_name  
        self.test_attr_threshold = test_attr_threshold 
        self.child_ge = child_ge
        self.child_lt = child_lt
        self.miss_lt = miss_lt

    def classify(self, example):
        """Classify an example based on its test attribute value.
        
        Args:
            example: a dictionary { attr name -> value } representing a data instance

        Returns: a class label and probability as tuple
        """
        test_val = example[self.test_attr_name]
        if test_val is None:
            child_miss = self.child_lt if self.miss_lt else self.child_ge
            return child_miss.classify(example)
        elif test_val < self.test_attr_threshold:
            return self.child_lt.classify(example)
        else:
            return self.child_ge.classify(example)

    def __str__(self):
        return "test: {} < {:.4f}".format(self.test_attr_name, self.test_attr_threshold) 


class LeafNode(TreeNodeInterface):
    """Class representing a leaf node of a decision tree.  Holds the predicted class."""

    def __init__(self, pred_class, pred_class_count, total_count):
        """Constructor for the leaf node.

        Args:
            pred_class: class label for the majority class that this leaf represents
            pred_class_count: number of training instances represented by this leaf node
            total_count: the total number of training instances used to build the leaf node
        """    
        self.pred_class = pred_class
        self.pred_class_count = pred_class_count
        self.total_count = total_count
        self.prob = pred_class_count / total_count  # probability of having the class label

    def classify(self, example):
        """Classify an example.
        
        Args:
            example: a dictionary { attr name -> value } representing a data instance

        Returns: a class label and probability as tuple as stored in this leaf node.  This will be
            the same for all examples!
        """
        return self.pred_class, self.prob

    def __str__(self):
        return "leaf {} {}/{}={:.2f}".format(self.pred_class, self.pred_class_count, 
                                             self.total_count, self.prob)


class DecisionTree:
    """Class representing a decision tree model."""

    def __init__(self, examples, id_name, class_name, min_leaf_count = 1):
        """Constructor for the decision tree model.  Calls learn_tree().

        Args:
            examples: training data to use for tree learning, as a list of dictionaries
            id_name: the name of an identifier attribute (ignored by learn_tree() function)
            class_name: the name of the class label attribute (assumed categorical)
            min_leaf_count: the minimum number of training examples represented at a leaf node
        """
        self.id_name = id_name
        self.class_name = class_name
        self.min_leaf_count = min_leaf_count

        # build the tree!
        self.root = self.learn_tree(examples)

    def get_prob(self, examples, class_label):

        total = len(examples)
        if total == 0:
            return 0, 0

        first_label = 0
        second_label = 0

        for example in examples:
            if example.get(self.class_name) == class_label[0]:
                first_label += 1
            else:
                second_label += 1

        first_label /= total
        second_label /= total
        
        return first_label, second_label

    def entropy(self, examples, class_label):
        set_entropy = self.get_prob(examples, class_label)

        if set_entropy[0] == 0 or set_entropy[1] == 0:
            return 0.0

        return -1.0 * (set_entropy[0] * math.log(set_entropy[0], 2) + set_entropy[1] * math.log(set_entropy[1], 2))
    
    def info_gain(self, parent_entropy, left_prob, right_prob, left_entropy, right_entropy):
        return parent_entropy - (left_prob * left_entropy + right_prob * right_entropy)

    def find_best_split(self, examples, attributes, class_label):
        entropy_parent = self.entropy(examples, class_label)
        value_split = None
        attribute_split = None
        left_examples = []
        right_examples = []
        max_info = 0

        for attribute in attributes:

            threshold = []

            for example in examples:
                if example.get(attribute) not in threshold and example.get(attribute) != None:
                    threshold.append(example.get(attribute))

            for value in threshold:

                left = []
                right = []

                for example in examples:
                    if example.get(attribute) == None:
                        continue
                    elif example.get(attribute) >= value:
                        right.append(example)
                    elif example.get(attribute) < value:
                        left.append(example)

                left_entropy = self.entropy(left, class_label)
                right_entropy = self.entropy(right, class_label)
                total_len = len(left) + len(right)
                left_prob = len(left) / total_len
                right_prob = len(right) / total_len

                info = self.info_gain(entropy_parent, left_prob, right_prob, left_entropy, right_entropy)

                if info > max_info and len(left) >= self.min_leaf_count and len(right) >= self.min_leaf_count:
                    max_info = info
                    value_split = value
                    attribute_split = attribute
                    left_examples = left
                    right_examples = right 

        if attribute_split != None:
            attributes.remove(attribute_split)              

        return attribute_split, value_split, left_examples, right_examples

    def learn_tree(self, examples):
        """Build the decision tree based on entropy and information gain.
        
        Args:
            examples: training data to use for tree learning, as a list of dictionaries.  The
                attribute stored in self.id_name is ignored, and self.class_name is consided
                the class label.
        
        Returns: a DecisionNode or LeafNode representing the tree
        """
        #
        # fill in the function body here!
        #
        attributes = []
        for key in examples[0].keys():
            attributes.append(key)

        attributes.remove(self.id_name)
        attributes.remove(self.class_name)
    
        class_label = []
        for example in examples:
            if example.get(self.class_name) not in class_label:
                class_label.append(example.get(self.class_name))

        return self.learn(examples, attributes, class_label) # fix this line!
    
    def learn(self, examples, attributes, class_label):

        example_prob = self.get_prob(examples, class_label)
        find_split = self.find_best_split(examples, attributes, class_label)

        if find_split[0] == None or example_prob[0] == 1.0 or example_prob[1] == 1.0:

            total_count = len(examples)
            class_name = None
            class_count = None

            if example_prob[0] > example_prob[1]:
                class_name = class_label[0]
                class_count = example_prob[0] * total_count
            else:
                class_name = class_label[1]
                class_count = example_prob[1] * total_count

            return LeafNode(class_name, class_count, total_count)
        
        miss = None
        child_left = self.learn(find_split[2], attributes, class_label)
        child_right = self.learn(find_split[3], attributes, class_label)
        if len(find_split[2]) > len(find_split[3]):
            miss = True
        else:
            miss = False

        return DecisionNode(find_split[0], find_split[1], child_left, child_right, miss)
    
    def classify(self, example):
        """Perform inference on a single example.

        Args:
            example: the instance being classified

        Returns: a tuple containing a class label and a probability
        """
        #
        # fill in the function body here!
        #
        return self.root.classify(example) # fix this line!

    def __str__(self):
        """String representation of tree, calls _ascii_tree()."""
        ln_bef, ln, ln_aft = self._ascii_tree(self.root)
        return "\n".join(ln_bef + [ln] + ln_aft)

    def _ascii_tree(self, node):
        """Super high-tech tree-printing ascii-art madness."""
        indent = 6  # adjust this to decrease or increase width of output 
        if type(node) == LeafNode:
            return [""], "leaf {} {}/{}={:.2f}".format(node.pred_class, node.pred_class_count, node.total_count, node.prob), [""]  
        else:
            child_ln_bef, child_ln, child_ln_aft = self._ascii_tree(node.child_ge)
            lines_before = [ " "*indent*2 + " " + " "*indent + line for line in child_ln_bef ]            
            lines_before.append(" "*indent*2 + u'\u250c' + " >={}----".format(node.test_attr_threshold) + child_ln)
            lines_before.extend([ " "*indent*2 + "|" + " "*indent + line for line in child_ln_aft ])

            line_mid = node.test_attr_name
            
            child_ln_bef, child_ln, child_ln_aft = self._ascii_tree(node.child_lt)
            lines_after = [ " "*indent*2 + "|" + " "*indent + line for line in child_ln_bef ]
            lines_after.append(" "*indent*2 + u'\u2514' + "- <{}----".format(node.test_attr_threshold) + child_ln)
            lines_after.extend([ " "*indent*2 + " " + " "*indent + line for line in child_ln_aft ])

            return lines_before, line_mid, lines_after


def test_model(model, test_examples):
    """Test the tree on the test set and see how we did."""
    correct = 0
    test_act_pred = {}
    for example in test_examples:
        actual = example[model.class_name]
        pred, prob = model.classify(example)
        print("{:30} pred {:15} ({:.2f}), actual {:15} {}".format(example[model.id_name] + ':', 
                                                            "'" + pred + "'", prob, 
                                                            "'" + actual + "'",
                                                            '*' if pred == actual else ''))
        if pred == actual:
            correct += 1
        test_act_pred[(actual, pred)] = test_act_pred.get((actual, pred), 0) + 1 

    acc = correct/len(test_examples)
    return acc, test_act_pred


def confusion2x2(labels, vals):
    """Create an normalized predicted vs. actual confusion matrix for four classes."""
    n = sum([ v for v in vals.values() ])
    abbr = [ "".join(w[0] for w in lab.split()) for lab in labels ]
    s =  ""
    s += " actual _________________  \n"
    for ab, labp in zip(abbr, labels):
        row = [ vals.get((labp, laba), 0)/n for laba in labels ]
        s += "       |        |        | \n"
        s += "  {:^4s} | {:5.2f}  | {:5.2f}  | \n".format(ab, *row)
        s += "       |________|________| \n"
    s += "          {:^4s}     {:^4s} \n".format(*abbr)
    s += "            predicted \n"
    return s



#############################################

if __name__ == '__main__':

    path_to_csv = 'mass_towns_2022.csv'
    id_attr_name = 'Town'
    class_attr_name = '2022_gov'

    min_examples = 10  # minimum number of examples for a leaf node

    # read in the data
    examples = read_data(path_to_csv)
    train_examples, test_examples = train_test_split(examples, 0.25)

    # learn a tree from the training set
    tree = DecisionTree(train_examples, id_attr_name, class_attr_name, min_examples)

    # test the tree on the test set and see how we did
    acc, test_act_pred = test_model(tree, test_examples)

    # print some stats
    print("\naccuracy: {:.2f}".format(acc))

    # visualize the results and tree in sweet, 8-bit text
    print(tree) 
    print(confusion2x2(["Healey", "Diehl"], test_act_pred))
