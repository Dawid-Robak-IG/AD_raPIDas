import src.trainings as trainings


def train_all():
    trainings.train_by_sp()
    trainings.train_by_model_params()
    trainings.train_by_load()

if __name__ == "__main__":
    train_all()