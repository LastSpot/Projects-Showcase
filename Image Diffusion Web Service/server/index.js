// Desciption: This file contains the CRUD functions for the PouchDB database.
import express from 'express';
import session from 'express-session';
import passport from 'passport';
import { Strategy as LocalStrategy } from 'passport-local';
import cors from 'cors';
import logger from 'morgan';
import PouchDB from 'pouchdb';
import PouchDBFind from 'pouchdb-find';
import { body, validationResult, query } from 'express-validator';
import dotenv from 'dotenv';
import chalkAnimation from 'chalk-animation';
import FuseSearch from './fuseSearch.js';
import { fileURLToPath } from 'url';
import { dirname } from 'path';
import path from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);


dotenv.config();
PouchDB.plugin(PouchDBFind);

// check if the env variable is set
if (!process.env.SEARCH_KEYS) {
    console.error('SEARCH_KEYS env variable not set');
    process.exit(1);
}
if (!process.env.SESSION_SECRET) {
    console.error('SESSION_SECRET env variable not set');
    process.exit(1);
}
if (!process.env.ADMIN_SECRET) {
    console.error('ADMIN_SECRET env variable not set');
    process.exit(1);
}

const dataDb = new PouchDB('dataDb'); // database for model data
const rankDb = new PouchDB('rankDb'); // database for tag rank data
const userLoginDb = new PouchDB('userLoginDb'); // database for user login data




////////////////////////////////////////////////////////////////


// server and router setup
const server = express();
const port = 3000;

// server.use(cors());
server.use(logger('dev'));
server.use(express.json());
server.use(express.urlencoded({ extended: false }));
server.use('/', express.static(path.join(__dirname, '../client')));

const fuseSearch = new FuseSearch(dataDb);


// async function userRegister(res, username, password) {
//     try {
//         if (await userExists(username)) {
//             res.status(409).json({
//                 status: 'fail',
//                 data: {
//                     message: `User ${username} already exists`
//                 }
//             });
//         } else {
//             await userLoginDb.put({
//                 _id: username,
//                 password: password
//             });
//             await usersDB.put({
//                 _id: username,
//                 password: password
//             });
//             res.status(200).json({
//                 status: 'success',
//                 data: {
//                     message: `User ${username} created`
//                 }
//             });
//         }
//     } catch (err) {
//         res.status(500).json({
//             status: 'fail',
//             data: {
//                 message: err.message
//             }
//         });
//     }
// }

// server.post('/register', [
//     body('username').isString(),
//     body('password').isString().isLength({ min: 8 }).withMessage('Password must be at least 8 characters long')
// ], (req, res) => {
//     const errors = validationResult(req);
//     if (!errors.isEmpty()) {
//         res.status(400).json({
//             status: 'fail',
//             data: {
//                 message: errors.array()
//             }
//         });
//         return;
//     }
//         userRegister(res, req.body.username, req.body.password);
//     }
// );

// create a new user
async function userRegister(res, username, password) {
    if (!username || !password) {
        res.status(400).json({
            status: 'fail',
            data: {
                message: 'Username or password missing'
            }
        });
    } else {
        // const userExists = await userExists(username);
        if (await userExists(username)) {
            res.status(409).json({
                status: 'fail',
                data: {
                    message: `User ${username} already exists`
                }
            });
        } else {
            await userLoginDb.put({
                _id: username,
                password: password,
            });
            res.status(200).json({
                status: 'success',
                data: {
                    message: `User ${username} created`
                }
            });
        }
    }
} // tested

server.post('/api/register', (req, res) => {
    const username = req.body.username;
    const password = req.body.password;
    userRegister(res, username, password);
});

// check if the user login information is correct
async function userLogin(res, username, password) {
    if (!username || !password) {
        res.status(400).json({
            status: 'fail',
            data: {
                message: 'Username or password missing'
            }
        });
    } else {
        // const userExists = await userExists(username);
        if (!await userExists(username)) {
            res.status(404).json({
                status: 'fail',
                data: {
                    message: 'User does not exist'
                }
            });
        } else {
            const user = await userLoginDb.get(username);
            if (user.password !== password) {
                res.status(401).json({
                    status: 'fail',
                    data: {
                        message: 'Wrong password'
                    }
                });
            } else {
                res.status(200).json({
                    status: 'success',
                    data: {
                        message: `User ${username}: Login successful`
                    }
                });
            }
        }
    }
} // tested

server.post('/api/login', (req, res) => {
    const username = req.body.username;
    const password = req.body.password;
    userLogin(res, username, password);
});

async function deleteUser(res, username, secret) {
    try {
        if (secret !== process.env.ADMIN_SECRET) {
            res.status(401).json({
                status: 'fail',
                data: {
                    message: 'Unauthorized'
                }
            });
            return;
        }
        await userLoginDb.remove(username);
        res.status(200).json({
            status: 'success',
            data: {
                message: `User ${username} deleted`
            }
        });

    } catch (err) {
        res.status(500).json({
            status: 'fail',
            data: {
                message: err.message
            }
        });
    }
}

server.delete('/api/deleteUser', [
    body('username').isString(),
    body('secret').isString().notEmpty()
], (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        res.status(400).json({
            status: 'fail',
            data: {
                message: errors.array()
            }
        });
        return;
    }
    deleteUser(res, req.body.username, req.body.secret);
});



async function fuzzySearch(res, query) {
    try {
        const result = await fuseSearch.search(query);
        res.status(200).json({
            status: 'success',
            data: result,
        });
    } catch (err) {
        res.status(500).json({
            status: 'fail',
            data: {
                message: err.message,
            },
        });
    }
}

// server routes
server.get('/api/search', [query('query').isString()], (req, res) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        res.status(400).json({
            status: 'fail',
            data: {
                message: errors.array(),
            },
        });
        return;
    }

    // fuzzy search
    fuzzySearch(res, req.query.query);
});






// dump all user login data
async function dumpUserLogin(res) {
    try {
        const result = await userLoginDb.allDocs({
            include_docs: true,
        });
        res.status(200).json({
            status: 'success',
            data: {
                message: result.rows
                    .map((row) => row.doc)
                    .filter((doc) => doc._id !== '_design/_auth'), // filter out the design document
            }
        });
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: err.toString()
        });
    }
} // tested

server.get('/api/dumpUserLogin', (req, res) => {
    dumpUserLogin(res);
});

// create tag index in rankDb, not called outside
async function createTagsIndex() {
    try {
        await dataDb.createIndex({
            index: {
                fields: ['tags'],
                ddoc: 'tags-index-design-document',
                type: 'json',
            },
        });
        console.log('Tags index created successfully.');
    } catch (err) {
        console.error('Error creating tags index:', err);
    }
} // tested

createTagsIndex();

// check if model name exists in the database
async function modelExists(name) {
    try {
        const result = await dataDb.find({
            selector: {
                name: name,
            },
            limit: 1,
        });
        return result.docs.length > 0;
    } catch (err) {
        console.error('Error finding document with name:', err);
        return false;
    }
} // tested

// create a new model in the dataDb
async function createModel(res, name, description = '', type, tagstr = '', downloadLink = '', fineTuneMethod, baseModel, pictureLink = '', license = 'CC0', secret) {
    // Check if the user is authorized
    if (secret !== process.env.ADMIN_SECRET) {
        res.status(401).json({
            status: 'fail',
            data: {
                message: 'Unauthorized'
            }
        });
        return;
    }

    // Check if the model already exists
    if (await modelExists(name)) {
        res.status(409).json({
            status: 'fail',
            data: {
                message: 'Model already exists'
            }
        });
        return;
    }

    // Convert the tagstr string into an array of tags
    const tags = tagstr.split(',').map((tag) => tag.trim());

    try {
        // Sync the tags with the rank database
        await Promise.all(tags.map((tag) => syncTag(tag)));
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: 'Unable to sync tags: ' + err
        });
        return;
    }

    // Create the model object
    const model = {
        _id: name,
        name: name,
        description: description,
        type: type,
        tags: tags,
        downloadLink: downloadLink,
        fineTuneMethod: fineTuneMethod,
        baseModel: baseModel,
        pictureLink: pictureLink,
        view: 0,
        like: 0,
        share: 0,
        license: license,
    };

    // update database and fuse
    try {
        // put the model into the database
        await dataDb.put(model);

        // update fuse index
        fuseSearch.updateFuseIndex();

        res.status(200).json({
            status: 'success',
            data: {
                message: 'Model created'
            }
        });
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: err.toString()
        });
    }
} // tested

server.post('/api/createModel', [
    body('name').isString().trim().notEmpty(),
    body('description').isString(),
    body('type').isString().trim().notEmpty(),
    body('tags').isString().trim().notEmpty(),
    body('downloadLink').isString().trim().isURL(),
    body('fineTuneMethod').isString().trim().notEmpty(),
    body('baseModel').isString().trim().notEmpty(),
    body('pictureLink').isString().trim().isURL(),
    body('license').optional().isString(),
    body('secret').isString().trim().notEmpty(),
], (req, res) => {
    const result = validationResult(req);
    if (!result.isEmpty()) {
        res.status(400).json({
            status: 'fail',
            data: {
                message: result.array()
            }
        });
        return;
    }

    const name = req.body.name;
    const description = req.body.description;
    const type = req.body.type;
    const tagstr = req.body.tags;
    const downloadLink = req.body.downloadLink;
    const fineTuneMethod = req.body.fineTuneMethod;
    const baseModel = req.body.baseModel;
    const pictureLink = req.body.pictureLink;
    const license = req.body.license;
    const secret = req.body.secret;
    createModel(res, name, description, type, tagstr, downloadLink, fineTuneMethod, baseModel, pictureLink, license, secret);
});

// delete a model by its name in the dataDb
async function deleteModel(res, name, secret) {
    try {
        // Check if is authorized
        if (secret !== process.env.ADMIN_SECRET) {
            res.status(401).json({
                status: 'fail',
                data: {
                    message: 'Unauthorized'
                }
            });
            return;
        }
        // delete the model from the database
        const model = await dataDb.get(name);
        await dataDb.remove(model);

        // update fuse index
        fuseSearch.updateFuseIndex();
        res.status(200).json({
            status: 'success',
            data: {
                message: 'Model deleted'
            }
        });
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: err.toString()
        });
    }
} // tested

server.delete('/api/deleteModel', [
    body('id').isString().trim().notEmpty(),
], (req, res) => {
    const result = validationResult(req);
    if (!result.isEmpty()) {
        res.status(400).json({
            status: 'fail',
            data: {
                message: result.array()
            }
        });
        return;
    }

    const id = req.body.id;
    const secret = req.body.secret;
    deleteModel(res, id, secret);
});

// update like number of a model by its id in the dataDb
async function updateModelLike(res, id) {
    try {
        const model = await dataDb.get(id);
        model.like += 1;
        await dataDb.put(model);
        res.status(200).json({
            status: 'success',
            data: {
                message: 'Model like number updated'
            }
        });
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: err.toString()
        });
    }
} // tested

server.put('/api/likeModel', [body('id').isString().trim().notEmpty(),
body('userId').isString().trim().notEmpty(),
], (req, res) => {
    const result = validationResult(req);
    if (!result.isEmpty()) {
        res.status(400).json({
            status: 'fail',
            data: {
                message: result.array()
            }
        });
        return;
    }

    const id = req.body.id;
    const userId = req.body.userId;
    updateModelLike(res, id);
});

// update share number of a model by its id in the dataDb
async function updateModelShare(res, id) {
    try {
        const model = await dataDb.get(id);
        model.share += 1;
        await dataDb.put(model);
        res.status(200).json({
            status: 'success',
            data: {
                message: 'Model share number updated'
            }
        });
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: err.toString()
        });
    }
} // tested

server.put('/api/updateModelShare', [body('id').isString().trim().notEmpty(),
], (req, res) => {
    const result = validationResult(req);
    if (!result.isEmpty()) {
        res.status(400).json({
            status: 'fail',
            data: {
                message: result.array()
            }
        });
        return;
    }

    const id = req.body.id;
    updateModelShare(res, id);
});

// update view number of a model by its id in the dataDb
async function updateModelView(res, id) {
    try {
        const model = await dataDb.get(id);
        model.view += 1;
        await dataDb.put(model);
        res.status(200).json({
            status: 'success',
            data: {
                message: 'Model view number updated'
            }
        });
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: err.toString()
        });
    }
} // tested

server.put('/api/updateModelView', [body('id').isString().trim().notEmpty(),
], (req, res) => {
    const result = validationResult(req);
    if (!result.isEmpty()) {
        res.status(400).json({
            status: 'fail',
            data: {
                message: result.array()
            }
        });
        return;
    }

    const id = req.body.id;
    updateModelView(res, id);
});

// unlike a model by its id in the dataDb
async function unlikeModel(res, id) {
    try {
        const model = await dataDb.get(id);
        model.like = Math.max(0, model.like - 1);
        await dataDb.put(model);
        res.status(200).json({
            status: 'success',
            data: {
                message: 'Model like number updated'
            }
        });
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: err.toString()
        });
    }
} // tested

server.put('/api/unlikeModel', [body('id').isString().trim().notEmpty(),
body('userId').isString().trim().notEmpty(),
], (req, res) => {
    const result = validationResult(req);
    if (!result.isEmpty()) {
        res.status(400).json({
            status: 'fail',
            data: {
                message: result.array()
            }
        });
        return;
    }

    const id = req.body.id;
    const userId = req.body.userId;
    unlikeModel(res, id);
});


// NOT USE ANYMORE
// search model contains all tag in tags array
// async function searchModelByTags(res, tagstr) {
//     // Convert the tagstr string into an array of tags
//     const tags = tagstr.split(',').map(tag => tag.trim());

//     try {
//         const result = await dataDb.find({
//             selector: {
//                 tags: {
//                     $all: tags
//                 }
//             },
//             use_index: 'tags-index-design-document',
//             limit: 10,
//         });

//         // Update the search times of the tags
//         await Promise.all(tags.map((tag) => updateTagSearchTimes(tag)));

//         // Handle the response with the found documents
//         res.status(200).json({
//             status: 'success',
//             data: result.docs
//         });
//     } catch (err) {
//         console.error('Error in getTopTags function:', err);
//         res.status(500).json({
//             status: 'error',
//             message: err.toString()
//         });
//     }
// } //tested

// NOT USE ANYMORE
// server.post('/searchModelByTags', [
//     body('tags').isString().trim().notEmpty().matches(/^([a-zA-Z0-9]+\,\ *)*([a-zA-Z0-9 ]*)$/),
// ], (req, res) => {
//     const result = validationResult(req);
//     if (!result.isEmpty()) {
//         res.status(400).json({
//             status: 'fail',
//             data: {
//                 message: result.array()
//             }
//         });
//         return;
//     }
//     const tagstr = req.body.tags;
//     searchModelByTags(res, tagstr);
// });

// get a model by its name in the dataDb
async function fetchModelById(res, id) {
    try {
        const model = await dataDb.get(id);
        res.status(200).json({
            status: 'success',
            data: model
        });
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: err.toString()
        });
    }
} // tested

server.get('/api/fetchModelById', [
    query('id').isString().trim().notEmpty(),
], (req, res) => {
    const result = validationResult(req);
    if (!result.isEmpty()) {
        res.status(400).json({
            status: 'fail',
            data: {
                message: result.array()
            }
        });
        return;
    }

    const id = req.query.id;
    fetchModelById(res, id);
});

// check if tag exists in the rankDb
async function tagExists(tag) {
    try {
        await rankDb.get(tag);
        return true;
    } catch (err) {
        if (err.status === 404) {
            return false;
        }
    }
} //tested

// sync tag with rankDb
async function syncTag(tag) {
    if (!tag) {
        return;
    }
    if (!(await tagExists(tag))) {
        await rankDb.put({
            _id: tag,
            searchTimes: 0,
        });
    }
} // tested

// update tag SearchTimes in rankDb
async function updateTagSearchTimes(tag) {
    if (!tag) {
        return;
    }
    if (!(await tagExists(tag))) {
        return;
    }
    const tagDoc = await rankDb.get(tag);
    tagDoc.searchTimes += 1;
    await rankDb.put(tagDoc);
} // tested

// create index for tag's SearchTimes in rankDb
async function createSearchTimesIndex() {
    try {
        await rankDb.createIndex({
            index: {
                fields: ['searchTimes'],
                ddoc: 'searchTimes-index-design-document',
            },
        });
        console.log('SearchTimes index created successfully');
    } catch (err) {
        console.error('Error creating searchTimes index:', err);
    }
}
// tested

createSearchTimesIndex();

// get top 10 tags by searchTimes in rankDb
async function getTopTags(res) {
    try {
        const result = await rankDb.find({
            selector: {
                searchTimes: { $gte: 0 }
            },
            sort: [{ 'searchTimes': 'desc' }],
            limit: 10,
            use_index: 'searchTimes-index-design-document',
        });
        res.status(200).json({
            status: 'success',
            data: result.docs
        });
    } catch (err) {
        console.error('Error in getTopTags function:', err);
        res.status(500).json({
            status: 'error',
            message: err.toString()
        });
    }
} // tested

server.get('/api/getTopTags', (req, res) => {
    getTopTags(res);
});

// syncTag('tag1');
// syncTag('tag2');

// delete a tag by its name in the rankDb
async function deleteTag(res, tag) {
    try {
        const tagDoc = await rankDb.get(tag);
        await rankDb.remove(tagDoc);
        res.status(200).json({
            status: 'success',
            data: {
                message: 'Tag deleted'
            }
        });
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: err.toString()
        });
    }
} // tested

server.delete('/api/deleteTag', [body('tag').isString().trim().notEmpty()], (req, res) => {
    const result = validationResult(req);
    if (!result.isEmpty()) {
        res.status(400).json({
            status: 'fail',
            data: {
                message: result.array()
            }
        });
        return;
    }
    const tag = req.body.tag;
    deleteTag(res, tag);
});

// dump all tags in the rankDb
async function dumpTags(res) {
    try {
        const result = await rankDb.allDocs({
            include_docs: true,
        });
        res.status(200).json({
            status: 'success',
            data: result.rows
                .map((row) => row.doc)
                .filter((doc) => !doc._id.startsWith('_design/')), // filter out design docs
        });
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: err.toString()
        });
    }
} // tested

server.get('/api/dumpTags', (req, res) => {
    dumpTags(res);
});




// dump all models in the dataDb
async function dumpModels(res) {
    try {
        const result = await dataDb.allDocs({
            include_docs: true,
        });
        res.status(200).json({
            status: 'success',
            data: result.rows
                .map((row) => row.doc)
                .filter((doc) => !doc._id.startsWith('_design/')), // filter out design docs
        });
    } catch (err) {
        res.status(500).json({
            status: 'error',
            message: err.toString()
        });
    }
} // tested

server.get('/api/dumpModels', (req, res) => {
    dumpModels(res);
});





server.all('*', (req, res) => {
    res.status(404).json({
        status: 'fail',
        data: {
            message: 'Not found'
        }
    });
});

// run the server
server.listen(process.env.PORT || 3000, () => {
    const port = process.env.PORT || 3000;
    // This is totally just for fun!
    const banner = `
    ████████╗███████╗ █████╗ ███╗   ███╗    ██████╗  ██████╗ 
    ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║    ╚════██╗██╔═████╗
       ██║   █████╗  ███████║██╔████╔██║     █████╔╝██║██╔██║
       ██║   ██╔══╝  ██╔══██║██║╚██╔╝██║     ╚═══██╗████╔╝██║
       ██║   ███████╗██║  ██║██║ ╚═╝ ██║    ██████╔╝╚██████╔╝
       ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝    ╚═════╝  ╚═════╝ 
                                                             
    `;
    const msg = `${banner}\n     Server started on http://localhost:${port}`;
    const rainbow = chalkAnimation.rainbow(msg);

    // Have the rainbow stop so we can log stuff to the console.
    setTimeout(() => {
        rainbow.stop(); // Animation stops
    }, 2000);
}
);