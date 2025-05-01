import React, { useState } from 'react';
import { uploadFile } from '../services/api';

const FileUpload = () => {
    const [file, setFile] = useState(null);
    const [message, setMessage] = useState('');

    const handleFileChange = (e) => {
        setFile(e.target.files[0]);
    };

    const handleUpload = async () => {
        if (!file) {
            setMessage('Please select a file to upload.');
            return;
        }

        try {
            const response = await uploadFile(file);
            setMessage(`File uploaded successfully: ${response.filename}`);
        } catch (error) {
            console.error("Upload failed:", error);
            setMessage(`Error: ${error.message}`);
        }
    };

    return (
        <div className="p-4">
            <input type="file" onChange={handleFileChange} className="mb-2" />
            <button
                onClick={handleUpload}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
                Upload
            </button>
            {message && <p className="mt-2">{message}</p>}
        </div>
    );
};

export default FileUpload;