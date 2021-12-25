def ln_detector(guess_instance,code,only_name=True):
    if only_name:
        return guess_instance.language_name(code)
    else:
        return guess_instance.probabilities(code)