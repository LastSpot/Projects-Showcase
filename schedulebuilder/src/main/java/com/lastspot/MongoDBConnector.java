package com.lastspot;

import com.mongodb.client.MongoClient;
import com.mongodb.client.MongoClients;
import com.mongodb.client.MongoCollection;
import com.mongodb.client.MongoCursor;
import com.mongodb.client.MongoDatabase;

import java.util.ArrayList;
import java.util.List;

import org.bson.Document;

public class MongoDBConnector {
    private static final String connectionString = "mongodb+srv://artificialvoidstorage:bf0rd8pcYhSAXOXH@cluster0.wydfctd.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0";
    private static final String DATABASE_NAME = "courses";
    private static final String COLLECTION_NAME = "course";

    private MongoClient client;
    private MongoDatabase database;
    MongoCollection<Document> collection;

    public MongoDBConnector() {
        client = MongoClients.create(connectionString);
        database = client.getDatabase(DATABASE_NAME);
        collection = database.getCollection(COLLECTION_NAME);
    }

    public void insertCourse(Course course) {
        Document doc = new Document("name", course.getName())
                            .append("day", course.getWeekDay())
                            .append("start", course.getStart())
                            .append("end", course.getEnd());
        if (collection.find(doc).first() != null) {
            System.out.println("Course already existed");
        }
        else {
            collection.insertOne(doc);
            System.out.println("Successfully insert course into database");
        }
    }

    public void deleteCourse(Course course) {
        Document doc = new Document("name", course.getName())
                            .append("day", course.getWeekDay())
                            .append("start", course.getStart())
                            .append("end", course.getEnd());
        if (collection.find(doc).first() != null) {
            collection.deleteOne(doc);
            System.out.println("Successfully deleted the course from the database");
        }
        else {
            System.out.println("Course does not exist in the database");
        }
    }

    public Course findCourse(Course course) {
        Document doc = new Document("name", course.getName())
                            .append("day", course.getWeekDay())
                            .append("start", course.getStart())
                            .append("end", course.getEnd());
        Document foundDoc = collection.find(doc).first();
        if (foundDoc != null) {
            String name = foundDoc.getString("name");
            String day = foundDoc.getString("day");
            int start = foundDoc.getInteger("start");
            int end = foundDoc.getInteger("end");
            return new Course(name, day, start, end);
        }
        else {
            return null;
        }
    }

    public List<Course> getCourse(String name) {
        List<Course> course = new ArrayList<>();
        Document doc = new Document("name", name);
        MongoCursor<Document> cursor = collection.find(doc).iterator();
        while (cursor.hasNext()) {
            Document newCourse = cursor.next();
            String courseName = newCourse.getString("name");
            String day = newCourse.getString("day");
            int start = newCourse.getInteger("start");
            int end = newCourse.getInteger("end");
            course.add(new Course(courseName, day, start, end));
        }
        return course;
    }

    public List<Course> allCourses() {
        List<Course> courses = new ArrayList<>();
        MongoCursor<Document> cursor = collection.find().iterator();
        while (cursor.hasNext()) {
            Document newCourse = cursor.next();
            String name = newCourse.getString("name");
            String day = newCourse.getString("day");
            int start = newCourse.getInteger("start");
            int end = newCourse.getInteger("end");
            if (!courses.contains(newCourse)) {
                courses.add(new Course(name, day, start, end));
            }
        }
        return courses;
    }

    public void close() {
        client.close();
    }
}
