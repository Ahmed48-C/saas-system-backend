class JsonUtils:

    @staticmethod
    def get_choices(choice_name, choices, message=""):
        options = []
        for key, val in choices:
            child = {
                "id": key,
                "name": val
            }
            options.append(child)

        obj = {
            choice_name: {
                "actual_count": len(choices),
                "data": options
            },
            "errMsg": message
        }
        return obj

    @staticmethod
    def get_choices_as_list(choices):
        options = []
        for _, val in choices:
            options.append(val)

        return options
