from sklearn.ensemble import RandomForestClassifier
from modAL.uncertainty import entropy_sampling
from modAL.models import ActiveLearner
import os
import pickle
import numpy
from database.services.Documents import DocumentsQueryService
from services.cluster import ClusterService
from sentence_transformers import SentenceTransformer
import warnings
from sklearn.exceptions import DataConversionWarning
warnings.filterwarnings(action='ignore', category=DataConversionWarning)


embedder = SentenceTransformer('distiluse-base-multilingual-cased-v2')

PATH = os.getenv("VOLUMN_PATH")


class ClassificationService:
    @staticmethod
    def prepare():
        documents = DocumentsQueryService.getAllUploaded()
        X_train = []
        X_train_corpus = []
        for doc in documents:
            X_train_corpus.append(doc['content'])
        X_train = embedder.encode(X_train_corpus)
        cluster = ClusterService(5)
        initialSample = cluster.cluster(X_train, documents)
        return initialSample

    @staticmethod
    def initial(documents):
        X_train = []
        Y_train = []
        X_train_corpus = []
        for document in documents:
            X_train_corpus.append(document['content'])
            Y_train.append(document['label_id'])
        print(Y_train)
        X_train = embedder.encode(X_train_corpus)
        learner = ActiveLearner(
            estimator=RandomForestClassifier(n_jobs=4),
            query_strategy=entropy_sampling,
            X_training=X_train, y_training=Y_train
        )
        with open('{PATH}/model/model_{user_id}.pkl'.format(user_id='00000003', PATH=PATH), 'wb') as file:
            pickle.dump(learner, file)
        return "Success"

    @staticmethod
    def predict(content='', model='public'):
        corpus = []
        corpus.append(content)
        embeddings = embedder.encode(corpus)
        with open('{PATH}/model/model_{schema_name}.pkl'.format(schema_name=model, PATH=PATH), 'rb') as file:
            learner = pickle.load(file)
            print('model loaded')
        print(embeddings)
        prediction = learner.predict(embeddings)
        print(prediction)
        return prediction[0]

    @staticmethod
    def confirm(content, label, model='public'):
        try:
            corpus = []
            corpus.append(content)
            print(corpus)
            embeddings = embedder.encode(corpus)
            with open('{PATH}/model/model_{schema_name}.pkl'.format(schema_name=model, PATH=PATH), 'rb') as file:
                learner = pickle.load(file)
            if isinstance(label, str):
                label = numpy.array([label])
            elif isinstance(label, list):
                label = numpy.array(label)
                pass
            else:
                raise ValueError("label must be a string or a list")
            print(numpy.array([label]))
            print(embeddings.shape)
            print(label.shape)
            learner.teach(embeddings.reshape(1, -1), numpy.array([label]))
            with open('{PATH}/model/model_{schema_name}.pkl'.format(schema_name=model, PATH=PATH), 'wb') as file:
                pickle.dump(learner, file)
                print('Model Saved!')
        except Exception as e:
            print(e)
        return True
