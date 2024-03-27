package com.lastspot;

import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class Main {

    private static void help() {
        System.out.println();
        System.out.println("List of commands: help, insert, delete, add, show, quit");
        System.out.println("-----------------------------------------");
        System.out.println("help: show all possible commands");
        System.out.println("insert: add a course into the database");
        System.out.println("delete: delete a course from the database");
        System.out.println("choose: choose courses to add into the schedule");
        System.out.println("show: show all possible courses");
        System.out.println("quit: quit the program");
        System.out.println("-----------------------------------------");
        System.out.println();
    }

    public static void main( String[] args ) {
        Methods methods = new Methods();
        Scanner scanner = new Scanner(System.in);
        List<Course> courses = new ArrayList<>();
        boolean program = true;

        while (program) {
            System.out.println();
            System.out.print("Enter command (help for more): ");
            String userInput = scanner.nextLine();
            System.out.println();

            switch (userInput) {
                case "help":
                    help();
                    break;

                case "insert":
                    System.out.print("Enter course prefix and number: ");
                    String insertName = scanner.nextLine();
                    System.out.print("Enter the day of the week: ");
                    String insertDay = scanner.nextLine();
                    System.out.print("Enter start time: ");
                    int insertStart = scanner.nextInt();
                    System.out.print("Enter end time: ");
                    int insertEnd = scanner.nextInt();
                    methods.insertCourse(insertName, insertDay, insertStart, insertEnd);
                    scanner.nextLine();
                    break;

                case "delete":
                    System.out.print("Enter course prefix and number: ");
                    String deleteName = scanner.nextLine();
                    System.out.print("Enter the day of the week: ");
                    String deleteDay = scanner.nextLine();
                    System.out.print("Enter start time: ");
                    int deleteStart = scanner.nextInt();
                    System.out.print("Enter end time: ");
                    int deleteEnd = scanner.nextInt();
                    methods.deleteCourse(deleteName, deleteDay, deleteStart, deleteEnd);
                    scanner.nextLine();
                    break;

                case "add":
                    boolean choosing = true;
                    List<String> schedule = new ArrayList<>();
                    
                    while (choosing) {
                        System.out.print("Enter course prefix and number (quit to generate schedule): ");
                        String addName = scanner.nextLine();

                        switch (addName) {
                            case "quit":
                                choosing = false;
                                break;
                        
                            default:
                                schedule.add(addName);
                                break;
                        }
                    }

                    methods.displaySchedule(methods.schedule(schedule));
                    break;

                case "show":
                    methods.getAllCourses();
                    break;

                case "quit":
                    program = false;
                    break;
            
                default:
                    System.out.println("Invalid command");
                    break;
            }
        }
        scanner.close();
        System.out.println("Exiting the drawing application...");
        try {
            Thread.sleep(3000);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        System.exit(0);
    }
}