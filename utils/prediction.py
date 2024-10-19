import random

def pred_spaces_change(parkinglot_id: int, minutes: int) -> int:
    # query data n_minutes ahead

    pred_change = random.randint(0, minutes // 5)

    # make the prediction based on the query data
    # predict 5 minutes later

    return pred_change
