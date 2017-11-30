from timetable.models import TeacherTimePreference
from common import Database, PreferenceLevel, toStartIndex, level_to_type


def staffTimePreferences(tt):
    db = Database()
    entries = []
    next_id = db.getNextID()

    # Timetable from last year
    for teacher in tt.teachers.all():
        preferences = PreferenceLevel.Neutral * 336
        for time_preference in TeacherTimePreference.objects.filter(
                preferenceset=tt.preferenceset,
                teacher=teacher):
            start_index = toStartIndex(time_preference.day,
                                       time_preference.start)
            type = level_to_type[time_preference.level]
            type = type[0] if time_preference.weight > 1.0 else type[1] 
            preferences = preferences[:start_index] + type * (time_preference.duration*2) + preferences[start_index + time_preference.duration*2:]
        external_id = teacher.id

        teacher_id_query = u"SELECT uniqueid FROM departmental_instructor WHERE external_uid={0}".format(external_id)
        db.execute(teacher_id_query)
        assert db.rowcount == 1, "More than one entry in unitime for teacher {0} with id {1}".format(teacher, teacher.id)
        teacher_id = db.fetchnextrow()[0]

        remove_previous_preference_query = u"""DELETE FROM timetable.time_pref WHERE owner_id={0}""".format(teacher_id)
        db.execute(remove_previous_preference_query)

        add_preference_query = u"""INSERT INTO timetable.time_pref 
                   (owner_id, pref_level_id, preference, time_pattern_id, uniqueid) 
                   VALUES ({0}, 1, '{1}', null, {2})""".format(teacher_id, preferences, next_id)

        db.execute(add_preference_query)
        next_id = db.getNextID()
    db.commit()
    db.close()
