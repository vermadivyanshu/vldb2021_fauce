"""
http://papers.nips.cc/paper/5138-the-randomized-dependence-coefficient.pdf
"""
import numpy as np
from scipy.stats import rankdata
import csv
import pandas
from sklearn.preprocessing import OrdinalEncoder

ordinal_encoder = OrdinalEncoder()
# df=pandas.read_csv('/Users/dverma/uottawa/project/job/person_info.csv', on_bad_lines='skip', low_memory=False)
df=pandas.read_csv('/Users/dverma/uottawa/project/job/person_info.csv', on_bad_lines='skip', low_memory=False, quoting=3, escapechar='\\')
# df.fillna({'imdb_id': -1}, inplace=True)
df.fillna('', inplace=True)
# df.fillna({'phonetic_code': ''}, inplace=True)
# df.sort_values(by=['kind'], inplace=True)
# df.fillna({"kind_id": -1, "production_year": 0, "phonetic_code": '', "episode_of_id": -1, "season_nr": -1, "episode_nr": -1}, inplace=True)
# df['title'].fillna('', inplace=True)
# df['imdb_index'].fillna('', inplace=True)
# df['phonetic_code'].fillna('', inplace=True)
# df['series_years'].fillna('', inplace=True)
# cols = ['title', 'imdb_index', 'phonetic_code', 'series_years', 'md5sum']
# df[cols] = ordinal_encoder.fit_transform(df[cols])
# df['imdb_id'].fillna(-1, inplace=True)
# df['production_year'].fillna(-1, inplace=True)
# df['episode_of_id'].fillna(-1, inplace=True)
# df['season_nr'].fillna(-1, inplace=True)
# df['episode_nr'].fillna(-1, inplace=True)
df = df.drop(axis=1, labels=["note"])
# cols = ['title']
# cols = ['link']
# df[cols] = ordinal_encoder.fit_transform(df[cols])
# df.sort_values(by=['title'], inplace=True)
# cols = ['title']
# df[cols] = ordinal_encoder.fit_transform(df[cols])
df.sort_values(by=['info'], inplace=True)
cols = ['info']
# df[cols] = ordinal_encoder.fit_transform(df[cols])
# df.sort_values(by=['phonetic_code'], inplace=True)
# cols = ['phonetic_code']
# df[cols] = ordinal_encoder.fit_transform(df[cols])
# cols = ['imdb_index']
# df.sort_values(by=['imdb_index'], inplace=True)
# df[cols] = ordinal_encoder.fit_transform(df[cols])
# cols = ['name_pcode_cf']
# df.sort_values(by=['name_pcode_cf'], inplace=True)
# df[cols] = ordinal_encoder.fit_transform(df[cols])
# df.sort_values(by=['name_pcode_nf'], inplace=True)
# cols = ['name_pcode_nf']
# df[cols] = ordinal_encoder.fit_transform(df[cols])
# df.sort_values(by=['surname_pcode'], inplace=True)
# cols = ['surname_pcode']
# df[cols] = ordinal_encoder.fit_transform(df[cols])
# df.sort_values(by=['md5sum'], inplace=True)
# cols = ['md5sum']
# df[cols] = ordinal_encoder.fit_transform(df[cols])
# df.sort_values(by=['gender'], inplace=True)
# cols = ['gender']
# df[cols] = ordinal_encoder.fit_transform(df[cols])

# median = df['nr_order'].median()
# df['nr_order'].fillna(median, inplace=True)
# df['person_role_id'].fillna(-1, inplace=True)

array=df.values
def rdc(x, y, f=np.sin, k=20, s=1/6., n=1):
    """
    Computes the Randomized Dependence Coefficient
    x,y: numpy arrays 1-D or 2-D
         If 1-D, size (samples,)
         If 2-D, size (samples, variables)
    f:   function to use for random projection
    k:   number of random projections to use
    s:   scale parameter
    n:   number of times to compute the RDC and
         return the median (for stability)

    According to the paper, the coefficient should be relatively insensitive to
    the settings of the f, k, and s parameters.
    """
    print("*** x, y ****", x[0], y[0])
    if n > 1:
        values = []
        for i in range(n):
            try:
                values.append(rdc(x, y, f, k, s, 1))
            except np.linalg.linalg.LinAlgError:
                pass
        return np.median(values)

    if len(x.shape) == 1:
        x = x.reshape((-1, 1))
    if len(y.shape) == 1:
        y = y.reshape((-1, 1))

    # Copula Transformation
    cx = np.column_stack([rankdata(xc, method='ordinal') for xc in x.T])/float(x.size)
    cy = np.column_stack([rankdata(yc, method='ordinal') for yc in y.T])/float(y.size)

    # Add a vector of ones so that w.x + b is just a dot product
    O = np.ones(cx.shape[0])
    X = np.column_stack([cx, O])
    Y = np.column_stack([cy, O])

    # Random linear projections
    Rx = (s/X.shape[1])*np.random.randn(X.shape[1], k)
    Ry = (s/Y.shape[1])*np.random.randn(Y.shape[1], k)
    X = np.dot(X, Rx)
    Y = np.dot(Y, Ry)

    # Apply non-linear function to random projections
    fX = f(X)
    fY = f(Y)

    # Compute full covariance matrix
    C = np.cov(np.hstack([fX, fY]).T)

    # Due to numerical issues, if k is too large,
    # then rank(fX) < k or rank(fY) < k, so we need
    # to find the largest k such that the eigenvalues
    # (canonical correlations) are real-valued
    k0 = k
    lb = 1
    ub = k
    while True:

        # Compute canonical correlations
        Cxx = C[:k, :k]
        Cyy = C[k0:k0+k, k0:k0+k]
        Cxy = C[:k, k0:k0+k]
        Cyx = C[k0:k0+k, :k]

        eigs = np.linalg.eigvals(np.dot(np.dot(np.linalg.pinv(Cxx), Cxy),
                                         np.dot(np.linalg.pinv(Cyy), Cyx)))

        # Binary search if k is too large
        if not (np.all(np.isreal(eigs)) and
                0 <= np.min(eigs) and
                np.max(eigs) <= 1):
            ub -= 1
            k = (ub + lb) // 2
            continue
        if lb == ub:
            break
        lb = k
        if ub == lb + 1:
            k = ub
        else:
            k = (ub + lb) // 2

    return np.sqrt(np.max(eigs))
matrix=np.zeros((len(array[0]), len(array[0])))
for i in range(len(array[0])):
    for j in range(len(array[0])):
        matrix[i][j]=rdc(array[:,i], array[:,j])
my_df=pandas.DataFrame(matrix)
my_df.to_csv('/Users/dverma/uottawa/project/job/rdc_person_info.csv', index=False, header=False)
