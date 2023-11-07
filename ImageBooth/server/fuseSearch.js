import Fuse from 'fuse.js';
import dotenv from 'dotenv';
// SEARCH_KEYS="name=0.4,tags=0.4,description=0.2"


class FuseSearch {
    constructor(dataDb) {
        if (!process.env.SEARCH_KEYS) {
            throw new Error("Search keys are not provided");
        }

        const searchKeys = process.env.SEARCH_KEYS.split(',').reduce((acc, key) => {
            const [name, weight] = key.split('=');
            acc[name] = Number(weight);
            return acc;
        }, {});

        const totalWeight = Object.values(searchKeys).reduce((acc, weight) => acc + weight, 0);
        if (Math.abs(totalWeight - 1) > 0.00001) {
            throw new Error("The sum of the weights of the keys does not equal 1");
        }

        this.dataDb = dataDb;
        this.fuse = null;
        this.fuseIndex = null;
        this.searchOptions = {
            includeScore: true,
            threshold: 0.3,
            distance: 50,
            keys: Object.entries(searchKeys).map(([name, weight]) => ({ name, weight })),
        };

        // initialize 
        this.init();
    }

    async init() {
        const docs = await this.dataDb.allDocs({
            include_docs: true,
        });
        const data = docs.rows.map((row) => row.doc);
        this.fuseIndex = Fuse.createIndex(this.searchOptions.keys, data);
        this.fuse = new Fuse(data, this.searchOptions, this.fuseIndex);
    }

    async search(query) {
        if (!this.fuse) {
            await this.init();
        }
        return this.fuse.search(query);
    }

    async updateFuseIndex() {
        const docs = await this.dataDb.allDocs({
            include_docs: true,
        });
        const data = docs.rows.map((row) => row.doc);
        this.fuseIndex = Fuse.createIndex(this.searchOptions.keys, data);
        this.fuse.setCollection(data, this.fuseIndex);
    }

}

export default FuseSearch;