###Saaty's Analytic hierarchy process (AHP)
##
import hashlib
import sys
import math

scale = [
        {'definition': 'Equal importance', 'value': 1.0}, 
        {'definition': 'Mild superiority', 'value': 3.0}, 
        {'definition': 'Strong superiority', 'value': 5.0}, 
        {'definition': 'Very strong superiority', 'value': 7.0}, 
        {'definition': 'Supreme superiority', 'value': 9.0}, 
        {'definition': 'Mild superiority of the second one', 'value': 1.0/3},  ##here goes reversed rating
        {'definition': 'Strong superiority of the second one', 'value': 1.0/5}, 
        {'definition': 'Very strong superiority of the second one', 'value': 1.0/7}, 
        {'definition': 'Supreme superiority of the second one', 'value': 1.0/9}, 
    ]

criterias = ['Map coverage', 'Map details', 'Routes construction']
alternatives = ['Yandex.Maps', 'Google.Maps', '2GIS']

def make_eigenvector(matrix):
    eigenvector = []
    for i in range(0, len(matrix)):
        prod = 1
        for j in range(0, len(matrix[i])):
            prod = prod * matrix[i][j]
        eigenvector.append(prod ** (1.0 / len(matrix)))
    return eigenvector

def normalize_vector(vector):
    vec_len = sum(vector)
    return list(map(lambda x: x / vec_len, vector))



print('Criterias:')
for criteria in criterias:
    print(criteria)
print '\n'
print('Alternatives')
for alternative in alternatives:
    print(alternative)
print'\n'
print('Scales:')
i = 0
for factor in scale:
    print('%s) %s ' % (i, factor['definition']))
    i = i + 1
print('\n')
print('Give your opinion on relations. Choose by number from the table above:')
criteria_compare_matrix = [[None for _ in range(0, len(criterias))] for _ in range(0, len(criterias))]
for i in range(0, len(criterias)):
    criteria_compare_matrix[i][i] = scale[0]['value']
    for j in range(i+1, len(criterias)):
        choice = int(input('%s vs %s: ' % (criterias[i], criterias[j])))
        criteria_compare_matrix[i][j] = scale[choice]['value']
        criteria_compare_matrix[j][i] = 1.0 / scale[choice]['value']
print(criteria_compare_matrix)
eigenvector = make_eigenvector(criteria_compare_matrix)
print('Eigenvector: %s' % eigenvector)
eigenvector = normalize_vector(eigenvector)
print('Normalized eigenvector: %s' % eigenvector)

criterias_eigenvectors = []
for i in range(0, len(criterias)):
    print '\n'
    print('Criteria: %s' % criterias[i])
    per_criteria_matrix = [[None for _ in range(0, len(criterias))] for _ in range(0, len(criterias))]
    for j in range(0, len(alternatives)):
        per_criteria_matrix[j][j] = scale[0]['value']
        for k in range(j + 1, len(alternatives)):
            choice = int(input('%s vs %s: ' % (alternatives[j], alternatives[k])))
            per_criteria_matrix[j][k] = scale[choice]['value']
            per_criteria_matrix[k][j] = 1.0 / scale[choice]['value']
    per_criteria_eigenvector = make_eigenvector(per_criteria_matrix)
    print('Matrix %s' % per_criteria_matrix)
    print('Eigenvector %s' % per_criteria_eigenvector)
    per_criteria_eigenvector = normalize_vector(per_criteria_eigenvector)
    print('Normalized eigenvector: %s' % per_criteria_eigenvector)
    criterias_eigenvectors.append(per_criteria_eigenvector)
print '\n'

final_scores = []
for j in range(0, len(alternatives)):
    s = 0
    for i in range(0, len(criterias)):
        s = s + (criterias_eigenvectors[i][j] * eigenvector[i])
    final_scores.append(s)
print('Importance coefficients: %s' % final_scores)
print '\n'
best_alternative_index = final_scores.index(max(final_scores))
print('Your best choice is: %s' % alternatives[best_alternative_index])