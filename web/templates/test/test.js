// __tests__/fileUpload.test.js

import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import CryptoJS from 'crypto-js';
import { initIndexedDB, storeChunkInIndexedDB, getChunksFromIndexedDB, clearChunksFromIndexedDB, getCsrfToken, calculateMd5, createMasterFile, uploadChunkToServer, getLastUploadedChunk, updateMasterFileStatus, uploadFile, printIndexedDBContents, resumeUpload, downloadFile } from '../path/to/your/fileUploadFunctions'; // Ajusta la ruta según tu estructura

describe('fileUploadFunctions', () => {
    let mock;

    beforeAll(() => {
        mock = new MockAdapter(axios);
    });

    afterAll(() => {
        mock.restore();
    });

    describe('initIndexedDB', () => {
        it('should initialize IndexedDB and create object stores', async () => {
            const db = await initIndexedDB();
            expect(db.objectStoreNames.contains('chunks')).toBe(true);
        });
    });

    describe('storeChunkInIndexedDB', () => {
        it('should store a chunk in IndexedDB', async () => {
            const db = await initIndexedDB();
            await storeChunkInIndexedDB(1, 'testFile', 'testChunk', 0);
            const chunks = await getChunksFromIndexedDB(1);
            expect(chunks.length).toBe(1);
            expect(chunks[0].fileName).toBe('testFile');
        });
    });

    describe('getCsrfToken', () => {
        it('should get CSRF token from the document', () => {
            document.body.innerHTML = '<input type="hidden" name="csrfmiddlewaretoken" value="testCsrfToken">';
            const csrfToken = getCsrfToken();
            expect(csrfToken).toBe('testCsrfToken');
        });
    });

    describe('calculateMd5', () => {
        it('should calculate MD5 hash of a blob', async () => {
            const blob = new Blob(['testData']);
            const md5 = await calculateMd5(blob);
            expect(md5).toBe(CryptoJS.MD5(CryptoJS.enc.Latin1.parse('testData')).toString());
        });
    });

    describe('createMasterFile', () => {
        it('should create a master file', async () => {
            mock.onPost('/upload/masterfile/').reply(200, { id: 1 });
            const csrfToken = 'testCsrfToken';
            const masterFile = await createMasterFile('testFile', 5, 'testMd5', csrfToken);
            expect(masterFile.id).toBe(1);
        });
    });

    describe('uploadChunkToServer', () => {
        it('should upload a chunk to the server', async () => {
            mock.onPost('/upload/chunkedfile/').reply(200, { success: true });
            const csrfToken = 'testCsrfToken';
            const response = await uploadChunkToServer(1, 'testChunk', 0, 'testMd5', csrfToken);
            expect(response.success).toBe(true);
        });
    });

    describe('getLastUploadedChunk', () => {
        it('should get the last uploaded chunk number', async () => {
            mock.onGet('/upload/chunkedfile/last-chunk/?master_file_id=1').reply(200, { chunk_number: 2 });
            const lastUploadedChunk = await getLastUploadedChunk(1);
            expect(lastUploadedChunk).toBe(2);
        });
    });

    describe('updateMasterFileStatus', () => {
        it('should update the master file status', async () => {
            mock.onPatch('/upload/masterfile/1/').reply(200, { status: 'in_progress' });
            const csrfToken = 'testCsrfToken';
            const response = await updateMasterFileStatus(1, 'in_progress', csrfToken);
            expect(response.status).toBe('in_progress');
        });
    });

    describe('uploadFile', () => {
        it('should upload file in chunks', async () => {
            document.body.innerHTML = '<input type="file" id="file" value="testFile">';
            const event = { preventDefault: jest.fn() };
            const csrfToken = 'testCsrfToken';

            mock.onPost('/upload/masterfile/').reply(200, { id: 1 });
            mock.onGet('/upload/chunkedfile/last-chunk/?master_file_id=1').reply(200, { chunk_number: 2 });
            mock.onPost('/upload/chunkedfile/').reply(200, { success: true });
            mock.onPatch('/upload/masterfile/1/').reply(200, { status: 'completed' });

            await uploadFile(event);

            expect(mock.history.post.length).toBe(2);
            expect(mock.history.get.length).toBe(1);
            expect(mock.history.patch.length).toBe(1);
        });
    });

});
