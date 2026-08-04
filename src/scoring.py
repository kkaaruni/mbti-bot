def calculate_mbti(answers, questions):

    scores = {
        "E": 0,
        "I": 0,
        "S": 0,
        "N": 0,
        "T": 0,
        "F": 0,
        "J": 0,
        "P": 0
    }


    for answer, question in zip(answers, questions):

        first, second = question["dimension"]

        scores[first] += answer
        scores[second] += (11 - answer)


    mbti = ""

    pairs = [
        ("E", "I"),
        ("S", "N"),
        ("T", "F"),
        ("J", "P")
    ]

    for a, b in pairs:

        if scores[a] >= scores[b]:
            mbti += a
        else:
            mbti += b


    return mbti, scores