package com.lastspot;

public class Course {
    private String name, weekDay;
    private int time_start, time_end;

    public Course(String name, String weekDay, int time_start, int time_end) {
        this.name = name;
        this.weekDay = weekDay;
        this.time_start = time_start;
        this.time_end = time_end;
    }

    public String getName() {
        return this.name;
    }

    public String getWeekDay() {
        return this.weekDay;
    }

    public int getStart() {
        return this.time_start;
    }

    public int getEnd() {
        return this.time_end;
    }

    public void setName(String newName) {
        this.name = newName;
    }

    public void setWeekDay(String newWeekDay) {
        this.weekDay = newWeekDay;
    }

    public void setStart(int newStart) {
        this.time_start = newStart;
    }

    public void setEnd(int newEnd) {
        this.time_end = newEnd;
    }
}
