function dropHandler(ev) {
    console.log("File(s) dropped");

    // Prevent default behavior (Prevent file from being opened)
    ev.preventDefault();

    if (ev.dataTransfer.items) {
        // Use DataTransferItemList interface to access the file(s)
        [...ev.dataTransfer.items].forEach((item, i) => {
            // If dropped items aren't files, reject them
            if (item.kind === "file") {
                const file = item.getAsFile();
                console.log(`… file[${i}].name = ${file.name}`);
            }
        });
    } else {
        // Use DataTransfer interface to access the file(s)
        [...ev.dataTransfer.files].forEach((file, i) => {
            console.log(`… file[${i}].name = ${file.name}`);
        });
    }
}

function dragOverHandler(ev) {
    console.log("File(s) in drop zone");
    ev.preventDefault();
}

function dragEnterHandler(ev) {
    console.log("File(s) entering drop zone");
    ev.target.classList.add('dark');
}

function dragLeaveHandler(ev) {
    console.log("File(s) leaving drop zone");
    ev.target.classList.remove('dark');
}

document.querySelectorAll('.file-upload-design').forEach(element => {
    element.addEventListener('dragenter', dragEnterHandler);
    element.addEventListener('dragleave', dragLeaveHandler);
});

async function uploadFile(event) {
            event.preventDefault();
            const fileInput = document.getElementById('file');
            const file = fileInput.files[0];
            const chunkSize = 1024 * 1024; // 1MB
            const totalChunks = Math.ceil(file.size / chunkSize);
            let fileId = null;
            const csrfToken = document.getElementById('csrf_token').value;

            for (let i = 0; i < totalChunks; i++) {
                const chunk = file.slice(i * chunkSize, (i + 1) * chunkSize);
                const formData = new FormData();
                formData.append('file', chunk);
                formData.append('chunk_number', i);
                formData.append('total_chunks', totalChunks);
                formData.append('file_name', file.name);

                if (fileId) {
                    formData.append('file_id', fileId);
                }

                try {
                    const response = await fetch('http://localhost:8000/upload_file_chunk', {
                        method: 'POST',
                        body: formData,
                        headers: {
                            'X-CSRFToken': csrfToken
                        }
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP error! status: ${response.status}`);
                    }

                    const result = await response.json();
                    console.log('Response from server:', result);

                    fileId = result.file_id;
                    console.log('file id: ' + fileId);

                    if (result.is_complete) {
                        console.log('File uploaded successfully!');
                        alert('File uploaded successfully!')
                        break;
                    }
                } catch (error) {
                    console.error('Error during file upload:', error);
                }
            }
        }