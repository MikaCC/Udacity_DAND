#!/usr/bin/python

import sys
import pickle
import matplotlib.pyplot
sys.path.append("../tools/")

from numpy import mean

from feature_format import featureFormat, targetFeatureSplit
from sklearn.feature_selection import SelectKBest
from sklearn import preprocessing
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.grid_search import GridSearchCV
from sklearn.cross_validation import train_test_split
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".

financial_features = ['salary', 'deferral_payments', 'total_payments', \
'loan_advances', 'bonus', 'restricted_stock_deferred', 'deferred_income', \
'total_stock_value', 'expenses', 'exercised_stock_options', 'other', \
'long_term_incentive', 'restricted_stock', 'director_fees']
 
email_features = ['to_messages', 'from_poi_to_this_person', 'from_messages', \
'from_this_person_to_poi', 'shared_receipt_with_poi']

poi_label = ['poi']
features_list = poi_label + email_features + financial_features

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "r") as data_file:
    data_dict = pickle.load(data_file)
    
#Total number of data points
print("Total number of data points: %i" %len(data_dict))

#Poi and Non-Poi
poi = 0
for person in data_dict:
    if data_dict[person]['poi'] == True:
       poi += 1
print("Number of poi: %i" % poi)
print("Number of non-poi: %i" % (len(data_dict) - poi))
       
# Number of features used ('total' was removed from dataset)
all_features = data_dict[data_dict.keys()[0]].keys()
print("There are %i features for each person in the dataset, and %i features \
are used" %(len(all_features), len(features_list)))

# NaN Values
missing_values = {}
for feature in all_features:
    missing_values[feature] = 0
##count NaN for each feature
for person in data_dict:
    for feature in data_dict[person]:
        if data_dict[person][feature] == "NaN":
            missing_values[feature] += 1
print("The number of missing values for each feature: ")
for feature in missing_values:
    print("%s: %i" %(feature, missing_values[feature]))
    
### Task 2: Remove outliers
def plotOutliers(data_set, feature_x, feature_y):
    #data_set:dictionary, feature_c: string, featue_y: string)

    data = featureFormat(data_set, [feature_x, feature_y])
    for point in data:
        x = point[0]
        y = point[1]
        matplotlib.pyplot.scatter( x, y )
    matplotlib.pyplot.xlabel(feature_x)
    matplotlib.pyplot.ylabel(feature_y)
    matplotlib.pyplot.show()
    
# Visualize data to identify outliers
print(plotOutliers(data_dict, 'total_payments', 'total_stock_value'))
print(plotOutliers(data_dict, 'from_poi_to_this_person', 'from_this_person_to_poi'))
print(plotOutliers(data_dict, 'salary', 'bonus'))
print(plotOutliers(data_dict, 'total_payments', 'other'))

#NaN Entries
identity = []
for person in data_dict:
    if data_dict[person]['total_payments'] != "NaN":
        identity.append((person, data_dict[person]['total_payments']))
print("Outlier:")
print(sorted(identity, key = lambda x: x[1], reverse=True)[0:4])

# Find persons whose financial features are "NaN"
fi_nan_dict = {}
for person in data_dict:
    fi_nan_dict[person] = 0
    for feature in financial_features:
        if data_dict[person][feature] == "NaN":
            fi_nan_dict[person] += 1
sorted(fi_nan_dict.items(), key=lambda x: x[1])

# Find persons whose email features are "NaN"
email_nan_dict = {}
for person in data_dict:
    email_nan_dict[person] = 0
    for feature in email_features:
        if data_dict[person][feature] == "NaN":
            email_nan_dict[person] += 1
sorted(email_nan_dict.items(), key=lambda x: x[1])

# Observe the intersection of the two lists above
# Remove outliers
data_dict.pop("TOTAL", 0)
data_dict.pop("THE TRAVEL AGENCY IN THE PARK", 0)
data_dict.pop("LOCKHART EUGENE E", 0)


### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.
### I created two new features 'fraction_to_poi' and 'fraction_from_poi' here
my_dataset = data_dict
for person in my_dataset:
    msg_from_poi = my_dataset[person]['from_poi_to_this_person']
    to_msg = my_dataset[person]['to_messages']
    if msg_from_poi != "NaN" and to_msg != "NaN":
        my_dataset[person]['fraction_from_poi'] = msg_from_poi/float(to_msg)
    else:
        my_dataset[person]['fraction_from_poi'] = 0
    msg_to_poi = my_dataset[person]['from_this_person_to_poi']
    from_msg = my_dataset[person]['from_messages']
    if msg_to_poi != "NaN" and from_msg != "NaN":
        my_dataset[person]['fraction_to_poi'] = msg_to_poi/float(from_msg)
    else:
        my_dataset[person]['fraction_to_poi'] = 0
new_features_list = features_list + ['fraction_to_poi', 'fraction_from_poi']

## Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, new_features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

#Select the best features: 
#Removes all but the k highest scoring features
from sklearn.feature_selection import f_classif
k = 7
selector = SelectKBest(f_classif, k=7)
selector.fit_transform(features, labels)
print("Best features:")
scores = zip(new_features_list[1:],selector.scores_)
sorted_scores = sorted(scores, key = lambda x: x[1], reverse=True)
print sorted_scores
optimized_features_list = poi_label + list(map(lambda x: x[0], sorted_scores))[0:k]
print(optimized_features_list)

# Extract from dataset
data = featureFormat(my_dataset, optimized_features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)
#rescale
scaler = preprocessing.MinMaxScaler()
features = scaler.fit_transform(features)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html
def evaluate_clf(clf, features, labels, params, iters=100):
    accuracy = []
    precision = []
    recall = []
    for i in range(iters):
        features_train, features_test, labels_train, labels_test = \
        train_test_split(features, labels, test_size=0.3, random_state=i)
        
        clf.fit(features_train, labels_train)
        predictions = clf.predict(features_test)
        accuracy.append(accuracy_score(labels_test, predictions))
        precision.append(precision_score(labels_test, predictions))
        recall.append(recall_score(labels_test, predictions))
        
    print "accuracy: {}".format(mean(accuracy))
    print "precision: {}".format(mean(precision))
    print "recall:    {}".format(mean(recall))
    best_params = clf.best_estimator_.get_params()
    for param_name in params.keys():
        print("%s = %r, " % (param_name, best_params[param_name]))

from sklearn import naive_bayes        
nb_clf = naive_bayes.GaussianNB()
nb_param = {}
nb_grid_search = GridSearchCV(nb_clf, nb_param)

#print("Evaluate naive bayes model")
#evaluate_clf(nb_grid_search, features, labels, nb_param)
#accuracy: 0.852619047619
#precision: 0.431829365079
#recall:    0.375834054834



from sklearn.cluster import KMeans
k_clf = KMeans()
k_param = {'n_clusters': [2], 'tol': [1, 0.1, 0.01, 0.001, 0.0001]}
k_grid_search = GridSearchCV(k_clf, k_param)

print("Evaluate k-mean model")
evaluate_clf(k_grid_search, features, labels, k_param)
#accuracy: 0.713571428571
#precision: 0.467001625323
#recall:    0.363350649351
#tol = 0.1 
#n_clusters = 2
#clf = 

from sklearn import linear_model
from sklearn.pipeline import Pipeline
lo_clf = Pipeline(steps=[
        ('scaler', preprocessing.StandardScaler()),
        ('classifier', linear_model.LogisticRegression())])
         
lo_param = {'classifier__tol': [1, 0.1, 0.01, 0.001, 0.0001], \
            'classifier__C': [0.1, 0.01, 0.001, 0.0001]}
lo_grid_search = GridSearchCV(lo_clf, lo_param)
#print("Evaluate logistic regression model")
#evaluate_clf(lo_grid_search, features, labels, lo_param)
#accuracy: 0.863333333333
#precision: 0.507341269841
#recall:    0.261941558442
#classifier__tol = 1, 
#classifier__C = 0.1, 

from sklearn import svm
s_clf = svm.SVC()
s_param = {'kernel': ['rbf', 'linear', 'poly'], 'C': [0.1, 1, 10, 100, 1000],\
           'gamma': [1, 0.1, 0.01, 0.001, 0.0001], 'random_state': [42]}    
s_grid_search = GridSearchCV(s_clf, s_param)
#print("Evaluate svm model")
#evaluate_clf(s_grid_search, features, labels, s_param)
#accuracy: 0.865714285714
#precision: 0.154666666667
#recall:    0.0600357142857
#kernel = 'rbf'
#C = 0.1 
#gamma = 1

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

#This part is included in the Task 4 using gridsearch

features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)



### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

clf = naive_bayes.GaussianNB()
features_list = optimized_features_list

dump_classifier_and_data(clf, my_dataset, features_list)