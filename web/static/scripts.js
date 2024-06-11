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
        reader.onload = function (event) {
            const data = event.target.result;
            const md5 = CryptoJS.MD5(CryptoJS.enc.Latin1.parse(data)).toString();
            resolve(md5);
        };
        reader.onerror = function () {
            reject('File read error');
        };
        reader.readAsBinaryString(blob);
    });
}


async function createMasterFile(fileName, totalChunks, md5Checksum, csrfToken) {
    try {
        const response = await axios.post('http://localhost:8000/upload/masterfile/', {
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
        if (error.response) {
            throw new Error(`Failed to create master file: ${error.response.data}`);
        } else {
            throw new Error('Failed to create master file');
        }
    }
}

async function uploadChunk(fileId, chunk, chunkNumber, chunkMd5, csrfToken) {
    const formData = new FormData();
    formData.append('file', chunk);
    formData.append('chunk_number', chunkNumber);
    formData.append('master_file', fileId);
    formData.append('md5_checksum', chunkMd5);

    try {
        const response = await axios.post('http://localhost:8000/upload/chunkedfile/', formData, {
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        return response.data;
    } catch (error) {
        if (error.response) {
            throw new Error(`HTTP error! status: ${error.response.status}: ${error.response.data}`);
        } else {
            throw new Error('HTTP error! status: Network Error');
        }
    }
}

// Manejar la subida completa del archivo
async function uploadFile(event) {
    console.log("1 - Iniciando función uploadFile");
    event.preventDefault();

    try {
        const fileInput = document.getElementById('file');
        const file = fileInput.files[0];
        const chunkSize = 1024 * 1024; // 1MB
        const totalChunks = Math.ceil(file.size / chunkSize);
        const csrfToken = getCsrfToken();

        // Calcular MD5 del archivo completo
        const fileMd5 = await calculateMd5(file);

        const masterFile = await createMasterFile(file.name, totalChunks, fileMd5, csrfToken);
        const fileId = masterFile.id;
        console.log("1 - MasterFile creado con ID:", fileId);

        for (let i = 0; i < totalChunks; i++) {
            const chunk = file.slice(i * chunkSize, (i + 1) * chunkSize);
            const chunkMd5 = await calculateMd5(chunk);
            console.log(`2 - Subiendo chunk ${i + 1} de ${totalChunks} con MD5: ${chunkMd5}`);
            await uploadChunk(fileId, chunk, i, chunkMd5, csrfToken);
        }

        console.log('3 - Archivo subido exitosamente!');
        alert('File uploaded successfully!');
    } catch (error) {
        console.error('Error during file upload:', error);
    }
}

document.addEventListener('DOMContentLoaded', (event) => {
    const form = document.getElementById('uploadForm');
    //form.addEventListener('submit', uploadFile);
});

window.getCsrfToken = getCsrfToken;
window.calculateMd5 = calculateMd5;
window.createMasterFile = createMasterFile;
window.uploadChunk = uploadChunk;
window.uploadFile = uploadFile;