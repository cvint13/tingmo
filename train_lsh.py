from tingmo import TingMo
import pickle


# Create LSH object
tm = TingMo()

# Serialize the LSH
data = pickle.dumps(tm)

# Save to file
with open('lsh.pickle', 'wb') as handle:
    pickle.dump(data, handle, protocol=pickle.HIGHEST_PROTOCOL)