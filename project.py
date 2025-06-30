import copy
import time

# تعريف بيانات المشكلة 
def get_problem_data_default():
    """
    تعريف بيانات المشكلة الافتراضية: الدورات، القاعات، والقيود.
    """
    courses_definition = [
        {"name": "مقدمة في البرمجة", "duration": 1.0, "instructor": "د. أحمد", "num_students": 30},
        {"name": "هياكل البيانات", "duration": 1.0, "instructor": "د. ليلى", "num_students": 25},
        {"name": "قواعد البيانات", "duration": 1.0, "instructor": "د. محمد", "num_students": 20},
        {"name": "الذكاء الاصطناعي", "duration": 1.0, "instructor": "د. ليلى", "num_students": 28},
        {"name": "شبكات الحاسوب", "duration": 1.0, "instructor": "د. أحمد", "num_students": 35}
    ]

    rooms_definition = [
        {"name": "قاعة A", "capacity": 30, "available_times": [(9.0, 17.0)]},
        {"name": "قاعة B", "capacity": 25, "available_times": [(9.0, 17.0)]},
        {"name": "معمل الحاسوب", "capacity": 40, "available_times": [(9.0, 17.0)]}
    ]

    constraints_definition = {
        "precedence_constraints": [
            {"y_course": "مقدمة في البرمجة", "x_course": "هياكل البيانات"}
        ],
        "absolute_time_constraints": [
            {"course_name": "الذكاء الاصطناعي", "type": "start_after", "time_value": 13.0},
            {"course_name": "شبكات الحاسوب", "type": "end_before", "time_value": 12.0}
        ],
        "working_hours_constraints": {"start": 9.0, "end": 17.0},
        "instructor_availability_constraints": [
            {"instructor_name": "د. ليلى", "unavailable_times": [(10.0, 11.0)]}
        ]
    }

    problem_data = {
        "courses": courses_definition,
        "rooms": rooms_definition,
        "constraints": constraints_definition
    }
    return problem_data

# دوال طباعة الجدول 
def format_time(time_float):
    """Formats a float time (e.g., 9.5) into a HH:MM string (e.g., '09:30')."""
    hours = int(time_float)
    minutes = int((time_float - hours) * 60)
    return f"{hours:02d}:{minutes:02d}"

def print_schedule_table(schedule, problem_data, title="جدول الدورات"):
    """
    Prints the schedule in a formatted table.
    """
    print("\n" + " " * 4 + f"--- {title} ---")
    print(" " * 4 + "=" * 70)
    header = f"{'الدورة':<25} | {'المحاضر':<15} | {'الوقت':<15} | {'القاعة':<15}"
    print(" " * 4 + header)
    print(" " * 4 + "-" * 70)

    # Sort courses by start time for a clean, chronological view
    sorted_courses = sorted(
        schedule.items(),
        key=lambda item: item[1].get("start_time", float('inf'))
    )

    for course_name, details in sorted_courses:
        start_time = details.get("start_time")
        end_time = details.get("end_time")
        room = details.get("room")
        course_details = get_course_details(course_name, problem_data["courses"])
        instructor = course_details["instructor"] if course_details else "غير معروف"

        if start_time is not None and room is not None:
            time_str = f"{format_time(start_time)} - {format_time(end_time)}"
            row = f"{course_name:<25} | {instructor:<15} | {time_str:<15} | {room:<15}"
            print(" " * 4 + row)
        else:
            row = f"{course_name:<25} | {instructor:<15} | {'غير مجدول':<15} | {'---':<15}"
            print(" " * 4 + row)

    print(" " * 4 + "=" * 70)
    print("\n")


#  دوال التحقق من القيود (منطق الخوارزمية) 

def get_course_details(course_name, courses_definition):
    """تسترجع خصائص دورة معينة."""
    for course in courses_definition:
        if course["name"] == course_name:
            return course
    return None

def get_room_details(room_name, rooms_definition):
    """تسترجع خصائص قاعة معينة."""
    for room in rooms_definition:
        if room["name"] == room_name:
            return room
    return None

def check_working_hours(curr_course_schedule, course_name, problem_data):
    """تتحقق مما إذا كانت الدورة تقع بالكامل ضمن ساعات العمل المحددة."""
    if curr_course_schedule[course_name].get("start_time") is None:
        return True

    start_time = curr_course_schedule[course_name]["start_time"]
    end_time = curr_course_schedule[course_name]["end_time"]
    working_hours_const = problem_data["constraints"]["working_hours_constraints"]

    if not (working_hours_const["start"] <= start_time and
            end_time <= working_hours_const["end"]):
        return False
    return True

def check_precedence_constraint(curr_schedule, course_name, problem_data):
    """تتأكد أن الدورة السابقة قد انتهت قبل أن تبدأ الدورة الحالية."""
    if curr_schedule[course_name].get("start_time") is None:
        return True

    precedence_constraints = problem_data["constraints"]["precedence_constraints"]
    
    for p_const in precedence_constraints:
        if p_const["x_course"] == course_name:
            y_course_name = p_const["y_course"]
            if y_course_name in curr_schedule and curr_schedule[y_course_name].get("start_time") is not None:
                y_end_time = curr_schedule[y_course_name]["end_time"]
                x_start_time = curr_schedule[course_name]["start_time"]
                
                if x_start_time < y_end_time:
                    return False
    return True

def check_absolute_time_constraint(curr_course_schedule, course_name, problem_data):
    """تتحقق من التزام الدورة بالقيود الزمنية المطلقة."""
    if curr_course_schedule[course_name].get("start_time") is None:
        return True

    start_time = curr_course_schedule[course_name]["start_time"]
    end_time = curr_course_schedule[course_name]["end_time"]
    abso_time_consts = problem_data["constraints"]["absolute_time_constraints"]

    for abs_const in abso_time_consts:
        if abs_const["course_name"] == course_name:
            if abs_const["type"] == "start_after" and start_time < abs_const["time_value"]:
                return False
            elif abs_const["type"] == "start_before" and start_time > abs_const["time_value"]:
                return False
            elif abs_const["type"] == "end_after" and end_time < abs_const["time_value"]:
                return False
            elif abs_const["type"] == "end_before" and end_time > abs_const["time_value"]:
                return False
    return True

def check_room_capacity(curr_course_schedule, course_name, problem_data):
    """تتحقق من أن سعة القاعة كافية لعدد طلاب الدورة."""
    if curr_course_schedule[course_name].get("start_time") is None:
        return True

    room_name = curr_course_schedule[course_name].get("room")
    if not room_name:
        return False # يجب أن يكون هناك قاعة مخصصة
    
    course_details = get_course_details(course_name, problem_data["courses"])
    room_details = get_room_details(room_name, problem_data["rooms"])

    if course_details and room_details and course_details["num_students"] > room_details["capacity"]:
        return False
    return True

def check_instructor_availability(curr_course_schedule, course_name, problem_data):
    """تتحقق من توفر المحاضر في الوقت المجدول للدورة."""
    if curr_course_schedule[course_name].get("start_time") is None:
        return True

    course_details = get_course_details(course_name, problem_data["courses"])
    if not course_details: return True # لا يوجد تفاصيل للدورة

    instructor_name = course_details["instructor"]
    
    start_time = curr_course_schedule[course_name]["start_time"]
    end_time = curr_course_schedule[course_name]["end_time"]

    instructor_constraints = problem_data["constraints"].get("instructor_availability_constraints", [])

    for inst_const in instructor_constraints:
        if inst_const["instructor_name"] == instructor_name:
            for unavailable_start, unavailable_end in inst_const["unavailable_times"]:
                # If course time overlaps with instructor unavailable time
                if (start_time < unavailable_end and unavailable_start < end_time):
                    return False
    return True

def check_no_overlap_constraints(curr_schedule, current_course_name, problem_data):
    """تتأكد أن الدورة الحالية لا تتداخل زمنيًا مع أي دورة أخرى مجدولة (قاعة أو محاضر)."""
    if curr_schedule[current_course_name].get("start_time") is None:
        return True

    current_course_details = get_course_details(current_course_name, problem_data["courses"])
    if not current_course_details: return True

    current_start = curr_schedule[current_course_name]["start_time"]
    current_end = curr_schedule[current_course_name]["end_time"]
    current_room = curr_schedule[current_course_name].get("room")
    current_instructor = current_course_details["instructor"]

    for other_course_name, other_schedule_details in curr_schedule.items():
        if other_course_name == current_course_name:
            continue

        if other_schedule_details.get("start_time") is None:
            continue

        if other_schedule_details.get("end_time") is None:
            other_course_details = get_course_details(other_course_name, problem_data["courses"])
            if other_course_details and other_schedule_details.get("start_time") is not None:
                other_schedule_details["end_time"] = other_schedule_details["start_time"] + other_course_details["duration"]
            else:
                continue
            
        other_start = other_schedule_details["start_time"]
        other_end = other_schedule_details["end_time"]
        other_room = other_schedule_details.get("room")
        other_course_details = get_course_details(other_course_name, problem_data["courses"])
        if not other_course_details: continue
        other_instructor = other_course_details["instructor"]

        # تحقق من التداخل الزمني
        if (current_start < other_end and other_start < current_end):
            # تعارض قاعة
            if current_room and other_room and current_room == other_room:
                return False
            # تعارض محاضر
            if current_instructor and other_instructor and current_instructor == other_instructor:
                return False
    return True


def check_all_constraints(curr_schedule, course_name, problem_data):
    """
    الدالة الرئيسية التي تنسق عملية التحقق من جميع القيود.
    تُرجع True إذا كانت جميع القيود مستوفاة، False بخلاف ذلك.
    """
    if course_name not in curr_schedule or curr_schedule[course_name].get("start_time") is None:
        return True 

    course_details = get_course_details(course_name, problem_data["courses"])
    if not course_details:
        return False
    
    # حساب end_time للدورة التي يتم فحصها حاليًا (إذا لم تكن محددة بالفعل)
    if curr_schedule[course_name].get("end_time") is None:
        curr_schedule[course_name]["end_time"] = curr_schedule[course_name]["start_time"] + course_details["duration"]

    # استدعاء دوال التحقق الفرعية
    if not check_working_hours(curr_schedule, course_name, problem_data):
        return False
    if not check_precedence_constraint(curr_schedule, course_name, problem_data):
        return False
    if not check_absolute_time_constraint(curr_schedule, course_name, problem_data):
        return False
    if not check_room_capacity(curr_schedule, course_name, problem_data):
        return False
    if not check_instructor_availability(curr_schedule, course_name, problem_data):
        return False
    if not check_no_overlap_constraints(curr_schedule, course_name, problem_data):
        return False

    return True 

#  خوارزمية البحث بالتراجع مع تحسين MCV والفحص الأمامي المبسّط 

def find_mcv_course(curr_schedule, courses_names, possible_times, problem_data):
    """
    تجد الدورة الأكثر تقييداً (Most Constrained Variable - MCV)
    التي لم يتم جدولتها بعد، بناءً على عدد التعيينات الصالحة المحتملة لها.
    """
    unassigned_courses = [c_name for c_name in courses_names if curr_schedule[c_name]["start_time"] is None]
    
    if not unassigned_courses:
        return None

    min_remaining_values = float('inf')
    mcv_course = None

    for course_name in unassigned_courses:
        num_possible_assignments = 0
        course_details = get_course_details(course_name, problem_data["courses"])
        if not course_details: continue

        course_duration = course_details["duration"]

        for time_slot in possible_times:
            proposed_start_time = time_slot[0]
            proposed_room_name = time_slot[1]
            proposed_end_time = proposed_start_time + course_duration

            temp_schedule = copy.deepcopy(curr_schedule)
            temp_schedule[course_name]["start_time"] = proposed_start_time
            temp_schedule[course_name]["end_time"] = proposed_end_time
            temp_schedule[course_name]["room"] = proposed_room_name

            # تحقق من جميع القيود للدورة نفسها مع هذا التعيين المقترح
            # هذا جزء من عملية MCV لتحديد "أكثر تقييدًا"
            if check_all_constraints(temp_schedule, course_name, problem_data):
                num_possible_assignments += 1
        
        if num_possible_assignments < min_remaining_values:
            min_remaining_values = num_possible_assignments
            mcv_course = course_name
    
    return mcv_course

def backtracking_search_optimized(curr_schedule, problem_data, all_course_names, possible_times_and_rooms):
    """
    خوارزمية البحث بالتراجع لحل مشكلة جدولة الدورات مع تحسين بسيط للفحص الأمامي.
    """
    # الشرط الأساسي للتوقف: إذا تم جدولة جميع الدورات
    if all(curr_schedule[c_name].get("start_time") is not None for c_name in all_course_names):
        return curr_schedule

    # اختيار الدورة الأكثر تقييدًا (MCV) لتقليل مساحة البحث
    course_to_assign = find_mcv_course(curr_schedule, all_course_names, possible_times_and_rooms, problem_data)

    if course_to_assign is None:
        # قد يحدث إذا لم يكن هناك دورات غير مجدولة (وتم حل المشكلة)
        # أو إذا كانت هناك دورات غير مجدولة ولكن لا توجد حلول ممكنة لها (توقف الفحص الأمامي)
        # في هذه الحالة، إذا لم يتم حلها بالكامل، لا يوجد حل.
        return None 

    # تجربة كل تعيين ممكن (وقت وقاعة) للدورة المختارة
    for time_and_room_slot in possible_times_and_rooms:
        proposed_start_time = time_and_room_slot[0]
        proposed_room = time_and_room_slot[1]

        # إنشاء نسخة جديدة من الجدول لتجربة التعيين
        new_schedule = copy.deepcopy(curr_schedule)
        new_schedule[course_to_assign]["start_time"] = proposed_start_time
        
        course_details = get_course_details(course_to_assign, problem_data["courses"])
        if course_details:
            new_schedule[course_to_assign]["end_time"] = proposed_start_time + course_details["duration"]
        else: # حالة استثنائية إذا لم يتم العثور على تفاصيل الدورة
            continue 
        
        new_schedule[course_to_assign]["room"] = proposed_room

        
        #تعديل 
        if check_all_constraints(new_schedule, course_to_assign, problem_data):
            # إذا كان التعيين الحالي صالحًا، ننتقل بشكل تكراري لجدولة الدورة التالية
            result = backtracking_search_optimized(new_schedule, problem_data, all_course_names, possible_times_and_rooms)
            if result:
                return result # تم العثور على حل كامل
    
    return None # لا يمكن العثور على حل في هذا المسار ضمن هذا المسار من البحث


def run_test_scenario(scenario_name, initial_schedule, problem_data, run_solver=False):
    """
    يشغل سيناريو اختبار واحد ويعرض نتائجه مع قياس الوقت.
    إذا كانت run_solver True، فسيحاول حل الجدولة بدلاً من مجرد التحقق.
    """
    print(f"\n--- بدء سيناريو: {scenario_name} ---")
    start_time_scenario = time.time() # Start timer

    all_course_names = [c["name"] for c in problem_data["courses"]]
    
    # بناء جدول أولي كامل بجميع الدورات مع قيم None للوقت والغرفة إذا لم يتم تحديدها
    full_initial_schedule = {}
    for c_name in all_course_names:
        full_initial_schedule[c_name] = initial_schedule.get(c_name, {"start_time": None, "end_time": None, "room": None})

    # حساب end_time لجميع الدورات في الجدول الأولي قبل بدء أي تحققات
    temp_schedule_for_check_all = copy.deepcopy(full_initial_schedule)
    for course_name in temp_schedule_for_check_all:
        course_details = get_course_details(course_name, problem_data["courses"])
        if course_details and temp_schedule_for_check_all[course_name].get("start_time") is not None:
            temp_schedule_for_check_all[course_name]["end_time"] = temp_schedule_for_check_all[course_name]["start_time"] + course_details["duration"]

    is_initial_schedule_complete = all(full_initial_schedule[c].get("start_time") is not None for c in full_initial_schedule)
    
    if is_initial_schedule_complete:
        print("  ✅ الجدول الأولي المعطى مكتمل. جاري التحقق من قيوده...")
        
        # Measure time for validation
        start_validation_time = time.time()
        
        violated_constraints_details = []
        is_valid_initial_schedule = True
        
        for course_name in temp_schedule_for_check_all:
            if not check_all_constraints(temp_schedule_for_check_all, course_name, problem_data):
                is_valid_initial_schedule = False
                
                # تحديد القيد المخالف بالتفصيل
                if not check_working_hours(temp_schedule_for_check_all, course_name, problem_data):
                    violated_constraints_details.append(f"    - **{course_name}**: مخالفة ساعات العمل (خارج [{problem_data['constraints']['working_hours_constraints']['start']:.0f}:00 - {problem_data['constraints']['working_hours_constraints']['end']:.0f}:00]).")
                elif not check_precedence_constraint(temp_schedule_for_check_all, course_name, problem_data):
                    y_course = next((p['y_course'] for p in problem_data['constraints']['precedence_constraints'] if p['x_course'] == course_name), 'دورة سابقة غير محددة')
                    violated_constraints_details.append(f"    - **{course_name}**: مخالفة قيد الأسبقية (تبدأ قبل انتهاء {y_course}).")
                elif not check_absolute_time_constraint(temp_schedule_for_check_all, course_name, problem_data):
                    abs_const = next((ac for ac in problem_data['constraints']['absolute_time_constraints'] if ac['course_name'] == course_name), None)
                    if abs_const:
                        violated_constraints_details.append(f"    - **{course_name}**: مخالفة قيد الوقت المطلق ({abs_const['type'].replace('_', ' ')} {abs_const['time_value']:.1f}).")
                    else:
                        violated_constraints_details.append(f"    - **{course_name}**: مخالفة قيد الوقت المطلق.")
                elif not check_room_capacity(temp_schedule_for_check_all, course_name, problem_data):
                    course_dets = get_course_details(course_name, problem_data["courses"])
                    room_dets = get_room_details(temp_schedule_for_check_all[course_name].get("room"), problem_data["rooms"])
                    violated_constraints_details.append(f"    - **{course_name}**: مخالفة سعة القاعة ({course_dets['num_students']} طلاب > سعة {room_dets['name']} {room_dets['capacity']}).")
                elif not check_instructor_availability(temp_schedule_for_check_all, course_name, problem_data):
                    course_dets = get_course_details(course_name, problem_data["courses"])
                    unavailable_times_str = ""
                    for inst_const in problem_data['constraints']['instructor_availability_constraints']:
                        if inst_const['instructor_name'] == course_dets['instructor']:
                            unavailable_times_str = ", ".join([f"[{s:.1f}-{e:.1f}]" for s, e in inst_const['unavailable_times']])
                            break
                    violated_constraints_details.append(f"    - **{course_name}**: مخالفة توفر المحاضر ({course_dets['instructor']} غير متاح في الوقت المجدول، أوقات عدم التوفر: {unavailable_times_str}).")
                elif not check_no_overlap_constraints(temp_schedule_for_check_all, course_name, problem_data):
                    violated_constraints_details.append(f"    - **{course_name}**: مخالفة تداخل زمني (قاعة أو محاضر آخر مشغول).")
        
        end_validation_time = time.time()
        validation_duration_ms = (end_validation_time - start_validation_time) * 1000

        print(f"  (استغرق التحقق: {validation_duration_ms:.2f} مللي ثانية)")
        
        if is_valid_initial_schedule:
            print("  ✅ **النتيجة**: الجدول الأولي المعطى **صالح** ولا توجد مخالفات.")
            print_schedule_table(temp_schedule_for_check_all, problem_data, title="الجدول الأولي المعطى")
        else:
            print("  ❌ **النتيجة**: الجدول الأولي المعطى **غير صالح**. التفاصيل:")
            for detail in violated_constraints_details:
                print(detail)
            print_schedule_table(temp_schedule_for_check_all, problem_data, title="الجدول الأولي المخالف")

    # 2. محاولة إيجاد حل باستخدام Backtracking Search إذا طُلب ذلك أو إذا كان الجدول الأولي غير مكتمل
    if run_solver or not is_initial_schedule_complete:
        print("\n  جاري محاولة إيجاد جدول صالح باستخدام خوارزمية البحث بالتراجع المحسّنة...")
        
        start_time_solver = time.time()
        
        courses_names = [c["name"] for c in problem_data["courses"]]
        rooms_names = [r["name"] for r in problem_data["rooms"]]

        solver_initial_schedule = {
            course_name: {"start_time": None, "end_time": None, "room": None}
            for course_name in courses_names
        }

        # توليد جميع التركيبات الممكنة من الأوقات والقاعات
        all_possible_times_and_rooms = []
        general_start = problem_data["constraints"]["working_hours_constraints"]["start"]
        general_end = problem_data["constraints"]["working_hours_constraints"]["end"]

        time_increment = 1.0 
        current_time_slot = general_start
        while current_time_slot < general_end:
            for room_name in rooms_names:
                room_details = get_room_details(room_name, problem_data["rooms"])
                is_room_available_in_slot = False
                if room_details:
                    # تحقق من توفر القاعة للفترة الزمنية الكاملة للدورة (افتراض 1 ساعة)
                    if current_time_slot >= room_details["available_times"][0][0] and \
                       (current_time_slot + time_increment) <= room_details["available_times"][0][1]:
                        is_room_available_in_slot = True
                if is_room_available_in_slot:
                    all_possible_times_and_rooms.append((current_time_slot, room_name))
            current_time_slot += time_increment
        
        all_possible_times_and_rooms.sort(key=lambda x: x[0]) 

        solution = backtracking_search_optimized(solver_initial_schedule, problem_data, courses_names, all_possible_times_and_rooms)

        end_time_solver = time.time()
        solver_duration_ms = (end_time_solver - start_time_solver) * 1000

        if solution:
            print(f"\n  ✅ **تم العثور على حل صالح للجدولة بواسطة الخوارزمية المحسّنة!** (استغرق {solver_duration_ms:.2f} مللي ثانية)")
            print_schedule_table(solution, problem_data, title="الحل الذي تم إيجاده")
        else:
            print(f"\n  ❌ **لم يتم العثور على حل صالح بواسطة الخوارزمية مع القيود المعطاة.** (استغرق {solver_duration_ms:.2f} مللي ثانية)")
            print("  قد يكون السبب: تعارضات قوية في القيود، أو عدم وجود حل ممكن، أو تعقيد عالٍ للمشكلة.")
    
    end_time_scenario = time.time()
    scenario_duration_ms = (end_time_scenario - start_time_scenario) * 1000
    print(f"--- انتهاء سيناريو: {scenario_name} (إجمالي الوقت: {scenario_duration_ms:.2f} مللي ثانية) ---\n" + "="*80)


if __name__ == "__main__":
    problem_data = get_problem_data_default() 

    print(" بدء تشغيل سيناريوهات الجدولة")

    # سيناريو 1: إيجاد جدول صالح (باستخدام Backtracking Solver)
    scenario_1_schedule = {
        c["name"]: {"start_time": None, "end_time": None, "room": None}
        for c in problem_data["courses"]
    }
    run_test_scenario("1. إيجاد جدول صالح (Backtracking Solver)", scenario_1_schedule, problem_data, run_solver=True)

    
    # سيناريو 2: جدول يدوي صالح
    scenario_2_schedule = {
        "مقدمة في البرمجة": {"start_time": 9.0, "end_time": 10.0, "room": "قاعة A"},
        "هياكل البيانات": {"start_time": 11.0, "end_time": 12.0, "room": "قاعة B"},
        "قواعد البيانات": {"start_time": 10.0, "end_time": 11.0, "room": "معمل الحاسوب"},
        "الذكاء الاصطناعي": {"start_time": 14.0, "end_time": 15.0, "room": "قاعة A"},
        "شبكات الحاسوب": {"start_time": 9.0, "end_time": 10.0, "room": "معمل الحاسوب"}
    }
    run_test_scenario("2. جدول يدوي صالح", scenario_2_schedule, problem_data)

    # سيناريو 3: مخالفة قيد الأسبقية
    scenario_3_schedule = {
        "مقدمة في البرمجة": {"start_time": 9.0, "end_time": 10.0, "room": "قاعة A"},
        "هياكل البيانات": {"start_time": 9.5, "end_time": 10.5, "room": "قاعة B"},
        "قواعد البيانات": {"start_time": 10.0, "end_time": 11.0, "room": "معمل الحاسوب"},
        "الذكاء الاصطناعي": {"start_time": 13.0, "end_time": 14.0, "room": "قاعة A"},
        "شبكات الحاسوب": {"start_time": 10.0, "end_time": 11.0, "room": "قاعة A"}
    }
    run_test_scenario("3. مخالفة قيد الأسبقية (هياكل البيانات)", scenario_3_schedule, problem_data)

    # سيناريو 4: مخالفة ساعات العمل
    scenario_4_schedule = {
        "مقدمة في البرمجة": {"start_time": 8.0, "end_time": 9.0, "room": "قاعة A"},
        "هياكل البيانات": {"start_time": 11.0, "end_time": 12.0, "room": "قاعة B"},
        "قواعد البيانات": {"start_time": 10.0, "end_time": 11.0, "room": "معمل الحاسوب"},
        "الذكاء الاصطناعي": {"start_time": 13.0, "end_time": 14.0, "room": "قاعة A"},
        "شبكات الحاسوب": {"start_time": 10.0, "end_time": 11.0, "room": "قاعة A"}
    }
    run_test_scenario("4. مخالفة ساعات العمل (مقدمة في البرمجة)", scenario_4_schedule, problem_data)

    # سيناريو 5: مخالفة توفر المحاضر
    scenario_5_schedule = {
        "مقدمة في البرمجة": {"start_time": 9.0, "end_time": 10.0, "room": "قاعة A"},
        "هياكل البيانات": {"start_time": 10.0, "end_time": 11.0, "room": "قاعة B"},
        "قواعد البيانات": {"start_time": 11.0, "end_time": 12.0, "room": "معمل الحاسوب"},
        "الذكاء الاصطناعي": {"start_time": 13.0, "end_time": 14.0, "room": "قاعة A"},
        "شبكات الحاسوب": {"start_time": 10.0, "end_time": 11.0, "room": "قاعة A"}
    }
    run_test_scenario("5. مخالفة توفر المحاضر (د. ليلى)", scenario_5_schedule, problem_data)

    # سيناريو 6: مخالفة تداخل قاعة
    scenario_6_schedule = {
        "مقدمة في البرمجة": {"start_time": 9.0, "end_time": 10.0, "room": "قاعة A"},
        "هياكل البيانات": {"start_time": 10.0, "end_time": 11.0, "room": "قاعة B"},
        "قواعد البيانات": {"start_time": 9.0, "end_time": 10.0, "room": "قاعة A"},
        "الذكاء الاصطناعي": {"start_time": 13.0, "end_time": 14.0, "room": "معمل الحاسوب"},
        "شبكات الحاسوب": {"start_time": 10.0, "end_time": 11.0, "room": "قاعة B"}
    }
    run_test_scenario("6. مخالفة تداخل قاعة (قاعة A)", scenario_6_schedule, problem_data)

    # سيناريو 7: مخالفة تداخل محاضر
    scenario_7_schedule = {
        "مقدمة في البرمجة": {"start_time": 9.0, "end_time": 10.0, "room": "قاعة A"},
        "هياكل البيانات": {"start_time": 10.0, "end_time": 11.0, "room": "قاعة B"},
        "قواعد البيانات": {"start_time": 11.0, "end_time": 12.0, "room": "معمل الحاسوب"},
        "الذكاء الاصطناعي": {"start_time": 13.0, "end_time": 14.0, "room": "قاعة A"},
        "شبكات الحاسوب": {"start_time": 9.0, "end_time": 10.0, "room": "قاعة B"}
    }
    run_test_scenario("7. مخالفة تداخل محاضر (د. أحمد)", scenario_7_schedule, problem_data)

    # سيناريو 8: مخالفة سعة القاعة
    scenario_8_schedule = {
        "مقدمة في البرمجة": {"start_time": 9.0, "end_time": 10.0, "room": "قاعة B"},
        "هياكل البيانات": {"start_time": 10.0, "end_time": 11.0, "room": "قاعة A"},
        "قواعد البيانات": {"start_time": 11.0, "end_time": 12.0, "room": "معمل الحاسوب"},
        "الذكاء الاصطناعي": {"start_time": 13.0, "end_time": 14.0, "room": "قاعة A"},
        "شبكات الحاسوب": {"start_time": 10.0, "end_time": 11.0, "room": "معمل الحاسوب"}
    }
    run_test_scenario("8. مخالفة سعة القاعة (مقدمة في البرمجة في قاعة B)", scenario_8_schedule, problem_data)

    # سيناريو 9: مخالفة الوقت المطلق (الذكاء الاصطناعي تبدأ قبل 13:00)
    scenario_9_schedule = {
        "مقدمة في البرمجة": {"start_time": 9.0, "end_time": 10.0, "room": "قاعة A"},
        "هياكل البيانات": {"start_time": 10.0, "end_time": 11.0, "room": "قاعة B"},
        "قواعد البيانات": {"start_time": 11.0, "end_time": 12.0, "room": "معمل الحاسوب"},
        "الذكاء الاصطناعي": {"start_time": 12.0, "end_time": 13.0, "room": "قاعة A"},
        "شبكات الحاسوب": {"start_time": 10.0, "end_time": 11.0, "room": "قاعة A"}
    }
    run_test_scenario("9. مخالفة الوقت المطلق (الذكاء الاصطناعي: تبدأ بعد)", scenario_9_schedule, problem_data)

    # سيناريو 10: مخالفة الوقت المطلق (شبكات الحاسوب تنتهي بعد 12:00)
    scenario_10_schedule = {
        "مقدمة في البرمجة": {"start_time": 9.0, "end_time": 10.0, "room": "قاعة A"},
        "هياكل البيانات": {"start_time": 10.0, "end_time": 11.0, "room": "قاعة B"},
        "قواعد البيانات": {"start_time": 11.0, "end_time": 12.0, "room": "معمل الحاسوب"},
        "الذكاء الاصطناعي": {"start_time": 13.0, "end_time": 14.0, "room": "قاعة A"},
        "شبكات الحاسوب": {"start_time": 12.0, "end_time": 13.0, "room": "قاعة A"}
    }
    run_test_scenario("10. مخالفة الوقت المطلق (شبكات الحاسوب: تنتهي قبل)", scenario_10_schedule, problem_data)
    
    scenario_11_schedule = {
        "مقدمة في البرمجة": {"start_time": 10.0, "end_time": 11.0, "room": "قاعة A"},
        "هياكل البيانات": {"start_time": 11.0, "end_time": 12.0, "room": "قاعة B"},
        "قواعد البيانات": {"start_time": 9.0, "end_time": 10.0, "room": "معمل الحاسوب"},
        "الذكاء الاصطناعي": {"start_time": 14.0, "end_time": 15.0, "room": "قاعة A"},
        "شبكات الحاسوب": {"start_time": 9.0, "end_time": 10.0, "room": "معمل الحاسوب"}
    }
    run_test_scenario("11. إيجاد جدول صالح (Backtracking Solver)", scenario_11_schedule, problem_data, run_solver=True)

    print("\n انتهى تشغيل جميع السيناريوهات ")
