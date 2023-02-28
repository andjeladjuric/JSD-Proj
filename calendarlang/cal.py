from textx import metamodel_from_file
from os.path import dirname, join

def main(file_name):
    this_folder = dirname(__file__)
    calendar_mm = metamodel_from_file(join(this_folder, 'calendarlang.tx'), debug=False)
    calendar_model = calendar_mm.model_from_file(file_name)
    
    print(calendar_model.owner.email)

if __name__ == "__main__":
    main("calendarExample.cal")
