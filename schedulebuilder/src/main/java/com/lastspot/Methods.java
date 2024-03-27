package com.lastspot;

import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class Methods {

    private MongoDBConnector db;

    public Methods() {
        db = new MongoDBConnector();
    }

    public Course createCourse(String name, String weekDay, int start, int end) {
        return new Course(name, weekDay, start, end);
    }

    public void insertCourse(String name, String weekDay, int start, int end) {
        db.insertCourse(createCourse(name, weekDay, start, end));
    }

    public void deleteCourse(String name, String weekDay, int start, int end) {
        db.deleteCourse(createCourse(name, weekDay, start, end));
    }

    public Course getCourse(String name, String weekDay, int start, int end) {
        return db.findCourse(new Course(name, weekDay, start, end));
    }

    public List<Course> findCourse(String name) {
        return db.getCourse(name);
    }

    public List<Course> selectCourses(List<String> courses) {
        List<Course> selectedCourses = new ArrayList<>();
        for (String name : courses) {
            List<Course> foundCourses = findCourse(name);
            for (Course course : foundCourses) {
                selectedCourses.add(course);
            }
        }
        return selectedCourses;
    }

    public boolean courseConflict(Course course1, Course course2) {
        return course1.getWeekDay().equals(course2.getWeekDay()) && !(course1.getEnd() <= course2.getStart() || course1.getStart() >= course2.getEnd());
    }
    
    public boolean conflictsCheck(List<Course> courses) {
        for (int i = 0; i < courses.size(); i++) {
            Course course1 = courses.get(i);
            for (int j = 0; j < courses.size(); j++) {
                Course course2 = courses.get(j);
                if (i != j && courseConflict(course1, course2)) {
                    return true;
                }
            }
        }
        return false;
    }

    public void generateSchedule(Map<String, List<Course>> courseGroups, List<Course> curCombination, List<List<Course>> schedule) {
        if (curCombination.size() == courseGroups.size() && !conflictsCheck(curCombination)) {
            curCombination.sort(Comparator.comparingInt(Course::getStart));
            List<Course> deepCopy = new ArrayList<>();
            for (Course course : curCombination) {
                deepCopy.add(new Course(course.getName(), course.getWeekDay(), course.getStart(), course.getEnd()));
            }
            schedule.add(deepCopy);
            return;
        }

        for (Map.Entry<String, List<Course>> entry : courseGroups.entrySet()) {
            String courseName = entry.getKey();
            if (!curCombination.stream().anyMatch(c -> c.getName().equals(courseName))) {
                for (Course course : entry.getValue()) {
                    curCombination.add(course);
                    generateSchedule(courseGroups, curCombination, schedule);
                    curCombination.remove(course);
                }
            }
        }
    }

    public List<List<Course>> schedule(List<String> courses) {
        List<List<Course>> schedule = new ArrayList<>();
        List<Course> selectedCourses = selectCourses(courses);
        Map<String, List<Course>> courseGroups = new HashMap<>();

        for (Course course : selectedCourses) {
            String courseName = course.getName();
            if (!courseGroups.containsKey(courseName)) {
                courseGroups.put(courseName, new ArrayList<>());
            }
            courseGroups.get(courseName).add(course);
        }

        generateSchedule(courseGroups, new ArrayList<>(), schedule);
        return schedule;
    }

    public void getDayCourses(List<Course> day) {
        for (Course course : day) {
            System.out.println(course.getName() + "   " + course.getStart() + " - " + course.getEnd());
        }
    }

    public void displaySchedule(List<List<Course>> schedule) {
        for (List<Course> courses : schedule) {
            List<Course> monday = new ArrayList<>();
            List<Course> tuesday = new ArrayList<>();
            List<Course> wednesday = new ArrayList<>();
            List<Course> thursday = new ArrayList<>();
            List<Course> friday = new ArrayList<>();
            for (Course course : courses) {
                switch (course.getWeekDay()) {
                    case "monday":
                        monday.add(course);
                        break;
                    case "tuesday":
                        tuesday.add(course);
                        break;
                    case "wednesday":
                        wednesday.add(course);
                        break;
                    case "thursday":
                        thursday.add(course);
                        break;
                    case "friday":
                        friday.add(course);
                        break;
                    default:
                        // Handle unrecognized weekday if necessary
                        break;
                }
            }
            System.out.println();
            System.out.println("--------------------------------");
            System.out.println("Monday: ");
            getDayCourses(monday);
            System.out.println();

            System.out.println("Tuesday: ");
            getDayCourses(tuesday);
            System.out.println();

            System.out.println("Wednesday: ");
            getDayCourses(wednesday);
            System.out.println();

            System.out.println("Thursday: ");
            getDayCourses(thursday);
            System.out.println();

            System.out.println("Friday: ");
            getDayCourses(friday);
            System.out.println();
            System.out.println("--------------------------------");
            System.out.println();
        }
    }

    public void getAllCourses() {
        List<Course> allCourses = db.allCourses();
        System.out.println();
        System.out.println("List of all available courses:");
        for (int i = 0; i < allCourses.size(); i++) {
            Course course = allCourses.get(i);
            System.out.println(course.getName() + " / " + course.getWeekDay() + " / " + course.getStart() + " - " + course.getEnd());
        }
        System.out.println();
    }

    public void end() {
        db.close();
    }
}
