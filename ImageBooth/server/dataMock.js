import { createReadStream } from 'fs';
import pkg from 'papaparse';
const { parse } = pkg;
import PouchDB from 'pouchdb';


// Replace 'your_database_name' with the desired PouchDB database name
let dataDb = new PouchDB('dataDb'); // database for model data
let rankDb = new PouchDB('rankDb'); // database for tag rank data
let userLoginDb = new PouchDB('userLoginDb'); // database for user login data

// Destroy the database before importing the CSV file
await dataDb.destroy().then(function () {
    console.log('dataDb destroyed');
    dataDb = new PouchDB('dataDb');
}).catch(function (err) {
    console.log(err);
});

await rankDb.destroy().then(function () {
    console.log('rankDb destroyed');
    rankDb = new PouchDB('rankDb');
}).catch(function (err) {
    console.log(err);
});

await userLoginDb.destroy().then(function () {
    console.log('userLoginDb destroyed');
    userLoginDb = new PouchDB('userLoginDb');
}).catch(function (err) {
    console.log(err);
});

const fileUser = createReadStream('mock_data/username_mock.csv');
const fileModel = createReadStream('mock_data/model_mock3.csv');
const fileTag = createReadStream('mock_data/tag_mock.csv');

console.log('Importing CSV data to PouchDB...');
// Parse the CSV file
parse(fileUser, {
    header: true, // Set to true if your CSV file contains headers
    complete: async function (results) {
        try {
            const docs = results.data.map((row, index) => {
                // Add an _id field if your CSV data doesn't have a unique ID
                //row._id = 'doc_' + (index + 1);
                return row;
            });
            // console.log(docs);
            // Bulk insert the JSON objects into PouchDB
            await userLoginDb.bulkDocs(docs);

            console.log('CSV imported successfully to userLoginDb');
        } catch (err) {
            console.error('Error importing CSV to PouchDB:', err);
        }
    },
    error: function (err) {
        console.error('Error parsing CSV file:', err);
    },
});


parse(fileModel, {
    header: true, // Set to true if your CSV file contains headers
    complete: async function (results) {
        try {
            const docs = results.data.map((row, index) => {
                // Split the 'tags' column string into an array
                if (row.tags) {
                    row.tags = row.tags.split(',').map(tag => tag.trim());
                } else {
                    row.tags = [];
                }
                row.like = 0;
                row.view = 0;
                row.share = 0;

                // Add an _id field if your CSV data doesn't have a unique ID
                //row._id = 'doc_' + (index + 1);

                return row;
            });
            // console.log(docs);

            // Bulk insert the JSON objects into PouchDB
            await dataDb.bulkDocs(docs);

            console.log('CSV imported successfully to dataDb');
        } catch (err) {
            console.error('Error importing CSV to PouchDB:', err);
        }
    },
    error: function (err) {
        console.error('Error parsing CSV file:', err);
    },
});


parse(fileTag, {
    header: true, // Set to true if your CSV file contains headers
    complete: async function (results) {
        try {
            const docs = results.data.map((row, index) => {
                // Add an _id field if your CSV data doesn't have a unique ID
                //row._id = 'doc_' + (index + 1);
                row.searchTimes = 0;
                return row;
            });
            // console.log(docs);
            // Bulk insert the JSON objects into PouchDB
            await rankDb.bulkDocs(docs);

            console.log('CSV imported successfully to rankDb');
        } catch (err) {
            console.error('Error importing CSV to PouchDB:', err);
        }
    },
    error: function (err) {
        console.error('Error parsing CSV file:', err);
    },
});
