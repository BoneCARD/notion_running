import uuid
import json


def wordClass_struct(className, classInterpret, parent):
    return {
        className.strip(): {
            "classInterpret": classInterpret.strip(),
            "parent": parent
        }
    }


def run():
    with open("./conf/word_class.yml") as f:
        _db = {}
        parent = None
        for _ in f.readlines():
            if not _.startswith("\t"):
                _raw_list = _.split("- ")[1].split(" ")
                _db.update(wordClass_struct(_raw_list[0], _raw_list[1], None))
                parent = _raw_list[0]
            else:
                _raw_list = _.split("\t- ")[1].split(" ")
                _db.update(wordClass_struct(_raw_list[0], _raw_list[1], parent))
        with open("./conf/word_class.json", "w", encoding="utf-8") as ff:
            # class_db = {}
            # for classCell in _db:
            #     class_db.update({classCell["className"]: classCell})
            ff.write(json.dumps(_db, indent=4, ensure_ascii=False))


if __name__ == '__main__':
    run()
