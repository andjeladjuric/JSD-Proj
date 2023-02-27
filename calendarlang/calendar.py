from os.path import  join,dirname
from textx import metamodel_from_file



#class GoogleCalendar(object):
    #def...

    
def main(file_name_to_interpret):

    this_folder = dirname(__file__)

    google_calendar_meta_model = metamodel_from_file(join(this_folder, 'calendarlang.tx'), debug=False)
    google_calendar_model = google_calendar_meta_model.model_from_file(file_name_to_interpret)

    #google_calendar = GoogleCalendar()

if __name__ == "__main__":
    main("calendarExample.txt")