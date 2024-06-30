function initIndexedDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open("uploadDatabase", 1);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains("chunks")) {
                const objectStore = db.createObjectStore("chunks", { keyPath: "id", autoIncrement: true });
                objectStore.createIndex("fileId", "fileId", { unique: false });
                objectStore.createIndex("chunkNumber", "chunkNumber", { unique: false });
            }

        };

        request.onsuccess = (event) => {
            resolve(event.target.result);
        };

        request.onerror = (event) => {
            reject(event.target.error);
        };
    });
}

async function storeChunkInIndexedDB(fileId, fileName, chunk, chunkNumber) {
    const db = await initIndexedDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(["chunks"], "readwrite");
        const objectStore = transaction.objectStore("chunks");
        const request = objectStore.add({ fileId: fileId, chunkNumber: chunkNumber, fileName: fileName, chunk: chunk });

        request.onsuccess = () => {
            console.log(`Chunk ${chunkNumber} del archivo ${fileName} almacenado en IndexedDB`);
            resolve();
        };

        request.onerror = (event) => {
            reject(event.target.error);
        };
    });
}


async function getChunksFromIndexedDB(fileId) {
    const db = await initIndexedDB();
    return new Promise((resolve, reject) => {

        const request = db
              .transaction(["chunks"], "readonly")
              .objectStore("chunks").index("fileId")
              .getAll(Number(fileId));

        request.onsuccess = (event) => {
            console.log(`Chunks recuperados de IndexedDB para fileId ${fileId}`);
            console.log(event.target.result)
            resolve(event.target.result);
        };

        request.onerror = (event) => {
            reject(event.target.error);
        };
    });
}

async function clearChunksFromIndexedDB(fileId) {
    const db = await initIndexedDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(["chunks"], "readwrite");
        const objectStore = transaction.objectStore("chunks");
        const index = objectStore.index("fileId");
        const request = index.openCursor(IDBKeyRange.only(fileId));

        request.onsuccess = (event) => {
            const cursor = event.target.result;
            if (cursor) {
                cursor.delete();
                cursor.continue();
            } else {
                resolve();
            }
        };

        request.onerror = (event) => {
            reject(event.target.error);
        };
    });
}

function getCsrfToken() {
    const csrfTokenElement = document.querySelector('[name=csrfmiddlewaretoken]');
    if (!csrfTokenElement) {
        throw new Error('CSRF token not found in the document');
    }
    return csrfTokenElement.value;
}

function calculateMd5(blob) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function(event) {
            const data = event.target.result;
            const md5 = CryptoJS.MD5(CryptoJS.enc.Latin1.parse(data)).toString();
            resolve(md5);
        };
        reader.onerror = function() {
            reject('File read error');
        };
        reader.readAsBinaryString(blob);
    });
}

async function createMasterFile(fileName, totalChunks, md5Checksum, csrfToken) {
    try {
        const response = await axios.post('/upload/masterfile/', {
            file_name: fileName,
            md5_checksum: md5Checksum,
            number_of_chunks: totalChunks
        }, {
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
        return response.data;
    } catch (error) {
        handleError(error, 'Failed to create master file');
    }
}

let simulateNetworkFailureAfterChunks = 2; // Simular falla después de 3 chunks subidos

async function uploadChunkToServer(masterFileId, chunk, chunkNumber, chunkMd5, csrfToken) {
    const formData = new FormData();
    formData.append('file', chunk);
    formData.append('chunk_number', chunkNumber);
    formData.append('master_file', masterFileId);
    formData.append('md5_checksum', chunkMd5);

    try {
        const response = await axios.post('/upload/chunkedfile/', formData, {
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
        return response.data;
    } catch (error) {
        handleError(error, 'Failed to components chunk');
    }
}

async function getLastUploadedChunk(masterFileId) {
    try {
        const response = await axios.get(`/upload/chunkedfile/last-chunk/?master_file_id=${masterFileId}`);
        console.log(`Último chunk subido: ${response.data.chunk_number}`); // Depuración
        return response.data.chunk_number;
    } catch (error) {
        if (error.response && error.response.status === 404) {
            console.warn(`Master file with ID ${masterFileId} not found.`);
            return 0;
        } else {
            handleError(error, 'Failed to fetch last uploaded chunk');
        }
    }
}

function handleError(error, message) {
    if (error.response) {
        console.error(`${message}: ${error.response.data}`);
    } else {
        console.error(`${message}: Network Error`);
    }
    throw new Error(message);
}

async function updateMasterFileStatus(masterFileId, status, csrfToken) {
    try {
        const response = await axios.patch(`/upload/masterfile/${masterFileId}/`, {
            status: status
        }, {
            headers: {
                'X-CSRFToken': csrfToken
            }
        });
        return response.data;
    } catch (error) {
        handleError(error, 'Failed to update master file status');
    }
}

async function uploadFile(event, masterFileId = null, startChunk = 0) {
    console.log("1 - Iniciando función uploadFile");
    event.preventDefault();

    try {
        const fileInput = document.getElementById(masterFileId ? `file-input-${masterFileId}` : 'file');
        const file = fileInput.files[0];
        const totalChunks = 5; // Dividir en 5 partes
        const chunkSize = Math.ceil(file.size / totalChunks); // Tamaño de cada chunk
        const csrfToken = getCsrfToken();
        const fileMd5 = await calculateMd5(file);

        if (!masterFileId) {
            const masterFile = await createMasterFile(file.name, totalChunks, fileMd5, csrfToken);
            masterFileId = masterFile.id;
        } else {
            const lastUploadedChunk = await getLastUploadedChunk(masterFileId);
            startChunk = lastUploadedChunk ? lastUploadedChunk + 1 : 0;
        }

        for (let i = startChunk; i < totalChunks; i++) {
            const chunk = file.slice(i * chunkSize, (i + 1) * chunkSize);
            const chunkMd5 = await calculateMd5(chunk);
            console.log(`2 - Subiendo chunk ${i + 1} de ${totalChunks} con MD5: ${chunkMd5}`);
            try {
                await uploadChunkToServer(masterFileId, chunk, i, chunkMd5, csrfToken);
            } catch (error) {
                console.warn(`Error subiendo chunk ${i + 1}, almacenando en IndexedDB para reanudar luego`);
                // Almacenar todos los chunks faltantes en IndexedDB
                for (let j = i; j < totalChunks; j++) {
                    const remainingChunk = file.slice(j * chunkSize, (j + 1) * chunkSize);
                    await storeChunkInIndexedDB(masterFileId, file.name, remainingChunk, j);
                }
                throw error;
            }
            if (i === startChunk) {
                await updateMasterFileStatus(masterFileId, 'in_progress', csrfToken);
            }
        }

        await updateMasterFileStatus(masterFileId, 'completed', csrfToken);
        await clearChunksFromIndexedDB(masterFileId); //

        console.log('4 - Archivo subido exitosamente!');
    } catch (error) {
        console.error('Error durante la subida del archivo:', error);
    }
}


async function printIndexedDBContents() {
    const db = await initIndexedDB();
    return new Promise((resolve, reject) => {
        const transaction = db.transaction(["chunks"], "readonly");
        const objectStore = transaction.objectStore("chunks");
        const request = objectStore.getAll();

        request.onsuccess = (event) => {
            console.log('IndexedDB Contents:', event.target.result);
            resolve(event.target.result);
        };

        request.onerror = (event) => {
            reject(event.target.error);
        };
    });
}

    async function resumeUpload(event, masterFileId) {
        event.preventDefault();
        const csrfToken = getCsrfTokened();

        const storedChunks = await getChunksFromIndexedDB(masterFileId);
        if (storedChunks.length > 0) {
            console.log(`Reanudando la carga desde IndexedDB, chunk ${storedChunks[0].chunkNumber + 1}`);
            for (const {fileId, chunkNumber, chunk } of storedChunks) {
                const chunkMd5 = await calculateMd5(chunk);
                console.log(`Subiendo chunk ${chunkNumber + 1} desde IndexedDB`);
                console.log("MasterFileId : "+fileId)
                console.log("File : "+chunk)
                console.log("ChunkNumber : "+chunkNumber)
                console.log("ChunkMd5 : "+chunkMd5)
                console.log("CsrfToken : "+csrfToken)
                await uploadChunkToServer(fileId, chunk, chunkNumber, chunkMd5, csrfToken);

            }
            await updateMasterFileStatus(masterFileId, 'completed', csrfToken);
            await clearChunksFromIndexedDB(masterFileId);
        }
    }

    async function downloadFile(masterFileId) {
        try {
            const response = await axios.get(`/upload/chunkedfile/download/?master_file_id=${masterFileId}`, {
                responseType: 'blob'
            });

            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;

            const contentDisposition = response.headers['content-disposition'];
            console.log("Content-Disposition:", contentDisposition); // Depuración

            let fileName = 'downloaded_file.png';
            if (contentDisposition) {
                const matches = /filename="([^"]*)"/.exec(contentDisposition);
                if (matches != null && matches[1]) {
                    fileName = matches[1];
                }
            }
            link.setAttribute('download', fileName);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            console.error('Error downloading file:', error);
        }
    }

document.addEventListener('DOMContentLoaded', (event) => {
    printIndexedDBContents();
});